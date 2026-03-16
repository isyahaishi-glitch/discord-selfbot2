import discord
from discord.ext import commands, tasks
import asyncio
import sys
import json
import msg
from dotenv import load_dotenv
import os
import time

load_dotenv()
bot1 = os.getenv('bot1')

if len(sys.argv) < 2:
    print("Error: JSON config tidak diberikan.")
    sys.exit(1)

raw_config = sys.argv[1]
config = json.loads(raw_config)

place = config["place"]
channel_ids = {
    "bg"          : config["channel_idbg"],
    "sign"        : config["channel_idsign"],
    "plat"        : config["channel_idplat"],
    "consumable"  : config["channel_idconsumable"],
    "block"       : config["channel_idblock"],
    "guild"       : config["channel_idguild"],
    "door"        : config["channel_iddoor"],
    "winterfest"  : config["channel_winterfest"],
    "ubiweek"     : config["channel_ubiweek"],
    "carni"       : config["channel_carni"],
    "valentine"   : config["channel_valentine"],
    "test"        : config["channel_test"],
}

msgs = {
    "bg"         : msg.msg_bg.replace("{place}", place),
    "sign"       : msg.msg_sign.replace("{place}", place),
    "plat"       : msg.msg_plat.replace("{place}", place),
    "consumable" : msg.msg_consumable.replace("{place}", place),
    "block"      : msg.msg_block.replace("{place}", place),
    "guild"      : msg.msg_guild.replace("{place}", place),
    "door"       : msg.msg_door.replace("{place}", place),
    "winterfest" : msg.msg_winterfest.replace("{place}", place),
    "ubiweek"    : msg.msg_ubiweek.replace("{place}", place),
    "carnival"   : msg.msg_carnival.replace("{place}", place),
    "valentine"  : msg.msg_valen.replace("{place}", place),
    "test"       : msg.msg_test.replace("{place}", place),
}

BLOCK_COOLDOWN = 6 * 3600  # 6 jam dalam detik
TIMESTAMP_FILE = f"block_last_sent_{place}.txt"

def can_send_block():
    if not os.path.exists(TIMESTAMP_FILE):
        return True
    with open(TIMESTAMP_FILE, "r") as f:
        last = float(f.read().strip())
    return (time.time() - last) >= BLOCK_COOLDOWN

def save_block_timestamp():
    with open(TIMESTAMP_FILE, "w") as f:
        f.write(str(time.time()))

bot = commands.Bot(command_prefix="!")

async def send_msg(d):
    await asyncio.sleep(5)
    try:
        channel = bot.get_channel(channel_ids[d])
        if channel:
            await channel.send(msgs[d])
            print(f"[{place}] Sent [{d}]")
        else:
            print(f"[{place}] Channel not found: {d}")
    except discord.HTTPException as e:
        if e.status == 429:
            print(f"[{place}] Rate limited on {d}, skipping...")
        else:
            print(f"[{place}] HTTP error on {d}: {e}")

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        return
    raise error

@bot.event
async def on_ready():
    print(f"[{place}] {bot.user.name} is online")
    try:
        ds = ["bg", "sign", "plat", "consumable", "guild", "door", "winterfest", "ubiweek", "valentine"]
        for d in ds:
            await send_msg(d)

        # Block dikirim hanya kalau sudah 6 jam sejak terakhir
        if can_send_block():
            await send_msg("block")
            save_block_timestamp()
            print(f"[{place}] Block sent and timestamp saved.")
        else:
            with open(TIMESTAMP_FILE, "r") as f:
                last = float(f.read().strip())
            sisa = BLOCK_COOLDOWN - (time.time() - last)
            print(f"[{place}] Block skipped. Cooldown sisa {sisa/3600:.1f} jam.")

        print(f"[{place}] All done.")
    finally:
        await bot.close()

bot.run(bot1)