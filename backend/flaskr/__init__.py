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
  
  
  @app.after_request
  def after_request(response):
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
    response.headers.add('Access-Control-Allow-Methods', 'GET,POST,DELETE')
    return response

  
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
 
  @app.route("/questions")
  def get_questions():
    # categories = Category.query.all()
    # categoriesDict = {}
    # for category in categories:
    #     categoriesDict[category.id] = category.type
    categories = Category.query.order_by(Category.id).all()
    categorie=get_categories_dict(categories)
    questions = Question.query.order_by(Question.difficulty).all()
    page_questions = paginate_questions(request, questions)

    if len(page_questions) is None:
      abort(404)
    
    return jsonify({
        'success':True,
      "questions": page_questions,
      "total_questions": len(questions),
      "categories": categorie,
      "current_category": 0
      })

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
 
  @app.route('/quizzes', methods=['POST'])
  def get_guesses():
        try:
            body = request.get_json()
            previous_questions = body.get('previous_questions', None)
            quiz_category = body.get('quiz_category', None)
            category_id = quiz_category['id']

            if category_id == 0:
                questions = Question.query.filter(
                    Question.id.notin_(previous_questions)).all()
            else:
                questions = Question.query.filter(
                    Question.id.notin_(previous_questions),
                    Question.category == category_id).all()
            question = None
            if(questions):
                question = random.choice(questions)

            return jsonify({
                'success': True,
                'question': question.format()
            })
        

        except Exception:
            abort(422)
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

  
  return app

    