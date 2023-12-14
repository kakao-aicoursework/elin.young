from dto import ChatbotRequest
from samples import list_card
import aiohttp
import time
import logging
import openai
from project_level2 import ChatBot

# 환경 변수 처리 필요!
openai.api_key = ''
SYSTEM_MSG = "당신은 카카오 서비스 제공자입니다."
logger = logging.getLogger("Callback")

async def callback_handler(request: ChatbotRequest) -> dict:

    # ===================== start =================================
    chatbot = ChatBot()
    ChatBot.run()
    
    # ===================== end =================================
    # 참고링크1 : https://kakaobusiness.gitbook.io/main/tool/chatbot/skill_guide/ai_chatbot_callback_guide
    # 참고링크1 : https://kakaobusiness.gitbook.io/main/tool/chatbot/skill_guide/answer_json_format

    time.sleep(1.0)

    url = request.userRequest.callbackUrl

    if url:
        async with aiohttp.ClientSession() as session:
            async with session.post(url=url, json=payload, ssl=False) as resp:
                await resp.json()