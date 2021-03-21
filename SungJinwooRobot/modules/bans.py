import html
import telethon

from telegram import ParseMode, Update
from telegram.error import BadRequest
from telegram.ext import CommandHandler, Filters, run_async, CallbackContext
from telegram.utils.helpers import mention_html


from SungJinwooRobot import LOGGER, dispatcher
from SungJinwooRobot.modules.disable import DisableAbleCommandHandler
from SungJinwooRobot.modules.helper_funcs.admin_rights import user_can_ban
from SungJinwooRobot.modules.helper_funcs.alternate import typing_action
from SungJinwooRobot.modules.helper_funcs.chat_status import (
    bot_admin,
    can_restrict,
    is_user_admin,
    is_user_ban_protected,
    is_user_in_chat,
    user_admin,
    can_delete,
)

from SungJinwooRobot.modules.helper_funcs.extraction import extract_user_and_text
from SungJinwooRobot.modules.helper_funcs.string_handling import extract_time
from SungJinwooRobot.modules.log_channel import loggable
from SungJinwooRobot.modules.tr_engine.strings import tld


@run_async
@bot_admin
@can_restrict
@user_admin
@loggable
@typing_action
def ban(update, context):
    chat = update.effective_chat
    user = update.effective_user
    message = update.effective_message
    args = context.args

    if user_can_ban(chat, user, context.bot.id) is False:
        message.reply_text("You don't have enough rights to ban users!")
        return ""

    user_id, reason = extract_user_and_text(message, args)

    if not user_id:
        message.reply_text("Dude atleast refer some user to ban!")
        return ""

    try:
        member = chat.get_member(user_id)
    except BadRequest as excp:
        if excp.message == "User not found":
            message.reply_text("I can't seem to find this user")
            return ""
        else:
            raise

    if is_user_ban_protected(chat, user_id, member):
        message.reply_text(
            "I'm not gonna ban an admin, don't make fun of yourself b-baka!")
        return ""

    if user_id == context.bot.id:
        message.reply_text("性交オフ")
        return ""

    log = (
        "<b>{}:</b>"
        "\n#BANNED"
        "\n<b>Admin:</b> {}"
        "\n<b>User:</b> {} (<code>{}</code>)".format(
            html.escape(chat.title),
            mention_html(user.id, user.first_name),
            mention_html(member.user.id, member.user.first_name),
            member.user.id,
        )
    )
    if reason:
        log += "\n<b>Reason:</b> {}".format(reason)

    try:
        chat.kick_member(user_id)
        # context.bot.send_sticker(chat.id, BAN_STICKER)  # banhammer marie
        # sticker
        context.bot.sendMessage(
            chat.id,
            "User got banned: {}".format(
                mention_html(member.user.id, member.user.first_name)
            ),
            parse_mode=ParseMode.HTML,
        )
        return log

    except BadRequest as excp:
        if excp.message == "Reply message not found":
            # Do not reply
            message.reply_text("Banned!", quote=False)
            return log
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

######################
@run_async
@bot_admin
@can_restrict
@user_admin
@loggable
@typing_action
def dban(update, context):
    chat = update.effective_chat  # type: Optional[Chat]
    user = update.effective_user  # type: Optional[User]
    message = update.effective_message  # type: Optional[Message]
    args = context.args
    bot = context.bot


    if user_can_ban (chat, user, context.bot.id) is False:
        message.reply_text("You don't have enough rights to ban users!")
        return ""

    if message.reply_to_message:
        user = update.effective_user  # type: Optional[User]
        chat = update.effective_chat  # type: Optional[Chat]
        if can_delete(chat, bot.id):
            update.effective_message.reply_to_message.delete()
    else:
        message.reply_text("You have to reply to a message to delete it and ban the user.")
        return ""

    user_id, reason = extract_user_and_text(message, args)

    try:
        member = chat.get_member(user_id)
    except BadRequest as excp:
        if excp.message == "User not found":
            message.reply_text("I can't seem to find this user")
            return ""
        else:
            raise

    if is_user_ban_protected(chat, user_id, member):
        message.reply_text("I'm not gonna ban an admin, don't make fun of yourself!")
        return ""

    if user_id == context.bot.id:
        message.reply_text("I'm not gonna ban myself, that's pretty dumb idea!")
        return ""
    
    if user_id == 777000 or user_id == 1087968824:
        message.reply_text(str(user_id) + " is an account reserved for telegram, I cannot ban it!")
        return ""            

    log = (
        "<b>{}:</b>"
        "\n#BANNED"
        "\n<b>Admin:</b> {}"
        "\n<b>User:</b> {} (<code>{}</code>)".format(   
            html.escape(chat.title),
            mention_html(user.id, user.first_name),
            mention_html(member.user.id, member.user.first_name),
            member.user.id,
        )
    )
    if reason:
        log += "\n<b>Reason:</b> {}".format(reason)

    try:
        chat.kick_member(user_id)
        context.bot.sendMessage(
            chat.id,
            "Admin {} has successfully banned {} in <b>{}</b>!.".format(
                mention_html(user.id, user.first_name),
                mention_html(member.user.id, member.user.first_name),
                html.escape(chat.title)
            ),
            parse_mode=ParseMode.HTML,
        )
        return log

    except BadRequest as excp:
        if excp.message == "Reply message not found":
            # Do not reply
            message.reply_text("Banned!", quote=False)
            return log
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
################

