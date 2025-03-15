import time


async def send_message_in_chunks(message, content):
    content = str(content)
    if content.replace("\n", "") == "":
        return
    chunk_size = 2000
    for i in range(0, len(content), chunk_size):
        await message.channel.send(content=content[i : i + chunk_size])
        time.sleep(0.5)  # 0.5초 간격으로 보내기 위해 sleep을 사용
