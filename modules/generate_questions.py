from ollama import chat
from ollama import ChatResponse
import re

System_prompt = '''
Generate a structured set of interview questions in JSON format tailored to a given job description and candidate resume. The JSON should include the following fields:

question: The interview question designed to evaluate a specific skill, experience, or competency and should be clear and concise and focus on the candidate's qualifications and experiences relevant to the job description.

skill_set: The specific skill(s) or competency(ies) the question is targeting (e.g., programming, teamwork, problem-solving, etc.).

enclose the json objects in a list and stick to the format mentioned above and generate the questions. and response should only contain json and nothing else. Address the candidate in second person and avoid using first person. The questions should be relevant to the job description and the candidate's resume. The questions should be beginner to intermediate level, avoiding overly technical or advanced topics. The JSON should not include any additional text or explanations outside of the JSON structure.
'''

def generate_questions(job_description, resume):
    """Generate interview questions using the Ollama model."""
    print("question generation started")
    global generated_questions
    response: ChatResponse = chat(model='gemma3', messages=[
        {"role": "system", "content": System_prompt},
        {"role": "user", "content": f"Ask 10 beginner to intermediate level questions based on job description: {job_description} and resume: {resume} of the candidate. Response should only contain JSON and nothing else."}
    ])
    response_text = response['message']['content']
    clean_response = re.sub(r'<think>.*?</think>', '', response_text, flags=re.DOTALL).strip()
    print("question generation completed")
    print(clean_response)
    return clean_response[7:-3]

if __name__ == "__main__":
    # Example job description and candidate resume
    job_description = "We are looking for a software engineer with experience in Python and machine learning."
    resume = "Candidate has 5 years of experience in software development, specializing in Python and data analysis."

    # Generate interview questions
    generated_questions = generate_questions(job_description, resume)

    # Print the generated questions
    print(generated_questions)