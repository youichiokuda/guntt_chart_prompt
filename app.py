import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import json
import re
import os
import matplotlib.font_manager as fm
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

# ✅ JSON形式か判定
def is_json_like(text):
    return bool(re.match(r'^[\s]*[\[{]', text.strip()))

def json_to_df(json_text):
    try:
        data = json.loads(json_text)
        df = pd.DataFrame(data)
        df["start"] = pd.to_datetime(df["start"])
        df["end"] = pd.to_datetime(df["end"])
        return df
    except Exception as e:
        st.error(f"❌ JSON解析エラー: {e}")
        return pd.DataFrame()

def draw_gantt_chart(df):
    fig, ax = plt.subplots(figsize=(10, 2 + 0.5 * len(df)))
    for i, row in df.iterrows():
        ax.barh(
            y=row["task"],
            width=(row["end"] - row["start"]).days,
            left=row["start"],
            height=row.get("height", 0.4),
            color=row.get("color", "skyblue"),
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

def extract_tasks_from_text(text, api_key, style_instruction=""):
    client = OpenAI(api_key=api_key)
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",  # 権限のあるモデルに変更
        messages=[
            {"role": "system", "content": "あなたはプロジェクトマネージャーです。入力された文章からタスク一覧を抽出し、JSON形式で返してください。"},
            {"role": "user", "content": f"""
以下の文章を読み取り、JSON形式でタスクを抽出してください。形式は以下に準拠してください：

[
  {{
    "task": "タスク名",
    "start": "YYYY-MM-DD",
    "end": "YYYY-MM-DD",
    "color": "任意の色名またはコード",
    "height": 任意の数値（バーの高さ）
  }},
  ...
]

入力文章:
{text}

スタイルに関する指示:
{style_instruction}
"""}
        ]
    )
    return response.choices[0].message.content.strip()

# Streamlit アプリUI
st.title("📊 自然言語からガントチャートを生成")

api_key = st.text_input("🔑 OpenAI API Key", type="password")
text = st.text_area("📝 プロジェクト文章またはJSONを入力")
style_prompt = st.text_area("🎨 スタイル指定（任意）", placeholder="色、高さなどのルールを指示できます")

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
