import os
import re
import anthropic

client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

def generate_questions(resume_text, job_text, analysis):
    # Use compressed versions if available
    compressed_resume = analysis.get('compressed_resume', resume_text)
    compressed_job = analysis.get('compressed_job', job_text)
    
    messages = [
        {"role": "user", "content": f"""
        You are an expert technical interviewer. 
        
        RESUME SUMMARY:
        {compressed_resume}
        
        JOB DESCRIPTION SUMMARY:
        {compressed_job}
        
        MATCHING KEYWORDS: {analysis['comparison']['matching_skills']}
        MISSING KEYWORDS: {analysis['comparison']['missing_skills']}
        
        Generate exactly 7 interview questions based on this candidate's background and the job requirements.
        - Ask about specific experience and projects from their background
        - Ask about matching keywords they claim to have
        - Ask about missing keywords the job requires
        - Mix behavioral and technical questions
        
        Format your response as a numbered list:
        1. question here
        2. question here
        
        Return questions only, no extra text.
        """}
    ]
    
    response = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=1000,
        messages=messages
    )
    
    response_text = response.content[0].text
    questions = re.findall(r'\d+\.\s+(.*)', response_text)
    return questions

def evaluate_answer(question, answer, job_description):
    messages = [
        {"role": "user", "content": f"""
        You are an expert technical interviewer.
        
        QUESTION:
        {question}
        
        ANSWER:
        {answer}
        
        JOB DESCRIPTION:
        {job_description}
        
        Evaluate the answer and return three things:
        - What was good about the answer
        - What was missing or weak
        - A score out of 10
        
        Format your response as:
        GOOD: ...
        MISSING: ...
        SCORE: 7
        """}
    ]
    
    response = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=1000,
        messages=messages
    )
    
    response_text = response.content[0].text
    return response_text