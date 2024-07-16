import re
from app.logger import parser_logger

class DocumentTemplateParser:
    def __init__(self, template_path):
        self.template_path = template_path
        self.template_content = self.load_template()
        self.template_structure = self.parse_template_structure()

    def load_template(self):
        parser_logger.info(f"Loading template from {self.template_path}")
        try:
            with open(self.template_path, 'r', encoding='utf-8') as file:
                return file.read()
        except FileNotFoundError:
            parser_logger.error(f"Template file not found: {self.template_path}")
            raise
        except Exception as e:
            parser_logger.error(f"Error loading template: {str(e)}")
            raise

    def parse_template_structure(self):
        parser_logger.info("Parsing template structure")
        structure = []
        lines = self.template_content.split('\n')
        current_section = None

        for line in lines:
            if line.startswith('# '):
                if current_section:
                    structure.append(current_section)
                current_section = {'title': line[2:].strip(), 'content': [], 'subsections': []}
            elif line.startswith('## '):
                if current_section:
                    structure.append(current_section)
                current_section = {'title': line[3:].strip(), 'content': [], 'subsections': []}
            elif line.startswith('### '):
                if current_section:
                    current_section['subsections'].append({'title': line[4:].strip(), 'content': []})
            elif current_section:
                if current_section['subsections']:
                    current_section['subsections'][-1]['content'].append(line)
                else:
                    current_section['content'].append(line)

        if current_section:
            structure.append(current_section)

        parser_logger.info(f"Parsed {len(structure)} main sections")
        return structure

    def fill_template(self, data):
        parser_logger.info("Filling template with data")
        try:
            if isinstance(data, str):
                # If data is a string, assume it's the full content and return it
                return data
            elif isinstance(data, dict):
                filled_content = self.template_content
                for key, value in data.items():
                    placeholder = f'{{{{{key}}}}}'
                    filled_content = filled_content.replace(placeholder, str(value))
                return filled_content
            else:
                raise ValueError("Data must be either a string or a dictionary")
        except Exception as e:
            parser_logger.error(f"Error filling template: {str(e)}")
            raise