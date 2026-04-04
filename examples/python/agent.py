from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    api_key="",
    base_url="http://localhost:8000",  # Overwrite base URL
    default_headers={
        "x-api-key": "value_here", # API_KEY from SEMANTIC-CACHE-API TO PROTECT AGAINST UNAUTHORIZATED REQUEST
    }
)

def ask_question(question: str) -> str:
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a helpful AI assistant."},
            {"role": "user", "content": question},
        ],
    )
    return response.choices[0].message.content


def main():
    print("AI Agent - Type your question (or 'exit' to quit):")
    while True:
        user_input = input("You: ")
        if user_input.lower() == "exit":
            break
        response = ask_question(user_input)
        print(f"AI: {response}\n")


if __name__ == "__main__":
    main()
