import streamlit as st
import pandas as pd
import os
import altair as alt
from datetime import datetime
from zoneinfo import ZoneInfo

# =========================
# 日本時間（最重要）
# =========================
today = datetime.now(ZoneInfo("Asia/Tokyo")).date()

# =========================
# ページ設定
# =========================
st.set_page_config(
    page_title="歩数トラッカー",
    page_icon="🐾",
    layout="wide"
)

# =========================
# デザイン
# =========================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Nunito', sans-serif;
}

.stApp {
    background-color: #fffaf4;
}

.card {
    background: white;
    padding: 20px;
    border-radius: 18px;
    box-shadow: 0 6px 18px rgba(0,0,0,0.08);
    margin-bottom: 20px;
}

.title {
    font-size: 30px;
    font-weight: 700;
    color: #ff8fab;
}

.subtitle {
    font-size: 14px;
    color: #888;
}

.kpi {
    font-size: 26px;
    font-weight: bold;
}

.stButton > button {
    background: linear-gradient(135deg, #ff8fab, #ffb3c1);
    color: white;
    border-radius: 12px;
    border: none;
}

/* progress色 */
.stProgress > div > div > div > div {
    background-color: #FFA500 !important;
}
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
    return pd.DataFrame({
        "date": dates.date,
        "steps": [0]*len(dates)
    })

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
col1, col2 = st.columns(2)

with col1:
   
    st.subheader("🎯 目標設定")

    target1 = st.number_input("目標①", value=15000)
    target_past_avg = st.number_input("今日までの目標平均", value=15000)

with col2:
    st.subheader("📅 今日の記録")

    # ← 修正ポイント
    selected_date = st.date_input("日付", today)

    today_steps = df.loc[df["date"] == selected_date, "steps"]
    default_steps = int(today_steps.values[0]) if len(today_steps)>0 else 0

    if "steps_input" not in st.session_state:
        st.session_state.steps_input = default_steps

    c1, c2 = st.columns(2)
    with c1:
        if st.button("+100"):
            st.session_state.steps_input += 100
    with c2:
        if st.button("+1000"):
            st.session_state.steps_input += 1000

    steps = st.number_input(
        "歩数",
        min_value=0,
        key="steps_input"
    )

    if st.button("保存"):
        df.loc[df["date"] == selected_date, "steps"] = steps
        save_data(df)
        st.success("保存しました！")

# =========================
# 計算
# =========================
total_steps = df["steps"].sum()
days = len(df)

# ← ここも日本時間を使う
# todayは上で定義済み

goal1_total = target1 * days
progress1 = min(total_steps / goal1_total * 100, 100)

remaining_days = (df["date"] >= today).sum()
remain1 = max(goal1_total - total_steps, 0)

# ★ここはあなたの希望通りそのまま
avg_needed1 = remain1 / (remaining_days-1) if remaining_days > 0 else 0

# 今日まで
df_past = df[df["date"] <= today]
past_days = len(df_past)

past_total = df_past["steps"].sum()
avg_steps_so_far = past_total / past_days if past_days > 0 else 0

target_past_total = target_past_avg * past_days
needed_past = max(target_past_total - past_total, 0)

# =========================
# KPI
# =========================

# 今日まで
st.markdown("### 📅 今日まで")

c1, c2, c3 = st.columns(3)

with c1:
    st.markdown(f"""
    <div class="card">
        <div class="subtitle">平均歩数</div>
        <div class="kpi">{avg_steps_so_far:.0f}</div>
    </div>
    """, unsafe_allow_html=True)

with c2:
    st.markdown(f"""
    <div class="card">
        <div class="subtitle">目標平均</div>
        <div class="kpi">{target_past_avg}</div>
    </div>
    """, unsafe_allow_html=True)

with c3:
    st.markdown(f"""
    <div class="card">
        <div class="subtitle">不足歩数</div>
        <div class="kpi">{needed_past:,.0f}</div>
    </div>
    """, unsafe_allow_html=True)


st.markdown("### 📊 月全体")

c1, c2, c3 = st.columns(3)

with c1:
    st.markdown(f"""
    <div class="card">
        <div class="subtitle">合計歩数</div>
        <div class="kpi">{total_steps:,}</div>
    </div>
    """, unsafe_allow_html=True)

with c2:
    st.markdown(f"""
    <div class="card">
        <div class="subtitle">達成率</div>
        <div class="kpi">{progress1:.1f}%</div>
    </div>
    """, unsafe_allow_html=True)

with c3:
    st.markdown(f"""
    <div class="card">
        <div class="subtitle">必要平均歩数</div>
        <div class="kpi">{avg_needed1:.0f}</div>
    </div>
    """, unsafe_allow_html=True)

# =========================
# 進捗バー
# =========================
st.write("### 🎯 目標①")
st.progress(int(progress1))
st.write(f"残り：{remain1:,.0f}歩 / 必要平均：{avg_needed1:.0f}歩/日")

# =========================
# グラフ
# =========================
chart_df = df.copy()
chart_df["date"] = pd.to_datetime(chart_df["date"])
chart_df["target"] = target1

bars = alt.Chart(chart_df).mark_bar(
    cornerRadiusTopLeft=6,
    cornerRadiusTopRight=6
).encode(
    x='date:T',
    y='steps:Q',
    color=alt.value("#FFA500")
)

line = alt.Chart(chart_df).mark_line(
    strokeDash=[5,5],
    color="#ff8fab"
).encode(
    x='date:T',
    y='target:Q'
)

st.altair_chart(bars + line, use_container_width=True)

# ========================= 
#  累計グラフ用データ作成 
# ========================= 
chart_df = df.copy() 
chart_df["date"] = pd.to_datetime(chart_df["date"]) 
# 実績累計
chart_df["actual_cum"] = chart_df["steps"].cumsum() 
# 目標累計（例：target1） 
chart_df["target_cum"] = target1 * (chart_df.index + 1)

# ========================= 
#  グラフ 
# =========================

actual_line = alt.Chart(chart_df).mark_line(
    color="#FFA500",
    strokeWidth=3
).encode(
    x=alt.X("date:T", title="日付"),
    y=alt.Y("actual_cum:Q", title="累計歩数")
)

target_line = alt.Chart(chart_df).mark_line(
    color="#ff8fab",
    strokeDash=[5,5],
    strokeWidth=2
).encode(
    x="date:T",
    y="target_cum:Q"
)

# 合成
st.altair_chart(actual_line + target_line, use_container_width=True)