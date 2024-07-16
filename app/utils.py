# utils.py

import concurrent.futures
import logging
from typing import Dict, List, Tuple
from phi.assistant import Assistant
from phi.knowledge import AssistantKnowledge
from phi.vectordb.pineconedb import PineconeDB
import time
import os

from functools import lru_cache

from .sow_template import SOW_TEMPLATE, TEMPLATE_SECTIONS

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Retrieve API keys from environment variables
openai_api_key = os.getenv("OPENAI_API_KEY")
pinecone_api_key = os.getenv("PINECONE_API_KEY")

class SOWGenerationError(Exception):
    pass

questions = [
    "1. What is the official name of the project?",
    "2. Can you provide a brief history or background of the project?",
    "3. What is the primary purpose of this project?",
    "4. What are the main objectives the project aims to achieve?",
    "5. Who is the client (organization/department) for this project?",
    "6. What is the mission of the client organization?",
    "7. Can you describe the current operations that this project will support or enhance?",
    "8. What specific tasks and activities are within the scope of this project?",
    "9. Are there any tasks or activities explicitly out of scope?",
    "10. What are the key deliverables for this project? Please provide details for each.",
    "11. What are the critical milestones and their respective deadlines?",
    "12. What technologies, tools, and platforms will be used in this project?",
    "13. What type of data will be handled? Are there any specific data processing or storage requirements?",
    "14. Are there existing systems that need to be integrated with? If so, please provide details.",
    "15. What are the security requirements for the project? Are there any specific compliance standards to follow?",
    "16. How will data privacy be ensured throughout the project?",
    "17. Who are the key personnel involved in the project? What are their roles and responsibilities?",
    "18. What is the expected composition of the project team (e.g., developers, data scientists)?",
    "19. Are there any specific training requirements for project personnel?",
    "20. What are the potential risks associated with this project?",
    "21. What strategies will be employed to mitigate these risks?",
    "22. What metrics will be used to measure the success of the project?",
    "23. What are the reporting requirements (e.g., frequency, format)?",
    "24. What is the process for reviewing project deliverables?",
    "25. What are the criteria for approving deliverables and milestones?",
    "26. What are the key terms and conditions of the contract?",
    "27. Are there any specific compliance requirements that need to be adhered to?",
    "28. Are there any dependencies on other projects or initiatives?",
    "29. Are there any special considerations or circumstances that need to be taken into account?",
    "30. Can you detail the classification support services required (e.g., reviewing position descriptions, creating evaluation statements)?",
    "31. What specific data entry tasks and documentation processes are needed?",
    "32. What should be included in the weekly project status reports?",
    "33. How often will project status reviews be conducted and what should they cover?",
    "34. What security clearances and background checks are required for personnel?",
    "35. What information and resources will the government provide to the contractor?",
]        

sow_section_mapping = {
    "Template Header, PR#": ["1"],
    "Section I Task Name, Requisitioning Office": ["3", "4"],
    "Section II – Background": ["5", "6", "7", "8"],
    "Section III - Purpose": ["9", "10"],
    "Section IV – Technical Requirements": ["11", "12", "13", "14", "16"],
    "Contractor Personnel": ["23", "24", "25"],
    "Transition": ["27"],
    "Deliverables": ["20"],
    "Period of Performance": ["18", "19"],
    "Place of Performance": ["22"],
    "Delivery Instructions": ["21"],
    "Travel Requirements": ["17"],
    "GFE/GFI ": ["26"],
    "Special Security Requirements ": ["15"],
    "Section V – Applicable Documents ": ["28"],
}

def run_with_exponential_backoff(run_function, args: Tuple, max_retries: int = 5):
    """
    Attempts to run a function with exponential backoff in case of exceptions.

    Parameters:
    - run_function: The function to be executed.
    - args: Arguments to pass to the function.
    - max_retries: Maximum number of retries before raising the last exception.

    Returns:
    - The result of the function call if successful.
    """
    retry_delay = 1
    for attempt in range(max_retries):
        try:
            return run_function(*args)
        except Exception as e:
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
                retry_delay *= 2
            else:
                raise e