@run_async
@bot_admin
@can_restrict
@user_admin
@loggable
@typing_action
def temp_ban(update, context):
    chat = update.effective_chat
    user = update.effective_user
    message = update.effective_message
    args = context.args

    if user_can_ban(chat, user, context.bot.id) is False:
        message.reply_text(
            "You don't have enough rights to temporarily ban someone!")
        return ""

    user_id, reason = extract_user_and_text(message, args)

    if not user_id:
        message.reply_text("Dude! atleast refer some user to ban...")
        return ""

    try:
        member = chat.get_member(user_id)
    except BadRequest as excp:
        if excp.message == "User not found":
            message.reply_text("I can't seem to find this user")
            return ""
        else:
            raise

    if is_user_ban_protected(chat, user_id, member):
        message.reply_text("Wow! let's start banning Admins themselves?...")
        return ""

    if user_id == context.bot.id:
        message.reply_text("性交オフ -_-")
        return ""

    if not reason:
        message.reply_text(
            "You haven't specified a time to ban this user for!")
        return ""

    split_reason = reason.split(None, 1)

    time_val = split_reason[0].lower()
    if len(split_reason) > 1:
        reason = split_reason[1]
    else:
        reason = ""

    bantime = extract_time(message, time_val)

    if not bantime:
        return ""

    log = (
        "<b>{}:</b>"
        "\n#TEMP BANNED"
        "\n<b>Admin:</b> {}"
        "\n<b>User:</b> {} (<code>{}</code>)"
        "\n<b>Time:</b> {}".format(
            html.escape(chat.title),
            mention_html(user.id, user.first_name),
            mention_html(member.user.id, member.user.first_name),
            member.user.id,
            time_val,
        )
    )
    if reason:
        log += "\n<b>Reason:</b> {}".format(reason)

    try:
        chat.kick_member(user_id, until_date=bantime)
        # context.bot.send_sticker(chat.id, BAN_STICKER)  # banhammer marie
        # sticker
        message.reply_text(
            "Banned! User will be banned for {}.".format(time_val))
        return log

    except BadRequest as excp:
        if excp.message == "Reply message not found":
            # Do not reply
            message.reply_text(
                "Goodbye.. we'll meet after {}.".format(time_val), quote=False
            )
            return log
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
  
######### SBAN ###########
@run_async
@bot_admin
@can_restrict
@user_admin
@loggable
def sban(update, context):
    bot = context.bot
    args = context.args
    chat = update.effective_chat  # type: Optional[Chat]
    user = update.effective_user  # type: Optional[User]
    message = update.effective_message  # type: Optional[Message]

    update.effective_message.delete()

    user_id, reason = extract_user_and_text(message, args)

    if not user_id:
        return ""

    try:
        member = chat.get_member(user_id)
    except BadRequest as excp:
        if excp.message == "User not found":
            return ""
        else:
            raise

    if is_user_ban_protected(chat, user_id, member):
        return ""

    if user_id == bot.id:
        return ""

    log = tld(chat.id, "bans_sban_logger").format(
        html.escape(chat.title), mention_html(user.id, user.first_name),
        mention_html(member.user.id, member.user.first_name), user_id)
    if reason:
        log += tld(chat.id, "bans_logger_reason").format(reason)

    try:
        chat.kick_member(user_id)
        return log

    except BadRequest as excp:
        if excp.message == "Reply message not found":
            return log
        else:
            LOGGER.warning(update)
            LOGGER.exception("ERROR banning user %s in chat %s (%s) due to %s",
                             user_id, chat.title, chat.id, excp.message)
    return ""

