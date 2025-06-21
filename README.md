# 📊 Gantt Chart Generator (Streamlit + OpenAI + Docker)

このアプリは、自然文やテキストファイルからタスクを抽出し、OpenAI API を用いてガントチャートを自動生成する Streamlit アプリです。Docker で簡単に動作させることができます。

---

## 🚀 機能概要

- 自然文テキストからタスク（名称、開始日、終了日）を抽出
- ChatGPTを活用してJSON形式に変換
- matplotlibでガントチャートを描画
- 色・高さなどのスタイル指定をプロンプトで指示可能

---

## 📦 セットアップ手順

### 1. リポジトリをクローン

```bash
git clone <REPO_URL>
cd guntt_chart_prompt
```

### 2. Dockerイメージをビルド

```bash
docker build -t gantt-chart-app .
```

### 3. コンテナを起動

```bash
docker run -p 8501:8501 gantt-chart-app
```

### 4. ブラウザでアクセス

```
http://localhost:8501
```

---

## 🧠 使用方法

1. OpenAI APIキーを入力
2. テキストファイルをアップロードするか、手動でタスクを入力
3. 任意でスタイル指示（例："ネットワーク設計は赤に。バーの高さは0.3に"）を入力
4. [🚀 ChatGPTで解析してガントチャート生成] をクリック

---

## 📝 例

### 入力テキスト：
```
4月にネットワーク設計。5月に開発。6月にテスト。
```

### スタイル指示：
```
ネットワーク設計は赤。開発は青。テストは緑。バーの高さは0.3に。
```

---

## ✅ 必要条件
- OpenAI APIキー（`gpt-4o-mini` モデル推奨）
- Docker

---

## 📄 ファイル構成

```
guntt_chart_prompt/
├── app.py             # Streamlitアプリ本体
├── Dockerfile         # Dockerビルド用
├── requirements.txt   # Python依存ライブラリ
└── README.md          # 本ファイル
```

---

## 🛠 よくあるエラー対処

| エラー | 対処方法 |
|--------|-----------|
| OpenAIのJSON出力が不正 | プロンプトを簡潔にし、構造化指示を見直す |
| フォントが表示されない | Dockerfileで日本語フォントを明示的にインストール |
| アプリにアクセスできない | `localhost:8501` を確認、ポートが空いているか検証 |

---

## 📬 サポート

不明点・改善希望があれば、Issues か Pull Request を送ってください。

---

## 🧡 ライセンス

MIT License