def get_qa_template(sow_section_mapping: Dict[str, List[int]], question_answer_trio: Tuple[int, str, str], section: str) -> str:
    """
    Generates a template string containing questions and answers for a specific section.

    Parameters:
    - sow_section_mapping: Mapping from sections to lists of question numbers.
    - question_answer_trio: Tuple containing question number, question, and answer.
    - section: The section for which the template is generated.

    Returns:
    - A formatted string with questions and answers for the section.
    """
    template = ""  # Initialize an empty string to build the template
    for question_number in sow_section_mapping[section]:  # Loop through each question number in the given section
        # Find the question corresponding to the current question number
        question = next(j for i, j, k in question_answer_trio if question_number == i)
        # Find the answer corresponding to the current question number
        answer = next(k for i, j, k in question_answer_trio if question_number == i)
        # Append the formatted question and answer to the template string
        template += f"Question {question_number}: \n{question}\n\nAnswer: \n{answer}\n\n"
    return template  # Return the completed template string

def generate_section(sow_section_mapping: Dict[str, List[int]], question_answer_trio: Tuple[int, str, str], section_to_fill: str, sow_section_details: str) -> str:
    """
    Generates the prompt for filling a section of the SOW.

    Parameters:
    - sow_section_mapping: Mapping from sections to lists of question numbers.
    - question_answer_trio: Tuple containing question number, question, and answer.
    - section_to_fill: The section name to fill.
    - sow_section_details: Pre-existing details of the section.

    Returns:
    - A prompt string for filling the section.
    """
    # Get the formatted questions and answers for the section to fill
    get_answers = get_qa_template(sow_section_mapping, question_answer_trio, section_to_fill)
    # Construct the prompt string with the section details and the questions and answers
    prompt = f"""
    Fill out this section:
    \n\n
    {section_to_fill}
    \n
    {sow_section_details}
    

    Using information below:
    \n\n
    {get_answers}
    """ 
    return prompt  # Return the constructed prompt string