########### SBAN ###########


  
@run_async
@bot_admin
@can_restrict
@user_admin
@user_can_ban
@loggable
def stemp_ban(update, context): 
    chat = update.effective_chat
    user = update.effective_user
    message = update.effective_message
    log_message = ""
    bot, args = context.bot, context.args
    user_id, reason = extract_user_and_text(message, args)
    update.effective_message.delete()
    if not user_id:
        return log_message


    try:
        member = chat.get_member(user_id)
    except BadRequest as excp:
        if excp.message == "User not found":
            return log_message
        else:
            raise

    if user_id == bot.id:
        return log_message

    if is_user_ban_protected(chat, user_id, member):
        return log_message

    if not reason:
        message.reply_text("You haven't specified a time to ban this user for!")
        return log_message

    split_reason = reason.split(None, 1)

    time_val = split_reason[0].lower()
    if len(split_reason) > 1:
        reason = split_reason[1]
    else:
        reason = ""

    bantime = extract_time(message, time_val)

    if not bantime:
        return log_message

    log = (
        f"<b>{html.escape(chat.title)}:</b>\n"
        "#STEMP BANNED\n"
        f"<b>Admin:</b> {mention_html(user.id, html.escape(user.first_name))}\n"
        f"<b>User:</b> {mention_html(member.user.id, html.escape(member.user.first_name))}\n"
        f"<b>Time:</b> {time_val}")
    if reason:
        log += "\n<b>Reason:</b> {}".format(reason)

    try:
        chat.kick_member(user_id, until_date=bantime)
        bot.send_sticker(chat.id, BAN_STICKER)  #banhammer marie sticker
        return log

    except BadRequest as excp:
        if excp.message == "Reply message not found":
            # Do not reply
            return log
        else:
            LOGGER.warning(update)
            LOGGER.exception("ERROR banning user %s in chat %s (%s) due to %s",
                             user_id, chat.title, chat.id, excp.message)
    return log_message


########## dkick ##########

@run_async
@bot_admin
@can_restrict
@user_admin
@loggable
@typing_action
def dkick(update, context):
    chat = update.effective_chat  # type: Optional[Chat]
    user = update.effective_user  # type: Optional[User]
    message = update.effective_message  # type: Optional[Message]
    args = context.args
    bot = context.bot

    if user_can_ban(chat, user, context.bot.id) is False:
        message.reply_text("You don't have enough rights to kick users!")
        return ""

    if message.reply_to_message:
        user = update.effective_user  # type: Optional[User]
        chat = update.effective_chat  # type: Optional[Chat]
        if can_delete(chat, bot.id):
            update.effective_message.reply_to_message.delete()
    else:
        message.reply_text("You have to reply to a message to delete it and kick the user.")
        return ""

    user_id, reason = extract_user_and_text(message, args)

    try:
        member = chat.get_member(user_id)
    except BadRequest as excp:
        if excp.message == "User not found":
            message.reply_text("I can't seem to find this user")
            return ""
        else:
            raise

    if is_user_ban_protected(chat, user_id):
        message.reply_text("Yeahh... let's start kicking admins?")
        return ""

    if user_id == context.bot.id:
        message.reply_text("Yeahhh I'm not gonna do that")
        return ""
    
    if user_id == 777000 or user_id == 1087968824:
        message.reply_text(str(user_id) + " is an account reserved for telegram, I cannot kick it!")
        return ""  

    res = chat.unban_member(user_id)  # unban on current user = kick
    if res:
        
        context.bot.sendMessage(
            chat.id,
            "Admin {} has successfully kicked {} in <b>{}</b>!".format(
            mention_html(user.id, user.first_name),
            mention_html(member.user.id, member.user.first_name),
            html.escape(chat.title)),
            parse_mode=ParseMode.HTML,
        )
        log = (
            "<b>{}:</b>"
            "\n#KICKED"
            "\n<b>Admin:</b> {}"
            "\n<b>User:</b> {} (<code>{}</code>)".format(
                html.escape(chat.title),
                mention_html(user.id, user.first_name),
                mention_html(member.user.id, member.user.first_name),
                member.user.id,
            )
        )
        if reason:
            log += "\n<b>Reason:</b> {}".format(reason)

        return log

    else:
        message.reply_text("Get Out!.")

    return ""


