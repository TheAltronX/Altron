import html

from telegram import ParseMode, Update
from telegram.error import BadRequest
from telegram.ext import CallbackContext, CommandHandler, Filters, run_async
from telegram.utils.helpers import mention_html

from Altron import (
    DEV_USERS,
    LOGGER,
    OWNER_ID,
    DRAGONS,
    DEMONS,
    TIGERS,
    WOLVES,
    dispatcher,
)
from Altron.modules.disable import DisableAbleCommandHandler
from Altron.modules.helper_funcs.chat_status import (
    bot_admin,
    can_restrict,
    connection_status,
    is_user_admin,
    is_user_ban_protected,
    is_user_in_chat,
    user_admin,
    user_can_ban,
    can_delete,
)
from Altron.modules.helper_funcs.extraction import extract_user_and_text
from Altron.modules.helper_funcs.string_handling import extract_time
from Altron.modules.log_channel import gloggable, loggable


@run_async
@connection_status
@bot_admin
@can_restrict
@user_admin
@user_can_ban
@loggable
def ban(update: Update, context: CallbackContext) -> str:
    chat = update.effective_chat
    user = update.effective_user
    message = update.effective_message
    bot = context.bot
    args = context.args
    user_id, reason = extract_user_and_text(message, args)

    if not user_id:
        message.reply_text("I doubt that's a user.")
        return ""
    try:
        member = chat.get_member(user_id)
    except BadRequest as excp:
        if excp.message != "User not found":
            raise
        message.reply_text("Can't seem to find this person.")
        return ""
    if user_id == bot.id:
        message.reply_text("Oh yeah, I can't ban myself, noob!")
        return ""

    if is_user_ban_protected(chat, user_id, member) and user not in DEV_USERS:
        if user_id == OWNER_ID:
            message.reply_text("Trying to put me against a God level disaster huh?")
        elif user_id in DEV_USERS:
            message.reply_text("I can't act against our own.")
        elif user_id in DRAGONS:
            message.reply_text(
                "Fighting this Dragon here will put civilian lives at risk."
            )
        elif user_id in DEMONS:
            message.reply_text(
                "Bring an order from Heroes association to fight a Demon disaster."
            )
        elif user_id in TIGERS:
            message.reply_text(
                "Bring an order from Heroes association to fight a Tiger disaster."
            )
        elif user_id in WOLVES:
            message.reply_text("Wolf abilities make them ban immune!")
        else:
            message.reply_text("This user has immunity and cannot be banned.")
        return ""
    if message.text.startswith("/s"):
        silent = True
        if not can_delete(chat, context.bot.id):
            return ""
    else:
        silent = False

    try:
        chat.kick_member(user_id)

        if silent:
            if message.reply_to_message:
                message.reply_to_message.delete()
            message.delete()
            return

        reply = (
            f"<code>❕</code><b>ʙᴀɴ ᴇᴠᴇɴᴛ</b>\n"
            f"<code> </code><b>•  ʙᴀɴɴᴇᴅ ʙʏ:</b> {mention_html(user.id, user.first_name)}\n"
            f"<code> </code><b>•  ᴜsᴇʀ:</b> {mention_html(member.user.id, html.escape(member.user.first_name))}"
        )
        if reason:
            reply += f"\n\n<code> </code><b>•  ʀᴇᴀsᴏɴ:</b> \n{html.escape(reason)}"
        bot.sendMessage(chat.id, reply, parse_mode=ParseMode.HTML, quote=False)
        return

    except BadRequest as excp:
        if excp.message == "Reply message not found":
            # Do not reply
            if silent:
                return
            message.reply_text("ʙᴀɴɴᴇᴅ !", quote=False)
            return
        else:
            LOGGER.warning(update)
            LOGGER.exception(
                "ERROR banning user %s in chat %s (%s) due to %s",
                user_id,
                chat.title,
                chat.id,
                excp.message,
            )
            message.reply_text("Uhm...that didn't work...")

    return ""



