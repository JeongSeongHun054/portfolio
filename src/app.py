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
    page_title="정성훈 | 데이터 엔지니어링 & 사이언스 포트폴리오",
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
        background: {CARD_BG_COLOR};
        border: 1px solid {BORDER_COLOR};
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1.2rem;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        transition: transform 0.2s, border-color 0.2s;
    }}}}
    .pf-card:hover {{{{
        transform: translateY(-2px);
        border-color: {ACCENT_BLUE};
    }}}}
    .pf-title {{{{
        font-size: 1.2rem;
        font-weight: 700;
        color: {TEXT_WHITE};
        margin-bottom: 0.5rem;
        display: flex;
        align-items: center;
        gap: 8px;
    }}}}
    .pf-subtitle {{{{
        font-size: 0.85rem;
        color: {ACCENT_BLUE};
        font-weight: 600;
        text-transform: uppercase;
        margin-bottom: 0.8rem;
    }}}}
    .pf-body {{{{
        font-size: 0.9rem;
        color: {TEXT_MUTED};
        line-height: 1.6;
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
    .badge-blue {{{{ color: {ACCENT_BLUE}; background: rgba(59, 130, 246, 0.1); border: 1px solid rgba(59, 130, 246, 0.2); }}}}
    .badge-green {{{{ color: {ACCENT_GREEN}; background: rgba(16, 185, 129, 0.1); border: 1px solid rgba(16, 185, 129, 0.2); }}}}
    .badge-orange {{{{ color: {ACCENT_ORANGE}; background: rgba(245, 158, 11, 0.1); border: 1px solid rgba(245, 158, 11, 0.2); }}}}
    
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
        <span style="font-size: 0.8rem; font-weight: 700; color: {ACCENT_BLUE}; text-transform: uppercase; letter-spacing: 0.1em;">DATA ENGINEERING & DATA SCIENCE INTEGRATED PORTFOLIO</span>
        <h1 style="margin: 5px 0 0 0; font-size: 2.3rem; font-weight: 800; color: {TEXT_WHITE}; letter-spacing: -0.02em;">비정형 로그 기반 데이터 엔지니어링 & 사이언스 통합 플랫폼</h1>
    </div>
    """, unsafe_allow_html=True)
with head_right:
    st.markdown(f"""
    <div style="text-align: right; margin-top: 10px;">
        <span class="badge badge-blue" style="font-size: 0.85rem; padding: 5px 12px;">Data Engineering</span><br>
        <span class="badge badge-green" style="font-size: 0.85rem; padding: 5px 12px; margin-top: 5px;">Data Science</span>
    </div>
    """, unsafe_allow_html=True)

# 4. 메인 탭 네비게이션 정의 (포트폴리오 핵심 구성)
tabs = st.tabs([
    "💼 Portfolio Home (포트폴리오 홈)",
    "🃏 Interactive Demo (실전 분석 데모)",
    "🛠️ Technical Deep Dive (기술 아키텍처)"
])

# =========================================================================
# TAB 1: Portfolio Home (플래그십 프로젝트 개요 및 기술 사양)
# =========================================================================
with tabs[0]:
    st.markdown(f"""
    <div class="pf-card" style="border-left: 4px solid {ACCENT_BLUE}; margin-bottom: 1.5rem;">
        <div class="pf-title">📊 프로젝트 개요: 포커 로그 기반 데이터 엔지니어링 & 사이언스 통합 파이프라인</div>
        <div class="pf-body" style="font-size: 0.95rem;">
            본 프로젝트는 비정형 텍스트 로그 파일의 수집 및 가공(ETL)부터 데이터베이스 다차원 모델링, 통계적 가설 검정, 그리고 기계학습 모델링에 이르는 <b>엔드투엔드 데이터 플랫폼</b> 개발 프로젝트입니다.<br>
            대량의 비정형 데이터 속에서 유의미한 행동 패턴을 정량적으로 추출하여 의사결정 시스템과 모니터링 대시보드를 연동함으로써, 실무적 데이터 아키텍처 구축 역량을 증명합니다.
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
            <div class="kpi-val" style="color: {ACCENT_GREEN};">80.2%</div>
            <div class="kpi-lbl">기계학습 행동 예측 정확도 (Accuracy)</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    col_h1, col_h2 = st.columns([6, 6])
    
    with col_h1:
        st.markdown(f"""
        <div class="pf-card" style="height: 100%;">
            <div class="pf-title" style="color: {ACCENT_BLUE};">🛠️ 데이터 엔지니어링 (DE) 핵심 사양</div>
            <div class="pf-body">
                비구조적 원천 데이터의 정형화 적재 및 대용량 실시간 쿼리 처리를 위한 데이터 아키텍처 설계 역량을 입증합니다.
                <ul style="margin-top: 0.8rem; padding-left: 1.2rem; color: {TEXT_MUTED}; font-size: 0.85rem; line-height: 1.6;">
                    <li><b>비정형 데이터 정제 (ETL)</b>: 정규표현식을 통해 텍스트 로그 파일의 한 행 단위로 이벤트를 파싱하여 무손실(100% 성공률) 정형 데이터로 변환.</li>
                    <li><b>관계형 데이터베이스 모델링 (RDBMS)</b>: 3NF(제3정규형) 준수 스키마 설계를 통해 데이터 중복을 방지하고 트랜잭션 무결성을 확보(hands, actions, players, tournaments 테이블 관계 정의).</li>
                    <li><b>이기종 DB 호환 (Dual DB)</b>: SQLite와 PostgreSQL 간의 SQL Dialect 문법 차이를 데이터 접근 계층(Connector)에서 추상화 및 캡슐화하여 인프라 마이그레이션 유연성 확보.</li>
                </ul>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
    with col_h2:
        st.markdown(f"""
        <div class="pf-card" style="height: 100%;">
            <div class="pf-title" style="color: {ACCENT_GREEN};">🔬 데이터 사이언스 (DS) 핵심 사양</div>
            <div class="pf-body">
                가공 완료된 테이블을 기반으로 고급 통계 기법과 머신러닝 알고리즘을 적용하여 데이터 기반 예측 및 인사이트를 도출합니다.
                <ul style="margin-top: 0.8rem; padding-left: 1.2rem; color: {TEXT_MUTED}; font-size: 0.85rem; line-height: 1.6;">
                    <li><b>사용자 플레이어 군집화 (Clustering)</b>: VPIP, PFR, AF 등 행동 지표를 표준화 전처리 후 K-Means 알고리즘을 사용해 유저의 플레이 성향(K=4) 자동 세분화.</li>
                    <li><b>행동 예측 머신러닝 (ML)</b>: 초기 라운드 베팅 패턴을 학습하여 최종 쇼다운(패 공개) 진출 여부를 예측하는 랜덤 포레스트 앙상블 분류 모델 구축.</li>
                    <li><b>통계적 가설 검정 (T-Test)</b>: 특정 플레이 조건에 따른 기대 수익률 차이의 유의성을 독립표본 T-검정으로 분석하고, 표본 크기 및 편차 노이즈의 통계적 검정력을 분석하여 한계점 보완 솔루션 설계.</li>
                </ul>
            </div>
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
        <h2 style="font-size: 1.8rem; font-weight: 800; color: {TEXT_WHITE};">🛠️ 데이터 엔지니어링 및 사이언스 기술 명세 (Technical Deep-Dive)</h2>
        <p style="font-size: 0.9rem; color: {TEXT_MUTED};">기술 면접 및 아키텍처 검증을 위해 세부적인 데이터 파이프라인 명세와 DB 스키마 설계, 그리고 머신러닝 파이프라인의 내부 작동 사양을 상세히 공개합니다.</p>
    </div>
    """, unsafe_allow_html=True)
    
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
                hand_id_pattern = re.compile(r"PokerStars Hand #(\d+):")<br>
                action_pattern = re.compile(r"(\w+): (calls|bets|raises|folds)\s*(\d*)")
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
            <div class="pf-title" style="color: {ACCENT_GREEN};">3. 머신러닝 기반 성향 군집 및 예측 파이프라인 (DS)</div>
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
            <div class="pf-title" style="color: {ACCENT_GREEN};">4. A/B 테스트 및 T-Test 가설 검정 (DS)</div>
            <div class="pf-body" style="font-size: 0.85rem;">
                데이터 사이언티스트로서 데이터 뒤에 숨겨진 실제 유의성을 통계학적으로 판별하기 위한 분석 체계를 내장했습니다.<br><br>
                <b>[실전 가설 검정 시나리오]</b><br>
                * <b>귀무가설(H0)</b>: 프리미엄 패를 쥐었을 때 선제 공격(Raise)을 한 그룹과 수동적 대응(Call)을 한 그룹 간의 평균 수익 차이는 우연일 뿐, 실제 차이가 없다.<br>
                * <b>대립가설(H1)</b>: 선제 공격을 한 그룹의 평균 수익이 통계적으로 유의미하게 더 높다.<br><br>
                <b>[통계적 보완 의사결정]</b><br>
                실제 독립표본 T-검정 실행 결과 p-value가 0.05 이상으로 산출되어 귀무가설을 일차적으로 채택했습니다. 이는 도메인의 초고변동성(표준편차가 평균 수익차 대비 15배 이상 높은 현상) 때문임을 정량 분석해 냈습니다. 단순히 분석 완료로 끝내는 것이 아니라, <b>"데이터 아웃라이어 정제 및 표본 크기(Sample Size)의 확장 검정력을 고려한 2차 재검정 보완 로드맵"</b>을 수립함으로써 실무 데이터 분석가로서의 타당성 있는 의사결정 프로세스를 입증했습니다.
            </div>
        </div>
        """, unsafe_allow_html=True)

# 5. 하단 공통 푸터
st.markdown(f"""
<div class="divider"></div>
<div style="text-align: center; color: {TEXT_MUTED}; font-size: 0.75rem; padding-bottom: 1.5rem;">
    © 2026 Jeong Seong Hun. Data Engineering & Data Science Portfolio.<br>
    본 포트폴리오는 개인 프로젝트 자료를 바탕으로 작성되었으며, 상용 권리를 침해하지 않는 순수 기술 포트폴리오입니다.
</div>
""", unsafe_allow_html=True)
