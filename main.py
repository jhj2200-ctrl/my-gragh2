import streamlit as st
import pandas as pd
import plotly.express as px

# -----------------------------------
# 페이지 기본 설정
# -----------------------------------
st.set_page_config(
    page_title="영화 데이터 그래프 도감 2 - 분포와 관계",
    page_icon="🎬",
    layout="wide"
)

st.title("🎬 영화 데이터 그래프 도감 2 - 분포와 관계")
st.write(
    "1년간 박스오피스 10위권에 든 영화 가운데 "
    "이 기간에 개봉한 영화들의 데이터를 살펴봅니다."
)

# -----------------------------------
# 데이터 불러오기
# -----------------------------------
DATA_URL = (
    "https://raw.githubusercontent.com/greatsong/modudata/main/data/kobis_movies.csv"
)


@st.cache_data
def load_data():
    df = pd.read_csv(DATA_URL)

    # 개봉일을 날짜 형식으로 변환
    df["openDt"] = pd.to_datetime(
        df["openDt"].astype(str),
        format="%Y%m%d",
        errors="coerce"
    )

    # 장르가 여러 개라면 첫 번째 장르만 사용
    df["genre"] = (
        df["genre"]
        .fillna("기타")
        .astype(str)
        .str.split("|")
        .str[0]
        .str.strip()
    )

    # 빈 장르는 기타로 처리
    df.loc[df["genre"] == "", "genre"] = "기타"

    return df


df = load_data()

# -----------------------------------
# 데이터 확인
# -----------------------------------
st.subheader("📊 데이터 개요")

col1, col2 = st.columns(2)

with col1:
    st.metric("영화 수", f"{len(df):,}편")

with col2:
    st.metric("장르 수", f"{df['genre'].nunique():,}개")


# -----------------------------------
# 그래프 1. 장르별 영화 편수
# -----------------------------------
st.divider()
st.header("1. 장르별 영화 편수")

genre_count = (
    df["genre"]
    .value_counts()
    .reset_index()
)

genre_count.columns = ["장르", "영화 편수"]

fig = px.pie(
    genre_count,
    names="장르",
    values="영화 편수",
    hole=0.45,
    title="장르별 영화 편수"
)

fig.update_traces(
    textinfo="label+percent",
    hovertemplate=(
        "<b>%{label}</b><br>"
        "영화 편수: %{value}편<br>"
        "비율: %{percent}<extra></extra>"
    )
)

fig.update_layout(
    height=550,
    legend_title_text="장르"
)

st.plotly_chart(fig, use_container_width=True)

st.info("💡 이 그래프로 알 수 있는 것:"  "영화 장르 중 어떤 장르가 가장 많은 비중을 차지하고, "
    "어떤 장르가 적은 비중을 차지하는지 알 수 있습니다.")

# -----------------------------------
# 원본 데이터 일부 확인
# -----------------------------------
st.divider()
st.subheader("📋 원본 데이터 미리보기")

st.dataframe(
    df,
    use_container_width=True,
    hide_index=True
)
# -----------------------------------
# 그래프 2. 장르별 영화 트리맵
# -----------------------------------
st.divider()
st.header("2. 장르 안에 들어 있는 영화")

# 총 관객 수를 숫자로 변환
df["total_audi"] = pd.to_numeric(
    df["total_audi"],
    errors="coerce"
).fillna(0)

fig2 = px.treemap(
    df,
    path=["genre", "movieNm"],
    values="total_audi",
    title="장르별 영화의 총 관객 규모"
)

fig2.update_traces(
    hovertemplate=(
        "<b>%{label}</b><br>"
        "총 관객: %{value:,.0f}명"
        "<extra></extra>"
    )
)

fig2.update_layout(
    height=650
)

st.plotly_chart(
    fig2,
    use_container_width=True
)

st.info(
    "💡 이 그래프로 알 수 있는 것: "
    "각 장르 안에서 어떤 영화가 많은 관객을 모았는지와 "
    "영화별 총 관객 규모의 차이를 비교할 수 있습니다."
)
# -----------------------------------
# 그래프 3. 총 관객 히스토그램
# -----------------------------------
st.divider()
st.header("3. 영화별 총 관객 분포")

# 총 관객 수를 숫자로 변환
df["total_audi"] = pd.to_numeric(
    df["total_audi"],
    errors="coerce"
).fillna(0)

