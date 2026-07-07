from flask import Flask, render_template, request, jsonify
from chatbot import SafeXChatbot
import logging

app = Flask(__name__)
chatbot = SafeXChatbot()

logging.basicConfig(level=logging.INFO)

@app.route('/')
def home():
    suggestions = chatbot.get_suggestions()
    return render_template('index.html', suggestions=suggestions)

@app.route('/chat', methods=['POST'])
def chat():
    try:
        user_message = request.json.get('message', '').strip()
        
        if not user_message:
            return jsonify({'error': 'Empty message'}), 400
        
        response = chatbot.get_response(user_message)
        
        app.logger.info(f"Query: {user_message} | Intent: {response['intent']} | Confidence: {response['confidence']}%")
        
        return jsonify(response)
        
    except Exception as e:
        app.logger.error(f"Error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=10000)