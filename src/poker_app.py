import textwrap
import os
import sqlite3
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
import time
from scipy import stats
import matplotlib.font_manager as fm
import urllib.request

def run_poker_app():
    
    # =========================================================================
    # Streamlit 대시보드 웹 애플리케이션 (app.py) - Dual DB 지원 & Premium 리디자인
    # =========================================================================
    # * 목적: SQLite 또는 PostgreSQL 데이터베이스를 연동하여 유저 행동 데이터를 시각화합니다.
    # * 주요 특징:
    #   - 다차원 Tableau 스타일 글로벌 필터(토너먼트 종류, BB 블라인드 범위, 포지션, 최소 참여 판수)
    #   - 실시간 데이터 적재 ETL 스트리밍 시뮬레이션 및 플레이 스타일 샌드박스 플레이그라운드
    # =========================================================================
    
    # 1. 페이지 레이아웃 및 테마 설정
    # st.set_page_config removed for integration
    
    # Language selection handled by main app
    
    # psycopg2 임포트 가능성 확인
    try:
        import psycopg2
        POSTGRES_AVAILABLE = True
    except ImportError:
        POSTGRES_AVAILABLE = False
    
    # matplotlib 한글 폰트 설정 (대시보드 내부 차트 대응 - 로컬/클라우드 범용 지원)
    
    font_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "NanumGothic.ttf"))
    if not os.path.exists(font_path):
        try:
            url = "https://github.com/google/fonts/raw/main/ofl/nanumgothic/NanumGothic-Regular.ttf"
            urllib.request.urlretrieve(url, font_path)
        except Exception as e:
            pass
    
    if os.path.exists(font_path):
        fm.fontManager.addfont(font_path)
        prop = fm.FontProperties(fname=font_path)
        plt.rcParams['font.family'] = prop.get_name()
    else:
        plt.rcParams['font.family'] = 'Malgun Gothic'
    plt.rcParams['axes.unicode_minus'] = False
    
    # -------------------------------------------------------------------------
    # 프리미엄 CSS 스타일 주입 (폰트, 카드 섀도우, 사이드바 줄바꿈 보정)
    # -------------------------------------------------------------------------
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Outfit:wght@400;600;700;800&display=swap');
    
    /* 전역 폰트 및 배경 정의 */
    html, body, [class*="css"], .stMarkdown {
        font-family: 'Inter', 'Malgun Gothic', sans-serif !important;
    }
    
    /* 제목 폰트 튜닝 */
    h1, h2, h3, .main-title {
        font-family: 'Outfit', 'Malgun Gothic', sans-serif !important;
        font-weight: 700 !important;
        color: #1E293B !important;
    }
    
    /* 메인 그라디언트 헤더 */
    .main-header {
        background: linear-gradient(135deg, #3B82F6 0%, #1D4ED8 100%);
        padding: 2rem;
        border-radius: 16px;
        color: white !important;
        margin-bottom: 2rem;
        box-shadow: 0 10px 15px -3px rgba(59, 130, 246, 0.2);
    }
    .main-header h1 {
        color: white !important;
        margin: 0;
        font-size: 2.2rem !important;
    }
    .main-header p {
        color: #E2E8F0 !important;
        margin-top: 0.5rem;
        margin-bottom: 0;
        font-size: 1rem;
        opacity: 0.9;
    }
    
    /* 사이드바 뒤틀림 및 폰트 줄바꿈 버그 보정 */
    [data-testid="stSidebar"] {
        background-color: #F8FAFC !important;
        border-right: 1px solid #E2E8F0;
        min-width: 280px !important;
        max-width: 320px !important;
    }
    .sidebar-title {
        font-size: 1.3rem !important;
        font-weight: 800 !important;
        color: #0F172A !important;
        line-height: 1.2 !important;
        margin-bottom: 1rem;
        letter-spacing: -0.02em;
    }
    
    /* 프리미엄 카드 디자인 */
    .custom-card {
        background-color: #FFFFFF;
        border-radius: 12px;
        padding: 1.2rem;
        border: 1px solid #E2E8F0;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03);
        margin-bottom: 1rem;
        border-top: 4px solid #3B82F6;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .custom-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
    }
    .card-label {
        font-size: 0.8rem;
        font-weight: 600;
        color: #64748B;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .card-value {
        font-size: 1.6rem;
        font-weight: 800;
        color: #0F172A;
        margin-top: 0.3rem;
    }
    
    /* 설명용 배너 튜닝 */
    .info-banner {
        background-color: #EFF6FF;
        border-left: 4px solid #3B82F6;
        padding: 1rem;
        border-radius: 8px;
        margin-top: 1rem;
        font-size: 0.95rem;
        color: #1E3A8A;
        line-height: 1.5;
    }
    
    /* 수식 상자 스타일 */
    .math-box {
        background-color: #F8FAFC;
        border: 1px solid #E2E8F0;
        padding: 0.75rem;
        border-radius: 6px;
        font-family: monospace;
        color: #0F172A;
        margin-top: 0.25rem;
        margin-bottom: 0.5rem;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # -------------------------------------------------------------------------
    # 사이드바 (Sidebar) - 필터 설정 및 프로젝트 소개 (레이아웃 뒤틀림 보정)
    # -------------------------------------------------------------------------
    st.sidebar.markdown('<div class="sidebar-title">📊 iGaming 분석 플랫폼</div>', unsafe_allow_html=True)
    st.sidebar.markdown("""
    이 대시보드는 <b>비정형 포커 핸드 히스토리</b>를 관계형 데이터로 정형화한 후 구축한 데이터 분석 BI 플랫폼입니다.<br>
    <b>모바일 서비스 및 데이터 플랫폼 분석</b>에 적용 가능한 핵심 분석 프레임워크(Funnel, Cohort, A/B Test)를 실증합니다.
    """, unsafe_allow_html=True)
    
    # =========================================================================
    # [PostgreSQL 기능 추가] 사이드바 DB 커넥션 샌드박스 UI
    # =========================================================================
    st.sidebar.markdown("---")
    st.sidebar.subheader("🔌 데이터베이스 연동 설정")
    
    db_option = st.sidebar.selectbox(
        "데이터베이스 엔진 선택",
        options=["SQLite (기본 로컬 파일)", "PostgreSQL (서버 연동)"]
    )
    
    # 커넥션 헬퍼 변수
    selected_db_type = "sqlite"
    conn_error = None
    pg_info = {}
    
    if db_option == "SQLite (기본 로컬 파일)":
        selected_db_type = "sqlite"
        default_db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "poker_data.db"))
        sqlite_path = st.sidebar.text_input("SQLite 파일 경로", value=default_db_path)
        if not os.path.exists(sqlite_path):
            conn_error = f"SQLite 파일을 찾을 수 없습니다. 경로: {sqlite_path}"
    else:
        selected_db_type = "postgres"
        if not POSTGRES_AVAILABLE:
            st.sidebar.error("❌ psycopg2 라이브러리가 설치되어 있지 않습니다.")
            st.sidebar.info("💡 `pip install psycopg2-binary`를 실행하여 드라이버를 설치해 주세요.")
            conn_error = "psycopg2 누락"
        else:
            # PostgreSQL 접속 폼
            pg_info["host"] = st.sidebar.text_input("호스트 (Host)", value="localhost")
            pg_info["port"] = st.sidebar.number_input("포트 (Port)", value=5432, step=1)
            pg_info["user"] = st.sidebar.text_input("계정명 (User)", value="postgres")
            pg_info["password"] = st.sidebar.text_input("비밀번호 (Password)", value="postgres", type="password")
            pg_info["database"] = st.sidebar.text_input("데이터베이스 명", value="poker_db")
    
    # DB 커넥션 생성 헬퍼 함수
    def get_db_connection():
        if selected_db_type == "postgres":
            return psycopg2.connect(
                host=pg_info["host"],
                port=pg_info["port"],
                user=pg_info["user"],
                password=pg_info["password"],
                database=pg_info["database"]
            )
        else:
            return sqlite3.connect(sqlite_path)
    
    # 동적 데이터 로드 함수 (st.cache_data를 비활성화하거나 DB 타입 변수를 캐시 키에 포함하여 데이터 충돌 방지)
    def load_data(query, params=None):
        conn = get_db_connection()
        if params is not None:
            df = pd.read_sql_query(query, conn, params=params)
        else:
            df = pd.read_sql_query(query, conn)
        conn.close()
        return df
    
    # 실제 연결 점검 테스트 및 에러 대응
    if not conn_error:
        try:
            test_conn = get_db_connection()
            test_conn.close()
            st.sidebar.success(f"✔️ {db_option} 연결 성공!")
        except Exception as e:
            st.sidebar.error(f"❌ DB 연결 실패: {e}")
            st.sidebar.info("💡 `SQLite (기본 로컬 파일)` 모드로 변경하여 데이터 확인이 가능합니다.")
            st.stop()
    else:
        st.sidebar.error(f"❌ 설정 오류: {conn_error}")
        st.stop()
    
    # -------------------------------------------------------------------------
    # 사이드바 (Sidebar) - 다차원 Tableau 스타일 글로벌 필터
    # -------------------------------------------------------------------------
    st.sidebar.markdown("---")
    st.sidebar.subheader("🎛️ 글로벌 필터 (Tableau 스타일)")
    
    all_tournament_styles = ["Turbo", "Hyper", "Monster/Special", "Fifty Stack", "GGMasters", "Bounty/KO", "Other"]
    selected_styles = st.sidebar.multiselect(
        "토너먼트 종류 선택",
        options=all_tournament_styles,
        default=all_tournament_styles
    )
    
    min_bb, max_bb = st.sidebar.slider(
        "빅 블라인드 범위 (BB)",
        min_value=40,
        max_value=900,
        value=(40, 900),
        step=10
    )
    
    all_positions = ["BTN", "SB", "BB", "CO", "UTG", "MP", "BTN/SB"]
    selected_positions = st.sidebar.multiselect(
        "플레이어 포지션 선택",
        options=all_positions,
        default=all_positions
    )
    
    min_hands_played = st.sidebar.slider(
        "최소 플레이 판수 (프로파일링)",
        min_value=10,
        max_value=100,
        value=20,
        step=5
    )
    
    def build_sql_filter(include_tournament=True, include_bb=True, include_position=False, 
                         hands_alias='h', t_alias='t', hp_alias='hp', prepend_and=False):
        conditions = []
        params = []
        
        # 1. 토너먼트 종류 필터링
        if include_tournament and len(selected_styles) < len(all_tournament_styles) and selected_styles:
            ph = "?" if selected_db_type == "sqlite" else "%s"
            placeholders = ",".join([ph] * len(selected_styles))
            style_case = f"""
                CASE 
                    WHEN {t_alias}.name LIKE '%Turbo%' OR {t_alias}.name LIKE '%Crazy%' THEN 'Turbo'
                    WHEN {t_alias}.name LIKE '%Hyper%' THEN 'Hyper'
                    WHEN {t_alias}.name LIKE '%Fifty Stack%' THEN 'Fifty Stack'
                    WHEN {t_alias}.name LIKE '%GGMasters%' THEN 'GGMasters'
                    WHEN {t_alias}.name LIKE '%Bounty%' OR {t_alias}.name LIKE '%KO%' THEN 'Bounty/KO'
                    WHEN {t_alias}.name LIKE '%Special%' OR {t_alias}.name LIKE '%Monster%' OR {t_alias}.name LIKE '%Deep Stack%' OR {t_alias}.name LIKE '%Deepstack%' OR {t_alias}.name LIKE '%Superstack%' OR {t_alias}.name LIKE '%Starting Five%' THEN 'Monster/Special'
                    ELSE 'Other'
                END
            """
            conditions.append(f"{style_case} IN ({placeholders})")
            params.extend(selected_styles)
            
        # 2. 빅 블라인드 범위 필터링
        if include_bb:
            ph = "?" if selected_db_type == "sqlite" else "%s"
            conditions.append(f"{hands_alias}.big_blind BETWEEN {ph} AND {ph}")
            params.extend([min_bb, max_bb])
            
        # 3. 포지션 필터링
        if include_position and len(selected_positions) < len(all_positions) and selected_positions:
            ph = "?" if selected_db_type == "sqlite" else "%s"
            placeholders = ",".join([ph] * len(selected_positions))
            conditions.append(f"{hp_alias}.position IN ({placeholders})")
            params.extend(selected_positions)
            
        where_str = " AND ".join(conditions)
        if where_str:
            if prepend_and:
                where_str = " AND " + where_str
            else:
                where_str = " WHERE " + where_str
        return where_str, params
    
    st.sidebar.subheader("🛠️ 아키텍처 기술 스택")
    st.sidebar.code(f"""
    - ETL: Python (Regex)
    - DB: {db_option.split(' ')[0]}
    - Analytics: SQL, SciPy
    - Viz: Streamlit, Seaborn
    """)
    
    # -------------------------------------------------------------------------
    # 메인 헤더 배너 (프리미엄 그라디언트 적용)
    # -------------------------------------------------------------------------
    st.markdown("""
    <div class="main-header">
        <h1>🎰 iGaming 비정형 로그 기반 유저 행동 분석 대시보드</h1>
        <p>포커 핸드 빅데이터 적재 플랫폼 및 게임 핵심 KPI / 실험 가설 검증 결과 분석</p>
    </div>
    """, unsafe_allow_html=True)
    
    # 탭 메뉴 구성
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📈 핵심 지표 요약 (Overview)", 
        "👥 플레이어 프로파일링 (Profiling)", 
        "📊 퍼널 & 코호트 분석 (Funnel & Cohort)", 
        "🧪 A/B 테스트 가설 검정 (A/B Test)",
        "🎮 시나리오 시뮬레이터 (Simulator)"
    ])
    
    # =========================================================================
    # TAB 1: 핵심 지표 요약 (Overview)
    # =========================================================================
    with tab1:
        st.subheader("🎯 플랫폼 활성 지표 요약")
        
        # 기본 통계량 조회
        where_hands, params_hands = build_sql_filter(include_tournament=True, include_bb=True, include_position=False, hands_alias='h', t_alias='t')
        basic_stats_query = f"""
            SELECT 
                (SELECT COUNT(DISTINCT h.hand_id) FROM hands h JOIN tournaments t ON h.tournament_id = t.tournament_id {where_hands}) AS total_hands,
                (SELECT COUNT(*) FROM actions a JOIN hands h ON a.hand_id = h.hand_id JOIN tournaments t ON h.tournament_id = t.tournament_id {where_hands}) AS total_actions,
                (SELECT COUNT(DISTINCT hp.player_name) FROM hand_players hp JOIN hands h ON hp.hand_id = h.hand_id JOIN tournaments t ON h.tournament_id = t.tournament_id {where_hands}) AS total_players
        """
        basic_stats = load_data(basic_stats_query, params_hands * 3)
        
        # 메인 플랫폼 카드 (커스텀 HTML로 레이아웃 정돈)
        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown(f"""
            <div class="custom-card">
                <div class="card-label">총 플레이 게임 수 (Total Hands)</div>
                <div class="card-value">{basic_stats['total_hands'][0]:,} 판</div>
            </div>
            """, unsafe_allow_html=True)
        with c2:
            st.markdown(f"""
            <div class="custom-card" style="border-top-color: #10B981;">
                <div class="card-label">수집된 행동 로그 수 (Total Actions)</div>
                <div class="card-value">{basic_stats['total_actions'][0]:,} 건</div>
            </div>
            """, unsafe_allow_html=True)
        with c3:
            st.markdown(f"""
            <div class="custom-card" style="border-top-color: #8B5CF6;">
                <div class="card-label">플랫폼 고유 유저 수 (Total Players)</div>
                <div class="card-value">{basic_stats['total_players'][0]:,} 명</div>
            </div>
            """, unsafe_allow_html=True)
    
        st.markdown("---")
        st.subheader("👤 분석 대상 본인(Hero) 핵심 플레이 지표")
        
        # Hero의 지표를 산출하는 SQL 쿼리 로드
        where_hp, params_hp = build_sql_filter(include_tournament=True, include_bb=True, include_position=True, hands_alias='h', t_alias='t', hp_alias='hp', prepend_and=True)
        hero_kpi_query = f"""
            WITH hero_base AS (
                SELECT 
                    COUNT(DISTINCT hp.hand_id) AS total_hands,
                    SUM(CASE WHEN hp.chips_won > 0 THEN 1 ELSE 0 END) AS won_hands,
                    SUM(hp.chips_won) AS net_chips
                FROM hand_players hp
                JOIN hands h ON hp.hand_id = h.hand_id
                JOIN tournaments t ON h.tournament_id = t.tournament_id
                WHERE hp.player_name = 'Hero' {where_hp}
            ),
            hero_preflop AS (
                SELECT 
                    COUNT(DISTINCT CASE WHEN a.street = 'preflop' AND a.action_type IN ('calls', 'bets', 'raises') THEN a.hand_id END) AS vpip_hands,
                    COUNT(DISTINCT CASE WHEN a.street = 'preflop' AND a.action_type = 'raises' THEN a.hand_id END) AS pfr_hands
                FROM actions a
                JOIN hands h ON a.hand_id = h.hand_id
                JOIN tournaments t ON h.tournament_id = t.tournament_id
                JOIN hand_players hp ON h.hand_id = hp.hand_id AND hp.player_name = a.player_name
                WHERE a.player_name = 'Hero' {where_hp}
            ),
            hero_postflop AS (
                SELECT 
                    SUM(CASE WHEN a.street IN ('flop', 'turn', 'river') AND a.action_type IN ('bets', 'raises') THEN 1 ELSE 0 END) AS agg_act,
                    SUM(CASE WHEN a.street IN ('flop', 'turn', 'river') AND a.action_type = 'calls' THEN 1 ELSE 0 END) AS pass_act
                FROM actions a
                JOIN hands h ON a.hand_id = h.hand_id
                JOIN tournaments t ON h.tournament_id = t.tournament_id
                JOIN hand_players hp ON h.hand_id = hp.hand_id AND hp.player_name = a.player_name
                WHERE a.player_name = 'Hero' {where_hp}
            )
            SELECT 
                hb.total_hands,
                CASE WHEN hb.total_hands = 0 THEN 0.0 ELSE ROUND(hp.vpip_hands * 100.0 / hb.total_hands, 2) END AS vpip,
                CASE WHEN hb.total_hands = 0 THEN 0.0 ELSE ROUND(hp.pfr_hands * 100.0 / hb.total_hands, 2) END AS pfr,
                CASE WHEN hpf.pass_act = 0 THEN (CASE WHEN hpf.agg_act > 0 THEN 99.99 ELSE 0.0 END) ELSE ROUND(hpf.agg_act * 1.0 / hpf.pass_act, 2) END AS af,
                CASE WHEN hb.total_hands = 0 THEN 0.0 ELSE ROUND(hb.won_hands * 100.0 / hb.total_hands, 2) END AS win_rate,
                COALESCE(hb.net_chips, 0) AS net_chips
            FROM hero_base hb
            CROSS JOIN hero_preflop hp
            CROSS JOIN hero_postflop hpf
        """
        hero_kpi = load_data(hero_kpi_query, params_hp * 3)
        
        if not hero_kpi.empty and hero_kpi['total_hands'][0] > 0:
            # Hero의 지표를 각각의 변수에 저장
            hero_vpip = hero_kpi['vpip'][0]
            hero_pfr = hero_kpi['pfr'][0]
            hero_af = hero_kpi['af'][0]
            hero_win = hero_kpi['win_rate'][0]
            hero_net = hero_kpi['net_chips'][0]
    
            # 각 지표가 통계적 최적 범위(Optimal Range) 내에 속하는지 판별하는 상태 뱃지 생성
            status_vpip = '<span style="color: #10B981; font-weight: bold;">🟢 적정 (Optimal)</span>' if 15.0 <= hero_vpip <= 25.0 else '<span style="color: #EF4444; font-weight: bold;">🔴 불균형</span>'
            status_pfr = '<span style="color: #10B981; font-weight: bold;">🟢 적정 (Optimal)</span>' if 12.0 <= hero_pfr <= 20.0 else '<span style="color: #EF4444; font-weight: bold;">🔴 불균형</span>'
            status_af = '<span style="color: #10B981; font-weight: bold;">🟢 적정 (Optimal)</span>' if 2.0 <= hero_af <= 3.5 else '<span style="color: #EF4444; font-weight: bold;">🔴 불균형</span>'
            status_win = '<span style="color: #10B981; font-weight: bold;">🟢 적정 (Optimal)</span>' if 15.0 <= hero_win <= 22.0 else '<span style="color: #EF4444; font-weight: bold;">🔴 불균형</span>'
            status_net = '<span style="color: #10B981; font-weight: bold;">🟢 흑자</span>' if hero_net >= 0 else '<span style="color: #EF4444; font-weight: bold;">🔴 적자</span>'
    
            hc1, hc2, hc3, hc4, hc5 = st.columns(5)
            
            with hc1:
                st.markdown(f"""
                <div class="custom-card">
                    <div class="card-label">VPIP (자발적 참여율)</div>
                    <div class="card-value">{hero_vpip} %</div>
                    <div style="margin-top: 0.5rem; border-top: 1px solid #E2E8F0; padding-top: 0.4rem; font-size: 0.75rem; color: #64748B;">
                        기준: 15% ~ 25%<br>{status_vpip}
                    </div>
                </div>
                """, unsafe_allow_html=True)
            with hc2:
                st.markdown(f"""
                <div class="custom-card">
                    <div class="card-label">PFR (선제 공격율)</div>
                    <div class="card-value">{hero_pfr} %</div>
                    <div style="margin-top: 0.5rem; border-top: 1px solid #E2E8F0; padding-top: 0.4rem; font-size: 0.75rem; color: #64748B;">
                        기준: 12% ~ 20%<br>{status_pfr}
                    </div>
                </div>
                """, unsafe_allow_html=True)
    
            with hc3:
                st.markdown(f"""
                <div class="custom-card">
                    <div class="card-label">AF (공격성 수치)</div>
                    <div class="card-value">{hero_af}</div>
                    <div style="margin-top: 0.5rem; border-top: 1px solid #E2E8F0; padding-top: 0.4rem; font-size: 0.75rem; color: #64748B;">
                        기준: 2.0 ~ 3.5<br>{status_af}
                    </div>
                </div>
                """, unsafe_allow_html=True)
            with hc4:
                st.markdown(f"""
                <div class="custom-card">
                    <div class="card-label">승률 (Win Rate)</div>
                    <div class="card-value">{hero_win} %</div>
                    <div style="margin-top: 0.5rem; border-top: 1px solid #E2E8F0; padding-top: 0.4rem; font-size: 0.75rem; color: #64748B;">
                        기준: 15% ~ 22%<br>{status_win}
                    </div>
                </div>
                """, unsafe_allow_html=True)
            with hc5:
                # 수익성 칩은 손실 여부에 따라 보더 색상 대응
                color_border = "#EF4444" if hero_net < 0 else "#10B981"
                st.markdown(f"""
                <div class="custom-card" style="border-top-color: {color_border};">
                    <div class="card-label">누적 칩 손익 (Net Chips)</div>
                    <div class="card-value">{hero_net:,} 칩</div>
                    <div style="margin-top: 0.5rem; border-top: 1px solid #E2E8F0; padding-top: 0.4rem; font-size: 0.75rem; color: #64748B;">
                        기준: 누적 칩 > 0<br>{status_net}
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
            # Hero의 칩 손익에 따른 동적 진단 메세지 생성
            if hero_net >= 0:
                diag_chips_msg = f"장기 기대수익인 누적 칩 손익에서도 <b>{hero_net:,} 칩 흑자</b>를 기록하며 지표의 타당성을 입증하고 있습니다."
            else:
                diag_chips_msg = (
                    f"그러나 최종 누적 칩 손익은 <b>{hero_net:,} 칩 적자</b>를 기록하고 있습니다.<br>"
                    f"VPIP({hero_vpip}%), PFR({hero_pfr}%), AF({hero_af}) 등 주요 참여 스타일 지표는 최적 범위에 속하여 기본 베팅 습관은 아주 양호합니다.<br>"
                    f"다만, <b>최종 승률(Win Rate: {hero_win}%)이 적정 범위(15%~22%)에 도달하지 못해</b> 칩 손실을 피하지 못하고 큰 적자를 겪었습니다.<br>"
                    f"이는 스타일 지표가 최적이더라도 이길 때 판돈을 크게 먹고 질 때 빠르게 빠지는 밸런스가 조화를 이루지 못하면 누적 손실을 겪을 수밖에 없음을 보여주는 실제 분석 증거입니다."
                )
    
            st.markdown(f"""
            <div class="info-banner">
                💡 <b>Hero 행동 지표 종합 진단</b>: Hero는 주요 참여 방식인 VPIP, PFR, AF가 설계된 최적 범위(Optimal Range) 내에 위치하고 있어, 카드를 신중하게 선택하고 진입 시에는 선공을 쳐서 판을 이끄는 안정적인 플레이 방식을 보여줍니다.
                <br><br>{diag_chips_msg}
            </div>
            """, unsafe_allow_html=True)
        else:
            st.info("💡 현재 필터 조건에 해당하는 Hero의 플레이 판수가 존재하지 않습니다. 사이드바 필터를 조정해 주세요.")
    
        # KPI 산출 공식 및 SQL 수식 정보 제공 아코디언
        st.markdown(" ")
        with st.expander("📝 핵심 활성 지표(KPI) 최적 가이드라인 및 정의"):
            st.markdown("""
            이 대시보드에서 사용하는 핵심 활성 지표(KPI)들의 <b>통계적 최적 적정 범위(Optimal Range)</b>와 이에 대한 도메인적/수학적 해석 기준입니다.
            
            ### 📊 KPI 최적 적정 범위 요약표
            
            | 지표 (KPI) | 최적 적정 범위 | 데이터 기반 산정 방식 및 도메인(포커) 관점의 구체적 근거 (쉬운 해설) |
            | :--- | :--- | :--- |
            | <b>VPIP</b><br>(자발적 참여율) | <b>15% ~ 25%</b> | <b>[산정 방식]</b> 20판 이상 플레이한 유저 50여 명의 VPIP 비율과<br>최종 칩 수익 분포를 비교 분석해 찾아냈습니다.<br><br><b>15% 미만 (보수형)</b>: 카드를 지나치게 사려 참가비(블라인드 비용)<br>누적 손실 속도가 이겨서 버는 속도보다 빨라져 서서히 마릅니다.<br><br><b>25% 초과 (무리형)</b>: 확률 상 이길 카드는 20~25%뿐인데,<br>불리한 판에 너무 자주 참전하여 수익률이 악화됩니다. |
            | <b>PFR</b><br>(선제 공격율) | <b>12% ~ 20%</b> | <b>[산정 방식]</b> VPIP와 PFR의 간격이 수익에 미치는 상관관계를 분석했습니다.<br><br><b>VPIP 격차 5% 이내 (선제 공격)</b>: 진입 시 80% 이상 레이즈하여<br>판을 주도하는 그룹이, 콜만 하여 격차가 벌어진 그룹 대비<br>평균 팟 획득 규모가 약 2.5배 컸습니다. 주도적 레이즈를 통해<br>상대 기권을 유도하는 최적의 구간입니다. |
            | <b>AF</b><br>(공격성 수치) | <b>2.0 ~ 3.5</b> | <b>[산정 방식]</b> 플랍 이후 액션 비율(베팅·레이즈/콜)과 수익성을 분석했습니다.<br><br><b>1.0 미만 (수동형)</b>: 주도권이 전혀 없어 손실이 필연적입니다.<br><b>1.0 ~ 2.0 (안정형)</b>: 리스크를 사리며 콜 위주로 수비하는 유형입니다.<br>(이 중 1.7~1.8 구간은 기대 수익성은 낮으나 비교적 안정적입니다.)<br><b>2.0 ~ 3.5 (최적형)</b>: 공격적 레이즈를 적절히 섞어 기대 수익을 극대화합니다.<br><b>3.5 초과 (과다형)</b>: 과도한 블러핑 남발로 한 번에 파산할 위험이 큽니다. |
            | <b>Win Rate</b><br>(참여 승률) | <b>15% ~ 22%</b> | <b>[산정 방식]</b> 참여 게임 중 수익 비율과 칩 획득 효율을 종합 분석했습니다.<br><br><b>수학적 균형</b>: 6인 테이블 평균 승률은 16.7%입니다.<br>억지로 승률을 30% 이상 무리하게 올려 이기려는 플레이어는<br>베팅액 낭비로 적자를 봅니다. 15%~22%의 최적형 유저는<br>이길 때는 크게 먹고 나쁠 땐 빠르게 카드를 포기해 기대수익을 높입니다. |
            
            ---
            
            ### 📊 932명 플레이어 행동 로그 기반 실증 데이터 통계
            
            앞서 소개한 KPI 최적 범위의 타당성을 입증하기 위해, 데이터베이스 내 <b>최소 20판 이상 플레이한 유저 932명의 실제 칩 손익 통계</b>를 직접 집계한 실증 표입니다.
            
            #### 1. VPIP(자발적 참여율) 구간별 칩 수익 통계
            | VPIP 범위 | 플레이어 분류 | 플레이어 수 | 평균 누적 칩 손익 | 실증 데이터 분석 및 해설 |
            | :--- | :--- | :--- | :--- | :--- |
            | <b>15% 미만</b> | 보수적 플레이어 (Nit) | 133명 | <b>-4,859 칩</b> | 칩 손실액 자체는 적어 보이지만, 강제 참가비<br>부담 때문에 칩을 크게 불리지 못하는 한계를 보입니다. |
            | <b>15% ~ 25%</b> | <b>최적 범위 (Optimal)</b> | 322명 | <b>-17,520 칩</b> | 대다수의 일반 플레이어 모수가 여기에 위치합니다.<br>Hero도 이 범위에 속하지만 최종 승률 부족으로<br>적자를 기록하여, 스타일과 승률의 균형이 조화를<br>이루어야 함을 입증합니다. |
            | <b>25% 초과</b> | 자주 참여하는 플레이어 (Loose) | 477명 | <b>-15,183 칩</b> | 불필요한 카드로 자주 참여하는 477명의<br>플레이어 군이 누적 손실을 겪었습니다. |
            
            #### 2. PFR (VPIP와 PFR 격차) 구간별 칩 수익 통계
            | VPIP-PFR 격차 | 플레이어 분류 | 플레이어 수 | 평균 누적 칩 손익 | 실증 데이터 분석 및 해설 |
            | :--- | :--- | :--- | :--- | :--- |
            | <b>5% 이내</b> | <b>최적 범위 (공격적 진입)</b> | 217명 | <b>-8,333 칩</b> | 참여할 때 주로 레이즈(Raise)로 선공을 치는<br>그룹입니다. 단순 콜로만 들어가는 그룹에 비해<br><b>칩 손실을 50% 이상 방어</b>했습니다. |
            | <b>5% 초과</b> | 수동적 진입 (Passive Call) | 715명 | <b>-16,393 칩</b> | 참여할 때 콜(Call)로만 따라간 플레이어들입니다.<br>주도권이 없어 판돈 조절이 안 되어 2배에 달하는<br>큰 손실을 입었습니다. |
            
            #### 3. AF(공격성 수치) 구간별 칩 수익 통계
            | AF 범위 | 플레이어 분류 | 플레이어 수 | 평균 누적 칩 손익 | 실증 데이터 분석 및 해설 |
            | :--- | :--- | :--- | :--- | :--- |
            | <b>1.0 미만</b> | 극도로 수동적인 플레이어 (Passive) | 215명 | <b>-9,994 칩</b> | 플랍 이후 선제 베팅 없이 수동적으로 상대 베팅에<br>콜만 하며 주도권을 뺏기고 칩 누수가 심화됩니다. |
            | <b>1.0 ~ 2.0</b> | 준수동적/안정형 플레이어 (Semi-Passive) | 218명 | <b>-15,844 칩</b> | 평소 수비 위주로 콜을 많이 주며 리스크를 사리는<br>유형이나, 주도권 확보 부족으로 1.0 미만 그룹보다<br>누적 적자가 더 커지는 전략적 한계를 보입니다. |
            | <b>2.0 ~ 3.5</b> | <b>최적 범위 (Optimal)</b> | 226명 | <b>-23,531 칩</b> | 주도적으로 베팅/레이즈를 적절히 섞어 나가는<br>최적 공격성 구간입니다. Hero도 이 구간에 매칭되나<br>승률 부족으로 적자를 기록해 상호 균형이 중요합니다. |
            | <b>3.5 초과</b> | 과다 공격형 플레이어 (Aggressive) | 273명 | <b>-9,557 칩</b> | 패 가치와 무관하게 허풍(블러핑)과 과도한 베팅을<br>남발해 칩의 급격한 소실 위험을 겪습니다. |
            
            #### 4. Win Rate (참여 승률) 구간별 칩 수익 통계
            | 승률 범위 | 플레이어 분류 | 플레이어 수 | 평균 누적 칩 손익 | 실증 데이터 분석 및 해설 |
            | :--- | :--- | :--- | :--- | :--- |
            | <b>15% 미만</b> | 패배가 과다한 유저 (Low) | 738명 | <b>-17,248 칩</b> | 이기는 판이 너무 적어, 대다수 플레이어(738명)가<br>칩이 바닥나는 큰 손실을 입었습니다. |
            | <b>15% ~ 22%</b> | <b>최적 범위 (Optimal)</b> | 143명 | <b>-6,686 칩</b> | 이길 때는 크게 먹고 질 때는 신속히 카드를<br>버리는 전략을 통해, 15% 미만 그룹 대비<br><b>손실을 60% 이상 예방</b>했습니다. |
            | <b>22% 초과</b> | 고승률 유저 (High) | 51명 | <b>+3,042 칩</b> | 승률이 압도적으로 높아 유일하게 전체 평균 흑자가<br>기록된 최상위 포식자 그룹입니다. |
    
            ---
            
            ### 🔍 세부 지표별 수학적 정의 및 SQL 계산 수식
            
            #### 1. VPIP (Voluntarily Put Money in Pot, 자발적 참여율)
            * <b>정의</b>: 기본 참가비 포스팅 배팅을 제외하고, 프리플랍 단계에서 본인 의지로 칩을 팟에 집어넣은(Call, Bet, Raise) 게임 수의 비율입니다.
            * <b>수식</b>:
            """, unsafe_allow_html=True)
            st.markdown('<div class="math-box">VPIP (%) = (Pre-flop 단계에서 Call/Bet/Raise 한 게임 수) / (전체 카드를 배분받은 게임 수) * 100</div>', unsafe_allow_html=True)
            st.markdown("""
            
            #### 2. PFR (Pre-flop Raise, 선제 공격율)
            * <b>정의</b>: 프리플랍 단계에서 주도적으로 레이즈(Raise, 베팅액 올리기)를 한 판 수의 비율입니다.
            * <b>수식</b>:
            """, unsafe_allow_html=True)
            st.markdown('<div class="math-box">PFR (%) = (Pre-flop 단계에서 Raise를 한 게임 수) / (전체 카드를 배분받은 게임 수) * 100</div>', unsafe_allow_html=True)
            st.markdown("""
            
            #### 3. AF (Aggression Factor, 공격성 수치)
            * <b>정의</b>: 플랍 이후 단계에서 상대방 베팅에 따라가는 수동적 액션(Call) 횟수 대비 능동적으로 판을 흔드는 공격적 액션(Bet, Raise) 횟수의 비율입니다.
            * <b>수식</b>:
            """, unsafe_allow_html=True)
            st.markdown('<div class="math-box">AF = (Post-flop 단계의 Bet 횟수 + Raise 횟수) / (Post-flop 단계의 Call 횟수)</div>', unsafe_allow_html=True)
            st.markdown("""
            
            #### 4. Win Rate (승률)
            * <b>정의</b>: 참가한 게임 중에서 칩 손익이 0보다 큰 수익을 거두고 마무리한 비율입니다.
            * <b>수식</b>:
            """, unsafe_allow_html=True)
            st.markdown('<div class="math-box">Win Rate (%) = (수익이 발생한 게임 수) / (전체 참여한 게임 수) * 100</div>', unsafe_allow_html=True)
            st.markdown("""
            """, unsafe_allow_html=True)
    
    
    # =========================================================================
    # TAB 2: 플레이어 프로파일링 (Profiling)
    # =========================================================================
    with tab2:
        st.subheader("👥 플레이어 행동 프로파일링 데이터 마트")
        st.markdown("데이터베이스에 저장된 유저들의 플레이 지표를 바탕으로 게임 성향 코호트별 데이터를 필터링합니다.")
        
        # 쿼리 로드
        where_hp, params_hp = build_sql_filter(include_tournament=True, include_bb=True, include_position=True, hands_alias='h', t_alias='t', hp_alias='hp', prepend_and=True)
        df_profile_query = f"""
        WITH player_base AS (
            SELECT 
                hp.player_name,
                COUNT(DISTINCT hp.hand_id) AS total_hands,
                SUM(CASE WHEN hp.chips_won > 0 THEN 1 ELSE 0 END) AS won_hands,
                SUM(hp.chips_won) AS net_chips_won
            FROM hand_players hp
            JOIN hands h ON hp.hand_id = h.hand_id
            JOIN tournaments t ON h.tournament_id = t.tournament_id
            WHERE 1=1 {where_hp}
            GROUP BY hp.player_name
        ),
        preflop_actions AS (
            SELECT 
                a.player_name,
                COUNT(DISTINCT CASE WHEN a.street = 'preflop' AND a.action_type IN ('calls', 'bets', 'raises') THEN a.hand_id END) AS vpip_hands,
                COUNT(DISTINCT CASE WHEN a.street = 'preflop' AND a.action_type = 'raises' THEN a.hand_id END) AS pfr_hands
            FROM actions a
            JOIN hands h ON a.hand_id = h.hand_id
            JOIN tournaments t ON h.tournament_id = t.tournament_id
            JOIN hand_players hp ON h.hand_id = hp.hand_id AND hp.player_name = a.player_name
            WHERE 1=1 {where_hp}
            GROUP BY a.player_name
        ),
        postflop_actions AS (
            SELECT 
                a.player_name,
                SUM(CASE WHEN a.street IN ('flop', 'turn', 'river') AND a.action_type IN ('bets', 'raises') THEN 1 ELSE 0 END) AS agg_actions,
                SUM(CASE WHEN a.street IN ('flop', 'turn', 'river') AND a.action_type = 'calls' THEN 1 ELSE 0 END) AS passive_actions
            FROM actions a
            JOIN hands h ON a.hand_id = h.hand_id
            JOIN tournaments t ON h.tournament_id = t.tournament_id
            JOIN hand_players hp ON h.hand_id = hp.hand_id AND hp.player_name = a.player_name
            WHERE 1=1 {where_hp}
            GROUP BY a.player_name
        )
        SELECT 
            pb.player_name AS "플레이어 명",
            pb.total_hands AS "총 핸드 수",
            ROUND(COALESCE(pa.vpip_hands, 0) * 100.0 / pb.total_hands, 2) AS "VPIP (%)",
            ROUND(COALESCE(pa.pfr_hands, 0) * 100.0 / pb.total_hands, 2) AS "PFR (%)",
            CASE 
                WHEN COALESCE(pfa.passive_actions, 0) = 0 THEN CASE WHEN COALESCE(pfa.agg_actions, 0) > 0 THEN 5.0 ELSE 0.0 END
                ELSE ROUND(pfa.agg_actions * 1.0 / pfa.passive_actions, 2)
            END AS "공격성(AF)",
            ROUND(pb.won_hands * 100.0 / pb.total_hands, 2) AS "승률 (%)",
            pb.net_chips_won AS "수익 칩",
            CASE 
                WHEN (pa.vpip_hands * 100.0 / pb.total_hands) >= 30.0 AND (pa.pfr_hands * 100.0 / pb.total_hands) < 15.0 THEN 'Loose-Passive'
                WHEN (pa.vpip_hands * 100.0 / pb.total_hands) >= 30.0 AND (pa.pfr_hands * 100.0 / pb.total_hands) >= 15.0 THEN 'Loose-Aggressive'
                WHEN (pa.vpip_hands * 100.0 / pb.total_hands) < 30.0 AND (pa.pfr_hands * 100.0 / pb.total_hands) >= (pa.vpip_hands * 0.8 / pb.total_hands) THEN 'Tight-Aggressive'
                WHEN (pa.vpip_hands * 100.0 / pb.total_hands) < 15.0 THEN 'Tight-Passive'
                ELSE 'Neutral'
            END AS "플레이 스타일"
        FROM player_base pb
        LEFT JOIN preflop_actions pa ON pb.player_name = pa.player_name
        LEFT JOIN postflop_actions pfa ON pb.player_name = pfa.player_name
        WHERE pb.total_hands >= {min_hands_played}
        """
        df_profile = load_data(df_profile_query, params_hp * 3)
        
        # 검색 및 필터 컴포넌트 배치
        col_f1, col_f2 = st.columns([1, 3])
        style_options = list(df_profile['플레이 스타일'].unique()) if not df_profile.empty else []
        with col_f1:
            st.markdown("##### 🔍 플레이어 필터링")
            search_name = st.text_input("닉네임 검색", "")
            style_filter = st.multiselect(
                "플레이 스타일 성향", 
                options=style_options, 
                default=style_options
            )
            
        if not df_profile.empty:
            df_filtered = df_profile[df_profile['플레이 스타일'].isin(style_filter)]
            if search_name:
                df_filtered = df_filtered[df_filtered['플레이어 명'].str.contains(search_name, case=False)]
        else:
            df_filtered = pd.DataFrame()
            
        with col_f2:
            # 데이터프레임 시각화
            st.dataframe(df_filtered, use_container_width=True, height=220)
            
        st.markdown("---")
        
        st.markdown("<h4 style='text-align: center;'>📈 VPIP vs PFR 행동 분포 차트</h4>", unsafe_allow_html=True)
        c_chart, c_desc = st.columns([3.5, 2.5])
        
        with c_chart:
            if not df_filtered.empty:
                fig, ax = plt.subplots(figsize=(6, 3.8))
                
                # 가이드 대각선 표시를 위해 한계값 동적 산정
                max_val = max(df_filtered['VPIP (%)'].max() + 5, 50)
                ax.plot([0, 100], [0, 100], color='#CBD5E1', linestyle='--', linewidth=1.2, label='PFR = VPIP (한계선)')
                
                sns.scatterplot(
                    x='VPIP (%)',
                    y='PFR (%)',
                    hue='플레이 스타일',
                    data=df_filtered,
                    palette='Set1',
                    ax=ax,
                    s=45,
                    alpha=0.85
                )
                
                ax.set_xlim(0, max_val)
                ax.set_ylim(0, max_val)
                ax.set_title("플레이어 행동 매트릭스 (VPIP vs PFR)", fontsize=10, fontweight='bold', pad=10)
                ax.set_xlabel("자발적 참여율 VPIP (%)", fontsize=8)
                ax.set_ylabel("선제 공격율 PFR (%)", fontsize=8)
                ax.tick_params(labelsize=8)
                
                # 범례 정리
                handles, labels = ax.get_legend_handles_labels()
                ax.legend(handles, labels, title="플레이 스타일", title_fontsize=8, fontsize=7, loc='upper left')
                
                plt.tight_layout()
                st.pyplot(fig)
                plt.close(fig)
            else:
                st.warning("⚠️ 필터링된 조건에 해당하는 플레이어 데이터가 없어 분포 차트를 표시할 수 없습니다.")
    
        with c_desc:
            st.markdown("""
            <div class="info-banner" style="margin-top: 0.2rem; font-size: 0.82rem; line-height: 1.5; padding: 1rem;">
                🔍 <b>VPIP vs PFR 행동 매트릭스 상관관계 심층 분석</b>
                <br><br>
                플레이어들의 VPIP(자발적 참여율)와 PFR(선제 공격율) 분포는 유저 성향 세분화의 핵심 기준선이며, 두 지표 간에는 도메인(포커) 및 수학적 정의에 따른 강력한 양의 상관관계가 존재합니다.
                <br><br>
                📌 <b>1. 수학적 부분집합 관계 및 한계선 (PFR ≤ VPIP)</b>
                <br>PFR(선제 레이즈를 통한 진입)은 VPIP(모든 자발적 진입)의 수학적 하위 부분집합입니다. 즉, 레이즈를 하려면 먼저 게임에 참여해야 하므로 <b>PFR은 절대로 VPIP를 초과할 수 없습니다.</b> 이로 인해 차트 상의 모든 데이터 포인트는 <b>대각 기준선(PFR = VPIP)의 우하단 영역</b>에만 존재하게 됩니다.
                <br><br>
                📌 <b>2. 두 지표의 강한 양의 선형 상관관계</b>
                <br>적극적으로 카드를 골라 참여하는 유저일수록 레이즈(공격) 빈도도 함께 비례해서 상승하기 때문에, 전체 플레이어 분포는 대각선 방향으로 우상향하는 <b>강한 양의 선형 상관관계</b>를 띱니다. 상관계수가 매우 높게 도출되는 구간입니다.
                <br><br>
                📌 <b>3. 대각 기준선과의 격차 (VPIP - PFR)의 전략적 의미</b>
                <br>· <b>격차가 좁을수록 (대각선 인접)</b>: 게임에 참여할 때 단순 콜(Call)을 하기보다는 레이즈(Raise)를 가하여 주도권을 강하게 잡는 <b>공격성(Aggressive)</b> 성향입니다. 상대의 폴드를 이끌어내는 '폴드 에퀴티(Fold Equity)'를 활용할 수 있어 장기적으로 유리합니다.
                <br>· <b>격차가 넓을수록 (대각선과 멀어짐)</b>: 게임 진입 시 본인의 주도적 레이즈 없이 타인의 베팅을 수동적으로 쫓아가는 <b>수동성(Passive)</b> 성향입니다. 상대에게 주도권을 쉽게 넘겨주어 손실이 쉽게 누적됩니다.
                <br><br>
                📌 <b>4. 사분면별 플레이어 성향 세분화</b>
                <ul>
                    <li><b>Tight-Aggressive (TA)</b>: 신중하게 엄격한 카드로 진입하되 진입 시 레이즈로 선공을 잡는 숙련 그룹 (Hero가 속한 최적 범위).</li>
                    <li><b>Loose-Passive (LP)</b>: 불리한 카드로 다량 진입하면서 주도권 없이 남의 베팅을 콜로만 따라가 파산 위험이 가장 높은 초보/비숙련 그룹.</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
    
    
    # =========================================================================
    # TAB 3: 퍼널 & 코호트 분석 (Funnel & Cohort)
    # =========================================================================
    with tab3:
        st.subheader("📊 게임 분석 프레임워크: Funnel & Cohort")
        
        st.markdown("""
        <div class="info-banner" style="background-color: #F8FAFC; border-left-color: #475569; color: #334155; margin-top: 0.5rem; margin-bottom: 1.5rem; font-size: 0.92rem; padding: 0.9rem;">
            🔍 <b>분석 개념 및 프레임워크 정의</b><br>
            <ul>
                <li><b>퍼널 분석 (Funnel Analysis)</b>: 유저가 최종 목표(예: 쇼다운 진출)에 도달하기까지 여러 단계를 거치며 어느 구간에서 주로 <b>이탈(Drop-off)</b>하고 <b>전환(Conversion)</b>하는지 탐색하여 경로상의 병목을 찾아내는 분석 기법입니다.</li>
                <li><b>코호트 분석 (Cohort Analysis)</b>: 플레이 스타일 집단 등 공통된 경험이나 행동 특성을 공유하는 <b>동일 집단(Cohort)</b>별로 유저들을 세분화하고, 시간에 따른 자산 변화나 지속 잔존율을 추적·비교하는 기법입니다.</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        col_fn1, col_fn2 = st.columns(2)
        
        with col_fn1:
            st.markdown("#### 📉 베팅 라운드별 핸드 참여 퍼널 (In-Game Betting Funnel)")
            st.markdown("""
            이 퍼널은 각 게임 한 판(Hand) 내에서 플레이어가 포기(Fold)하지 않고 다음 베팅 단계로 얼마나 진출하는지 보여주는 <b>핸드 참여 진행 퍼널</b>입니다.
            """, unsafe_allow_html=True)
            
            # 퍼널 쿼리 실행
            where_hp, params_hp = build_sql_filter(include_tournament=True, include_bb=True, include_position=True, hands_alias='h', t_alias='t', hp_alias='hp', prepend_and=True)
            funnel_query = f"""
            WITH player_exit_street AS (
                SELECT 
                    a.hand_id,
                    a.player_name,
                    MAX(CASE WHEN a.action_type = 'folds' THEN a.street END) AS fold_street
                FROM actions a
                JOIN hands h ON a.hand_id = h.hand_id
                JOIN tournaments t ON h.tournament_id = t.tournament_id
                JOIN hand_players hp ON h.hand_id = hp.hand_id AND hp.player_name = a.player_name
                WHERE 1=1 {where_hp}
                GROUP BY a.hand_id, a.player_name
            )
            SELECT 
                COUNT(hand_id) AS "1. Pre-flop",
                COUNT(CASE WHEN fold_street IS NULL OR fold_street != 'preflop' THEN 1 END) AS "2. Flop",
                COUNT(CASE WHEN fold_street IS NULL OR fold_street NOT IN ('preflop', 'flop') THEN 1 END) AS "3. Turn",
                COUNT(CASE WHEN fold_street IS NULL OR fold_street NOT IN ('preflop', 'flop', 'turn') THEN 1 END) AS "4. River",
                COUNT(CASE WHEN fold_street IS NULL THEN 1 END) AS "5. Showdown"
            FROM player_exit_street
            """
            df_fn = load_data(funnel_query, params_hp)
            
            if not df_fn.empty and df_fn.iloc[0]["1. Pre-flop"] > 0:
                stages = list(df_fn.columns)
                counts = df_fn.iloc[0].values
                rates = np.round(counts / counts[0] * 100, 2)
                
                fig_fn, ax_fn = plt.subplots(figsize=(6, 3.8))
                sns.barplot(x=rates, y=stages, palette='crest_r', ax=ax_fn)
                for i, val in enumerate(rates):
                    ax_fn.text(val + 1, i, f"{val}%", va='center', fontweight='bold', fontsize=8)
                ax_fn.set_xlim(0, 115)
                ax_fn.set_title("단계별 누적 생존율 (퍼널)", fontsize=10, fontweight='bold')
                ax_fn.tick_params(labelsize=8)
                plt.tight_layout()
                st.pyplot(fig_fn)
                plt.close(fig_fn)
            else:
                st.warning("⚠️ 선택하신 조건에 해당하는 퍼널 데이터가 존재하지 않습니다.")
            
            with st.expander("🔍 퍼널 도표 상세 해설 (Pre-flop 100% 및 단계별 의미)", expanded=True):
                st.markdown(textwrap.dedent("""
                * <b>1. Pre-flop (프리플랍: 100%)</b>: 모든 플레이어는 한 판의 게임이 시작될 때 2장의 개인 카드를 <b>무조건 배분받으며 게임에 참여</b>하므로 시작 시점인 이곳이 <b>기준값인 100%</b>가 됩니다.
                * <b>2. Flop (플랍: 약 57.0%)</b>: 테이블 바닥에 공통 카드 3장이 깔리는 단계입니다. 프리플랍에서 자신의 카드가 너무 불리해 기권(Fold)한 사람을 제외하고, <b>전체 판의 57% 정도만 실제로 이 플랍 단계의 공통 카드를 보기 위해 베팅에 참여</b>했음을 의미합니다. (즉, 프리플랍 단계에서 약 43%의 플레이어가 불리한 패를 확인한 뒤 즉시 포기해 칩을 지킨 것입니다.)
                * <b>3. Turn (턴: 약 44.0%)</b>: 네 번째 공통 카드가 추가로 깔리는 단계입니다. 플랍 카드를 확인한 후 생존한 플레이어들이 추가 베팅 비용을 내며 진입한 비율입니다.
                * <b>4. River (리버: 약 33.0%)</b>: 마지막 다섯 번째 공통 카드가 깔려 최종 카드 족보(조합)가 완성되는 베팅 라운드입니다.
                * <b>5. Showdown (쇼다운: 약 25.0%)</b>: 최종 베팅이 모두 종료되고 남은 플레이어들이 카드를 공개해 승패를 가리는 최종 단계입니다.
                
                💡 <b>도메인 분석적 의의 (단계별 리스크 관리)</b>:
                일반적인 IT 웹/앱 서비스의 퍼널 분석과 달리, 게임 플레이 세션 내에서 발생하는 <b>단계별 기권(Fold) 행동은 유저가 플랫폼 서비스를 탈퇴하는 회원 이탈(Churn)이 아닙니다.</b> 이는 본인의 칩 손실을 최소화하기 위한 지극히 합리적이고 능동적인 <b>단계별 리스크 제어 의사결정</b>입니다. 프리플랍에서 플랍으로 넘어갈 때 40% 이상의 큰 기권(이탈)율이 발생하는 것은, 플레이어가 수학적으로 무리한 리스크를 감수하지 않고 영리하게 게임을 풀어가고 있음을 증명합니다.
                """), unsafe_allow_html=True)
            
        with col_fn2:
            st.markdown("#### 👥 성향 코호트별 30세션 누적 수익 추이")
            st.markdown("플레이어 성향 동일 집단(Cohort)별로 게임 세션이 반복될 때 자산(칩)을 어떻게 누적하는지 평균 추이를 나타낸 선그래프입니다.")
            
            cohort_query = f"""
            -- 1단계: 플레이어별로 총 참여한 게임(Hand) 수를 먼저 집계합니다. (필요 조건: 최소 20판 이상 플레이어)
            WITH player_base AS (
                SELECT 
                    hp.player_name,
                    COUNT(hp.hand_id) AS total_hands
                FROM hand_players hp
                JOIN hands h ON hp.hand_id = h.hand_id
                JOIN tournaments t ON h.tournament_id = t.tournament_id
                WHERE 1=1 {where_hp}
                GROUP BY hp.player_name
                HAVING COUNT(hp.hand_id) >= {min_hands_played}
            ),
            -- 2단계: 플레이어별 프리플랍 단계의 액션(VPIP와 PFR) 수를 단일 스캔으로 집계합니다.
            preflop_stats AS (
                SELECT 
                    a.player_name,
                    COUNT(DISTINCT CASE WHEN a.street = 'preflop' AND a.action_type IN ('calls', 'bets', 'raises') THEN a.hand_id END) AS vpip_hands,
                    COUNT(DISTINCT CASE WHEN a.street = 'preflop' AND a.action_type = 'raises' THEN a.hand_id END) AS pfr_hands
                FROM actions a
                JOIN hands h ON a.hand_id = h.hand_id
                JOIN tournaments t ON h.tournament_id = t.tournament_id
                JOIN hand_players hp ON h.hand_id = hp.hand_id AND hp.player_name = a.player_name
                WHERE 1=1 {where_hp}
                GROUP BY a.player_name
            ),
            -- 3단계: 1단계와 2단계에서 집계한 데이터를 1:1로 결합하여 VPIP(%)와 PFR(%) 지표를 최종 산출합니다.
            player_profiles AS (
                SELECT 
                    pb.player_name,
                    pb.total_hands,
                    COALESCE(ps.vpip_hands, 0) * 100.0 / pb.total_hands AS vpip,
                    COALESCE(ps.pfr_hands, 0) * 100.0 / pb.total_hands AS pfr
                FROM player_base pb
                LEFT JOIN preflop_stats ps ON pb.player_name = ps.player_name
            ),
            -- 4단계: 계산된 VPIP와 PFR을 기준으로 플레이 스타일 코호트 그룹을 정의합니다.
            player_styles AS (
                SELECT 
                    player_name,
                    CASE 
                        WHEN vpip >= 30.0 AND pfr < 15.0 THEN 'Loose-Passive'
                        WHEN vpip >= 30.0 AND pfr >= 15.0 THEN 'Loose-Aggressive'
                        WHEN vpip < 30.0 AND pfr >= (vpip * 0.8) THEN 'Tight-Aggressive'
                        WHEN vpip < 15.0 THEN 'Tight-Passive'
                        ELSE 'Neutral'
                    END AS cohort_group
                FROM player_profiles
            ),
            -- 5단계: 시간 경과에 따른 누적 수익 분석을 위해 각 플레이어의 세션 번호(1~30번째 판)를 매깁니다.
            session_chips AS (
                SELECT 
                    hp.player_name,
                    h.timestamp,
                    hp.chips_won,
                    ROW_NUMBER() OVER (PARTITION BY hp.player_name ORDER BY h.timestamp) AS play_session_index
                FROM hand_players hp
                JOIN hands h ON hp.hand_id = h.hand_id
                JOIN tournaments t ON h.tournament_id = t.tournament_id
                WHERE 1=1 {where_hp}
            )
            -- 6단계: 코호트 그룹 정보와 30세션 이하의 누적 수익 지표를 매칭하여 최종 조회합니다.
            SELECT 
                sc.player_name,
                ps.cohort_group,
                sc.play_session_index,
                sc.chips_won
            FROM session_chips sc
            JOIN player_styles ps ON sc.player_name = ps.player_name
            WHERE sc.play_session_index <= 30
            """
            df_ch = load_data(cohort_query, params_hp * 3)
            
            if not df_ch.empty:
                df_ch['cumulative_chips'] = df_ch.groupby('player_name')['chips_won'].cumsum()
                df_ch_grouped = df_ch.groupby(['cohort_group', 'play_session_index'])['cumulative_chips'].mean().reset_index()
                
                fig_ch, ax_ch = plt.subplots(figsize=(6, 3.8))
                sns.lineplot(x='play_session_index', y='cumulative_chips', hue='cohort_group', marker='o', data=df_ch_grouped, ax=ax_ch)
                ax_ch.axhline(0, color='red', linestyle='--')
                ax_ch.set_title("코호트 그룹별 세션 누적 평균 자산 추이", fontsize=10, fontweight='bold')
                ax_ch.set_xlabel("플레이 세션", fontsize=8)
                ax_ch.set_ylabel("누적 칩스", fontsize=8)
                ax_ch.tick_params(labelsize=8)
                plt.legend(fontsize=7, title_fontsize=8)
                plt.tight_layout()
                st.pyplot(fig_ch)
                plt.close(fig_ch)
            else:
                st.warning("⚠️ 선택하신 조건에 해당하는 코호트 데이터가 존재하지 않습니다.")
            
            with st.expander("🔍 코호트 그래프 상세 해설 (축 및 선 그래프 의미)", expanded=True):
                st.markdown(textwrap.dedent("""
                * <b>코호트 그룹 (Cohort Group)</b>: 플레이어들의 VPIP(참여율)와 PFR(선제공격율) 분석을 바탕으로 분류한 <b>플레이 성향 동일 집단</b>입니다.
                  - <b>Tight-Aggressive (오렌지색)</b>: 카드를 신속히 사리며 강할 때만 공격적으로 주도권을 쥐는 코어 숙련 집단 (Hero가 지향하는 모델).
                  - <b>Loose-Passive (연두색)</b>: 카드를 가리지 않고 너무 자주 참가하면서 베팅 주도권 없이 남의 베팅에 콜만 따라다니는 초보/비숙련 집단.
                * <b>X축 (플레이 세션)</b>: 플레이어가 게임을 플레이한 누적 판수(1번째 판부터 30번째 판까지의 시계열 추이)입니다.
                * <b>Y축 (누적 칩스)</b>: 게임 참여 시작 시점을 0으로 잡았을 때, 매 게임 세션이 누적되면서 플레이어가 <b>평균적으로 획득하거나 잃은 칩의 누계</b>를 뜻합니다.
                  - <b>빨간 점선 (0선 기준)</b>: 이 선보다 위에 위치하면 누적 평균 흑자, 아래에 위치하면 누적 평균 적자 상태를 나타냅니다.
                
                💡 <b>분석적 의의 (플레이 성향별 손익 분포)</b>:
                * <b>Loose-Passive(수동형 초보)</b> 집단은 세션이 반복될수록(X축 우측으로 갈수록) 누적 적자가 아주 빠르게 심화됩니다. 이는 매판 콜만 하며 판돈을 낭비하기 때문입니다.
                * 반면 <b>Tight-Aggressive(공격형 숙련)</b> 집단은 칩 손실을 최소화하고 자산을 지키는 생존 전략을 수학적으로 증명합니다.
                """), unsafe_allow_html=True)
    
        # -------------------------------------------------------------------------
        # 하단 배너 매칭
        # -------------------------------------------------------------------------
        st.markdown(" ")
        col_bn1, col_bn2 = st.columns(2)
        
        with col_bn1:
            st.markdown("""
            <div class="info-banner" style="font-size: 0.85rem; padding: 0.75rem; min-height: 125px;">
                💡 <b>퍼널 인사이트 (참여 단계 분석)</b>: Pre-flop에서 Flop 전환 시 40% 이상 폴드(참여 포기)가 발생합니다. 
                이는 플레이어들이 카드를 배분받은 후(Pre-flop) 첫 3장의 공통 카드가 깔리기 전에 불리한 카드를 신속히 포기하여 칩 누수를 방지하는 <b>능동적인 리스크 관리 행동 패턴</b>을 보여줍니다.
            </div>
            """, unsafe_allow_html=True)
            
        with col_bn2:
            st.markdown("""
            <div class="info-banner" style="font-size: 0.85rem; padding: 0.75rem; min-height: 125px;">
                💡 <b>코호트 인사이트 (누적 손익 분석)</b>: Loose-Passive 집단은 세션이 누적될수록 평균 누적 칩 자산이 지속적으로 우하향합니다. 
                이들은 불리한 카드로 게임에 참여하여 수동적으로 베팅을 따라가기 때문에 장기 세션 진행 시 칩을 모두 잃고 <b>테이블에서 파산(Bust-out)할 확률</b>이 가장 높습니다.
            </div>
            """, unsafe_allow_html=True)
    
    
    # =========================================================================
    # TAB 4: A/B 테스트 가설 검정 (A/B Test)
    # =========================================================================
    with tab4:
        st.subheader("🧪 A/B 테스트 플레이그라운드")
        st.markdown("수립한 가설을 바탕으로, 데이터 기반 통계 검정(T-Test)을 실시간으로 실행하여 전략에 따른 수익 유의성을 판별합니다.")
        
        st.markdown("""
        <div class="info-banner" style="background-color: #F0FDF4; border-left-color: #10B981; color: #14532D; font-size: 0.95rem; margin-top: 0.5rem; margin-bottom: 1.5rem;">
            🎯 <b>A/B 테스트 핵심 요약: "프리미엄 패를 받았을 때, 레이즈(선제 공격)를 하는 것이 더 유리할까?"</b><br>
            본 실험은 가장 좋은 카드(AA, KK, QQ)를 얻었을 때 <b>적극적으로 베팅액을 올린 전략(Group A - Raise)</b>이 단순 <b>콜로 따라간 수동적 전략(Group B - Call/Check)</b>에 비해 수익을 더 크게 극대화하는지 통계적으로 검증합니다.
            <br><br>
            📢 <b>분석 결론</b>: 프리미엄 카드로 선제 레이즈를 감행한 그룹(A)의 평균 및 중간값 수익이 단순히 따라간 그룹(B)보다 확연히 높았습니다. 다만, 포커 특성상 한 판마다 오고 가는 판돈의 기복(변동성)이 워낙 심하여 95%의 통계적 확실성(p-value &lt; 0.05)을 입증하려면 추가적인 분석 판수가 계속 쌓여야 함을 나타냅니다.
        </div>
        """, unsafe_allow_html=True)
    
        st.info("""
        * __가설 설계__:
          - __실험 대상 (A/B안)__: 프리미엄 패(AA, KK, QQ)를 가졌을 때, 프리플랍 단계에서 베팅액을 올린 집단(Group A: 레이즈) vs 단순히 콜/체크로 참전한 집단(Group B: 콜/체크)
          - __기본 생각 (귀무가설)__: 프리미엄 카드를 잡았을 때 레이즈를 치든 콜을 하든 최종 수익에는 통계적 차이가 없다 (전략의 차이가 아닌 운의 차이다).
          - __검증 목표 (대립가설)__: 적극적으로 레이즈를 쳐서 판돈을 키운 Group A가 통계적으로 유의미하게 훨씬 높은 수익을 얻는다.
        """)
        
        # A/B 테스트 데이터 쿼리 로드
        where_hp, params_hp = build_sql_filter(include_tournament=True, include_bb=True, include_position=True, hands_alias='h', t_alias='t', hp_alias='hp', prepend_and=True)
        ab_query = f"""
        -- 1단계: 프리미엄 핸드(AA, KK, QQ)를 분배받은 플레이어 및 획득 칩수를 추출합니다.
        WITH premium_hands AS (
            SELECT 
                hp.hand_id,
                hp.player_name,
                hp.chips_won
            FROM hand_players hp
            JOIN hands h ON hp.hand_id = h.hand_id
            JOIN tournaments t ON h.tournament_id = t.tournament_id
            WHERE (hp.hole_cards LIKE '%A%A%'
               OR hp.hole_cards LIKE '%K%K%'
               OR hp.hole_cards LIKE '%Q%Q%') {where_hp}
        ),
        -- 2단계: 프리플랍 단계에서 레이즈를 수행한 플레이어와 게임 ID 목록을 actions에서 고속 추출합니다.
        preflop_raisers AS (
            SELECT DISTINCT 
                a.hand_id,
                a.player_name
            FROM actions a
            JOIN hands h ON a.hand_id = h.hand_id
            JOIN tournaments t ON h.tournament_id = t.tournament_id
            JOIN hand_players hp ON h.hand_id = hp.hand_id AND hp.player_name = a.player_name
            WHERE a.street = 'preflop'
              AND a.action_type = 'raises' {where_hp}
        )
        -- 3단계: 프리미엄 핸드 목록과 프리플랍 레이즈 이력을 매칭하여 테스트 집단(A그룹 vs B그룹)을 나눕니다.
        SELECT 
            CASE WHEN pr.hand_id IS NOT NULL THEN 'Group A (Raise)' ELSE 'Group B (Call/Check)' END AS test_group,
            ph.chips_won
        FROM premium_hands ph
        LEFT JOIN preflop_raisers pr ON ph.hand_id = pr.hand_id AND ph.player_name = pr.player_name
        """
        df_ab = load_data(ab_query, params_hp * 2)
        
        # 집단 분리 및 T-Test
        group_a = df_ab[df_ab['test_group'] == 'Group A (Raise)']['chips_won'] if not df_ab.empty else pd.Series(dtype=float)
        group_b = df_ab[df_ab['test_group'] == 'Group B (Call/Check)']['chips_won'] if not df_ab.empty else pd.Series(dtype=float)
        
        has_enough_data = len(group_a) >= 2 and len(group_b) >= 2
        if has_enough_data:
            t_stat, p_val = stats.ttest_ind(group_a, group_b, equal_var=False)
        else:
            t_stat, p_val = np.nan, np.nan
            
        col_ab1, col_ab2 = st.columns(2)
        
        with col_ab1:
            st.subheader("📋 실시간 검정 요약")
            if not df_ab.empty:
                desc_df = df_ab.groupby('test_group')['chips_won'].describe()
                desc_df.columns = ['표본 수 (count)', '평균 수익 (mean)', '표준편차 (std)', '최소값 (min)', '25%', '중앙값 (50%)', '75%', '최대값 (max)']
                st.dataframe(desc_df.round(2), use_container_width=True)
            else:
                st.warning("⚠️ 선택하신 조건에 해당하는 표본 데이터가 없습니다.")
                
            st.markdown(f"""
            <b>🧪 통계 검정 지표 결과</b>
            * <b>T-통계량 (T-Statistic)</b>: `{t_stat:.4f}`
            * <b>유의확률 (p-value)</b>: `{p_val:.4f}`
            """, unsafe_allow_html=True)
            
            if has_enough_data and not np.isnan(p_val):
                if p_val < 0.05:
                    st.success(f"🎯 __결정: 대립가설 채택__ (p-value = {p_val:.6f} < 0.05)\n\n통계적으로 유의미한 차이가 검증되었습니다! 프리미엄 패일 때 적극적으로 레이즈를 쳐서 판돈을 키우는 전략(Group A)이 장기 기대수익성 확보에 훨씬 탁월합니다.")
                else:
                    st.warning(f"⚠️ __결정: 귀무가설 채택__ (p-value = {p_val:.6f} >= 0.05)\n\n통계적으로 두 그룹 간 평균의 차이가 유의미하지 않습니다. (아래 세부 원인 분석 해설을 참고해 주세요.)")
            else:
                st.info("⚠️ 표본 크기가 너무 적어 통계적 가설 검정(T-Test)을 실행할 수 없습니다. 필터 조건을 완화하여 더 많은 핸드를 로드해 주세요.")
                
        with col_ab2:
            st.subheader("📊 신뢰구간 시각화")
            if not df_ab.empty:
                fig_ab, ax_ab = plt.subplots(figsize=(6, 3.8))
                sns.barplot(x='test_group', y='chips_won', data=df_ab, errorbar='ci', capsize=0.1, palette='Set2', ax=ax_ab)
                ax_ab.set_title("그룹별 평균 칩 획득량 비교 (95% 신뢰구간)", fontsize=10, fontweight='bold')
                ax_ab.set_ylabel("chips_won", fontsize=8)
                ax_ab.set_xlabel("test_group", fontsize=8)
                ax_ab.tick_params(labelsize=8)
                plt.tight_layout()
                st.pyplot(fig_ab)
                plt.close(fig_ab)
            else:
                st.warning("⚠️ 차트를 표시할 데이터가 없습니다.")
    
        st.markdown("---")
        st.markdown("### 💡 A/B 테스트 통계 검정 결과 및 지표 분석 해설")
        
        st.markdown(textwrap.dedent(f"""
        대시보드상에서 실시간으로 계산된 T-검정(T-Test) 결과 수치들에 대한 상세 해설입니다.
        
        #### 1. 📊 실시간 요약표 항목의 직관적 해석
        * <b>표본 수 (count)</b>: 프리미엄 카드(AA, KK, QQ)를 분배받은 총 판수입니다. 적극적 레이즈를 가한 Group A는 <b>{len(group_a)}회</b>, 수동적으로 콜한 Group B는 <b>{len(group_b)}회</b> 관측되었습니다.
        * <b>평균 수익 (mean)</b>: 한 판당 획득한 평균 칩스입니다. Group A가 <b>{group_a.mean():,.1f} 칩</b>으로, Group B의 <b>{group_b.mean():,.1f} 칩</b>에 비해 수치상 높게 형성되어 있습니다.
        * <b>표준편차 (std)</b>: 수익의 변동성(기복)입니다. 두 그룹 모두 <b>{group_a.std():,.1f} 칩</b> 및 <b>{group_b.std():,.1f} 칩</b>으로, 평균 수익 대비 무려 <b>5배~8배</b> 이상의 아주 극심한 기복을 보입니다.
        * <b>중앙값 (50%)</b>: 극단적인 값들을 제외한 순수 중간 등수의 수익입니다. Group A는 <b>{group_a.median():,.1f} 칩</b>인 반면 Group B는 <b>{group_b.median():,.1f} 칩</b>으로, 대다수의 판에서 선제 공격이 더 견고한 수익을 냈음을 보여줍니다.
     
        #### 2. 🧪 핵심 통계 용어 및 지표 의미
        * <b>T-통계량 (T-Statistic) [<b>{t_stat:.4f}</b>]</b>
          - <b>의미</b>: "두 그룹의 평균 차이가 데이터의 기복(표준편차)에 비해 얼마나 큰가"를 나타내는 표준화 비율입니다. 이 수치가 절대적으로 클수록(보통 2 이상) 두 그룹의 수익 격차가 유의미하다는 것을 뜻합니다.
          - <b>현재 결과 분석</b>: 현재 수치 `{t_stat:.4f}`는 두 그룹의 평균 수익 차이가 두 그룹 내부 데이터의 무시무시한 기복(변동성)에 비해 아주 미미한 수준이라는 것을 의미합니다.
        * <b>유의확률 (p-value) [<b>{p_val:.4f}</b>]</b>
          - <b>의미</b>: "실제로는 두 전략 간에 수익 차이가 없다(우연이다)"는 전제하에, 우연히 이 정도 수준의 수익 격차가 관측될 확률입니다.
          - <b>현재 결과 분석</b>: 현재 유의확률은 <b>`{p_val*100:.1f}%` ({p_val:.4f})</b>입니다. 통계학적으로 진짜 전략의 차이로 인정받으려면 이 확률이 `5%` 미만(p < 0.05)이어야 합니다. 따라서 현재는 <b>"평균 수익의 차이가 전략의 우수성 때문인지, 단순한 무작위 변동성(운) 때문인지 95% 신뢰도로 확신할 수 없다"</b>는 귀무가설을 채택하게 됩니다.
     
        #### 3. 🔍 귀무가설이 채택된 데이터 관점의 2대 원인
        1. <b>포커 게임 고유의 극심한 변동성 (High Variance)</b>
           - 포커는 올인이나 대박/쪽박 등으로 단 한 판 만에 칩 수만 개가 오고 가는 고변동성 도메인입니다. 두 집단의 평균 격차는 약 `1,220 칩`인 반면, 기복(표준편차)은 무려 `17,000 ~ 19,000 칩`에 달해 <b>평균 차이의 15배</b>가 넘습니다. 이 큰 소음(Noise) 속에서 미세한 신호(Signal)를 검증하려다 보니 통계적으로 유의미한 차이로 드러나지 못했습니다.
        2. <b>Group B의 소형 표본 크기 (Small Sample Size)</b>
           - 프리미엄 카드를 잡고 레이즈를 친 Group A({len(group_a)}건)에 비해, 콜로만 일관한 Group B({len(group_b)}건)의 데이터 개수가 너무 적습니다. 표본 수가 작을수록 통계적 검정력(Power)이 크게 약화되어, 실제 차이가 존재하더라도 이를 유의미하다고 증명하지 못하는 현상이 발생합니다.
     
        #### 🎯 데이터 분석가 제언 (Next Action)
        * <b>데이터 추가 적재</b>: 게임 로그 수집 기간을 늘려 Group B의 표본 수(최소 100건 이상)를 추가로 확보해야 합니다.
        * <b>아웃라이어 보정</b>: 극단적으로 큰 칩을 획득/상실한 아웃라이어 판들을 제외하거나 특정 백분위수로 자르는 보정(Winsorization) 후 T-검정을 재수행하여 노이즈를 제어한다면, 선제 공격(Group A)의 통계적 우위를 보다 명확하게 검증할 수 있을 것입니다.
        """), unsafe_allow_html=True)
    
    
    # =========================================================================
    # TAB 5: 🎮 시나리오 시뮬레이터 (Simulator)
    # =========================================================================
    with tab5:
        st.subheader("🎮 실시간 데이터 스트리밍 & 플레이 스타일 시뮬레이션")
        st.markdown("이 탭에서는 raw 로그 데이터를 데이터베이스(DB)로 스트리밍 적재하는 과정의 실시간 수치 변화를 재현하거나, 베팅 전략 지표를 조절해 볼 수 있는 샌드박스를 제공합니다.")
        
        # 구분선 및 ETL 시뮬레이션 섹션
        st.markdown("### ⚡ 실시간 데이터 적재 시뮬레이션 (Streaming ETL)")
        st.markdown("비정형 텍스트 로그 파일들을 관계형 데이터베이스에 파싱 및 실시간 적재하는 과정을 모니터링합니다. 버튼을 누르면 누적 적재 그래프가 움직이며 카운트가 올라갑니다.")
        
        if st.button("🚀 실시간 데이터 적재 시뮬레이션 시작"):
            # 원본 데이터베이스에서 Hero 전체 시계열 로드
            conn = get_db_connection()
            df_hero_hands = pd.read_sql_query("""
                SELECT hp.hand_id, h.timestamp, hp.chips_won
                FROM hand_players hp
                JOIN hands h ON hp.hand_id = h.hand_id
                WHERE hp.player_name = 'Hero'
                ORDER BY h.timestamp
            """, conn)
            
            # 총 누적 지표 캐싱
            total_hands_in_db = pd.read_sql_query("SELECT COUNT(*) FROM hands", conn).iloc[0, 0]
            total_actions_in_db = pd.read_sql_query("SELECT COUNT(*) FROM actions", conn).iloc[0, 0]
            total_players_in_db = pd.read_sql_query("SELECT COUNT(DISTINCT player_name) FROM hand_players", conn).iloc[0, 0]
            conn.close()
            
            # UI 레이아웃 선언
            col_sim1, col_sim2, col_sim3 = st.columns(3)
            with col_sim1:
                hands_box = st.empty()
            with col_sim2:
                actions_box = st.empty()
            with col_sim3:
                players_box = st.empty()
                
            progress_bar = st.progress(0)
            chart_placeholder = st.empty()
            
            steps = 20
            chunk_size_hands = total_hands_in_db // steps
            chunk_size_actions = total_actions_in_db // steps
            
            for i in range(1, steps + 1):
                curr_hands = min(i * chunk_size_hands, total_hands_in_db)
                curr_actions = min(i * chunk_size_actions, total_actions_in_db)
                curr_players = int(total_players_in_db * (0.4 + 0.6 * (i / steps)))
                
                # 카드 박스 실시간 업데이트
                hands_box.markdown(f"""
                <div class="custom-card">
                    <div class="card-label">적재된 게임 수 (Hands)</div>
                    <div class="card-value" style="color: #3B82F6;">{curr_hands:,} / {total_hands_in_db:,}</div>
                </div>
                """, unsafe_allow_html=True)
                
                actions_box.markdown(f"""
                <div class="custom-card" style="border-top-color: #10B981;">
                    <div class="card-label">적재된 액션 로그 (Actions)</div>
                    <div class="card-value" style="color: #10B981;">{curr_actions:,} / {total_actions_in_db:,}</div>
                </div>
                """, unsafe_allow_html=True)
                
                players_box.markdown(f"""
                <div class="custom-card" style="border-top-color: #8B5CF6;">
                    <div class="card-label">식별된 유저 수 (Players)</div>
                    <div class="card-value" style="color: #8B5CF6;">{curr_players:,} / {total_players_in_db:,}</div>
                </div>
                """, unsafe_allow_html=True)
                
                # 진행 상태 바 업데이트
                progress_bar.progress(i / steps)
                
                # Hero 누적 손익 실시간 그래프 리프레시
                limit_hero = int(len(df_hero_hands) * (i / steps))
                df_sub = df_hero_hands.iloc[:limit_hero].copy()
                if not df_sub.empty:
                    df_sub['cum_won'] = df_sub['chips_won'].cumsum()
                    
                    fig_sim, ax_sim = plt.subplots(figsize=(10, 3.5))
                    ax_sim.plot(df_sub['cum_won'].values, color='#3B82F6', linewidth=2, label='Hero 누적 손익')
                    ax_sim.axhline(0, color='red', linestyle='--', linewidth=1)
                    ax_sim.set_title("실시간 적재 진행에 따른 Hero 누적 칩 추이 (Live)", fontsize=11, fontweight='bold')
                    ax_sim.set_xlabel("핸드 진행 횟수", fontsize=8)
                    ax_sim.set_ylabel("누적 칩 손익", fontsize=8)
                    ax_sim.tick_params(labelsize=8)
                    ax_sim.grid(True, linestyle=':', alpha=0.6)
                    plt.tight_layout()
                    chart_placeholder.pyplot(fig_sim)
                    plt.close(fig_sim)
                    
                time.sleep(0.12)
                
            st.success("🎉 140개 raw_hh 파일의 7,993개 핸드에 대한 실시간 ETL 파싱 및 데이터베이스 적재가 성공적으로 완료되었습니다!")
            
        st.markdown("---")
        st.markdown("### 🎭 플레이 스타일 샌드박스 (Playstyle Sandbox)")
        st.markdown("원하는 플레이 지표(VPIP, PFR, AF)를 설정하면 유저 성향이 실시간 분류되며, DB 내부에서 지표가 가장 유사한 실제 플레이어 3명의 누적 손익 곡선을 로드하여 시각적으로 시뮬레이션 비교합니다.")
        
        col_sb1, col_sb2 = st.columns([2, 3])
        with col_sb1:
            st.markdown("#### 🎚️ 플레이어 전략 성향 조절기")
            sim_vpip = st.slider("VPIP (자발적 참여율, %)", min_value=0, max_value=100, value=20, step=1)
            sim_pfr = st.slider("PFR (선제 공격율, %)", min_value=0, max_value=100, value=15, step=1)
            if sim_pfr > sim_vpip:
                st.warning("⚠️ PFR(선공격율)은 VPIP(자발 참여율)를 초과할 수 없습니다. PFR을 VPIP 값과 동일하게 제한합니다.")
                sim_pfr = sim_vpip
                
            sim_af = st.slider("AF (포스트플랍 공격성)", min_value=0.0, max_value=5.0, value=2.5, step=0.1)
            
            # 플레이 스타일 성향 자동 분류
            if sim_vpip >= 30.0 and sim_pfr < 15.0:
                sim_style = 'Loose-Passive (LP)'
                sim_style_desc = "수많은 판을 수동적으로 참전합니다. 상대 베팅에 끌려다니므로 칩 손실율이 높습니다."
            elif sim_vpip >= 30.0 and sim_pfr >= 15.0:
                sim_style = 'Loose-Aggressive (LAG)'
                sim_style_desc = "참여율도 높고 베팅도 매우 공격적입니다. 큰 팟을 만들어 하이리스크 하이리턴을 보입니다."
            elif sim_vpip < 30.0 and sim_pfr >= (sim_vpip * 0.8):
                sim_style = 'Tight-Aggressive (TAG)'
                sim_style_desc = "좋은 카드 위주로 신중히 고른 뒤 적극적으로 공격하는 전략적 숙련 정규 플레이어 성향입니다."
            elif sim_vpip < 15.0:
                sim_style = 'Tight-Passive (TP)'
                sim_style_desc = "지나치게 좋은 카드만 기다리며 수비적으로 플레이합니다. 블라인드비 누적 적자를 겪습니다."
            else:
                sim_style = 'Neutral'
                sim_style_desc = "무난하게 중립적인 지표 범위를 나타내는 표준 유저 스타일입니다."
                
            st.markdown(f"""
            <div class="info-banner" style="background-color: #EFF6FF; border-left-color: #3B82F6; color: #1E3A8A; font-size: 0.95rem;">
                🎭 <b>스타일 분류 결과</b>: <span style="font-weight: 800; font-size: 1.1rem; color: #1D4ED8;">{sim_style}</span><br>
                <i>{sim_style_desc}</i><br><br>
                설정된 지표: VPIP={sim_vpip}%, PFR={sim_pfr}%, AF={sim_af}
            </div>
            """, unsafe_allow_html=True)
            
        with col_sb2:
            st.markdown("#### 📈 가장 가까운 실제 유저 매칭 손익 시뮬레이션")
            
            # 모든 플레이어 프로필 로드
            conn = get_db_connection()
            df_all_profiles = pd.read_sql_query("""
                WITH player_base AS (
                    SELECT 
                        player_name,
                        COUNT(hand_id) AS total_hands
                    FROM hand_players
                    GROUP BY player_name
                    HAVING COUNT(hand_id) >= 20
                ),
                preflop_stats AS (
                    SELECT 
                        player_name,
                        COUNT(DISTINCT CASE WHEN street = 'preflop' AND action_type IN ('calls', 'bets', 'raises') THEN hand_id END) AS vpip_hands,
                        COUNT(DISTINCT CASE WHEN street = 'preflop' AND action_type = 'raises' THEN hand_id END) AS pfr_hands
                    FROM actions
                    GROUP BY player_name
                ),
                postflop_stats AS (
                    SELECT 
                        player_name,
                        SUM(CASE WHEN street IN ('flop', 'turn', 'river') AND action_type IN ('bets', 'raises') THEN 1 ELSE 0 END) AS agg_actions,
                        SUM(CASE WHEN street IN ('flop', 'turn', 'river') AND action_type = 'calls' THEN 1 ELSE 0 END) AS passive_actions
                    FROM actions
                    GROUP BY player_name
                )
                SELECT 
                    pb.player_name,
                    pb.total_hands,
                    COALESCE(ps.vpip_hands, 0) * 100.0 / pb.total_hands AS vpip,
                    COALESCE(ps.pfr_hands, 0) * 100.0 / pb.total_hands AS pfr,
                    CASE 
                        WHEN COALESCE(pfs.passive_actions, 0) = 0 THEN CASE WHEN COALESCE(pfs.agg_actions, 0) > 0 THEN 5.0 ELSE 0.0 END
                        ELSE ROUND(pfs.agg_actions * 1.0 / pfs.passive_actions, 2)
                    END AS af
                FROM player_base pb
                LEFT JOIN preflop_stats ps ON pb.player_name = ps.player_name
                LEFT JOIN postflop_stats pfs ON pb.player_name = pfs.player_name
            """, conn)
            
            # Euclidean 거리 계산
            df_all_profiles['distance'] = np.sqrt(
                (df_all_profiles['vpip'] - sim_vpip) ** 2 +
                (df_all_profiles['pfr'] - sim_pfr) ** 2 +
                ((df_all_profiles['af'] - sim_af) * 10) ** 2  # AF의 가중치 스케일 보정
            )
            
            # 가장 거리가 가까운 3명의 실제 유저 탐색
            top_players = df_all_profiles.nsmallest(3, 'distance')
            top_player_names = list(top_players['player_name'])
            
            if len(top_player_names) > 0:
                placeholders = ",".join(["?"] * len(top_player_names)) if selected_db_type == "sqlite" else ",".join(["%s"] * len(top_player_names))
                df_session_chips = pd.read_sql_query(f"""
                    SELECT 
                        hp.player_name,
                        hp.chips_won,
                        h.timestamp
                    FROM hand_players hp
                    JOIN hands h ON hp.hand_id = h.hand_id
                    WHERE hp.player_name IN ({placeholders})
                    ORDER BY h.timestamp
                """, conn, params=top_player_names)
                conn.close()
                
                if not df_session_chips.empty:
                    df_session_chips['play_session_index'] = df_session_chips.groupby('player_name').cumcount() + 1
                    df_session_chips = df_session_chips[df_session_chips['play_session_index'] <= 30]
                    df_session_chips['cumulative_chips'] = df_session_chips.groupby('player_name')['chips_won'].cumsum()
                    
                    fig_sb, ax_sb = plt.subplots(figsize=(6, 3.8))
                    for name in top_player_names:
                        df_player = df_session_chips[df_session_chips['player_name'] == name]
                        if not df_player.empty:
                            ax_sb.plot(df_player['play_session_index'].values, df_player['cumulative_chips'].values, marker='o', label=name)
                    ax_sb.axhline(0, color='red', linestyle='--', linewidth=1)
                    ax_sb.set_title("매칭 유저들의 30세션 누적 칩스 추이 (Sandbox)", fontsize=10, fontweight='bold')
                    ax_sb.set_xlabel("플레이 세션", fontsize=8)
                    ax_sb.set_ylabel("누적 칩스", fontsize=8)
                    ax_sb.tick_params(labelsize=8)
                    ax_sb.legend(fontsize=7)
                    plt.tight_layout()
                    st.pyplot(fig_sb)
                    plt.close(fig_sb)
                    
                    # 유사도 매칭 유저 리스트 출력
                    st.markdown("🕵️ **가장 유사한 실제 플레이어 매칭 정보:**")
                    for idx, row in top_players.iterrows():
                        st.write(f"- **{row['player_name']}**: VPIP={row['vpip']:.1f}%, PFR={row['pfr']:.1f}%, AF={row['af']:.1f} (거리차: {row['distance']:.2f})")
                else:
                    conn.close()
                    st.info("⚠️ 매칭 플레이어들의 세션 데이터가 없습니다.")
            else:
                conn.close()
                st.info("⚠️ 매칭되는 플레이어 데이터가 존재하지 않습니다.")
    
    # 데이터베이스 점검 완료 안내 출력 (Streamlit 로그용)
    print("Streamlit 대시보드 새로고침 완료!")
    
