import json
from discord.ext import commands
import discord
import os
from dotenv import load_dotenv
from saucenao_api import SauceNao

current_dir = os.getcwd()
env_file_path = os.path.join(current_dir, "..", ".env")
data_file_path = os.path.join(current_dir, "..", "data", "message_id.json")

load_dotenv(env_file_path)
TAROT_CHANNEL_ID = int(os.getenv("TAROT_CHANNEL_ID"))
OMIKUJI_CHANNEL_ID = int(os.getenv("OMIKUJI_CHANNEL_ID"))

SAUCENAO_API_KEY = os.getenv("SAUCENAO_API_KEY")
IMAGE_SEARCH_CHANNEL_ID = int(os.getenv("IMAGE_SEARCH_CHANNEL_ID"))


class MyBot(commands.Bot):
    # Bot の初期化時に必要な引数を追加
    async def setup_hook(self):
        await self.tree.sync()

        for guild in self.guilds:
            await self.tree.sync(guild=guild)
        with open(data_file_path, "r") as f:
            self.message_id = json.load(f)

    async def invoke_command(self, command_name: str, interaction):
        try:
            member = interaction.user
            ctx = await self.get_context(interaction.message)
            ctx.author = member
            await self.get_command(command_name).invoke(ctx)
        except Exception as e:
            print(e)

    async def handle_command_button(self, channel_id: int, button, label: str):
        print("handle_command_button")
        # コマンドのボタンを押したときの処理
        # 常にチャンネルの下にボタンが表示されるようにする
        channel = self.get_channel(channel_id)
        try:
            message = await channel.fetch_message(self.message_id[label])
            await message.delete()
        except Exception as e:
            print("該当するメッセージが見つかりませんでした。")

        print("handle_command_button2")
        try:
            next_message = await channel.send(view=button)
            self.message_id[label] = next_message.id
            with open(data_file_path, "w") as f:
                json.dump(self.message_id, f, indent=4)
        except Exception as e:
            print(e)

    async def image_reverse_search(self, message, channel_id: int):
        channel = self.get_channel(channel_id)
        sauce = SauceNao(SAUCENAO_API_KEY)
        results = sauce.from_url(message.attachments[0].url)

        best_result = results[0] if results else None

        if best_result:
            thumbnailImage = best_result.thumbnail
            similarity = best_result.similarity
            title = best_result.title
            urls = best_result.urls if best_result.urls else results[1].urls
            author = best_result.author

            # embed の 定義を行う
            embed = discord.Embed(
                title="",
                description=f"### [{title}]({urls[0] if urls else '取得出来ませんでした。'})",
                color=0x0000ff
            )

            embed.set_thumbnail(url=thumbnailImage)
            embed.add_field(name="作者", value=f"{author}", inline=True)
            embed.add_field(name="類似度", value=f"{similarity}%", inline=True)

            for i, url in enumerate(urls[:3]):
                embed.add_field(name=f"URL{i+1}", value=f"{url}", inline=False)

            if similarity > 80:
                await channel.send(embed=embed)

            elif 80 >= similarity >= 40:
                embed.add_field(
                    name="この画像は", value="この画像は検索したものではない可能性があります！！", inline=False)
                embed.add_field(
                    name="手動で検索？？", value="以下の二次元画像に特化したサイトで検索することが出来ます。\n [二次元画像検索](https://ascii2d.net/)", inline=False)
                embed.color = 0xffa500
                await channel.send(embed=embed)
            else:
                await channel.send("類似度が低いため、検索結果が見つかりませんでした。")
