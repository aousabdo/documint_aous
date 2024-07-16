import re
import json
from app.logger import parser_logger

class Question:
    def __init__(self, id, text, user_hint, llm_hint, required):
        self.id = id
        self.text = text
        self.user_hint = user_hint
        self.llm_hint = llm_hint
        self.required = required

class QuestionParser:
    @staticmethod
    def split_questions(text):
        question_pattern = re.compile(r'(\d+\..*?(@Optional|@Required))', re.DOTALL)
        questions = question_pattern.findall(text)
        return [q[0].strip() for q in questions]

    @staticmethod
    def extract_metadata(block):
        metadata = {
            'userHint': '',
            'llmHint': '',
            'required': False
        }

        user_match = re.search(r'@User:\s*(.*?)(?=@LLM:|@Optional|@Required)', block, re.DOTALL)
        if user_match:
            metadata['userHint'] = user_match.group(1).strip()

        llm_match = re.search(r'@LLM:\s*(.*?)(?=@Optional|@Required)', block, re.DOTALL)
        if llm_match:
            metadata['llmHint'] = llm_match.group(1).strip()

        metadata['required'] = '@Required' in block

        return metadata

    @staticmethod
    def parse_question(question_block):
        id_match = re.match(r'(\d+)\.\s*(.*?)(?=@User:|@LLM:|@Required|@Optional)', question_block, re.DOTALL)
        if not id_match:
            return None

        question_id = int(id_match.group(1).strip())
        question_text = id_match.group(2).strip()
        metadata = QuestionParser.extract_metadata(question_block)

        return Question(
            id=question_id,
            text=question_text,
            user_hint=metadata['userHint'],
            llm_hint=metadata['llmHint'],
            required=metadata['required']
        )

    @staticmethod
    def parse_questions(file_path):
        parser_logger.info(f"Parsing questions from {file_path}")
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                text_sample = file.read()

            questions = QuestionParser.split_questions(text_sample)
            parsed_questions = [QuestionParser.parse_question(q) for q in questions if QuestionParser.parse_question(q) is not None]
            
            parser_logger.info(f"Successfully parsed {len(parsed_questions)} questions")
            return parsed_questions
        except Exception as e:
            parser_logger.error(f"Error parsing questions: {str(e)}")
            raise

    @staticmethod
    def load_example_answers(file_path):
        # This method is no longer needed as example answers are included in the questions
        return {}