import os
from datetime import datetime, timezone

import requests
import discord
from discord import Intents
from dotenv import load_dotenv

load_dotenv()

DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
ATTENDANCE_CHANNEL_ID = os.getenv("ATTENDANCE_CHANNEL_ID")
GAS_WEBAPP_URL = os.getenv("GAS_WEBAPP_URL")
GAS_SHARED_SECRET = os.getenv("GAS_SHARED_SECRET")

if ATTENDANCE_CHANNEL_ID is None:
    raise RuntimeError("ATTENDANCE_CHANNEL_ID is not set")

if GAS_WEBAPP_URL is None:
    raise RuntimeError("GAS_WEBAPP_URL is not set")

if GAS_SHARED_SECRET is None:
    raise RuntimeError("GAS_SHARED_SECRET is not set")

try:
    ATTENDANCE_CHANNEL_ID_INT = int(ATTENDANCE_CHANNEL_ID)
except ValueError as exc:
    raise RuntimeError("ATTENDANCE_CHANNEL_ID must be an integer") from exc

CLOCK_IN_TEXT = "出勤しました"
CLOCK_OUT_TEXT = "退勤しました"

intents = Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)


def classify_message(content: str):
    trimmed = content.strip()
    if trimmed == CLOCK_IN_TEXT:
        return "clock_in"
    if trimmed == CLOCK_OUT_TEXT:
        return "clock_out"
    return None


def post_to_gas(payload: dict):
    response = requests.post(GAS_WEBAPP_URL, json=payload, timeout=10)
    response.raise_for_status()
    return response.json() if response.content else {"ok": True}


@client.event
async def on_ready():
    print(f"Logged in as {client.user} (ID: {client.user.id})")


@client.event
async def on_message(message: discord.Message):
    if message.author.bot:
        return

    if message.channel.id != ATTENDANCE_CHANNEL_ID_INT:
        return

    record_type = classify_message(message.content)
    if record_type is None:
        return

    iso_time = datetime.now(timezone.utc).isoformat()

    payload = {
        "secret": GAS_SHARED_SECRET,
        "type": record_type,
        "isoTime": iso_time,
        "userId": str(message.author.id),
        "userName": message.author.display_name,
        "messageId": str(message.id),
        "channelId": str(message.channel.id),
        "content": message.content,
    }

    try:
        result = post_to_gas(payload)
    except requests.RequestException as exc:
        await message.reply(f"打刻失敗: GASへの送信に失敗しました。{exc}")
        return
    except Exception as exc:
        await message.reply(f"打刻失敗: 想定外エラーが発生しました。{exc}")
        return

    if isinstance(result, dict) and result.get("ok"):
        await message.reply("打刻しました。")
    else:
        await message.reply(f"打刻失敗: {result}")


if __name__ == "__main__":
    if not DISCORD_BOT_TOKEN:
        raise RuntimeError("DISCORD_BOT_TOKEN is not set")

    client.run(DISCORD_BOT_TOKEN)
