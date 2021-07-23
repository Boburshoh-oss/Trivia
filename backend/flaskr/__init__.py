import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random
from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10
def paginate_questions(request,selection):
  current_questions = []
  page = request.args.get('page',1,type=int)
  start = (page-1)*QUESTIONS_PER_PAGE 
  end = start + QUESTIONS_PER_PAGE
  questions = [question.format() for question in selection]
  current_questions = questions[start:end]
  return current_questions

#returns a dictionary of {id:type} for all available categories
def get_all_categories():
    categories = Category.query.order_by(Category.id).all()
    return {cat.id: cat.type for cat in categories}
def get_categories_dict(categories):
  categories_dict = {}
  for category in categories:
    categories_dict[category.id] = category.type
  return(categories_dict)

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)
  
  '''
  @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
  '''
  CORS(app, resources={r"/*": {"origins": "*"}})
  # CORS Headers 
  
  '''
  @TODO: Use the after_request decorator to set Access-Control-Allow
  '''
  @app.after_request
  def after_request(response):
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
    response.headers.add('Access-Control-Allow-Methods', 'GET,POST,DELETE')
    return response

  '''
  @TODO: 
  Create an endpoint to handle GET requests 
  for all available categories.
  '''
  @app.route('/categories')
  def get_categories():
    categories = Category.query.all()
    categoriesDict = {}
    for category in categories:
        categoriesDict[category.id] = category.type

    return jsonify({
        'success': True,
        'categories': categoriesDict
    })

  '''
  @TODO: 
  Create an endpoint to handle GET requests for questions, 
  including pagination (every 10 questions). 
  This endpoint should return a list of questions, 
  number of total questions, current category, categories. 

  TEST: At this point, when you start the application
  you should see questions and categories generated,
  ten questions per page and pagination at the bottom of the screen for three pages.
  Clicking on the page numbers should update the questions. 
  '''
  @app.route("/categories/<category_id>/questions")
  def get_category_by_id(category_id):
    questions = Question.query.filter(Question.category == category_id).order_by(Question.difficulty).all()
    page_questions = paginate_questions(request, questions)

    if len(page_questions) < 1:
      abort(404)

    return jsonify({
      "questions":page_questions,
      "total_questions": len(questions),
      "current_category":category_id
      })
  '''
  @TODO: 
  Create an endpoint to DELETE question using a question ID. 

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page. 
  '''
  @app.route("/questions")
  def get_questions():
    categories =  get_all_categories()
    questions = Question.query.order_by(Question.difficulty).all()
    page_questions = paginate_questions(request, questions)

    if len(page_questions) is None:
      abort(404)
    
    return jsonify({
      "questions": page_questions,
      "total_questions": len(questions),
      "categories": categories,
      "current_category": 0
      })
  '''
  @TODO: 
  Create an endpoint to POST a new question, 
  which will require the question and answer text, 
  category, and difficulty score.
  
  TEST: When you submit a question on the "Add" tab, 
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.  
  '''
  @app.route('/questions/<int:id>', methods=['DELETE'])
  def delete_question(id):
      '''
      Handles DELETE requests for deleting a question by id.
      '''

      try:
          # get the question by id
          question = Question.query.filter_by(id=id).one_or_none()

          # abort 404 if no question found
          if question is None:
              abort(404)

          # delete the question
          question.delete()

          # return success response
          return jsonify({
              'success': True,
              'deleted': id
          })

      except:
          # abort if problem deleting question
          abort(422)
  '''
  @TODO: 
  Create a POST endpoint to get questions based on a search term. 
  It should return any questions for whom the search term 
  is a substring of the question. 

  TEST: Search by any phrase. The questions list will update to include 
  only question that include that string within their question. 
  Try using the word "title" to start. 
  '''
  @app.route('/questions', methods=['POST'])
  def create_question():
      body = request.get_json()
      new_question = body.get('question', None)
      new_answer = body.get('answer', None)
      new_category = body.get('category', None)
      new_difficulty = body.get('difficulty', None)
      search = body.get('searchTerm', None)

      try:
          if search:
              questions = Question.query.filter(
                  Question.question.ilike(f'%{search}%')
              ).all()

              current_questions = [question.format()
                                    for question in questions]
              return jsonify({
                  'success': True,
                  'questions': current_questions,
                  'total_questions': len(current_questions),
              })

          else:
              question = Question(
                  question=new_question,
                  answer=new_answer,
                  category=new_category,
                  difficulty=new_difficulty
              )
              question.insert()

              selection = Question.query.order_by(Question.id).all()
              current_questions = paginate_questions(request, selection)

              return jsonify({
                  'success': True,
                  'questions': current_questions,
                  'total_questions': len(Question.query.all())
              })
      except Exception:
          abort(422)
  '''
  @TODO: 
  Create a GET endpoint to get questions based on category. 

  TEST: In the "List" tab / main screen, clicking on one of the 
  categories in the left column will cause only questions of that 
  category to be shown. 
  '''
  @app.route('/quizzes', methods=['POST'])
  def get_guesses():
      body = request.get_json()

      if body == None or 'quiz_category' not in body.keys():
          return abort(422)

      previous_questions = []
      if 'previous_questions' in body.keys():
          previous_questions = body['previous_questions']

      question = Question.query.filter(
          Question.category == body['quiz_category']['id'], Question.id.notin_(previous_questions)).first()

      return jsonify({
          "success": True,
          "question": question.format() if question != None else None
      })
  # error handlers

  @app.errorhandler(404)
  def not_found(error):
      return jsonify({
          "success": False,
          "error": 404,
          "message": "resource not found"
      }), 404

  @app.errorhandler(422)
  def unprocessable(error):
      return jsonify({
          "success": False,
          "error": 422,
          "message": "unprocessable"
      }), 422

  @app.errorhandler(500)
  def unprocessable(error):
      return jsonify({
          "success": False,
          "error": 500,
          "message": 'unprocessable'
      }), 500

    
  '''
  @TODO: 
  Create a POST endpoint to get questions to play the quiz. 
  This endpoint should take category and previous question parameters 
  and return a random questions within the given category, 
  if provided, and that is not one of the previous questions. 

  TEST: In the "Play" tab, after a user selects "All" or a category,
  one question at a time is displayed, the user is allowed to answer
  and shown whether they were correct or not. 
  '''

  '''
  @TODO: 
  Create error handlers for all expected errors 
  including 404 and 422. 
  '''
  
  return app

    