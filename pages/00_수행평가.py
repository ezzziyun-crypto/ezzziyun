import streamlit as st
import pandas as pd
import plotly.express as px

# 1. 데이터 로드 및 캐싱 (Streamlit Cloud 환경 최적화)
# @st.cache_data를 사용하여 파일 로딩 속도를 최적화합니다.
@st.cache_data
def load_data(file_path):
    """
    'm.csv' 파일을 로드하고 초기 데이터 처리를 수행합니다.
    """
    try:
        # 파일이 같은 디렉토리에 있다고 가정하고 로드합니다.
        df = pd.read_csv(file_path)
        # 필요한 경우 컬럼명 정리 및 데이터 타입 변환을 여기에 추가할 수 있습니다.
        return df
    except FileNotFoundError:
        st.error("⚠️ 'm.csv' 파일을 찾을 수 없습니다. 파일을 앱 디렉토리에 넣어주세요.")
        return pd.DataFrame()

# ==============================================================================
# 메인 Streamlit 애플리케이션 시작
# ==============================================================================

# 2. 데이터 로드
DATA_FILE = 'm.csv'
df = load_data(DATA_FILE)

st.set_page_config(layout="wide")
st.title("🏥 지역별 보건의료기관 유형 분석 대시보드")
st.markdown("---")

if not df.empty:
    
    # 3. 사이드바에 지역 선택 위젯 구현
    st.sidebar.header("🗺️ 분석 지역 선택")
    
    # 고유한 '시도' 리스트를 가져와 정렬
    all_sidos = sorted(df['시도'].unique().tolist())
    
    selected_sido = st.sidebar.selectbox(
        "분석할 광역 지역(시도)을 선택하세요.",
        all_sidos
    )
    
    # 4. 데이터 필터링 및 기관 유형별 집계
    
    # 선택된 지역으로 데이터 필터링
    filtered_df = df[df['시도'] == selected_sido]
    
    # '기관유형'별 기관 수 집계
    type_counts = filtered_df['기관유형'].value_counts().reset_index()
    type_counts.columns = ['기관유형', '기관_수']
    
    # 기관 수 기준 내림차순 정렬 (차트 순서를 위해)
    type_counts = type_counts.sort_values(by='기관_수', ascending=False).reset_index(drop=True)

    # 5. Plotly 그래프 생성 및 요구사항 색상 설정
    
    if not type_counts.empty:
        
        # 1등(최대 기관 수) 기관 유형 식별
        top_type = type_counts.iloc[0]['기관유형']
        
        # 색상 설정 로직: 1등은 'red', 나머지는 파란색 그라데이션 느낌
        num_bars = len(type_counts)
        num_other_bars = num_bars - 1
        
        # Plotly의 Blues_r(역순 파란색) 시퀀스에서 필요한 만큼 추출하여 그라데이션 느낌 부여
        # 상위권일수록 진한 파랑, 하위권일수록 연한 파랑으로 설정하기 위해 Blues_r을 사용
        if num_other_bars > 0:
             # 파란색 그라데이션을 낮은 순위부터 순서대로 적용 (진한 파랑 -> 연한 파랑)
             blue_gradient_colors = px.colors.sequential.Blues_r[:num_other_bars]
        else:
             blue_gradient_colors = []
        
        # 최종 색상 리스트 생성
        colors = []
        j = 0
        for index, row in type_counts.iterrows():
            if row['기관유형'] == top_type:
                colors.append('red') # 1등은 빨간색
            else:
                if j < len(blue_gradient_colors):
                    colors.append(blue_gradient_colors[j])
                else:
                    colors.append('#4c78a8') # 그라데이션이 부족할 경우 대비 기본 파란색
                j += 1
                
        # Plotly Bar Chart 생성 (인터랙티브)
        fig = px.bar(
            type_counts,
            x='기관유형',
            y='기관_수',
            title=f"<b>{selected_sido}</b> 지역 보건의료기관 유형별 분포",
            labels={'기관유형': '기관 유형', '기관_수': '기관 수'},
            template='plotly_white', # 깔끔한 템플릿 사용
            text='기관_수' # 막대 위에 값 표시
        )
        
        # 막대 색상 업데이트
        fig.update_traces(
            marker_color=colors,
            textposition='outside' # 텍스트를 막대 바깥에 표시
        )
        
        # 레이아웃 조정 (제목 중앙 정렬 및 크기)
        fig.update_layout(
            xaxis_title="보건의료기관 유형",
            yaxis_title="기관 수 (개)",
            title_font_size=20,
            title_x=0.5, 
            hovermode="x unified", # 호버 시 x축 정보 통일
            uniformtext_minsize=8, 
            uniformtext_mode='hide',
            showlegend=False
        )
        
        # 6. Streamlit에 그래프 표시
        st.header(f"📈 {selected_sido} 기관 유형 비율 분석 결과")
        st.plotly_chart(fig, use_container_width=True)
        
        # 데이터 테이블 표시
        st.markdown("### 🔍 상세 데이터 테이블")
        st.dataframe(type_counts, use_container_width=True)
    
    else:
        st.warning(f"선택하신 {selected_sido} 지역에 해당하는 기관 데이터가 없습니다.")
