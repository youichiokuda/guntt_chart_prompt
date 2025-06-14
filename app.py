import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.font_manager as fm
import datetime
import openai
import json
import re
import os
import urllib.request
from pathlib import Path

# ✅ 日本語フォント設定（Streamlit Cloud対応）
font_url = "https://github.com/googlefonts/noto-cjk/raw/main/Sans/OTF/Japanese/NotoSansCJKjp-Regular.otf"
font_dir = Path("/tmp/fonts")
font_path = font_dir / "NotoSansCJKjp-Regular.otf"

if not font_path.exists():
    font_dir.mkdir(parents=True, exist_ok=True)
    urllib.request.urlretrieve(font_url, font_path)

fm.fontManager.addfont(str(font_path))
plt.rcParams["font.family"] = fm.FontProperties(fname=str(font_path)).get_name()

# ✅ JSON判定関数
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

# ✅ Streamlit UI
st.title("🗓️ ガントチャート生成アプリ")

api_key = st.text_input("🔑 OpenAI APIキーを入力", type="password")
user_input = st.text_area("📋 スケジュール内容を入力してください", height=300)
model = st.selectbox("🤖 使用するモデル", ["gpt-4o", "gpt-4", "gpt-4o-mini", "gpt-3.5-turbo"])

if st.button("ガントチャートを生成"):
    if not api_key:
        st.warning("⚠️ OpenAI APIキーを入力してください。")
    elif not user_input.strip():
        st.warning("⚠️ スケジュール内容を入力してください。")
    else:
        try:
            openai.api_key = api_key
            with st.spinner("⏳ ChatGPTがスケジュールを解析中..."):
                prompt = f"""
以下の文章から日付とタスクを抽出し、JSON形式で出力してください。
各タスクは、"task"（内容）, "start"（開始日）, "end"（終了日）を含みます。
フォーマット:
[
  {{
    "task": "タスク名",
    "start": "2025-06-01",
    "end": "2025-06-10"
  }},
  ...
]
文章:
{user_input}
"""
                response = openai.ChatCompletion.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": "あなたはプロジェクトマネージャーです。"},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.2
                )

            result = response.choices[0].message.content.strip()

            if is_json_like(result):
                try:
                    json_data = json.loads(result)
                    df = pd.DataFrame(json_data)
                    df["start"] = pd.to_datetime(df["start"])
                    df["end"] = pd.to_datetime(df["end"])
                    st.success("✅ ガントチャートを表示します")
                    plot_gantt(df, "スケジュール")
                    with st.expander("📄 JSON表示"):
                        st.json(json_data)
                    with st.expander("📊 表形式"):
                        st.dataframe(df)
                except Exception as e:
                    st.error(f"JSON解析エラー: {e}")
            else:
                st.error("❌ ChatGPTから有効なJSONが返されませんでした。出力:\n\n" + result)

        except Exception as e:
            st.error(f"エラーが発生しました: {e}")
