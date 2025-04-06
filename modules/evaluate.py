from ollama import chat
from ollama import ChatResponse
import re
import time

System_prompt = '''
you will be provided with a question and a answer. Please rate the answer on a scale of 0 to 10 based on clarity, relevance, accuracy, and completeness. If the score is less than 7, provide an expected response or improvements. Always output the evaluation only in JSON format with the following structure:

{
  "score": "Evaluation score (0-10)",
  "feedback": "Feedback or suggestions for improvement”,
  "expected_response": "Expected or improved response (if score < 7 else None)”
}

'''

def evaluate(question, answer):
    """Generate interview questions using the Ollama model."""
    global generated_questions
    response: ChatResponse = chat(model='gemma3', messages=[
        {"role": "system", "content": System_prompt},
        {"role": "user", "content": f"evaluate teh user response : {answer} for the question : {question} and provide the evaluation in JSON format."}
    ])
    response_text = response['message']['content']
    return response_text[7:-3]


if __name__ == "__main__":
    # Example job description and candidate resume
    question = "Difference between for loop and while loop in Python"
    answer = "For loops are primarily used when you know in advance how many times you want to iterate, often iterating over a sequence (like a list or range). While loops are used when you want to repeat a block of code as long as a certain condition remains true.  A key difference is that for loops implicitly manage iteration counts, while while loops require you to explicitly manage the condition that controls the loop's execution.  Example:  For a for loop, you'd iterate through a list.  For a while loop, you might repeatedly ask the user for input until they enter a specific value."

    # Generate interview questions
    generated_questions = evaluate(question, answer)

    # Print the generated questions
    print(generated_questions)