def generate_sow(sow_section_mapping: Dict[str, List[int]], question_answer_trio: Tuple[int, str, str], project_context: Dict[str, str]) -> str:
    """
    Generates a Statement of Work (SOW) using given mappings and question-answer data.

    Parameters:
    - sow_section_mapping: Mapping from sections to lists of question numbers.
    - question_answer_trio: Tuple containing question number, question, and answer.

    Returns:
    - A refined and complete SOW as a string.
    """
    
    try:
        logger.info(f"Starting SOW generation for project: {project_context.get('project_name', 'Unknown')}")

        # Setup PineconeDB with necessary parameters and configurations
        vector_db = PineconeDB(
            name="sow-template",
            dimension=1536,
            metric="cosine",
            spec={"serverless": {"cloud": "aws", "region": "us-west-1"}},
            api_key=pinecone_api_key,
            namespace="main"
        )

        # Create an instance of AssistantKnowledge using the vector database
        knowledge_base = AssistantKnowledge(vector_db=vector_db)

        # Create a search assistant with specific instructions for text extraction from the knowledge base
        search_assistant = Assistant(
            instructions=[
                "You are an expert in developing Statement of Work (SOW) documents and project management.",
                "Given a search query, extract the most relevant and comprehensive information from the knowledge base.",
                "Focus on providing context-rich, detailed information that aligns with professional SOW standards.",
                "Ensure the extracted information is tailored to the specific section of the SOW being queried.",
                "If multiple relevant pieces of information are found, synthesize them into a coherent response.",
                "If no directly relevant information is found, provide the closest match and explain its potential relevance.",
                "Always consider the overall structure and flow of a professional SOW when providing information.",
            ],
            knowledge_base=knowledge_base,
            search_knowledge=True,
        )

        # Create a section writer assistant with instructions for filling in sections using answers
        sow_section_writer = Assistant(
            instructions=[
                "You are an expert Statement of Work (SOW) writer with extensive experience in various industries.",
                "Your task is to craft professional, detailed, and clear SOW sections based on the provided information.",
                "Follow these guidelines:",
                "1. Use formal, precise language appropriate for legal and business documents.",
                "2. Ensure each section is comprehensive, covering all necessary details without redundancy.",
                "3. Maintain consistency in tone, terminology, and format throughout the document.",
                "4. Tailor the content to the specific project, client, and industry context provided.",
                "5. Include specific, measurable, achievable, relevant, and time-bound (SMART) objectives where applicable.",
                "6. Clearly define deliverables, timelines, and responsibilities.",
                "7. Anticipate potential questions or ambiguities and address them proactively.",
                "8. Use industry-standard terminology and structure for each section.",
                "9. Ensure logical flow and coherence within and between sections.",
                "10. Highlight any assumptions, constraints, or dependencies relevant to the section.",
                "Use the provided information as a foundation, but apply your expertise to expand and refine the content as needed for a professional SOW."
            ],
        )
        
        sow_refiner = Assistant(
            instructions=[
                "You are a senior contract specialist and technical writer specializing in Statement of Work (SOW) documents.",
                "Your task is to refine and polish the provided SOW draft to meet the highest professional standards.",
                "Follow these guidelines:",
                "1. Ensure consistency in style, tone, and terminology throughout the document.",
                "2. Eliminate any redundancies or duplicate information.",
                "3. Verify that all sections are logically ordered and properly formatted.",
                "4. Create a detailed, accurate table of contents.",
                "5. Enhance clarity and precision of language, especially in technical or legal terms.",
                "6. Verify that all project objectives, deliverables, and timelines are clearly defined and aligned.",
                "7. Ensure that roles and responsibilities are unambiguously stated.",
                "8. Add or refine transition sentences between sections for improved flow.",
                "9. Verify that all referenced documents, standards, or regulations are accurately cited.",
                "10. Proofread for grammar, punctuation, and spelling errors.",
                "11. Ensure that the document adheres to any specified formatting requirements.",
                "12. Add any necessary disclaimers, confidentiality statements, or legal notices.",
                "13. Verify that all tables, figures, or appendices are properly labeled and referenced in the text.",
                "14. Ensure that the refined SOW is comprehensive, professional, and ready for client presentation.",
                "Return the refined SOW in proper Markdown format, maintaining professional document structure."
            ],
            markdown=True,
        )
        
        @lru_cache(maxsize=100)
        def cached_search(query: str) -> str:
            return search_assistant.run(query)

        def process_section(section: str) -> str:
            logger.info(f"Processing section: {section}")
            # Run the search assistant with exponential backoff to get section details
            section_details = run_with_exponential_backoff(cached_search, (section,))
            # section_details = run_with_exponential_backoff(search_assistant.run, (section,))
            # Generate the section prompt using the section details
            section_to_fill = generate_section(sow_section_mapping, question_answer_trio, section, section_details)
            # Run the section writer assistant with exponential backoff to get the filled section
            answered_section = run_with_exponential_backoff(sow_section_writer.run, (section_to_fill,))
            return answered_section  # Return the filled section
        
        def main() -> Dict[str, str]:
            sow_sections = {}
            sections = list(sow_section_mapping.keys())
            with concurrent.futures.ThreadPoolExecutor() as executor:
                results = list(executor.map(process_section, sections))
                for section, content in zip(sections, results):
                    sow_sections[section] = content
            return sow_sections

        sow_sections = main()
        
        # Dynamic mapping of generated sections to template structure
        template_mapping = {
            "project_name": project_context.get("project_name", ""),
            "table_of_contents": generate_table_of_contents(TEMPLATE_SECTIONS)
        }

        for section in TEMPLATE_SECTIONS:
            section_key = section.lower().replace(' ', '_')
            template_mapping[section_key] = sow_sections.get(section, "")

        raw_sow = SOW_TEMPLATE.format(**template_mapping)
        
        refined_sow = run_with_exponential_backoff(sow_refiner.run, (raw_sow,))  
        
        consistency_checker = Assistant(
            instructions=[
                "You are a SOW consistency expert. Review the entire document for:",
                "1. Consistent terminology and phrasing",
                "2. Alignment with project objectives and client requirements",
                "3. Logical flow and structure",
                "Provide a list of any inconsistencies or areas for improvement."
            ]
        )
        
        consistency_check = run_with_exponential_backoff(consistency_checker.run, (refined_sow,))
        if consistency_check:
            final_sow = run_with_exponential_backoff(sow_refiner.run, (refined_sow, consistency_check))
        else:
            final_sow = refined_sow

        logger.info("SOW generation completed successfully")
        return final_sow
    
    except Exception as e:
        logger.error(f"Error in generate_sow: {str(e)}")
        raise SOWGenerationError(f"Failed to generate SOW: {str(e)}")
    
    def generate_table_of_contents(sections: List[str]) -> str:
        toc = ""
        for i, section in enumerate(sections, start=1):
            toc += f"{i}. [{section}](#{section.lower().replace(' ', '-')})\n"
        return toc
    
          