########## dkick ##########

@run_async
@bot_admin
@can_restrict
@user_admin
@loggable
@typing_action
def kick(update, context):
    chat = update.effective_chat
    user = update.effective_user
    message = update.effective_message
    args = context.args

    if user_can_ban(chat, user, context.bot.id) is False:
        message.reply_text("You don't have enough rights to kick users!")
        return ""

    user_id, reason = extract_user_and_text(message, args)

    if not user_id:
        return ""

    try:
        member = chat.get_member(user_id)
    except BadRequest as excp:
        if excp.message == "User not found":
            message.reply_text("I can't seem to find this user")
            return ""
        else:
            raise

    if is_user_ban_protected(chat, user_id):
        message.reply_text("Yeahh... let's start kicking admins?")
        return ""

    if user_id == context.bot.id:
        message.reply_text("Yeahhh I'm not gonna do that")
        return ""

    res = chat.unban_member(user_id)  # unban on current user = kick
    if res:
        # context.bot.send_sticker(chat.id, BAN_STICKER)  # banhammer marie
        # sticker
        context.bot.sendMessage(
            chat.id,
            "Untill we meet again {}.".format(
                mention_html(member.user.id, member.user.first_name)
            ),
            parse_mode=ParseMode.HTML,
        )
        log = (
            "<b>{}:</b>"
            "\n#KICKED"
            "\n<b>Admin:</b> {}"
            "\n<b>User:</b> {} (<code>{}</code>)".format(
                html.escape(chat.title),
                mention_html(user.id, user.first_name),
                mention_html(member.user.id, member.user.first_name),
                member.user.id,
            )
        )
        if reason:
            log += "\n<b>Reason:</b> {}".format(reason)

        return log

    else:
        message.reply_text("Get Out!.")

    return ""


@run_async
@bot_admin
@can_restrict
@loggable
@typing_action
def banme(update, context):
    user_id = update.effective_message.from_user.id
    chat = update.effective_chat
    user = update.effective_user
    if is_user_admin(update.effective_chat, user_id):
        update.effective_message.reply_text("Yeahhh.. not gonna ban an admin.")
        return

    res = update.effective_chat.kick_member(user_id)
    if res:
        update.effective_message.reply_text("Yes, you're right! GTFO..")
        log = ("<b>{}:</b>"
               "\n#BANME"
               "\n<b>User:</b> {}"
               "\n<b>ID:</b> <code>{}</code>".format(html.escape(chat.title),
                                                     mention_html(user.id,
                                                                  user.first_name),
                                                     user_id))
        return log

    else:
        update.effective_message.reply_text("Huh? I can't :/")

@run_async
@bot_admin
@can_restrict
@user_admin
@user_can_ban
@loggable
def skick(update, context): 
    chat = update.effective_chat
    user = update.effective_user
    message = update.effective_message
    log_message = ""
    bot, args = context.bot, context.args
    user_id, reason = extract_user_and_text(message, args)
    update.effective_message.delete()
    if not user_id:
        return log_message

    try:
        member = chat.get_member(user_id)
    except BadRequest as excp:
        if excp.message == "User not found":
            return log_message
        else:
            raise

    if user_id == bot.id:
        return log_message

    if is_user_ban_protected(chat, user_id):
        return log_message

   res = chat.unban_member(user_id)  # unban on current user = kick
    if res:
        log = (
            f"<b>{html.escape(chat.title)}:</b>\n"
            f"#SKICKED\n"
            f"<b>Admin:</b> {mention_html(user.id, html.escape(user.first_name))}\n"
            f"<b>User:</b> {mention_html(member.user.id, html.escape(member.user.first_name))}"
        )
        if reason:
            log += f"\n<b>Reason:</b> {reason}"

       return log

    return log_message
        
@run_async
@bot_admin
@can_restrict
@typing_action
def kickme(update, context):
    user_id = update.effective_message.from_user.id
    if is_user_admin(update.effective_chat, user_id):
        update.effective_message.reply_text(
            "Yeahhh.. not gonna kick an admin.")
        return

    res = update.effective_chat.unban_member(
        user_id)  # unban on current user = kick
    if res:
        update.effective_message.reply_text("Yeah, you're right Get Out!..")
    else:
        update.effective_message.reply_text("Huh? I can't :/")


