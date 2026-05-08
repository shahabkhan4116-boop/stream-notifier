import discord
import os
from discord.ext import tasks
from googleapiclient.discovery import build

# ========== YOUR SETTINGS ==========
DISCORD_TOKEN = os.environ.get("DISCORD_TOKEN")
YOUTUBE_API_KEY = os.environ.get("YOUTUBE_API_KEY")
CHANNEL_ID = "UCxbQTmW6WqmSXa8GsI_D1xA"
DISCORD_CHANNEL_ID = 1502365003444129822
PING_ROLE_ID = 1502378594423410778
# ====================================

intents = discord.Intents.default()
client = discord.Client(intents=intents)
youtube = build("youtube", "v3", developerKey=YOUTUBE_API_KEY)

last_live_id = None

def check_if_live():
    request = youtube.search().list(
        part="snippet",
        channelId=CHANNEL_ID,
        eventType="live",
        type="video"
    )
    response = request.execute()
    if response["items"]:
        item = response["items"][0]
        video_id = item["id"]["videoId"]
        title = item["snippet"]["title"]
        thumbnail = item["snippet"]["thumbnails"]["high"]["url"]
        url = f"https://www.youtube.com/watch?v={video_id}"
        return video_id, title, thumbnail, url
    return None, None, None, None

@tasks.loop(seconds=5)
async def check_live():
    global last_live_id
    video_id, title, thumbnail, url = check_if_live()
    if video_id and video_id != last_live_id:
        last_live_id = video_id
        channel = client.get_channel(DISCORD_CHANNEL_ID)
        await channel.send(f"<@&{PING_ROLE_ID}> RONY IS LIVE! 🔴")
        embed = discord.Embed(
            title=title,
            url=url,
            description=f"🔴 **RONY IS LIVE! JOIN NOW!**\n\n🔗 {url}",
            color=discord.Color.red()
        )
        embed.set_image(url=thumbnail)
        embed.set_footer(text="Click the title or link to watch!")
        await channel.send(embed=embed)

@client.event
async def on_ready():
    print(f"Bot is online as {client.user}")
    check_live.start()

client.run(DISCORD_TOKEN)
