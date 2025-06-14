import os
import re
import json
import datetime
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.font_manager as fm
import streamlit as st
from openai import OpenAI

# ✅ 日本語フォント設定
font_candidates = [
    "/usr/share/fonts/opentype/ipafont-gothic/ipagp.ttf",
    "/usr/share/fonts/truetype/takao-gothic/TakaoPGothic.ttf",
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
]
for font_path in font_candidates:
    if os.path.exists(font_path):
        font_prop = fm.FontProperties(fname=font_path)
        plt.rcParams["font.family"] = font_prop.get_name()
        break
else:
    plt.rcParams["font.family"] = "sans-serif"

# ✅ JSON形式チェック関数
def is_json_like(text):
    return bool(re.match(r'^[\s]*[\[{]', text.strip()))

# ✅ ガントチャート描画
def plot_gantt(df, title):
    df = df.sort_values("start", ascending=False)
    fig, ax = plt.subplots(figsize=(12, 6))
    for i, row in df.iterrows():
        ax.barh(
            row['task'],
            (row['end'] - row['start']).days,
            left=row['start'],
            height=0.5,
            color=row.get('color', 'skyblue'),
            edgecolor="black"
        )

    ax.xaxis.set_major_locator(mdates.MonthLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
    ax.xaxis.tick_top()
    ax.xaxis.set_label_position('top')
    plt.xticks(rotation=45)
    ax.grid(True, axis='both', linestyle='--', alpha=0.5)
    plt.title(title, y=1.1)
    plt.tight_layout()
    st.pyplot(fig)

# ✅ ChatGPT から JSON を抽出
def extract_tasks_from_text(text, api_key, style_prompt="あなたはプロジェクトマネージャーです。以下の文章からガントチャート用のJSONを生成してください。"):
    client = OpenAI(api_key=api_key)
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": style_prompt},
            {"role": "user", "content": text}
        ],
        temperature=0.3
    )
    reply = response.choices[0].message.content.strip()
    match = re.search(r'\[.*\]', reply, re.DOTALL)
    if match:
        return match.group(0)
    elif is_json_like(reply):
        return reply
    else:
        raise ValueError("ChatGPTが有効なJSONを返しませんでした。")

# ✅ Streamlit UI
st.title("🗓️ ガントチャート自動生成アプリ")
text = st.text_area("プロジェクトスケジュールを日本語で入力してください：", height=250)
api_key = st.text_input("🔑 OpenAI APIキー", type="password")
style_prompt = st.text_area("🎯 出力スタイルプロンプト（任意）", value="あなたはプロジェクトマネージャーです。以下の文章からガントチャート用のJSONを生成してください。", height=100)

if st.button("✅ ガントチャート生成"):
    if not api_key or not text:
        st.warning("APIキーと文章の両方を入力してください。")
    else:
        try:
            json_text = extract_tasks_from_text(text, api_key, style_prompt)
            tasks = json.loads(json_text)
            for t in tasks:
                t["start"] = datetime.datetime.strptime(t["start"], "%Y-%m-%d")
                t["end"] = datetime.datetime.strptime(t["end"], "%Y-%m-%d")
            df = pd.DataFrame(tasks)
            plot_gantt(df, "プロジェクトスケジュール")
        except Exception as e:
            st.error(f"エラー: {e}")