@run_async
@bot_admin
@can_restrict
@user_admin
@loggable
@typing_action
def unban(update, context):
    message = update.effective_message
    user = update.effective_user
    chat = update.effective_chat
    args = context.args

    if user_can_ban(chat, user, context.bot.id) is False:
        message.reply_text(
            "You don't have enough rights to unban people here!")
        return ""

    user_id, reason = extract_user_and_text(message, args)

    if not user_id:
        return ""

    try:
        member = chat.get_member(user_id)
    except BadRequest as excp:
        if excp.message == "User not found":
            message.reply_text("I can't seem to find this user")
            return ""
        else:
            raise

    if user_id == context.bot.id:
        message.reply_text("How would I unban myself if I wasn't here...?")
        return ""

    if is_user_in_chat(chat, user_id):
        message.reply_text(
            "Why are you trying to unban someone who's already in this chat?"
        )
        return ""

    chat.unban_member(user_id)
    message.reply_text("Done, they can join again!")

    log = (
        "<b>{}:</b>"
        "\n#UNBANNED"
        "\n<b>Admin:</b> {}"
        "\n<b>User:</b> {} (<code>{}</code>)".format(
            html.escape(chat.title),
            mention_html(user.id, user.first_name),
            mention_html(member.user.id, member.user.first_name),
            member.user.id,
        )
    )
    if reason:
        log += "\n<b>Reason:</b> {}".format(reason)

    return log


__help__ = """

Some people need to be publicly banned; spammers, annoyances, or just trolls.
This module allows you to do that easily, by exposing some common actions, so everyone will see!
 • /kickme: Kicks the user who issued the command
 • /banme: Bans the user who issued the command

⚙️ *Admin only:*
 • /ban <userhandle>: Bans a user. (via handle, or reply)
 • /sban <userhandle>: Silently bans a user.
 • /tban <userhandle> x(m/h/d): Bans a user for x time. (via handle, or reply). m = minutes, h = hours, d = days.
 • /stban <userhandle> x(m/h/d): Silently bans a user for x time. Same as tban, but ban message will not appear. 
 • /dban <userhandle>: Bans a user and also deletes the message sent by banned user.
 • /unban <userhandle>: Unbans a user. (via handle, or reply)
 • /kick <userhandle>: Kicks a user, (via handle, or reply)
 • /dkick: Kick a user by reply, and delete their message.
 • /skick <userhandle>: Silently kicks a user, (via handle, or reply)

⚙️ *An example of temporarily banning someone:*
• /tban @username 2h: this bans a user for 2 hours.
"""


__mod_name__ = "Bans"

BAN_HANDLER = CommandHandler("ban", ban, pass_args=True, filters=Filters.group)
TEMPBAN_HANDLER = CommandHandler(
    ["tban", "tempban"], temp_ban, pass_args=True, filters=Filters.group
)
SBAN_HANDLER = DisableAbleCommandHandler("sban",
                                         sban,
                                         pass_args=True,
                                         filters=Filters.group,
                                         admin_ok=True)
KICK_HANDLER = CommandHandler(
    "kick",
    kick,
    pass_args=True,
    filters=Filters.group)
DKICK_HANDLER = CommandHandler(["dkick", "fuckoff"], dkick, pass_args=True, filters=Filters.group)
UNBAN_HANDLER = CommandHandler(
    "unban",
    unban,
    pass_args=True,
    filters=Filters.group)
KICKME_HANDLER = DisableAbleCommandHandler(
    "kickme", kickme, filters=Filters.group)
BANME_HANDLER = DisableAbleCommandHandler(
    "banme", banme, filters=Filters.group)
STEMPBAN_HANDLER = CommandHandler(["stban"], stemp_ban)
SBAN_HANDLER = CommandHandler("sban", sban)
SKICK_HANDLER = CommandHandler("skick", skick)
DBAN_HANDLER = CommandHandler("dban", dban)


dispatcher.add_handler(BAN_HANDLER)
dispatcher.add_handler(TEMPBAN_HANDLER)
dispatcher.add_handler(KICK_HANDLER)
dispatcher.add_handler(DKICK_HANDLER)
dispatcher.add_handler(UNBAN_HANDLER)
dispatcher.add_handler(KICKME_HANDLER)
dispatcher.add_handler(BANME_HANDLER)
dispatcher.add_handler(STEMPBAN_HANDLER)
dispatcher.add_handler(SKICK_HANDLER)
dispatcher.add_handler(SBAN_HANDLER)
dispatcher.add_handler(DBAN_HANDLER)