from flask import Flask, render_template_string, request, redirect, url_for, session, flash, send_file
import json
import os
from datetime import datetime
from io import BytesIO
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.enums import TA_CENTER, TA_LEFT

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-this-in-production'

# File to store data
ADMINS_FILE = 'admins.json'
QUESTIONS_FILE = 'questions.json'
ANSWERS_FILE = 'user_answers.json'

# Initialize files if they don't exist
def init_files():
    if not os.path.exists(ADMINS_FILE):
        with open(ADMINS_FILE, 'w') as f:
            json.dump({}, f)
    if not os.path.exists(QUESTIONS_FILE):
        with open(QUESTIONS_FILE, 'w') as f:
            json.dump({}, f)
    if not os.path.exists(ANSWERS_FILE):
        with open(ANSWERS_FILE, 'w') as f:
            json.dump({}, f)
    
    # Migrate old data format to new format
    migrate_old_data()

def migrate_old_data():
    """Convert old list format to new dictionary format"""
    # Migrate questions
    try:
        with open(QUESTIONS_FILE, 'r') as f:
            data = json.load(f)
            if isinstance(data, list):  # Old format
                # Move old questions to a default admin
                new_data = {'default_admin': data}
                with open(QUESTIONS_FILE, 'w') as fw:
                    json.dump(new_data, fw, indent=2)
                
                # Create default admin if questions exist
                if data:
                    admins = load_admins()
                    if 'default_admin' not in admins:
                        admins['default_admin'] = {
                            'password': 'admin123',
                            'created_at': datetime.now().isoformat()
                        }
                        save_admins(admins)
    except:
        pass
    
    # Migrate answers
    try:
        with open(ANSWERS_FILE, 'r') as f:
            data = json.load(f)
            if isinstance(data, list):  # Old format
                # Move old answers to default admin
                new_data = {'default_admin': data}
                with open(ANSWERS_FILE, 'w') as fw:
                    json.dump(new_data, fw, indent=2)
    except:
        pass

# Load admins
def load_admins():
    with open(ADMINS_FILE, 'r') as f:
        return json.load(f)

# Save admins
def save_admins(admins):
    with open(ADMINS_FILE, 'w') as f:
        json.dump(admins, f, indent=2)

# Load questions
def load_questions():
    with open(QUESTIONS_FILE, 'r') as f:
        return json.load(f)

# Save questions
def save_questions(questions):
    with open(QUESTIONS_FILE, 'w') as f:
        json.dump(questions, f, indent=2)

# Load answers
def load_answers():
    with open(ANSWERS_FILE, 'r') as f:
        return json.load(f)

# Save answers
def save_answers(answers):
    with open(ANSWERS_FILE, 'w') as f:
        json.dump(answers, f, indent=2)