# 히스토그램
fig3 = px.histogram(
    df,
    x="total_audi",
    nbins=20,
    title="영화별 총 관객 분포",
    labels={
        "total_audi": "총 관객 수",
        "count": "영화 편수"
    }
)

fig3.update_traces(
    hovertemplate=(
        "총 관객 구간: %{x}<br>"
        "영화 편수: %{y}편"
        "<extra></extra>"
    )
)

fig3.update_layout(
    height=550,
    xaxis_title="총 관객 수",
    yaxis_title="영화 편수"
)

st.plotly_chart(
    fig3,
    use_container_width=True
)


# 가장 관객이 많은 영화 찾기
max_audience_row = df.loc[df["total_audi"].idxmax()]

max_movie = max_audience_row["movieNm"]
max_audience = max_audience_row["total_audi"]


# 가장 많은 영화가 속한 관객 구간 계산
hist_counts, bin_edges = __import__("numpy").histogram(
    df["total_audi"],
    bins=20
)

max_bin_index = hist_counts.argmax()
bin_start = bin_edges[max_bin_index]
bin_end = bin_edges[max_bin_index + 1]

st.info(
    f"💡 이 그래프로 알 수 있는 것: "
    f"대부분의 영화는 총 관객 약 {bin_start:,.0f}명~{bin_end:,.0f}명 구간에 몰려 있으며, "
    f"가장 많은 관객을 기록한 영화는 '{max_movie}'로 총 {max_audience:,.0f}명입니다."
)
# ==============================
# 4. 개봉일 스크린수와 총 관객의 관계
# ==============================

st.divider()
st.header("4. 개봉일 스크린수와 총 관객의 관계")

# 숫자형으로 변환
df["first_scrn"] = pd.to_numeric(df["first_scrn"], errors="coerce").fillna(0)
df["total_audi"] = pd.to_numeric(df["total_audi"], errors="coerce").fillna(0)

# 산점도
fig4 = px.scatter(
    df,
    x="first_scrn",
    y="total_audi",
    color="genre",
    hover_name="movieNm",
    title="개봉일 스크린수와 총 관객의 관계",
    labels={
        "first_scrn": "개봉일 스크린수",
        "total_audi": "총 관객 수",
        "genre": "장르"
    }
)

fig4.update_traces(
    marker=dict(size=10),
    hovertemplate=(
        "<b>%{hovertext}</b><br>"
        "개봉일 스크린수: %{x:,.0f}개<br>"
        "총 관객: %{y:,.0f}명"
        "<extra></extra>"
    )
)

fig4.update_layout(
    height=600,
    xaxis_title="개봉일 스크린수",
    yaxis_title="총 관객 수"
)

st.plotly_chart(
    fig4,
    use_container_width=True,
    key="graph4_scatter"
)

st.info(
    "💡 이 그래프로 알 수 있는 것: "
    "영화가 개봉할 때 확보한 스크린 수와 전체 기간 동안의 총 관객 수가 "
    "어떤 관계를 보이는지 비교할 수 있으며, 장르별로 영화들의 분포도 살펴볼 수 있습니다."
)
# ==============================
# 5. 장르별 총 관객 분포
# ==============================

st.divider()
st.header("5. 장르별 총 관객 분포")

# 영화가 10편 이상인 장르만 선택
genre_counts = df["genre"].value_counts()
selected_genres = genre_counts[genre_counts >= 10].index

df_box = df[df["genre"].isin(selected_genres)].copy()

# 상자 그림
fig5 = px.box(
    df_box,
    x="genre",
    y="total_audi",
    color="genre",
    points="outliers",
    hover_name="movieNm",
    title="영화가 10편 이상인 장르의 총 관객 분포",
    labels={
        "genre": "장르",
        "total_audi": "총 관객 수"
    }
)

fig5.update_traces(
    hovertemplate=(
        "<b>%{hovertext}</b><br>"
        "장르: %{x}<br>"
        "총 관객: %{y:,.0f}명"
        "<extra></extra>"
    )
)

fig5.update_layout(
    height=600,
    xaxis_title="장르",
    yaxis_title="총 관객 수",
    showlegend=False
)

st.plotly_chart(
    fig5,
    use_container_width=True,
    key="graph5_boxplot"
)

st.info(
    "💡 이 그래프로 알 수 있는 것: "
    "영화가 10편 이상인 장르를 대상으로 장르별 총 관객의 분포와 중앙값, "
    "관객 수의 차이를 비교할 수 있으며, 상자 밖의 점을 통해 해당 장르에서 "
    "특히 많은 관객을 모은 영화도 확인할 수 있습니다."
)
# ==============================
# 6. 첫 주 관객을 반영한 버블 그래프
# ==============================

