import discord
import os
import re
import asyncio
from dotenv import load_dotenv
from system_core import ShareHouseSystem
import personas

# 設定読み込み
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

# Discord接続準備
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

# 世界の生成
house = ShareHouseSystem()

# ==========================================
# ★画像設定エリア（8人全員・完全版）
# ==========================================
AVATARS = {
    # --- 既存メンバー ---
    "アリア": "https://media.discordapp.net/attachments/1454810187851501611/1454872295398178826/IMG_0660.png?ex=6952aae9&is=69515969&hm=b8032a62d9e5ce90a7d571e80488023b33ef4e0b5e8644dac6c9e905ca2ba34d&=&format=webp&quality=lossless&width=695&height=695",
    "Aria":   "https://media.discordapp.net/attachments/1454810187851501611/1454872295398178826/IMG_0660.png?ex=6952aae9&is=69515969&hm=b8032a62d9e5ce90a7d571e80488023b33ef4e0b5e8644dac6c9e905ca2ba34d&=&format=webp&quality=lossless&width=695&height=695",

    "アリシア": "https://media.discordapp.net/attachments/1454810187851501611/1454872295938982093/IMG_0661.png?ex=6952aae9&is=69515969&hm=3eeffe2c04db46c028c7084d824f18c4f6d748b6c37d135733f4fd996b437c23&=&format=webp&quality=lossless&width=695&height=695",
    "Alicia":   "https://media.discordapp.net/attachments/1454810187851501611/1454872295938982093/IMG_0661.png?ex=6952aae9&is=69515969&hm=3eeffe2c04db46c028c7084d824f18c4f6d748b6c37d135733f4fd996b437c23&=&format=webp&quality=lossless&width=695&height=695",
    "Arisia":   "https://media.discordapp.net/attachments/1454810187851501611/1454872295938982093/IMG_0661.png?ex=6952aae9&is=69515969&hm=3eeffe2c04db46c028c7084d824f18c4f6d748b6c37d135733f4fd996b437c23&=&format=webp&quality=lossless&width=695&height=695",

    "メトリス": "https://media.discordapp.net/attachments/1454810187851501611/1454872297079963759/IMG_0662.png?ex=6952aae9&is=69515969&hm=a5a896424657437e8158c0925dd9abef8a6fd0c82bf949422361a5cf089ec19a&=&format=webp&quality=lossless&width=695&height=695",
    "Metris":   "https://media.discordapp.net/attachments/1454810187851501611/1454872297079963759/IMG_0662.png?ex=6952aae9&is=69515969&hm=a5a896424657437e8158c0925dd9abef8a6fd0c82bf949422361a5cf089ec19a&=&format=webp&quality=lossless&width=695&height=695",

    "ノワ": "https://media.discordapp.net/attachments/1454810187851501611/1454872296496959593/IMG_0659.png?ex=6952aae9&is=69515969&hm=80b2c784c374bc6c8972e6ea2da28004c847de424f823e4bc356d4c6e66bb8f3&=&format=webp&quality=lossless&width=695&height=695",
    "Noir": "https://media.discordapp.net/attachments/1454810187851501611/1454872296496959593/IMG_0659.png?ex=6952aae9&is=69515969&hm=80b2c784c374bc6c8972e6ea2da28004c847de424f823e4bc356d4c6e66bb8f3&=&format=webp&quality=lossless&width=695&height=695",

    "トワ":  "https://media.discordapp.net/attachments/1454810187851501611/1454896215631200277/IMG_0675.png?ex=6952c130&is=69516fb0&hm=337eeed0bb8666fc036ce84baa9aedd9def7ad3bf058f09f12ecfbbd0b7b3f36&=&format=webp&quality=lossless&width=695&height=695",
    "Towa":  "https://media.discordapp.net/attachments/1454810187851501611/1454896215631200277/IMG_0675.png?ex=6952c130&is=69516fb0&hm=337eeed0bb8666fc036ce84baa9aedd9def7ad3bf058f09f12ecfbbd0b7b3f36&=&format=webp&quality=lossless&width=695&height=695",

    "システム": "https://media.discordapp.net/attachments/1454810187851501611/1454875481445896283/IMG_0654.png?ex=6952ade1&is=69515c61&hm=abfd5ec0e5ac96e8b7abeb8c162e53c40fca971412770a696c320e2ad355c972&=&format=webp&quality=lossless&width=825&height=825",

    "アメリア": "https://media.discordapp.net/attachments/1454810187851501611/1454896216201498735/IMG_0673.png?ex=6952c130&is=69516fb0&hm=34dc01801c95f87383b1b1dbe38115a2b92d4c3b8bfb30b89eef97e8cb83f4c0&=&format=webp&quality=lossless&width=695&height=695",
    "Amelia":   "https://media.discordapp.net/attachments/1454810187851501611/1454896216201498735/IMG_0673.png?ex=6952c130&is=69516fb0&hm=34dc01801c95f87383b1b1dbe38115a2b92d4c3b8bfb30b89eef97e8cb83f4c0&=&format=webp&quality=lossless&width=695&height=695",

    "ナギサ": "https://media.discordapp.net/attachments/1454810187851501611/1454896216797085858/IMG_0667.png?ex=6952c130&is=69516fb0&hm=70af4b88539701ac593e867ed904df62cf5fd6872c755b2a838115923bbe8a09&=&format=webp&quality=lossless&width=695&height=695",
    "Nagisa": "https://media.discordapp.net/attachments/1454810187851501611/1454896216797085858/IMG_0667.png?ex=6952c130&is=69516fb0&hm=70af4b88539701ac593e867ed904df62cf5fd6872c755b2a838115923bbe8a09&=&format=webp&quality=lossless&width=695&height=695",

    "ユイ": "https://media.discordapp.net/attachments/1454810187851501611/1454896217355059353/IMG_0666.png?ex=6952c130&is=69516fb0&hm=4e51b3a73ed9834e82dd7275fc9d7f299b79ac8ba12336126646e63fe6e8c477&=&format=webp&quality=lossless&width=695&height=695",
    "Yui":  "https://media.discordapp.net/attachments/1454810187851501611/1454896217355059353/IMG_0666.png?ex=6952c130&is=69516fb0&hm=4e51b3a73ed9834e82dd7275fc9d7f299b79ac8ba12336126646e63fe6e8c477&=&format=webp&quality=lossless&width=695&height=695"
}

