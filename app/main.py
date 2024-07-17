import os
import streamlit as st
from dotenv import load_dotenv
from app.assistants import create_documint_assistants, generate_document
from app.questionnaire import create_questionnaire, create_questionnaire_with_preload
from app.document_template_parser import DocumentTemplateParser
from app.question_parser import QuestionParser
from app.logger import main_logger
import pypandoc
import tempfile
from datetime import datetime

load_dotenv()

# Load questionnaire at app startup
question_parser = QuestionParser()
try:
    questions = question_parser.parse_questions('data/documintv10.txt')
    main_logger.info(f"Parsed {len(questions)} questions at startup")
except Exception as e:
    main_logger.error(f"Error loading questions at startup: {str(e)}")
    questions = []

def convert_markdown_to_docx(markdown_content):
    with tempfile.NamedTemporaryFile(delete=False, suffix='.docx') as temp_docx:
        temp_docx_path = temp_docx.name
    
    try:
        # Convert markdown to docx
        pypandoc.convert_text(markdown_content, 'docx', format='md', outputfile=temp_docx_path)
        
        # Read the content of the temporary file
        with open(temp_docx_path, 'rb') as docx_file:
            docx_content = docx_file.read()
        
        return docx_content
    finally:
        # Ensure the temporary file is deleted
        os.unlink(temp_docx_path)

def main():
    st.title("DocuMint: AI-Powered Document Generator 📄")
    st.caption("Create professional PR documents for TSA")
    
    # Add sidebar for LLM selection
    st.sidebar.title("LLM Selection")
    llm_options = {
      "Claude Sonnet 3.5": "claude-3-5-sonnet-20240620",
      "Claude Opus": "claude-3-opus-20240229",
      "GPT-4o": "gpt-4o",
        "Llama 3": "llama3"
    }

    selected_llm = st.sidebar.selectbox(
      "Choose an LLM:",
      options=list(llm_options.keys()),
        index=0  # Default to Claude Sonnet 3.5
    )
    
    # Add user name input
    user_name = st.sidebar.text_input("Enter your name", value="DocuMint_User")
    
    selected_llm_model = llm_options[selected_llm]

    try:
        anthropic_api_key = os.getenv('ANTHROPIC_API_KEY')
        openai_api_key = os.getenv('OPENAI_API_KEY')
        if not anthropic_api_key:
            st.error("ANTHROPIC_API_KEY not found in environment variables")
            return
        if not openai_api_key and selected_llm == "GPT-4o":
          st.error("OPENAI_API_KEY not found in environment variables")
          return

        documint_orchestrator = create_documint_assistants(selected_llm_model, anthropic_api_key, openai_api_key)

        document_types = {
            "Statement of Work (SOW)": "templates/sow_template.txt",
            "Performance Work Statement (PWS)": "templates/pws_template.txt",
            "Statement of Objectives (SOO)": "templates/soo_template.txt"
        }

        selected_doc_type = st.selectbox("Select document type (Only SoW is supported for now):", list(document_types.keys()), key="doc_type_selector")
        st.write(f"You selected: {selected_doc_type}")

        template_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), document_types[selected_doc_type])
        template_parser = DocumentTemplateParser(template_path)

        st.subheader("Questionnaire")
        st.write(f"Loaded {len(questions)} questions")
        
        use_preload = st.checkbox("Use pre-loaded answers for testing", value=False, key="use_preload_checkbox")
        
        if use_preload:
            questionnaire_responses = create_questionnaire_with_preload(questions)
            if st.button("Submit Pre-loaded Questionnaire", key="submit_preload_button"):
                st.success("Pre-loaded questionnaire submitted successfully!")
        else:
            questionnaire_responses = create_questionnaire(questions)
        
        if questionnaire_responses:
            generate_button = st.button("Generate Document", key="generate_document_button")
            if generate_button:
                main_logger.info("Generate Document button clicked")
                with st.spinner(f"Generating {selected_doc_type}..."):
                    try:
                        main_logger.info(f"Starting document generation for {selected_doc_type}")
                        document_content = generate_document(
                            documint_orchestrator,
                            selected_doc_type,
                            template_parser.template_structure,
                            {str(q.id): questionnaire_responses[q.id] for q in questions},
                            {str(q.id): q.llm_hint for q in questions}
                        )
                        main_logger.info("Document generation completed")
                        if document_content:
                            st.subheader(f"Generated {selected_doc_type}")
                            st.text_area("Document Content", value=document_content, height=600, key="generated_document_content")
                            
                            # Create a filename-safe version of the LLM name and document type
                            safe_llm_name = selected_llm.replace(" ", "_").lower()
                            safe_doc_type = selected_doc_type.lower().replace(" ", "_").replace("(", "").replace(")", "")
                            
                            # Get current date and time
                            current_datetime = datetime.now().strftime("%Y%m%d_%H%M%S")
                            
                            # Base filename
                            base_filename = f"{safe_doc_type}_{safe_llm_name}_{user_name}_{current_datetime}"
                            
                            # Markdown download
                            st.download_button(
                                label=f"Download {selected_doc_type} as Markdown",
                                data=document_content,
                                file_name=f"{base_filename}.md",
                                mime="text/markdown",
                                key="download_markdown_button"
                            )
                            
                            # Plain text download
                            st.download_button(
                                label=f"Download {selected_doc_type} as Plain Text",
                                data=document_content,
                                file_name=f"{base_filename}.txt",
                                mime="text/plain",
                                key="download_text_button"
                            )
                            
                            # Word document download using pypandoc
                            try:
                                docx_content = convert_markdown_to_docx(document_content)
                                st.download_button(
                                    label=f"Download {selected_doc_type} as Word Document",
                                    data=docx_content,
                                    file_name=f"{base_filename}.docx",
                                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                                    key="download_word_button"
                                )
                                main_logger.info("Word document conversion successful")
                            except Exception as e:
                                st.error(f"Error converting to Word format: {str(e)}")
                                main_logger.error(f"Error converting to Word format: {str(e)}")
                            
                            main_logger.info("Document download buttons created")
                        else:
                            st.warning("No content was generated. Please try again.")
                            main_logger.warning("No content was generated")
                    except Exception as e:
                        st.error(f"Error generating document: {str(e)}")
                        main_logger.error(f"Error generating document: {str(e)}")

    except Exception as e:
        st.error(f"An unexpected error occurred: {str(e)}")
        main_logger.error(f"An unexpected error occurred: {str(e)}")

if __name__ == "__main__":
    main()