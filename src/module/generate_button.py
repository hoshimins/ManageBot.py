import discord


async def generate_button(label: str, style: discord.ButtonStyle, custom_ids: str):
    button = discord.ui.View()
    button.add_item(discord.ui.Button(
        label=label, style=style, custom_id=custom_ids))
    return button
