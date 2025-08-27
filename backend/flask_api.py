from flask import Flask, request, jsonify
from flask_cors import CORS
from agent import FlaskPortfolioAgent
import os

app = Flask(__name__)
CORS(app)  # Enable React frontend to call this API

# Initialize your CrewAI agent
portfolio_agent = FlaskPortfolioAgent()

@app.route('/', methods=['GET'])
def home():
    return jsonify({
        'message': "Uday Kiran's Portfolio Agent API is running!",
        'status': 'active',
        'endpoints': ['/api/chat', '/api/health']
    })

@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        question = data.get('question', '')
        
        if not question:
            return jsonify({
                'response': 'Please ask me something!',
                'status': 'error'
            }), 400
        
        # Use your CrewAI agent
        result = portfolio_agent.process_chat_message(question)
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'response': 'Sorry, I encountered an error. Please try again!',
            'status': 'error',
            'error': str(e)
        }), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'agent': 'ready',
        'message': "Uday's Portfolio Agent is operational!"
    })

@app.route('/api/intro', methods=['GET'])
def get_intro():
    try:
        result = portfolio_agent.process_chat_message("Tell me about yourself briefly")
        return jsonify(result)
    except Exception as e:
        return jsonify({
            'response': 'Error getting introduction',
            'status': 'error'
        }), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') != 'production'
    app.run(debug=debug, host='0.0.0.0', port=port)


import time
from litellm import RateLimitError

def safe_answer(agent, question, retries=2, delay=4):
    for attempt in range(retries + 1):
        try:
            return agent.answer_question(question)
        except RateLimitError:
            if attempt < retries:
                time.sleep(delay * (attempt + 1))
            else:
                return "I'm a bit busy right now (rate-limited). Please try again in a minute."
        except Exception as e:
            return f"Error: {str(e)[:120]}"

