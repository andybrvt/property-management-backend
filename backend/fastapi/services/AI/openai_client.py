import openai
import os
import logging

# ✅ Load OpenAI API key
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = openai.OpenAI(api_key=OPENAI_API_KEY)

def call_openai_extraction(prompt: str, max_tokens: int = 200, model: str = "gpt-4o-mini") -> str:
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        logging.error(f"❌ OpenAI API Error: {e}")
        return ""
    

def call_openai_chat(messages: list, max_tokens: int = 200, model: str = "gpt-4o-mini") -> str:
    try:
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            max_tokens=max_tokens
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        logging.error(f"❌ Chat API Error: {e}")
        return ""

