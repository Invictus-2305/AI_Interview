from ollama import chat
from ollama import ChatResponse
import re
import time

System_prompt = '''
Generate a structured set of 10 interview questions in JSON format tailored to a given job description and candidate resume. The JSON should include the following fields:

question: The interview question designed to evaluate a specific skill, experience, or competency.

skill_set: The specific skill(s) or competency(ies) the question is targeting (e.g., programming, teamwork, problem-solving, etc.).

difficulty_level: The level of difficulty of the question (e.g., Beginner, Intermediate, Advanced).

enclose the json objects in a list and stick to the format mentioned above and generate the questions. and response should only contain json and nothing else.
'''

# System_prompt = '''
# you will be provided with job description and resume. Please generate 10 beginner level interview questions based on the same. focus more on the skills mentioned in the Job description and generate most of the question related to it and few question based on the skills and projects mentioned in resume. Always give output only in JSON format. . The JSON should include the following fields:
# question
# skillset : The specific skill(s) or competency(ies) the question is targeting (e.g., programming, teamwork, problem-solving, etc.).
# difficulty level : The level of difficulty of the question (e.g., Beginner, Intermediate, Advanced).
# '''
def generate_questions(job_description, resume):
    """Generate interview questions using the Ollama model."""
    print("question generation started")
    # start = time.time()
    global generated_questions
    response: ChatResponse = chat(model='gemma3', messages=[
        {"role": "system", "content": System_prompt},
        {"role": "user", "content": f"job description: {job_description} || resume: {resume}"}
    ])
    response_text = response['message']['content']
    clean_response = re.sub(r'<think>.*?</think>', '', response_text, flags=re.DOTALL).strip()
    print("question generation completed")
    # print(clean_response)
    # print(time.time()- start)
    return clean_response[7:-3]

if __name__ == "__main__":
    # Example job description and candidate resume
    job_description = "We are looking for a software engineer with experience in Python and machine learning."
    resume = "Candidate has 5 years of experience in software development, specializing in Python and data analysis."

    # Generate interview questions
    generated_questions = generate_questions(job_description, resume)

    # Print the generated questions
    print(generated_questions)