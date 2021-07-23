import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgres://{}/{}".format('localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)
        
        #new question
        
        self.new_question = {
            'question': "Uzbekiston davlati qachon mustaqil bo'ldi?",
            'answer': '1991-yil 1-sentabr',
            'difficulty': 3,
            'category': '3'
        }
        
        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """
    def test_get_categories(self):
        res = self.client().get('/categories')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['categories'])
    def test_get_paginated_questions(self):
        res = self.client().get('/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['questions'])
        # self.assertEqual(len(data['questions']), 18)
        self.assertTrue(len(data['questions']))

    def test_404_invalid_page_numbers(self):
        res = self.client().get('/questions?page=10000')
        data = json.loads(res.data)
        
        self.assertEqual(data['error'], 404)
        self.assertEqual(data['success'], False)
    def test_delete_question(self):
        """Tests question deletion success"""

        # create a new question to be deleted
        question = Question(question=self.new_question['question'], answer=self.new_question['answer'],
                            category=self.new_question['category'], difficulty=self.new_question['difficulty'])
        question.insert()

        # get the id of the new question
        q_id = question.id

        # get number of questions before delete
        questions_before = Question.query.all()

        # delete the question and store response
        response = self.client().delete('/questions/{}'.format(q_id))
        data = json.loads(response.data)

        # get number of questions after delete
        questions_after = Question.query.all()

        # see if the question has been deleted
        question = Question.query.filter(Question.id == 1).one_or_none()

        # check status code and success message
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)

        # check if question id matches deleted id
        self.assertEqual(data['deleted'], q_id)

        # check if one less question after delete
        self.assertTrue(len(questions_before) - len(questions_after) == 1)

        # check if question equals None after delete
        self.assertEqual(question, None)
    def test_create_question(self):
        new_question = {
        'question': 'What is the color of the sky?',
        'answer': 'blue',
        'category': '1',
        'difficulty': 1,
        }

        res = self.client().post('/questions', json=new_question)
        data = json.loads(res.data)

        self.assertEqual(data['success'], True)
        self.assertTrue(data['created'])
    def test_422_cannot_create_question(self):
        bad_question = {
        'question': 'What is the day after Sunday?',
        'category': '1',
        'answer':'',
        'difficulty': 1,
        }

        res = self.client().post('/questions', json=bad_question)
        data = json.loads(res.data)

        self.assertEqual(data['success'], False)
        self.assertEqual(data['error'], 422)
        self.assertEqual(data['message'], "unprocessable. Synax error.")
    def test_422_if_question_to_delete_does_not_exist(self):
        res = self.client().delete('/questions/1000')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Not Processable')
    def search_question(self):
        res = self.client().post('questions/search', json={"searchTerm": "title"})
        data = json.loads(res.data)

        self.assertEqual(data['success'], True)
        self.assertTrue(data['questions'])
        self.assertTrue(data['total_questions'])
    def test_404_invalid_search_input(self):
        res = self.client().post('questions/search', json={"searchTerm": "beer"})
        data = json.loads(res.data)

        self.assertEqual(data['success'], False)
        self.assertEqual(data['error'], 404)
        self.assertEqual(data['message'], "Resource not found. Input out of range.")
    def test_get_quiz(self):
        res = self.client().post('/quizzes',
                                json={'previous_questions': [],
                                    'quiz_category':
                                    {'id': '5', 'type': 'Entertainment'}})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['question'])
        self.assertEqual(data['question']['category'], 5)
    def test_422_get_quiz(self):
        res = self.client().post('/quizzes',
                                json={
                                    'previous_questions': []
                                })
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Not Processable')
    
# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()