# HTML Templates
HOME_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Quiz System</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 50px auto;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }
        .container {
            background: white;
            padding: 40px;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        h1 {
            color: #333;
            text-align: center;
            margin-bottom: 30px;
        }
        .btn-container {
            display: flex;
            gap: 20px;
            justify-content: center;
            flex-wrap: wrap;
        }
        .btn {
            padding: 15px 30px;
            font-size: 18px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            text-decoration: none;
            color: white;
            transition: transform 0.2s;
        }
        .btn:hover {
            transform: translateY(-2px);
        }
        .btn-admin {
            background: #e74c3c;
        }
        .btn-user {
            background: #3498db;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>📚 Quiz Management System</h1>
        <div class="btn-container">
            <a href="{{ url_for('admin_login') }}" class="btn btn-admin">🔐 Admin Panel</a>
            <a href="{{ url_for('user_quiz') }}" class="btn btn-user">✏️ Take Quiz</a>
        </div>
    </div>
</body>
</html>
'''

ADMIN_LOGIN_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Admin Login</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 500px;
            margin: 50px auto;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }
        .container {
            background: white;
            padding: 40px;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        h2 {
            color: #333;
            text-align: center;
        }
        input {
            width: 100%;
            padding: 12px;
            margin: 10px 0;
            border: 1px solid #ddd;
            border-radius: 5px;
            box-sizing: border-box;
        }
        .btn {
            width: 100%;
            padding: 12px;
            background: #e74c3c;
            color: white;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-size: 16px;
            margin-top: 10px;
        }
        .btn:hover {
            background: #c0392b;
        }
        .back-link {
            display: block;
            text-align: center;
            margin-top: 20px;
            color: #667eea;
            text-decoration: none;
        }
        .flash {
            padding: 10px;
            margin: 10px 0;
            border-radius: 5px;
            background: #f8d7da;
            color: #721c24;
        }
        .flash.success {
            background: #d4edda;
            color: #155724;
        }
        .tab-links {
            display: flex;
            margin-bottom: 20px;
        }
        .tab-link {
            flex: 1;
            padding: 12px;
            text-align: center;
            cursor: pointer;
            background: #f0f0f0;
            border: none;
            border-bottom: 3px solid transparent;
        }
        .tab-link.active {
            background: white;
            border-bottom-color: #e74c3c;
            font-weight: bold;
        }
        .tab-content {
            display: none;
        }
        .tab-content.active {
            display: block;
        }
    </style>
    <script>
        function showTab(tabName) {
            document.querySelectorAll('.tab-content').forEach(tab => {
                tab.classList.remove('active');
            });
            document.querySelectorAll('.tab-link').forEach(link => {
                link.classList.remove('active');
            });
            document.getElementById(tabName).classList.add('active');
            event.target.classList.add('active');
        }
    </script>
</head>
<body>
    <div class="container">
        <h2>🔐 Admin Access</h2>
        
        {% with messages = get_flashed_messages(with_categories=true) %}
            {% if messages %}
                {% for category, message in messages %}
                    <div class="flash {{ category }}">{{ message }}</div>
                {% endfor %}
            {% endif %}
        {% endwith %}
        
        <div class="tab-links">
            <button class="tab-link active" onclick="showTab('login-tab')">Login</button>
            <button class="tab-link" onclick="showTab('register-tab')">Register</button>
        </div>
        
        <!-- Login Tab -->
        <div id="login-tab" class="tab-content active">
            <form method="POST" action="{{ url_for('admin_login') }}">
                <input type="hidden" name="action" value="login">
                <input type="text" name="username" placeholder="Username" required>
                <input type="password" name="password" placeholder="Password" required>
                <button type="submit" class="btn">Login</button>
            </form>
        </div>
        
        <!-- Register Tab -->
        <div id="register-tab" class="tab-content">
            <form method="POST" action="{{ url_for('admin_login') }}">
                <input type="hidden" name="action" value="register">
                <input type="text" name="username" placeholder="Choose Username" required>
                <input type="password" name="password" placeholder="Choose Password" required>
                <input type="password" name="confirm_password" placeholder="Confirm Password" required>
                <button type="submit" class="btn" style="background: #27ae60;">Create Admin Account</button>
            </form>
        </div>
        
        <a href="{{ url_for('home') }}" class="back-link">← Back to Home</a>
    </div>
</body>
</html>
'''

ADMIN_PANEL_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Admin Panel</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 1200px;
            margin: 20px auto;
            padding: 20px;
            background: #f5f5f5;
        }
        .container {
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }
        h2 {
            color: #333;
            border-bottom: 3px solid #e74c3c;
            padding-bottom: 10px;
        }
        .admin-info {
            background: #f0f0f0;
            padding: 10px 15px;
            border-radius: 5px;
            margin-bottom: 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .form-group {
            margin: 15px 0;
        }
        label {
            display: block;
            margin-bottom: 5px;
            font-weight: bold;
            color: #555;
        }
        input, textarea, select {
            width: 100%;
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 5px;
            box-sizing: border-box;
        }
        textarea {
            min-height: 100px;
            resize: vertical;
        }
        .btn {
            padding: 12px 24px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-size: 16px;
            margin: 5px;
            text-decoration: none;
            display: inline-block;
            color: white;
        }
        .btn-primary {
            background: #e74c3c;
        }
        .btn-secondary {
            background: #95a5a6;
        }
        .btn-success {
            background: #27ae60;
        }
        .btn-info {
            background: #3498db;
        }
        .btn:hover {
            opacity: 0.9;
        }
        .question-list {
            margin-top: 30px;
        }
        .question-item {
            background: #f9f9f9;
            padding: 15px;
            margin: 10px 0;
            border-radius: 5px;
            border-left: 4px solid #e74c3c;
        }
        .question-item h4 {
            margin: 0 0 10px 0;
            color: #333;
        }
        .options {
            margin: 10px 0;
            padding-left: 20px;
        }
        .correct {
            color: #27ae60;
            font-weight: bold;
        }
        .logout {
            float: right;
            background: #95a5a6;
        }
        .nav-tabs {
            display: flex;
            gap: 10px;
            margin-bottom: 20px;
            border-bottom: 2px solid #ddd;
        }
        .nav-tab {
            padding: 12px 24px;
            background: #f0f0f0;
            border: none;
            cursor: pointer;
            border-radius: 5px 5px 0 0;
            font-size: 16px;
        }
        .nav-tab.active {
            background: #e74c3c;
            color: white;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }
        th, td {
            padding: 12px;
            border: 1px solid #ddd;
            text-align: left;
        }
        th {
            background: #f0f0f0;
            font-weight: bold;
        }
        tr:hover {
            background: #f9f9f9;
        }
        .download-section {
            margin-top: 20px;
            padding: 15px;
            background: #e8f4f8;
            border-radius: 5px;
            text-align: center;
        }
    </style>
    <script>
        function showTab(tabName) {
            document.querySelectorAll('.tab-content').forEach(tab => {
                tab.style.display = 'none';
            });
            document.querySelectorAll('.nav-tab').forEach(btn => {
                btn.classList.remove('active');
            });
            document.getElementById(tabName).style.display = 'block';
            event.target.classList.add('active');
        }
    </script>
</head>
<body>
    <div class="container">
        <h2>📝 Admin Panel
            <a href="{{ url_for('logout') }}" class="btn btn-secondary logout">Logout</a>
        </h2>
        
        <div class="admin-info">
            <span><strong>Logged in as:</strong> {{ current_admin }}</span>
            <span><strong>Your Questions:</strong> {{ questions|length }} | <strong>Your Students:</strong> {{ student_results|length }}</span>
        </div>
        
        <div class="nav-tabs">
            <button class="nav-tab active" onclick="showTab('questions-tab')">📋 My Questions</button>
            <button class="nav-tab" onclick="showTab('results-tab')">📊 Student Results</button>
        </div>
        
        <!-- Questions Tab -->
        <div id="questions-tab" class="tab-content">
            <h3>Add New Question</h3>
            <form method="POST" action="{{ url_for('admin_panel') }}">
                <div class="form-group">
                    <label>Question:</label>
                    <textarea name="question" required></textarea>
                </div>
                
                <div class="form-group">
                    <label>Option A:</label>
                    <input type="text" name="option_a" required>
                </div>
                
                <div class="form-group">
                    <label>Option B:</label>
                    <input type="text" name="option_b" required>
                </div>
                
                <div class="form-group">
                    <label>Option C:</label>
                    <input type="text" name="option_c" required>
                </div>
                
                <div class="form-group">
                    <label>Option D:</label>
                    <input type="text" name="option_d" required>
                </div>
                
                <div class="form-group">
                    <label>Correct Answer:</label>
                    <select name="correct_answer" required>
                        <option value="A">A</option>
                        <option value="B">B</option>
                        <option value="C">C</option>
                        <option value="D">D</option>
                    </select>
                </div>
                
                <button type="submit" class="btn btn-primary">Add Question</button>
            </form>
            
            <div class="question-list">
                <h3>📋 My Questions ({{ questions|length }})</h3>
                {% if questions %}
                    {% for q in questions %}
                        <div class="question-item">
                            <h4>Q{{ loop.index }}: {{ q.question }}</h4>
                            <div class="options">
                                <div {% if q.correct_answer == 'A' %}class="correct"{% endif %}>A) {{ q.options.A }}</div>
                                <div {% if q.correct_answer == 'B' %}class="correct"{% endif %}>B) {{ q.options.B }}</div>
                                <div {% if q.correct_answer == 'C' %}class="correct"{% endif %}>C) {{ q.options.C }}</div>
                                <div {% if q.correct_answer == 'D' %}class="correct"{% endif %}>D) {{ q.options.D }}</div>
                            </div>
                            <form method="POST" action="{{ url_for('delete_question', index=loop.index0) }}" style="display: inline;">
                                <button type="submit" class="btn btn-secondary" onclick="return confirm('Delete this question?')">Delete</button>
                            </form>
                        </div>
                    {% endfor %}
                {% else %}
                    <p style="text-align: center; color: #888; padding: 20px;">No questions yet. Add your first question above!</p>
                {% endif %}
            </div>
        </div>
        
        <!-- Results Tab -->
        <div id="results-tab" class="tab-content" style="display: none;">
            <h3>📊 Student Results for My Quizzes ({{ student_results|length }} students)</h3>
            
            {% if student_results %}
                <table>
                    <thead>
                        <tr>
                            <th>Student Name</th>
                            <th style="text-align: center;">Score</th>
                            <th style="text-align: center;">Percentage</th>
                            <th style="text-align: center;">Date & Time</th>
                            <th style="text-align: center;">Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for result in student_results %}
                            <tr>
                                <td>{{ result.student_name }}</td>
                                <td style="text-align: center;"><strong>{{ result.score }} / {{ result.total }}</strong></td>
                                <td style="text-align: center;">
                                    <span style="color: {% if result.percentage >= 70 %}#27ae60{% elif result.percentage >= 50 %}#f39c12{% else %}#e74c3c{% endif %}; font-weight: bold;">
                                        {{ result.percentage }}%
                                    </span>
                                </td>
                                <td style="text-align: center; font-size: 12px;">{{ result.date }}<br>{{ result.time }}</td>
                                <td style="text-align: center;">
                                    <a href="{{ url_for('download_pdf', index=loop.index0) }}" class="btn btn-success">
                                        📥 PDF
                                    </a>
                                </td>
                            </tr>
                        {% endfor %}
                    </tbody>
                </table>
                
                <div class="download-section">
                    <h4>📊 Download All Results</h4>
                    <p>Export all student results to Excel spreadsheet</p>
                    <a href="{{ url_for('download_excel') }}" class="btn btn-info">
                        📥 Download Excel Report
                    </a>
                </div>
            {% else %}
                <p style="text-align: center; color: #888; padding: 40px;">No student results yet.</p>
            {% endif %}
        </div>
    </div>
