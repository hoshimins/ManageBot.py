import datetime
import json

def get_today():
    """今日の日付を取得"""
    today = datetime.date.today()
    return today.strftime("%Y/%m/%d")

def write_today_to_file(file_path, data):
    """日付をファイルへ書き込み"""
    try:
        with open(file_path, 'w', encoding="utf-8") as file:
              json.dump(data, file, ensure_ascii=False, indent=4)
        print("日付がファイルに書き込まれました。")
    except Exception as e:
        print("ファイルへの書き込み中にエラーが発生しました:", str(e))

def read_today_from_file(file_path):
    """日付をファイルから読み込み"""
    try:
        with open(file_path, encoding='utf-8') as file:
            file = json.load(file)
            return file
    except Exception as e:
        print("ファイルの読み込み中にエラーが発生しました:", str(e))
        return None
