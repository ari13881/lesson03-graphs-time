import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

DATA_URL = (
    "https://raw.githubusercontent.com/greatsong/modudata/main/data/kobis_daily.csv"
)

st.set_page_config(page_title="영화 데이터 그래프 도감 1 - 시간", layout="wide")


# ---------------------------------------------------------------------------
# 데이터 불러오기
# ---------------------------------------------------------------------------
@st.cache_data(show_spinner="데이터를 불러오는 중...")
def load_data() -> pd.DataFrame:
    df = pd.read_csv(DATA_URL)
    df.columns = df.columns.str.strip()
    # 20240101 같은 여덟 자리 숫자를 진짜 날짜(datetime)로 변환
    df["날짜"] = pd.to_datetime(df["날짜"].astype(str), format="%Y%m%d")
    return df.sort_values(["날짜", "순위"]).reset_index(drop=True)


def show_insight(text: str) -> None:
    """그래프 아래에 '이 그래프로 알 수 있는 것' 한 문장을 보여 주는 자리."""
    st.markdown(f"💡 **이 그래프로 알 수 있는 것:** {text}")


# ---------------------------------------------------------------------------
# 구역 1. 영화별 일관객 변화
# ---------------------------------------------------------------------------
def section_daily_audience(df: pd.DataFrame) -> None:
    st.header("구역 1. 영화별 일관객 변화")

    # 일관객 합계가 큰 영화부터 나열 (첫 번째가 기본 선택)
    movies = (
        df.groupby("영화명")["일관객"].sum().sort_values(ascending=False).index.tolist()
    )
    movie = st.selectbox("영화를 골라 보세요", movies, key="sec1_movie")

    movie_df = df[df["영화명"] == movie].sort_values("날짜")

    fig = px.line(movie_df, x="날짜", y="일관객", markers=True, title=f"{movie} - 날짜별 일관객")
    fig.update_traces(
        hovertemplate="날짜: %{x|%Y-%m-%d}<br>일관객: %{y:,}명<extra></extra>"
    )
    fig.update_layout(
        xaxis_title="날짜",
        yaxis_title="일관객(명)",
        hovermode="closest",
    )
    st.plotly_chart(fig, use_container_width=True)

    # ✏️ 아래 문구를 원하는 한 문장으로 바꿔 쓰세요.
    show_insight("여기에 이 그래프로 알 수 있는 것을 한 문장으로 적어 주세요.")


# ---------------------------------------------------------------------------
# 구역 2. 일관객 합계 상위 5편 비교
# ---------------------------------------------------------------------------
def section_top5_compare(df: pd.DataFrame) -> None:
    st.header("구역 2. 일관객 합계 상위 5편 비교")

    # 이 기간 일관객 합계가 가장 큰 5편 (큰 순서)
    top5 = (
        df.groupby("영화명")["일관객"].sum().sort_values(ascending=False).head(5).index.tolist()
    )
    top_df = df[df["영화명"].isin(top5)].sort_values("날짜")

    fig = px.line(
        top_df,
        x="날짜",
        y="일관객",
        color="영화명",
        category_orders={"영화명": top5},  # 범례 순서 = 합계 순위
        title="상위 5편 - 날짜별 일관객",
    )
    fig.update_traces(
        hovertemplate=(
            "%{fullData.name}<br>날짜: %{x|%Y-%m-%d}<br>일관객: %{y:,}명<extra></extra>"
        )
    )
    fig.update_layout(
        xaxis_title="날짜",
        yaxis_title="일관객(명)",
        legend_title_text="영화 (클릭하면 켜고 끔)",
        hovermode="closest",
    )
    st.plotly_chart(fig, use_container_width=True)

    # ✏️ 아래 문구를 원하는 한 문장으로 바꿔 쓰세요.
    show_insight("여기에 이 그래프로 알 수 있는 것을 한 문장으로 적어 주세요.")


# ---------------------------------------------------------------------------
# 구역 3. 날짜별 10위권 일관객 합계
# ---------------------------------------------------------------------------
def section_daily_total(df: pd.DataFrame) -> None:
    st.header("구역 3. 날짜별 10위권 일관객 합계")

    # 날짜별로 그날 10위권 일관객을 모두 더함
    daily = df.groupby("날짜", as_index=False)["일관객"].sum().sort_values("날짜")
    # 합계가 가장 컸던 3일
    top3 = daily.nlargest(3, "일관객").sort_values("날짜")

    fig = px.area(daily, x="날짜", y="일관객", title="날짜별 10위권 일관객 합계")
    fig.update_traces(
        hovertemplate="날짜: %{x|%Y-%m-%d}<br>합계: %{y:,}명<extra></extra>"
    )

    # 합계 상위 3일을 점으로 찍고 날짜를 적음
    fig.add_trace(
        go.Scatter(
            x=top3["날짜"],
            y=top3["일관객"],
            mode="markers+text",
            text=top3["날짜"].dt.strftime("%Y-%m-%d"),
            textposition="top center",
            cliponaxis=False,
            marker=dict(size=11, color="crimson", line=dict(width=1, color="white")),
            name="합계 상위 3일",
            hovertemplate="날짜: %{x|%Y-%m-%d}<br>합계: %{y:,}명<extra></extra>",
        )
    )
    fig.update_layout(
        xaxis_title="날짜",
        yaxis_title="10위권 일관객 합계(명)",
        showlegend=False,
        hovermode="closest",
    )
    # 위쪽 날짜 글자가 잘리지 않도록 여유를 둠
    fig.update_yaxes(range=[0, daily["일관객"].max() * 1.15])
    st.plotly_chart(fig, use_container_width=True)

    # ✏️ 아래 문구를 원하는 한 문장으로 바꿔 쓰세요.
    show_insight("여기에 이 그래프로 알 수 있는 것을 한 문장으로 적어 주세요.")


# ---------------------------------------------------------------------------
# 앞으로 추가할 구역은 위처럼 함수를 하나 만들고,
# 아래 main()에 호출을 한 줄 추가하면 됩니다.
# 예) def section_xxx(df): ...
# ---------------------------------------------------------------------------


def main() -> None:
    st.title("영화 데이터 그래프 도감 1 - 시간")

    try:
        df = load_data()
    except Exception as e:
        st.error(f"데이터를 불러오지 못했어요: {e}")
        st.stop()

    section_daily_audience(df)
    st.divider()

    section_top5_compare(df)
    st.divider()

    section_daily_total(df)
    st.divider()

    # section_xxx(df)   # ← 다음 구역은 여기에 추가
    # st.divider()


main()

