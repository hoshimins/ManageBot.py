import asyncio
import os
import discord
from dotenv import load_dotenv

from module.check_Date import read_today_from_file
from module.weather_forecast import get_weather_forecast
from module.schedule_adjustment import schedule_adjustment
from module.generate_button import generate_button

from classes.my_bot import MyBot
from classes.shared_list_manager import SharedListManager
from classes.add_row_react_button import AddRowReactButton
from classes.add_role_button import AddRoleButton

current_dir = os.getcwd()
env_file_path = os.path.join(current_dir, ".env")
played_user_file_path = os.path.join(current_dir, "..", "data", "playedUser.json")

load_dotenv(env_file_path)

TOKEN = os.getenv('TOKEN')

TAROT_CHANNEL_ID = int(os.getenv("TAROT_CHANNEL_ID"))
OMIKUJI_CHANNEL_ID = int(os.getenv("OMIKUJI_CHANNEL_ID"))
IMAGE_SEARCH_CHANNEL_ID = int(os.getenv("IMAGE_SEARCH_CHANNEL_ID"))
SCHEDULE_CHANNEL_ID = int(os.getenv("SCHEDULE_CHANNEL_ID"))

ROLE_MANAGEMENT_MESSAGE_ID = int(os.getenv("ROLE_MANAGEMENT_MESSAGE_ID"))

# ボタンの生成
omikuji_button = None
tarot_button = None
color_manage_button = None
add_role_button = None


async def init():
    global omikuji_button, tarot_button, add_role_button
    # Button 必要な View を生成
    # おみくじ＆占いのボタン
    omikuji_button = await generate_button(
        label="くるったおみくじ", style=discord.ButtonStyle.success, custom_ids="omikuji2")
    tarot_button = await generate_button(
        label="タロット", style=discord.ButtonStyle.success, custom_ids="tarot")
    # 役職管理のボタン
    add_role_button = AddRoleButton()
    # ボタンのリアクションについてのイベントを登録
    await bot.add_cog(AddRowReactButton(bot=bot))

# 接続に必要なオブジェクトを生成
intents = discord.Intents.all()
intents.message_content = True
intents.members = True

# Botのインスタンス取得
bot = MyBot(command_prefix=['/'], intents=intents)


# 読み込むCogの名前を格納
INITIAL_EXTENSIONS = [
    'cogs.tarot',
    'cogs.omikuji',
    'cogs.utils',
]


async def load_extension():
    # Cogの読み込み
    for cog in INITIAL_EXTENSIONS:
        await bot.load_extension(cog)


@bot.event
async def on_ready():
    # おみくじ＆占いの結果を保存するファイルの読み込み
    SharedListManager.sharedList = read_today_from_file(file_path=played_user_file_path)

    # 天気予報の取得を開始
    await get_weather_forecast(bot)


# Botの起動とDiscordサーバーへの接続
async def main():
    async with bot:
        await init()
        await load_extension()
        await bot.start(TOKEN)


@bot.event
async def on_message(message):
    global omikuji_button, tarot_button

    # メッセージ送信者がBotだった場合は無視する
    if message.author.bot:
        return

    if message.channel.id == SCHEDULE_CHANNEL_ID:
        # メッセージ送信者が管理者の場合
        if message.content == "/date" and message.author.guild_permissions.administrator:
            # 日程調整チャンネル
            await schedule_adjustment(bot)

    elif message.channel.id == ROLE_MANAGEMENT_MESSAGE_ID:
        if message.content == "/role":
            pass

    # 画像検索チャンネルに反応
    elif message.channel.id == IMAGE_SEARCH_CHANNEL_ID:
        # 画像が送信されたとき
        if message.attachments:
            await bot.image_reverse_search(message, IMAGE_SEARCH_CHANNEL_ID)

    # おみくじチャンネルに反応
    elif message.channel.id == OMIKUJI_CHANNEL_ID:
        await bot.handle_command_button(OMIKUJI_CHANNEL_ID,
                                        omikuji_button, label='omikuji_id')

    # タロットチャンネルに反応
    elif message.channel.id == TAROT_CHANNEL_ID:
        await bot.handle_command_button(TAROT_CHANNEL_ID,  tarot_button, label='tarot_id')


@bot.event
async def on_interaction(inter: discord.Interaction):
    #! Botを再起動してしまうと、ボタンが押せなくなるので、再起動してもボタンが押せるようにする
    # * 参考  https://qiita.com/Kodai0417/items/18617b53ba629939e066
    try:
        if inter.data['component_type'] == 2:
            # ボタンを押したときの処理
            await on_button_click(inter)
    except Exception as e:
        print(e)


async def on_button_click(inter: discord.Interaction):
    global add_role_button

    # button を押したときの処理
    custom_id = inter.data["custom_id"]
    if custom_id == "image":
        await add_role_button.check_role("Image", inter.user, inter)
    elif custom_id == "weather":
        await add_role_button.check_role("Weather", inter.user, inter)
    elif custom_id == "archive":
        await add_role_button.check_role("Archive", inter.user, inter)
    elif custom_id == "omikuji2":
        await bot.invoke_command("omikuji2", inter)
        await bot.handle_command_button(OMIKUJI_CHANNEL_ID, omikuji_button, label='omikuji_id')
    elif custom_id == "tarot":
        await bot.invoke_command("tarot", inter)
        await bot.handle_command_button(TAROT_CHANNEL_ID, tarot_button, label='tarot_id')

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
