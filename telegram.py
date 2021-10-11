# pylint: disable=C0321, C0114, W0702, C0103, C0301, R1710, W0603, W0621
"""
Adds support for Telegram Bot messaging.

To enable, provide a TELEGRAM_TOKEN environment variable.
"""

import asyncio
import logging
from os import getenv

from aiogram import Bot, Dispatcher, types
from aiogram.utils import exceptions

TELEGRAM_TOKEN = getenv('TELEGRAM_TOKEN')
TELEGRAM_USERS = getenv('TELEGRAM_USERS').split(',')

logging.basicConfig(level=logging.INFO)
log = logging.getLogger('telegam')

log.info("Module loaded.")
# TODO Remove this before merging to main.
log.info("Sending as bot %s to %s", TELEGRAM_TOKEN, TELEGRAM_USERS)

bot = Bot(token=TELEGRAM_TOKEN, parse_mode=types.ParseMode.HTML)
dp = Dispatcher(bot)


async def send_message(user_id: int, text: str, disable_notification: bool = False) -> bool:
    """
    Safe messages sender

    :param user_id:
    :param text:
    :param disable_notification:
    :return:
    """
    try:
        await bot.send_message(user_id, text, disable_notification=disable_notification)

    except exceptions.BotBlocked:
        log.error("Target [%s]: blocked by user", user_id)

    except exceptions.ChatNotFound:
        log.error("Target [%s]: invalid user ID", user_id)

    except exceptions.RetryAfter as e:
        log.error(
            "Target [%s]: flood limit exceeded, sleeping %d.", user_id, e.timeout)
        await asyncio.sleep(e.timeout)
        return await send_message(user_id, text)

    except exceptions.UserDeactivated:
        log.error("Target [ID:%s]: user is deactivated", user_id)

    except exceptions.TelegramAPIError:
        log.exception("Target [ID:%s]: failed", user_id)

    else:
        log.info("Target [ID:%s]: success", user_id)
        return True

    return False


async def send(message="Doorbell!"):
    """
    Sends a message to the envrionment-programmed recipients

    Keyword arguments:
    message -- Any string
    """
    return [await send_message(t, message) for t in TELEGRAM_USERS]
