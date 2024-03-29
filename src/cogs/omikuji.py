import discord
from discord.ext import commands
import random
from dotenv import load_dotenv
import os
import json
from module.check_Date import get_today, write_today_to_file
from classes.shared_list_manager import SharedListManager

current_dir = os.getcwd()
env_file_path = os.path.join(current_dir, "..",  ".env")
data_file_path = os.path.join(current_dir, "..", "data", "omikuji.json")
result_file_path = os.path.join(current_dir, "..", "data", "omikujiResult.json")
played_user_file_path = os.path.join(current_dir, "..", "data", "playedUser.json")

load_dotenv(env_file_path)


class Omikuji(commands.Cog):

    # 初期化
    def __init__(self, bot):
        super().__init__()
        self.bot = bot
        self.OMIKUJI_CHANNEL_ID: int = int(os.getenv('OMIKUJI_CHANNEL_ID'))
        self.PERSONAL_GENERAL_CHANNEL_ID: int = int(
            os.getenv('PERSONAL_GENERAL_CHANNEL_ID'))
        self.OMIKUJI_CHANNEL_ID_TUPLE: tuple = (
            self.OMIKUJI_CHANNEL_ID, self.PERSONAL_GENERAL_CHANNEL_ID)
        self.SOLO_GUILD_ID: int = int(os.getenv("SOLO_GUILD_ID"))
        self.YOUKAN_GUILD_ID: int = int(os.getenv("YOUKAN_GUILD_ID"))

        #  おみくじ結果ファイルの読み込み
        self.omikuji_result_dict: dict[str, str] = self.read_dict_from_file(file_path=result_file_path)

    def read_dict_from_file(self, file_path):
        """おみくじ結果ファイルからの読み込み"""
        try:
            with open(file_path, encoding='utf-8') as file:
                omikuji_result_dict: dict[str, str] = json.load(file)
                return omikuji_result_dict
        except Exception as e:
            print("ファイルの読み込み中にエラーが発生しました:", str(e))
            return None

    def write_dict_to_file(self, file_path, data_dict):
        """おみくじ結果ファイルへの書き込み"""
        try:
            with open(file_path, 'w', encoding="utf-8") as file:
                json.dump(data_dict, file, ensure_ascii=False, indent=4)
            print("リストがファイルに書き込まれました。")
        except Exception as e:
            print("ファイルへの書き込み中にエラーが発生しました:", str(e))

    @commands.Cog.listener()
    async def on_ready(self):
        await self.bot.tree.sync(guild=discord.Object(self.SOLO_GUILD_ID))
        await self.bot.tree.sync(guild=discord.Object(self.YOUKAN_GUILD_ID))
        print("omikujiのコマンド登録完了")

    # おみくじ

    @commands.hybrid_command(name="omikuji", description="普通のおみくじが引けるよ！！\nおみくじの結果は大吉、中吉、小吉、吉、凶、大凶の6種類です。\nそれぞれの確率は、大吉が10%、中吉が15%、小吉が15%、吉が30%、凶が20%、大凶が10%です。")
    async def omikuji(self, ctx: commands.Context):
        """普通のおみくじが引けるよ！！"""

        # おみくじを行えるチャンネルかどうか
        if ctx.channel.id not in self.OMIKUJI_CHANNEL_ID_TUPLE:
            await ctx.send(f"このチャンネルではおみくじを行えません。")
            return

        # おみくじを行ったユーザーかどうか
        if SharedListManager.sharedList[f"{ctx.author.id}"]["omikujiDate"] == get_today():
            print(
                SharedListManager.sharedList[f"{ctx.author.id}"]["omikujiDate"])
            await ctx.send(f"{ctx.author.mention}さんは既におみくじを行っています。")
            return

        # 抽選
        OMIKUJI: list[str] = ["大吉", "中吉", "小吉", "吉", "凶", "大凶"]
        probabilities: list[float] = [0.1, 0.15, 0.15, 0.3, 0.2, 0.1]
        omikuji_result: str = random.choices(OMIKUJI, probabilities)[0]

        # 記録を取得
        # 前回までの回数
        prev = self.omikuji_result_dict[ctx.author.id][omikuji_result]["Normal"]
        # 結果を記録
        self.omikuji_result_dict[str(
            ctx.author.id)][omikuji_result]["Normal"] = prev + 1

        # 結果に出力文字列作成
        title: str = f"## おみくじ結果 \n\n"
        desc = f"{ctx.author.mention}の今日のおみくじ結果は...\n\n"
        desc += f"## {omikuji_result}です！\n\n"
        desc += f"いままで{ctx.author.display_name}は、普通のおみくじで {omikuji_result} を {prev+1} 回出しました！！\n\n"

        if omikuji_result == "大吉":
            desc += f"おめでとうございます！！"
            color = 0xf1c40f

        embed = discord.Embed(title=title, description=desc, color=color)

        # 送信
        await ctx.send(embed=embed)

        # おみくじを行った日付を記録
        SharedListManager.sharedList[f"{ctx.author.id}"]["omikujiDate"] = get_today(
        )
        write_today_to_file(played_user_file_path,SharedListManager.sharedList)

        # 結果を記録
        self.omikuji_result_dict[str(
            ctx.author.id)][omikuji_result]["Normal"] = prev + 1
        self.write_dict_to_file(self.omikuji_result_dict,result_file_path)

    # くるったおみくじ
    @commands.hybrid_command(name="omikuji2", description="くるったおみくじが引けるよ！！\nおみくじの結果は大吉、大凶の2種類です。\nそれぞれの確率は、大吉が1%、大凶が99%です。")
    async def omikuji2(self, ctx: commands.Context):
        """くるったおみくじが引けるよ！！"""

        # おみくじを行えるチャンネルかどうか
        if ctx.channel.id not in self.OMIKUJI_CHANNEL_ID_TUPLE:
            await ctx.send(f"このチャンネルではおみくじを行えません。")
            return

        # おみくじを行ったユーザーかどうか
        if SharedListManager.sharedList[f"{ctx.author.id}"]["omikujiDate"] == get_today():
            print(
                SharedListManager.sharedList[f"{ctx.author.id}"]["omikujiDate"])
            await ctx.send(f"{ctx.author.mention}さんは既におみくじを行っています。")
            return

        # 抽選
        OMIKUJI: list[str] = ["大吉", "大凶"]
        probabilities: list[float] = [0.01, 0.99]
        omikuji_result: str = random.choices(OMIKUJI, probabilities)[0]

        # 記録を取得
        # 前回までの回数
        prev = self.omikuji_result_dict[str(
            ctx.author.id)][omikuji_result]["Crazy"]

        # 結果に出力文字列作成
        title: str = f"おみくじ結果 \n\n"
        desc = f"{ctx.author.mention}の今日のおみくじ結果は...\n\n"
        desc += f"## {omikuji_result}です！\n\n"
        desc += f"いままで{ctx.author.display_name}は、くるったおみくじで {omikuji_result} を {prev+1} 回出しました！！\n\n"
        color = 0x3498db

        if omikuji_result == "大吉":
            desc += f"おめでとうございます！！"
            color = 0xf1c40f

        embed = discord.Embed(title=title, description=desc, color=color)

        # 送信
        await ctx.send(embed=embed)

        # おみくじを行った日付を記録
        SharedListManager.sharedList[f"{ctx.author.id}"]["omikujiDate"] = get_today(
        )
        write_today_to_file(played_user_file_path,SharedListManager.sharedList)

        # 結果を記録
        self.omikuji_result_dict[str(
            ctx.author.id)][omikuji_result]["Crazy"] = prev + 1
        self.write_dict_to_file(result_file_path, self.omikuji_result_dict)

    @commands.hybrid_command(name="omikuji-stats", description="今まで引いてきたおみくじの戦績を表示するよ！！")
    async def omikuji_stats(self, ctx: commands.Context):
        "今まで引いてきたおみくじの戦績を表示するよ！！"
        if ctx.channel.id not in self.OMIKUJI_CHANNEL_ID_TUPLE:
            await ctx.send(f"このチャンネルではこのコマンドを行えません。")
            return

        message: str = f"{ctx.author.mention}の今までおみくじ成績を表示します。\n"
        message += f"## 通常のおみくじ\n"
        message += f"大吉：{self.omikuji_result_dict[str(ctx.author.id)]['大吉']['Normal']} 回\n"
        message += f"中吉：{self.omikuji_result_dict[str(ctx.author.id)]['中吉']['Normal']} 回\n"
        message += f"小吉：{self.omikuji_result_dict[str(ctx.author.id)]['小吉']['Normal']}  回\n"
        message += f"  吉：{self.omikuji_result_dict[str(ctx.author.id)]['吉']['Normal']} 回\n"
        message += f"  凶：{self.omikuji_result_dict[str(ctx.author.id)]['凶']['Normal']} 回\n"
        message += f"大凶：{self.omikuji_result_dict[str(ctx.author.id)]['大凶']['Normal']} 回\n"

        message += f"## 狂ったおみくじ\n"
        message += f"大吉：{self.omikuji_result_dict[str(ctx.author.id)]['大吉']['Crazy']} 回\n"
        message += f"大凶：{self.omikuji_result_dict[str(ctx.author.id)]['大凶']['Crazy']} 回\n"

        await ctx.send(message)


# コマンドを登録する
async def setup(bot: commands.Bot):
    await bot.add_cog(Omikuji(bot))
