# Online Quiz Management System

A web-based quiz management platform built with Python and Flask, designed for conducting online assessments for students and interviews.

> **Note:** This is the first version (v1.0) of the application. Future updates and enhancements are planned.

## 📋 Overview

This system provides a comprehensive solution for creating, managing, and taking online quizzes. It supports multiple administrators and includes features for automated quiz handling, result tracking, and data export capabilities.

## ✨ Features

- **Multi-Admin Support** - Multiple administrators can manage the system simultaneously
- **Admin Registration System** - Secure registration and authentication for administrators
- **Modern Bootstrap 5 UI** - Beautiful, responsive interface with smooth animations and contemporary design
- **Quiz Timer** - Configurable time limits for each quiz session
- **Auto-Submit on Timeout** - Automatically submits quizzes when time expires to ensure fair assessment
- **CSV Student Upload** - Bulk import students from CSV/Excel files (supports both comma and tab-separated formats)
- **Email Notifications** - Welcome emails sent to admins on registration via Gmail SMTP
- **Excel & PDF Export** - Export quiz results and reports in multiple formats for easy sharing and record-keeping
- **Student Management** - Manage allowed students per quiz with controlled access
- **Real-Time Analytics** - View detailed quiz statistics and student performance metrics
- **User-Friendly Interface** - Clean and intuitive design for both administrators and quiz takers

## 📸 Screenshots

### Home View
![Home View](images/home%20view.png)

### Admin Dashboard
![Admin Dashboard](images/admin-dashboard.png)

### Admin - Setting Timer
![Admin Setting Time](images/admin-setting%20time.png)

### Student Interface
![Student Interface](images/student%20interface.png)

### Student Quiz View
![Student View](images/student%20view.png)

### Admin - Students Results
![Admin Students Result](images/admin-%20students%20result.png)

## 🛠️ Technologies Used

- **Python** - Core programming language
- **Flask** - Web framework for building the application
- **Bootstrap 5** - Modern CSS framework for responsive design
- **Chart.js** - Data visualization and analytics
- **Jinja2** - Template engine for dynamic HTML
- **HTML/CSS/JavaScript** - Frontend interface and interactivity
- **Gmail SMTP** - Email service for notifications

## 🎯 Use Cases

- Educational institutions for student assessments
- Online interview platforms
- Training and certification programs
- Knowledge evaluation tools

## 🚀 Getting Started

### Prerequisites
- Python 3.x installed on your system
- Flask framework

### Installation

1. Clone the repository:
```bash
git clone https://github.com/brys-124/Online-quiz-management.git
```

2. Navigate to the project directory:
```bash
cd Online-quiz-management
```

3. Install required dependencies:
```bash
pip install flask
```

4. **Configure Email (Optional)** - For email notifications:
   - Create a Gmail app password: https://support.google.com/accounts/answer/185833
   - Set environment variables:
   ```bash
   set GMAIL_USER=your-email@gmail.com
   set GMAIL_PASSWORD=your-app-password
   ```

5. Run the application:
```bash
python app.py
```

6. Open your browser and navigate to `http://localhost:5000`

### First-Time Setup

1. **Register as Admin** - Click "Register" on the admin login page to create your admin account
2. **Add Students** - Upload a CSV file with student names and IDs (see `sample_students.csv` for format)
3. **Create Quiz Questions** - Add quiz questions through the admin panel
4. **Configure Quiz Settings** - Set time limits and other quiz parameters
5. **Share Quiz Link** - Students can then access the quiz using their credentials

## 🔮 Future Enhancements

Planned features for upcoming versions:
- Database integration for persistent data storage (SQLite/PostgreSQL)
- Advanced question types (essay, fill-in-the-blank, image selection)
- Real-time quiz monitoring and proctoring
- Enhanced security features (two-factor authentication, question shuffling)
- Mobile responsive design improvements
- Dark mode support
- Question bank and randomization
- Detailed performance analytics and reports

## 👤 Author

**Bryson Nkinda**
- GitHub: [@brys-123](https://github.com/brys-123)
- Email: brysonnkinda@gmail.com

## 📝 License

This project is available for educational and personal use.