</body>
</html>
'''

QUIZ_SELECT_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Select Quiz</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 50px auto;
            padding: 20px;
            background: linear-gradient(135deg, #3498db 0%, #2980b9 100%);
            min-height: 100vh;
        }
        .container {
            background: white;
            padding: 40px;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        h2 {
            color: #333;
            text-align: center;
            margin-bottom: 30px;
        }
        .quiz-card {
            background: #f9f9f9;
            padding: 20px;
            margin: 15px 0;
            border-radius: 8px;
            border-left: 4px solid #3498db;
            display: flex;
            justify-content: space-between;
            align-items: center;
            transition: transform 0.2s;
        }
        .quiz-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        }
        .quiz-info {
            flex: 1;
        }
        .quiz-info h3 {
            margin: 0 0 10px 0;
            color: #333;
        }
        .quiz-info p {
            margin: 5px 0;
            color: #666;
        }
        .btn {
            padding: 12px 30px;
            background: #3498db;
            color: white;
            text-decoration: none;
            border-radius: 5px;
            font-weight: bold;
            transition: background 0.3s;
        }
        .btn:hover {
            background: #2980b9;
        }
        .back-link {
            display: block;
            text-align: center;
            margin-top: 30px;
            color: #3498db;
            text-decoration: none;
            font-weight: bold;
        }
        .no-quizzes {
            text-align: center;
            padding: 60px 20px;
            color: #888;
        }
    </style>
</head>
<body>
    <div class="container">
        <h2>📚 Available Quizzes</h2>
        <p style="text-align: center; color: #666; margin-bottom: 30px;">Select a quiz to begin</p>
        
        {% if available_quizzes %}
            {% for quiz in available_quizzes %}
                <div class="quiz-card">
                    <div class="quiz-info">
                        <h3>{{ quiz.admin_name }}'s Quiz</h3>
                        <p>📝 <strong>{{ quiz.question_count }}</strong> questions</p>
                    </div>
                    <a href="{{ url_for('take_quiz', admin_id=quiz.admin_id) }}" class="btn">Start Quiz →</a>
                </div>
            {% endfor %}
        {% else %}
            <div class="no-quizzes">
                <h3>No quizzes available yet!</h3>
                <p>Please wait for administrators to create quizzes.</p>
            </div>
        {% endif %}
        
        <a href="{{ url_for('home') }}" class="back-link">← Back to Home</a>
    </div>
</body>
</html>
'''

