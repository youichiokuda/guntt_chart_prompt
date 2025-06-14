import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.font_manager as fm
import os
import re
import json
from datetime import datetime
from openai import OpenAI

st.set_page_config(page_title="ガントチャート生成アプリ", layout="wide")
st.title("🗓️ ガントチャート生成アプリ")

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

def parse_schedule(text):
    try:
        data = json.loads(text)
        df = pd.DataFrame(data)
        df['start'] = pd.to_datetime(df['start'])
        df['end'] = pd.to_datetime(df['end'])
        return df
    except Exception as e:
        st.error("JSONパースエラー: {}".format(e))
        return pd.DataFrame()

def plot_gantt(df, title):
    df = df.sort_values("start", ascending=False)
    fig, ax = plt.subplots(figsize=(12, 6))
    for i, row in df.iterrows():
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

st.sidebar.header("🔑 OpenAI APIキーと設定")
api_key = st.sidebar.text_input("OpenAI APIキー", type="password")
model = st.sidebar.selectbox("モデル", ["gpt-4o", "gpt-4", "gpt-3.5-turbo"])
st.sidebar.markdown("---")
st.sidebar.markdown("[📚 使い方の説明](https://github.com/openai/openai-python)")

st.subheader("📝 スケジュール文章を入力")
user_input = st.text_area("スケジュール内容を日本語で入力してください", height=200)

if st.button("ガントチャートを生成"):
    if not api_key:
        st.warning("⚠️ OpenAI APIキーを入力してください。")
    elif not user_input.strip():
        st.warning("⚠️ スケジュール内容を入力してください。")
    else:
        try:
            client = OpenAI(api_key=api_key)

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
                
                response = client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": "あなたはプロジェクトマネージャーです。"},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.2
                )

                result = response.choices[0].message.content.strip()

            st.subheader("📋 ChatGPTの解析結果")
            st.code(result, language='json')

            if is_json_like(result):
                df = parse_schedule(result)
                if not df.empty:
                    st.subheader("📊 ガントチャート")
                    plot_gantt(df, "プロジェクトスケジュール")
                else:
                    st.warning("解析されたデータが空です。入力内容を確認してください。")
            else:
                st.warning("ChatGPTからの出力がJSON形式ではありませんでした。")

        except Exception as e:
            st.error(f"エラーが発生しました: {e}")
