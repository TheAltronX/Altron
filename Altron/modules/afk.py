import re
import time

from pyrogram import filters
from pyrogram.types import Message

from Altron import pbot
from Altron.helper_extra.afk_mongo import is_afk, add_afk, remove_afk

afkcheacker = 31

def get_readable_time(seconds: int) -> str:
    count = 0
    ping_time = ""
    time_list = []
    time_suffix_list = ["s", "m", "h", "days"]
    while count < 4:
        count += 1
        if count < 3:
            remainder, result = divmod(seconds, 60)
        else:
            remainder, result = divmod(seconds, 24)
        if seconds == 0 and remainder == 0:
            break
        time_list.append(int(result))
        seconds = int(remainder)
    for i in range(len(time_list)):
        time_list[i] = str(time_list[i]) + time_suffix_list[i]
    if len(time_list) == 4:
        ping_time += time_list.pop() + ", "
    time_list.reverse()
    ping_time += ":".join(time_list)
    return ping_time


@pbot.on_message(filters.command(["afk", f"afk@AltronXRobot"]))
async def afk(_, message: Message):
    if message.sender_chat:
        return
    user_id = message.from_user.id
    verifier, reasondb = await is_afk(user_id)
    if verifier:
        await remove_afk(user_id)
        try:
            afktype = reasondb["type"]
            timeafk = reasondb["time"]
            data = reasondb["data"]
            seenago = get_readable_time((int(time.time() - timeafk)))
            # count of afk time here
            if afktype == ("text" or "text_reason"):
                return await message.reply_text(
                    f"{message.from_user.first_name} ɪꜱ ʙᴀᴄᴋ ᴏɴʟɪɴᴇ\n\nʏᴏᴜ ᴡᴇʀᴇ ᴀᴡᴀʏ ꜰᴏʀ: `{seenago}`",
                    disable_web_page_preview=True,
                )
            if afktype == "animation":
                return await message.reply_animation(
                    data,
                    caption=f"{message.from_user.first_name} ɪꜱ ʙᴀᴄᴋ ᴏɴʟɪɴᴇ\n\nʏᴏᴜ ᴡᴇʀᴇ ᴀᴡᴀʏ ꜰᴏʀ: `{seenago}`",
                )
            if afktype == "photo":
                return await message.reply_photo(
                    photo=f"downloads/{user_id}.jpg",
                    caption=f"{message.from_user.first_name} ɪꜱ ʙᴀᴄᴋ ᴏɴʟɪɴᴇ\n\nʏᴏᴜ ᴡᴇʀᴇ ᴀᴡᴀʏ ꜰᴏʀ: `{seenago}`",
                )
        except Exception as e:
            return await message.reply_text(
                f"{message.from_user.first_name} ɪꜱ ʙᴀᴄᴋ ᴏɴʟɪɴᴇ",
                disable_web_page_preview=True,
            )
    if len(message.command) == 1 and not message.reply_to_message:
        details = {
            "type": "text",
            "time": time.time(),
            "data": None,
            "reason": None,
        }
    elif len(message.command) > 1 and not message.reply_to_message:
        _reason = (message.text.split(None, 1)[1].strip())[:100]
        details = {
            "type": "text_reason",
            "time": time.time(),
            "data": None,
            "reason": _reason,
        }
    elif (
        len(message.command) == 1
        and message.reply_to_message.animation
    ):
        _data = message.reply_to_message.animation.file_id
        details = {
            "type": "animation",
            "time": time.time(),
            "data": _data,
            "reason": None,
        }
    elif (
        len(message.command) > 1
        and message.reply_to_message.animation
    ):
        _data = message.reply_to_message.animation.file_id
        _reason = (message.text.split(None, 1)[1].strip())[:100]
        details = {
            "type": "animation",
            "time": time.time(),
            "data": _data,
            "reason": _reason,
        }
    elif len(message.command) == 1 and message.reply_to_message.photo:
        await pbot.download_media(
            message.reply_to_message, file_name=f"{user_id}.jpg"
        )
        details = {
            "type": "photo",
            "time": time.time(),
            "data": None,
            "reason": None,
        }
    elif len(message.command) > 1 and message.reply_to_message.photo:
        await pbot.download_media(
            message.reply_to_message, file_name=f"{user_id}.jpg"
        )
        _reason = message.text.split(None, 1)[1].strip()
        details = {
            "type": "photo",
            "time": time.time(),
            "data": None,
            "reason": _reason,
        }
    elif (
        len(message.command) == 1 and message.reply_to_message.sticker
    ):
        if message.reply_to_message.sticker.is_animated:
            details = {
                "type": "text",
                "time": time.time(),
                "data": None,
                "reason": None,
            }
        else:
            await pbot.download_media(
                message.reply_to_message, file_name=f"{user_id}.jpg"
            )
            details = {
                "type": "photo",
                "time": time.time(),
                "data": None,
                "reason": None,
            }
    elif (
        len(message.command) > 1 and message.reply_to_message.sticker
    ):
        _reason = (message.text.split(None, 1)[1].strip())[:100]
        if message.reply_to_message.sticker.is_animated:
            details = {
                "type": "text_reason",
                "time": time.time(),
                "data": None,
                "reason": _reason,
            }
        else:
            await pbot.download_media(
                message.reply_to_message, file_name=f"{user_id}.jpg"
            )
            details = {
                "type": "photo",
                "time": time.time(),
                "data": None,
                "reason": _reason,
            }
    else:
        details = {
            "type": "text",
            "time": time.time(),
            "data": None,
            "reason": None,
        }

    await add_afk(user_id, details)
    await message.reply_text(
        f"{message.from_user.first_name} ɪꜱ ᴜɴᴀᴠᴀɪʟᴀʙʟᴇ"
    )

