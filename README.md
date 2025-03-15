# Discord LLM SSH Agent

# Setting
`config.py` 파일을 작성하여 discord, google api key를 넣어주세요<br>
```python
discord_token = "디스코드 봇 토큰"
google_api_key = "구글 API 키"
model_name = "gemini-2.0-flash"
```

# How To Run
`pip install -r requirements.txt`<br>
`python index.py`

# Function
- ssh 접속하여 명령어 실행 및 응답
