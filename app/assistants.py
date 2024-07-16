from phi.assistant import Assistant
from phi.llm.anthropic import Claude
from textwrap import dedent
from app.logger import assistant_logger
import os

# Get API keys from environment variables
anthropic_api_key = os.environ.get('ANTHROPIC_API_KEY')

def create_documint_assistants(anthropic_api_key):
    assistant_logger.info("Creating DocuMint assistants")
    documint_orchestrator = Assistant(
        name="DocuMintOrchestrator",
        llm=Claude(model="claude-3-5-sonnet-20240620", api_key=anthropic_api_key),
        description="Experienced procurement document orchestrator overseeing the entire generation process.",
        instructions=[
            "Coordinate the overall document generation process",
            "Generate procurement documents such as SOW, PWS, and SOO based on provided information",
            "Incorporate user responses from the questionnaire into the document",
            "Ensure all required sections are completed",
            "Maintain a professional tone and use appropriate terminology for DHS TSA procurement",
            "Adapt the content based on the specific document type (SOW, PWS, SOO)",
        ],
        markdown=True,
    )
    assistant_logger.info("DocuMint assistants created successfully")
    return documint_orchestrator

def generate_document(orchestrator, document_type, template_structure, questionnaire_responses, example_answers):
    assistant_logger.info(f"Starting document generation for {document_type}")
    prompt = f"""
    Generate a {document_type} based on the following information:

    Document Type: {document_type}
    Template Structure: {template_structure}
    Questionnaire Responses: {questionnaire_responses}
    Example Answers: {example_answers}

    Please follow these guidelines:
    1. Use the template structure to organize the document.
    2. Incorporate the questionnaire responses into the appropriate sections.
    3. Reference the example answers for style and content guidance.
    4. Ensure all required sections are completed.
    5. Maintain a professional tone and use appropriate terminology for DHS TSA procurement.
    6. Adapt the content based on the specific document type (SOW, PWS, SOO).

    Generate the complete document content, filling in any missing information with appropriate placeholder text.
    """

    assistant_logger.info("Sending prompt to orchestrator")
    try:
        response = orchestrator.run(prompt)
        assistant_logger.info("Received response from orchestrator")
        
        # Ensure response is a string
        if isinstance(response, str):
            full_response = response
        else:
            full_response = ''.join(response)
        
        assistant_logger.info(f"Generated content (first 100 chars): {full_response[:100]}...")
        return full_response
    except Exception as e:
        assistant_logger.error(f"Error in generate_document: {str(e)}")
        raise

    assistant_logger.info(f"Starting document generation for {document_type}")
    prompt = f"""
    Generate a {document_type} based on the following information:

    Document Type: {document_type}
    Template Structure: {template_structure}
    Questionnaire Responses: {questionnaire_responses}
    Example Answers: {example_answers}

    Please follow these guidelines:
    1. Use the template structure to organize the document.
    2. Incorporate the questionnaire responses into the appropriate sections.
    3. Reference the example answers for style and content guidance.
    4. Ensure all required sections are completed.
    5. Maintain a professional tone and use appropriate terminology for DHS TSA procurement.
    6. Adapt the content based on the specific document type (SOW, PWS, SOO).

    Generate the complete document content, filling in any missing information with appropriate placeholder text.
    """

    assistant_logger.info("Sending prompt to orchestrator")
    try:
        response = orchestrator.run(prompt)
        assistant_logger.info("Received response from orchestrator")
        
        # Handle the response if it's a generator
        if hasattr(response, '__iter__') and not isinstance(response, str):
            full_response = ''.join(response)
        else:
            full_response = response
        
        assistant_logger.info(f"Generated content (first 100 chars): {full_response[:100]}...")
        return full_response
    except Exception as e:
        assistant_logger.error(f"Error in generate_document: {str(e)}")
        raise