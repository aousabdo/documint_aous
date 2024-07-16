import unittest
from unittest.mock import patch
from app.assistants import create_documint_assistants, generate_document

class TestAssistants(unittest.TestCase):
    @patch('app.assistants.Claude')
    def test_create_documint_assistants(self, mock_claude):
        assistants = create_documint_assistants('fake_api_key')
        self.assertIsNotNone(assistants)
        self.assertEqual(mock_claude.call_count, 4)  # One for each assistant

    @patch('app.assistants.Assistant.run')
    def test_generate_document(self, mock_run):
        mock_run.return_value = "Generated document content"
        
        orchestrator = create_documint_assistants('fake_api_key')
        document_type = "Statement of Work (SOW)"
        template_structure = [{'title': 'Section 1', 'content': [], 'subsections': []}]
        questionnaire_responses = {'project_name': 'Test Project'}
        example_answers = {'project_name': 'Example Project Name'}

        result = generate_document(orchestrator, document_type, template_structure, questionnaire_responses, example_answers)
        
        self.assertEqual(result, "Generated document content")
        mock_run.assert_called_once()

if __name__ == '__main__':
    unittest.main()