import os
import json
import openai
import chromadb
import pandas as pd
import fire

class ChatBot():
    def __init__(self, conf_fname: str = './Config/chatbot.json') -> None:
        f = open(conf_fname)
        self.conf = json.loads(f.read())
        self.client = chromadb.PersistentClient()
        self.collection = self.client.get_or_create_collection(
            name=self.conf["collection_name"],
            metadata={"hnsw:space": "cosine"}
        )
        self.message_log = [
            {
                "role": "system",
                "content": "You are an assistant of kakaochannel. Your user will be Korean, so communicate in Korean. At first, Briefly introduce about kakaochannel in one line. After then answer to user's requests. Please answer the description within 500 to 600 words."
            }
        ]
        
        self.functions = []
        self.functions.append(self.conf["functions"])
        openai.api_key = self.conf["openai_api_key"]

    def text_to_json(self, file_path:str):
        f = open(file_path, "r")
        full_txt = f.read()

        json_file = []
        for txt in full_txt.split('\n#'):
            t = [i for i in txt.split('\n') if i != '']
            if len(t) <= 1:
                continue
            json_file.append({
                "Title": t[0],
                "Description": ''.join(t[1:])
            })

        return json.dumps(json_file, ensure_ascii=False)   

    def save_data_db(self, file_path: str):
        res = self.text_to_json(file_path = file_path)
        json_obj = json.loads(res)

        # 데이터 준비
        ids = []  # 인덱스
        documents = []  # 벡터로 변환 저장할 텍스트 데이터로 ChromaDB에 Embedding 데이터가 없으면 자동으로 벡터로 변환해서 저장

        for item in json_obj:
            id = item['Title'].replace(' ','-')
            document = f"{item['Title'].strip()} : {item['Description'].strip()}"

            ids.append(id)
            documents.append(document)

        # DB 저장
        self.collection.add(
            documents=documents,
            ids=ids
        )

    def get_kakaochannel_info(self, query_texts: str):

        # DB 쿼리
        results = self.collection.query(
            query_texts=[query_texts],
            n_results=10,
        )
        items = results["documents"][0]

        srchres = []

        for item in items:
            splited_item = item.split("||")
            srchres.append({
                'Title' : splited_item[0],
                'Description' : splited_item[1]
            })

        return json.dumps(srchres, ensure_ascii = False)

    def channel_assistant(self, message, functions, gpt_model: str = "gpt-3.5-turbo", temperature: float = 0.1, max_tokens: int = 1024):
        response = openai.ChatCompletion.create( 
            model=gpt_model,
            messages=message,
            temperature=temperature,
            functions=functions,
            function_call='auto',
            max_tokens=max_tokens
        )

        response_message = response["choices"][0]["message"]

        if response_message.get("function_call"):
            available_functions = {
                "get_kakaochannel_info": self.get_kakaochannel_info,
            }
            function_name = response_message["function_call"]["name"]
            fuction_to_call = available_functions[function_name]
            function_args = json.loads(response_message["function_call"]["arguments"])
            # 사용하는 함수에 따라 사용하는 인자의 개수와 내용이 달라질 수 있으므로
            # **function_args로 처리하기
            function_response = fuction_to_call(**function_args)

            # 함수를 실행한 결과를 GPT에게 보내 답을 받아오기 위한 부분
            message.append(response_message)  # GPT의 지난 답변을 message_logs에 추가하기
            message.append(
                {
                    "role": "function",
                    "name": function_name,
                    "content": function_response,
                }
            )  # 함수 실행 결과도 GPT messages에 추가하기
            response = openai.ChatCompletion.create(
                model=gpt_model,
                messages=message,
                temperature=temperature,
            )  # 함수 실행 결과를 GPT에 보내 새로운 답변 받아오기

        return response.choices[0].message.content

    def run(self):
        self.save_data_db(self.conf["file_path"])

        print("안녕하세요 카카오채널 비서입니다. 무엇을 도와드릴까요?")
        print("종료를 원하시면 '종료' 또는 'quit'을 입력하세요")
        while True:
            user_input = input()
            if (('종료' in user_input) | ('quit' in user_input)):
                print("카카오채널 assistant가 종료 되었습니다")
                break
            else:
                self.message_log.append({"role": "user", "content": "user_input"})
                res = self.channel_assistant(self.message_log, functions=self.functions, max_tokens=1024)
                print(res)

if __name__ == '__main__':
    fire.Fire(ChatBot)
