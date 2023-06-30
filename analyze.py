import sys
import datetime

# データを読み込む
with open(sys.argv[1], "r", encoding="utf-8") as f:
    data = f.readlines()

# タイトルごとの時間を格納する辞書を初期化
time_dict = {}

for line in data:
    # 各行を分割
    start, end, time, title = line.strip().split(',')

    # 時間を時と分に分割
    hours, minutes, seconds = map(int, time.split(':'))

    # 時間を分に変換
    total_minutes = hours * 60 + minutes

    # タイトルが辞書に存在する場合、時間を追加
    if title in time_dict:
        time_dict[title] += total_minutes
    else:  # タイトルが辞書に存在しない場合、新しいエントリを作成
        time_dict[title] = total_minutes

with open(sys.argv[2], "w", encoding="utf-8") as f:
    # タイトルごとの合計時間を表示
    for title, time in time_dict.items():
        f.write(f"{time}m {title}\n")

    sum = sum(time for time in time_dict.values())
    f.write(f"sum {sum}m = {sum/60}h\n")
