import streamlit as st
from openai import OpenAI
import pandas as pd
import json
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.font_manager as fm
import os
import re

# フォント設定（日本語対応）
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

def extract_tasks_from_text(text, api_key, style_instruction=""):
    client = OpenAI(api_key=api_key)
    prompt = f"""
以下のテキストからプロジェクトのタスクとその期間（開始日・終了日）を抽出し、以下のJSON形式で返してください。
可能であれば、タスクごとに "color" や "height" を指定してください。

[
  {{
    "task": "ネットワーク設計",
    "start": "2025-06-01",
    "end": "2025-06-15",
    "color": "red",
    "height": 0.4
  }}
]

説明は不要です。返答はJSONのみでお願いします。

テキスト:
{text}

スタイルに関する指示:
{style_instruction}
"""
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "あなたはプロジェクトマネージャーのアシスタントです。"},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content.strip()

def json_to_df(json_text):
    if not json_text.strip() or not is_json_like(json_text):
        st.error("❌ ChatGPTが有効なJSONを返しませんでした。以下をご確認ください：")
        st.code(json_text)
        return pd.DataFrame()
    try:
        task_list = json.loads(json_text)
        df = pd.DataFrame(task_list)
        df['start'] = pd.to_datetime(df['start'], format="%Y-%m-%d")
        df['end'] = pd.to_datetime(df['end'], format="%Y-%m-%d")
        return df
    except Exception as e:
        st.error("❌ JSONまたは日付変換に失敗しました。以下の出力を確認してください：")
        st.code(json_text)
        raise e

def plot_gantt(df, title):
    df = df.sort_values("start", ascending=False)
    fig, ax = plt.subplots(figsize=(12, 6))
    for i, row in df.iterrows():
        color = row.get("color", "skyblue")
        height = row.get("height", 0.5)
        ax.barh(row['task'], (row['end'] - row['start']).days,
                left=row['start'], height=height, color=color)

    ax.xaxis.set_major_locator(mdates.MonthLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
    ax.xaxis.tick_top()
    ax.xaxis.set_label_position('top')
    plt.xticks(rotation=45)
    ax.grid(True, axis='both', linestyle='--', alpha=0.5)
    plt.title(title, y=1.1)
    plt.tight_layout()
    st.pyplot(fig)

# Streamlit UI
st.title("📤 テキスト or .txtファイル → ガントチャート生成")

api_key = st.text_input("🔑 OpenAI APIキーを入力してください", type="password")

st.subheader("📄 テキストを入力するか、.txtファイルをアップロードしてください")
col1, col2 = st.columns(2)
with col1:
    uploaded_file = st.file_uploader("📁 .txtファイルをアップロード", type="txt")
with col2:
    manual_text = st.text_area("✍️ 自由入力欄", height=300, placeholder="例：4月にネットワーク設計を実施。5月にはサーバー構築…")

style_prompt = st.text_area("🎨 スタイルの指定（任意）", placeholder="例：ネットワーク設計は赤く、開発は青く。全体のバーの高さは0.4に。")

text = ""
if uploaded_file:
    text = uploaded_file.read().decode("utf-8")
    st.success("✅ ファイル読み込み成功")
elif manual_text.strip():
    text = manual_text
    st.success("✅ 入力内容を使用します")

if text and api_key:
    st.subheader("📄 入力されたテキスト内容")
    st.text(text[:1000] + ("..." if len(text) > 1000 else ""))

    chart_title = st.text_input("📌 ガントチャートのタイトル", value="自然文から生成されたガントチャート")

    if st.button("🚀 ChatGPTで解析してガントチャート生成"):
        with st.spinner("ChatGPTで解析中..."):
            json_text = extract_tasks_from_text(text, api_key, style_prompt)
            df = json_to_df(json_text)

        if not df.empty:
            st.success("✅ ガントチャート生成完了！")
            st.subheader("📋 抽出されたタスク一覧")
            st.dataframe(df)
            st.subheader("📈 ガントチャート")
            plot_gantt(df, chart_title)
