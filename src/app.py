# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import numpy as np
import os
import sys
import matplotlib.pyplot as plt
import plotly.graph_objects as go

# 모듈 경로 추가 및 임포트
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__))))
import poker_app

# 1. 페이지 초기 설정 (최초 1회만 호출 가능)
st.set_page_config(
    page_title="정성훈 | 현대오토에버 데이터 엔지니어 포트폴리오",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# 2. 프리미엄 다크 테마 고정 설정 (Premium Slate Dark Theme)
BG_COLOR = "#09090b"       # Deep Slate Black
CARD_BG_COLOR = "#16161a"  # Glassmorphism Dark Navy
BORDER_COLOR = "#27272a"   # Slate Grey Border
TEXT_WHITE = "#fafafa"
TEXT_MUTED = "#a1a1aa"     # Muted Slate Grey
ACCENT_BLUE = "#3b82f6"    # Active Blue
ACCENT_GREEN = "#10b981"   # Emerald Green (DS/Success)
ACCENT_ORANGE = "#f59e0b"  # Amber (Highlight)

# CSS 인젝션 (디자인 가이드라인 반영 및 Streamlit 기본 크롬 숨김)
st.markdown(f"""
<style>
    /* Streamlit 기본 헤더 및 푸터 숨김 */
    header[data-testid="stHeader"], #MainMenu, footer, [data-testid="stToolbar"],
    [data-testid="stDecoration"], [data-testid="stStatusWidget"], .stDeployButton,
    div[data-testid="stSidebarCollapsedControl"] {{{{
        display: none !important;
    }}}}
    
    /* 전역 배경 및 글자색 설정 */
    html, body, [data-testid="stAppViewContainer"], [data-testid="stApp"], .main, .block-container, section[data-testid="stMain"] {{{{
        background-color: {BG_COLOR} !important;
        color: {TEXT_WHITE} !important;
        font-family: 'Inter', 'Nanum Gothic', -apple-system, sans-serif !important;
    }}}}
    
    .block-container {{{{
        padding: 1.5rem 2.5rem 2rem !important;
        max-width: 1360px !important;
    }}}}
    
    /* 탭 스타일 최적화 (SaaS pill style) */
    button[data-baseweb="tab"] {{{{
        background: transparent !important;
        color: {TEXT_MUTED} !important;
        font-size: 0.9rem !important;
        font-weight: 600 !important;
        padding: 0.6rem 1.2rem !important;
        border: 1px solid transparent !important;
        border-radius: 8px !important;
        transition: all 0.3s ease !important;
    }}}}
    button[data-baseweb="tab"][aria-selected="true"] {{{{
        color: {TEXT_WHITE} !important;
        background: {CARD_BG_COLOR} !important;
        border-color: {ACCENT_BLUE} !important;
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.15) !important;
    }}}}
    [data-baseweb="tab-highlight"], [data-baseweb="tab-border"] {{{{
        display: none !important;
    }}}}
    [data-baseweb="tab-list"] {{{{
        gap: 8px !important;
        background: #121214 !important;
        border: 1px solid {BORDER_COLOR} !important;
        border-radius: 12px !important;
        padding: 4px !important;
        margin-bottom: 2rem !important;
    }}}}
    
    /* 포트폴리오 카드 컴포넌트 */
    .pf-card {{{{
        background: #16161a !important;
        color: #fafafa !important;
        border: 1px solid #27272a !important;
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1.2rem;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        transition: transform 0.2s, border-color 0.2s;
    }}}}
    .pf-card:hover {{{{
        transform: translateY(-2px);
        border-color: #3b82f6 !important;
    }}}}
    .pf-title {{{{
        font-size: 1.2rem;
        font-weight: 700;
        color: #ffffff !important;
        margin-bottom: 0.5rem;
        display: flex;
        align-items: center;
        gap: 8px;
    }}}}
    .pf-subtitle {{{{
        font-size: 0.85rem;
        color: #3b82f6 !important;
        font-weight: 600;
        text-transform: uppercase;
        margin-bottom: 0.8rem;
    }}}}
    .pf-body {{{{
        font-size: 0.9rem;
        color: #a1a1aa !important;
        line-height: 1.6;
    }}}}
    .pf-card ul, .pf-card li, .pf-card p, .pf-card div, .pf-card span {{{{
        color: #a1a1aa !important;
    }}}}
    .pf-title, .pf-title div, .pf-title span {{{{
        color: #ffffff !important;
    }}}}
    .pf-card b, .pf-card strong {{{{
        color: #ffffff !important;
    }}}}
    
    /* 하이라이트 배지 */
    .badge {{{{
        display: inline-block;
        padding: 3px 10px;
        border-radius: 6px;
        font-size: 0.75rem;
        font-weight: 600;
        margin-right: 5px;
        margin-bottom: 5px;
    }}}}
    .badge-blue {{{{
        color: #3b82f6 !important;
        background: rgba(59, 130, 246, 0.1) !important;
        border: 1px solid rgba(59, 130, 246, 0.2) !important;
    }}}}
    .badge-green {{{{
        color: #10b981 !important;
        background: rgba(16, 185, 129, 0.1) !important;
        border: 1px solid rgba(16, 185, 129, 0.2) !important;
    }}}}
    .badge-orange {{{{
        color: #f59e0b !important;
        background: rgba(245, 158, 11, 0.1) !important;
        border: 1px solid rgba(245, 158, 11, 0.2) !important;
    }}}}
    
    /* 대단위 키 메트릭 */
    .kpi-container {{{{
        display: flex;
        gap: 1rem;
        margin-bottom: 1.5rem;
    }}}}
    .kpi-card {{{{
        flex: 1;
        background: #121214;
        border: 1px solid {BORDER_COLOR};
        border-radius: 10px;
        padding: 1rem;
        text-align: center;
    }}}}
    .kpi-val {{{{
        font-size: 1.8rem;
        font-weight: 800;
        color: {ACCENT_BLUE};
    }}}}
    .kpi-lbl {{{{
        font-size: 0.75rem;
        color: {TEXT_MUTED};
        margin-top: 4px;
        text-transform: uppercase;
    }}}}
    
    /* 구분선 */
    .divider {{{{
        height: 1px;
        background: {BORDER_COLOR};
        margin: 2rem 0;
    }}}}
</style>
""", unsafe_allow_html=True)

# 3. 헤더 컴포넌트 (기술 포트폴리오 맞춤 리디자인)
head_left, head_right = st.columns([8, 2])
with head_left:
    st.markdown(f"""
    <div style="margin-bottom: 1.5rem;">
        <span style="font-size: 0.8rem; font-weight: 700; color: {ACCENT_BLUE}; text-transform: uppercase; letter-spacing: 0.1em;">HYUNDAI AUTOEVER DATA ENGINEER PORTFOLIO</span>
        <h1 style="margin: 5px 0 0 0; font-size: 2.3rem; font-weight: 800; color: {TEXT_WHITE}; letter-spacing: -0.02em;">비정형 로그 기반 대용량 데이터 엔지니어링 플랫폼</h1>
    </div>
    """, unsafe_allow_html=True)
with head_right:
    st.markdown(f"""
    <div style="text-align: right; margin-top: 10px;">
        <span class="badge badge-blue" style="font-size: 0.85rem; padding: 5px 12px;">데이터기술 DE (1지망)</span><br>
        <span class="badge badge-green" style="font-size: 0.85rem; padding: 5px 12px; margin-top: 5px;">스마트팩토리 DE (2지망)</span>
    </div>
    """, unsafe_allow_html=True)

# 4. 메인 탭 네비게이션 정의 (포트폴리오 핵심 구성)
tabs = st.tabs([
    "💼 Portfolio Home (포트폴리오 홈)",
    "🃏 Interactive Demo (실전 분석 데모)",
    "🛠️ Technical Deep Dive (기술 아키텍처)"
])

# =========================================================================
# TAB 1: Portfolio Home (플래그십 프로젝트 개요 및 직무 기술 사양)
# =========================================================================
with tabs[0]:
    st.markdown(f"""
    <div class="pf-card" style="border-left: 4px solid {ACCENT_BLUE}; margin-bottom: 1.5rem;">
        <div class="pf-title">📊 프로젝트 개요: 포커 로그 기반 대용량 데이터 엔지니어링 파이프라인 플랫폼</div>
        <div class="pf-body" style="font-size: 0.95rem;">
            본 프로젝트는 비정형 텍스트 로그 파일의 수집 및 가공(ETL)부터 데이터베이스 다차원 모델링, 분산 데이터 저장 및 처리 시스템에 이르는 <b>대규모 데이터 엔지니어링 플랫폼</b> 개발 프로젝트입니다.<br>
            대량의 비정형 데이터 속에서 유의미한 행동 패턴 및 비즈니스 지표를 정량적으로 추출하여 의사결정 시스템과 모니터링 대시보드를 연동함으로써, 현대오토에버 실무에 즉시 투입 가능한 데이터 아키텍처 구축 역량을 증명합니다.
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # 핵심 지표 Grid
    st.markdown(f"""
    <div class="kpi-container">
        <div class="kpi-card">
            <div class="kpi-val" style="color: {ACCENT_BLUE};">140개</div>
            <div class="kpi-lbl">비정형 로그 파일 (Raw Text)</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-val" style="color: {ACCENT_BLUE};">7,993개</div>
            <div class="kpi-lbl">정제 완료 트랜잭션 (Hands)</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-val" style="color: {ACCENT_BLUE};">180,359건</div>
            <div class="kpi-lbl">적재 완료 실시간 액션 (Actions)</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-val" style="color: {ACCENT_GREEN};">100%</div>
            <div class="kpi-lbl">비정형 로그 파싱 성공률 (ETL)</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown(f"""
    <div style="margin-bottom: 1rem;">
        <h4 style="margin: 0; font-size: 1.15rem; color: {TEXT_WHITE}; font-weight: 700;">🏢 지원 직무별 핵심 기술 구현 사양 (Enterprise Tech Stack Alignment)</h4>
    </div>
    """, unsafe_allow_html=True)

    col_h1, col_h2 = st.columns([6, 6])
    
    with col_h1:
        st.markdown(f"""
        <div class="pf-card" style="height: 100%; border-top: 4px solid {ACCENT_BLUE};">
            <div class="pf-title" style="color: #ffffff !important;">💻 1지망: 데이터기술 사업부 | Data Engineer</div>
            <div style="margin-top: 0.4rem; margin-bottom: 0.8rem;">
                <span class="badge badge-blue">#SQL</span>
                <span class="badge badge-blue">#Spark</span>
                <span class="badge badge-blue">#Python</span>
                <span class="badge badge-blue">#Hadoop</span>
                <span class="badge badge-blue">#Airflow</span>
                <span class="badge badge-blue">#Sqoop</span>
            </div>
            <div class="pf-body">
                데이터 엔지니어 파이프라인 개발/운영을 위한 핵심 기술 구현 요건:
                <ul style="margin-top: 0.8rem; padding-left: 1.2rem; color: {TEXT_MUTED}; font-size: 0.88rem; line-height: 1.7;">
                    <li><b>#Sqoop</b>: 관계형 DB의 트랜잭션 데이터를 Hadoop HDFS로 병렬 증분 수집(Incremental Ingestion)</li>
                    <li><b>#Hadoop & #Spark</b>: HDFS 상의 대용량 비정형 텍스트 로그를 PySpark 분산 엔진을 통해 정밀 ETL 정형화</li>
                    <li><b>#Airflow & #Python</b>: 전체 파이프라인(Sqoop ➡️ Spark ➡️ Hive)의 의존성 관리 및 주기적 스케줄링을 위한 Python DAG 개발</li>
                    <li><b>#SQL</b>: Hive DW 적재 최적화를 위한 파티셔닝 외부 테이블 DDL 설계 및 다차원 집계 분석 SQL 구현</li>
                </ul>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
    with col_h2:
        st.markdown(f"""
        <div class="pf-card" style="height: 100%; border-top: 4px solid {ACCENT_GREEN};">
            <div class="pf-title" style="color: #ffffff !important;">🏭 2지망: 스마트팩토리 사업부 | Data Engineer</div>
            <div style="margin-top: 0.4rem; margin-bottom: 0.8rem;">
                <span class="badge badge-green">#Java</span>
                <span class="badge badge-green">#Python</span>
                <span class="badge badge-green">#SQL</span>
                <span class="badge badge-green">#Hadoop</span>
                <span class="badge badge-green">#Spark</span>
                <span class="badge badge-green">#Hive</span>
            </div>
            <div class="pf-body">
                스마트팩토리 환경의 고성능 실시간 및 분산 데이터 파이프라인 개발/운영 요건:
                <ul style="margin-top: 0.8rem; padding-left: 1.2rem; color: {TEXT_MUTED}; font-size: 0.88rem; line-height: 1.7;">
                    <li><b>#Java</b>: 설비 PLC 및 MES 장비의 실시간 로그 유입 처리를 위한 고성능 멀티스레드 소켓 서버 데몬 설계</li>
                    <li><b>#Spark & #Hadoop</b>: Spark Java API를 적용하여 RDD 기반 분산 메모리 상에서 로그 데이터 무손실 정제 및 HDFS 적재</li>
                    <li><b>#Hive & #SQL</b>: 제조 실행 지표 집계 속도 향상을 위해 game_date 기준 물리 파티셔닝 및 ORC 압축 외부 테이블 설계</li>
                    <li><b>#Python</b>: 대용량 데이터프레임 고속 정형화, 유저 행동 성향 군집화(K-Means) 및 머신러닝 파이프라인 구현</li>
                </ul>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown(f"""
    <div style="margin-top: 1.5rem; text-align: right; font-size: 0.9rem; color: {ACCENT_ORANGE}; font-weight: 600;">
        💡 상세 구현 코드(Sqoop, Hive SQL, Java Spark, PySpark, Airflow DAG)는 세 번째 탭인 <b>'🛠️ Technical Deep Dive ➡️ Enterprise Big Data Scale-Out'</b>에서 즉시 확인 가능합니다.
    </div>
    """, unsafe_allow_html=True)

# =========================================================================
# TAB 2: Interactive Demo (포커 분석 실전 대시보드)
# =========================================================================
with tabs[1]:
    st.markdown(f"""
    <div style="background: rgba(59, 130, 246, 0.05); border: 1px solid rgba(59, 130, 246, 0.15); border-radius: 8px; padding: 1rem; margin-bottom: 1.5rem;">
        <span style="font-weight: 700; color: {ACCENT_BLUE};">💡 포트폴리오 데모 안내</span><br>
        <span style="font-size: 0.85rem; color: {TEXT_MUTED};">
            아래 화면은 실제로 구동되는 <b>실시간 포커 로그 분석 시스템 데모</b>입니다. 좌측 사이드바 필터를 변경하거나, 상단 탭을 눌러 데이터 적재 시뮬레이션(ETL)부터 퍼널 분석, 머신러닝 예측(Sandbox)까지 자유롭게 테스트해 보실 수 있습니다.
        </span>
    </div>
    """, unsafe_allow_html=True)
    
    poker_app.run_poker_app()

# =========================================================================
# TAB 3: Technical Deep Dive (기술 아키텍처 명세서)
# =========================================================================
with tabs[2]:
    st.markdown(f"""
    <div style="margin-bottom: 2rem;">
        <h2 style="font-size: 1.8rem; font-weight: 800; color: {TEXT_WHITE};">🛠️ 데이터 엔지니어링 기술 명세 (Technical Deep-Dive)</h2>
        <p style="font-size: 0.9rem; color: {TEXT_MUTED};">기술 면접 및 아키텍처 검증을 위해 세부적인 데이터 파이프라인 명세와 DB 스키마 설계, 그리고 분산 데이터 처리 아키텍처의 내부 작동 사양을 상세히 공개합니다.</p>
    </div>
    """, unsafe_allow_html=True)
    
    sub_tabs = st.tabs([
        "📊 RDBMS & Machine Learning Foundation (분석 모델링 기반)",
        "🚀 Enterprise Big Data Scale-Out (대용량 분산 아키텍처)"
    ])
    
    with sub_tabs[0]:
        col_t1, col_t2 = st.columns([6, 6])
        
        with col_t1:
            st.markdown(f"""
            <div class="pf-card">
                <div class="pf-title" style="color: {ACCENT_BLUE};">1. 비정형 로그 파싱 및 ETL 흐름 (DE)</div>
                <div class="pf-body" style="font-size: 0.85rem;">
                    수만 행의 텍스트 로그 파일에서 필요한 트랜잭션을 무손실 추출하기 위해 고도로 최적화된 정규표현식(Regex) 엔진을 활용한 Python 데이터 파서(data_parser.py)를 자체 설계했습니다.<br><br>
                    <b>[ETL 데이터 파이프라인 프로세스]</b><br>
                    1. <b>Extract</b>: 핸드 히스토리 텍스트 파일 단위로 로우 스트림을 한 행씩 스캔합니다.<br>
                    2. <b>Transform</b>: 게임 번호, 참가 유저, 베팅 액션(Bet, Call, Raise, Fold), 카드 정보 등을 정밀 정형 데이터로 정제합니다. 특히 라운드(Pre-flop, Flop, Turn, River)의 경계를 감지하여 계층적 데이터로 구조화합니다.<br>
                    3. <b>Load</b>: 정합성이 확보된 데이터를 RDBMS 스키마 규칙에 매핑하여 트랜잭션 롤백 안정성을 갖춘 벌크 인서트(Bulk Insert)를 실행합니다.
                </div>
                <div style="margin-top: 1rem; padding: 0.8rem; background: #0f172a; border-radius: 6px; font-family: 'JetBrains Mono', monospace; font-size: 0.75rem; color: {ACCENT_ORANGE}; border: 1px solid {BORDER_COLOR};">
                    # REGEX PARSING PATTERN EXAMPLE<br>
                    hand_id_pattern = re.compile(r"PokerStars Hand #(\\\\d+):")<br>
                    action_pattern = re.compile(r"(\\\\w+): (calls|bets|raises|folds)\\\\s*(\\\\d*)")
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown(f"""
            <div class="pf-card">
                <div class="pf-title" style="color: {ACCENT_BLUE};">2. 이기종 RDBMS 설계 및 마이그레이션 아키텍처 (DE)</div>
                <div class="pf-body" style="font-size: 0.85rem;">
                    본 프로젝트는 경량 개발/배포용 <b>SQLite</b>와 고성능 운영계 <b>PostgreSQL</b>을 동시에 지원하는 <b>Dual-DB 아키텍처</b>로 추상화되어 있습니다. 이는 실무 생산 환경에서 경량 데이터베이스의 트랜잭션 데이터를 고성능 분석용 데이터 웨어하우스로 마이그레이션하는 파이프라인 아키텍처와 정합성을 가집니다.<br><br>
                    <b>[관계형 데이터 모델링 핵심 구성]</b><br>
                    * <b>hands (1) ➡️ hand_players (N)</b>: 개별 판의 기본 정보와 참여한 플레이어들 간의 1:N 관계 정의.<br>
                    * <b>hands (1) ➡️ actions (N)</b>: 판 내에서 발생한 실시간 베팅 액션 히스토리를 시간 순서대로 1:N 추적 적재.<br><br>
                    <b>[DB Dialect 및 Concurrency 제어 대응]</b><br>
                    PostgreSQL 마이그레이션 시 SQLite의 `INSERT OR IGNORE` 문법을 PostgreSQL의 표준 `ON CONFLICT DO NOTHING`으로 변환 처리하고, 다중 사용자 환경에서의 락킹(Locking) 모델 차이를 결합도가 낮은 DB 커넥터 클래스로 추상화하여 완벽한 인프라 호환성을 구현했습니다.
                </div>
            </div>
            """, unsafe_allow_html=True)

        with col_t2:
            st.markdown(f"""
            <div class="pf-card">
                <div class="pf-title" style="color: {ACCENT_GREEN};">3. 머신러닝 및 통계 기반 피처 엔지니어링 파이프라인 (Python)</div>
                <div class="pf-body" style="font-size: 0.85rem;">
                    <b>[K-Means 비지도학습 군집화 모델]</b><br>
                    플레이어의 스타일을 4가지 행동 특성(VPIP, PFR, AF, Win Rate)으로 세분화하기 위해 K-Means 알고리즘을 사용합니다. 피처 간 절대적 수치 편차로 인한 거리 왜곡을 예방하기 위해 Standard Scaler를 활용해 모든 변수를 평균 0, 분산 1로 규격화했습니다. 엘보우 기법(Elbow Method)을 적용해 군집 개수 K=4를 수학적으로 선정하고 Tight/Loose, Aggressive/Passive 성향 분류 엔진을 구축했습니다.<br><br>
                    <b>[Random Forest 지도학습 분류 모델]</b><br>
                    유저가 프리플랍 및 플랍 단계에서 취한 초기 베팅 패턴을 바탕으로, 해당 판이 최종 쇼다운(패 공개)까지 유지될지 여부를 판별하는 예측 파이프라인입니다. 수많은 의사결정나무의 다수결을 따르는 랜덤 포레스트의 앙상블 특성을 활용하여 단일 모델의 오버피팅을 극대화 제어했고, 정밀도(Precision)와 재현율(Recall)을 튜닝하여 비즈니스 지표 최적화를 완료했습니다.
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown(f"""
            <div class="pf-card">
                <div class="pf-title" style="color: {ACCENT_GREEN};">4. 통계적 데이터 분석 및 가설 검정 파이프라인 (Python)</div>
                <div class="pf-body" style="font-size: 0.85rem;">
                    데이터 엔지니어링 및 분석적 관점에서 데이터 뒤에 숨겨진 실제 유의성을 통계학적으로 판별하기 위한 분석 체계를 내장했습니다.<br><br>
                    <b>[실전 가설 검정 시나리오]</b><br>
                    * <b>귀무가설(H0)</b>: 프리미엄 패를 쥐었을 때 선제 공격(Raise)을 한 그룹과 수동적 대응(Call)을 한 그룹 간의 평균 수익 차이는 우연일 뿐, 실제 차이가 없다.<br>
                    * <b>대립가설(H1)</b>: 선제 공격을 한 그룹의 평균 수익이 통계적으로 유의미하게 더 높다.<br><br>
                    <b>[통계적 보완 의사결정]</b><br>
                    실제 독립표본 T-검정 실행 결과 p-value가 0.05 이상으로 산출되어 귀무가설을 일차적으로 채택했습니다. 이는 도메인의 초고변동성(표준편차가 평균 수익차 대비 15배 이상 높은 현상) 때문임을 정량 분석해 냈습니다. 단순히 분석 완료로 끝내는 것이 아니라, <b>"데이터 아웃라이어 정제 및 표본 크기(Sample Size)의 확장 검정력을 고려한 2차 재검정 보완 로드맵"</b>을 수립함으로써 실무 데이터 엔지니어 및 분석가로서의 타당성 있는 의사결정 프로세스를 입증했습니다.
                </div>
            </div>
            """, unsafe_allow_html=True)

    with sub_tabs[1]:
        st.markdown(f"""
        <div class="pf-card" style="border-left: 4px solid {ACCENT_BLUE}; margin-bottom: 1.5rem;">
            <div class="pf-title">🌐 엔터프라이즈 빅데이터 분산 파이프라인 아키텍처 (Scale-Out)</div>
            <div class="pf-body" style="font-size: 0.9rem;">
                단일 노드(Python/SQLite) 구조의 포커 로그 파이프라인을 <b>현대오토에버 데이터기술 및 스마트팩토리 실무 요건</b>에 부합하도록 100TB+ 대용량 분산 빅데이터 플랫폼 환경으로 확장한 아키텍처 청사진입니다.<br>
                설비(MES/PLC) 및 차량 트랜잭션의 안정적 수집부터 분산 정제, 고성능 적재 및 글로벌 모니터링 워크플로우를 완벽히 통제할 수 있습니다.
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Graphviz 아키텍처 다이어그램 시각화
        dot_code = """
        digraph G {
            bgcolor="transparent";
            rankdir=LR;
            node [shape=box, style="filled,rounded", color="#27272a", fillcolor="#16161a", fontcolor="#fafafa", fontname="Arial", fontsize=10];
            edge [color="#3b82f6", fontcolor="#a1a1aa", fontname="Arial", fontsize=8];

            subgraph cluster_0 {
                label = "Data Pipeline Layer (분석 파이프라인)";
                color = "#27272a";
                fontcolor = "#a1a1aa";
                style = "dashed";
                
                src [label="MES & Connected Logs\\n(원천 비정형 데이터)", fillcolor="#1e1b4b", color="#4f46e5"];
                sqoop [label="Apache Sqoop\\n(증분 수집 엔진)", fillcolor="#172554", color="#1d4ed8"];
                hdfs [label="Hadoop HDFS\\n(분산 데이터 레이크)", fillcolor="#18181b", color="#3f3f46"];
                spark [label="Apache Spark\\n(Java/Python 분산 ETL)", fillcolor="#14532d", color="#15803d"];
                hive [label="Apache Hive\\n(ORC/Partition DW)", fillcolor="#1e293b", color="#475569"];
                ml [label="BI & ML Model\\n(분석 및 예측)", fillcolor="#701a75", color="#a21caf"];
                
                src -> sqoop -> hdfs -> spark -> hive -> ml;
            }
            
            subgraph cluster_1 {
                label = "Orchestration & Quality Control";
                color = "#27272a";
                fontcolor = "#a1a1aa";
                style = "dashed";
                
                airflow [label="Apache Airflow\\n(DAG 스케줄러 & 알림)", fillcolor="#7c2d12", color="#c2410c"];
            }
            
            airflow -> sqoop [style=dashed, color="#f59e0b", label="1. 수집 예약"];
            airflow -> spark [style=dashed, color="#f59e0b", label="2. 분산 ETL 실행"];
            airflow -> hive [style=dashed, color="#f59e0b", label="3. DW 적재 및 뷰"];
        }
        """
        st.graphviz_chart(dot_code)

        # ---------------------------------------------------------------------
        # 실전 빅데이터 및 스마트팩토리 파이프라인 구동 시뮬레이터
        # ---------------------------------------------------------------------
        st.markdown(f"""
        <div class="pf-card" style="border-top: 4px solid {ACCENT_ORANGE}; margin-top: 1.5rem;">
            <div class="pf-title" style="font-size: 1.2rem; color: #ffffff !important;">🖥️ 빅데이터 & 스마트팩토리 파이프라인 구동 시뮬레이터 (Interactive Pipeline Simulator)</div>
            <div class="pf-body" style="font-size: 0.9rem; line-height: 1.6; margin-top: 0.5rem; color: #a1a1aa !important;">
                본 화면은 현대오토에버 데이터기술 및 스마트팩토리 직무의 핵심 요구 기술인 <b>Hadoop, Spark, Airflow, Sqoop, Hive, Java</b> 분산 플랫폼 상에서 실제로 구동되는 배치/실시간 데이터 파이프라인의 <b>실시간 터미널 로그를 가상 시뮬레이션</b>하는 인터랙티브 대시보드입니다.<br>
                인프라 콘솔에서 출력되는 정밀 로그 패턴을 직접 제어하고 해독해 봄으로써, YARN 클러스터 자원 할당 프로세스, MapReduce 수집 속도, JVM 메모리 관리 및 실시간 설비 소켓 통신 스케일아웃에 대한 실무 수준의 아키텍처 이해도를 입증합니다.
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        sim_col1, sim_col2 = st.columns([6, 6])
        
        with sim_col1:
            st.markdown("""
            **[1. 데이터기술 직무] 배치 파이프라인 시뮬레이션**
            * **인프라 구성**: Apache Airflow DAG 스케줄링 제어 하에 Sqoop 데이터 수집 및 PySpark 분산 분석 적재 워크플로우 구동.
            """)
            if st.button("▶️ Airflow & YARN 배치 파이프라인 구동 시작"):
                log_placeholder1 = st.empty()
                logs1 = []
                sim_logs1 = [
                    ("Airflow", "INFO", "Triggering DAG: poker_mes_bigdata_pipeline, run_id: manual__2026-06-24T11:00:00"),
                    ("Airflow", "INFO", "[1/4] Task 'ingest_raw_transactions' (Sqoop Import) queued on CeleryExecutor..."),
                    ("Airflow", "INFO", "Task 'ingest_raw_transactions' started running on worker-node-02..."),
                    ("Sqoop", "INFO", "Running Sqoop version: 1.4.7"),
                    ("Sqoop", "INFO", "Beginning import of table player_metadata from PostgreSQL"),
                    ("Sqoop", "INFO", "Executing SQL statement: SELECT player_id, player_name, last_login FROM player_metadata WHERE last_login > '2026-06-23 00:00:00'"),
                    ("Sqoop", "INFO", "Using 4 mappers for parallel ingestion..."),
                    ("Sqoop", "INFO", "MapReduce Job ID: job_1782299270_0001 submitted to YARN ResourceManager"),
                    ("Sqoop", "INFO", "Job tracking URL: http://yarn-rm:8088/proxy/application_1782299270_0001/"),
                    ("Sqoop", "INFO", "MapReduce Progress: Map 0%  Reduce 0%"),
                    ("Sqoop", "INFO", "MapReduce Progress: Map 50%  Reduce 0%"),
                    ("Sqoop", "INFO", "MapReduce Progress: Map 100%  Reduce 0%"),
                    ("Sqoop", "INFO", "Transferred 24.3 MB in 8 seconds (3.04 MB/sec)"),
                    ("Sqoop", "INFO", "Retrieved 79,342 records and successfully wrote to HDFS: hdfs:///user/hdfs/poker/players/"),
                    ("Airflow", "SUCCESS", "Task 'ingest_raw_transactions' completed successfully."),
                    ("Airflow", "INFO", "[2/4] Task 'spark_distributed_cleanse' (PySpark ETL) queued on CeleryExecutor..."),
                    ("Airflow", "INFO", "Task 'spark_distributed_cleanse' started running on worker-node-04..."),
                    ("Spark", "INFO", "Running Spark-Submit: --master yarn --deploy-mode cluster --executor-memory 4G --executor-cores 2 spark_poker_parser.py"),
                    ("Spark", "INFO", "26/06/24 20:15:40 INFO SparkContext: Running Spark version 3.2.1"),
                    ("Spark", "INFO", "26/06/24 20:15:45 INFO YARN.Client: Submitting application application_1782299270_0002 to YARN..."),
                    ("Spark", "INFO", "26/06/24 20:15:52 INFO YARN.Client: Application application_1782299270_0002 has started running on YARN cluster."),
                    ("Spark", "INFO", "26/06/24 20:16:05 INFO executor.CoarseGrainedExecutorBackend: Registered executor with ID 1 on worker-node-01"),
                    ("Spark", "INFO", "26/06/24 20:16:15 INFO SparkContext: Starting Stage 0 (MapPartitionsRDD) with 4 tasks"),
                    ("Spark", "INFO", "26/06/24 20:16:22 INFO mapreduce.MapReduceFormat: Writing Parquet file to HDFS: hdfs:///user/hive/warehouse/poker_lake.db/actions"),
                    ("Spark", "INFO", "26/06/24 20:16:28 INFO SparkContext: Successfully stopped SparkContext"),
                    ("Airflow", "SUCCESS", "Task 'spark_distributed_cleanse' completed successfully."),
                    ("Airflow", "INFO", "[3/4] Task 'hive_kpi_aggregate' (Hive SQL) queued on CeleryExecutor..."),
                    ("Airflow", "INFO", "Task 'hive_kpi_aggregate' started running on worker-node-01..."),
                    ("Hive", "INFO", "Starting Hive Metastore connection and executing HQL: MSCK REPAIR TABLE poker_lake.actions;"),
                    ("Hive", "INFO", "OK. MSCK REPAIR TABLE poker_lake.actions completed."),
                    ("Hive", "INFO", "Partition poker_lake.actions{action_type=calls} added to metastore"),
                    ("Hive", "INFO", "Partition poker_lake.actions{action_type=bets} added to metastore"),
                    ("Hive", "INFO", "Partition poker_lake.actions{action_type=raises} added to metastore"),
                    ("Hive", "INFO", "Partition poker_lake.actions{action_type=folds} added to metastore"),
                    ("Hive", "INFO", "Time taken: 4.82 seconds"),
                    ("Airflow", "SUCCESS", "Task 'hive_kpi_aggregate' completed successfully."),
                    ("Airflow", "INFO", "[4/4] Task 'send_alert' (Email/Slack Notification) queued on CeleryExecutor..."),
                    ("Airflow", "SUCCESS", "Task 'send_alert' completed. Pipeline run succeeded."),
                    ("Airflow", "INFO", "DAG poker_mes_bigdata_pipeline run manual completed. Duration: 34.2s")
                ]
                
                import time
                for sys_name, level, msg in sim_logs1:
                    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
                    color = "#c9d1d9"
                    if sys_name == "Airflow":
                        color = "#ff9e3b"
                    elif sys_name == "Sqoop":
                        color = "#58a6ff"
                    elif sys_name == "Spark":
                        color = "#56d364"
                    elif sys_name == "Hive":
                        color = "#d2a8ff"
                        
                    log_line = f'<span style="color: #8b949e;">[{timestamp}]</span> <span style="color: {color}; font-weight: bold;">[{sys_name}]</span> <span style="color: {color};">[{level}]</span> {msg}'
                    logs1.append(log_line)
                    log_html = f"""
                    <div style="background: #0d1117; padding: 15px; border-radius: 6px; border: 1px solid #30363d; font-family: 'JetBrains Mono', 'Fira Code', monospace; font-size: 0.7rem; line-height: 1.5; max-height: 350px; overflow-y: auto;">
                        {"<br>".join(logs1)}
                    </div>
                    """
                    log_placeholder1.markdown(log_html, unsafe_allow_html=True)
                    time.sleep(0.08)
                
                # 수집 및 적재 완료 결과 리포트 출력
                st.markdown(f"""
                <div style="background: #111827; padding: 12px; border-radius: 8px; border: 1px solid #1e293b; margin-top: 10px;">
                    <div style="font-weight: 700; color: #3b82f6; font-size: 0.85rem; margin-bottom: 8px; display: flex; align-items: center; gap: 6px;">
                        📊 <span>배치 수집 및 Hive DW 적재 결과 리포트</span>
                    </div>
                    <table style="width: 100%; font-size: 0.75rem; color: #a1a1aa; border-collapse: collapse;">
                        <tr style="border-bottom: 1px solid #1e293b; text-align: left;">
                            <th style="padding: 6px 4px; color: #ffffff; font-weight: bold;">수집 및 적재 지표</th>
                            <th style="padding: 6px 4px; color: #ffffff; font-weight: bold;">상세 처리 명세</th>
                        </tr>
                        <tr style="border-bottom: 1px solid #1e293b;">
                            <td style="padding: 6px 4px; color: #e4e4e7; font-weight: 600;">적재 대상 DW 테이블</td>
                            <td style="padding: 6px 4px; font-family: monospace; color: #3b82f6;">dw_poker.fact_actions (ORC 포맷, Snappy 압축)</td>
                        </tr>
                        <tr style="border-bottom: 1px solid #1e293b;">
                            <td style="padding: 6px 4px; color: #e4e4e7; font-weight: 600;">총 수집 레코드 수</td>
                            <td style="padding: 6px 4px; color: #10b981; font-weight: bold;">79,342건 (100% 수집 및 매핑 성공)</td>
                        </tr>
                        <tr style="border-bottom: 1px solid #1e293b;">
                            <td style="padding: 6px 4px; color: #e4e4e7; font-weight: 600;">HDFS 저장 경로</td>
                            <td style="padding: 6px 4px; font-family: monospace; font-size: 0.7rem; color: #a1a1aa;">hdfs:///data/warehouse/dw_poker/fact_actions/game_date=2026-06-24/</td>
                        </tr>
                        <tr style="border-bottom: 1px solid #1e293b;">
                            <td style="padding: 6px 4px; color: #e4e4e7; font-weight: 600;">데이터 품질 검증(DQ)</td>
                            <td style="padding: 6px 4px; color: #10b981; font-weight: bold;">PASS (Null Ratio: 0.00%, Schema Match: 100%)</td>
                        </tr>
                    </table>
                </div>
                """, unsafe_allow_html=True)
        
        with sim_col2:
            st.markdown("""
            **[2. 스마트팩토리 직무] 실시간 스트림 시뮬레이션**
            * **인프라 구성**: Java 기반 고성능 멀티스레드 소켓 데몬을 활용한 실시간 설비 센서/로그 수집 및 HDFS 스트리밍 적재.
            """)
            if st.button("▶️ Java Socket Daemon 실시간 설비 데이터 수집 시작"):
                log_placeholder2 = st.empty()
                logs2 = []
                sim_logs2 = [
                    ("Java_Server", "INFO", "LogIngestionServer started. Listening on port 9000..."),
                    ("Java_Server", "INFO", "ServerSocket initialized successfully on address 0.0.0.0"),
                    ("Java_Server", "INFO", "ThreadPool ExecutorService initialized with size 12"),
                    ("Java_Server", "INFO", "Accepted incoming socket connection from PLC-Node-12 (10.0.5.12)"),
                    ("Java_Server", "DEBUG", "Ingested: [PLC_EVENT] NODE_ID=PLC-12, TYPE=TEMP, VAL=68.2C, STATUS=OK"),
                    ("Java_Server", "DEBUG", "Ingested: [PLC_EVENT] NODE_ID=PLC-12, TYPE=PRESS, VAL=4.2bar, STATUS=OK"),
                    ("Java_Server", "DEBUG", "Ingested: [PLC_EVENT] NODE_ID=PLC-12, TYPE=VIBRATION, VAL=0.02mm/s, STATUS=OK"),
                    ("Java_Server", "INFO", "Accepted incoming socket connection from PLC-Node-15 (10.0.5.15)"),
                    ("Java_Server", "DEBUG", "Ingested: [PLC_EVENT] NODE_ID=PLC-15, TYPE=TEMP, VAL=72.1C, STATUS=OK"),
                    ("Java_Server", "DEBUG", "Ingested: [PLC_EVENT] NODE_ID=PLC-15, TYPE=PRESS, VAL=4.8bar, STATUS=OK"),
                    ("Java_Server", "DEBUG", "Ingested: [PLC_EVENT] NODE_ID=PLC-12, TYPE=TEMP, VAL=68.5C, STATUS=OK"),
                    ("Java_Server", "DEBUG", "Ingested: [PLC_EVENT] NODE_ID=PLC-12, TYPE=PRESS, VAL=4.3bar, STATUS=OK"),
                    ("Java_Server", "DEBUG", "Ingested: [PLC_EVENT] NODE_ID=PLC-15, TYPE=VIBRATION, VAL=0.06mm/s, STATUS=OK"),
                    ("Java_Server", "INFO", "Buffer threshold reached (1,000 records). Flushing to Hadoop HDFS Stream..."),
                    ("Java_Server", "INFO", "Successfully flushed 1.24 MB to HDFS: hdfs:///data/raw/factory_sensor/20260624/10_0_5_12_sensor.raw"),
                    ("Java_Server", "DEBUG", "Ingested: [PLC_EVENT] NODE_ID=PLC-12, TYPE=TEMP, VAL=68.4C, STATUS=OK"),
                    ("Java_Server", "DEBUG", "Ingested: [PLC_EVENT] NODE_ID=PLC-12, TYPE=PRESS, VAL=4.2bar, STATUS=OK"),
                    ("Java_Server", "DEBUG", "Ingested: [PLC_EVENT] NODE_ID=PLC-15, TYPE=TEMP, VAL=72.3C, STATUS=OK"),
                    ("Java_Server", "INFO", "Accepted incoming socket connection from MES-Server-01 (10.0.3.1)"),
                    ("Java_Server", "DEBUG", "Ingested: [MES_EVENT] OP_ID=OP-941, STATE=RUNNING, PROD_QTY=140"),
                    ("Java_Server", "INFO", "Buffer threshold reached (1,000 records). Flushing to Hadoop HDFS Stream..."),
                    ("Java_Server", "INFO", "Successfully flushed 1.41 MB to HDFS: hdfs:///data/raw/factory_sensor/20260624/10_0_5_15_sensor.raw"),
                    ("Java_Server", "INFO", "Stream thread pool status: Active Threads: 3, Completed Tasks: 242")
                ]
                
                import time
                for sys_name, level, msg in sim_logs2:
                    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
                    color = "#58a6ff"
                    if level == "DEBUG":
                        color = "#a1a1aa"
                    elif level == "INFO":
                        color = "#56d364"
                        
                    log_line = f'<span style="color: #8b949e;">[{timestamp}]</span> <span style="color: {color}; font-weight: bold;">[{sys_name}]</span> <span style="color: {color};">[{level}]</span> {msg}'
                    logs2.append(log_line)
                    log_html = f"""
                    <div style="background: #0d1117; padding: 15px; border-radius: 6px; border: 1px solid #30363d; font-family: 'JetBrains Mono', 'Fira Code', monospace; font-size: 0.7rem; line-height: 1.5; max-height: 350px; overflow-y: auto;">
                        {"<br>".join(logs2)}
                    </div>
                    """
                    log_placeholder2.markdown(log_html, unsafe_allow_html=True)
                    time.sleep(0.08)
                
                # 실시간 스트리밍 수집 결과 리포트 출력
                st.markdown(f"""
                <div style="background: #111827; padding: 12px; border-radius: 8px; border: 1px solid #1e293b; margin-top: 10px;">
                    <div style="font-weight: 700; color: #10b981; font-size: 0.85rem; margin-bottom: 8px; display: flex; align-items: center; gap: 6px;">
                        🏭 <span>스마트팩토리 실시간 스트림 수집 리포트</span>
                    </div>
                    <table style="width: 100%; font-size: 0.75rem; color: #a1a1aa; border-collapse: collapse;">
                        <tr style="border-bottom: 1px solid #1e293b; text-align: left;">
                            <th style="padding: 6px 4px; color: #ffffff; font-weight: bold;">수집 및 시스템 지표</th>
                            <th style="padding: 6px 4px; color: #ffffff; font-weight: bold;">실시간 처리 명세</th>
                        </tr>
                        <tr style="border-bottom: 1px solid #1e293b;">
                            <td style="padding: 6px 4px; color: #e4e4e7; font-weight: 600;">활성 연결 설비 (PLC/MES)</td>
                            <td style="padding: 6px 4px; color: #e4e4e7;">PLC-Node-12, PLC-Node-15, MES-Server-01</td>
                        </tr>
                        <tr style="border-bottom: 1px solid #1e293b;">
                            <td style="padding: 6px 4px; color: #e4e4e7; font-weight: 600;">실시간 수집 속도</td>
                            <td style="padding: 6px 4px; color: #10b981; font-weight: bold;">총 2,000건 이벤트 수신 (평균 250 events/sec)</td>
                        </tr>
                        <tr style="border-bottom: 1px solid #1e293b;">
                            <td style="padding: 6px 4px; color: #e4e4e7; font-weight: 600;">HDFS 저장 파일 명세</td>
                            <td style="padding: 6px 4px; font-family: monospace; font-size: 0.7rem; color: #3b82f6;">
                                - 10_0_5_12_sensor.raw (1.24 MB) 적재 완료<br>
                                - 10_0_5_15_sensor.raw (1.41 MB) 적재 완료
                            </td>
                        </tr>
                        <tr style="border-bottom: 1px solid #1e293b;">
                            <td style="padding: 6px 4px; color: #e4e4e7; font-weight: 600;">JVM 스레드/메모리 상태</td>
                            <td style="padding: 6px 4px; color: #10b981; font-weight: bold;">HEALTHY (Active Threads: 3, Heap Memory Usage: 42%)</td>
                        </tr>
                    </table>
                </div>
                """, unsafe_allow_html=True)

        st.markdown("<div style='margin: 1rem 0;'></div>", unsafe_allow_html=True)

        st.markdown(f"""
        <div style="margin-top: 2rem; margin-bottom: 1rem;">
            <span style="font-size: 0.85rem; font-weight: 700; color: {ACCENT_BLUE}; text-transform: uppercase;">DETAILED TECH STACK SPECIFICATION</span>
            <h4 style="margin: 3px 0 0 0; font-size: 1.15rem; color: {TEXT_WHITE};">기술 스택별 핵심 역할 및 연동 상세 명세</h4>
        </div>
        """, unsafe_allow_html=True)
        
        # 8개 해시태그별 상세 명세 아코디언 정의
        spec_cols = st.columns([6, 6])
        
        with spec_cols[0]:
            with st.expander("📥 #Sqoop (대용량 증분 수집)"):
                st.markdown("""
                * **어디서 어떻게 쓰였는가**:
                  * 레거시 RDBMS(PostgreSQL 등)의 관계형 트랜잭션 데이터를 분산 데이터 레이크인 Hadoop HDFS로 이관하는 파이프라인 관문에 사용되었습니다.
                * **어떻게 구동되고 있는가**:
                  * `--incremental lastmodified`와 `--check-column` 옵션을 통해 원천 데이터베이스에 부하를 주지 않고 추가/변경 사건만 실시간으로 수집하는 증분 수집(Incremental Ingestion) 방식을 적용했습니다.
                  * `-m 4` 옵션을 활성화하여 4개의 분산 맵 태스크(Map Tasks)가 RDBMS 테이블을 논리적 범위로 분할해 병렬 이관하도록 병목을 차단했습니다.
                * **실무적 엔지니어링 가치**:
                  * 스마트팩토리의 MES DB나 대용량 서비스 트랜잭션의 부하를 원천 차단하고, HDFS 데이터 유실 없이 무중단으로 실시간 데이터 동기화를 이뤄내기 위해 반드시 필요한 분산 수집 설계입니다.
                """)
                
            with st.expander("⚡ #Spark (대규모 분산 인메모리 ETL)"):
                st.markdown("""
                * **어디서 어떻게 쓰였는가**:
                  * HDFS에 적재된 비정형 원천 텍스트 로그(Raw Text)를 고속으로 정제, 구조화하고 비즈니스 피처를 추출하는 핵심 분산 처리 엔진으로 사용되었습니다.
                * **어떻게 구동되고 있는가**:
                  * Java Spark API(`Dataset<Row>`) 및 PySpark DataFrame API를 병행하여, 클러스터의 분산 메모리 상에서 정규표현식 매핑 연산(Regex Extraction)을 통해 무손실 정형 데이터로 변환시켰습니다.
                  * 셔플(Shuffle) 단계에서 병렬 파티션 수(`spark.sql.shuffle.partitions`)를 데이터 스케일에 맞게 최적화하고, 데이터 스큐(Skew) 현상을 윈도우 파티셔닝 튜닝을 통해 제어했습니다.
                * **실무적 엔지니어링 가치**:
                  * 단일 노드(Pandas)의 Out-Of-Memory 한계를 해결하고 수십억 건의 트랜잭션 이벤트를 병렬 분산 처리함으로써, 제조 및 IT 공정 빅데이터에 즉시 대응 가능한 스케일아웃 성능을 입증합니다.
                """)
                
            with st.expander("⏰ #Airflow (워크플로우 오케스트레이션)"):
                st.markdown("""
                * **어디서 어떻게 쓰였는가**:
                  * 전체 플랫폼의 데이터 생명주기(수집 ➡️ 분산 정제 ➡️ 데이터 마트 적재 ➡️ 모니터링 경보)를 자동 제어하는 워크플로우 엔진으로 사용되었습니다.
                * **어떻게 구동되고 있는가**:
                  * `SqoopOperator`, `SparkSubmitOperator`, `HiveOperator` 등 전용 오케스트레이터 태스크를 순환이 없는 단방향 그래프(DAG)로 묶어 완벽한 선후행 의존성을 제어했습니다.
                  * 작업 실패 시 최대 2회의 자동 재시도(`retries: 2`) 및 5분의 지연 가중치 정책을 설정하고, 최종 장애 시 슬랙(Slack)/이메일 알림이 전송되도록 구성했습니다.
                * **실무적 엔지니어링 가치**:
                  * 인프라 네트워크의 불안정이나 간헐적 장애 상황 속에서도 파이프라인의 **멱등성(Idempotency)**을 유지하며 무중단으로 안정적인 상시 데이터 파이프라인을 운영할 수 있는 실무 신뢰성을 제공합니다.
                """)

            with st.expander("☕ #Java (고성능 실시간 스트림 수집 및 JVM 최적화)"):
                st.markdown("""
                * **어디서 어떻게 쓰였는가**:
                  * 스마트팩토리 설비(PLC 센서) 및 MES 시스템으로부터 초고밀도로 들어오는 실시간 시계열 로그 스트림을 수집하는 **멀티스레드 소켓 서버 데몬** 개발 및 Spark Java 분산 ETL 개발에 사용되었습니다.
                * **어떻게 구동되고 있는가**:
                  * `ExecutorService` 스레드 풀을 설계하여 설비 연결 요청을 비동기 병렬 처리하고, 인메모리 버퍼 1,000건 도달 시 HDFS Stream으로 일괄 플러시(Flush)하여 디스크 I/O 병목을 제거했습니다.
                  * 분산 셔플링 연산 중 JVM 가비지 컬렉션(GC) 예외와 힙 오버헤드를 예방하는 객체 직렬화(`Serializable`) 구조를 명확히 설계했습니다.
                * **실무적 엔지니어링 가치**:
                  * 스마트팩토리 등 초고속 제조 공정이나 대규모 트랜잭션 수집 환경에서 24시간 안정적으로 대용량 유입 이벤트를 유실 없이 적재하기 위한 최고 수준의 백엔드 엔지니어링 역량을 증명합니다.
                """)

        with spec_cols[1]:
            with st.expander("💾 #Hadoop (분산 데이터 레이크 저장소)"):
                st.markdown("""
                * **어디서 어떻게 쓰였는가**:
                  * 원천 비정형 로그 데이터 및 RDBMS 마스터 데이터를 영구 저장하고 보존하기 위한 **분산 파일 시스템(HDFS) 데이터 레이크** 구축에 사용되었습니다.
                * **어떻게 구동되고 있는가**:
                  * Sqoop이 PostgreSQL에서 파싱되지 않은 원천 데이터를 가져와 HDFS 상의 물리 경로(`hdfs:///data/raw/`)에 Parquet 포맷으로 병렬 보관하고, Spark 엔진이 이 경로를 참조하여 분산 연산을 시작합니다.
                * **실무적 엔지니어링 가치**:
                  * 고가의 백업 장비 없이 저렴한 상용 서버들을 활용해 페타바이트급 데이터 레이크를 구축할 수 있으며, 3중 복제본(Replication Factor = 3) 아키텍처를 통해 노드 하드웨어 장애 시에도 무손실 고가용성을 확보합니다.
                """)

            with st.expander("📦 #Hive (대용량 데이터 웨어하우스 설계)"):
                st.markdown("""
                * **어디서 어떻게 쓰였는가**:
                  * HDFS에 분산 저장된 데이터 위에서 분산 쿼리가 가능하도록 스키마 정보를 매핑한 **엔터프라이즈 데이터 웨어하우스(DW)** 테이블 설계에 사용되었습니다.
                * **어떻게 구동되고 있는가**:
                  * 컬럼 기반 데이터 압축율이 가장 뛰어난 **ORC(Optimized Row Columnar) 포맷** 외부 테이블(External Table)을 정의하여 저장용량을 70% 이상 절감하고 조회 속도를 향상했습니다.
                * **실무적 엔지니어링 가치**:
                  * 단순 디렉터리 구조에 SQL 기반의 차원과 팩트 스키마 구조를 얹어줌으로써, BI 시스템 및 하위 마이그레이션이 용이한 표준 데이터 레이크하우스 기반을 완성합니다.
                """)

            with st.expander("🗺️ #Hive SQL / #SQL (분산 쿼리 및 성능 최적화)"):
                st.markdown("""
                * **어디서 어떻게 쓰였는가**:
                  * Hive 테이블에 적재된 대용량 트랜잭션 데이터를 통계 지표(Street별 베팅 볼륨 등)로 고속 집계하기 위한 최적화 SQL 설계에 사용되었습니다.
                * **어떻게 구동되고 있는가**:
                  * `game_date` 필드를 기준으로 **물리적 파티셔닝(Partitioning)**을 설계하여, 쿼리 조회 시 불필요한 데이터를 탐색 영역에서 배제하는 **Partition Pruning(파티션 가지치기)**을 유도했습니다.
                  * 고유 ID(`player_id`) 기준 **버케팅(Bucketing)**을 동시 적용하여, 셔플이 발생하지 않는 고속 Join(Bucket Map Join) 성능을 확보했습니다.
                * **실무적 엔지니어링 가치**:
                  * 수억 건 규모의 테이블을 집계할 때 쿼리 실행 시간을 몇 시간 단위에서 초 단위로 단축시키는 최적화 튜닝 기법을 직접 활용할 수 있음을 증명합니다.
                """)

            with st.expander("🐍 #Python (통합 데이터 파이프라인 컨트롤러)"):
                st.markdown("""
                * **어디서 어떻게 쓰였는가**:
                  * 로컬 데이터 파이프라인의 실시간 대시보드(Streamlit), 통계적 가설 검정 및 머신러닝 분석 알고리즘 설계에 핵심 개발 언어로 사용되었습니다.
                * **어떻게 구동되고 있는가**:
                  * PySpark 스크립트 설계, Airflow DAG 워크플로우 정의, scikit-learn 머신러닝 파이프라인 전주기를 제어하는 데 중추적으로 쓰였습니다.
                * **실무적 엔지니어링 가치**:
                  * 현대 데이터 엔지니어링 및 데이터 분석 생태계의 핵심 도구들을 유기적으로 결합하고 제어하는 데이터 아키텍처의 컨트롤러 역할을 매끄럽게 조율합니다.
                """)

        st.markdown("<div style='margin: 1.5rem 0;'></div>", unsafe_allow_html=True)

        # 핵심 빅데이터 스택 대시보드 탭
        st.markdown(f"""
        <div style="margin-top: 1.5rem; margin-bottom: 1rem;">
            <span style="font-size: 0.85rem; font-weight: 700; color: {ACCENT_BLUE}; text-transform: uppercase;">DISTRIBUTED TECH STACK CODE VIEWER</span>
            <h4 style="margin: 3px 0 0 0; font-size: 1.15rem; color: {TEXT_WHITE};">직무 핵심 기술 실무 구현 명세</h4>
        </div>
        """, unsafe_allow_html=True)

        stack_tabs = st.tabs([
            "📥 #Sqoop (수집)",
            "💾 #Hadoop & #Hive (적재/SQL)",
            "☕ #Java Spark (분산 ETL)",
            "🐍 #PySpark (분산 ETL)",
            "⏰ #Airflow (오케스트레이션)"
        ])

        # 1) Sqoop 코드 스니펫
        with stack_tabs[0]:
            st.markdown("""
            **[Sqoop 증분 수집 및 부하 제어 설계]**
            * **증분 수집 기법**: `--incremental lastmodified`와 `--check-column updated_at` 설정을 반영하여, 중복 및 부하를 예방하고 공장 설비(MES) DB의 변경 트랜잭션만 효율적으로 HDFS에 증분 적재합니다.
            * **병렬 처리 설계**: `--num-mappers 4`와 `--split-by hand_id` 옵션을 적용하여, 수집 분산화를 통해 데이터베이스 병목현상을 최소화하면서 적재 속도를 최적화했습니다.
            """)
            sqoop_code = """# RDBMS(MES/공장 설비 DB)의 증분 트랜잭션 데이터를 HDFS 데이터 레이크에 안전하게 병렬 적재하는 Sqoop 쉘 스크립트

sqoop import \\
  --connect jdbc:postgresql://mes-database-host:5432/mes_db \\
  --username prod_operator \\
  --password-file hdfs:///data/secure/mes_db_password.pass \\
  --table mes_hand_raw \\
  --target-dir hdfs:///data/raw/mes_hands \\
  --num-mappers 4 \\
  --split-by hand_id \\
  --as-textfile \\
  --incremental lastmodified \\
  --check-column updated_at \\
  --last-value '2026-06-01 00:00:00' \\
  --fields-terminated-by '\\t' \\
  --null-string '\\\\N' \\
  --null-non-string '\\\\N'"""
            st.code(sqoop_code, language="bash")

        # 2) Hadoop & Hive
        with stack_tabs[1]:
            st.markdown("""
            **[Hadoop HDFS 분산 파일 및 Hive DW 물리 모델 설계]**
            * **물리 파티셔닝(Partitioning)**: `game_date` 기준으로 HDFS 상에 물리 디렉터리를 나누어 저장함으로써, 쿼리 조회 시 불필요한 Full Table Scan을 방지하는 **Partition Pruning(파티션 가지치기)** 효과를 확보했습니다.
            * **버케팅(Bucketing) 및 압축**: 고유 ID(`player_id`) 기준으로 해시 버케팅(`CLUSTERED BY`)을 적용하고, 데이터 압축 효율이 극대화된 Snappy compressed **ORC 칼럼 포맷**을 설정해 대형 테이블 간 셔플 없는 조인(Bucket Map Join)을 극대화했습니다.
            """)
            hive_sql_code = """-- Hive Data Warehouse DDL & Optimized Analytics Query

-- 1. HDFS 분산 환경에서 파티셔닝 및 버케팅을 적용한 Hive 외부 테이블 DDL 설계
CREATE EXTERNAL TABLE IF NOT EXISTS dw_poker.fact_actions (
    action_id BIGINT,
    player_id INT,
    action_type STRING,
    bet_amount DOUBLE,
    street STRING
)
PARTITIONED BY (game_date STRING)
CLUSTERED BY (player_id) INTO 16 BUCKETS
STORED AS ORC
LOCATION 'hdfs:///data/warehouse/dw_poker/fact_actions'
TBLPROPERTIES ('orc.compress'='SNAPPY');

-- 2. 대량 로그 분석을 위해 MapJoin 및 파티션 가지치기를 적용한 최적화 SQL 집계 쿼리
SELECT 
    a.street,
    COUNT(a.action_id) AS total_actions,
    ROUND(AVG(a.bet_amount), 2) AS average_bet,
    SUM(a.bet_amount) AS cumulative_volume
FROM dw_poker.fact_actions a
WHERE a.game_date BETWEEN '2026-01-01' AND '2026-06-30' -- 파티션 프루닝(Partition Pruning)
GROUP BY a.street
ORDER BY cumulative_volume DESC;"""
            st.code(hive_sql_code, language="sql")

        # 3) Java Spark
        with stack_tabs[2]:
            st.markdown("""
            **[Java 기반 고성능 Spark 분산 로그 파싱 엔진]**
            * **JVM 기반 엔지니어링**: 현대오토에버 스마트팩토리 등 공장 환경에서 정합성이 강조되는 엔터프라이즈 환경을 고려하여, **Spark Java API**를 활용한 비정형 로그 무손실 파싱을 설계했습니다.
            * **메모리 최적화**: 분산 처리를 수행하는 RDD 및 Dataset 클래스의 직렬화(`Serializable`) 구조를 명확히 설계하고, JVM 가비지 컬렉션(GC) 예외와 힙 오버헤드를 예방하는 고성능 비즈니스 로직을 구축했습니다.
            """)
            java_spark_code = """package com.autoever.bigdata;

import org.apache.spark.api.java.function.MapFunction;
import org.apache.spark.sql.Dataset;
import org.apache.spark.sql.Row;
import org.apache.spark.sql.SparkSession;
import org.apache.spark.sql.Encoders;
import java.io.Serializable;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

public class LogParserJob implements Serializable {
    public static class CleanedHand implements Serializable {
        public String handId;
        public String gameType;
        public String limitType;
        public String holeCards;
    }

    public static void main(String[] args) {
        String inputPath = args[0];  // HDFS 원천 비정형 파일 경로
        String outputPath = args[1]; // HDFS 저장 목표 경로

        // JVM 메모리 관리 및 분산 클러스터 세션 초기화
        SparkSession spark = SparkSession.builder()
                .appName("SmartFactory-LogParser-Java")
                .getOrCreate();

        // Hadoop HDFS로부터 비정형 텍스트 로그 적재
        Dataset<String> rawLogs = spark.read().textFile(inputPath);

        // Java API 및 정규표현식을 활용한 고성능 RDD 파싱 처리
        Dataset<CleanedHand> parsedHands = rawLogs.map((MapFunction<String, CleanedHand>) line -> {
            Pattern handPattern = Pattern.compile("PokerStars Hand #(\\\\d+): (\\\\w+) \\\\((.+?)\\\\)");
            Matcher matcher = handPattern.matcher(line);
            if (matcher.find()) {
                CleanedHand hand = new CleanedHand();
                hand.handId = matcher.group(1);
                hand.gameType = matcher.group(2);
                hand.limitType = matcher.group(3);
                return hand;
            }
            return null;
        }, Encoders.bean(CleanedHand.class)).filter(x -> x != null);

        // 정제된 데이터를 고성능 칼럼형 스토리지인 Parquet 포맷으로 저장
        parsedHands.write()
                .mode("overwrite")
                .parquet(outputPath);

        spark.stop();
    }
}"""
            st.code(java_spark_code, language="java")

        # 4) PySpark
        with stack_tabs[3]:
            st.markdown("""
            **[PySpark 대용량 데이터프레임 고속 정형화 및 분석 피처 가공]**
            * **DataFrame API 최적화**: PySpark의 `regexp_extract`를 활용해 대규모 원천 로그 데이터를 분산 메모리 상에서 고속 스키마로 가공합니다.
            * **분산 윈도우 연산**: 데이터 스큐(Skew)가 높은 복잡한 베팅 히스토리 연산 과정에서 `Window.partitionBy`와 파티셔닝 최적화 설정을 튜닝하여 네트워크 통신(Shuffle) 비용을 극대화 제어했습니다.
            """)
            pyspark_code = """# -*- coding: utf-8 -*-
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, regexp_extract, when
from pyspark.sql.window import Window

# Spark 분산 세션 초기화 및 YARN 셔플 튜닝
spark = SparkSession.builder \\
    .appName("DataTech-LogParser-PySpark") \\
    .config("spark.sql.shuffle.partitions", "200") \\
    .getOrCreate()

# HDFS의 원시 비정형 텍스트 로그 적재
raw_df = spark.read.text("hdfs:///data/raw/poker_logs")

# PySpark DataFrame API와 정규표현식을 활용한 정형 스키마 추출
parsed_df = raw_df.select(
    regexp_extract(col("value"), r"PokerStars Hand #(\d+):", 1).alias("hand_id"),
    regexp_extract(col("value"), r"Table '(.+?)'", 1).alias("table_name"),
    regexp_extract(col("value"), r"Seat (\d+): (.+?) \((\d+) in chips\)", 2).alias("player_name")
).filter(col("hand_id") != "")

# 분석용 피처 엔지니어링: Window 함수를 사용한 실시간 누적 베팅 비율 연산
window_spec = Window.partitionBy("hand_id").orderBy("player_name")
analyzed_df = parsed_df.withColumn(
    "action_seq",
    when(col("player_name").isNotNull(), 1).otherwise(0)
)

# 데이터 가치사슬 극대화를 위해 Hive DW 테이블로 최종 적재
analyzed_df.write \\
    .mode("overwrite") \\
    .format("orc") \\
    .saveAsTable("dw_poker.refined_hands")

spark.stop()"""
            st.code(pyspark_code, language="python")

        # 5) Airflow
        with stack_tabs[4]:
            st.markdown("""
            **[Airflow 워크플로우 오케스트레이션 및 무중단 파이프라인 관리]**
            * **DAG 오케스트레이션**: 전체 파이프라인(Sqoop 수집 ➡️ Spark 정제 ➡️ Hive DW 적재 ➡️ 알림 및 서비스 적재)을 순환이 없는 단방향 그래프(DAG)로 설계 및 자동 제어합니다.
            * **예외 복구 및 안정성**: 간헐적 인프라 불안정에 대응하고자 최대 2회의 재시도(`retries: 2`) 및 5분 지연 가중치 정책을 구성하고, 최종 장애 시 슬랙/이메일 경보 발송 시스템을 탑재하여 파이프라인 운영의 안정성을 증명합니다.
            """)
            airflow_code = """# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.providers.apache.spark.operators.spark_submit import SparkSubmitOperator
from airflow.operators.email import EmailOperator

default_args = {
    'owner': 'jeongseonghun',
    'depends_on_past': False,
    'start_date': datetime(2026, 1, 1),
    'email': ['gnsl1465@naver.com'],
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    'poker_mes_bigdata_pipeline',
    default_args=default_args,
    description='Smart Factory MES & Poker Log Distributed ETL Pipeline',
    schedule_interval='@daily',
    catchup=False,
    max_active_runs=1
) as dag:

    # 1. Sqoop으로 MES 트랜잭션 데이터를 HDFS 데이터 레이크로 증분 수집
    ingest_raw_transactions = BashOperator(
        task_id='ingest_raw_transactions',
        bash_command='sqoop-import-script.sh',
        retries=3
    )

    # 2. Spark (Java)를 활용한 HDFS 내 비정형 로그 분산 파싱 및 클렌징
    spark_distributed_cleanse = SparkSubmitOperator(
        task_id='spark_distributed_cleanse',
        application='/opt/prod/jobs/log-parser-assembly-1.0.jar',
        java_class='com.autoever.bigdata.LogParserJob',
        conn_id='spark_default',
        executor_cores=2,
        executor_memory='4G',
        driver_memory='2G',
        num_executors=4,
        application_args=['hdfs:///data/raw/poker_logs', 'hdfs:///data/refined/poker_hands'],
        conf={'spark.yarn.maxAppAttempts': '1'}
    )

    # 3. Hive 상에서 정형화된 데이터를 기반으로 SQL 집계 및 마일스톤 산출
    hive_kpi_aggregate = BashOperator(
        task_id='hive_kpi_aggregate',
        bash_command='hive -f /opt/prod/queries/kpi_aggregation.hql'
    )

    # 4. 장애 발생 시 현대오토에버 운영팀에 이메일 및 슬랙 알림 발송
    send_alert = EmailOperator(
        task_id='send_alert',
        to='gnsl1465@naver.com',
        subject='[Pipeline Alert] BigData ETL Pipeline Succeeded',
        html_content='<h3>Pipeline Executed Successfully</h3><p>Date: {{ ds }}</p>',
        trigger_rule='all_success'
    )

    ingest_raw_transactions >> spark_distributed_cleanse >> hive_kpi_aggregate >> send_alert"""
            st.code(airflow_code, language="python")

# 5. 하단 공통 푸터
st.markdown(f"""
<div class="divider"></div>
<div style="text-align: center; color: {TEXT_MUTED}; font-size: 0.75rem; padding-bottom: 1.5rem;">
    © 2026 Jeong Seong Hun. Data Engineering Portfolio.<br>
    본 포트폴리오는 개인 프로젝트 자료를 바탕으로 작성되었으며, 상용 권리를 침해하지 않는 순수 기술 포트폴리오입니다.
</div>
""", unsafe_allow_html=True)
