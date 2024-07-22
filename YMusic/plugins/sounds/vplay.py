from YMusic import app
from YMusic.core import userbot
from YMusic.utils import ytDetails
from YMusic.utils.queue import QUEUE, add_to_queue

from pyrogram import filters


import asyncio
import time

import config

VIDEO_PLAY = ["VP", "VPLAY"]

PREFIX = config.PREFIX

RPREFIX = config.RPREFIX


async def ytdl(link):
    proc = await asyncio.create_subprocess_exec(
        "yt-dlp",
        "-g",
        "-f",
        "best[height<=?720][width<=?1280]",
        f"{link}",
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await proc.communicate()
    if stdout:
        return 1, stdout.decode().split("\n")[0]
    else:
        return 0, stderr.decode()


async def bash(cmd):
    process = await asyncio.create_subprocess_shell(
        cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await process.communicate()
    err = stderr.decode().strip()
    out = stdout.decode().strip()
    return out, err


async def processReplyToMessage(message):
    msg = message.reply_to_message
    if msg.video or msg.video_note:
        m = await message.reply_text("Please wait... downloading your video...")
        video_original = await msg.download()
        return video_original, m
    else:
        return None


async def playWithLinks(link):
    if "&" in link:
        pass
    if "?" in link:
        pass

    return 0


@app.on_message((filters.command(VIDEO_PLAY, [PREFIX, RPREFIX])) & filters.group)
async def _vPlay(_, message):
    start_time = time.time()
    chat_id = message.chat.id
    if (message.reply_to_message) is not None:
        if message.reply_to_message.video or message.reply_to_message.video_note:
            input_filename, m = await processReplyToMessage(message)
            if input_filename is None:
                await message.reply_text(
                    "Kindly reply to a video file or give song name/yt link"
                )
                return
            await m.edit("Rukja...Tera Video Play kar raha hu...")
            Status, Text = await userbot.playVideo(chat_id, input_filename)
            if Status == False:
                await m.edit(Text)
            else:
                await message.delete()
                if chat_id in QUEUE:
                    queue_num = add_to_queue(
                        chat_id,
                        message.reply_to_message.video.title[:19],
                        message.reply_to_message.video.duration,
                        message.reply_to_message.video.file_id,
                        message.reply_to_message.link,
                    )
                    await m.edit(
                        f"# {queue_num}\n{message.reply_to_message.video.title[:19]}\nYour song has been added to the queue"
                    )
                    return
                finish_time = time.time()
                total_time_taken = str(int(finish_time - start_time)) + "s"
                await m.edit(
                    f"Playing your video\n\nVideoName:- [{message.reply_to_message.video.title[:19]}]({message.reply_to_message.link})\nDuration:- {message.reply_to_message.video.duration}\nTime taken to play:- {total_time_taken}",
                    disable_web_page_preview=True,
                )

    elif (len(message.command)) < 2:
        await message.reply_text("Kindly provide song name or link")
    else:
        m = await message.reply_text("Please wait finding your song")
        query = message.text.split(" ", 1)[1]
        try:
            if "youtu.be" in query:
                video_id = query.split("/")[3].split("?")[0]  # Extract ID from youtu.be links
            elif "https" in query:
                video_id = query.split("?v=")[1].split("&")[0]  # Extract ID from traditional links
            else:
                video_id = query
            
            title, duration, link = ytDetails.searchYt(video_id)
        except Exception as e:
            await message.reply_text(f"Error:- <code>{e}</code>")
            return

        await m.edit("Please wait downloading video of requested song")
        resp, ytlink = await ytdl(link)
        if resp == 0:
            await m.edit(f"❌ yt-dl issues detected\n\n» `{ytlink}`")
        else:
            if chat_id in QUEUE:
                queue_num = add_to_queue(chat_id, title[:19], duration, ytlink, link)
                await m.edit(
                    f"# {queue_num}\n{title[:19]}\nYour song has been added to the queue"
                )
                return
            # await asyncio.sleep(2)
            Status, Text = await userbot.playVideo(chat_id, ytlink)
            # Check if the video ended
            if Status == False:
                await m.edit(Text)
            else:
                if duration is None:
                    duration = "Playing From LiveStream"
                add_to_queue(chat_id, title[:19], duration, ytlink, link)

                finish_time = time.time()
                total_time_taken = str(int(finish_time - start_time)) + "s"
                await m.edit(
                    f"Playing your video\n\nVideoName:- [{title[:19]}]({link})\nDuration:- {duration}\nTime taken to play:- {total_time_taken}\n\n Powered by: @moonuserbot",
                    disable_web_page_preview=True,
                )
