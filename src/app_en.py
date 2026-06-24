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

def main():
    # =========================================================================
    # Streamlit 대시보드 웹 애플리케이션 (app.py) - Dual DB 지원 & Premium 리디자인
    # =========================================================================
    # * 목적: SQLite 또는 PostgreSQL 데이터베이스를 연동하여 유저 행동 데이터를 시각화합니다.
    # * 주요 특징:
    #   - 다차원 Tableau 스타일 글로벌 필터(토너먼트 종류, BB 블라인드 범위, 포지션, 최소 참여 판수)
    #   - 실시간 데이터 적재 ETL 스트리밍 시뮬레이션 및 플레이 스타일 샌드박스 플레이그라운드
    # =========================================================================

    # 1. 페이지 레이아웃 및 테마 설정
    pass  # Page config set in app.py

    pass  # Language routing managed in app.py

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
    st.markdown("""<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Outfit:wght@400;600;700;800&display=swap');

    /* Define global font and background */
    html, body, [class*=\"css\"], .stMarkdown {
        font-family: 'Inter', 'Malgun Gothic', sans-serif !important;
    }

    /* Title font tuning */
    h1, h2, h3, .main-title {
        font-family: 'Outfit', 'Malgun Gothic', sans-serif !important;
        font-weight: 700 !important;
        color: #1E293B !important;
    }

    /* Main gradient header */
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

    /* Sidebar distortion and font line wrapping bug correction */
    [data-testid=\"stSidebar\"] {
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

    /* Premium card design */
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

    /* Tuning banner for explanation */
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

    /* Formula box style */
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
    </style>""", unsafe_allow_html=True)

    # -------------------------------------------------------------------------
    # 사이드바 (Sidebar) - 필터 설정 및 프로젝트 소개 (레이아웃 뒤틀림 보정)
    # -------------------------------------------------------------------------
    st.sidebar.markdown('<div class="sidebar-title">📊 iGaming Analysis Platform</div>', unsafe_allow_html=True)
    st.sidebar.markdown("""This dashboard is a data analysis BI platform built after formalizing <b>unstructured poker hand history</b> into relational data.<br>
    Demonstrates core analysis frameworks (Funnel, Cohort, A/B Test) applicable to <b>mobile service and data platform analysis</b>.""", unsafe_allow_html=True)

    # =========================================================================
    # [PostgreSQL 기능 추가] 사이드바 DB 커넥션 샌드박스 UI
    # =========================================================================
    st.sidebar.markdown("---")
    st.sidebar.subheader("🔌 Database link settings")

    db_option = st.sidebar.selectbox(
        "Select database engine",
        options=["SQLite (default local file)", "PostgreSQL (server connection)"]
    )

    # 커넥션 헬퍼 변수
    selected_db_type = "sqlite"
    conn_error = None
    pg_info = {}

    if db_option == "SQLite (default local file)":
        selected_db_type = "sqlite"
        default_db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "poker_data.db"))
        sqlite_path = st.sidebar.text_input("SQLite file path", value=default_db_path)
        if not os.path.exists(sqlite_path):
            conn_error = f"SQLite file not found. Path: {sqlite_path}"
    else:
        selected_db_type = "postgres"
        if not POSTGRES_AVAILABLE:
            st.sidebar.error("❌ The psycopg2 library is not installed.")
            st.sidebar.info("💡 Run `pip install psycopg2-binary` to install the driver.")
            conn_error = "psycopg2 missing"
        else:
            # PostgreSQL 접속 폼
            pg_info["host"] = st.sidebar.text_input("Host", value="localhost")
            pg_info["port"] = st.sidebar.number_input("Port", value=5432, step=1)
            pg_info["user"] = st.sidebar.text_input("Account name (User)", value="postgres")
            pg_info["password"] = st.sidebar.text_input("Password", value="postgres", type="password")
            pg_info["database"] = st.sidebar.text_input("database name", value="poker_db")

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
            st.sidebar.success(f"✔️ {db_option} Connection successful!")
        except Exception as e:
            st.sidebar.error(f"❌ DB connection failure: {e}")
            st.sidebar.info("💡 You can check data by changing to `SQLite (default local file)` mode.")
            st.stop()
    else:
        st.sidebar.error(f"❌ Setting error: {conn_error}")
        st.stop()

    # -------------------------------------------------------------------------
    # 사이드바 (Sidebar) - 다차원 Tableau 스타일 글로벌 필터
    # -------------------------------------------------------------------------
    st.sidebar.markdown("---")
    st.sidebar.subheader("🎛️ Global filters (Tableau style)")

    all_tournament_styles = ["Turbo", "Hyper", "Monster/Special", "Fifty Stack", "GGMasters", "Bounty/KO", "Other"]
    selected_styles = st.sidebar.multiselect(
        "Select tournament type",
        options=all_tournament_styles,
        default=all_tournament_styles
    )

    min_bb, max_bb = st.sidebar.slider(
        "Big Blind Range (BB)",
        min_value=40,
        max_value=900,
        value=(40, 900),
        step=10
    )

    all_positions = ["BTN", "SB", "BB", "CO", "UTG", "MP", "BTN/SB"]
    selected_positions = st.sidebar.multiselect(
        "Select player position",
        options=all_positions,
        default=all_positions
    )

    min_hands_played = st.sidebar.slider(
        "Minimum number of plays (profiling)",
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

    st.sidebar.subheader("🛠️ Architecture Technology Stack")
    st.sidebar.code(f"""
    - ETL: Python (Regex)
    - DB: {db_option.split(' ')[0]}
    - Analytics: SQL, SciPy
    - Viz: Streamlit, Seaborn
    """)

    # -------------------------------------------------------------------------
    # 메인 헤더 배너 (프리미엄 그라디언트 적용)
    # -------------------------------------------------------------------------
    st.markdown("""<div class=\"main-header\">
        <h1>🎰 iGaming unstructured log-based user behavior analysis dashboard</h1>
        <p>Poker hand big data loading platform and game core KPI / analysis of experimental hypothesis verification results</p>
    </div>""", unsafe_allow_html=True)

    # 탭 메뉴 구성
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📈 Summary of key indicators (Overview)", 
        "👥 Player Profiling", 
        "📊 Funnel & Cohort Analysis", 
        "🧪 A/B Test Hypothesis Testing (A/B Test)",
        "🎮 Scenario Simulator"
    ])

    # =========================================================================
    # TAB 1: 핵심 지표 요약 (Overview)
    # =========================================================================
    with tab1:
        st.subheader("🎯 Summary of platform activity metrics")

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
            st.markdown(f"""<div class=\"custom-card\">
                <div class=\"card-label\">Total Hands</div>
                <div class=\"card-value\">{basic_stats['total_hands'][0]:,} version</div>
            </div>""", unsafe_allow_html=True)
        with c2:
            st.markdown(f"""<div class=\"custom-card\" style=\"border-top-color: #10B981;\">
                <div class=\"card-label\">Number of collected action logs (Total Actions)</div>
                <div class=\"card-value\">{basic_stats['total_actions'][0]:,} card</div>
            </div>""", unsafe_allow_html=True)
        with c3:
            st.markdown(f"""<div class=\"custom-card\" style=\"border-top-color: #8B5CF6;\">
                <div class=\"card-label\">Number of platform unique users (Total Players)</div>
                <div class=\"card-value\">{basic_stats['total_players'][0]:,} people</div>
            </div>""", unsafe_allow_html=True)

        st.markdown("---")
        st.subheader("👤 Analysis target: Hero’s core play indicators")

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
            status_vpip = '<span style="color: #10B981; font-weight: bold;">🟢 Optimal</span>' if 15.0 <= hero_vpip <= 25.0 else '<span style="color: #EF4444; font-weight: bold;">🔴 Imbalance</span>'
            status_pfr = '<span style="color: #10B981; font-weight: bold;">🟢 Optimal</span>' if 12.0 <= hero_pfr <= 20.0 else '<span style="color: #EF4444; font-weight: bold;">🔴 Imbalance</span>'
            status_af = '<span style="color: #10B981; font-weight: bold;">🟢 Optimal</span>' if 2.0 <= hero_af <= 3.5 else '<span style="color: #EF4444; font-weight: bold;">🔴 Imbalance</span>'
            status_win = '<span style="color: #10B981; font-weight: bold;">🟢 Optimal</span>' if 15.0 <= hero_win <= 22.0 else '<span style="color: #EF4444; font-weight: bold;">🔴 Imbalance</span>'
            status_net = '<span style="color: #10B981; font-weight: bold;">🟢 Black</span>' if hero_net >= 0 else '<span style="color: #EF4444; font-weight: bold;">🔴 Red</span>'

            hc1, hc2, hc3, hc4, hc5 = st.columns(5)

            with hc1:
                st.markdown(f"""<div class=\"custom-card\">
                    <div class=\"card-label\">VPIP (Voluntary Participation Rate)</div>
                    <div class=\"card-value\">{hero_vpip} %</div>
                    <div style=\"margin-top: 0.5rem; border-top: 1px solid #E2E8F0; padding-top: 0.4rem; font-size: 0.75rem; color: #64748B;\">
                        Standard: 15% ~ 25%<br>{status_vpip}
                    </div>
                </div>""", unsafe_allow_html=True)
            with hc2:
                st.markdown(f"""<div class=\"custom-card\">
                    <div class=\"card-label\">PFR (First Strike Rate)</div>
                    <div class=\"card-value\">{hero_pfr} %</div>
                    <div style=\"margin-top: 0.5rem; border-top: 1px solid #E2E8F0; padding-top: 0.4rem; font-size: 0.75rem; color: #64748B;\">
                        Standard: 12% ~ 20%<br>{status_pfr}
                    </div>
                </div>""", unsafe_allow_html=True)

            with hc3:
                st.markdown(f"""<div class=\"custom-card\">
                    <div class=\"card-label\">AF (Aggressiveness Level)</div>
                    <div class=\"card-value\">{hero_af}</div>
                    <div style=\"margin-top: 0.5rem; border-top: 1px solid #E2E8F0; padding-top: 0.4rem; font-size: 0.75rem; color: #64748B;\">
                        Standard: 2.0 ~ 3.5<br>{status_af}
                    </div>
                </div>""", unsafe_allow_html=True)
            with hc4:
                st.markdown(f"""<div class=\"custom-card\">
                    <div class=\"card-label\">Win Rate</div>
                    <div class=\"card-value\">{hero_win} %</div>
                    <div style=\"margin-top: 0.5rem; border-top: 1px solid #E2E8F0; padding-top: 0.4rem; font-size: 0.75rem; color: #64748B;\">
                        Standard: 15% ~ 22%<br>{status_win}
                    </div>
                </div>""", unsafe_allow_html=True)
            with hc5:
                # 수익성 칩은 손실 여부에 따라 보더 색상 대응
                color_border = "#EF4444" if hero_net < 0 else "#10B981"
                st.markdown(f"""<div class=\"custom-card\" style=\"border-top-color: {color_border};\">
                    <div class=\"card-label\">Accumulated Chip P&L (Net Chips)</div>
                    <div class=\"card-value\">{hero_net:,} chip</div>
                    <div style=\"margin-top: 0.5rem; border-top: 1px solid #E2E8F0; padding-top: 0.4rem; font-size: 0.75rem; color: #64748B;\">
                        Criteria: Accumulated Chips > 0<br>{status_net}
                    </div>
                </div>""", unsafe_allow_html=True)

            # Hero의 칩 손익에 따른 동적 진단 메세지 생성
            if hero_net >= 0:
                diag_chips_msg = f"Accumulated chip profit and loss, which is a long-term expected profit, also recorded <b>{hero_net:,} chip surplus</b>, proving the validity of the indicator."
            else:
                diag_chips_msg = (
                    f"However, the final accumulated chip profit and loss is <b>{hero_net:,} chip deficit</b>.<br>"
                    f"Key engagement style indicators such as VPIP ({hero_vpip}%), PFR ({hero_pfr}%) and AF ({hero_af}) are within the optimal range, indicating very good basic betting habits.<br>"
                    f"However, <b>the final win rate (Win Rate: {hero_win}%) did not reach the appropriate range (15% to 22%)</b>, so chip losses were not avoided and a large deficit was suffered.<br>"
                    f"This is actual analysis evidence showing that even if the style indicator is optimal, if the balance is not harmonized, such as increasing the stake when winning and losing quickly when losing, it is inevitable to suffer cumulative losses."
                )

            st.markdown(f"""<div class=\"info-banner\">
                💡 <b>Comprehensive diagnosis of Hero behavioral indicators</b>: Hero's main participation methods, VPIP, PFR, and AF, are located within the designed optimal range, showing a stable play style that leads the game by carefully selecting cards and attacking first when entering.
                <br><br>{diag_chips_msg}
            </div>""", unsafe_allow_html=True)
        else:
            st.info("💡 There is currently no number of Heroes that match the filter conditions. Please adjust your sidebar filters.")

        # KPI 산출 공식 및 SQL 수식 정보 제공 아코디언
        st.markdown(" ")
        with st.expander("📝 Key activity indicators (KPI) optimal guidelines and definitions"):
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
            st.markdown('<div class="math-box">VPIP (%) = (Number of games Call/Bet/Raise played in the pre-flop stage) / (Number of games in which all cards were distributed) * 100</div>', unsafe_allow_html=True)
            st.markdown("""#### 2. PFR (Pre-flop Raise)
            * <b>Definition</b>: This is the ratio of the number of rounds that were proactively raised during the pre-flop stage.
            * <b>Formula</b>:""", unsafe_allow_html=True)
            st.markdown('<div class="math-box">PFR (%) = (Number of games with Raise in the pre-flop stage) / (Number of games with all cards distributed) * 100</div>', unsafe_allow_html=True)
            st.markdown("""#### 3. AF (Aggression Factor)
            * <b>Definition</b>: The ratio of the number of aggressive actions (Bet, Raise) that actively shake the board to the number of passive actions (Call) that follow the opponent's bet in the post-flop stage.
            * <b>Formula</b>:""", unsafe_allow_html=True)
            st.markdown('<div class="math-box">AF = (Number of Bets in Post-flop phase + Number of Raises) / (Number of Calls in Post-flop phase)</div>', unsafe_allow_html=True)
            st.markdown("""#### 4. Win Rate
            * <b>Definition</b>: The percentage of games participated that finished with a chip profit or loss greater than 0.
            * <b>Formula</b>:""", unsafe_allow_html=True)
            st.markdown('<div class="math-box">Win Rate (%) = (Number of profitable games) / (Total number of participating games) * 100</div>', unsafe_allow_html=True)
            st.markdown("""
            """, unsafe_allow_html=True)


    # =========================================================================
    # TAB 2: 플레이어 프로파일링 (Profiling)
    # =========================================================================
    with tab2:
        st.subheader("👥 Player Behavior Profiling Data Mart")
        st.markdown("Data is filtered by gaming tendency cohort based on users' play indicators stored in the database.")

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
            pb.player_name AS \"player name\",
            pb.total_hands AS \"total number of hands\",
            ROUND(COALESCE(pa.vpip_hands, 0) * 100.0 / pb.total_hands, 2) AS \"VPIP (%)\",
            ROUND(COALESCE(pa.pfr_hands, 0) * 100.0 / pb.total_hands, 2) AS \"PFR (%)\",
            CASE 
                WHEN COALESCE(pfa.passive_actions, 0) = 0 THEN CASE WHEN COALESCE(pfa.agg_actions, 0) > 0 THEN 5.0 ELSE 0.0 END
                ELSE ROUND(pfa.agg_actions * 1.0 / pfa.passive_actions, 2)
            END AS \"Aggression (AF)\",
            ROUND(pb.won_hands * 100.0 / pb.total_hands, 2) AS \"Win rate (%)\",
            pb.net_chips_won AS \"profit chips\",
            CASE 
                WHEN (pa.vpip_hands * 100.0 / pb.total_hands) >= 30.0 AND (pa.pfr_hands * 100.0 / pb.total_hands) < 15.0 THEN 'Loose-Passive'
                WHEN (pa.vpip_hands * 100.0 / pb.total_hands) >= 30.0 AND (pa.pfr_hands * 100.0 / pb.total_hands) >= 15.0 THEN 'Loose-Aggressive'
                WHEN (pa.vpip_hands * 100.0 / pb.total_hands) < 30.0 AND (pa.pfr_hands * 100.0 / pb.total_hands) >= (pa.vpip_hands * 0.8 / pb.total_hands) THEN 'Tight-Aggressive'
                WHEN (pa.vpip_hands * 100.0 / pb.total_hands) < 15.0 THEN 'Tight-Passive'
                ELSE 'Neutral'
            END AS \"Playstyle\"
        FROM player_base pb
        LEFT JOIN preflop_actions pa ON pb.player_name = pa.player_name
        LEFT JOIN postflop_actions pfa ON pb.player_name = pfa.player_name
        WHERE pb.total_hands >= {min_hands_played}
        """
        df_profile = load_data(df_profile_query, params_hp * 3)

        # 검색 및 필터 컴포넌트 배치
        col_f1, col_f2 = st.columns([1, 3])
        style_options = list(df_profile['Playstyle'].unique()) if not df_profile.empty else []
        with col_f1:
            st.markdown("##### 🔍 Player Filtering")
            search_name = st.text_input("Nickname search", "")
            style_filter = st.multiselect(
                "Play style tendencies", 
                options=style_options, 
                default=style_options
            )

        if not df_profile.empty:
            df_filtered = df_profile[df_profile['Playstyle'].isin(style_filter)]
            if search_name:
                df_filtered = df_filtered[df_filtered['player name'].str.contains(search_name, case=False)]
        else:
            df_filtered = pd.DataFrame()

        with col_f2:
            # 데이터프레임 시각화
            st.dataframe(df_filtered, use_container_width=True, height=220)

        st.markdown("---")

        st.markdown("<h4 style='text-align: center;'>📈 VPIP vs PFR behavior distribution chart</h4>", unsafe_allow_html=True)
        c_chart, c_desc = st.columns([3.5, 2.5])

        with c_chart:
            if not df_filtered.empty:
                fig, ax = plt.subplots(figsize=(6, 3.8))

                # 가이드 대각선 표시를 위해 한계값 동적 산정
                max_val = max(df_filtered['VPIP (%)'].max() + 5, 50)
                ax.plot([0, 100], [0, 100], color='#CBD5E1', linestyle='--', linewidth=1.2, label='PFR = VPIP (limit line)')

                sns.scatterplot(
                    x='VPIP (%)',
                    y='PFR (%)',
                    hue='Playstyle',
                    data=df_filtered,
                    palette='Set1',
                    ax=ax,
                    s=45,
                    alpha=0.85
                )

                ax.set_xlim(0, max_val)
                ax.set_ylim(0, max_val)
                ax.set_title("Player Behavior Matrix (VPIP vs PFR)", fontsize=10, fontweight='bold', pad=10)
                ax.set_xlabel("Voluntary Participation Rate VPIP (%)", fontsize=8)
                ax.set_ylabel("Preemptive strike rate PFR (%)", fontsize=8)
                ax.tick_params(labelsize=8)

                # 범례 정리
                handles, labels = ax.get_legend_handles_labels()
                ax.legend(handles, labels, title="Playstyle", title_fontsize=8, fontsize=7, loc='upper left')

                plt.tight_layout()
                st.pyplot(fig)
                plt.close(fig)
            else:
                st.warning("⚠️ The distribution chart cannot be displayed because there is no player data matching the filtered criteria.")

        with c_desc:
            st.markdown("""<div class=\"info-banner\" style=\"margin-top: 0.2rem; font-size: 0.82rem; line-height: 1.5; padding: 1rem;\">
                🔍 <b>VPIP vs PFR behavioral matrix correlation in-depth analysis</b>
                <br><br>
                The distribution of players' VPIP (Volunteer Participation Rate) and PFR (First Strike Rate) is a key baseline for user preference segmentation, and there is a strong positive correlation between the two indicators depending on the domain (poker) and mathematical definition.
                <br><br>
                📌 <b>1. Mathematical Subset Relations and Limits (PFR ≤ VPIP)</b>
                <br>PFR (entry via first raise) is a mathematical sub-subset of VPIP (all voluntary entry). This means that <b>PFR can never exceed VPIP because you must first be in the game to raise.</b> This causes all data points on the chart to exist only in the <b>bottom right area of ​​the diagonal baseline (PFR = VPIP)</b>.
                <br><br>
                📌 <b>2. Strong positive linear correlation between the two indicators</b>
                <br>As users actively select cards and participate, the frequency of raises (attacks) increases proportionally, so the overall player distribution shows a <b>strong positive linear correlation</b> that slops diagonally to the right. This is a section where the correlation coefficient is very high.
                <br><br>
                📌 <b>3. Strategic significance of gap from diagonal baseline (VPIP - PFR)</b>
                <br>· <b>The narrower the gap (diagonally adjacent)</b>: When participating in a game, it is an <b>Aggressive</b> tendency to take the initiative by raising rather than simply calling. It is advantageous in the long run as you can utilize ‘Fold Equity’ to induce your opponent to fold.
                <br>· <b>The wider the gap (further from the diagonal)</b>: It is a <b>Passive</b> tendency to passively follow other people's bets without raising one's own initiative when entering the game. It's easy to hand over the initiative to your opponent and easily accumulate losses.
                <br><br>
                📌 <b>4. Segmentation of player tendencies by quadrant</b>
                <ul>
                    <li><b>Tight-Aggressive (TA)</b>: A skilled group that enters cautiously with strict cards but takes the lead with a raise upon entry (optimal range for Hero).</li>
                    <li><b>Loose-Passive (LP)</b>: Beginner/unskilled group with the highest risk of bankruptcy by entering with a large number of unfavorable cards and only calling other people's bets without taking the initiative.</li>
                </ul>
            </div>""", unsafe_allow_html=True)


    # =========================================================================
    # TAB 3: 퍼널 & 코호트 분석 (Funnel & Cohort)
    # =========================================================================
    with tab3:
        st.subheader("📊 Game Analysis Framework: Funnel & Cohort")

        st.markdown("""<div class=\"info-banner\" style=\"background-color: #F8FAFC; border-left-color: #475569; color: #334155; margin-top: 0.5rem; margin-bottom: 1.5rem; font-size: 0.92rem; padding: 0.9rem;\">
            🔍 <b>Definition of analysis concepts and framework</b><br>
            <ul>
                <li><b>Funnel Analysis</b>: It is an analysis technique that finds bottlenecks in the path by exploring which sections the user mainly <b>drops off</b> and <b>converts</b> as they go through several stages until they reach the final goal (e.g., advancing to Showdown).</li>
                <li><b>Cohort Analysis</b>: This is a technique to segment users into <b>same groups</b> that share common experiences or behavioral characteristics, such as play style groups, and to track and compare changes in assets or continuous retention rates over time.</li>
            </ul>
        </div>""", unsafe_allow_html=True)

        col_fn1, col_fn2 = st.columns(2)

        with col_fn1:
            st.markdown("#### 📉 Hand participation funnel for each betting round (In-Game Betting Funnel)")
            st.markdown("""This is a <b>Hand Participation Progression Funnel</b> that shows how far players advance to the next betting stage within each hand of a game (Hand) without giving up (Fold).""", unsafe_allow_html=True)

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
                ax_fn.set_title("Cumulative survival rate by stage (funnel)", fontsize=10, fontweight='bold')
                ax_fn.tick_params(labelsize=8)
                plt.tight_layout()
                st.pyplot(fig_fn)
                plt.close(fig_fn)
            else:
                st.warning("⚠️ There is no funnel data matching the selected conditions.")

            with st.expander("🔍 Detailed explanation of funnel diagram (Pre-flop 100% and step-by-step meaning)", expanded=True):
                st.markdown(textwrap.dedent("""* <b>1. Pre-flop (Pre-flop: 100%)</b>: When a game begins, all players are <b>unconditionally distributed 2 personal cards and participate in the game</b>, so the starting point is <b>the standard value of 100%</b>.
                * <b>2. Flop (Flop: approx. 57.0%)</b>: This is the stage where three common cards are laid out on the floor of the table. Excluding those who folded pre-flop because their cards were too unfavorable, this means that <b>only about 57% of the total hands actually participated in betting to see the common cards of this flop phase</b>. (In other words, in the pre-flop phase, about 43% of players save their chips by immediately giving up after seeing a bad hand.)
                * <b>3. Turn (turn: approximately 44.0%)</b>: This is the stage where the fourth common card is additionally laid out. This is the percentage of players who survive after checking the flop cards and enter by paying an additional bet.
                * <b>4. River (River: approx. 33.0%)</b>: This is a betting round in which the final fifth common card is laid out to complete the final card family tree (combination).
                * <b>5. Showdown (approximately 25.0%)</b>: This is the final stage where all final betting is completed and the remaining players reveal their cards to determine the winner or loser.

                💡 <b>Domain analytical significance (step-by-step risk management)</b>:
                Unlike funnel analysis of general IT web/app services, the <b>step-by-step withdrawal (Fold) behavior that occurs within a game play session is not a member churn (churn) where the user withdraws from the platform service.</b> This is an extremely rational and active <b>step-by-step risk control decision</b> to minimize the user's chip loss. The fact that a large withdrawal rate of more than 40% occurs when going from pre-flop to flop proves that players are playing the game smartly and not taking unreasonable mathematical risks."""), unsafe_allow_html=True)

        with col_fn2:
            st.markdown("#### 👥 Cumulative profit trend for 30 sessions by propensity cohort")
            st.markdown("Player tendency This is a line graph showing the average trend of how assets (chips) are accumulated when game sessions are repeated for the same cohort.")

            cohort_query = f"""
            -- Step 1: First count the total number of games (Hands) participated by each player. (Requirement: Player with at least 20 games)
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
            -- Step 2: Count the number of pre-flop actions (VPIP and PFR) for each player in a single scan.
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
            -- Step 3: Combine the data collected in steps 1 and 2 1:1 to calculate the final VPIP(%) and PFR(%) indicators.
            player_profiles AS (
                SELECT 
                    pb.player_name,
                    pb.total_hands,
                    COALESCE(ps.vpip_hands, 0) * 100.0 / pb.total_hands AS vpip,
                    COALESCE(ps.pfr_hands, 0) * 100.0 / pb.total_hands AS pfr
                FROM player_base pb
                LEFT JOIN preflop_stats ps ON pb.player_name = ps.player_name
            ),
            -- Step 4: Define play style cohort groups based on calculated VPIP and PFR.
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
            -- Step 5: Number each player's session (1st through 30th rounds) to analyze cumulative profits over time.
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
            -- Step 6: Make a final search by matching the cohort group information with the cumulative profit indicator of 30 sessions or less.
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
                ax_ch.set_title("Session cumulative average asset trend by cohort group", fontsize=10, fontweight='bold')
                ax_ch.set_xlabel("play session", fontsize=8)
                ax_ch.set_ylabel("Cumulative Chips", fontsize=8)
                ax_ch.tick_params(labelsize=8)
                plt.legend(fontsize=7, title_fontsize=8)
                plt.tight_layout()
                st.pyplot(fig_ch)
                plt.close(fig_ch)
            else:
                st.warning("⚠️ There is no cohort data matching the selected conditions.")

            with st.expander("🔍 Detailed explanation of cohort graph (axis and line graph meaning)", expanded=True):
                st.markdown(textwrap.dedent("""* <b>Cohort Group</b>: A <b>group with the same playing tendency</b> classified based on analysis of players' VPIP (Participation Rate) and PFR (First Strike Rate).
                  - <b>Tight-Aggressive (Orange)</b>: A core skilled group that buys cards quickly and takes the initiative aggressively only when strong (the model that Hero aims for).
                  - <b>Loose-Passive (light green)</b>: A novice/unskilled group that participates too often, regardless of the card, and only follows other people's bets without taking the lead in betting.
                * <b>X-axis (play session)</b>: Cumulative number of rounds the player has played the game (time series trend from the 1st edition to the 30th edition).
                * <b>Y-Axis (Accumulated Chips)</b>: When the starting point of game participation is set to 0, this refers to the cumulative total of chips earned or lost on average by the player as each game session accumulates.
                  - <b>Red dotted line (based on line 0)</b>: If located above this line, it indicates a cumulative average surplus, and if located below this line, it indicates a cumulative average deficit.

                💡 <b>Analytical significance (profit and loss distribution by play tendency)</b>:
                * In the <b>Loose-Passive (passive beginner)</b> group, the cumulative deficit worsens very quickly as sessions are repeated (moving to the right of the X-axis). This is because you only make comprador calls and waste your stake.
                * On the other hand, the <b>Tight-Aggressive</b> group mathematically proves the survival strategy of minimizing chip loss and protecting assets."""), unsafe_allow_html=True)

        # -------------------------------------------------------------------------
        # 하단 배너 매칭
        # -------------------------------------------------------------------------
        st.markdown(" ")
        col_bn1, col_bn2 = st.columns(2)

        with col_bn1:
            st.markdown("""<div class=\"info-banner\" style=\"font-size: 0.85rem; padding: 0.75rem; min-height: 125px;\">
                💡 <b>Funnel Insight (Participation Stage Analysis)</b>: More than 40% of folds (abandonment of participation) occur when switching from pre-flop to flop. 
                This shows an <b>active risk management behavior pattern</b> in which players prevent chip leaks by quickly giving up unfavorable cards after being dealt cards (pre-flop) and before the first three common cards are laid out.
            </div>""", unsafe_allow_html=True)

        with col_bn2:
            st.markdown("""<div class=\"info-banner\" style=\"font-size: 0.85rem; padding: 0.75rem; min-height: 125px;\">
                💡 <b>Cohort Insight (Cumulative Profit and Loss Analysis)</b>: The Loose-Passive group's average accumulated chip assets continue to trend downward as sessions accumulate. 
                Because they participate in the game with unfavorable cards and passively follow the bets, they have the highest probability of losing all their chips and <b>busting out of the table</b> during long sessions.
            </div>""", unsafe_allow_html=True)


    # =========================================================================
    # TAB 4: A/B 테스트 가설 검정 (A/B Test)
    # =========================================================================
    with tab4:
        st.subheader("🧪 A/B testing playground")
        st.markdown("Based on the established hypothesis, a data-based statistical test (T-Test) is run in real time to determine the significance of profits according to the strategy.")

        st.markdown("""<div class=\"info-banner\" style=\"background-color: #F0FDF4; border-left-color: #10B981; color: #14532D; font-size: 0.95rem; margin-top: 0.5rem; margin-bottom: 1.5rem;\">
            🎯 <b>A/B Testing Key Takeaway: “When you are dealt a premium hand, is it better to raise (strike first)?”</b><br>
            This experiment statistically verifies whether the strategy of <b>actively raising the bet (Group A - Raise)</b> when obtaining the best cards (AA, KK, QQ)</b> maximizes profits to a greater extent than the passive strategy of simply <b>following the call (Group B - Call/Check)</b>.
            <br><br>
            📢 <b>Analysis conclusion</b>: The average and median profits of the group (A) that made a preemptive raise with a premium card were significantly higher than the group (B) that simply followed. However, due to the nature of poker, the ups and downs (volatility) of the stakes that come and go in each hand are so severe that additional analysis hands must continue to accumulate to prove 95% statistical certainty (p-value < 0.05).
        </div>""", unsafe_allow_html=True)

        st.info("""* __Hypothesis Design__:
          - __Experiment subject (A/B plan)__: When holding a premium hand (AA, KK, QQ), the group that raised the bet amount in the pre-flop stage (Group A: raise) vs. the group that simply called/checked (Group B: call/check)
          - __Basic idea (null hypothesis)__: When holding a premium card, there is no statistical difference in the final profit whether you raise or call (it is a difference in luck, not a difference in strategy).
          - __Testing goal (alternative hypothesis)__: Group A, which increases the stake by actively raising, receives statistically significantly higher profits.""")

        # A/B 테스트 데이터 쿼리 로드
        where_hp, params_hp = build_sql_filter(include_tournament=True, include_bb=True, include_position=True, hands_alias='h', t_alias='t', hp_alias='hp', prepend_and=True)
        ab_query = f"""
        -- Step 1: Extract the players who were distributed premium hands (AA, KK, QQ) and the number of chips earned.
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
        -- Step 2: Quickly extract the list of players and game IDs that raised in the preflop stage from actions.
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
        -- Step 3: Divide the test group (Group A vs. Group B) by matching the premium hand list and preflop raising history.
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
            st.subheader("📋 Real-time test summary")
            if not df_ab.empty:
                desc_df = df_ab.groupby('test_group')['chips_won'].describe()
                desc_df.columns = ['Sample count (count)', 'average profit (mean)', 'standard deviation (std)', 'Minimum (min)', '25%', 'Median (50%)', '75%', 'maximum value (max)']
                st.dataframe(desc_df.round(2), use_container_width=True)
            else:
                st.warning("⚠️ There is no sample data matching the criteria you selected.")

            st.markdown(f"""<b>🧪 Statistical test indicator results</b>
            * <b>T-Statistic</b>: `{t_stat:.4f}`
            * <b>Probability of significance (p-value)</b>: `{p_val:.4f}`""", unsafe_allow_html=True)

            if has_enough_data and not np.isnan(p_val):
                if p_val < 0.05:
                    st.success(f"🎯 __Decision: Accept alternative hypothesis__ (p-value = {p_val:.6f} < 0.05)\n\nStatistically significant difference has been verified! The strategy of increasing the stake by actively raising when a premium hand is made (Group A) is much better at securing expected long-term profitability.")
                else:
                    st.warning(f"⚠️ __Decision: Accept the null hypothesis__ (p-value = {p_val:.6f} >= 0.05)\n\nThe difference in means between the two groups is not statistically significant. (Please refer to the detailed cause analysis explanation below.)")
            else:
                st.info("⚠️ The sample size is too small to run a statistical hypothesis test (T-Test). Please load more hands by relaxing the filter conditions.")

        with col_ab2:
            st.subheader("📊 Confidence interval visualization")
            if not df_ab.empty:
                fig_ab, ax_ab = plt.subplots(figsize=(6, 3.8))
                sns.barplot(x='test_group', y='chips_won', data=df_ab, errorbar='ci', capsize=0.1, palette='Set2', ax=ax_ab)
                ax_ab.set_title("Comparison of average chip acquisition amount by group (95% confidence interval)", fontsize=10, fontweight='bold')
                ax_ab.set_ylabel("chips_won", fontsize=8)
                ax_ab.set_xlabel("test_group", fontsize=8)
                ax_ab.tick_params(labelsize=8)
                plt.tight_layout()
                st.pyplot(fig_ab)
                plt.close(fig_ab)
            else:
                st.warning("⚠️ There is no data to display the chart.")

        st.markdown("---")
        st.markdown("### 💡 A/B test statistical test results and indicator analysis commentary")

        st.markdown(textwrap.dedent(f"""This is a detailed explanation of the T-Test results calculated in real time on the dashboard.

        #### 1. 📊 Intuitive interpretation of real-time summary table items
        * <b>Sample count (count)</b>: The total number of premium cards (AA, KK, QQ) distributed. Group A, which actively raised, was observed <b>{len(group_a)} times</b>, and Group B, which called passively, was observed <b>{len(group_b)} times</b>.
        * <b>Average profit (mean)</b>: Average chips obtained per hand. Group A has <b>{group_a.mean():,.1f} chips</b>, which are numerically higher than Group B's <b>{group_b.mean():,.1f} chips</b>.
        * <b>Standard Deviation (std)</b>: The volatility (up and down) of returns. Both groups, <b>{group_a.std():,.1f} chips</b> and <b>{group_b.std():,.1f} chips</b>, show very extreme fluctuations of more than <b>5 to 8 times</b> compared to their average returns.
        * <b>Median (50%)</b>: The pure median return excluding extreme values. Group A is a <b>{group_a.median():,.1f} chip</b>, while Group B is a <b>{group_b.median():,.1f} chip</b>, showing that first strike yielded more solid returns in the majority of hands.

        #### 2. 🧪 Meaning of key statistical terms and indicators
        * <b>T-Statistic [<b>{t_stat:.4f}</b>]</b>
          - <b>Meaning</b>: A standardized ratio that indicates “how large the difference between the means of two groups is compared to the ups and downs (standard deviation) of the data.” The larger this number is in absolute terms (usually greater than 2), the more significant the gap in returns between the two groups is.
          - <b>Analysis of current results</b>: The current figure of `{t_stat:.4f}` means that the difference in average returns between the two groups is very small compared to the terrifying ups and downs (volatility) of the data within the two groups.
        * <b>Probability of significance (p-value) [<b>{p_val:.4f}</b>]</b>
          - <b>Meaning</b>: This is the probability of observing this level of profit gap by chance, under the premise that “in reality, there is no profit difference between the two strategies (it is a coincidence).”
          - <b>Current result analysis</b>: Current significance probability is <b>`{p_val*100:.1f}%` ({p_val:.4f})</b>. To be statistically recognized as a true strategy difference, this probability must be less than `5%` (p < 0.05). Therefore, we currently adopt the null hypothesis that <b>“We cannot be sure with 95% confidence whether the difference in average returns is due to the superiority of the strategy or simple random volatility (luck)”</b>.

        #### 3. 🔍 Two major reasons from a data perspective for the null hypothesis to be accepted
        1. <b>Extreme volatility unique to poker games (High Variance)</b>
           - Poker is a highly volatile domain where tens of thousands of chips are exchanged in just one game, such as all-in or jackpot/small win. The average gap between the two groups is about 1,220 chips, while the ups and downs (standard deviation) reach a whopping 17,000 to 19,000 chips, which is more than 15 times the average difference. As we tried to verify the subtle signal amid this loud noise, we were unable to find a statistically significant difference.
        2. <b>Small Sample Size of Group B</b>
           - Compared to Group A ({len(group_a)} cases), who held a premium card and raised, the number of data in Group B ({len(group_b)} cases), which only made calls, was too small. The smaller the sample size, the weaker the statistical power, which makes it impossible to prove that the actual difference is significant even if it exists.

        #### 🎯 Data Analyst Recommendation (Next Action)
        * <b>Additional data loading</b>: The game log collection period must be increased to secure additional samples for Group B (at least 100 or more).
        * <b>Outlier Correction</b>: If we control noise by re-performing the T-test after excluding outlier plates that gained/lost extremely large chips or cutting them to a specific percentile (Winsorization), we will be able to more clearly verify the statistical superiority of the preemptive attack (Group A)."""), unsafe_allow_html=True)


    # =========================================================================
    # TAB 5: 🎮 시나리오 시뮬레이터 (Simulator)
    # =========================================================================
    with tab5:
        st.subheader("🎮 Real-time data streaming & play style simulation")
        st.markdown("This tab provides a sandbox where you can reproduce real-time numerical changes in the process of streaming raw log data into a database (DB) or adjust betting strategy indicators.")

        # 구분선 및 ETL 시뮬레이션 섹션
        st.markdown("### ⚡ Real-time data loading simulation (Streaming ETL)")
        st.markdown("Monitors the process of parsing and loading unstructured text log files into a relational database in real time. When you press the button, the cumulative loading graph moves and the count increases.")

        if st.button("🚀 Start real-time data loading simulation"):
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
                hands_box.markdown(f"""<div class=\"custom-card\">
                    <div class=\"card-label\">Number of loaded games (Hands)</div>
                    <div class=\"card-value\" style=\"color: #3B82F6;\">{curr_hands:,} / {total_hands_in_db:,}</div>
                </div>""", unsafe_allow_html=True)

                actions_box.markdown(f"""<div class=\"custom-card\" style=\"border-top-color: #10B981;\">
                    <div class=\"card-label\">Loaded action log (Actions)</div>
                    <div class=\"card-value\" style=\"color: #10B981;\">{curr_actions:,} / {total_actions_in_db:,}</div>
                </div>""", unsafe_allow_html=True)

                players_box.markdown(f"""<div class=\"custom-card\" style=\"border-top-color: #8B5CF6;\">
                    <div class=\"card-label\">Number of identified users (Players)</div>
                    <div class=\"card-value\" style=\"color: #8B5CF6;\">{curr_players:,} / {total_players_in_db:,}</div>
                </div>""", unsafe_allow_html=True)

                # 진행 상태 바 업데이트
                progress_bar.progress(i / steps)

                # Hero 누적 손익 실시간 그래프 리프레시
                limit_hero = int(len(df_hero_hands) * (i / steps))
                df_sub = df_hero_hands.iloc[:limit_hero].copy()
                if not df_sub.empty:
                    df_sub['cum_won'] = df_sub['chips_won'].cumsum()

                    fig_sim, ax_sim = plt.subplots(figsize=(10, 3.5))
                    ax_sim.plot(df_sub['cum_won'].values, color='#3B82F6', linewidth=2, label='Hero Cumulative P&L')
                    ax_sim.axhline(0, color='red', linestyle='--', linewidth=1)
                    ax_sim.set_title("Hero cumulative chip trend according to real-time loading progress (Live)", fontsize=11, fontweight='bold')
                    ax_sim.set_xlabel("Number of hands played", fontsize=8)
                    ax_sim.set_ylabel("Cumulative Chip P&L", fontsize=8)
                    ax_sim.tick_params(labelsize=8)
                    ax_sim.grid(True, linestyle=':', alpha=0.6)
                    plt.tight_layout()
                    chart_placeholder.pyplot(fig_sim)
                    plt.close(fig_sim)

                time.sleep(0.12)

            st.success("🎉 Real-time ETL parsing and database load of 7,993 hands of 140 raw_hh files completed successfully!")

        st.markdown("---")
        st.markdown("### 🎭 Playstyle Sandbox")
        st.markdown("When you set the desired play indicators (VPIP, PFR, AF), user tendencies are classified in real time, and the cumulative profit and loss curves of the three real players with the most similar indicators are loaded from the DB to visually compare simulations.")

        col_sb1, col_sb2 = st.columns([2, 3])
        with col_sb1:
            st.markdown("#### 🎚️ Player Strategy Inclination Controller")
            sim_vpip = st.slider("VPIP (voluntary participation rate, %)", min_value=0, max_value=100, value=20, step=1)
            sim_pfr = st.slider("PFR (First Strike Rate, %)", min_value=0, max_value=100, value=15, step=1)
            if sim_pfr > sim_vpip:
                st.warning("⚠️ PFR (First Strike Rate) cannot exceed VPIP (Volunteer Participation Rate). Limit PFR equal to the VPIP value.")
                sim_pfr = sim_vpip

            sim_af = st.slider("AF (Postflop Aggressiveness)", min_value=0.0, max_value=5.0, value=2.5, step=0.1)

            # 플레이 스타일 성향 자동 분류
            if sim_vpip >= 30.0 and sim_pfr < 15.0:
                sim_style = 'Loose-Passive (LP)'
                sim_style_desc = "Passively participate in numerous rounds. The chip loss rate is high because you are drawn to the opponent's bet."
            elif sim_vpip >= 30.0 and sim_pfr >= 15.0:
                sim_style = 'Loose-Aggressive (LAG)'
                sim_style_desc = "Participation is high and betting is very aggressive. Create a large pot and show high risk and high return."
            elif sim_vpip < 30.0 and sim_pfr >= (sim_vpip * 0.8):
                sim_style = 'Tight-Aggressive (TAG)'
                sim_style_desc = "I am a strategically skilled regular player who carefully selects good cards and then actively attacks them."
            elif sim_vpip < 15.0:
                sim_style = 'Tight-Passive (TP)'
                sim_style_desc = "Play defensively, waiting for too many good cards. Blindbee experiences a cumulative deficit."
            else:
                sim_style = 'Neutral'
                sim_style_desc = "This is a standard user style that represents a fairly neutral metric range."

            st.markdown(f"""<div class=\"info-banner\" style=\"background-color: #EFF6FF; border-left-color: #3B82F6; color: #1E3A8A; font-size: 0.95rem;\">
                🎭 <b>Style classification results</b>: <span style=\"font-weight: 800; font-size: 1.1rem; color: #1D4ED8;\">{sim_style}</span><br>
                <i>{sim_style_desc}</i><br><br>
                Set indicators: VPIP={sim_vpip}%, PFR={sim_pfr}%, AF={sim_af}
            </div>""", unsafe_allow_html=True)

        with col_sb2:
            st.markdown("#### 📈 Profit/loss simulation matching closest real users")

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
                    ax_sb.set_title("Accumulated chips trend of matched users over 30 sessions (Sandbox)", fontsize=10, fontweight='bold')
                    ax_sb.set_xlabel("play session", fontsize=8)
                    ax_sb.set_ylabel("Cumulative Chips", fontsize=8)
                    ax_sb.tick_params(labelsize=8)
                    ax_sb.legend(fontsize=7)
                    plt.tight_layout()
                    st.pyplot(fig_sb)
                    plt.close(fig_sb)

                    # 유사도 매칭 유저 리스트 출력
                    st.markdown("🕵️ **Most similar real player matching information:**")
                    for idx, row in top_players.iterrows():
                        st.write(f"- **{row['player_name']}**: VPIP={row['vpip']:.1f}%, PFR={row['pfr']:.1f}%, AF={row['af']:.1f} (distance difference: {row['distance']:.2f})")
                else:
                    conn.close()
                    st.info("⚠️ There is no session data for matched players.")
            else:
                conn.close()
                st.info("⚠️ No matching player data exists.")

    # 데이터베이스 점검 완료 안내 출력 (Streamlit 로그용)
    print("Streamlit dashboard refresh complete!")

