import requests
import os
from dotenv import load_dotenv

# load .env file
load_dotenv()

API_KEY = os.getenv("OPENROUTER_API_KEY")

if not API_KEY:
    raise ValueError("❌ API key not found in .env file")


def chat_with_ai(prompt):
    url = "https://openrouter.ai/api/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost",
        "X-Title": "My Qwen Chatbot"
    }

    data = {
        "model": "qwen/qwen-2.5-coder-32b-instruct",
        "messages": [
            {"role": "user", "content": prompt}
        ]
    }

    response = requests.post(url, headers=headers, json=data)
    result = response.json()

    print("DEBUG RESPONSE:", result)

    if "choices" in result:
        return result["choices"][0]["message"]["content"]
    else:
        return f"Error from API: {result}"

# Simple chat loop — only runs when executed directly, not when imported
if __name__ == "__main__":
    while True:
        user_input = input("You: ")
        if user_input.lower() in ["exit", "quit"]:
            break

        reply = chat_with_ai(user_input)
        print("AI:", reply)