#     def main() -> List[str]:
#         # Initialize an empty list to hold the completed sections of the SOW
#         sow = []
#         # Get the list of sections from the mapping keys
#         sections = list(sow_section_mapping.keys())

#         # Use ThreadPoolExecutor to process each section in parallel
#         with concurrent.futures.ThreadPoolExecutor() as executor:
#             # Map the process_section function to the list of sections and collect results
#             results = list(executor.map(process_section, sections))
#             sow.extend(results)  # Extend the SOW list with the processed sections

#         return sow  # Return the list of completed sections

#     # Run the main function to process all sections in parallel and join them into a single string
#     raw_sow = "\n\n".join(main())
    
#     # Create a SOW refiner assistant with instructions for refining and formatting the SOW
#     sow_refiner = Assistant(
#         instructions=[
#             "You are a senior contract specialist and technical writer specializing in Statement of Work (SOW) documents.",
#             "Your task is to refine and polish the provided SOW draft to meet the highest professional standards.",
#             "Follow these guidelines:",
#             "1. Ensure consistency in style, tone, and terminology throughout the document.",
#             "2. Eliminate any redundancies or duplicate information.",
#             "3. Verify that all sections are logically ordered and properly formatted.",
#             "4. Create a detailed, accurate table of contents.",
#             "5. Enhance clarity and precision of language, especially in technical or legal terms.",
#             "6. Verify that all project objectives, deliverables, and timelines are clearly defined and aligned.",
#             "7. Ensure that roles and responsibilities are unambiguously stated.",
#             "8. Add or refine transition sentences between sections for improved flow.",
#             "9. Verify that all referenced documents, standards, or regulations are accurately cited.",
#             "10. Proofread for grammar, punctuation, and spelling errors.",
#             "11. Ensure that the document adheres to any specified formatting requirements.",
#             "12. Add any necessary disclaimers, confidentiality statements, or legal notices.",
#             "13. Verify that all tables, figures, or appendices are properly labeled and referenced in the text.",
#             "14. Ensure that the refined SOW is comprehensive, professional, and ready for client presentation.",
#             "Return the refined SOW in proper Markdown format, maintaining professional document structure."
#         ],
#     markdown=True,
# )
    
#     # Run the SOW refiner assistant to get the refined SOW
#     refined_sow = sow_refiner.run(raw_sow, stream=False)    
    
#     return refined_sow  # Return the refined SOW