USER_QUIZ_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Take Quiz</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 20px auto;
            padding: 20px;
            background: linear-gradient(135deg, #3498db 0%, #2980b9 100%);
            min-height: 100vh;
        }
        .container {
            background: white;
            padding: 40px;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        h2 {
            color: #333;
            text-align: center;
            margin-bottom: 30px;
        }
        .quiz-info {
            background: #f0f0f0;
            padding: 15px;
            border-radius: 5px;
            margin-bottom: 20px;
            text-align: center;
        }
        .question {
            background: #f9f9f9;
            padding: 20px;
            margin: 20px 0;
            border-radius: 5px;
            border-left: 4px solid #3498db;
        }
        .question h3 {
            color: #333;
            margin-bottom: 15px;
        }
        .options {
            margin: 10px 0;
        }
        .option {
            padding: 10px;
            margin: 8px 0;
            cursor: pointer;
            border: 2px solid #ddd;
            border-radius: 5px;
            transition: all 0.3s;
        }
        .option:hover {
            background: #e8f4f8;
            border-color: #3498db;
        }
        .option input {
            margin-right: 10px;
        }
        .btn {
            width: 100%;
            padding: 15px;
            background: #3498db;
            color: white;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-size: 18px;
            margin-top: 20px;
        }
        .btn:hover {
            background: #2980b9;
        }
        .back-link {
            display: block;
            text-align: center;
            margin-top: 20px;
            color: #3498db;
            text-decoration: none;
        }
        .name-input {
            width: 100%;
            padding: 12px;
            margin: 20px 0;
            border: 2px solid #ddd;
            border-radius: 5px;
            font-size: 16px;
        }
        .no-questions {
            text-align: center;
            padding: 40px;
            color: #888;
        }
    </style>
</head>
<body>
    <div class="container">
        <h2>✏️ Quiz Time!</h2>
        
        {% if questions %}
            <div class="quiz-info">
                <strong>Quiz by:</strong> {{ admin_name }} | <strong>Questions:</strong> {{ questions|length }}
            </div>
            
            <form method="POST" action="{{ url_for('submit_quiz') }}">
                <input type="text" name="student_name" class="name-input" placeholder="Enter your name" required>
                <input type="hidden" name="admin_id" value="{{ admin_id }}">
                
                {% for q in questions %}
                    <div class="question">
                        <h3>Question {{ loop.index }}: {{ q.question }}</h3>
                        <div class="options">
                            <label class="option">
                                <input type="radio" name="q{{ loop.index0 }}" value="A" required>
                                A) {{ q.options.A }}
                            </label>
                            <label class="option">
                                <input type="radio" name="q{{ loop.index0 }}" value="B">
                                B) {{ q.options.B }}
                            </label>
                            <label class="option">
                                <input type="radio" name="q{{ loop.index0 }}" value="C">
                                C) {{ q.options.C }}
                            </label>
                            <label class="option">
                                <input type="radio" name="q{{ loop.index0 }}" value="D">
                                D) {{ q.options.D }}
                            </label>
                        </div>
                    </div>
                {% endfor %}
                
                <button type="submit" class="btn">Submit Quiz</button>
            </form>
        {% else %}
            <div class="no-questions">
                <h3>No questions available yet!</h3>
                <p>This admin hasn't added questions yet.</p>
            </div>
        {% endif %}
        
        <a href="{{ url_for('user_quiz') }}" class="back-link">← Back to Quiz Selection</a>
    </div>
