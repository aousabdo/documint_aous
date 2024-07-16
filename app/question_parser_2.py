import re
import json

class Question:
    def __init__(self, text, key, required, user_note, llm_example):
        self.text = text
        self.key = key
        self.required = required
        self.user_note = user_note
        self.llm_example = llm_example

def split_questions(text):
    question_pattern = re.compile(r'(\d+\..*?(@Optional|@Required))', re.DOTALL)
    questions = question_pattern.findall(text)
    return [q[0].strip() for q in questions]

def extract_metadata(block):
    metadata = {
        'user_note': '',
        'llm_example': '',
        'required': False
    }
    
    user_match = re.search(r'@User:\s*(.*?)(?=@LLM:|@Optional|@Required)', block, re.DOTALL)
    if user_match:
        metadata['user_note'] = user_match.group(1).strip()

    llm_match = re.search(r'@LLM:\s*(.*?)(?=@Optional|@Required)', block, re.DOTALL)
    if llm_match:
        metadata['llm_example'] = llm_match.group(1).strip()

    if '@Required' in block:
        metadata['required'] = True

    return metadata

def parse_question(question_block):
    id_match = re.match(r'(\d+)\.\s*(.*?)(?=@User:|@LLM:|@Required|@Optional)', question_block, re.DOTALL)
    if not id_match:
        return None

    question_id = int(id_match.group(1).strip())
    question_text = id_match.group(2).strip()
    metadata = extract_metadata(question_block)

    return Question(
        text=question_text,
        key=f"q{question_id}",
        required=metadata['required'],
        user_note=metadata['user_note'],
        llm_example=metadata['llm_example']
    )

def parse_questions(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        text_sample = file.read()

    questions = split_questions(text_sample)
    parsed_questions = [parse_question(q) for q in questions if parse_question(q) is not None]
    return parsed_questions

def load_example_answers(file_paths):
    example_answers = {}
    for file_path in file_paths:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
            current_key = None
            current_answer = ""

            for line in content.split('\n'):
                if line.startswith('@'):
                    if current_key:
                        example_answers[current_key] = current_answer.strip()
                    current_key = line[1:].strip()
                    current_answer = ""
                else:
                    current_answer += line + " "

            if current_key:
                example_answers[current_key] = current_answer.strip()

    return example_answers

# Usage example:
if __name__ == "__main__":
    questions = parse_questions('../data/documintv10.txt')
    # example_answers = load_example_answers([
    #     'data/example_answers/answer1.txt',
    #     'data/example_answers/answer2.txt',
    #     'data/example_answers/answer3.txt'
    # ])
    print(type(questions))

    # for question in questions:
    #     print(f"Question: {question.text}")
    #     print(f"Key: {question.key}")
    #     print(f"Required: {question.required}")
    #     print(f"User Note: {question.user_note}")
    #     print(f"LLM Example: {question.llm_example}")
    #     # print(f"Example Answer: {example_answers.get(question.key, 'N/A')}")
    #     print()
