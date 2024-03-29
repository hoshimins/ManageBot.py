import discord
from discord.ext import commands
from dotenv import load_dotenv
import os

current_dir = os.getcwd()
env_file_path = os.path.join(current_dir, "..",  ".env")

load_dotenv(env_file_path)


class Utils(commands.Cog):

    # 初期化
    def __init__(self, bot):
        super().__init__()
        self.bot = bot
        self.OMIKUJI_CHANNEL_ID: int = int(os.getenv('OMIKUJI_CHANNEL_ID'))
        self.PERSONAL_GENERAL_CHANNEL_ID: int = int(
            os.getenv('PERSONAL_GENERAL_CHANNEL_ID'))
        self.OMIKUJI_CHANNEL_ID_TUPLE: tuple = (
            self.OMIKUJI_CHANNEL_ID, self.PERSONAL_GENERAL_CHANNEL_ID)
        self.ADMIN_NAME: str = os.getenv('ADMIN_NAME')
        self.SOLO_GUILD_ID: int = int(os.getenv("SOLO_GUILD_ID"))
        self.YOUKAN_GUILD_ID: int = int(os.getenv("YOUKAN_GUILD_ID"))

    @commands.Cog.listener()
    async def on_ready(self):
        await self.bot.tree.sync(guild=discord.Object(self.SOLO_GUILD_ID))
        await self.bot.tree.sync(guild=discord.Object(self.YOUKAN_GUILD_ID))
        print("Utilのコマンド登録完了")

    @commands.hybrid_command(name="cls", description="チャンネルのメッセージを削除するよ!!",)
    async def cls(self, ctx: commands.Context):
        """チャンネルのメッセージを削除するよ!!"""
        if str(ctx.author) == self.ADMIN_NAME:
            await ctx.channel.send("メッセージを削除します。")
            await ctx.channel.purge()

    @commands.hybrid_command(name="create-txtch", description="Textチャンネルを作成するよ!!", )
    async def createTextCh(self, ctx: commands.Context, text: str = "チャンネル名"):
        """テキストチャンネルを作成するよ!!"""
        await ctx.guild.create_text_channel(f"📔｜{text}")
        await ctx.send(f"{text}テキストチャンネルを作成しました。")

    @commands.hybrid_command(name="create-vcch", description="Voiceチャンネルを作成するよ!!", )
    async def createVcCh(self, ctx: commands.Context, text: str = "チャンネル名"):
        """ボイスチャンネルを作成するよ!!"""
        await ctx.guild.create_voice_channel(f"📔｜{text}")
        await ctx.send(f"{text}ボイスチャンネルを作成しました。")

    @commands.hybrid_command(name="create-category", description="カテゴリーを作成するよ!!", )
    async def createCategory(self, ctx: commands.Context, text: str = "チャンネル名"):
        """ボイスチャンネルを作成するよ!!"""
        await ctx.guild.create_category(f"📔｜{text}")
        await ctx.send(f"{text}カテゴリを作成しました。")


# コマンドを登録する
async def setup(bot: commands.Bot):
    await bot.add_cog(Utils(bot))
