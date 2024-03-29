import discord


class AddRoleButton(discord.ui.View):
    # ロール付与の作成
    def __init__(self):
        super().__init__()

    # 指定のチャンネルにボタンが送信されているかをチェックする

    async def check_button(self, channel: discord.TextChannel):
        # ボタンが送信されているかをチェック
        async for message in channel.history(limit=10):
            if message.author == self.bot.user and message.content == "役職管理":
                return True
        return False

    #  ↓作成するボタン群
    @discord.ui.button(label="画像検索", style=discord.ButtonStyle.success, row=0, custom_id="image")
    async def add_image_role_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        pass

    @discord.ui.button(label="天気予報", style=discord.ButtonStyle.success, row=0, custom_id="weather")
    async def add_weather_role_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        pass

    @discord.ui.button(label="アーカイブ", style=discord.ButtonStyle.success, row=0, custom_id="archive")
    async def add_archive_role_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        pass