@run_async
@connection_status
@bot_admin
@can_restrict
@user_admin
@user_can_ban
@loggable
def temp_ban(update: Update, context: CallbackContext) -> str:
    chat = update.effective_chat
    user = update.effective_user
    message = update.effective_message
    bot, args = context.bot, context.args
    user_id, reason = extract_user_and_text(message, args)

    if not user_id:
        message.reply_text("I doubt that's a user.")
        return ""

    try:
        member = chat.get_member(user_id)
    except BadRequest as excp:
        if excp.message != "User not found":
            raise
        message.reply_text("I can't seem to find this user.")
        return ""
    if user_id == bot.id:
        message.reply_text("I'm not gonna BAN myself, are you crazy?")
        return ""

    if is_user_ban_protected(chat, user_id, member):
        message.reply_text("I don't feel like it.")
        return ""

    if not reason:
        message.reply_text("You haven't specified a time to ban this user for!")
        return ""

    split_reason = reason.split(None, 1)

    time_val = split_reason[0].lower()
    reason = split_reason[1] if len(split_reason) > 1 else ""
    bantime = extract_time(message, time_val)

    if not bantime:
        return ""

    try:
        chat.kick_member(user_id, until_date=bantime)
        # bot.send_sticker(chat.id, BAN_STICKER)  # banhammer marie sticker
        bot.sendMessage(
            chat.id,
            f"ʙᴀɴɴᴇᴅ!\nᴜsᴇʀ {mention_html(member.user.id, html.escape(member.user.first_name))} "
            f"ɪs ɴᴏᴡ ʙᴀɴɴᴇᴅ ғᴏʀ {time_val}.",
            parse_mode=ParseMode.HTML,
        )
        return ""

    except BadRequest as excp:
        if excp.message == "Reply message not found":
            # Do not reply
            message.reply_text(
                f"Banned! User will be banned for {time_val}.", quote=False
            )
            return ""
        else:
            LOGGER.warning(update)
            LOGGER.exception(
                "ERROR banning user %s in chat %s (%s) due to %s",
                user_id,
                chat.title,
                chat.id,
                excp.message,
            )
            message.reply_text("Well damn, I can't ban that user.")

    return ""



@run_async
@connection_status
@bot_admin
@can_restrict
@user_admin
@user_can_ban
@loggable
def kick(update: Update, context: CallbackContext) -> str:
    chat = update.effective_chat
    message = update.effective_message
    bot, args = context.bot, context.args
    user_id, reason = extract_user_and_text(message, args)

    if not user_id:
        message.reply_text("I doubt that's a user.")
        return ""

    try:
        member = chat.get_member(user_id)
    except BadRequest as excp:
        if excp.message != "User not found":
            raise

        message.reply_text("I can't seem to find this user.")
        return ""
    if user_id == bot.id:
        message.reply_text("Yeahhh I'm not gonna do that.")
        return ""

    if is_user_ban_protected(chat, user_id):
        message.reply_text("I really wish I could kick this user....")
        return ""

    res = chat.unban_member(user_id)  # unban on current user = kick
    if res:
        bot.sendMessage(
            chat.id,
            f"<b>•  ᴜsᴇʀ:</b> {mention_html(member.user.id, html.escape(member.user.first_name))}\n<b>•  ᴀᴄᴛɪᴏɴ: kicked!</b> ",
            parse_mode=ParseMode.HTML,
        )
        return ""

    else:
        message.reply_text("Well damn, I can't kick that user.")
    return ""



@run_async
@bot_admin
@can_restrict
def kickme(update: Update, context: CallbackContext):
    user_id = update.effective_message.from_user.id
    if is_user_admin(update.effective_chat, user_id):
        update.effective_message.reply_text("You're an admin, how can I kick you???")
        return

    res = update.effective_chat.unban_member(user_id)  # unban on current user = kick
    if res:
        update.effective_message.reply_text("Kicks you out of the group")
    else:
        update.effective_message.reply_text("Huh? I can't :/")



@run_async
@connection_status
@bot_admin
@can_restrict
@user_admin
@user_can_ban
@loggable
def unban(update: Update, context: CallbackContext) -> str:
    message = update.effective_message
    user = update.effective_user
    chat = update.effective_chat
    bot, args = context.bot, context.args
    user_id, reason = extract_user_and_text(message, args)

    if not user_id:
        message.reply_text("I doubt that's a user.")
        return ""

    try:
        member = chat.get_member(user_id)
    except BadRequest as excp:
        if excp.message != "User not found":
            raise
        message.reply_text("I can't seem to find this user.")
        return ""
    if user_id == bot.id:
        message.reply_text("How would I unban myself if I wasn't here...?")
        return ""

    if is_user_in_chat(chat, user_id):
        message.reply_text("Isn't this person already here??")
        return ""

    chat.unban_member(user_id)
    msg = (
        f"**ᴜɴʙᴀɴɴᴇᴅ ɪɴ {html.escape(chat.title)}!**\n\n"
        f"**ᴜɴʙᴀɴɴᴇᴅ ʙʏ:** {mention_html(user.id, html.escape(user.first_name))}\n"
        f"**ᴜsᴇʀ:** {mention_html(member.user.id, html.escape(member.user.first_name))}"
    )
    if reason:
        msg += f"\n\n**ʀᴇᴀsᴏɴ:** {reason}"
    message.reply_text(msg)

    return ""



