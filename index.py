import discord.ext
from discord import app_commands
import datetime
import multiprocessing
import re
import traceback
import pickle
import config


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
        # noinspection PyTypeChecker
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
    guild_id = interaction.guild.id
    ssh_credentials[guild_id] = {}
    ssh_credentials[guild_id]["hostname"] = hostname
    if ":" in hostname:
        ssh_credentials[guild_id]["port"] = int(hostname.split(":")[1])  # Ensure port is an integer
        ssh_credentials[guild_id]["hostname"] = hostname.split(":")[0]  # Update the hostname without the port
    else:
        ssh_credentials[guild_id]["port"] = 22
    ssh_credentials[guild_id]["username"] = username
    ssh_credentials[guild_id]["password"] = password
    ssh_credentials[guild_id]["memo"] = memo  # Update memo
    save_ssh_credential()
    reset_llm(guild_id)
    #await interaction.delete_original_response()
    await interaction.response.send_message("SSH credentials updated successfully.")

@client.event
async def on_ready():
    if config.sync_tree:
        await tree.sync()
    print("We have logged in as {0.user}".format(client))

isSync = {}

def reset_llm(guild_id):
    global ssh_credentials 
    if guild_id in ssh_credentials:
        llmHistory[guild_id] = get_gemini_ssh_chat(ssh_credentials[guild_id]['memo'])
    else:
        llmHistory[guild_id] = get_gemini_chat()

@client.event
async def on_message(message):
    global llmUserCooltime, llmIsRunning, model, eongtemplate, isSync
    if message.guild is None:
        return
    if message.content is None:
        # reject no message
        return
    if message.channel is None:
        # reject DM
        return
    if message.author == client.user:
        # reject echo
        return
    if message.author.bot:
        return
    guild_id = message.guild.id
    try:
        user_last_message = message.content

        nowtime = datetime.datetime.now()
        # init dict
        if guild_id in llmUserCooltime:
            pass
        else:
            llmUserCooltime[guild_id] = nowtime - datetime.timedelta(
                seconds=llmDelay 
            )

        # 메시지 즉시답변
        if "-llm" in message.channel.name:
            if guild_id in llmIsRunning:
                # response = "please wait for the previous command to finish"
                pass
            elif user_last_message.startswith("!초기화") or user_last_message.startswith("!reset"):
                reset_llm(guild_id)
                await message.channel.send(
                    content="[command] 컨텍스트 초기화되었습니다. 이제부터는 새로운 질문에 대해서만 답변드리겠습니다."
                )
            elif user_last_message.startswith("!"):
                # !시작은 LLM 무시
                return
            else:
                async with message.channel.typing():
                    llmIsRunning[guild_id] = 1
                    nowtime = datetime.datetime.now()
                    llmUserCooltime[guild_id] = nowtime - datetime.timedelta(
                        seconds=60
                    )
                    if not (guild_id in llmHistory):
                        reset_llm(guild_id)
                    try:
                        await llmHistory[guild_id].send_message_async(user_last_message)
                        aio = llmHistory[guild_id].last.text
                        pattern1 = r"ssh\\(.*?)\\"
                        if re.search(pattern1, llmHistory[guild_id].last.text):
                            match1 = re.search(pattern1, llmHistory[guild_id].last.text)
                            # 셸 체크
                            if match1:
                                aiowithoutssh = aio.replace(match1.group(1), "").replace("ssh\\","").replace("\\","")
                                if aiowithoutssh.replace(" ","").replace("\n","") != "":
                                    await send_message_in_chunks(message, aiowithoutssh)
                                # call
                                await send_message_in_chunks(message, "⏳ run " + match1.group(1))
                                result = await call_ssh(match1.group(1), ssh_credentials[guild_id], message, client)
                                if result.replace(" ", "") == "":
                                    result = "no output"
                                #await send_message_in_chunks(message, "```"+remove_escape(result)+"```")
                                llmHistory[guild_id].send_message(result)
                                await send_message_in_chunks(
                                    message, llmHistory[guild_id].last.text
                                )
                        else:
                            await send_message_in_chunks(
                                message, aio
                            )
                        nowtime = datetime.datetime.now()
                    except Exception as e:
                        await message.channel.send(
                            str(e) + str(llmHistory[guild_id].last)
                        )
                        print(e)
                        llmUserCooltime[guild_id] = nowtime - datetime.timedelta(
                            seconds=llmDelay 
                        )

                llmUserCooltime[guild_id] = nowtime
                llmIsRunning.pop(guild_id, None)
    except Exception as e:
        print(e)
        # print stack trace
        print(traceback.format_exc())
        #await message.channel.send(str(e))

if __name__ == "__main__":
    multiprocessing.freeze_support()
    client.run(config.discord_token)
