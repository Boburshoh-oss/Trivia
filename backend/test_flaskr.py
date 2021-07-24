import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy
from flaskr import create_app
from models import setup_db, Question, Category
from settings import DB_NAME, DB_USER, DB_PASSWORD

class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgresql://{}:{}@{}/{}".format(DB_USER,DB_PASSWORD,'localhost:5432', DB_NAME)
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()

            self.new_question = {
                'question': 'Alifbeda nechta harf bor?',
                'answer': '31',
                'category': 5,
                'difficulty': 2,
            }

    def tearDown(self):
        """Executed after reach test"""
        pass

    def test_get_categories_success(self):
        response = self.client().get('/categories')
        data = json.loads(response.data)
        self.assertTrue(data['categories'])
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        
    def test_retrieve_questions(self):
        response = self.client().get('/questions')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['questions'])
        self.assertTrue(data['total_questions'])
        

    def test_422_question_does_not_exist(self):
        res = self.client().delete("/questions/1000")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertFalse(data['success'])
        self.assertEqual(data['message'], 'unprocessable')
        self.assertEqual(data['error'], 422)
        
    
    def test_delete_question_success(self):
        question = Question.query.order_by(Question.id.desc()).first()
        question_id = question.id

        response = self.client().delete('/questions/{}'.format(question_id))
        data = json.loads(response.data)

        question = Question.query.get(question_id)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['deleted'], question_id)
        self.assertIsNone(question)

    def test_delete_question_fail(self):
        res = self.client().delete('/questions/1000')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)

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
        self.assertEqual(data['message'], "resource not found")

    def test_create_question(self):
        res = self.client().post('/questions', json=self.new_question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
    

    def test_404_category_input_out_of_range(self):
        res = self.client().get('categories/100/questions')
        data = json.loads(res.data)

        self.assertEqual(data['error'], 404)
        self.assertEqual(data['success'], False)

    
    def test_get_next_question(self):
        res = self.client().post('/quizzes', json={
            "previous_questions":[],
            "quiz_category": {"id":0, "type":"All"}
            })
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertNotEqual(data['question'], None)

    def test_404_sent_requesting_beyond_valid_quiz_category(self):
        res = self.client().post('/quizzes', json={
            'previous_questions':[],
            'quiz_category': {'id':1000, 'type':"test"}
            })
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'unprocessable')

# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()