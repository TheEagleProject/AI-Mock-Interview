#  AI Mock Interview System

An AI-powered interview preparation tool that generates personalized interview questions based on your resume and a job description, then evaluates your answers with detailed feedback.

## Features

- Upload your resume (PDF) and paste a job description
- AI generates 7 personalized interview questions using Claude API
- Answer each question and receive detailed feedback and a score out of 10
- Dashboard tracks all past sessions and average scores
- NLP preprocessing using spaCy to optimize API token usage
- Full user authentication with secure password hashing

## Tech Stack

- **Backend** — Python, Flask
- **Database** — PostgreSQL, SQLAlchemy
- **NLP** — spaCy
- **AI** — Anthropic Claude API
- **Authentication** — Flask-Login
- **PDF Processing** — PyMuPDF

## Setup

1. Clone the repository
```bash
git clone https://github.com/TheEagleProject/AI-Mock-Interview.git
```

2. Create a virtual environment and install dependencies
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

3. Create a `.env` file in the root directory

4. Set up PostgreSQL database
```bash
psql postgres
CREATE DATABASE mock_interview_db;
```

5. Run the app
```bash
python3 run.py
```

## Usage

1. Register an account
2. Click **New Interview**
3. Enter job title, company name, and paste the job description
4. Upload your resume PDF
5. Answer 7 AI generated interview questions
6. Review your scores and detailed feedback
7. Track your progress on the dashboard