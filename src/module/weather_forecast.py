import requests
import os
import asyncio
import discord
from datetime import datetime, timedelta
from dotenv import load_dotenv

from classes.my_bot import MyBot


current_dir = os.getcwd()
env_file_path = os.path.join(current_dir, ".env")

load_dotenv(env_file_path)
FORECAST_CHANNEL_ID = int(os.getenv("FORECAST_CHANNEL_ID"))


# 天気予報を取得する時間
today_target_time = "05:00:00"
tomorrow_target_time = "18:00:00"

#! TODO 変更する
pref_code_lists = [
    110010,
    140010,
    200020,
]

color_codes = [
    0xB1063A,
    0x00ff00,
    0x00FF7F,
]


# 曜日の変換を行う
def get_weekday(gap_day):
    # 今日を基準としてgap_day日後の曜日を取得
    if gap_day == 0:
        day, month = datetime.now().day, datetime.now().month
        weekdayNum = datetime.now().weekday()
    else:
        weekdayNum = (datetime.now() + timedelta(days=gap_day)).weekday()
        day, month = (datetime.now() + timedelta(days=gap_day)
                      ).day, (datetime.now() + timedelta(days=gap_day)).month

    if weekdayNum == 0:
        weekday = "月曜日"
    elif weekdayNum == 1:
        weekday = "火曜日"
    elif weekdayNum == 2:
        weekday = "水曜日"
    elif weekdayNum == 3:
        weekday = "木曜日"
    elif weekdayNum == 4:
        weekday = "金曜日"
    elif weekdayNum == 5:
        weekday = "土曜日"
    elif weekdayNum == 6:
        weekday = "日曜日"

    return weekday, day, month


# 毎日の天気予報
async def get_weather_forecast(bot: MyBot):
    try:
        # 時間の取得
        while True:
            currnet_time = datetime.now().strftime("%H:%M:%S")
            # チャンネルIDの指定
            channel = bot.get_channel(FORECAST_CHANNEL_ID)

            if currnet_time == today_target_time:
                # チャンネル内のメッセージを削除
                await channel.purge()

                weekday, day, month = get_weekday(0)

                # 今日の日付を送信する
                await channel.send(f"## 今日は{month}月{day}日 {weekday}です。")

                for i in range(len(pref_code_lists)):
                    url = f'https://weather.tsukumijima.net/api/forecast?city={pref_code_lists[i]}'

                    response = requests.get(url)
                    if response.status_code == 200:
                        data = response.json()
                        # embed の 定義を行う
                        embed = discord.Embed(
                            title=f"{data['title']}",
                            description=f"## {data['forecasts'][0]['telop']} \n",
                            color=color_codes[i]
                        )
                        embed.set_thumbnail(
                            url=data['forecasts'][0]['image']['url'])
                        embed.add_field(
                            name="詳細", value=data['forecasts'][0]['detail']['weather'], inline=False)
                        c = "℃"
                        not_temperature = "取得出来ませんでした。"
                        embed.add_field(
                            name="最高気温", value=f"{data['forecasts'][0]['temperature']['max']['celsius'] if data['forecasts'][0]['temperature']['max']['celsius'] else not_temperature}", inline=False)

                        # embed を送信する
                        await channel.send(embed=embed)
                    else:
                        print('Error: ', response.status_code)

            if currnet_time == tomorrow_target_time:
                # チャンネル内のメッセージを削除
                await channel.purge()

                weekday, day, month = get_weekday(1)

                # 明日の日付を送信する
                await channel.send(f"## 明日{month}月{day}日 {weekday}の天気予報です。")

                for i in range(len(pref_code_lists)):
                    url = f'https://weather.tsukumijima.net/api/forecast?city={pref_code_lists[i]}'

                    response = requests.get(url)
                    if response.status_code == 200:
                        data = response.json()
                        # embed の 定義を行う
                        embed = discord.Embed(
                            title=f"{data['title']}",
                            description=f"## {data['forecasts'][1]['telop']} \n",
                            color=color_codes[i]
                        )
                        embed.set_thumbnail(
                            url=data['forecasts'][1]['image']['url'])
                        embed.add_field(
                            name="詳細", value=data['forecasts'][1]['detail']['weather'], inline=False)
                        c = "℃"
                        not_temperature = "取得出来ませんでした。"
                        embed.add_field(
                            name="最高気温", value=f"{data['forecasts'][1]['temperature']['max']['celsius']  if data['forecasts'][1]['temperature']['max']['celsius'] else not_temperature}", inline=False)
                        embed.add_field(
                            name="最低気温", value=f"{data['forecasts'][1]['temperature']['min']['celsius']  if data['forecasts'][1]['temperature']['max']['celsius'] else not_temperature}", inline=False)

                        # embed を送信する
                        await channel.send(embed=embed)
                    else:
                        print('Error: ', response.status_code)

            await asyncio.sleep(1)
    except Exception as e:
        print(e)
        pass
