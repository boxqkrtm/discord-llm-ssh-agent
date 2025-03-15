from google.generativeai import GenerativeModel, configure
import config

configure(api_key=config.google_api_key)

generation_config = {
    "temperature": 0.9,
    "top_p": 1,
    "top_k": 1,
    "max_output_tokens": 4096,
}
safety_settings = [
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
]

def get_gemini_chat():
    model = GenerativeModel(
        model_name=config.model_name,
        tools='code_execution',
        generation_config=generation_config,
        safety_settings=safety_settings,
    )
    template = []
    return model.start_chat(history=template)

def get_gemini_ssh_chat(memo):
    model = GenerativeModel(
        model_name=config.model_name,
        generation_config=generation_config,
        safety_settings=safety_settings,
        system_instruction="당신은 친절한 챗봇입니다.\n또한 서버의 shell실행 요청을 받을 수 있으며 ssh\\실행할 커맨드내용\\ 으로 사용자에게 응답하면 됩니다. 단 ssh명령은 한 대화 턴에 한번만 사용 가능합니다.\nexample\nuser:서버 업타임좀 알려줄래?\nai:네 알겠습니다. ssh\\uptime\\\nuser:02:47:39 up 11 days, 11:37,  3 users,  load average: 0.15, 0.07, 0.02\nai: 지금 서버 업타임은 11일 입니다."+memo
    )
    template = []
    return model.start_chat(history=template)
