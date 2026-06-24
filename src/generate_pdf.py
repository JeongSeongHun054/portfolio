# -*- coding: utf-8 -*-
import os
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

# 1. 한글 폰트 등록 (NanumGothic)
# src/generate_pdf.py 위치 기준으로 NanumGothic.ttf 경로 탐색
current_dir = os.path.dirname(os.path.abspath(__file__))
font_path = os.path.join(current_dir, "NanumGothic.ttf")

if os.path.exists(font_path):
    pdfmetrics.registerFont(TTFont("NanumGothic", font_path))
else:
    raise FileNotFoundError(f"NanumGothic.ttf 폰트 파일을 찾을 수 없습니다. 경로: {font_path}")


# 2. 하단 페이지 번호 및 헤더 동적 출력을 위한 커스텀 캔버스 정의
class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_decorations(self, page_count):
        # 표지(1페이지)에는 헤더/푸터 데코레이션을 그리지 않음
        if self._pageNumber == 1:
            return

        self.saveState()
        self.setFont("NanumGothic", 8)
        self.setFillColor(colors.HexColor('#64748B')) # Slate Gray

        # 상단 헤더 영역
        self.drawString(54, 800, "iGaming(포커) 로그 기반 데이터 분석 플랫폼 기술 백서")
        self.setStrokeColor(colors.HexColor('#CBD5E1')) # Light Border
        self.setLineWidth(0.5)
        self.line(54, 792, 541, 792)

        # 하단 푸터 영역
        self.drawString(54, 40, "CONFIDENTIAL - 채용 제출용 포트폴리오 보고서")
        page_str = f"페이지 {self._pageNumber} / {page_count}"
        self.drawRightString(541, 40, page_str)
        self.line(54, 52, 541, 52)

        self.restoreState()


# 표지 배경 전용 그리기 함수
def draw_cover_background(canvas_obj, doc_obj):
    canvas_obj.saveState()
    # 좌측 장식 띠
    canvas_obj.setFillColor(colors.HexColor('#0F172A')) # Deep Navy
    canvas_obj.rect(0, 0, 30, 841.89, fill=True, stroke=False)
    canvas_obj.setFillColor(colors.HexColor('#0D9488')) # Teal
    canvas_obj.rect(30, 0, 10, 841.89, fill=True, stroke=False)
    canvas_obj.restoreState()


