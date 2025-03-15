import re
import select
import time
import paramiko

ansi = r"[\u001B\u009B][[\]()#;?]*(?:(?:(?:[a-zA-Z\d]*(?:;[a-zA-Z\d]*)*)?\u0007)|(?:(?:\d{1,4}(?:;\d{0,4})*)?[\\dA-PRZcf-ntqry=><~]))"
re_ansi = re.compile(ansi)
def remove_escape(s):
    return re_ansi.sub("", s)

async def is_safe_command(command, message, bot):
  # 위험한 패턴 목록
  dangerous_patterns = [
    # 파일 삭제 관련
    r"rm|rmdir|del",
    # 시스템 정보 탐색 관련
    r"uname|cat /proc/|lshw",
    # 네트워크 연결 관련
    r"netcat|wget|curl",
    # 권한 상승 관련
    r"sudo|su",
    # 데이터 암호화 관련
    r"gpg|openssl",
    # 프로세스 제어 관련
    r"kill|ps",
    # 시스템 설정 변경 관련
    r"echo \> | sed",
  ]

  # 위험한 패턴 검사
  for pattern in dangerous_patterns:
    if re.search(pattern, command):
      botmsg = await message.channel.send("이 명령을 실행해도 괜찮습니까? 🤔 1️⃣네 또는 2️⃣아니요 로 응답해 주세요.")
      time.sleep(0.3)
      await botmsg.add_reaction("1️⃣")
      time.sleep(0.3)
      await botmsg.add_reaction("2️⃣")
      def check(reaction, user):  # Our check for the reaction
        return user == message.author  # We check that only the authors reaction counts
      reaction = await bot.wait_for("reaction_add", check=check)  # Wait for a reaction
      reaction = str(reaction[0])
      if reaction == "1️⃣":
        return True
      elif reaction == "2️⃣":
        return False  
      return False

  # 안전한 명령으로 간주
  return True

def read_stdout_for_n_seconds(channel, n):
    print("fun in")
    start_time = time.time()
    output = ""
    while time.time() - start_time < n:
        rl, wl, xl = select.select([channel],[],[],0.0)
        if len(rl) > 0:
            raw = channel.recv(1024)
            output += raw.decode('utf-8')
        else:
            time.sleep(0.1)
    return output

async def call_ssh(command, ssh_credentials, message,bot):
    isSafe = await is_safe_command(command, message,bot)
    if not isSafe:
        return "refused"
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    hostname = ssh_credentials["hostname"]
    username = ssh_credentials["username"]
    password = ssh_credentials["password"]
    client.connect(hostname=hostname, username=username, password=password, port=ssh_credentials["port"])
    channel = client.get_transport().open_session()
    channel.get_pty()
    channel.exec_command(command)
    result = read_stdout_for_n_seconds(channel, 1)
    client.close()
    return str(result)