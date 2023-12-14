import os
import json
import openai
from langchain.chat_models import ChatOpenAI
from langchain.schema import SystemMessage
from langchain.prompts.chat import ChatPromptTemplate, HumanMessagePromptTemplate
from langchain.chains import LLMChain, SequentialChain
import pandas as pd
import fire



class ChatBot():
    def __init__(self, conf_fname: str = './Config/chatbot.json') -> None:
        f = open(conf_fname)
        self.conf = json.loads(f.read())
        os.environ['OPENAI_API_KEY'] = self.conf["openai_api_key"]

    def text_to_json(self, file_path:str) -> json:
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

    def build_answer(self, llm):
        ref_file = self.text_to_json(file_path=self.conf["file_path"])

        system_message = self.conf["system_message"]
        system_message_prompt = SystemMessage(content=system_message)
        
        human_template = "{text} \n---\n 위 내용을 ref_file에서 찾아"
        human_message_prompt = HumanMessagePromptTemplate.from_template(
            human_template
        )
        
        chat_prompt = ChatPromptTemplate.from_messages([system_message_prompt,
                                                        human_message_prompt])

        return LLMChain(llm=llm, prompt=chat_prompt)    

    def run(self):
        llm = ChatOpenAI(model_name='gpt-3.5-turbo-16k', temperature=0.8)
        user_input = input("궁금한 내용을 입력해주세요\n")
        summarizer = self.build_answer(llm)
        res = summarizer.run(user_input)
        print(res)
        return res

if __name__ == '__main__':
    fire.Fire(ChatBot)