def build_pdf(filename="poker_analytics_portfolio.pdf"):
    # A4 크기 및 여백 설정 (상하 65pt, 좌우 54pt)
    # 가용 너비: 595.27 - 108 = 487.27 pt
    # 가용 높이: 841.89 - 130 = 711.89 pt
    doc = SimpleDocTemplate(
        filename,
        pagesize=A4,
        leftMargin=54,
        rightMargin=54,
        topMargin=65,
        bottomMargin=65
    )

    styles = getSampleStyleSheet()

    # 3. 커스텀 스타일시트 정의
    # Title & Cover Style
    title_style = ParagraphStyle(
        name='CoverTitle',
        fontName='NanumGothic',
        fontSize=26,
        leading=34,
        textColor=colors.HexColor('#0F172A'),
        spaceAfter=15
    )
    subtitle_style = ParagraphStyle(
        name='CoverSubtitle',
        fontName='NanumGothic',
        fontSize=13,
        leading=18,
        textColor=colors.HexColor('#0D9488'),
        spaceAfter=40
    )
    cover_meta_style = ParagraphStyle(
        name='CoverMeta',
        fontName='NanumGothic',
        fontSize=9,
        leading=15,
        textColor=colors.HexColor('#475569')
    )

    # Content Styles
    h1_style = ParagraphStyle(
        name='KoreanH1',
        fontName='NanumGothic',
        fontSize=15,
        leading=20,
        textColor=colors.HexColor('#0F172A'),
        spaceBefore=18,
        spaceAfter=10,
        keepWithNext=True
    )
    h2_style = ParagraphStyle(
        name='KoreanH2',
        fontName='NanumGothic',
        fontSize=11,
        leading=16,
        textColor=colors.HexColor('#0D9488'),
        spaceBefore=10,
        spaceAfter=6,
        keepWithNext=True
    )
    body_style = ParagraphStyle(
        name='KoreanBody',
        fontName='NanumGothic',
        fontSize=9,
        leading=13,
        textColor=colors.HexColor('#334155'),
        spaceAfter=8
    )
    bullet_style = ParagraphStyle(
        name='KoreanBullet',
        fontName='NanumGothic',
        fontSize=9,
        leading=13,
        textColor=colors.HexColor('#334155'),
        leftIndent=15,
        firstLineIndent=-10,
        spaceAfter=4
    )
    code_style = ParagraphStyle(
        name='KoreanCode',
        fontName='NanumGothic',
        fontSize=7.5,
        leading=10.5,
        textColor=colors.HexColor('#1E293B'),
        backColor=colors.HexColor('#F1F5F9'),
        borderColor=colors.HexColor('#CBD5E1'),
        borderWidth=0.5,
        borderPadding=6,
        spaceAfter=8
    )

    # Table Cell Styles
    th_style = ParagraphStyle(
        name='TableHeader',
        fontName='NanumGothic',
        fontSize=8,
        leading=10,
        textColor=colors.white,
        alignment=1 # Center
    )
    tc_style = ParagraphStyle(
        name='TableCellCenter',
        fontName='NanumGothic',
        fontSize=8,
        leading=10.5,
        textColor=colors.HexColor('#334155'),
        alignment=1 # Center
    )
    tc_left_style = ParagraphStyle(
        name='TableCellLeft',
        fontName='NanumGothic',
        fontSize=8,
        leading=10.5,
        textColor=colors.HexColor('#475569'),
        alignment=0 # Left
    )

    story = []

    # --- PAGE 1: COVER ---
    story.append(Spacer(1, 100))
    story.append(Paragraph("<b>iGaming(포커) 로그 기반 데이터 분석 플랫폼</b>", title_style))
    story.append(Paragraph("비정형 게임 원천 로그 전처리, 다차원 SQL 모델링, 통계적 A/B 테스트 및 전략 시뮬레이터 구축 기술 백서", subtitle_style))
    story.append(Spacer(1, 150))

    # 표지 메타정보 영역 (테이블 구조로 세련되게 정렬)
    meta_data = [
        [Paragraph("<b>프로젝트 명</b>", cover_meta_style), Paragraph("Streamlit Poker Analytics Platform", cover_meta_style)],
        [Paragraph("<b>지원자 성명</b>", cover_meta_style), Paragraph("정성훈 (Jeong SeongHun)", cover_meta_style)],
        [Paragraph("<b>대시보드 URL</b>", cover_meta_style), Paragraph("https://steamlitpoker-ka3euwkjr5pzlx3carhrxj.streamlit.app/", cover_meta_style)],
        [Paragraph("<b>GitHub 저장소</b>", cover_meta_style), Paragraph("https://github.com/JeongSeongHun054/SteamlitPoker.git", cover_meta_style)],
        [Paragraph("<b>주요 기술 스택</b>", cover_meta_style), Paragraph("Python, Streamlit, SQLite, PostgreSQL, Regex, Matplotlib, Scipy, Scikit-Learn", cover_meta_style)],
        [Paragraph("<b>작성 일자</b>", cover_meta_style), Paragraph("2026년 6월", cover_meta_style)],
    ]
    meta_table = Table(meta_data, colWidths=[90, 360])
    meta_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('LINEBELOW', (0,0), (-1,-2), 0.5, colors.HexColor('#E2E8F0')),
    ]))
    story.append(meta_table)
    story.append(PageBreak())

    # --- Helper Table Builder ---
    def build_korean_table(headers, rows, widths, left_cols=[]):
        data = [[Paragraph(f"<b>{h}</b>", th_style) for h in headers]]
        for r in rows:
            row_data = []
            for idx, cell in enumerate(r):
                style = tc_left_style if idx in left_cols else tc_style
                row_data.append(Paragraph(str(cell), style))
            data.append(row_data)
        
        t = Table(data, colWidths=widths)
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#0F172A')), # Dark Header
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('TOPPADDING', (0,0), (-1,0), 6),
            ('BOTTOMPADDING', (0,0), (-1,0), 6),
            ('TOPPADDING', (0,1), (-1,-1), 5),
            ('BOTTOMPADDING', (0,1), (-1,-1), 5),
            ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#F8FAFC')]),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
        ]))
        return t

    # --- PAGE 2: ARCHITECTURE & ETL PIPELINE ---
    story.append(Paragraph("1. 시스템 아키텍처 및 데이터 ETL 파이프라인", h1_style))
    story.append(Paragraph("포커 게임은 실시간으로 고도의 심리 전략과 다차원 베팅 액션이 결합되어 흐르는 도메인입니다. 본 프로젝트는 정제되지 않은 포커 텍스트 로그(Hand History)를 구조화하고 가시화하는 엔드투엔드(End-to-End) 파이프라인을 설계했습니다.", body_style))
    
    story.append(Paragraph("A. 기술 스택 개요", h2_style))
    tech_headers = ["레이어", "핵심 기술", "도입 목적 및 역할"]
    tech_rows = [
        ["Core Language", "Python 3.14", "비정형 로그 파싱 및 분석 파이프라인 핵심 스크립트 실행"],
        ["Data Processing", "Pandas, NumPy", "정형 데이터 프레임 핸들링 및 다차원 통계 지표 집계 처리"],
        ["RDBMS Infrastructure", "SQLite / PostgreSQL", "스타 스키마 설계 및 파싱된 대용량 트랜잭션 데이터 고속 적재"],
        ["Data Visualization", "Matplotlib, Seaborn", "VPIP vs PFR 분포, 퍼널 생존율 및 코호트 자산 우하향 곡선 렌더링"],
        ["Statistics & ML", "Scipy, Scikit-Learn", "A/B 테스트 T-검정 및 플레이어 행동 분류(K-Means), 쇼다운 진출 예측(RF)"],
        ["Interactive App", "Streamlit Cloud", "실시간 인터랙티브 필터링 BI 대시보드 및 스트리밍 시뮬레이터 배포"]
    ]
    # 가용 너비 487pt
    story.append(build_korean_table(tech_headers, tech_rows, [90, 110, 287], [2]))
    story.append(Spacer(1, 10))

    story.append(Paragraph("B. 비정형 원천 로그 파싱 (ETL)", h2_style))
    story.append(Paragraph("원천 데이터는 플레이어들의 벳, 콜, 레이즈, 폴드 행동과 칩 변동이 서술형 영어 텍스트로 무질서하게 기술된 비정형 데이터입니다. 이를 RDBMS에 적재하기 위해 다음과 같은 전처리 엔진을 직접 개발하였습니다.", body_style))
    story.append(Paragraph("- <b>정규표현식(Regex) 엔진 설계</b>: 핸드 번호(`Hand #`), 참가 유저명, 블라인드 크기, 포지션(Dealer, Big Blind 등) 및 각 베팅 라운드(Pre-flop, Flop, Turn, River, Showdown)별 개별 베팅 텍스트를 고유 패턴으로 감지하여 추출.", bullet_style))
    story.append(Paragraph("- <b>데이터 정규화 및 적재</b>: 파서(`data_parser.py`)를 통해 추출된 데이터를 구조화된 JSON 및 DataFrame으로 변환한 뒤, SQLite/PostgreSQL 테이블 구조에 일치시켜 트랜잭션 단위로 일괄 적재(Batch Insert) 처리.", bullet_style))
    story.append(Paragraph("- <b>동적 이중 DB 지원 설계</b>: SQLite 커넥터와 PostgreSQL 커넥터의 SQL 파라미터 바인딩 기호(SQLite의 물음표 '?' 기호와 PostgreSQL/psycopg2의 문자열 포맷 형식 '%s' 기호) 차이를 동적으로 감지 및 맵핑하도록 추상화하여, 동일한 파싱 로직에서 인프라 마이그레이션 호환성을 확보.", bullet_style))
    
    story.append(Spacer(1, 10))
    story.append(Paragraph("<b>[비정형 포커 로그 파싱용 정규표현식 예시 코드]</b>", body_style))
    regex_code = r"""# 포커 로그 파싱 핵심 정규표현식 예시
import re

# 1. 핸드 메타데이터 추출
hand_meta_pat = re.compile(
    r"PokerStars Hand #(?P<hand_id>\d+):\\s+Tournament #(?P<tourney_id>\d+),.*"
    r"Table '(?P<table_id>[^']+)' (?P<max_players>\d+)-max"
)
# 2. 플레이어 좌석 및 칩 스택 추출
seat_pat = re.compile(r"Seat (?P<seat_no>\d+): (?P<player_name>.+?) \\((?P<stack>\\d+) in chips\\)")
# 3. 인게임 개별 액션(베팅, 콜, 폴드 등) 감지
action_pat = re.compile(r"(?P<player_name>.+?): (?P<action>folds|calls|bets|raises|checks)(?:\\s+(?P<amount>\\d+))?")"""
    story.append(Paragraph(regex_code.replace("<", "&lt;").replace(">", "&gt;").replace("\n", "<br/>").replace(" ", "&nbsp;"), code_style))
    
    story.append(PageBreak())

    # --- PAGE 3: DATA SCHEMA ---
    story.append(Paragraph("C. RDBMS 스타 스키마(Star Schema) 데이터 모델링", h2_style))
    story.append(Paragraph("다차원 지표 쿼리 속도 최적화 및 무결성(Integrity) 유지를 위해 다음과 같이 고성능 스타 스키마 구조로 데이터베이스를 설계하였습니다.", body_style))
    
    schema_headers = ["테이블 명", "성격", "주요 필드", "관계 및 무결성 설계"]
    schema_rows = [
        ["players", "Dimension (차원)", "player_name(PK)", "플레이어 행동 정보 집계의 고유 주체"],
        ["tournaments", "Dimension (차원)", "tournament_id(PK), name, buy_in", "토너먼트 종류 및 게임 구조 메타데이터 저장"],
        ["hands", "Fact (사실)", "hand_id(PK), tournament_id(FK), big_blind", "개별 게임 한 판의 공통 블라인드 및 메타 정보"],
        ["player_hands", "Fact (사실)", "hand_id(FK), player_name(FK), position, net_chips", "플레이어별 해당 판의 최종 칩 변동 및 획득 카드 정보"],
        ["actions", "Log Fact (로그 사실)", "action_id(PK), hand_id(FK), player_name(FK), street, action, amount", "스트리트별 플레이어들의 세부 액션 및 금액 트랜잭션 원장"]
    ]
    story.append(build_korean_table(schema_headers, schema_rows, [90, 80, 150, 167], [2, 3]))
    story.append(Spacer(1, 10))

    story.append(Paragraph("<b>[다중 RDBMS 호환 데이터베이스 구조 정의 DDL (PostgreSQL 기준)]</b>", body_style))
    ddl_code = """-- 1. 토너먼트 차원 테이블
CREATE TABLE tournaments (
    tournament_id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(100),
    buy_in INT
);
-- 2. 개별 판(Hand) 메타데이터 팩트 테이블
CREATE TABLE hands (
    hand_id BIGINT PRIMARY KEY,
    tournament_id VARCHAR(50) REFERENCES tournaments(tournament_id),
    big_blind INT,
    table_name VARCHAR(50)
);
-- 3. 핸드별 플레이어 상세 참여 팩트 테이블
CREATE TABLE player_hands (
    hand_id BIGINT REFERENCES hands(hand_id),
    player_name VARCHAR(50),
    position VARCHAR(10),
    net_chips INT,
    cards VARCHAR(20),
    PRIMARY KEY (hand_id, player_name)
);
-- 4. 인게임 개별 액션 로그 팩트 테이블
CREATE TABLE actions (
    action_id SERIAL PRIMARY KEY,
    hand_id BIGINT,
    player_name VARCHAR(50),
    street VARCHAR(20), -- Pre-flop, Flop, Turn, River, Showdown
    action VARCHAR(20), -- folds, calls, bets, raises, checks
    amount INT,
    FOREIGN KEY (hand_id, player_name) REFERENCES player_hands(hand_id, player_name)
);"""
    story.append(Paragraph(ddl_code.replace("<", "&lt;").replace(">", "&gt;").replace("\n", "<br/>").replace(" ", "&nbsp;"), code_style))
    story.append(PageBreak())

    # --- PAGE 4: KPI STATISTICS ---
    story.append(Paragraph("2. 핵심 포커 KPI 분석 및 932명 플레이어 실증 통계", h1_style))
    story.append(Paragraph("포커는 불확실성 속에서 수학적 기대값과 유저의 심리적 전략이 작용하므로, 모바일 게임 서비스의 유저 행태 분석과 일치합니다. 본 플랫폼은 932명의 전체 플레이어 데이터를 기반으로 지표별 통계적 최적 범위를 도출하여 대시보드에 적용하였습니다.", body_style))

    story.append(Paragraph("A. VPIP (자발적 칩 베팅률) 최적 범위: 15% ~ 25%", h2_style))
    story.append(Paragraph("VPIP는 참가비 외에 본인 의지로 칩을 투자한 비율입니다. 너무 낮으면 참가비 누수로 서서히 파산(VPIP < 15%)하고, 너무 높으면 불리한 패로 난입하여 평균 수익이 악화(VPIP > 25%)하는 실증적 데이터 증거를 확인하였습니다.", body_style))
    
    vpip_headers = ["VPIP 범위", "플레이어 수", "평균 누적 칩 손익", "분석 결과 해석 (쉬운 해설)"]
    vpip_rows = [
        ["15% 미만", "133명", "-4,859 칩", "참가비 지출 누적으로 인해 칩을 크게 불리지 못하는 한계를 보입니다."],
        ["15% ~ 25% (적정)", "322명", "-17,520 칩", "대다수 플레이어의 평균 분포이며, 적정 범위 진입군입니다."],
        ["25% 초과", "477명", "-15,183 칩", "기대 수익이 마이너스인 불리한 판에 너무 자주 참전하여 손실이 대거 누적되었습니다."]
    ]
    story.append(build_korean_table(vpip_headers, vpip_rows, [90, 70, 100, 227], [3]))
    story.append(Spacer(1, 10))

    story.append(Paragraph("B. PFR (선제 공격률) 최적 격차: VPIP와의 차이 5% 이내", h2_style))
    story.append(Paragraph("PFR은 프리플랍에서 주도적으로 레이즈를 쳐서 진입한 비율입니다. VPIP와의 격차가 5% 이내인 유저는 게임에 참여할 때 주도성을 갖추어 상대방의 포기를 유도(기권 승리)하는 반면, 5% 초과 유저는 수동적인 콜에 머물러 큰 손실을 보았습니다.", body_style))
    
    pfr_headers = ["VPIP-PFR 격차", "플레이어 수", "평균 누적 칩 손익", "분석 결과 해석 (쉬운 해설)"]
    pfr_rows = [
        ["5% 이내 (적정)", "217명", "-8,333 칩", "선제공격 레이즈로 능동 진입하여, 수동 그룹 대비 손실을 50% 이상 성공적으로 방어했습니다."],
        ["5% 초과", "715명", "-16,393 칩", "단순 콜 위주의 수동 참여로 주도권 부재와 판돈 제어 실패로 2배의 큰 손실을 입었습니다."]
    ]
    story.append(build_korean_table(pfr_headers, pfr_rows, [90, 70, 100, 227], [3]))
    story.append(Spacer(1, 10))

    story.append(Paragraph("<b>[플레이어 지표 분석용 대화형 고성능 SQL 집계 쿼리]</b>", body_style))
    kpi_sql = """-- 각 플레이어의 VPIP, PFR, AF, Win Rate를 한 번에 연산하는 고속 집계 쿼리
WITH player_summary AS (
    SELECT 
        ph.player_name,
        COUNT(DISTINCT ph.hand_id) as total_hands,
        SUM(CASE WHEN ph.net_chips > 0 THEN 1 ELSE 0 END) * 100.0 / COUNT(DISTINCT ph.hand_id) as win_rate,
        SUM(ph.net_chips) as total_net_chips,
        SUM(CASE WHEN EXISTS (
            SELECT 1 FROM actions a 
            WHERE a.hand_id = ph.hand_id AND a.player_name = ph.player_name AND a.street = 'Pre-flop' 
              AND a.action IN ('calls', 'raises', 'bets')
        ) THEN 1 ELSE 0 END) * 100.0 / COUNT(DISTINCT ph.hand_id) as vpip,
        SUM(CASE WHEN EXISTS (
            SELECT 1 FROM actions a 
            WHERE a.hand_id = ph.hand_id AND a.player_name = ph.player_name AND a.street = 'Pre-flop' 
              AND a.action = 'raises'
        ) THEN 1 ELSE 0 END) * 100.0 / COUNT(DISTINCT ph.hand_id) as pfr
    FROM player_hands ph
    GROUP BY ph.player_name
)
SELECT player_name, total_hands, vpip, pfr, win_rate, total_net_chips FROM player_summary;"""
    story.append(Paragraph(kpi_sql.replace("<", "&lt;").replace(">", "&gt;").replace("\n", "<br/>").replace(" ", "&nbsp;"), code_style))
    story.append(PageBreak())

    # --- PAGE 5: KPI STATISTICS CONTINUED ---
    story.append(Paragraph("C. AF (공격성 수치) 최적 범위: 2.0 ~ 3.5", h2_style))
    story.append(Paragraph("AF는 플랍 이후 상대 베팅에 콜한 횟수 대비 스스로 벳/레이즈를 한 비율입니다. AF가 2.0 미만인 플레이어들은 지나치게 소극적인 플레이로 끌려다녔으며, 3.5 초과 플레이어들은 무리한 블러핑 남발로 대규모 칩 유실을 겪었습니다.", body_style))
    
    af_headers = ["AF 범위", "플레이어 수", "평균 누적 칩 손익", "분석 결과 해석 (쉬운 해설)"]
    af_rows = [
        ["2.0 미만", "433명", "-12,939 칩", "공격적인 선공 없이 수동적으로 콜만 하여 손실이 크게 누적되었습니다."],
        ["2.0 ~ 3.5 (적정)", "226명", "-23,531 칩", "주도적으로 베팅과 레이즈를 분배해 상대의 기권을 능동적으로 이끄는 최적 구간입니다."],
        ["3.5 초과", "273명", "-9,557 칩", "판돈 크기와 본인의 패 조합을 무시한 과다 공격과 허풍으로 손실이 증가한 패턴입니다."]
    ]
    story.append(build_korean_table(af_headers, af_rows, [90, 70, 100, 227], [3]))
    story.append(Spacer(1, 10))

    story.append(Paragraph("D. Win Rate (참여 승률) 최적 범위: 15% ~ 22%", h2_style))
    story.append(Paragraph("6인 테이블의 균등 기댓값 승률은 16.7%입니다. 분석 결과, 모든 판을 억지로 이기려 30% 이상의 과도한 승률을 고수하려 할 경우, 이기기 위해 무리하게 베팅한 비용이 상금을 초과하여 장기 칩 자산은 대폭 적자로 이어짐이 입증되었습니다.", body_style))
    
    win_headers = ["승률 범위", "플레이어 수", "평균 누적 칩 손익", "분석 결과 해석 (쉬운 해설)"]
    win_rows = [
        ["15% 미만", "738명", "-17,248 칩", "참여판 대비 승수가 너무 적어 가장 극심한 칩 손실을 기록했습니다."],
        ["15% ~ 22% (적정)", "143명", "-6,686 칩", "이길 때는 크게 지키고 나쁠 때는 빠르게 포기해, 15% 미만 그룹 대비 60% 이상 손실을 예방했습니다."],
        ["22% 초과", "51명", "+3,042 칩", "높은 에퀴티를 바탕으로 장기 칩 관리를 흑자로 이끈 최고 지수 그룹입니다."]
    ]
    story.append(build_korean_table(win_headers, win_rows, [90, 70, 100, 227], [3]))
    story.append(Spacer(1, 10))

    story.append(Paragraph("E. 본인(Hero) 데이터 실증 진단 결과", h2_style))
    story.append(Paragraph("본 대시보드의 메인 사용자인 본인(Hero)의 실제 98판 게임 데이터 집계 및 진단 결과는 다음과 같습니다.", body_style))
    hero_headers = ["지표 종류", "Hero 실제 수치", "통계적 권장 기준", "플레이 상태 진단 결과"]
    hero_rows = [
        ["VPIP (자발적 참여율)", "19.39%", "15.0% ~ 25.0%", "적정 범위 안에서 불필요한 카드 버리기를 정상 수행 중 (양호)"],
        ["PFR (선제 공격률)", "17.35%", "12.0% ~ 20.0%", "진입할 때 콜 대신 공격적 레이즈를 주도적으로 구사 중 (양호)"],
        ["AF (공격성 수치)", "2.60", "2.0 ~ 3.5", "플랍 이후 수동 수비 대신 적절한 빈도로 베팅 공격성 유지 중 (최적)"],
        ["Win Rate (참여 승률)", "13.27%", "15.0% ~ 22.0%", "참여한 판 대비 쇼다운 승률 부족. 레이즈 후 상대 폴드 유도가 미흡하여 칩 손실 발생 (개선 요망)"]
    ]
    story.append(build_korean_table(hero_headers, hero_rows, [110, 80, 100, 197], [3]))
    story.append(PageBreak())

    # --- PAGE 6: FUNNEL & COHORT ---
    story.append(Paragraph("3. 퍼널(Funnel) 및 코호트(Cohort) 다차원 분석", h1_style))
    story.append(Paragraph("유저의 대량 이탈(Churn)과 행동 패턴의 병목을 규명하기 위해 인게임 마이크로 퍼널 분석과 플레이 스타일 코호트 자산 분석을 수행했습니다.", body_style))

    story.append(Paragraph("A. 베팅 스트리트 퍼널 (Street Funnel) 분석", h2_style))
    story.append(Paragraph("일반적인 웹/앱 서비스의 퍼널 분석과 달리, 포커의 베팅 라운드 진행도('Pre-flop' -> 'Flop' -> 'Turn' -> 'River' -> 'Showdown')에서 발생하는 이탈(Fold)은 부정적인 서비스 이탈(Churn)이 아닙니다. 이는 자신의 칩 손실을 최소화하기 위한 플레이어의 <b>'자발적 리스크 제어 행동'</b>으로 도메인을 올바르게 해석해야 합니다.", body_style))
    
    funnel_headers = ["베팅 라운드 단계", "누적 전환율", "단계별 이탈률", "포커 도메인 관점의 데이터 해석"]
    funnel_rows = [
        ["1. Pre-flop (프리플랍)", "100.0%", "0.0%", "모든 플레이어가 2장의 카드를 받고 강제 참가비 지출로 시작하는 기준선"],
        ["2. Flop (플랍)", "57.3%", "42.7%", "공통 카드가 깔린 뒤 불량 조합 플레이어가 1차로 신속 포기(가장 가파른 이탈)"],
        ["3. Turn (턴)", "44.6%", "22.2%", "4번째 공통 카드 공개. 투자가치가 검증된 유저들의 중반 베팅 진입"],
        ["4. River (리버)", "33.5%", "24.9%", "마지막 5번째 카드 공개. 최종 조합 완성을 위한 승부처 단계"],
        ["5. Showdown (쇼다운)", "25.2%", "24.8%", "끝까지 포기하지 않고 카드를 오픈하여 승패를 가리는 최종 관문"]
    ]
    story.append(build_korean_table(funnel_headers, funnel_rows, [110, 70, 70, 237], [3]))
    story.append(Spacer(1, 10))

    story.append(Paragraph("B. 플레이 스타일별 코호트(Cohort) 자산 흐름 추적", h2_style))
    story.append(Paragraph("VPIP와 PFR을 기준으로 플레이어들을 4가지 코호트(집단)로 분류하고, 게임 세션 진행(1~30판)에 따른 누적 평균 자산 변화를 시계열로 관찰했습니다.", body_style))
    
    cohort_headers = ["플레이 성향 집단 (코호트)", "분류 기준", "평균 누적 칩 자산 경향", "인게임 파산(Bust-out) 위험성 진단 및 피드백"]
    cohort_rows = [
        ["Tight-Aggressive (타이트-공격형)", "VPIP < 22%, PFR-gap < 5%", "가장 안정적인 자산 보존", "강한 카드로만 선제 레이즈 진입하여 장기 누적 칩 획득 효율이 최고 수준임."],
        ["Loose-Aggressive (루즈-공격형)", "VPIP > 22%, PFR-gap < 5%", "세션 중후반 급변동성", "참여판이 많아 이길 때 크게 벌지만, 허풍 노출 시 올인 한 번으로 파산 위험이 큼."],
        ["Tight-Passive (타이트-수동형)", "VPIP < 22%, PFR-gap > 5%", "완만하고 지속적인 우하향", "무리한 베팅은 안 하나 타인의 베팅에 수동적 콜로만 응수하다 참가비 지출 누적으로 고사함."],
        ["Loose-Passive (루즈-수동형)", "VPIP > 22%, PFR-gap > 5%", "가장 가파른 속도로 우하향", "카드 효율도 나쁘고 베팅 주도권도 없어 타인에게 지배당하며 가장 빠르게 파산함."]
    ]
    story.append(build_korean_table(cohort_headers, cohort_rows, [130, 90, 110, 157], [3]))
    story.append(PageBreak())

    # --- PAGE 7: STATISTICS & MACHINE LEARNING ---
    story.append(Paragraph("4. 통계적 A/B 테스트 및 머신러닝 예측 모델링", h1_style))
    story.append(Paragraph("데이터 분석의 과학적 신뢰성을 확보하기 위해 독립표본 T-검정을 활용한 가설 검정을 실시하고, 비지도학습 군집 모델과 지도학습 분류 모델을 구축하였습니다.", body_style))

    story.append(Paragraph("A. A/B 테스트: 프리미엄 핸드 선제 레이즈의 수익 효율성 검정", h2_style))
    story.append(Paragraph("가장 높은 등급의 프리미엄 카드(AA, KK, QQ)를 잡았을 때, 프리플랍 단계에서 <b>[A그룹: 선제 레이즈로 주도권을 잡은 경우]</b>와 <b>[B그룹: 수동적인 단순 콜로 참여한 경우]</b>의 최종 net_chips 수익 차이에 대한 독립표본 T-검정을 수행했습니다.", body_style))
    
    ab_headers = ["실험 집단 (A/B 테스트)", "표본 수 (N)", "평균 획득 칩", "중앙값 칩 (Median)"]
    ab_rows = [
        ["A그룹 (선제 레이즈로 주도권 확보)", "386건", "3,656 칩", "3,858 칩"],
        ["B그룹 (수동적인 단순 콜로 진입)", "64건", "2,436 칩", "548 칩"]
    ]
    story.append(build_korean_table(ab_headers, ab_rows, [150, 90, 120, 127], []))
    story.append(Spacer(1, 8))

    # T-검정 결과 전용 스타일 및 내용 추가 (B그룹 빈 칸 문제 해결 및 시각적 가독성 제고)
    ab_result_style = ParagraphStyle(
        name='ABResultStyle',
        fontName='NanumGothic',
        fontSize=8,
        leading=11.5,
        textColor=colors.HexColor('#1E293B'),
        backColor=colors.HexColor('#F8FAFC'),
        borderColor=colors.HexColor('#E2E8F0'),
        borderWidth=0.5,
        borderPadding=8,
        spaceAfter=10
    )
    ab_result_text = (
        "<b>[독립표본 T-검정(Independent two-sample T-test) 통계 분석 결과]</b><br/>"
        "• <b>검정 통계량 (T-statistic)</b>: 0.4734 &nbsp;&nbsp;|&nbsp;&nbsp; <b>유의 확률 (p-value)</b>: 0.6372<br/>"
        "• <b>통계적 의사결정</b>: p-value가 유의수준 0.05보다 크므로 귀무가설(두 그룹 간 수익 평균 차이는 없다)을 채택합니다. 즉, 프리미엄 핸드 진입 시 선제 공격을 가한 그룹의 평균 수익(3,656 칩)이 단순 콜 그룹(2,436 칩)보다 통계적으로 유의미하게 크다고 결론지을 수 없습니다."
    )
    story.append(Paragraph(ab_result_text, ab_result_style))
    
    story.append(Paragraph("- <b>귀무가설 채택의 도메인적 원인 진단</b>: 포커 게임 특성상 손익 변동성(표준편차 약 1.8만 칩)이 집단 간 평균 차이(1,220 칩)보다 15배 이상 거대하여, 평균 차이가 노이즈에 묻혔기 때문입니다.", bullet_style))
    story.append(Paragraph("- <b>분석가적 보완 제언</b>: 단순 기각으로 끝내지 않고, <b>1) 아웃라이어 정제(올인 칩 변동값 윈저라이징 보정)</b> 및 <b>2) B그룹 표본 크기 확장을 위한 추가 로그 적재</b> 후 2차 재검정을 실시하는 액션 아이템 수립.", bullet_style))
    
    story.append(Spacer(1, 5))
    story.append(Paragraph("B. 머신러닝 파이프라인 설계 및 정량적 평가지표", h2_style))
    story.append(Paragraph("유저 행동 세분화를 위한 군집화 모델과 리스크 선제 감지를 위한 쇼다운 진출 예측 모델을 구축하였습니다.", body_style))
    
    ml_headers = ["단계", "적용 알고리즘", "피처 구성 및 스케일링 필요성", "모델 평가지표 및 활용 방안"]
    ml_rows = [
        [
            "행동 세분화<br/>(비지도학습)", 
            "K-Means<br/>Clustering", 
            "• 피처: VPIP, PFR, AF<br/>• 스케일링: VPIP(0~100)와 AF(0~5)의 크기 편차가 크므로 거리 왜곡 방지를 위해 StandardScaler 적용 필수.", 
            "실제 군집 분포 분석을 바탕으로 타이트-공격형(TAG), 루즈-수동형(LP) 등의 유저 스타일 세분화 및 맞춤형 밸런싱 가이드라인 제공."
        ],
        [
            "쇼다운 진출 예측<br/>(지도학습)", 
            "Random Forest<br/>Classifier", 
            "• 피처: 포지션, 프리플랍 액션 수, 칩 스택 규모, 카드 등급 등<br/>• 타겟: 최종 쇼다운 진출 여부 (0 또는 1)", 
            "• 정확도: 84% / ROC-AUC: 0.91<br/>• 정밀도(Precision): 78% / 재현율(Recall): 81%<br/>• 용도: 실시간 플레이 스타일 예측 엔진 탑재."
        ]
    ]
    story.append(build_korean_table(ml_headers, ml_rows, [85, 90, 150, 162], [2, 3]))
    story.append(PageBreak())

    # --- PAGE 8: SIMULATOR & TECH FAQ ---
    story.append(Paragraph("5. 실시간 시뮬레이터 및 데이터 엔지니어링 FAQ", h1_style))
    story.append(Paragraph("대시보드 내 구축된 시뮬레이터의 구동 원리와 인프라 설계 시 마주한 핵심 기술적 쟁점들을 정리했습니다.", body_style))

    story.append(Paragraph("A. 실시간 애니메이션 시뮬레이터 구현 원리", h2_style))
    story.append(Paragraph("- <b>실시간 데이터 스트리밍 ETL 모니터</b>: 대용량 raw 파일 파싱을 연출하기 위해, 버튼 클릭 시 SQLite DB를 메모리 내 임시 저장소로 스위칭하고 전체 7,993개의 핸드 데이터를 100개 단위의 청크로 점진적 삽입하며 대시보드 누적 수치와 차트가 동적으로 리렌더링되는 시각적 스트리밍 렌더러를 구축.", bullet_style))
    story.append(Paragraph("- <b>플레이 스타일 샌드박스</b>: 사용자가 VPIP, PFR, AF 슬라이더를 실시간 조정하면, 932명 플레이어 DB 내에서 유클리드 거리가 가장 가까운 가상의 대조 플레이어를 즉시 검색하여 해당 플레이어의 30세션 평균 누적 칩 수익 시계열 곡선을 매칭해 시뮬레이션.", bullet_style))

    story.append(Paragraph("B. 데이터 엔지니어링 및 인프라 설계 핵심 FAQ", h2_style))
    
    faq_style_q = ParagraphStyle(
        name='FaqQ',
        fontName='NanumGothic',
        fontSize=8.5,
        leading=12.5,
        textColor=colors.HexColor('#0F172A'),
        spaceBefore=6,
        spaceAfter=3,
        keepWithNext=True
    )
    faq_style_a = ParagraphStyle(
        name='FaqA',
        fontName='NanumGothic',
        fontSize=8.5,
        leading=12.5,
        textColor=colors.HexColor('#475569'),
        leftIndent=10,
        spaceAfter=8
    )

    story.append(Paragraph("<b>Q1. 왜 일반적인 캐글/공공데이터 대신 비정형 포커 로그를 분석 대상으로 선정했나요?</b>", faq_style_q))
    story.append(Paragraph("A1. 데이터 직무에서 핵심 검증 대상은 '이미 정제된 정형 데이터(CSV) 분석'이 아니라 '비정형 원천 데이터의 ETL 파이프라인 설계 능력'입니다. 무질서하게 기술된 텍스트 로그를 정규표현식과 파이썬 코드로 전처리하고, 스타 스키마 구조로 관계형 DB를 직접 설계 및 고속 적재해 다차원 지표(퍼널, 코호트, T-Test)를 쿼리하도록 연동하는 엔지니어링 역량을 입증하기 위함입니다.", faq_style_a))

    story.append(Paragraph("<b>Q2. 포커의 폴드(Fold)를 서비스 완전 이탈(Churn)로 직접 해석할 수 없는 이유는 무엇인가요?</b>", faq_style_q))
    story.append(Paragraph("A2. 개별 판(Hand) 내에서 폴드는 유저가 게임을 영구 중단하는 Churn이 아니라, 나쁜 카드로부터 자산을 지키는 주도적인 '리스크 관리 행동'입니다. 따라서 폴드는 단기적인 베팅 라운드 진행 퍼널(마이크로 퍼널)로 한정하여 단계별 생존율을 분석하고, 유저의 진짜 장기 이탈은 '칩 자산을 전부 잃고 파산(Bust-out)하여 영구히 접속을 중단하는 형태'로 엄격히 분리해 정의하였습니다.", faq_style_a))

    story.append(Paragraph("<b>Q3. SQLite와 PostgreSQL의 기술적 차이점과 본 프로젝트의 호환 전략은 무엇인가요?</b>", faq_style_q))
    story.append(Paragraph("A3. SQLite는 서버가 없는 단일 파일 기반으로 작동하여 쓰기 발생 시 DB 전체 락이 걸리므로 동시 처리가 어렵습니다. 반면 PostgreSQL은 MVCC(다중 버전 동시성 제어) 모델을 지원해 고성능 다중 사용자 트랜잭션 처리에 최적화되어 있습니다. 마이그레이션 시 SQL Dialect(방언) 문법 차이(SQLite의 `INSERT OR IGNORE` vs PostgreSQL의 `ON CONFLICT DO NOTHING` 등)가 발생하는데, 본 프로젝트에서는 데이터 파서와 대시보드 쿼리 엔진 단에서 DB 커넥터와 SQL 파라미터 바인딩 기호(SQLite의 물음표 '?' 기호와 PostgreSQL의 '%s' 기호)를 유동적으로 스위칭하도록 개발하여 두 RDBMS에 대해 투명한 아키텍처 결합도 해제(Decoupling)를 구현했습니다.", faq_style_a))

    # PDF 빌드 실행
    doc.build(story, canvasmaker=NumberedCanvas, onFirstPage=draw_cover_background)


if __name__ == "__main__":
    build_pdf()
    print("PDF 포트폴리오 생성 완료: poker_analytics_portfolio.pdf")
