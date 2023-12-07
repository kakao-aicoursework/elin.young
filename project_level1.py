import json
import openai
# import tkinter as tk
import pandas as pd
# from tkinter import scrolledtext
# import tkinter.filedialog as filedialog
openai.api_key = ''

def text_to_json(file_path:str):
    json_file = []
    f = open(file_path, "r")
    full_txt = f.read()


    for txt in full_txt.split('\n#'):
        t = [i for i in txt.split('\n') if i != '']
        if len(t) <= 1:
            continue
        json_file.append([{
            "Title": t[0],
            "Description": t[1:]
        }])

    return json_file

# res = text_to_json(file_path="./projects/project_data_카카오톡채널.txt")
# json.dumps(res, ensure_ascii=False)


def channel_assistant(message: str, gpt_model: str="gpt-3.5-turbo", temperature: float=0.1, max_tokens: int=1024):
    
    with open("./projects/project_data_카카오톡채널.txt", "r") as f:
        txt = f.readlines()

    message_log = [
        {"role": "system", "content": "당신은 카카오채널 비서입니다."},
        {"role": "user", "content": f"{txt[:10]}"},
        {"role": "user", "content": f"{message}"+"\n설명은 500 ~ 600 단어 이내로 출력해줘"}
        ]

    response = openai.ChatCompletion.create(
        model=gpt_model,
        messages=message_log,
        temperature=temperature,
        max_tokens=max_tokens
    )

    return response.choices[0].message.content

def run():
    print("안녕하세요 카카오채널 비서입니다. 무엇을 도와드릴까요?")
    while True:
        print("종료를 원하시면 '종료' 또는 'quit'을 입력하세요")
        message = input()
        print(message)
        if (('종료' in message) | ('quit' in message)):
            print("카카오채널 assistant가 종료 되었습니다")
            break
        else:
            res = channel_assistant(message, max_tokens=2048)
            print(res)

if __name__ == '__main__':
    run()