st.divider()
st.header("6. 개봉일 스크린수·총 관객·첫 주 관객의 관계")

# 첫 주 관객 수를 숫자형으로 변환
df["first_week_audi"] = pd.to_numeric(
    df["first_week_audi"],
    errors="coerce"
).fillna(0)

# 버블 그래프
fig6 = px.scatter(
    df,
    x="first_scrn",
    y="total_audi",
    size="first_week_audi",
    color="genre",
    hover_name="movieNm",
    size_max=60,
    title="첫 주 관객을 반영한 영화별 버블 그래프",
    labels={
        "first_scrn": "개봉일 스크린수",
        "total_audi": "총 관객 수",
        "first_week_audi": "첫 주 관객 수",
        "genre": "장르"
    }
)

fig6.update_traces(
    hovertemplate=(
        "<b>%{hovertext}</b><br>"
        "장르: %{marker.color}<br>"
        "개봉일 스크린수: %{x:,.0f}개<br>"
        "총 관객: %{y:,.0f}명"
        "<extra></extra>"
    )
)

fig6.update_layout(
    height=650,
    xaxis_title="개봉일 스크린수",
    yaxis_title="총 관객 수"
)

st.plotly_chart(
    fig6,
    use_container_width=True,
    key="graph6_bubble"
)

st.info(
    "💡 이 그래프로 알 수 있는 것: "
    "개봉일 스크린수와 총 관객 수의 관계를 살펴보면서, "
    "버블 크기를 통해 첫 주에 많은 관객을 모은 영화도 함께 비교할 수 있습니다."
)
# ==============================
# 7. 제작 국가와 장르별 영화 구성
# ==============================

st.divider()
st.header("7. 제작 국가에서 장르로 이어지는 영화 구성")

# 제작 국가와 장르의 결측값 처리
df["nation"] = df["nation"].fillna("기타").astype(str)
df["genre"] = df["genre"].fillna("기타").astype(str)

# 선버스트 그래프
fig7 = px.sunburst(
    df,
    path=["nation", "genre"],
    title="제작 국가 → 장르별 영화 편수",
    labels={
        "nation": "제작 국가",
        "genre": "장르"
    }
)

fig7.update_traces(
    hovertemplate=(
        "<b>%{label}</b><br>"
        "영화 편수: %{value}편"
        "<extra></extra>"
    )
)

fig7.update_layout(
    height=650
)

st.plotly_chart(
    fig7,
    use_container_width=True,
    key="graph7_sunburst"
)

st.info(
    "💡 이 그래프로 알 수 있는 것: "
    "제작 국가별 영화 편수와 각 국가에서 어떤 장르의 영화가 많이 제작되었는지 "
    "전체적인 구성을 비교할 수 있습니다."
)
# ==============================
# 8. 10위권에 오래 머문 영화는 총 관객도 많은가
# ==============================

st.divider()
st.header("8. 10위권에 오래 머문 영화는 총 관객도 많은가")

# 숫자형으로 변환
df["days_in_top10"] = pd.to_numeric(
    df["days_in_top10"],
    errors="coerce"
).fillna(0)

df["total_audi"] = pd.to_numeric(
    df["total_audi"],
    errors="coerce"
).fillna(0)

# 산점도
fig8 = px.scatter(
    df,
    x="days_in_top10",
    y="total_audi",
    color="genre",
    hover_name="movieNm",
    title="10위권에 오래 머문 영화는 총 관객도 많은가",
    labels={
        "days_in_top10": "10위권에 머문 날수",
        "total_audi": "총 관객 수",
        "genre": "장르"
    }
)

fig8.update_traces(
    marker=dict(size=10),
    hovertemplate=(
        "<b>%{hovertext}</b><br>"
        "10위권에 머문 날수: %{x:,.0f}일<br>"
        "총 관객: %{y:,.0f}명"
        "<extra></extra>"
    )
)

fig8.update_layout(
    height=600,
    xaxis_title="10위권에 머문 날수",
    yaxis_title="총 관객 수"
)

st.plotly_chart(
    fig8,
    use_container_width=True,
    key="graph8_scatter"
)

st.info(
    "💡 이 그래프로 알 수 있는 것: "
    "영화가 10위권에 머문 날수와 총 관객 수 사이에 어떤 관계가 있는지 "
    "살펴볼 수 있습니다."
)
