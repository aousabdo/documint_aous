import unittest
from app.question_parser import QuestionParser

class TestQuestionParser(unittest.TestCase):
    def setUp(self):
        self.parser = QuestionParser()
        self.test_file_path = 'tests/test_questions.docx'  # You'll need to create this test file

    def test_parse_questions(self):
        questions = self.parser.parse_questions(self.test_file_path)
        self.assertIsNotNone(questions)
        self.assertTrue(len(questions) > 0)
        
        # Test the first question
        first_question = questions[0]
        self.assertIsNotNone(first_question.text)
        self.assertIsNotNone(first_question.key)
        self.assertIsInstance(first_question.required, bool)

    def test_load_example_answers(self):
        example_answers = self.parser.load_example_answers([self.test_file_path])
        self.assertIsNotNone(example_answers)
        self.assertTrue(len(example_answers) > 0)

if __name__ == '__main__':
    unittest.main()