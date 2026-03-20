import streamlit as st
import pandas as pd
import plotly.express as px
from streamlit_folium import folium_static
import folium

# --- 페이지 설정 ---
st.set_page_config(page_title="서울 스타터: 첫 자취 명당 찾기", layout="wide")

# --- 데이터 로드 (분석된 결과 요약본) ---
@st.cache_data
def load_data():
    # 앞선 분석 결과를 바탕으로 한 자치구별 통합 데이터프레임 구성
    data = {
        '자치구': ['강남구', '강동구', '강북구', '강서구', '관악구', '광진구', '구로구', '금천구', '노원구', '도봉구', 
                  '동대문구', '동작구', '마포구', '서대문구', '서초구', '성동구', '성북구', '송파구', '양천구', '영등포구', 
                  '용산구', '은평구', '종로구', '중구', '중랑구'],
        '지하철호선': ['2,3,7,9', '5,8,9', '4', '5', '2', '2,5,7', '2,7', '7', '4,6,7', '4,7', 
                    '1,2,5', '2,4,7', '2,5,6', '2,3,5', '2,3,4,7', '2,3,5', '4,6', '2,3,5,8,9', '2,5', '2,5,7', 
                    '4,6', '3,6', '1,3,4,5,6', '1,2,3,4,5,6', '6,7'],
        '생활물가': [7361, 5935, 6424, 6165, 6629, 7265, 6021, 6619, 6837, 6338, 6384, 6378, 6705, 6735, 6680, 6599, 6973, 7098, 6593, 6070, 6978, 6388, 6702, 6614, 6687],
        '문화공간': [115, 24, 23, 25, 21, 33, 40, 20, 33, 33, 39, 32, 53, 36, 62, 33, 62, 62, 27, 27, 66, 33, 250, 83, 19],
        '공원수': [7, 7, 3, 10, 2, 2, 4, 4, 2, 6, 4, 7, 5, 4, 6, 5, 3, 7, 5, 5, 2, 7, 12, 6, 5],
        '평균월세': [95, 72, 62, 68, 60, 78, 63, 58, 60, 55, 68, 75, 85, 70, 92, 80, 65, 88, 70, 75, 82, 63, 75, 78, 60]
    }
    return pd.DataFrame(data)

df = load_data()

# --- 사이드바: 유저 취향 설정 ---
st.sidebar.header("🔍 나의 자취 조건 설정")
st.sidebar.write("본인에게 중요한 항목의 우선순위를 정해주세요.")

# 가중치 설정 (0~10)
w_rent = st.sidebar.slider("저렴한 월세 중요도", 0, 10, 8)
w_price = st.sidebar.slider("저렴한 생활물가 중요도", 0, 10, 5)
w_culture = st.sidebar.slider("문화생활 인프라 중요도", 0, 10, 6)
w_park = st.sidebar.slider("녹지(공원) 중요도", 0, 10, 4)

# 선호 호선 선택
target_lines = st.sidebar.multiselect("꼭 지나야 하는 지하철 호선", 
                                     ['1', '2', '3', '4', '5', '6', '7', '8', '9'],
                                     default=['2'])

# --- 메인 화면 ---
st.title("🏠 서울 스타터: 첫 자취 명당 찾기")
st.markdown("처음 서울 생활을 시작하는 당신을 위해, 공공데이터 기반으로 최적의 자치구를 추천합니다.")

# --- 추천 알고리즘 ---
# 데이터 정규화 (0~1 사이 값으로 변환하여 계산)
df_norm = df.copy()
# 낮을수록 좋은 지표 (월세, 물가) -> (최대값 - 현재값) / (최대값 - 최소값)
df_norm['score_rent'] = (df['평균월세'].max() - df['평균월세']) / (df['평균월세'].max() - df['평균월세'].min())
df_norm['score_price'] = (df['생활물가'].max() - df['생활물가']) / (df['생활물가'].max() - df['생활물가'].min())
# 높을수록 좋은 지표 (문화, 공원) -> (현재값 - 최소값) / (최대값 - 최소값)
df_norm['score_culture'] = (df['문화공간'] - df['문화공간'].min()) / (df['문화공간'].max() - df['문화공간'].min())
df_norm['score_park'] = (df['공원수'] - df['공원수'].min()) / (df['공원수'].max() - df['공원수'].min())

# 최종 점수 계산
df['final_score'] = (df_norm['score_rent'] * w_rent + 
                    df_norm['score_price'] * w_price + 
                    df_norm['score_culture'] * w_culture + 
                    df_norm['score_park'] * w_park)

# 지하철 필터링 (선택한 호선이 하나라도 포함된 구)
if target_lines:
    df = df[df['지하철호선'].apply(lambda x: any(line in x for line in target_lines))]

# 결과 정렬
recommendations = df.sort_values(by='final_score', ascending=False).head(5)

# --- 결과 출력 ---
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("🌟 당신을 위한 추천 Top 3")
    for i, row in enumerate(recommendations.iloc[:3].itertuples()):
        with st.expander(f"{i+1}위: {row.자치구}", expanded=True):
            st.write(f"🚇 **지나가는 호선:** {row.지하철호선}호선")
            st.write(f"💰 **평균 월세:** 약 {row.평균월세}만원")
            st.write(f"🛒 **생활 물가:** 평균 {format(int(row.생활물가), ',')}원")
            st.write(f"🌳 **공원 수:** {row.공원수}개 / 🎨 **문화공간:** {row.문화공간}개")

with col2:
    st.subheader("📊 추천 지역 비교 (항목별)")
    fig = px.bar(recommendations, x='자치구', y=['평균월세', '공원수', '문화공간'],
                 title="상위 추천 지역 인프라 비교", barmode='group')
    st.plotly_chart(fig, use_container_width=True)

# --- 하단 상세 분석 ---
st.divider()
st.subheader("📍 서울시 전체 지역 분포 확인")
tab1, tab2 = st.tabs(["물가 vs 월세 산점도", "자치구별 인프라 현황"])

with tab1:
    fig_scatter = px.scatter(df, x='평균월세', y='생활물가', text='자치구', size='문화공간', color='공원수',
                             labels={'평균월세': '평균 월세 (만원)', '생활물가': '평균 생필품 물가 (원)'},
                             title="월세와 물가 비례 관계 (원의 크기: 문화공간 수)")
    st.plotly_chart(fig_scatter, use_container_width=True)

with tab2:
    st.dataframe(df[['자치구', '지하철호선', '평균월세', '생활물가', '문화공간', '공원수']].sort_values('평균월세'), 
                 use_container_width=True)

st.caption("본 데이터는 서울시 공공데이터 및 최근 부동산 시장 평균치를 기반으로 작성되었습니다.")
