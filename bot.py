"""Telegram Forum Topic Index Bot.

Entry point that wires together aiogram (bot-facing API) and Telethon
(MTProto userbot) to list all topics of a Telegram forum group as
clickable HTML links.
"""

from __future__ import annotations

import asyncio
import logging
import re

from aiogram import Bot, Dispatcher, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command, CommandStart
from aiogram.types import Message
from telethon import TelegramClient
from telethon.errors import FloodWaitError
from telethon.sessions import StringSession

from config import ConfigError, config
from forum import (
    GroupNotFoundError,
    NotAForumError,
    UserbotNotMemberError,
    get_forum_topics,
)
from formatter import build_topic_pages

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)

bot = Bot(token=config.bot_token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dispatcher = Dispatcher()

try:
    userbot = TelegramClient(
        StringSession(config.session_string),
        config.api_id,
        config.api_hash,
    )
except ValueError as exc:
    raise ConfigError(
        "SESSION_STRING noto'g'ri yoki bo'sh. 'python generate_session.py' "
        "buyrug'ini bajarib, to'g'ri qiymat oling va uni .env fayliga "
        "SESSION_STRING sifatida qo'shing."
    ) from exc

USERNAME_PATTERN = re.compile(r"^@?[A-Za-z0-9_]{5,32}$")

START_TEXT = (
    "👋 Assalomu alaykum!\n\n"
    "Men Telegram forum guruhlaridagi barcha mavzularni (topics) "
    "avtomatik ravishda bosiladigan havolalar ko'rinishida chiqarib "
    "beruvchi botman.\n\n"
    "Foydalanish uchun forum guruhning username'ini yuboring, masalan:\n"
    "<code>@PythonUzForum</code>\n\n"
    "Buyruqlar ro'yxati uchun /help yozing."
)

HELP_TEXT = (
    "🆘 <b>Yordam</b>\n\n"
    "1️⃣ Forum guruh username'ini @ belgisi bilan yuboring.\n"
    "   Masalan: <code>@PythonUzForum</code>\n\n"
    "2️⃣ Bot guruhni tekshiradi va forum ekanligiga ishonch hosil qiladi.\n\n"
    "3️⃣ Barcha mavzular o'zbek alifbosi bo'yicha saralanib, "
    "bosiladigan havolalar ko'rinishida yuboriladi.\n\n"
    "⚠️ Eslatma: Userbot (kuzatuvchi akkaunt) tekshirilayotgan guruhga "
    "a'zo bo'lishi shart, aks holda mavzularni o'qiy olmaydi.\n\n"
    "Buyruqlar:\n"
    "/start — Bot haqida ma'lumot\n"
    "/help — Ushbu yordam oynasi\n"
    "/about — Loyiha haqida\n"
    "/ping — Bot ishlayotganini tekshirish"
)

ABOUT_TEXT = (
    "ℹ️ <b>Loyiha haqida</b>\n\n"
    "📌 Nomi: Telegram Forum Topic Index Bot\n"
    "⚙️ Texnologiyalar: Python 3.12+, Aiogram 3.x, Telethon (MTProto)\n"
    "🎯 Vazifasi: Forum guruhlardagi barcha mavzularni avtomatik "
    "aniqlab, bosiladigan havolalar ko'rinishida taqdim etish.\n"
    "🔤 Saralash: O'zbek lotin alifbosi tartibida."
)


@dispatcher.message(CommandStart())
async def handle_start(message: Message) -> None:
    """Handle the /start command.

    Args:
        message: The incoming Telegram message.
    """
    await message.answer(START_TEXT)


@dispatcher.message(Command("help"))
async def handle_help(message: Message) -> None:
    """Handle the /help command.

    Args:
        message: The incoming Telegram message.
    """
    await message.answer(HELP_TEXT)


@dispatcher.message(Command("about"))
async def handle_about(message: Message) -> None:
    """Handle the /about command.

    Args:
        message: The incoming Telegram message.
    """
    await message.answer(ABOUT_TEXT)


@dispatcher.message(Command("ping"))
async def handle_ping(message: Message) -> None:
    """Handle the /ping command, confirming the bot is alive.

    Args:
        message: The incoming Telegram message.
    """
    await message.answer("🏓 Pong! Bot ishlayapti.")


def _is_group_username(text: str) -> bool:
    """Check whether a message text looks like a Telegram group username.

    Args:
        text: The raw message text.

    Returns:
        True if the text matches the expected username pattern.
    """
    return bool(USERNAME_PATTERN.match(text.strip()))


async def _fetch_topics_with_flood_wait_retry(username: str):
    """Fetch forum topics, transparently retrying on FloodWaitError.

    Args:
        username: The group's public username.

    Returns:
        A sorted list of Topic objects.

    Raises:
        GroupNotFoundError: If the username does not resolve to a group.
        NotAForumError: If the group is not a forum.
        UserbotNotMemberError: If the userbot lacks access to the group.
    """
    while True:
        try:
            return await get_forum_topics(userbot, username)
        except FloodWaitError as exc:
            logger.warning("FloodWait: kutilmoqda %s soniya", exc.seconds)
            await asyncio.sleep(exc.seconds)


@dispatcher.message(F.text.func(_is_group_username))
async def handle_group_username(message: Message) -> None:
    """Handle a message containing a group username and reply with topics.

    Args:
        message: The incoming Telegram message containing "@group_username".
    """
    raw_username = message.text.strip()
    clean_username = raw_username.lstrip("@")

    status_message = await message.answer("⏳ Mavzular olinmoqda, kuting...")

    try:
        topics = await _fetch_topics_with_flood_wait_retry(clean_username)
    except GroupNotFoundError:
        await status_message.edit_text("❌ Guruh topilmadi.")
        return
    except NotAForumError:
        await status_message.edit_text("❌ Ushbu guruh forum emas.")
        return
    except UserbotNotMemberError:
        await status_message.edit_text("❌ Userbot ushbu guruhga qo'shilmagan.")
        return
    except Exception:
        logger.exception("Mavzularni olishda kutilmagan xatolik yuz berdi.")
        await status_message.edit_text(
            "❌ Kutilmagan xatolik yuz berdi. Keyinroq qayta urinib ko'ring."
        )
        return

    if not topics:
        await status_message.edit_text("ℹ️ Ushbu forumda hozircha mavzular mavjud emas.")
        return

    pages = build_topic_pages(
        group_username=clean_username,
        topics=topics,
        topics_per_page=config.topics_per_page,
    )

    await status_message.delete()

    for page_text in pages:
        try:
            await message.answer(page_text, disable_web_page_preview=True)
        except Exception:
            logger.exception("Sahifani yuborishda xatolik yuz berdi.")
        await asyncio.sleep(0.3)


async def main() -> None:
    """Start the Telethon userbot session and run the aiogram polling loop."""
    async with userbot:
        logger.info("Userbot (Telethon) muvaffaqiyatli ulandi.")
        logger.info("Aiogram bot polling boshlanmoqda...")
        await dispatcher.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot to'xtatildi.")
