from dateutil.rrule import rrule, DAILY
from dateutil.relativedelta import relativedelta
from datetime import datetime
import locale
import os
import discord

from classes.my_bot import MyBot

from dotenv import load_dotenv


current_dir = os.getcwd()
env_file_path = os.path.join(current_dir, ".env")

load_dotenv(env_file_path)

SCHEDULE_CHANNEL_ID = int(os.getenv('SCHEDULE_CHANNEL_ID'))

# 手動で祝日を設定
holidays = {
    "2024-01-01": "元日",
    "2024-01-08": "成人の日",
    "2024-02-11": "建国記念の日",
    "2024-02-12": "振替休日",
    "2024-02-23": "天皇誕生日",
    "2024-03-20": "春分の日",
    "2024-04-29": "昭和の日",
    "2024-05-03": "憲法記念日",
    "2024-05-04": "みどりの日",
    "2024-05-05": "こどもの日",
    "2024-07-15": "海の日",
    "2024-08-11": "山の日",
    "2024-08-12": "振替休日",
    "2024-09-16": "敬老の日",
    "2024-09-22": "秋分の日",
    "2024-09-23": "振替休日",
    "2024-10-14": "スポーツの日",
    "2024-11-03": "文化の日",
    "2024-11-04": "振替休日",
    "2024-11-23": "勤労感謝の日",
}


async def schedule_adjustment(bot: MyBot):
    try:
        # 送信チャンネルの設定
        channel = bot.get_channel(SCHEDULE_CHANNEL_ID)

        # 今日の日付
        today = datetime.now().today()

        # 来月の月を取得
        next_month = today + relativedelta(months=1)

        # 指定した月の初日
        start_date = next_month.replace(day=1)

        # 次の月の初日
        end_date = (start_date + relativedelta(months=1)).replace(day=1)

        # 月初から月末までの日付を生成
        dates_in_month = list(
            rrule(DAILY, dtstart=start_date, until=end_date))

        # 月初から月末までの土曜日と日曜日を抽出
        weekend_dates = [d.strftime('%Y-%m-%d')
                         for d in dates_in_month if d.weekday() in [5, 6]]

        # 月初から月末までの祝日を抽出
        holiday_dates = [d.strftime(
            '%Y-%m-%d') for d in dates_in_month if d.strftime('%Y-%m-%d') in holidays]

        # まとめる
        combined_list = weekend_dates + holiday_dates
        result_list = sorted(list(set(combined_list)))

        embed = discord.Embed(
            title=f"日程調整 {format(next_month.month)}月",
            description="都合がつく日程の番号をリアクションで選択してください。\n",
            color=0x6a5acd
        )
        locale.setlocale(locale.LC_TIME, 'ja_JP.UTF-8')
        for i, date in enumerate(result_list):
            date_obj = datetime.strptime(date, "%Y-%m-%d")
            day_of_week = date_obj.strftime('%A')
            formatted_date = date_obj.strftime('%m月 %d日')
            embed.description += f"### {i}\N{COMBINING ENCLOSING KEYCAP} : {formatted_date}       ({day_of_week[0]})  \n"

        message = await channel.send(embed=embed)

        for i in range(len(result_list)):
            await message.add_reaction(f"{i}\N{COMBINING ENCLOSING KEYCAP}")
    except Exception as e:
        print(e)
        return
