from ollama import chat
from ollama import ChatResponse
import json

System_prompt = '''
You will evaluate interview responses based on:
1. Technical accuracy (for technical questions)
2. Clarity and structure
3. Relevance to question
4. Depth of knowledge

Provide ratings (0-10) for each category and overall score.
Include specific feedback and expected response if score < 7.

Output in this JSON format:
{
  "technical_score": 0-10,
  "clarity_score": 0-10,
  "relevance_score": 0-10,
  "depth_score": 0-10,
  "overall_score": 0-10,
  "feedback": "Detailed feedback",
  "expected_response": "Only if score < 7"
}
'''

def evaluate(question, answer):
    """Evaluate a single interview response."""
    response: ChatResponse = chat(model='gemma3', messages=[
        {"role": "system", "content": System_prompt},
        {"role": "user", "content": f"Question: {question}\nAnswer: {answer}"}
    ])
    
    try:
        # Extract JSON from response
        response_text = response['message']['content']
        if response_text.startswith('```json') and response_text.endswith('```'):
            response_text = response_text[7:-3].strip()
        return json.loads(response_text)
    except json.JSONDecodeError:
        print("Failed to parse evaluation response")
        return {
            "technical_score": 0,
            "clarity_score": 0,
            "relevance_score": 0,
            "depth_score": 0,
            "overall_score": 0,
            "feedback": "Evaluation failed",
            "expected_response": ""
        }


if __name__ == "__main__":
    # Example job description and candidate resume
    question = "Difference between for loop and while loop in Python"
    answer = "For loops are primarily used when you know in advance how many times you want to iterate, often iterating over a sequence (like a list or range). While loops are used when you want to repeat a block of code as long as a certain condition remains true.  A key difference is that for loops implicitly manage iteration counts, while while loops require you to explicitly manage the condition that controls the loop's execution.  Example:  For a for loop, you'd iterate through a list.  For a while loop, you might repeatedly ask the user for input until they enter a specific value."

    # Generate interview questions
    generated_questions = evaluate(question, answer)

    # Print the generated questions
    # print(generated_questions)