@run_async
@connection_status
@bot_admin
@can_restrict
@gloggable
def selfunban(context: CallbackContext, update: Update) -> str:
    message = update.effective_message
    user = update.effective_user
    bot, args = context.bot, context.args
    if user.id not in DRAGONS or user.id not in TIGERS:
        return

    try:
        chat_id = int(args[0])
    except:
        message.reply_text("Give a valid chat ID.")
        return

    chat = bot.getChat(chat_id)

    try:
        member = chat.get_member(user.id)
    except BadRequest as excp:
        if excp.message == "User not found":
            message.reply_text("I can't seem to find this user.")
            return
        else:
            raise

    if is_user_in_chat(chat, user.id):
        message.reply_text("Aren't you already in the chat??")
        return

    chat.unban_member(user.id)
    msg = (
        f"**ᴜɴʙᴀɴɴᴇᴅ ɪɴ {html.escape(chat.title)}!**\n\n"
        f"**ᴜɴʙᴀɴɴᴇᴅ ʙʏ:** {mention_html(user.id, html.escape(user.first_name))}\n"
        f"**ᴜsᴇʀ:** {mention_html(member.user.id, html.escape(member.user.first_name))}"
    )
    message.reply_text(msg)

    return ""


__help__ = """
𝗨𝘀𝗲𝗿 𝗖𝗼𝗺𝗺𝗮𝗻𝗱𝘀:
  ➲ /kickme: ᴋɪᴄᴋꜱ ᴛʜᴇ ᴜꜱᴇʀ ᴡʜᴏ ɪꜱꜱᴜᴇᴅ ᴛʜᴇ ᴄᴏᴍᴍᴀɴᴅ

𝗔𝗱𝗺𝗶𝗻𝘀 𝗼𝗻𝗹𝘆:
  ➲ /ban <userhandle>: ʙᴀɴꜱ ᴀ ᴜꜱᴇʀ. (ᴠɪᴀ ʜᴀɴᴅʟᴇ, ᴏʀ ʀᴇᴘʟʏ)
  ➲ /sban <userhandle>: ꜱɪʟᴇɴᴛʟʏ ʙᴀɴ ᴀ ᴜꜱᴇʀ. ᴅᴇʟᴇᴛᴇꜱ ᴄᴏᴍᴍᴀɴᴅ, ʀᴇᴘʟɪᴇᴅ ᴍᴇꜱꜱᴀɢᴇ ᴀɴᴅ ᴅᴏᴇꜱɴ'ᴛ ʀᴇᴘʟʏ. (ᴠɪᴀ ʜᴀɴᴅʟᴇ, ᴏʀ ʀᴇᴘʟʏ)
  ➲ /tban <userhandle> x(m/h/d): ʙᴀɴꜱ ᴀ ᴜꜱᴇʀ ꜰᴏʀ x ᴛɪᴍᴇ. (ᴠɪᴀ ʜᴀɴᴅʟᴇ, ᴏʀ ʀᴇᴘʟʏ). ᴍ = ᴍɪɴᴜᴛᴇꜱ, ʜ = ʜᴏᴜʀꜱ, ᴅ = ᴅᴀʏꜱ.
  ➲ /unban <userhandle>: ᴜɴʙᴀɴꜱ ᴀ ᴜꜱᴇʀ. (ᴠɪᴀ ʜᴀɴᴅʟᴇ, ᴏʀ ʀᴇᴘʟʏ)
  ➲ /kick <userhandle>: ᴋɪᴄᴋꜱ ᴀ ᴜꜱᴇʀ ᴏᴜᴛ ᴏꜰ ᴛʜᴇ ɢʀᴏᴜᴘ, (ᴠɪᴀ ʜᴀɴᴅʟᴇ, ᴏʀ ʀᴇᴘʟʏ)
"""

BAN_HANDLER = CommandHandler(["ban", "sban"], ban)
TEMPBAN_HANDLER = CommandHandler(["tban"], temp_ban)
KICK_HANDLER = CommandHandler("kick", kick)
UNBAN_HANDLER = CommandHandler("unban", unban)
ROAR_HANDLER = CommandHandler("roar", selfunban)
KICKME_HANDLER = DisableAbleCommandHandler("kickme", kickme, filters=Filters.group)

dispatcher.add_handler(BAN_HANDLER)
dispatcher.add_handler(TEMPBAN_HANDLER)
dispatcher.add_handler(KICK_HANDLER)
dispatcher.add_handler(UNBAN_HANDLER)
dispatcher.add_handler(ROAR_HANDLER)
dispatcher.add_handler(KICKME_HANDLER)

__mod_name__ = "Bᴀɴs​"
__handlers__ = [
    BAN_HANDLER,
    TEMPBAN_HANDLER,
    KICK_HANDLER,
    UNBAN_HANDLER,
    ROAR_HANDLER,
    KICKME_HANDLER,
]
command_list = ['ban', 'sban', 'tban', 'kick', 'unban', 'roar', 'kickme']