@pbot.on_message(
        filters.incoming,
        group=afkcheacker
)
async def chat_watcher_func(_, message):
    if message.sender_chat:
        return
    userid = message.from_user.id
    user_name = message.from_user.first_name
    if message.entities:
        for entity in message.entities:
            if entity.type == "bot_command":
                if entity.offset == 0 and entity.length == 4:
                    text = message.text or message.caption
                    command_ = (text[0:4]).lower()
                    if command_ == "/afk":
                        return

    msg = ""
    replied_user_id = 0

    # Self AFK
    verifier, reasondb = await is_afk(userid)
    if verifier:
        await remove_afk(userid)
        try:
            afktype = reasondb["type"]
            timeafk = reasondb["time"]
            data = reasondb["data"]
            seenago = get_readable_time((int(time.time() - timeafk)))
            if afktype == ("text" or "text_reason"):
                msg += f"**{user_name}** ɪꜱ ʙᴀᴄᴋ ᴏɴʟɪɴᴇ\n\nʏᴏᴜ ᴡᴇʀᴇ ᴀᴡᴀʏ ꜰᴏʀ: `{seenago}`"
            if afktype == "animation":
                await message.reply_animation(
                    data,
                    caption=f"**{user_name}** ɪꜱ ʙᴀᴄᴋ ᴏɴʟɪɴᴇ\n\nʏᴏᴜ ᴡᴇʀᴇ ᴀᴡᴀʏ ꜰᴏʀ: `{seenago}`",
                )
            if afktype == "photo":
                await message.reply_photo(
                    photo=f"downloads/{userid}.jpg",
                    caption=f"**{user_name}** ɪꜱ ʙᴀᴄᴋ ᴏɴʟɪɴᴇ\n\nʏᴏᴜ ᴡᴇʀᴇ ᴀᴡᴀʏ ꜰᴏʀ: `{seenago}`",
                )
        except:
            msg += f"**{user_name}** ɪꜱ ʙᴀᴄᴋ ᴏɴʟɪɴᴇ"

    # Replied to a User which is AFK
    if message.reply_to_message:
        try:
            replied_first_name = (
                message.reply_to_message.from_user.first_name
            )
            replied_user_id = message.reply_to_message.from_user.id
            verifier, reasondb = await is_afk(replied_user_id)
            if verifier:
                try:
                    afktype = reasondb["type"]
                    timeafk = reasondb["time"]
                    data = reasondb["data"]
                    reasonafk = reasondb["reason"]
                    seenago = get_readable_time(
                        (int(time.time() - timeafk))
                    )
                    if afktype == "text":
                        msg += f"**{replied_first_name}** ɪꜱ ᴀꜰᴋ\n\nʟᴀꜱᴛ ꜱᴇᴇɴ : `{seenago}`"
                    if afktype == "text_reason":
                        msg += f"**{replied_first_name}** ɪꜱ ᴀꜰᴋ\nʀᴇᴀꜱᴏɴ : `{reasonafk}`\n\nʟᴀꜱᴛ ꜱᴇᴇɴ : `{seenago}`"
                    if afktype == "animation":
                        if str(reasonafk) == "None":
                            await message.reply_animation(
                                data,
                                caption=f"**{replied_first_name}** ɪꜱ ᴀꜰᴋ\n\nʟᴀꜱᴛ ꜱᴇᴇɴ : `{seenago}`",
                            )
                        else:
                            await message.reply_animation(
                                data,
                                caption=f"**{replied_first_name}** ɪꜱ ᴀꜰᴋ\nʀᴇᴀꜱᴏɴ : `{reasonafk}`\n\nʟᴀꜱᴛ ꜱᴇᴇɴ : `{seenago}`",
                            )
                    if afktype == "photo":
                        if str(reasonafk) == "None":
                            await message.reply_photo(
                                photo=f"downloads/{replied_user_id}.jpg",
                                caption=f"**{replied_first_name}** ɪꜱ ᴀꜰᴋ\n\nʟᴀꜱᴛ ꜱᴇᴇɴ : `{seenago}`",
                            )
                        else:
                            await message.reply_photo(
                                photo=f"downloads/{replied_user_id}.jpg",
                                caption=f"**{replied_first_name}** ɪꜱ ᴀꜰᴋ\nʀᴇᴀꜱᴏɴ : `{reasonafk}`\n\nʟᴀꜱᴛ ꜱᴇᴇɴ : `{seenago}`",
                            )
                except Exception as e:
                    msg += f"**{replied_first_name}** ɪꜱ ᴀꜰᴋ"
        except:
            pass

    if message.entities:
        entity = message.entities
        j = 0
        for x in range(len(entity)):
            if (entity[j].type) == "mention":
                found = re.findall("@([_0-9a-zA-Z]+)", message.text)
                try:
                    get_user = found[j]
                    user = await pbot.get_users(get_user)
                    if user.id == replied_user_id:
                        j += 1
                        continue
                except:
                    j += 1
                    continue
                verifier, reasondb = await is_afk(user.id)
                if verifier:
                    try:
                        afktype = reasondb["type"]
                        timeafk = reasondb["time"]
                        data = reasondb["data"]
                        reasonafk = reasondb["reason"]
                        seenago = get_readable_time(
                            (int(time.time() - timeafk))
                        )
                        if afktype == "text":
                            msg += f"**{user.first_name}** ɪꜱ ᴀꜰᴋ\n\nʟᴀꜱᴛ ꜱᴇᴇɴ : `{seenago}`"
                        if afktype == "text_reason":
                            msg += f"**{user.first_name}** ɪꜱ ᴀꜰᴋ\nʀᴇᴀꜱᴏɴ : `{reasonafk}`\n\nʟᴀꜱᴛ ꜱᴇᴇɴ : `{seenago}`"
                        if afktype == "animation":
                            if str(reasonafk) == "None":
                                await message.reply_animation(
                                    data,
                                    caption=f"**{user.first_name}** ɪꜱ ᴀꜰᴋ\n\nʟᴀꜱᴛ ꜱᴇᴇɴ : `{seenago}`",
                                )
                            else:
                                await message.reply_animation(
                                    data,
                                    caption=f"**{user.first_name}** ɪꜱ ᴀꜰᴋ\nʀᴇᴀꜱᴏɴ : `{reasonafk}`\n\nʟᴀꜱᴛ ꜱᴇᴇɴ : `{seenago}`",
                                )
                        if afktype == "photo":
                            if str(reasonafk) == "None":
                                await message.reply_photo(
                                    photo=f"downloads/{user.id}.jpg",
                                    caption=f"**{user.first_name}** ɪꜱ ᴀꜰᴋ\n\nʟᴀꜱᴛ ꜱᴇᴇɴ : `{seenago}`",
                                )
                            else:
                                await message.reply_photo(
                                    photo=f"downloads/{user.id}.jpg",
                                    caption=f"**{user.first_name}** ɪꜱ ᴀꜰᴋ\nʀᴇᴀꜱᴏɴ : `{reasonafk}`\n\nʟᴀꜱᴛ ꜱᴇᴇɴ : `{seenago}`",
                                )
                    except:
                        msg += (
                            f"**{user.first_name}** ɪꜱ ᴀꜰᴋ"
                        )
            elif (entity[j].type) == "text_mention":
                try:
                    user_id = entity[j].user.id
                    if user_id == replied_user_id:
                        j += 1
                        continue
                    first_name = entity[j].user.first_name
                except:
                    j += 1
                    continue
                verifier, reasondb = await is_afk(user_id)
                if verifier:
                    try:
                        afktype = reasondb["type"]
                        timeafk = reasondb["time"]
                        data = reasondb["data"]
                        reasonafk = reasondb["reason"]
                        seenago = get_readable_time(
                            (int(time.time() - timeafk))
                        )
                        if afktype == "text":
                            msg += f"**{first_name}** ɪꜱ ᴀꜰᴋ\n\nʟᴀꜱᴛ ꜱᴇᴇɴ : `{seenago}`"
                        if afktype == "text_reason":
                            msg += f"**{first_name}** ɪꜱ ᴀꜰᴋ\nʀᴇᴀꜱᴏɴ : `{user.reason}`\n\nʟᴀꜱᴛ ꜱᴇᴇɴ : `{seenago}`"
                        if afktype == "animation":
                            if str(reasonafk) == "None":
                                await message.reply_animation(
                                    data,
                                    caption=f"**{first_name}** ɪꜱ ᴀꜰᴋ\n\nʟᴀꜱᴛ ꜱᴇᴇɴ : `{seenago}`",
                                )
                            else:
                                await message.reply_animation(
                                    data,
                                    caption=f"**{first_name}** ɪꜱ ᴀꜰᴋ\nʀᴇᴀꜱᴏɴ : `{user.reason}`\n\nʟᴀꜱᴛ ꜱᴇᴇɴ : `{seenago}`",
                                )
                        if afktype == "photo":
                            if str(reasonafk) == "None":
                                await message.reply_photo(
                                    photo=f"downloads/{user_id}.jpg",
                                    caption=f"**{first_name}** ɪꜱ ᴀꜰᴋ\n\nʟᴀꜱᴛ ꜱᴇᴇɴ : `{seenago}`",
                                )
                            else:
                                await message.reply_photo(
                                    photo=f"downloads/{user_id}.jpg",
                                    caption=f"**{first_name}** ɪꜱ ᴀꜰᴋ\nʀᴇᴀꜱᴏɴ : `{user.reason}`\n\nʟᴀꜱᴛ ꜱᴇᴇɴ : `{seenago}`",
                                )
                    except:
                        msg += f"**{first_name}** ɪꜱ ᴀꜰᴋ"
            j += 1
    if msg != "":
        try:
            return await message.reply_text(
                msg, disable_web_page_preview=True
            )
        except:
            return

__mod_name__ = "Aғᴋ"
__help__ = """
𝗔𝘄𝗮𝘆 𝗙𝗿𝗼𝗺 𝗞𝗲𝘆𝗯𝗼𝗮𝗿𝗱:
  ➲ /afk <Reason>: ꜰᴏʀ ᴀᴡᴀʏ ꜰʀᴏᴍ ᴋᴇʏʙᴏᴀʀᴅ ᴏʀ ᴜɴᴀᴠᴀɪʟᴀʙɪʟɪᴛʏ ᴏꜰ ᴜꜱᴇʀ
"""
