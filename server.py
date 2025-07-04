from flask import Flask, render_template, request, jsonify, redirect, url_for, session, flash
import requests
import os
import datetime
import logging
from functools import wraps

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Flask app initialization
app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Change this to a secure secret key

# Create directories if they don't exist
if not os.path.exists('docs'):
    os.makedirs('docs')
if not os.path.exists('uploads'):
    os.makedirs('uploads')

# Gemini API Configuration
GEMINI_API_KEY = "AIzaSyD5rl09d6lHsf1D7R6-A_M3xht06A2BeDY"
GEMINI_API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"

# Mock user database (in production, use a real database)
users = {
    'admin': {'password': 'admin123', 'name': 'Admin User'},
    'ahmar': {'password': '1234', 'name': 'Test User'}
}

# Mock settings database
user_settings = {
    'admin': {
        'username': 'admin',
        'language': 'en',
        'theme': 'dark',
        'assistant': {
            'name': 'JARVIS 2.0',
            'wake_word': 'Jarvis'
        },
        'response_style': {
            'concise': False,
            'emojis': True
        },
        'voice': {
            'speed': 1.0,
            'pitch': 1.0,
            'style': 'neutral'
        },
        'privacy': {
            'save_history': True,
            'voice_recording': False
        },
        'advanced': {
            'api_key': GEMINI_API_KEY,
            'model': 'gemini-pro'
        }
    }
}

# Mock task database
user_tasks = {
    'admin': [
        {
            'id': 1,
            'title': 'Complete project documentation',
            'description': 'Write documentation for the new features',
            'due_date': (datetime.datetime.now() + datetime.timedelta(days=1)).isoformat(),
            'category': 'work',
            'priority': 'high',
            'completed': False
        }
    ]
}

# Mock job history
job_history = {
    'admin': [
        {
            'id': 1,
            'title': 'Software Engineer',
            'company': 'Tech Corp',
            'applied_date': (datetime.datetime.now() - datetime.timedelta(days=30)).isoformat(),
            'status': 'Interview'
        }
    ]
}

# Login required decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

# Routes
@app.route('/')
@login_required
def home():
    return render_template('index.html', username=session.get('username'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username in users and users[username]['password'] == password:
            session['username'] = username
            flash('Login successful!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Invalid username or password', 'error')
            return render_template('login.html', error="Invalid credentials")
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    flash('You have been logged out', 'info')
    return redirect(url_for('login'))

@app.route('/jarvis')
@login_required
def jarvis():
    return render_template('index.html', username=session.get('username'))

@app.route('/task')
@login_required
def task():
    username = session.get('username')
    return render_template('task.html', username=username, tasks=user_tasks.get(username, []))

@app.route('/job')
@login_required
def job():
    username = session.get('username')
    return render_template('job.html', username=username, jobs=job_history.get(username, []))

@app.route('/settings')
@login_required
def settings():
    username = session.get('username')
    return render_template('settings.html', 
                         username=username,
                         settings=user_settings.get(username, user_settings['admin']))

@app.route('/history')
@login_required
def history():
    username = session.get('username')
    # Mock history data
    history_data = [
        (1, 'User', 'Command: What is the weather today?', 'Response: The weather is sunny with a high of 75°F.', datetime.datetime.now().isoformat()),
        (2, 'User', 'Command: Set a reminder for meeting', 'Response: Reminder set for meeting at 2 PM tomorrow.', (datetime.datetime.now() - datetime.timedelta(hours=1)).isoformat())
    ]
    return render_template('history.html', username=username, history=history_data)

@app.route('/about')
@login_required
def about():
    return render_template('about.html')

@app.route('/generate', methods=['POST'])
@login_required
def generate_response():
    try:
        prompt = request.form.get('prompt')
        user_id = request.form.get('user_id')
        context = request.form.get('context', '')

        if not prompt:
            return jsonify({"error": "Prompt is missing!"}), 400

        logger.info(f"Received prompt from {user_id}: {prompt}")

        # Prepare Gemini API request with context
        headers = {'Content-Type': 'application/json'}
        payload = {
            "contents": [{
                "parts": [{"text": f"{context}\n{prompt}"}]
            }]
        }

        # Make API request to Gemini
        response = requests.post(GEMINI_API_URL, headers=headers, json=payload)
        response.raise_for_status()

        # Parse Gemini response
        response_data = response.json()
        if 'candidates' not in response_data or not response_data['candidates']:
            return jsonify({"error": "No response from AI"}), 500

        gemini_reply = response_data['candidates'][0]['content']['parts'][0]['text']
        logger.info(f"Gemini response: {gemini_reply}")

        # Save response to a document
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"docs/response_{timestamp}.txt"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(f"Prompt:\n{prompt}\n\nResponse:\n{gemini_reply}")

        return jsonify({
            "response": gemini_reply,
            "timestamp": datetime.datetime.now().strftime("%H:%M:%S"),
            "file": filename
        })

    except requests.exceptions.RequestException as e:
        logger.error(f"API request failed: {e}")
        return jsonify({"error": "Failed to connect to Gemini API"}), 500
    except Exception as e:
        logger.error(f"Error generating response: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/upload', methods=['POST'])
@login_required
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    
    if file:
        filename = os.path.join('uploads', file.filename)
        file.save(filename)
        return jsonify({
            "message": "File uploaded successfully",
            "filename": filename
        })

@app.route('/save-task', methods=['POST'])
@login_required
def save_task():
    try:
        username = session.get('username')
        task_data = request.json
        
        if username not in user_tasks:
            user_tasks[username] = []
        
        task_id = len(user_tasks[username]) + 1
        task_data['id'] = task_id
        user_tasks[username].append(task_data)
        
        return jsonify({
            "status": "success",
            "message": "Task saved successfully",
            "task_id": task_id
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/update-settings', methods=['POST'])
@login_required
def update_settings():
    try:
        username = session.get('username')
        settings_data = request.json
        
        if username not in user_settings:
            user_settings[username] = user_settings['admin'].copy()
        
        # Update settings
        user_settings[username].update(settings_data)
        
        return jsonify({
            "status": "success",
            "message": "Settings updated successfully"
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/clear-history', methods=['POST'])
@login_required
def clear_history():
    # In a real app, this would clear the user's history from the database
    return jsonify({
        "status": "success",
        "message": "History cleared successfully"
    })

if __name__ == "__main__":
    app.run(debug=True, port=5000)