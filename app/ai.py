import openai
from os import getenv

openai.api_key = getenv("OPENAI_KEY")

def generate(prompt:str) -> str:
    print('generating prompt...')
    _messages = [
        {"role": "system", "content": getenv("SYSTEM_PROMPT")},
        {"role": "user", "content": prompt}
    ]
    try:
        chat_completion = openai.ChatCompletion.create(model='gpt-3.5-turbo', messages=_messages, request_timeout=30.0)
    except:
        print('error generating prompt')
        return None
    return chat_completion.choices[0].message.content