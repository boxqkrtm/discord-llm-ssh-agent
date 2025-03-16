# Discord LLM SSH Agent

## 설정 (Setting)
`config.py` 파일을 작성하여 다음 설정을 넣어주세요<br>
```python
discord_token = "디스코드 봇 토큰"
google_api_key = "구글 API 키"
model_name = "gemini-2.0-flash"  # 사용할 Gemini 모델 (gemini-1.0-pro, gemini-1.5-pro 등 사용 가능)
ALWAYS_RESPONSE_CHANNEL_SUFFIX = "-llm"  # 자동 응답할 채널 이름 접미사
QUESTION_PREFIX = "!질문 "  # 채널 이름과 상관없이 응답할 메시지 접두사
```

## 실행 방법 (How To Run)
`pip install -r requirements.txt`<br>
`python index.py`

## 기능 (Function)
- SSH 접속하여 명령어 실행 및 응답
- 디스코드 채널 이름에 ALWAYS_RESPONSE_CHANNEL_SUFFIX가 포함된 채널에서 자동 응답
- 채널 이름과 상관없이 QUESTION_PREFIX로 시작하는 메시지에 자동 응답
- `/set_ssh` 명령어를 통해 SSH 접속 정보 설정 (호스트명, 사용자명, 비밀번호, 메모)
- `/reset_ssh` 명령어로 SSH 접속 정보 초기화
- `/test_ssh` 명령어로 SSH 연결 테스트
- `/list_ssh` 명령어로 현재 SSH 설정 정보 확인
- `!초기화` 또는 `!reset` 명령어로 대화 컨텍스트 초기화
- Gemini AI를 활용한 자연어 처리 및 SSH 명령어 실행

## SSH 명령어 (SSH Commands)
모든 SSH 관련 명령어는 서버 관리자 권한이 있는 사용자만 사용할 수 있습니다.

1. `/set_ssh` - SSH 접속 정보 설정
   - 매개변수: hostname, username, password, memo(선택사항)
   - 예시: `/set_ssh hostname=example.com username=user password=pass memo=서버메모`

2. `/reset_ssh` - SSH 접속 정보 초기화
   - 현재 서버에 저장된 SSH 접속 정보를 모두 삭제합니다.

3. `/test_ssh` - SSH 연결 테스트
   - 저장된 SSH 접속 정보를 사용하여 연결 테스트를 수행합니다.

4. `/list_ssh` - SSH 설정 정보 확인
   - 현재 서버에 저장된 SSH 접속 정보를 표시합니다 (비밀번호는 마스킹 처리).