</body>
</html>
'''

RESULTS_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Quiz Results</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 20px auto;
            padding: 20px;
            background: linear-gradient(135deg, #27ae60 0%, #229954 100%);
            min-height: 100vh;
        }
        .container {
            background: white;
            padding: 40px;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        h2 {
            color: #333;
            text-align: center;
        }
        .score {
            text-align: center;
            font-size: 48px;
            color: #27ae60;
            margin: 30px 0;
        }
        .result-item {
            background: #f9f9f9;
            padding: 15px;
            margin: 15px 0;
            border-radius: 5px;
        }
        .correct {
            border-left: 4px solid #27ae60;
        }
        .incorrect {
            border-left: 4px solid #e74c3c;
        }
        .question-text {
            font-weight: bold;
            margin-bottom: 10px;
        }
        .answer-comparison {
            margin: 5px 0;
        }
        .your-answer {
            color: #e74c3c;
        }
        .correct-answer {
            color: #27ae60;
        }
        .btn {
            display: block;
            width: 200px;
            margin: 20px auto;
            padding: 12px;
            background: #3498db;
            color: white;
            text-align: center;
            text-decoration: none;
            border-radius: 5px;
        }
        .btn:hover {
            background: #2980b9;
        }
    </style>
</head>
<body>
    <div class="container">
        <h2>🎉 Quiz Results</h2>
        <h3 style="text-align: center;">Student: {{ student_name }}</h3>
        <div class="score">{{ score }} / {{ total }}</div>
        <p style="text-align: center; font-size: 20px;">
            Percentage: {{ percentage }}%
        </p>
        
        <h3>Detailed Results:</h3>
        {% for item in results %}
            <div class="result-item {% if item.correct %}correct{% else %}incorrect{% endif %}">
                <div class="question-text">Q{{ loop.index }}: {{ item.question }}</div>
                <div class="answer-comparison">
                    <span class="your-answer">Your answer: {{ item.user_answer }}</span>
                </div>
                {% if not item.correct %}
                    <div class="answer-comparison">
                        <span class="correct-answer">Correct answer: {{ item.correct_answer }}</span>
                    </div>
                {% endif %}
            </div>
        {% endfor %}
        
        <a href="{{ url_for('home') }}" class="btn">Back to Home</a>
    </div>
</body>
</html>
'''

