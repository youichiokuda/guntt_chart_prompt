import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import os
import openai
import re
from datetime import datetime

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

def is_json_like(text):
    return bool(re.match(r'^[\s]*[\[{]', text.strip()))

def draw_gantt_chart(df):
    fig, ax = plt.subplots(figsize=(10, 4))
    for idx, row in df.iterrows():
        try:
            ax.barh(
                y=row["task"],
                left=row["start"],
                width=(row["end"] - row["start"]).days,
                height=row.get("height", 0.4),
                color=row.get("color", "skyblue"),
                edgecolor="black"
            )
        except ValueError as e:
            st.error(f"色指定 '{row.get('color')}' に問題があります: {e}")
            return
    ax.set_xlabel("日付")
    ax.set_ylabel("タスク")
    ax.set_title("ガントチャート")
    plt.tight_layout()
    st.pyplot(fig)

def json_to_df(json_text):
    try:
        data = eval(json_text) if isinstance(json_text, str) else json_text
        df = pd.DataFrame(data)
        df["start"] = pd.to_datetime(df["start"])
        df["end"] = pd.to_datetime(df["end"])
        return df
    except Exception as e:
        st.error(f"JSONパースエラー: {e}")
        return pd.DataFrame()

def extract_tasks_from_text(text, api_key, style_instruction=""):
    client = openai.OpenAI(api_key=api_key)
    prompt = f"""
以下の文章からタスクの一覧を抽出し、ガントチャート形式で視覚化できるように、各タスクをJSONで出力してください。
JSONの形式は以下のようにしてください：
[
  {{
    "task": "タスク名",
    "start": "YYYY-MM-DD",
    "end": "YYYY-MM-DD",
    "color": "任意の色（blueやgreenなど）",
    "height": 0.4
  }},
  ...
]

文章:
{text}

スタイルに関する指示:
{style_instruction}
"""
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "あなたはプロジェクトマネージャーです。"},
            {"role": "user", "content": prompt}
        ],
        temperature=0.3
    )
    return response.choices[0].message.content.strip()

st.title("🗓️ ガントチャート生成ツール（自然文 → 可視化）")

api_key = st.text_input("🔑 OpenAI APIキーを入力してください", type="password")
text = st.text_area("📄 ガントチャートにしたいスケジュール文章を入力してください")

style_prompt = st.text_area("🎨 表示スタイルや色の希望（任意）", "例：サーバー関係は青、イベントは緑、高さは0.4")

if st.button("🚀 ChatGPTで解析してガントチャート生成"):
    if not api_key:
        st.warning("APIキーを入力してください。")
    else:
        with st.spinner("ChatGPTで解析中..."):
            try:
                json_text = extract_tasks_from_text(text, api_key, style_prompt)
                df = json_to_df(json_text)
                if not df.empty:
                    st.success("✅ ガントチャートを生成しました！")
                    draw_gantt_chart(df)
                    with st.expander("📋 JSON出力を表示"):
                        st.code(json_text, language="json")
                else:
                    st.warning("解析されたデータが空です。入力内容を確認してください。")
            except Exception as e:
                st.error(f"エラーが発生しました: {e}")