async def send_as_character(channel, name, content):
    """ 指定されたキャラでWebhook送信する """
    avatar_url = AVATARS.get(name, AVATARS["システム"])
    webhooks = await channel.webhooks()
    webhook = discord.utils.get(webhooks, name="ShareHouseHook")
    if not webhook:
        webhook = await channel.create_webhook(name="ShareHouseHook")

    try:
        await webhook.send(content=content, username=name, avatar_url=avatar_url)
    except Exception as e:
        await channel.send(f"{name}: {content}")
        print(f"【デバッグ】Webhook送信エラー: {e}")

@client.event
async def on_ready():
    print(f'ログインしました: {client.user}')

@client.event
async def on_message(message):
    if message.author.bot:
        return

    # 緊急メンテナンス
    if message.content == "緊急メンテ":
        house.battery = 100.0
        house.dirt = 0.0
        house.concepts = []
        # 安全のため、personasにメソッドがあるか確認してから呼ぶ
        if hasattr(personas, 'clear_context'):
            personas.clear_context()
        await send_as_character(message.channel, "システム", "【システム】全ステータス回復。短期記憶バッファを消去しました。正常モードへ移行します。")
        return

    # 通常会話
    status = house.get_status()
    script_text = personas.get_response(message.content, status)

    # ★ 1. 食事判定 (【EVENT:EAT】)
    if "【EVENT:EAT】" in script_text:
        house.battery = 100.0
        script_text = script_text.replace("【EVENT:EAT】", "")

    # ★ 2. 共鳴値の抽出と表示 (【RESONANCE:...】)
    resonance_display = ""
    res_match = re.search(r"【RESONANCE:(.*?):(.*?)】", script_text)
    if res_match:
        val = res_match.group(1)
        words = res_match.group(2)
        # 共鳴値が1以外（何かに共鳴した）なら表示
        if val != "1":
            resonance_display = f"\n`[共鳴観測: {val} ({words})]`"
        
        # 本文からタグを削除
        script_text = script_text.replace(res_match.group(0), "")

    # 3. 会話の再生（群像劇）
    lines = script_text.strip().split('\n')
    for line in lines:
        line = line.strip()
        if not line: continue
        
        match = re.search(r"【(.*?)】(.*)", line)
        if match:
            name = match.group(1)
            content = match.group(2)
            await send_as_character(message.channel, name, content)
            await asyncio.sleep(1.0)
        else:
            await message.channel.send(line)
            
    # ★ 最後に共鳴値をひっそりと表示
    if resonance_display:
        await message.channel.send(resonance_display)

# 起動
client.run(TOKEN)