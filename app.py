import streamlit as st
import pandas as pd
import os
from datetime import date
import altair as alt

# =========================
# ページ設定
# =========================
st.set_page_config(
    page_title="歩数トラッカー",
    page_icon="🐾",
    layout="wide"
)

# =========================
# デザイン（Figma風）
# =========================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Nunito', sans-serif;
}

/* 背景 */
.stApp {
    background-color: #fffaf4;
}

/* カード */
.card {
    background: white;
    padding: 20px;
    border-radius: 18px;
    box-shadow: 0 6px 18px rgba(0,0,0,0.08);
    margin-bottom: 20px;
    transition: 0.2s;
}
.card:hover {
    transform: translateY(-3px);
}

/* タイトル */
.title {
    font-size: 30px;
    font-weight: 700;
    color: #ff8fab;
}

/* サブ */
.subtitle {
    font-size: 14px;
    color: #888;
}

/* KPI */
.kpi {
    font-size: 26px;
    font-weight: bold;
    color: #333;
}

/* ボタン */
.stButton > button {
    background: linear-gradient(135deg, #ff8fab, #ffb3c1);
    color: white;
    border-radius: 12px;
    border: none;
    padding: 10px 20px;
    font-weight: bold;
}

/* プログレス */
.stProgress > div > div > div {
    background-color: ##a6cdb6;
}
</style>
""", unsafe_allow_html=True)


st.markdown("""
<style>
/* 進捗バーの進んでいる部分（オレンジ） */
.stProgress > div > div > div > div {
    background-color: #FFA500 !important;
}

/* 残り部分（ピンクのところ） */
.stProgress > div > div > div {
    background-color: #FFE9B2 !important;
}
</style>
""", unsafe_allow_html=True)
# =========================
# データ管理
# =========================
FILE_NAME = "steps.csv"

def init_data():
    dates = pd.date_range("2026-05-01", "2026-05-31")
    df = pd.DataFrame({
        "date": dates.date,
        "steps": [0]*len(dates)
    })
    return df

def load_data():
    if os.path.exists(FILE_NAME):
        df = pd.read_csv(FILE_NAME)
        df["date"] = pd.to_datetime(df["date"]).dt.date
        return df
    else:
        df = init_data()
        df.to_csv(FILE_NAME, index=False)
        return df

def save_data(df):
    df.to_csv(FILE_NAME, index=False)

df = load_data()

# =========================
# ヘッダー
# =========================
st.markdown('<div class="title">🐾 歩数トラッカー（5月）</div>', unsafe_allow_html=True)


# =========================
# 入力エリア
# =========================
col1, col2 = st.columns([1,1])

with col1:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("📅 今日の記録")

    selected_date = st.date_input("日付", date(2026,5,1))

    today_steps = df.loc[df["date"] == selected_date, "steps"]
    default_steps = int(today_steps.values[0]) if len(today_steps)>0 else 0

    steps = st.number_input("歩数", min_value=0, value=default_steps)

    if st.button("保存"):
        df.loc[df["date"] == selected_date, "steps"] = steps
        save_data(df)
        st.success("保存しました！")

    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("🎯 目標設定")

    target1 = st.number_input("目標①（ゆるめ）", value=8000)
    target2 = st.number_input("目標②（チャレンジ）", value=10000)

    st.markdown('</div>', unsafe_allow_html=True)

# =========================
# 計算
# =========================
total_steps = df["steps"].sum()
days = len(df)

goal1_total = target1 * days
goal2_total = target2 * days

progress1 = min(total_steps / goal1_total * 100, 100)
progress2 = min(total_steps / goal2_total * 100, 100)

today = date.today()
remaining_days = (df["date"] >= today).sum()

remain1 = max(goal1_total - total_steps, 0)
remain2 = max(goal2_total - total_steps, 0)

avg_needed1 = remain1 / remaining_days if remaining_days > 0 else 0
avg_needed2 = remain2 / remaining_days if remaining_days > 0 else 0

# =========================
# KPI表示
# =========================
st.markdown("### 📊 進捗")

k1, k2, k3 = st.columns(3)

with k1:
    st.markdown(f"""
    <div class="card">
        <div class="subtitle">合計歩数</div>
        <div class="kpi">{total_steps:,}</div>
    </div>
    """, unsafe_allow_html=True)

with k2:
    st.markdown(f"""
    <div class="card">
        <div class="subtitle">達成率（目標①）</div>
        <div class="kpi">{progress1:.1f}%</div>
    </div>
    """, unsafe_allow_html=True)

with k3:
    st.markdown(f"""
    <div class="card">
        <div class="subtitle">必要平均</div>
        <div class="kpi">{avg_needed1:.0f} 歩/日</div>
    </div>
    """, unsafe_allow_html=True)

k1, k2, k3 = st.columns(3)

with k1:
    st.markdown(f"""
    <div class="card">
        <div class="subtitle">合計歩数</div>
        <div class="kpi">{total_steps:,}</div>
    </div>
    """, unsafe_allow_html=True)

with k2:
    st.markdown(f"""
    <div class="card">
        <div class="subtitle">達成率（目標②）</div>
        <div class="kpi">{progress2:.1f}%</div>
    </div>
    """, unsafe_allow_html=True)

with k3:
    st.markdown(f"""
    <div class="card">
        <div class="subtitle">必要平均</div>
        <div class="kpi">{avg_needed2:.0f} 歩/日</div>
    </div>
    """, unsafe_allow_html=True)

# =========================
# 詳細進捗
# =========================


st.write("### 🎯 目標①")
st.progress(int(progress1))
st.write(f"残り：{remain1:,.0f}歩 / 必要平均：{avg_needed1:.0f}歩/日")

st.write("### 🚀 目標②")
st.progress(int(progress2))
st.write(f"残り：{remain2:,.0f}歩 / 必要平均：{avg_needed2:.0f}歩/日")

st.markdown('</div>', unsafe_allow_html=True)

# =========================
# グラフ
# =========================


chart_df = df.copy()
chart_df["date"] = pd.to_datetime(chart_df["date"])

# 目標ライン用データ
chart_df["target"] = target1

# 実績（棒）
bars = alt.Chart(chart_df).mark_bar(
    cornerRadiusTopLeft=6,
    cornerRadiusTopRight=6
).encode(
    x=alt.X('date:T', title='日付'),
    y=alt.Y('steps:Q', title='歩数'),
    color=alt.value("#FFA500")  # ← 実績だけオレンジ
)

# 目標（線）
line = alt.Chart(chart_df).mark_line(
    strokeDash=[5,5],
    color="#ff8fab"
).encode(
    x='date:T',
    y='target:Q'
)

# 合成
chart = bars + line

st.altair_chart(chart, use_container_width=True)