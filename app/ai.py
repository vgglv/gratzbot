import openai
from os import getenv

openai.api_key = getenv("OPENAI_KEY")
MSG_LIMIT = 20
msg_list = []

def generate(prompt:str) -> str:
    print('generating prompt...')
    _messages = [
        {"role": "system", "content": getenv("SYSTEM_PROMPT")},
        {"role": "user", "content": prompt}
    ]
    if len(msg_list) >= MSG_LIMIT:
        msg_list.pop(0)
    msg_list.append(prompt)
    for msg in msg_list:
        _messages.append({"role": "user", "content": {msg}})
    try:
        chat_completion = openai.ChatCompletion.create(model='gpt-3.5-turbo', messages=_messages, request_timeout=9.0)
    except:
        print('error generating prompt')
        return None
    return chat_completion.choices[0].message.content