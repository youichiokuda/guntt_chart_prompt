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
from io import StringIO

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

def is_json_like(text):
    return bool(re.match(r'^[\s]*[\[{]', text.strip()))

# ✅ ガントチャート描画関数
def plot_gantt(df, title):
    df = df.sort_values("start", ascending=False)
    fig, ax = plt.subplots(figsize=(12, 6))

    for i, row in df.iterrows():
        ax.barh(
            row['task'],
            (row['end'] - row['start']).days,
            left=row['start'],
            height=row.get('height', 0.4),
            color=row.get('color', 'skyblue'),
            edgecolor='black'
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

# ✅ ChatGPTからJSON形式のタスクデータを抽出
def extract_tasks_from_text(text, api_key, prompt):
    client = OpenAI(api_key=api_key)

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": text}
        ],
        temperature=0.3
    )
    return response.choices[0].message.content.strip()

# ✅ JSONからDataFrame変換
def parse_json_to_df(json_text):
    try:
        tasks = json.loads(json_text)
        for task in tasks:
            task["start"] = datetime.datetime.strptime(task["start"], "%Y-%m-%d")
            task["end"] = datetime.datetime.strptime(task["end"], "%Y-%m-%d")
        return pd.DataFrame(tasks)
    except Exception as e:
        st.error(f"JSONパースエラー: {e}")
        return pd.DataFrame()

# ✅ Streamlit UI
st.title("📊 ガントチャート生成アプリ")

text = st.text_area("📋 入力テキスト または JSON：", height=300)
api_key = st.text_input("🔑 OpenAI APIキー", type="password")
style_prompt = st.text_area("🎨 スタイル指定プロンプト（任意）", height=100)

if st.button("🚀 ChatGPTで解析してガントチャート生成"):
    with st.spinner("ChatGPTで解析中..."):
        if is_json_like(text):
            json_text = text
        else:
            json_text = extract_tasks_from_text(text, api_key, style_prompt)

        df = parse_json_to_df(json_text)

        if not df.empty:
            st.success("✅ ガントチャートを生成しました")
            plot_gantt(df, "プロジェクトスケジュール")
        else:
            st.error("❌ データがありませんでした")