# Routes
@app.route('/')
def home():
    init_files()
    return render_template_string(HOME_TEMPLATE)

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        action = request.form.get('action')
        username = request.form.get('username')
        password = request.form.get('password')
        
        admins = load_admins()
        
        if action == 'register':
            confirm_password = request.form.get('confirm_password')
            
            if password != confirm_password:
                flash('Passwords do not match!', 'error')
                return redirect(url_for('admin_login'))
            
            if username in admins:
                flash('Username already exists!', 'error')
                return redirect(url_for('admin_login'))
            
            # Create new admin
            admins[username] = {
                'password': password,
                'created_at': datetime.now().isoformat()
            }
            save_admins(admins)
            
            flash('Admin account created successfully! Please login.', 'success')
            return redirect(url_for('admin_login'))
        
        elif action == 'login':
            if username in admins and admins[username]['password'] == password:
                session['admin'] = username
                return redirect(url_for('admin_panel'))
            else:
                flash('Invalid username or password!', 'error')
    
    return render_template_string(ADMIN_LOGIN_TEMPLATE)

@app.route('/admin/panel', methods=['GET', 'POST'])
def admin_panel():
    if 'admin' not in session:
        return redirect(url_for('admin_login'))
    
    current_admin = session['admin']
    all_questions = load_questions()
    
    # Get questions for current admin only
    admin_questions = all_questions.get(current_admin, [])
    
    if request.method == 'POST':
        question = {
            'question': request.form.get('question'),
            'options': {
                'A': request.form.get('option_a'),
                'B': request.form.get('option_b'),
                'C': request.form.get('option_c'),
                'D': request.form.get('option_d')
            },
            'correct_answer': request.form.get('correct_answer')
        }
        
        admin_questions.append(question)
        all_questions[current_admin] = admin_questions
        save_questions(all_questions)
        
        return redirect(url_for('admin_panel'))
    
    # Get answers for current admin's quizzes
    all_answers = load_answers()
    admin_answers = all_answers.get(current_admin, [])
    
    # Process student results for display
    student_results = []
    for answer in admin_answers:
        timestamp = datetime.fromisoformat(answer['timestamp'])
        percentage = round((answer['score'] / answer['total']) * 100, 2) if answer['total'] > 0 else 0
        student_results.append({
            'student_name': answer['student_name'],
            'score': answer['score'],
            'total': answer['total'],
            'percentage': percentage,
            'date': timestamp.strftime('%Y-%m-%d'),
            'time': timestamp.strftime('%I:%M %p')
        })
    
    return render_template_string(ADMIN_PANEL_TEMPLATE, 
                                 current_admin=current_admin,
                                 questions=admin_questions,
                                 student_results=student_results)

@app.route('/admin/delete/<int:index>', methods=['POST'])
def delete_question(index):
    if 'admin' not in session:
        return redirect(url_for('admin_login'))
    
    current_admin = session['admin']
    all_questions = load_questions()
    admin_questions = all_questions.get(current_admin, [])
    
    if 0 <= index < len(admin_questions):
        admin_questions.pop(index)
        all_questions[current_admin] = admin_questions
        save_questions(all_questions)
    
    return redirect(url_for('admin_panel'))

