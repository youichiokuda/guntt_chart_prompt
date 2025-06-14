import os
import re
import json
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import pandas as pd
import streamlit as st
from datetime import datetime
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

# ✅ JSONっぽい形式かを判定
def is_json_like(text):
    return bool(re.match(r'^[\s]*[\[{]', text.strip()))

# ✅ ChatGPT出力からJSONだけを抽出する
def extract_json_string(text):
    match = re.search(r'(\[.*?\]|\{.*?\})', text, re.DOTALL)
    return match.group(1) if match else None

# ✅ JSONからDataFrameへ変換
def json_to_df(json_text):
    try:
        tasks = json.loads(json_text)
        df = pd.DataFrame(tasks)
        df["start"] = pd.to_datetime(df["start"])
        df["end"] = pd.to_datetime(df["end"])
        return df
    except Exception as e:
        st.error(f"JSONパースエラー: {e}")
        return pd.DataFrame()

# ✅ ガントチャート描画
def draw_gantt_chart(df):
    fig, ax = plt.subplots(figsize=(10, 2 + 0.5 * len(df)))
    for i, row in df.iterrows():
        ax.barh(
            y=row["task"],
            width=(row["end"] - row["start"]).days,
            left=row["start"],
            height=0.4,
            color=row.get("color", "skyblue"),
            edgecolor="black"
        )
    ax.set_xlabel("日付")
    ax.set_ylabel("タスク")
    ax.grid(True)
    st.pyplot(fig)

# ✅ ChatGPTからタスク抽出
def extract_tasks_from_text(text, api_key, style_instruction=""):
    client = OpenAI(api_key=api_key)
    prompt = f"""
以下の日本語テキストからプロジェクトタスクを抽出し、JSON形式で出力してください。
説明文や補足は不要です。以下の形式でお願いします：

[
  {{
    "task": "タスク名",
    "start": "YYYY-MM-DD",
    "end": "YYYY-MM-DD",
    "color": "blue"（任意）
  }},
  ...
]

{style_instruction}

{text}
    """.strip()

    response = client.chat.completions.create(
        model="gpt-4o-mini",  # 修正済み
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
    )
    raw = response.choices[0].message.content
    json_text = extract_json_string(raw)
    return json_text

# ✅ Streamlit UI
st.set_page_config(page_title="ガントチャート生成ツール", layout="wide")
st.title("🗂 ChatGPTによるガントチャート自動生成")

text = st.text_area("📋 プロジェクトタスク概要を日本語で入力してください", height=250)
api_key = st.text_input("🔑 OpenAI APIキー", type="password")
style_prompt = st.text_area("🎨 スタイル指示（任意）", value="色はタスクごとに分けてください。")

if st.button("🚀 ChatGPTで解析してガントチャート生成"):
    with st.spinner("ChatGPTで解析中..."):
        if is_json_like(text):
            json_text = text
        else:
            json_text = extract_tasks_from_text(text, api_key, style_prompt)

        df = json_to_df(json_text)
        if not df.empty:
            st.success("✅ ガントチャートを生成しました")
            draw_gantt_chart(df)
        else:
            st.error("❌ データがありませんでした")
