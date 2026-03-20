import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json

# --- 페이지 설정 ---
st.set_page_config(page_title="서울 스타터: 나만의 첫 자취 명당", layout="wide", page_icon="🏠")

# --- 데이터 로드 및 전처리 ---
@st.cache_data
def get_seoul_data():
    # 앞선 보고서 기반 25개 자치구 정량 데이터
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
    df = pd.DataFrame(data)
    
    # 데이터 정규화 및 점수화 로직 (추천 알고리즘용)
    for col, high_is_good in [('평균월세', False), ('생활물가', False), ('문화공간', True), ('공원수', True)]:
        mn = df[col].min()
        mx = df[col].max()
        if high_is_good:
            df[f'score_{col}'] = (df[col] - mn) / (mx - mn)
        else:
            df[f'score_{col}'] = (mx - df[col]) / (mx - mn)
            
    # 시각화용 단순 위경도 좌표 (중심점)
    coords = {
        '강남구': [37.4959, 127.0664], '강동구': [37.5492, 127.1465], '강북구': [37.6469, 127.0147],
        '강서구': [37.5658, 126.8223], '관악구': [37.4654, 126.9436], '광진구': [37.5481, 127.0857],
        '구로구': [37.4954, 126.8581], '금천구': [37.4601, 126.9002], '노원구': [37.6544, 127.0772],
        '도봉구': [37.6659, 127.0318], '동대문구': [37.5838, 127.0507], '동작구': [37.5029, 126.9427],
        '마포구': [37.5623, 126.9088], '서대문구': [37.5820, 126.9356], '서초구': [37.4769, 127.0122],
        '성동구': [37.5506, 127.0409], '성북구': [37.6061, 127.0232], '송파구': [37.5048, 127.1145],
        '양천구': [37.5271, 126.8565], '영등포구': [37.5206, 126.9139], '용산구': [37.5311, 126.9811],
        '은평구': [37.6176, 126.9227], '종로구': [37.5991, 126.9861], '중구': [37.5579, 126.9942],
        '중랑구': [37.5954, 127.0922]
    }
    df['lat'] = df['자치구'].map(lambda x: coords[x][0])
    df['lon'] = df['자치구'].map(lambda x: coords[x][1])
    
    return df

df = get_seoul_data()

# --- 세션 상태 초기화 (클릭한 자치구 기억) ---
if 'selected_gu' not in st.session_state:
    st.session_state.selected_gu = '종로구' # 초기값

# --- 메인 화면 구성 ---
st.title("🏠 서울 스타터: 지도와 데이터로 찾는 나만의 자취 명당")
st.markdown("왼쪽 지도에서 **관심 있는 자치구를 클릭**하세요. 우측에 해당 지역의 상세 정주 여건이 나타납니다.")

col_map, col_info = st.columns([2, 1]) # 지도와 정보창 비율 2:1

# --- 왼쪽: 인터랙티브 서울 지도 (Plotly Scatter Mapbox) ---
with col_map:
    st.subheader("📍 서울시 자치구 지도")
    
    # 간단한 가중치 계산 (지도 색상용) - 사이드바 없이 메인에 간소화
    w = {'rent': 8, 'price': 5, 'culture': 7, 'park': 5}
    df['total_score'] = (df['score_평균월세'] * w['rent'] + df['score_생활물가'] * w['price'] + 
                         df['score_문화공간'] * w['culture'] + df['score_공원수'] * w['park'])
    
    # Plotly Scatter Mapbox 구현
    fig = px.scatter_mapbox(df, lat="lat", lon="lon", text="자치구", hover_name="자치구",
                            color="total_score", size="total_score",
                            color_continuous_scale=px.colors.sequential.Tealgrn, size_max=15,
                            zoom=10.5, center={"lat": 37.56, "lon": 126.98},
                            mapbox_style="carto-positron", height=600)
    
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    
    # 중요: 클릭 이벤트 등록 (streamlit >= 1.35.0 필요)
    # chart_data = st.plotly_chart(fig, use_container_width=True, on_select="rerun")
    # -> 현재 버전 제약으로 hover데이터로 대체 구현 (on_select는 최신버전 기능)
    
    # 최신 버전을 사용할 수 없는 경우를 대비한 Hover 데이터 활용 대안 UI
    select_event = st.plotly_chart(fig, use_container_width=True, on_select="rerun")

    # 클릭(또는 선택) 이벤트 처리
    if select_event and select_event.selection and select_event.selection.points:
        # 선택된 포인트의 자치구명 가져오기
        clicked_gu = select_event.selection.points[0]['hovertext']
        st.session_state.selected_gu = clicked_gu

# --- 오른쪽: 선택된 자치구 상세 특징 ---
with col_info:
    st.subheader(f"🔍 {st.session_state.selected_gu} 상세 리포트")
    
    if st.session_state.selected_gu:
        gu_data = df[df['자치구'] == st.session_state.selected_gu].iloc[0]
        
        # 1. 항목별 수치 (Metric)
        st.metric(label="📊 종합 정주 점수", value=f"{gu_data['total_score']:.1f} / 25.0")
        
        c1, c2 = st.columns(2)
        with c1:
            st.write(f"💰 **예상 월세:** `{gu_data['평균월세']}만원`")
            st.write(f"🛒 **생활 물가:** `{gu_data['생활물가']:,}원`")
        with c2:
            st.write(f"🎨 **문화공간:** `{gu_data['문화공간']}개`")
            st.write(f"🌳 **공원 수:** `{gu_data['공원수']}개`")
            
        st.divider()
        
        # 2. 지하철 호선 요약
        st.write("🚇 **지나가는 핵심 호선:**")
        lines = gu_data['지하철호선'].split(',')
        cols_lines = st.columns(len(lines))
        for i, line in enumerate(lines):
            cols_lines[i].markdown(f"**[{line}호선]**")
            
        st.divider()
        
        # 3. 방사형 차트 (Radar Chart)로 밸런스 시각화
        categories = ['월세 가성비', '물가 가성비', '문화 인프라', '녹지 인프라']
        # 가성비 지표는 스코어 그대로 사용
        scores = [gu_data['score_평균월세'], gu_data['score_생활물가'], 
                  gu_data['score_문화공간'], gu_data['score_공원수']]
        
        fig_radar = go.Figure()
        fig_radar.add_trace(go.Scatterpolar(
            r=scores, theta=categories, fill='toself', name=gu_data['자치구'],
            line_color='#1f77b4'
        ))
        fig_radar.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 1])), 
                                margin={"r":30,"t":30,"l":30,"b":30}, height=300)
        st.plotly_chart(fig_radar, use_container_width=True, config={'displayModeBar': False})
        
    else:
        st.info("지도에서 자치구 원형을 클릭하시면 상세 정보가 여기에 표시됩니다.")

# --- 하단 전체 데이터 비교 (선택 사항) ---
with st.expander("📊 서울시 전체 데이터 비교 테이블 보기"):
    st.dataframe(df[['자치구', '지하철호선', '평균월세', '생활물가', '문화공간', '공원수', 'total_score']].sort_values('total_score', ascending=False), 
                 use_container_width=True, hide_index=True)
