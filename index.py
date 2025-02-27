# -*- coding: utf-8 -*-

# import
import os
import time
import discord
import discord.ext
from discord import app_commands
import traceback
import datetime
import multiprocessing
import requests
from dotenv import load_dotenv
import re
import traceback
import pickle
load_dotenv()

# util
from util.message_util import send_message_in_chunks

# plugin
from plugin.ssh_tool import call_ssh
from plugin.gemini_llm import get_gemini_chat, get_gemini_ssh_chat

# discord
intent = discord.Intents.default()
intent.emojis = True
intent.message_content = True
intent.messages = True
client = discord.Client(intents=intent)
tree = app_commands.CommandTree(client)

# init variable
ssh_credentials = {}
def save_ssh_credential():
    global ssh_credentials
    with open('ssh_credentials.pkl', 'wb') as f:
        pickle.dump(ssh_credentials, f)
def load_ssh_credential():
    global ssh_credentials
    with open('ssh_credentials.pkl', 'rb') as f:
        ssh_credentials = pickle.load(f)
try:
    load_ssh_credential()
except:
    ssh_credentials = {}

llmUserCooltime = {}
llmHistory = {}
llmIsRunning = {}
llmDelay = 1

# discord commands
@tree.command(name="set_ssh")
async def set_ssh_credentials(interaction: discord.Interaction, hostname: str, username: str, password: str, memo: str = ""):
    global ssh_credentials
    """
    Slash command to set SSH credentials, with an optional memo.
    """
    guildId = interaction.guild.id
    ssh_credentials[guildId] = {}
    ssh_credentials[guildId]["hostname"] = hostname
    if ":" in hostname:
        ssh_credentials[guildId]["port"] = int(hostname.split(":")[1])  # Ensure port is an integer
        ssh_credentials[guildId]["hostname"] = hostname.split(":")[0]  # Update the hostname without the port
    else:
        ssh_credentials[guildId]["port"] = 22
    ssh_credentials[guildId]["username"] = username
    ssh_credentials[guildId]["password"] = password
    ssh_credentials[guildId]["memo"] = memo  # Update memo
    save_ssh_credential()
    reset_llm(guildId)
    #await interaction.delete_original_response()
    await interaction.response.send_message("SSH credentials updated successfully.")

@client.event
async def on_ready():
    #await tree.sync()
    print("We have logged in as {0.user}".format(client))

isSync = {}

def reset_llm(guildId):
    global ssh_credentials 
    if guildId in ssh_credentials:
        llmHistory[guildId] = get_gemini_ssh_chat(ssh_credentials[guildId]['memo'])
    else:
        llmHistory[guildId] = get_gemini_chat()

@client.event
async def on_message(message):
    global llmUserCooltime, llmIsRunning, model, eongtemplate, isSync
    if message.guild == None:
        return
    if message.content == None:
        # reject no message
        return
    if message.channel == None:
        # reject DM
        return
    if message.author == client.user:
        # reject echo
        return
    if message.author.bot == True:
        return
    guildId = message.guild.id
    try:
        userLastMessage = message.content

        nowtime = datetime.datetime.now()
        # init dict
        if guildId in llmUserCooltime:
            pass
        else:
            llmUserCooltime[guildId] = nowtime - datetime.timedelta(
                seconds=llmDelay 
            )

        # 메시지 즉시답변
        if "-llm" in message.channel.name:
            if guildId in llmIsRunning:
                response = "please wait for the previous command to finish"
            elif userLastMessage.startswith("!초기화") or userLastMessage.startswith("!reset"):
                reset_llm(guildId)
                await message.channel.send(
                    content="[command] 컨텍스트 초기화되었습니다. 이제부터는 새로운 질문에 대해서만 답변드리겠습니다."
                )
            elif userLastMessage.startswith("!"):
                # !시작은 LLM 무시
                return
            else:
                async with message.channel.typing():
                    llmIsRunning[guildId] = 1
                    nowtime = datetime.datetime.now()
                    llmUserCooltime[guildId] = nowtime - datetime.timedelta(
                        seconds=60
                    )
                    if not (guildId in llmHistory):
                        reset_llm(guildId)
                    fullmessage = ""
                    try:
                        await llmHistory[guildId].send_message_async(userLastMessage)
                        aio = llmHistory[guildId].last.text
                        pattern1 = r"ssh\\(.*?)\\"
                        if re.search(pattern1, llmHistory[guildId].last.text):
                            match1 = re.search(pattern1, llmHistory[guildId].last.text)
                            # 셸 체크
                            if match1:
                                aiowithoutssh = aio.replace(match1.group(1), "").replace("ssh\\","").replace("\\","")
                                if aiowithoutssh.replace(" ","").replace("\n","") != "":
                                    await send_message_in_chunks(message, aiowithoutssh)
                                # call
                                await send_message_in_chunks(message, "⏳ run " + match1.group(1))
                                result = await call_ssh(match1.group(1), ssh_credentials[guildId], message, client)
                                if(result.replace(" ", "") == ""):
                                    result = "no output"
                                #await send_message_in_chunks(message, "```"+remove_escape(result)+"```")
                                llmHistory[guildId].send_message(result)
                                await send_message_in_chunks(
                                    message, llmHistory[guildId].last.text
                                )
                        else:
                            await send_message_in_chunks(
                                message, aio
                            )
                        nowtime = datetime.datetime.now()
                    except Exception as e:
                        await message.channel.send(
                            str(e) + str(llmHistory[guildId].last)
                        )
                        print(e)
                        llmUserCooltime[guildId] = nowtime - datetime.timedelta(
                            seconds=llmDelay 
                        )

                llmUserCooltime[guildId] = nowtime
                llmIsRunning.pop(guildId, None)
    except Exception as e:
        print(e)
        # print stack trace
        print(traceback.format_exc())
        #await message.channel.send(str(e))

if __name__ == "__main__":
    multiprocessing.freeze_support()
    client.run(os.getenv("DISCORD_TOKEN"))
