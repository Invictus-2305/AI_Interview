from flask import Flask, render_template, request, jsonify, redirect, url_for, send_file
import pymupdf4llm
import pathlib
from docx import Document
import re
import threading
import time
from dotenv import load_dotenv
import os
from modules.generate_questions import generate_questions 
from modules.generate_audio import generate_audio_for_questions
from modules.evaluate import evaluate
import json
import speech_recognition as sr
from io import BytesIO
import pandas as pd
from modules.generate_report import generate_report
from flask import send_file

app = Flask(__name__)
r = sr.Recognizer()

# DataFrame to store introduction, questions, and responses
temp = '''[
  {
    "question": "What is a list in Python?",
    "skill_set": ["Python"]
  }
]'''
def docx_to_markdown(file_path):
    doc = Document(file_path)
    md_text = ""
    for para in doc.paragraphs:
        md_text += para.text + "\n\n"
    return md_text

def generate_questions_thread(jd, md_text):
    """Generate questions and store them in the DataFrame."""
    global generated_questions, questions_responses_df, num_questions
    try:
        # Generate questions using the Ollama model
        generated_questions = generate_questions(jd, md_text)
        questions = json.loads(generated_questions)
        # generated_questions = temp
        # questions = json.loads(temp)
        # Initialize the DataFrame with the introduction
        global questions_responses_df
        questions_responses_df = pd.DataFrame(columns=["Type", "Content", "User Response", "Score", "Feedback", "Expected Response"])
        questions_responses_df = pd.concat(
            [questions_responses_df, pd.DataFrame([{"Type": "Introduction", "Content": "Introduction", "User Response": None}])],
            ignore_index=True,
        )

        # Add questions to the DataFrame using pd.concat
        new_rows = [{"Type": "Question", "Content": q["question"], "User Response": None, "Score" : None, "Feedback": None, "Expected Response" : None} for q in questions]
        questions_responses_df = pd.concat(
            [questions_responses_df, pd.DataFrame(new_rows)], ignore_index=True
        )
        global num_questions
        num_questions = questions_responses_df.shape[0]
        print("Questions generated and added to DataFrame:")
        print(questions_responses_df)

    except Exception as e:
        print(f"Error generating questions: {e}")

# def evaluate_thread(question, user_response, current_index):
#     """Evaluate the user's response to a question."""
#     try:
#         evaluation = evaluate(question, user_response)
#         # Check if evaluation is not empty before parsing
#         if evaluation and evaluation.strip():
#             response = json.loads(evaluation)
            
#             # Update the DataFrame with evaluation results
#             questions_responses_df.at[current_index, "Score"] = int(response.get("score", 0))
#             questions_responses_df.at[current_index, "Feedback"] = response.get("feedback", "")
#             questions_responses_df.at[current_index, "Expected Response"] = response.get("expected_response", "")
            
#             # Check if all questions have been evaluated
#             total_questions = len(questions_responses_df) - 1  # Subtract 1 for introduction
#             if total_questions == current_index:
#                 print("All questions evaluated:")
#                 print(questions_responses_df)
#                 return url_for("show_results")
#         else:
#             print("Empty evaluation response received")
            
#     except json.JSONDecodeError as e:
#         print(f"Error parsing evaluation response: {e}")
#     except Exception as e:
#         print(f"Error in evaluation thread: {e}")

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

