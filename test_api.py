from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()


# Ensure you have the correct API key
client = OpenAI()

try:
    chat_completion = client.chat.completions.create(
    messages=[
        {
            "role": "user",
            "content": "Say this is a test",
        }
    ],
    model="gpt-4o",
    )

    print(chat_completion)

except Exception as e:
    print("OpenAI API Error:", e)



'''
from langchain_community.utilities import SerpAPIWrapper

params = {
    "engine": "google",  # or "bing" depending on the engine you're using
    "gl": "us",
    "hl": "en",
}
search = SerpAPIWrapper(params=params)

try:
    result = search.run("test search")
    print("SerpAPI Call Successful:", result)
except Exception as e:
    print("SerpAPI Error:", e)
'''