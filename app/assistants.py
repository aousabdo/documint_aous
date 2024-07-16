from phi.assistant import Assistant
from phi.llm.anthropic import Claude
from phi.llm.ollama import Ollama
from phi.llm.openai import OpenAIChat

from app.logger import assistant_logger
import os
import re

# Get API keys from environment variables
anthropic_api_key = os.environ.get('ANTHROPIC_API_KEY')
openai_api_key = os.getenv("OPENAI_API_KEY")

print(f"Anthropic API Key: {anthropic_api_key}")
print(f"OpenAI API Key: {openai_api_key}")

# Import the sow_section_mapping from utils.py
from app.utils import sow_section_mapping

def create_documint_assistants(model, anthropic_api_key=None, openai_api_key=None):
    assistant_logger.info("Creating DocuMint assistants")
    
    if model.startswith("claude"):
        llm = Claude(model=model, api_key=anthropic_api_key)
        assistant_logger.info(f"Using Claude LLM: {model}")
    elif model == "gpt-4o":
        # llm = OpenAIChat(model=model, api_key=openai_api_key, max_tokens=500, temperature=0.3)
        llm = OpenAIChat(model="gpt-4o")
        
        assistant_logger.info("Using GPT-4o LLM")
    elif model == "llama3":
        llm = Ollama(model=model)
        assistant_logger.info("Using Llama 3 LLM")
    else:
        raise ValueError(f"Unsupported model: {model}")
    
    documint_orchestrator = Assistant(  
        name="DocuMintOrchestrator",
        # llm=Claude(model="claude-3-5-sonnet-20240620", api_key=anthropic_api_key),
        llm=llm,
        description="Experienced procurement document orchestrator overseeing the entire generation process.",
        instructions=[
            "Coordinate the overall document generation process",
            "Generate procurement documents such as SOW, PWS, and SOO based on provided information",
            "Incorporate user responses from the questionnaire into the document",
            "Ensure all required sections are completed",
            "Maintain a professional tone and use appropriate terminology for DHS TSA procurement",
            "Adapt the content based on the specific document type (SOW, PWS, SOO)",
            "Do not include introductory phrases like 'Here's the generated content for...' in your output",
        ],
        markdown=True,
    )
    assistant_logger.info("DocuMint assistants created successfully")
    return documint_orchestrator

def clean_generated_content(content):
    # Remove introductory phrases
    content = re.sub(r"^Here's the generated (content|section) for.*?:\n", "", content, flags=re.IGNORECASE | re.MULTILINE)
    
    # Remove any remaining section headers (as we're adding them manually)
    content = re.sub(r"^#+\s+.*?\n", "", content, flags=re.MULTILINE)
    
    # Remove extra newlines
    content = re.sub(r"\n{3,}", "\n\n", content)
    
    return content.strip()

def generate_document(orchestrator, document_type, template_structure, questionnaire_responses, example_answers):
    assistant_logger.info(f"Starting document generation for {document_type}")
    
    full_document = ""
    
    for section, question_numbers in sow_section_mapping.items():
        assistant_logger.info(f"Generating section: {section}")
        
        section_responses = {
            q_num: questionnaire_responses.get(q_num, "") for q_num in question_numbers
        }
        section_examples = {
            q_num: example_answers.get(q_num, "") for q_num in question_numbers
        }
        
        # Find the relevant template structure for this section
        relevant_structure = next((item for item in template_structure if item['title'] == section), None)
        structure_content = relevant_structure['content'] if relevant_structure else "No specific structure provided"
        
        prompt = f"""
        Generate the '{section}' section of the {document_type} based on the following information:

        Section: {section}
        Relevant Template Structure: {structure_content}
        Questionnaire Responses: {section_responses}
        Example Answers: {section_examples}

        Please follow these guidelines:
        1. Focus only on generating content for the '{section}' section.
        2. Incorporate the relevant questionnaire responses into this section.
        3. Reference the example answers for style and content guidance.
        4. Ensure the section is complete and detailed.
        5. Maintain a professional tone and use appropriate terminology for DHS TSA procurement.
        6. Adapt the content based on the specific document type ({document_type}).
        7. Do not include any introductory phrases like "Here's the generated content for...".
        8. Start directly with the content of the section.

        Generate the complete content for this section, filling in any missing information with appropriate placeholder text.
        """

        try:
            response = orchestrator.run(prompt)
            assistant_logger.info(f"Generated content for section: {section}")
            
            if isinstance(response, str):
                section_content = response
            else:
                section_content = ''.join(response)
            
            # Clean the generated content
            cleaned_content = clean_generated_content(section_content)
            
            full_document += f"\n\n## {section}\n\n{cleaned_content}"
            
        except Exception as e:
            assistant_logger.error(f"Error generating section '{section}': {str(e)}")
            full_document += f"\n\n## {section}\n\nError generating this section."

    assistant_logger.info("Completed document generation")
    return full_document.strip()