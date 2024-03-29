import discord
from discord.ext import commands
import json
import random
import os
from dotenv import load_dotenv
from module.check_Date import get_today, write_today_to_file
from classes.shared_list_manager import SharedListManager


current_dir = os.getcwd()
env_file_path = os.path.join(current_dir, "..",  ".env")
data_file_path = os.path.join(current_dir, "..", "data", "tarot.json")
played_user_file_path = os.path.join(current_dir, "..", "data", "playedUser.json")

load_dotenv(env_file_path)
# JSONファイルを読み込む
with open(data_file_path, encoding="utf-8") as tarot_json_open:
    tarot_data: dict[str, str] = json.load(tarot_json_open)

# タロットのデータ定義
arcana: list[str] = ['Big', 'Small', 'Small', 'Small']
tarot_big_key: list[str] = list(tarot_data['Big'].keys())
tarot_small_key: list[str] = list(tarot_data['Small'].keys())
tarot_number: list[str] = list(tarot_data['Small'][tarot_small_key[0]].keys())
direction: list[str] = ['Upright', 'Reverse']


class Tarot(commands.Cog):

    # 初期化
    def __init__(self, bot):
        super().__init__()
        self.bot = bot
        self.TAROT_CHANNEL_ID: int = int(os.getenv('TAROT_CHANNEL_ID'))
        self.PERSONAL_GENERAL_CHANNEL_ID: int = int(
            os.getenv('PERSONAL_GENERAL_CHANNEL_ID'))
        self.TAROT_CHANNEL_ID_TUPLE: tuple = (
            self.TAROT_CHANNEL_ID, self.PERSONAL_GENERAL_CHANNEL_ID)
        self.SOLO_GUILD_ID: int = int(os.getenv('SOLO_GUILD_ID'))
        self.YOUKAN_GUILD_ID: int = int(os.getenv('YOUKAN_GUILD_ID'))

    @commands.Cog.listener()
    async def on_ready(self):
        await self.bot.tree.sync(guild=discord.Object(self.SOLO_GUILD_ID))
        await self.bot.tree.sync(guild=discord.Object(self.YOUKAN_GUILD_ID))
        print("tarotのコマンド登録完了")

    @commands.hybrid_command(name="tarot", description="タロットが引けるよ！\nタロットの結果は、大アルカナの22枚のカードと小アルカナの56枚のカードの合計78枚のカードから引かれます。")
    async def tarot(self, ctx: commands.Context):
        """タロットが引けるよ！！"""
        if ctx.channel.id not in self.TAROT_CHANNEL_ID_TUPLE:
            await ctx.send(f"このチャンネルではタロットを行えません。")
            return

        if SharedListManager.sharedList[f"{ctx.author.id}"]["tarotDate"] == get_today():
            await ctx.send(f"{ctx.author.mention}さんは既にタロットを行っています。")
            return

        is_arcana_big: str = random.choice(arcana)
        is_arcana_direction: str = random.choice(direction)
        message_content: str = f"{ctx.author.mention}の今日のカードは...\n\n"

        if is_arcana_big == 'Big':
            keys: int = random.randint(0, 21)
            tarot_result: str = tarot_data[is_arcana_big][tarot_big_key[keys]]
            card_name: str = tarot_result[is_arcana_direction]['name']
            card_meaning: str = tarot_result[is_arcana_direction]['meaning']
            card_image: str = tarot_result[is_arcana_direction]['imagePath']

            message_content += f"## 大アルカナ {card_name}\n\n"
            message_content += f"### カードの意味:\n{card_meaning}\n\n"
            message_content += f"### 画像:\n"

        elif is_arcana_big == 'Small':
            suits: int = random.randint(0, 3)
            numbers: int = random.randint(0, 13)
            tarot_result: str = tarot_data[is_arcana_big][tarot_small_key[suits]
                                                          ][tarot_number[numbers]]
            card_name: str = tarot_result[is_arcana_direction]['name']
            card_meaning: str = tarot_result[is_arcana_direction]['meaning']
            card_image: str = tarot_result[is_arcana_direction]['imagePath']

            message_content += f"## 小アルカナ {card_name}\n\n"
            message_content += f"### カードの意味:\n{card_meaning}\n\n"
            message_content += f"### 画像:\n"

        # 送信
        await ctx.send(message_content, file=discord.File(card_image))

        # おみくじを行った日付を記録
        SharedListManager.sharedList[f"{ctx.author.id}"]["tarotDate"] = get_today()
        write_today_to_file(played_user_file_path,SharedListManager.sharedList)


async def setup(bot: commands.Bot):
    await bot.add_cog(Tarot(bot))
