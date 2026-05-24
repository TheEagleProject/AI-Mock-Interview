from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.models import User, Resume, InterviewSession, QuestionAnswer
from app.utils.text_extractor import extract_text
from app.utils.spacy_analyzer import run_analysis
from app.utils.ai_interviewer import generate_questions, evaluate_answer
from werkzeug.utils import secure_filename
import os

main = Blueprint('main', __name__)

@main.route("/")
def home():
    return render_template("home.html")

@main.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash("Email already registered")
            return redirect(url_for("main.register"))
        else:
            user = User(email=email)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            flash("Account created successfully")
            return redirect(url_for("main.login"))
        
    return render_template("register.html")

@main.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        existing_user = User.query.filter_by(email=email).first()
        if not existing_user:
            flash("email not found")
            return redirect(url_for("main.login"))
        
        if not existing_user.check_password(password):
            flash("Incorrect password")
            return redirect(url_for("main.login"))
        
        login_user(existing_user)
        return redirect(url_for("main.dashboard"))

    return render_template("login.html")
                

@main.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("main.login"))


@main.route("/dashboard")
@login_required
def dashboard():
    sessions = InterviewSession.query.filter_by(user_id=current_user.id).all()
    avg_score = round(sum(session.overall_score for session in sessions) / len(sessions)) if sessions else 0
    return render_template("dashboard.html", sessions=sessions, avg_score=avg_score)

@main.route("/interview/setup", methods=["GET", "POST"])
@login_required
def interview():
    if request.method == "POST":
        job_title = request.form.get("job_title")
        company_name = request.form.get("company_name")
        job_description = request.form.get("job_description")
        file = request.files["resume"]
        filename = secure_filename(file.filename)
        os.makedirs('uploads', exist_ok=True)

        filepath = os.path.join('uploads', filename)
        file.save(filepath)

        text = extract_text(filepath)
        os.remove(filepath)

        analysis = run_analysis(text, job_description)

        resume = Resume(extracted_text=text, user_id=current_user.id)    
        db.session.add(resume)
        db.session.commit()

        interview_session = InterviewSession(job_title = job_title, company_name = company_name, job_description = job_description, user_id = current_user.id)
        db.session.add(interview_session)
        db.session.commit()

        questions = generate_questions(text, job_description, analysis)

        for i, question in enumerate(questions):
            qa = QuestionAnswer(
                session_id=interview_session.id,
                question=question,
                question_number=i + 1
            )
            db.session.add(qa)

        db.session.commit()

        return redirect(url_for("main.question", session_id=interview_session.id, question_number=1))
    
    return render_template("interview_setup.html")  



@main.route("/interview/<session_id>/question/<question_number>", methods=["GET", "POST"])
@login_required
def question(session_id, question_number):
    # Step 1 - find the right question from database
    question = QuestionAnswer.query.filter_by(
        session_id=session_id,
        question_number=question_number
    ).first()

    # Step 2 - handle the answer submission
    if request.method == "POST":
        # Step 3 - get the answer from the form
        answer = request.form.get("answer")

        # Step 4 - get the job description for context
        interview_session = InterviewSession.query.filter_by(id=session_id).first()

        # Step 5 - evaluate with Claude
        feedback = evaluate_answer(question.question, answer, interview_session.job_description)

        # Step 6 - parse score from feedback
        import re
        score_match = re.search(r'SCORE:\s*(\d+)', feedback)
        score = float(score_match.group(1)) if score_match else 5.0

        # Step 7 - save answer and feedback to database
        question.answer = answer
        question.feedback = feedback
        question.score = score
        db.session.commit()

        # Step 8 - go to next question or results
        if int(question_number) < 7:
            return redirect(url_for("main.question", session_id=session_id, question_number=int(question_number) + 1))
        else:
            return redirect(url_for("main.results", session_id=session_id))

    # GET - show the question
    return render_template("interview.html", question=question, question_number=question_number)

    

@main.route("/interview/<session_id>/results", methods=["GET"])
@login_required
def results(session_id):
    # Step 1 - get the session
    interview_session = InterviewSession.query.filter_by(id=session_id).first()

    # Step 2 - get all questions
    questions = QuestionAnswer.query.filter_by(
        session_id=session_id
    ).order_by(QuestionAnswer.question_number).all()

    # Step 3 - calculate overall score
    if questions:
        overall_score = round(sum(q.score for q in questions) / len(questions), 1)
        interview_session.overall_score = overall_score
        db.session.commit()
    else:
        overall_score = 0

    # Step 4 - render results
    return render_template("results.html", 
        session=interview_session,
        questions=questions,
        overall_score=overall_score
    )
