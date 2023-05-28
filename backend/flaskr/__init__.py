from colorsys import rgb_to_hls
import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from random import randrange as rg

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    """
    @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
    """
    cors = CORS(app, resources={r"/*": {"origins": "*"}})

    """
    @TODO: Use the after_request decorator to set Access-Control-Allow
    """
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers',
                             'Content-Type,-Authorization')
        response.headers.add('Access-Control-Allow-Methods',
                             'GET, POST, PATCH, DELETE, OPTIONS')
        return response
    """
    @TODO:
    Create an endpoint to handle GET requests
    for all available categories.
    """
    @app.route('/categories',methods=['GET'])
    def get_categories():
     try:
        categories=Category.query.all()
        list_categories={category.id:category.type for category in categories}
     except:
      abort(400)
     return jsonify({
        "success":True,
        "code":200,
        "message":"OK",
        "categories":list_categories,
        "num_categories":len(list_categories)    
        })

    """
    @TODO:
    Create an endpoint to handle GET requests for questions,
    including pagination (every 10 questions).
    This endpoint should return a list of questions,
    number of total questions, current category, categories.

    TEST: At this point, when you start the application
    you should see questions and categories generated,
    ten questions per page and pagination at the bottom of the screen for three pages.
    Clicking on the page numbers should update the questions.
    """
    @app.route('/questions', methods=['GET'])
    def get_questions():
        all_questions = Question.query.order_by(Question.id).all()
        page = request.args.get('page', 1, type=int)

        # Setting start / end points based on static
        # QUESTIONS_PER_PAGE variable
        start = (page - 1) * QUESTIONS_PER_PAGE
        end = start + QUESTIONS_PER_PAGE

        # Applying pagination to incoming question set
        questions = [question.format() for question in all_questions]
        paginated_questions = questions[start:end]

        categories = Category.query.order_by(Category.type).all()

        if len(paginated_questions) == 0:
            abort(404)

        return jsonify({
            'success': True,
            'questions': paginated_questions,
            'total_questions': len(all_questions),
            'categories': {category.id: category.type
                           for category in categories},
            'current_category': None
        })

    
       

    """
    @TODO:
    Create an endpoint to DELETE question using a question ID.

    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page.
    """
    @app.route('/questions/<int:id>',methods=['DELETE'])
    def delete_questions(id):
      try:
        question=Question.query.get(id)
        if question is None:
         abort(404)
        question.delete()
      except:
        abort(405)
      list_questions=Question.query.all()
      
      questions=[q.format() for q in list_questions]
      return jsonify({
        "success":True,
        "code":200,
        "message":"OK",
        "deleted":id        
            })
    """
    @TODO:
    Create an endpoint to POST a new question,
    which will require the question and answer text,
    category, and difficulty score.

    TEST: When you submit a question on the "Add" tab,
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.
    """

    @app.route('/questions', methods=['POST'])
    def add_question():
        body = request.json
        if 'question' in body and 'answer' in body \
                and 'category' in body and 'difficulty' in body:
            question_body = body['question']
            answer = body['answer']
            category = body['category']
            difficulty = body['difficulty']

            question = Question(question_body, answer, category, difficulty)
            question.insert()
            return jsonify({
                'success': True,
                'question': question.id
            })
        else:
            abort(422)

    """
    @TODO:
    Create a POST endpoint to get questions based on a search term.
    It should return any questions for whom the search term
    is a substring of the question.

    TEST: Search by any phrase. The questions list will update to include
    only question that include that string within their question.
    Try using the word "title" to start.
    """
    @app.route('/questions/search', methods=['POST'])
    def search_questions():
        body = request.get_json()

        search_term = body.get('search_term')
        print(search_term)

        if search_term:
            search_results = Question.query.filter(
                Question.question.ilike(f'%{search_term}%')).all()

            return jsonify({
                'success': True,
                'questions': [question.format()
                              for question in search_results],
                'total_questions': len(search_results),
                'current_category': None
            })

        abort(404)

    """
    @TODO:
    Create a GET endpoint to get questions based on category.

    TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    """
    @app.route('/categories/<int:id>/questions',methods=['GET'])
     
    def get_questions_by_category(id):
        NBR_CATEGORIES=len(Category.query.all())  
        if id>NBR_CATEGORIES:
            abort(404)
        if id<1:
            abort(422)
        list_questions=Question.query.filter(Question.category==id).all()
        
        if list_questions is None: #case where page is not found
          abort(404)
        questions=[q.format() for q in list_questions]
        return jsonify({
            'questions':questions,
            'totalQuestions':len(list_questions),
            'currentCategory':questions[0]['category'],
            'success':True,
            'code':200,
            'message':'OK'
            })
        """
    @TODO:
    Create a POST endpoint to get questions to play the quiz.
    This endpoint should take category and previous question parameters
    and return a random questions within the given category,
    if provided, and that is not one of the previous questions.

    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not.
    """
    @app.route('/quizzes',methods=['POST'])
 
    def get_question_quizz():
        categories=Category.query.all()
        id_categories=[c.format()['id'] for c in categories]
        type_categories=[c.format()['type'] for c in categories]
        print(id_categories,type_categories)
        data = request.get_json()
    
    
    
        if 'quiz_category' not in data.keys() or 'previous_questions' not in data.keys():
            abort(400)
        previous_questions=data.get('previous_questions')
        if data.get('quiz_category')['id']==0:
      
            list_questions=Question.query.all()
      
      
        else:
            print(int(data.get('quiz_category')['id']) in id_categories)
            print(data.get('quiz_category')['type']in type_categories )
            if int(data.get('quiz_category')['id']) not in id_categories:
                abort(404)
        if data.get('quiz_category')['type'] not in type_categories:
         abort(404) 
        list_questions=Question.query.filter(Question.category==data.get('quiz_category')['id']).all()
        list_questions=[q.format() for q in list_questions]
    
        next_questions=[]
        for q in list_questions:
         if q['id'] not in previous_questions:
          next_questions.append(q) 
          print("Number of questions  : ",len(next_questions))
         if next_questions != []:
          i=rg(0,len(next_questions)) 
          currentQuestion=next_questions[i]
        else:
          currentQuestion=None  
        print("Current question  : ",currentQuestion)  
        return jsonify({
        'success':True,
        'message':'OK',
        'code':200,
        'question':currentQuestion,
        'previousQuestions':previous_questions
        })

        # this POST endpoint take category and add new category   
    @app.route('/newcategories',methods=['POST'])
    def add_category():
        data=request.get_json()
        cat=data.get('category')
        category=Category(type=cat)
        category.insert()
        categories=category.query.all()
        categories=[c.format() for c in categories]
        return jsonify({
        'success':True,
        'message':'OK',
        'code':200,
        'category':category.format(),
        'categories':categories
        })
    """
    @TODO:
    Create error handlers for all expected errors
    including 404 and 422.
    """
    @app.errorhandler(404)
    def not_found_error(error):
     return jsonify({
        'success':False,
        'error':404,
        'message':'Not Found!'}), 404

    @app.errorhandler(422)
    def server_error(error):
     return jsonify({
        'success':False,
        'error':422,
        'message':'Unprocessable!'}), 422
        
    @app.errorhandler(400)
    def bad_request(error):
     return jsonify({
            'success': False,
            'error': 400,
            'message': 'Bad request'
        }),400

    @app.errorhandler(405)
    def not_allowed(error):
     return jsonify({
            'success': False,
            'error': 405,
            'message': 'not alowed'

        }),405

    @app.errorhandler(500)
    def not_allowed(error):
     return jsonify({
            'success': False,
            'error': 500,
            'message': 'Problem in Server crash !'

        }),500
    return app

