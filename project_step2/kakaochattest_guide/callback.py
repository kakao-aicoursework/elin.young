from dto import ChatbotRequest
from samples import list_card
import aiohttp
import time
import logging
import openai
from project_level2 import ChatBot

# 환경 변수 처리 필요!
logger = logging.getLogger("Callback")

async def callback_handler(request: ChatbotRequest) -> dict:

    # ===================== start =================================
    chatbot = ChatBot()
    output_text = ChatBot.run()
    
    payload = {
        "version": "2.0",
        "template": {
            "outputs": [
                {
                    "simpleText": {
                        "text": output_text
                    }
                }
            ]
        }
    }
    
    # ===================== end =================================
    # 참고링크1 : https://kakaobusiness.gitbook.io/main/tool/chatbot/skill_guide/ai_chatbot_callback_guide
    # 참고링크1 : https://kakaobusiness.gitbook.io/main/tool/chatbot/skill_guide/answer_json_format

    time.sleep(1.0)

    url = request.userRequest.callbackUrl

    if url:
        async with aiohttp.ClientSession() as session:
            async with session.post(url=url, json=payload, ssl=False) as resp:
                await resp.json()