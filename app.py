import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import json
import os
import re
import matplotlib.font_manager as fm
from openai import OpenAI

# ✅ システム内にある日本語フォント候補を探索
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

# ✅ JSON形式の入力か判定
def is_json_like(text):
    return bool(re.match(r'^[\s]*[\[{]', text.strip()))

# ✅ JSON文字列 → DataFrame
def json_to_df(json_text):
    try:
        tasks = json.loads(json_text)
        for task in tasks:
            task["start"] = pd.to_datetime(task["start"])
            task["end"] = pd.to_datetime(task["end"])
        return pd.DataFrame(tasks)
    except Exception as e:
        st.error(f"❌ JSON形式の読み込みでエラーが発生しました: {e}")
        return pd.DataFrame()

# ✅ Ganttチャート描画
def draw_gantt_chart(df):
    if not all(col in df.columns for col in ["task", "start", "end"]):
        st.error("❌ 必要なカラム（task, start, end）が不足しています。JSONフォーマットを確認してください。")
        return

    fig, ax = plt.subplots(figsize=(10, 2 + 0.5 * len(df)))
    for i, row in df.iterrows():
        color = row.get("color", "skyblue")
        try:
            plt.ColorConverter().to_rgba(color)
        except ValueError:
            color = "skyblue"

        ax.barh(
            y=row["task"],
            width=(row["end"] - row["start"]).days,
            left=row["start"],
            height=row.get("height", 0.4),
            color=color,
            edgecolor="black"
        )
        ax.text(
            row["start"], i,
            f"{row['start'].strftime('%m/%d')} - {row['end'].strftime('%m/%d')}",
            va='center', ha='left', fontsize=8
        )

    ax.set_xlabel("日付")
    ax.set_ylabel("タスク")
    plt.tight_layout()
    st.pyplot(fig)

# ✅ ChatGPTでプロンプトを解析しJSON生成
def extract_tasks_from_text(text, api_key, style_instruction=""):
    client = OpenAI(api_key=api_key)
    prompt = f"""
あなたはプロジェクト管理の専門家です。
以下の文章からタスク名、開始日、終了日を抽出して、JSON形式で出力してください。

出力形式は以下の通りです：
[
  {{
    "task": "タスク名",
    "start": "YYYY-MM-DD",
    "end": "YYYY-MM-DD",
    "color": "blue",
    "height": 0.4
  }},
  ...
]

スタイルに関する指示:
{style_instruction}

対象文章:
{text}
"""

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "あなたはプロジェクトマネージャーです。"},
            {"role": "user", "content": prompt}
        ],
        temperature=0.3
    )

    return response.choices[0].message.content.strip()

# ✅ Streamlitアプリ本体
st.title("🗂️ ガントチャート自動生成")

api_key = st.text_input("🔑 OpenAI APIキー", type="password")

text = st.text_area("📄 タスク説明（またはJSON形式）を入力", height=250)

style_prompt = st.text_input("🎨 スタイル指定（例：キックオフは緑で、稼働は太く）", "")

if st.button("🚀 ChatGPTで解析してガントチャート生成"):
    if not api_key:
        st.error("🔑 OpenAI APIキーを入力してください。")
    else:
        with st.spinner("ChatGPTで解析中..."):
            if is_json_like(text):
                df = json_to_df(text)
            else:
                json_text = extract_tasks_from_text(text, api_key, style_prompt)
                df = json_to_df(json_text)

        if not df.empty:
            draw_gantt_chart(df)
