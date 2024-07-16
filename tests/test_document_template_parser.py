import unittest
from app.document_template_parser import DocumentTemplateParser
import os

class TestDocumentTemplateParser(unittest.TestCase):
    def setUp(self):
        self.test_template_path = 'tests/test_template.docx'  # You'll need to create this test file
        self.parser = DocumentTemplateParser(self.test_template_path)

    def test_parse_template_structure(self):
        structure = self.parser.template_structure
        self.assertIsNotNone(structure)
        self.assertTrue(len(structure) > 0)
        
        # Test the structure of the first section
        first_section = structure[0]
        self.assertIn('title', first_section)
        self.assertIn('content', first_section)
        self.assertIn('subsections', first_section)

    def test_fill_template(self):
        test_data = {
            'project_name': 'Test Project',
            'project_description': 'This is a test project description.'
        }
        filled_doc_path = self.parser.fill_template(test_data)
        
        self.assertTrue(os.path.exists(filled_doc_path))
        self.assertNotEqual(self.test_template_path, filled_doc_path)

        # Clean up the generated file
        os.remove(filled_doc_path)

if __name__ == '__main__':
    unittest.main()