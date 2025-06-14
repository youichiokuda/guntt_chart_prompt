import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.font_manager as fm
import os
import re
from datetime import datetime
from openai import OpenAI
import json

# ✅ フォント設定（日本語対応）
font_candidates = [
    "/usr/share/fonts/opentype/ipafont-gothic/ipagp.ttf",
    "/usr/share/fonts/truetype/takao-gothic/TakaoPGothic.ttf",
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
]

for font_path in font_candidates:
    if os.path.exists(font_path):
        fm.fontManager.addfont(font_path)
        plt.rcParams["font.family"] = fm.FontProperties(fname=font_path).get_name()
        break
else:
    plt.rcParams["font.family"] = "sans-serif"

# ✅ OpenAI 初期化
client = OpenAI()

# ✅ JSONらしい形式かを確認
def is_json_like(text):
    return bool(re.match(r'^[\s]*[\[{]', text.strip()))

# ✅ ガントチャート描画関数
def plot_gantt(df, title):
    df = df.sort_values("start", ascending=False)
    fig, ax = plt.subplots(figsize=(12, 6))

    for _, row in df.iterrows():
        ax.barh(row['task'], (row['end'] - row['start']).days, left=row['start'], height=0.5)

    ax.xaxis.set_major_locator(mdates.MonthLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
    ax.xaxis.tick_top()
    ax.xaxis.set_label_position('top')
    plt.xticks(rotation=45)
    ax.grid(True, axis='both', linestyle='--', alpha=0.5)

    plt.title(title, y=1.1)
    plt.tight_layout()
    st.pyplot(fig)

# ✅ JSON→DataFrame変換
def json_to_df(json_str):
    try:
        data = json.loads(json_str)
        df = pd.DataFrame(data)
        df["start"] = pd.to_datetime(df["start"])
        df["end"] = pd.to_datetime(df["end"])
        return df
    except Exception as e:
        st.error(f"JSONパースエラー: {e}")
        return pd.DataFrame()

# ✅ OpenAI にプロンプト送信してJSON出力を得る
def get_gantt_from_prompt(prompt):
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {
                "role": "system",
                "content": "あなたはプロジェクトマネージャーです。与えられた説明からJSON形式のガントチャートデータを生成してください。形式: [{\"task\": ..., \"start\": ..., \"end\": ...}, ...]"
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.3,
        response_format="json"
    )
    return response.choices[0].message.content

# ✅ Streamlit アプリ本体
st.title("🗓️ プロンプトからガントチャート生成")

input_text = st.text_area("プロンプトを入力（例: システム開発のプロジェクト計画）", height=200)

if st.button("ガントチャート生成"):
    if not input_text.strip():
        st.warning("プロンプトを入力してください。")
    else:
        with st.spinner("生成中..."):
            output_json = get_gantt_from_prompt(input_text)
            if is_json_like(output_json):
                df = json_to_df(output_json)
                if not df.empty:
                    st.success("ガントチャートを生成しました。")
                    st.dataframe(df)
                    plot_gantt(df, "ガントチャート")
                else:
                    st.error("解析されたデータが空です。プロンプトの内容を確認してください。")
            else:
                st.error("OpenAIから有効なJSONが返されませんでした。")
                st.code(output_json)
