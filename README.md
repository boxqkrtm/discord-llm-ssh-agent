# Discord LLM SSH Agent

## 설정 (Setting)
`config.py` 파일을 작성하여 다음 설정을 넣어주세요<br>
```python
discord_token = "디스코드 봇 토큰"
google_api_key = "구글 API 키"
model_name = "gemini-2.0-flash"  # 사용할 Gemini 모델 (gemini-1.0-pro, gemini-1.5-pro 등 사용 가능)
ALWAYS_RESPONSE_CHANNEL_SUFFIX = "-llm"  # 자동 응답할 채널 이름 접미사
```

## 실행 방법 (How To Run)
`pip install -r requirements.txt`<br>
`python index.py`

## 기능 (Function)
- SSH 접속하여 명령어 실행 및 응답
- 디스코드 채널 이름에 ALWAYS_RESPONSE_CHANNEL_SUFFIX가 포함된 채널에서 자동 응답
- `/set_ssh` 명령어를 통해 SSH 접속 정보 설정 (호스트명, 사용자명, 비밀번호, 메모)
- `!초기화` 또는 `!reset` 명령어로 대화 컨텍스트 초기화
- Gemini AI를 활용한 자연어 처리 및 SSH 명령어 실행
