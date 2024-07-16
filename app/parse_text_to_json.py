import re
import json

def split_questions(text):
    question_pattern = re.compile(r'(\d+\..*?(@Optional|@Required))', re.DOTALL)
    questions = question_pattern.findall(text)
    return [q[0].strip() for q in questions]

def extract_metadata(block):
    metadata = {
        'userHint': '',
        'llmHint': '',
        'optional': False,
        'required': False
    }

    user_match = re.search(r'@User:\s*(.*?)(?=@LLM:|@Optional|@Required)', block, re.DOTALL)
    if user_match:
        metadata['userHint'] = user_match.group(1).strip()

    llm_match = re.search(r'@LLM:\s*(.*?)(?=@Optional|@Required)', block, re.DOTALL)
    if llm_match:
        metadata['llmHint'] = llm_match.group(1).strip()

    if '@Required' in block:
        metadata['required'] = True
    elif '@Optional' in block:
        metadata['optional'] = True

    return metadata

def strip_question_number(question):
    return re.sub(r'^\d+\.\s*', '', question)

def parse_question(question_block):
    id_match = re.match(r'(\d+)\.\s*(.*?)(?=@User:|@LLM:|@Required|@Optional)', question_block, re.DOTALL)
    if not id_match:
        return None

    question_id = int(id_match.group(1).strip())
    question_text = id_match.group(2).strip()
    metadata = extract_metadata(question_block)

    return {
        'id': question_id,
        'question': question_text,
        'metadata': metadata
    }

def parse_text_to_json(text_sample):
    questions = split_questions(text_sample)
    parsed_questions = [parse_question(q) for q in questions if parse_question(q) is not None]
    return json.dumps(parsed_questions, indent=4)

# Read the text file
with open('../data/documintv10.txt', 'r', encoding='utf-8') as file:
    text_sample = file.read()

# Parse the text to JSON
parsed_json = parse_text_to_json(text_sample)

# Save the JSON to a file
output_json_file_path = '../data/documint10.json'
with open(output_json_file_path, 'w', encoding='utf-8') as json_file:
    json_file.write(parsed_json)

print(parsed_json)
