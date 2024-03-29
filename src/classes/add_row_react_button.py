import os
import discord
from discord.ext import commands
from classes.my_bot import MyBot

from dotenv import load_dotenv

current_dir = os.getcwd()
env_file_path = os.path.join(current_dir, "..", ".env")

load_dotenv(env_file_path)

BOT_USER_ID = int(os.getenv("BOT_USER_ID"))
ROLE_MANAGEMENT_MESSAGE_ID = int(os.getenv("ROLE_MANAGEMENT_MESSAGE_ID"))


class AddRowReactButton(discord.ext.commands.Cog):
    def __init__(self, bot: MyBot):
        self.bot = bot

    async def callback(self, interaction: discord.Interaction):
        member = interaction.user
        if self.role in member.roles:
            await member.remove_roles(self.role)
            await interaction.response.send_message(f'`{self.role.name}`の役職を削除しました。', ephemeral=True)
        else:
            await member.add_roles(self.role)
            await interaction.response.send_message(f'`{self.role.name}`の役職を付与しました。', ephemeral=True)

    # リアクションで役職付与
    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if payload.user_id != BOT_USER_ID:
            if payload.message_id == ROLE_MANAGEMENT_MESSAGE_ID:
                guild_id = payload.guild_id
                guild = discord.utils.find(
                    lambda g: g.id == guild_id, self.bot.guilds)

                role = discord.utils.find(
                    lambda r: r.name == payload.emoji.name, guild.roles)
                if role is not None:
                    member = discord.utils.find(
                        lambda m: m.id == payload.user_id, guild.members)
                    if member is not None:
                        await member.add_roles(role)
                    else:
                        print('Member not found')

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        # リアクションで役職削除
        if payload.user_id != BOT_USER_ID:
            if payload.message_id == ROLE_MANAGEMENT_MESSAGE_ID:
                guild_id = payload.guild_id
                guild = discord.utils.find(
                    lambda g: g.id == guild_id, self.bot.guilds)

                role = discord.utils.find(
                    lambda r: r.name == payload.emoji.name, guild.roles)
                if role is not None:
                    member = discord.utils.find(
                        lambda m: m.id == payload.user_id, guild.members)
                    if member is not None:
                        await member.remove_roles(role)
                    else:
                        print('Member not found')