@app.route("/home", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        # Get the job description from the textarea
        jd = request.form.get("jd")

        # Get the uploaded resume file
        resume_file = request.files["resume"]

        # Save the uploaded file temporarily
        resume_path = "uploaded_resume"
        resume_file.save(resume_path)

        # Convert the resume to Markdown based on file type
        if resume_file.filename.endswith(".pdf"):
            md_text = pymupdf4llm.to_markdown(resume_path)
        elif resume_file.filename.endswith(".docx"):
            md_text = docx_to_markdown(resume_path)
        else:
            return "Unsupported file format. Please upload a PDF or DOCX file."

        # Start a background thread to generate questions
        global generated_questions
        generated_questions = None
        thread = threading.Thread(target=lambda: generate_questions_thread(jd, md_text))
        thread.start()

        # Redirect to the waiting page
        return redirect(url_for("waiting"))

    return render_template("home.html")

@app.route("/interview-process", methods=["GET"])
def waiting():
    return render_template("interview-process.html")

@app.route("/check_questions")
def check_questions():
    global generated_questions
    if generated_questions:
        questions = json.loads(generated_questions)
        # Start a background thread to generate audio for questions
        threading.Thread(target=generate_audio_for_questions, args=(questions,)).start()
        return jsonify({"status": "done", "questions": questions})
    else:
        return jsonify({"status": "generating"})

@app.route('/s_t_t', methods=['POST'])
def stt():
    if 'audio' not in request.files:
        return jsonify({"error": "No audio file provided"}), 400

    # Get the audio file from the request
    audio_file = request.files['audio']

    # Initialize the recognizer
    recognizer = sr.Recognizer()

    try:
        # Load the audio file directly into memory
        with BytesIO(audio_file.read()) as audio_stream:
            with sr.AudioFile(audio_stream) as source:
                audio = recognizer.record(source)  # Read the entire audio file

        # Perform speech-to-text using Google's Speech Recognition API
        text = recognizer.recognize_google(audio)
        print("Recognized Text:", text)

        # Get the current question index from the request
        current_question_index = int(request.form.get("question_index", 0))

        # Update the DataFrame with the user's response
        global questions_responses_df
        # The introduction is at index 0, so questions start from index 1
        response_index = current_question_index  # Adjust for introduction row
        if response_index < len(questions_responses_df):
            questions_responses_df.at[response_index, "User Response"] = text

        # Print the DataFrame to the terminal (for debugging)
        print("Updated DataFrame:")
        print(questions_responses_df[1:3])

        # Return the recognized text in the response
        return jsonify({"status": "success", "text": text}), 200

    except sr.UnknownValueError:
        return jsonify({"error": "Google Speech Recognition could not understand the audio"}), 400
    except sr.RequestError as e:
        return jsonify({"error": f"Could not request results from Google Speech Recognition service; {e}"}), 500

@app.route("/results")
def show_results():
    global questions_responses_df
    
    # Convert NaN/None to empty strings for cleaner display
    questions_responses_df = questions_responses_df.fillna('')
    
    # Convert to list of dictionaries for easy templating
    results_data = questions_responses_df.to_dict('records')
    
    return render_template(
        "results.html",
        results=results_data,
        columns=questions_responses_df.columns.tolist()
    )



# @app.route("/export_csv", methods=["GET"])
# def export_csv():
#     global questions_responses_df
#     try:
#         # Save the DataFrame to a CSV file
#         csv_file_path = "interview_responses.csv"
#         questions_responses_df.to_csv(csv_file_path, index=False)

#         # Send the CSV file as a response
#         return send_file(csv_file_path, as_attachment=True)
#     except Exception as e:
#         return jsonify({"error": f"Failed to export CSV: {e}"}), 500

@app.route("/generate_report", methods=["GET"])
def generate_report_route():
    global questions_responses_df
    try:
        # Ensure we have responses to evaluate
        if questions_responses_df.empty or len(questions_responses_df[questions_responses_df['User Response'].notna()]) == 0:
            return jsonify({"error": "No interview responses available to generate report"}), 400
            
        report_path = generate_report(questions_responses_df)
        
        if not pathlib.Path(report_path).exists():
            raise FileNotFoundError("Report file was not created")
            
        return send_file(
            report_path,
            as_attachment=True,
            mimetype='application/pdf',
            download_name='interview_report.pdf'
        )
    except Exception as e:
        print(f"Report generation error: {str(e)}")
        return jsonify({"error": f"Failed to generate report: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(debug=True)