@app.route('/admin/download-pdf/<int:index>')
def download_pdf(index):
    if 'admin' not in session:
        return redirect(url_for('admin_login'))
    
    current_admin = session['admin']
    all_answers = load_answers()
    admin_answers = all_answers.get(current_admin, [])
    
    if 0 <= index < len(admin_answers):
        result = admin_answers[index]
        timestamp = datetime.fromisoformat(result['timestamp'])
        percentage = round((result['score'] / result['total']) * 100, 2) if result['total'] > 0 else 0
        
        # Create PDF in memory
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.5*inch, bottomMargin=0.5*inch)
        
        # Container for PDF elements
        elements = []
        
        # Styles
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#333333'),
            spaceAfter=30,
            alignment=TA_CENTER
        )
        
        # Title
        title = Paragraph("Quiz Result Report", title_style)
        elements.append(title)
        elements.append(Spacer(1, 0.2*inch))
        
        # Student Info
        student_info_data = [
            ['Student Name:', result['student_name']],
            ['Date:', timestamp.strftime('%Y-%m-%d')],
            ['Time:', timestamp.strftime('%I:%M %p')],
        ]
        
        student_table = Table(student_info_data, colWidths=[2*inch, 4*inch])
        student_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f0f0f0')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 12),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('TOPPADDING', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#dddddd'))
        ]))
        elements.append(student_table)
        elements.append(Spacer(1, 0.3*inch))
        
        # Score Summary
        grade = 'A' if percentage >= 70 else 'B' if percentage >= 60 else 'C' if percentage >= 50 else 'D' if percentage >= 40 else 'F'
        
        score_data = [
            ['SCORE', 'PERCENTAGE', 'GRADE'],
            [f"{result['score']}/{result['total']}", f"{percentage}%", grade]
        ]
        
        score_table = Table(score_data, colWidths=[2*inch, 2*inch, 2*inch])
        score_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e74c3c')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('FONTSIZE', (0, 1), (-1, 1), 18),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 15),
            ('TOPPADDING', (0, 0), (-1, -1), 15),
            ('BACKGROUND', (0, 1), (-1, 1), colors.HexColor('#f9f9f9')),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#dddddd'))
        ]))
        elements.append(score_table)
        elements.append(Spacer(1, 0.3*inch))
        
        # Questions
        for idx, item in enumerate(result['results'], 1):
            question_data = [
                [f"Q{idx}: {item['question']}"],
                [f"Student's Answer: {item['user_answer']}"]
            ]
            
            if not item['correct']:
                question_data.append([f"Correct Answer: {item['correct_answer']}"])
            
            question_table = Table(question_data, colWidths=[6.5*inch])
            
            table_style = [
                ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f9f9f9')),
                ('FONTNAME', (0, 0), (0, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('PADDING', (0, 0), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#dddddd')),
            ]
            
            if item['correct']:
                table_style.append(('LINEAFTER', (0, 0), (0, -1), 4, colors.HexColor('#27ae60')))
            else:
                table_style.append(('LINEAFTER', (0, 0), (0, -1), 4, colors.HexColor('#e74c3c')))
            
            question_table.setStyle(TableStyle(table_style))
            elements.append(question_table)
            elements.append(Spacer(1, 0.15*inch))
        
        # Build PDF
        doc.build(elements)
        buffer.seek(0)
        
        # Return PDF as download
        return send_file(
            buffer,
            as_attachment=True,
            download_name=f"Quiz_Result_{result['student_name'].replace(' ', '_')}_{timestamp.strftime('%Y%m%d')}.pdf",
            mimetype='application/pdf'
        )
    
    return redirect(url_for('admin_panel'))

@app.route('/admin/download-excel')
def download_excel():
    if 'admin' not in session:
        return redirect(url_for('admin_login'))
    
    current_admin = session['admin']
    all_answers = load_answers()
    admin_answers = all_answers.get(current_admin, [])
    
    # Create Excel workbook
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Student Results"
    
    # Style definitions
    header_fill = PatternFill(start_color="E74C3C", end_color="E74C3C", fill_type="solid")
    header_font = Font(bold=True, color="FFFFFF", size=12)
    
    # Headers
    headers = ['Student Name', 'Score', 'Total', 'Percentage', 'Grade', 'Date', 'Time']
    for col, header in enumerate(headers, 1):
        cell = ws.cell(row=1, column=col, value=header)
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(horizontal='center', vertical='center')
    
    # Data rows
    for row_idx, answer in enumerate(admin_answers, 2):
        timestamp = datetime.fromisoformat(answer['timestamp'])
        percentage = round((answer['score'] / answer['total']) * 100, 2) if answer['total'] > 0 else 0
        grade = 'A' if percentage >= 70 else 'B' if percentage >= 60 else 'C' if percentage >= 50 else 'D' if percentage >= 40 else 'F'
        
        ws.cell(row=row_idx, column=1, value=answer['student_name'])
        ws.cell(row=row_idx, column=2, value=answer['score'])
        ws.cell(row=row_idx, column=3, value=answer['total'])
        ws.cell(row=row_idx, column=4, value=percentage)
        ws.cell(row=row_idx, column=5, value=grade)
        ws.cell(row=row_idx, column=6, value=timestamp.strftime('%Y-%m-%d'))
        ws.cell(row=row_idx, column=7, value=timestamp.strftime('%I:%M %p'))
        
        # Color code based on grade
        if percentage >= 70:
            grade_color = "27AE60"
        elif percentage >= 50:
            grade_color = "F39C12"
        else:
            grade_color = "E74C3C"
        
        ws.cell(row=row_idx, column=4).font = Font(bold=True, color=grade_color)
        ws.cell(row=row_idx, column=5).font = Font(bold=True, color=grade_color)
    
    # Adjust column widths
    for col in ws.columns:
        max_length = 0
        col_letter = col[0].column_letter
        for cell in col:
            try:
                if len(str(cell.value)) > max_length:
                    max_length = len(str(cell.value))
            except:
                pass
        adjusted_width = (max_length + 2)
        ws.column_dimensions[col_letter].width = adjusted_width
    
    # Save to BytesIO
    buffer = BytesIO()
    wb.save(buffer)
    buffer.seek(0)
    
    # Return Excel file as download
    return send_file(
        buffer,
        as_attachment=True,
        download_name=f"Student_Results_{current_admin}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )

@app.route('/logout')
def logout():
    session.pop('admin', None)
    return redirect(url_for('home'))

@app.route('/quiz')
def user_quiz():
    # Show list of all available quizzes
    all_questions = load_questions()
    
    available_quizzes = []
    for admin_id, questions in all_questions.items():
        if questions:  # Only show admins with questions
            available_quizzes.append({
                'admin_id': admin_id,
                'admin_name': admin_id,
                'question_count': len(questions)
            })
    
    return render_template_string(QUIZ_SELECT_TEMPLATE, available_quizzes=available_quizzes)

@app.route('/quiz/<admin_id>')
def take_quiz(admin_id):
    # Get specific admin's questions
    all_questions = load_questions()
    questions = all_questions.get(admin_id, [])
    
    return render_template_string(USER_QUIZ_TEMPLATE, 
                                 questions=questions, 
                                 admin_name=admin_id,
                                 admin_id=admin_id)

@app.route('/quiz/submit', methods=['POST'])
def submit_quiz():
    student_name = request.form.get('student_name')
    admin_id = request.form.get('admin_id')
    
    all_questions = load_questions()
    questions = all_questions.get(admin_id, [])
    
    score = 0
    results = []
    
    for i, question in enumerate(questions):
        user_answer = request.form.get(f'q{i}')
        correct = user_answer == question['correct_answer']
        if correct:
            score += 1
        
        results.append({
            'question': question['question'],
            'user_answer': user_answer,
            'correct_answer': question['correct_answer'],
            'correct': correct
        })
    
    # Save results under admin's data
    all_answers = load_answers()
    if admin_id not in all_answers:
        all_answers[admin_id] = []
    
    all_answers[admin_id].append({
        'student_name': student_name,
        'score': score,
        'total': len(questions),
        'timestamp': datetime.now().isoformat(),
        'results': results
    })
    save_answers(all_answers)
    
    percentage = round((score / len(questions)) * 100, 2) if len(questions) > 0 else 0
    
    return render_template_string(RESULTS_TEMPLATE, 
                                  student_name=student_name,
                                  score=score, 
                                  total=len(questions),
                                  percentage=percentage,
                                  results=results)

if __name__ == '__main__':
    init_files()
    print("\n" + "="*50)
    print("🚀 Quiz System Starting...")
    print("="*50)
    print("\n📍 Access: http://127.0.0.1:5000")
    print("\n✨ New Features:")
    print("   • Multi-admin support")
    print("   • Admin registration system")
    print("   • Separate data per admin")
    print("   • Excel export for results")
    print("\n" + "="*50 + "\n")
    app.run(debug=True, port=5000)