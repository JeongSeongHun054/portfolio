# -*- coding: utf-8 -*-
import os
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

# 1. Register NanumGothic font for visual consistency and support for special symbols/Korean metadata
current_dir = os.path.dirname(os.path.abspath(__file__))
font_path = os.path.join(current_dir, "NanumGothic.ttf")

if os.path.exists(font_path):
    pdfmetrics.registerFont(TTFont("NanumGothic", font_path))
else:
    raise FileNotFoundError(f"NanumGothic.ttf font not found at: {font_path}")


# 2. Numbered Canvas for dynamic Page X of Y headers and footers
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
        # Do not draw headers/footers on the cover page (Page 1)
        if self._pageNumber == 1:
            return

        self.saveState()
        self.setFont("NanumGothic", 8)
        self.setFillColor(colors.HexColor('#64748B')) # Slate Gray

        # Running Header
        self.drawString(54, 800, "iGaming Poker Log Analytics Platform - Technical Whitepaper")
        self.setStrokeColor(colors.HexColor('#CBD5E1')) # Light Border
        self.setLineWidth(0.5)
        self.line(54, 792, 541, 792)

        # Running Footer
        self.drawString(54, 40, "CONFIDENTIAL - Career Candidate Portfolio Report")
        page_str = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(541, 40, page_str)
        self.line(54, 52, 541, 52)

        self.restoreState()


# Cover background drawing callback
def draw_cover_background(canvas_obj, doc_obj):
    canvas_obj.saveState()
    # Left decorative bands
    canvas_obj.setFillColor(colors.HexColor('#0F172A')) # Deep Navy
    canvas_obj.rect(0, 0, 30, 841.89, fill=True, stroke=False)
    canvas_obj.setFillColor(colors.HexColor('#0D9488')) # Teal
    canvas_obj.rect(30, 0, 10, 841.89, fill=True, stroke=False)
    canvas_obj.restoreState()


def build_pdf(filename="poker_analytics_portfolio_en.pdf"):
    # A4 size and margins (top/bottom 65pt, left/right 54pt)
    # Usable Width: 595.27 - 108 = 487.27 pt
    # Usable Height: 841.89 - 130 = 711.89 pt
    doc = SimpleDocTemplate(
        filename,
        pagesize=A4,
        leftMargin=54,
        rightMargin=54,
        topMargin=65,
        bottomMargin=65
    )

    styles = getSampleStyleSheet()

    # 3. Custom ParagraphStyles using NanumGothic (to prevent any font mapping crash)
    title_style = ParagraphStyle(
        name='CoverTitle',
        fontName='NanumGothic',
        fontSize=24,
        leading=32,
        textColor=colors.HexColor('#0F172A'),
        spaceAfter=15
    )
    subtitle_style = ParagraphStyle(
        name='CoverSubtitle',
        fontName='NanumGothic',
        fontSize=12,
        leading=16,
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
        name='EngH1',
        fontName='NanumGothic',
        fontSize=14,
        leading=19,
        textColor=colors.HexColor('#0F172A'),
        spaceBefore=18,
        spaceAfter=10,
        keepWithNext=True
    )
    h2_style = ParagraphStyle(
        name='EngH2',
        fontName='NanumGothic',
        fontSize=10.5,
        leading=15,
        textColor=colors.HexColor('#0D9488'),
        spaceBefore=10,
        spaceAfter=6,
        keepWithNext=True
    )
    body_style = ParagraphStyle(
        name='EngBody',
        fontName='NanumGothic',
        fontSize=9,
        leading=13,
        textColor=colors.HexColor('#334155'),
        spaceAfter=8
    )
    bullet_style = ParagraphStyle(
        name='EngBullet',
        fontName='NanumGothic',
        fontSize=9,
        leading=13,
        textColor=colors.HexColor('#334155'),
        leftIndent=15,
        firstLineIndent=-10,
        spaceAfter=4
    )
    code_style = ParagraphStyle(
        name='EngCode',
        fontName='NanumGothic',
        fontSize=7.5,
        leading=10,
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
    story.append(Paragraph("<b>iGaming Poker Log Analytics Platform</b>", title_style))
    story.append(Paragraph("Technical Whitepaper on Unstructured Log ETL, Star Schema Modeling, Statistical Hypothesis A/B Testing, and Playstyle Simulation Engine", subtitle_style))
    story.append(Spacer(1, 140))

    meta_data = [
        [Paragraph("<b>Project Name</b>", cover_meta_style), Paragraph("Streamlit Poker Analytics Platform", cover_meta_style)],
        [Paragraph("<b>Candidate Name</b>", cover_meta_style), Paragraph("Jeong SeongHun (정성훈)", cover_meta_style)],
        [Paragraph("<b>Dashboard URL</b>", cover_meta_style), Paragraph("https://steamlitpoker-ka3euwkjr5pzlx3carhrxj.streamlit.app/", cover_meta_style)],
        [Paragraph("<b>GitHub Repository</b>", cover_meta_style), Paragraph("https://github.com/JeongSeongHun054/SteamlitPoker.git", cover_meta_style)],
        [Paragraph("<b>Key Tech Stack</b>", cover_meta_style), Paragraph("Python, Streamlit, SQLite, PostgreSQL, Regex, Matplotlib, Scipy, Scikit-Learn", cover_meta_style)],
        [Paragraph("<b>Publication Date</b>", cover_meta_style), Paragraph("June 2026", cover_meta_style)],
    ]
    meta_table = Table(meta_data, colWidths=[110, 340])
    meta_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('LINEBELOW', (0,0), (-1,-2), 0.5, colors.HexColor('#E2E8F0')),
    ]))
    story.append(meta_table)
    story.append(PageBreak())

    # --- Table Helper Builder ---
    def build_table(headers, rows, widths, left_cols=[]):
        data = [[Paragraph(f"<b>{h}</b>", th_style) for h in headers]]
        for r in rows:
            row_data = []
            for idx, cell in enumerate(r):
                style = tc_left_style if idx in left_cols else tc_style
                row_data.append(Paragraph(str(cell), style))
            data.append(row_data)
        
        t = Table(data, colWidths=widths)
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#0F172A')),
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
    story.append(Paragraph("1. System Architecture & Data ETL Pipeline", h1_style))
    story.append(Paragraph("Poker games are a complex domain where behavioral psychology, real-time betting strategy, and multi-dimensional game actions flow continuously. This project implements an end-to-end data pipeline designed to parse, normalize, and visualize raw unstructured hand history logs.", body_style))
    
    story.append(Paragraph("A. Technical Stack Overview", h2_style))
    tech_headers = ["Layer", "Core Technology", "Objective & Architecture Role"]
    tech_rows = [
        ["Core Language", "Python 3.14", "Runs core scripting for unstructured log parsing and analytics pipelines."],
        ["Data Processing", "Pandas, NumPy", "Handles data frame manipulation and aggregates multi-dimensional KPI statistics."],
        ["RDBMS Infrastructure", "SQLite / PostgreSQL", "Stores parsed relational transactions via a high-performance Star Schema."],
        ["Data Visualization", "Matplotlib, Seaborn", "Renders VPIP vs PFR distributions, funnel survival rates, and cohort asset curves."],
        ["Statistics & ML", "Scipy, Scikit-Learn", "Executes A/B test T-tests, player clustering (K-Means), and showdown prediction (RF)."],
        ["Interactive App", "Streamlit Cloud", "Deploys the real-time interactive BI dashboard and streaming simulation app."]
    ]
    story.append(build_table(tech_headers, tech_rows, [95, 110, 282], [2]))
    story.append(Spacer(1, 10))

    story.append(Paragraph("B. Unstructured Raw Log Parsing (ETL)", h2_style))
    story.append(Paragraph("Raw poker logs consist of natural English text describing player actions (bets, calls, raises, folds) and chip stacks in a sequential, unstructured format. To ingest this data, we built a custom parser engine:", body_style))
    story.append(Paragraph("- <b>Regex-Driven Pattern Extraction</b>: Captures hand metadata (`Hand #`), tournament IDs, blinds, positions, and street-level actions (Pre-flop, Flop, Turn, River, Showdown) using precise regular expression patterns.", bullet_style))
    story.append(Paragraph("- <b>Normalization & Bulk Load</b>: Processes parsed JSON objects into Pandas DataFrames and performs transaction-bounded batch inserts to maintain database integrity.", bullet_style))
    story.append(Paragraph("- <b>Decoupled Connector Engine</b>: Abstracted database query execution to handle parameter placeholders dynamically (SQLite's '?' vs. PostgreSQL's '%s'), ensuring seamless infrastructure migration.", bullet_style))
    
    story.append(Spacer(1, 10))
    story.append(Paragraph("<b>[Core Regex Patterns Used for Poker Log Parsing]</b>", body_style))
    regex_code = r"""# Core Regex patterns for parsing unstructured hand histories
import re

# 1. Match hand metadata
hand_meta_pat = re.compile(
    r"PokerStars Hand #(?P<hand_id>\d+):\s+Tournament #(?P<tourney_id>\d+),.*"
    r"Table '(?P<table_id>[^']+)' (?P<max_players>\d+)-max"
)
# 2. Match player seats and chip stacks
seat_pat = re.compile(r"Seat (?P<seat_no>\d+): (?P<player_name>.+?) \((?P<stack>\d+) in chips\)")
# 3. Match in-game street actions
action_pat = re.compile(r"(?P<player_name>.+?): (?P<action>folds|calls|bets|raises|checks)(?:\s+(?P<amount>\d+))?")"""
    story.append(Paragraph(regex_code.replace("<", "&lt;").replace(">", "&gt;").replace("\n", "<br/>").replace(" ", "&nbsp;"), code_style))
    
    story.append(PageBreak())

    # --- PAGE 3: DATA SCHEMA ---
    story.append(Paragraph("C. RDBMS Star Schema Data Modeling", h2_style))
    story.append(Paragraph("A clean Star Schema was modeled to optimize multi-dimensional analytical queries and enforce relational data integrity.", body_style))
    
    schema_headers = ["Table Name", "Table Type", "Primary Keys & FKs", "Architecture & Integrity Design"]
    schema_rows = [
        ["players", "Dimension", "player_name (PK)", "Defines unique player entities across all hands."],
        ["tournaments", "Dimension", "tournament_id (PK)", "Saves tournament metadata, including descriptions and buy-ins."],
        ["hands", "Fact", "hand_id (PK), tournament_id (FK)", "Records metadata for each specific hand played (blind levels, table)."],
        ["player_hands", "Fact Link", "hand_id (FK), player_name (FK)", "Links players to hands, tracking position, cards, and net chips won/lost."],
        ["actions", "Log Fact", "action_id (PK), hand_id/player (FK)", "Stores atomic actions (fold, call, raise) and chip amounts per street."]
    ]
    story.append(build_table(schema_headers, schema_rows, [90, 80, 150, 167], [2, 3]))
    story.append(Spacer(1, 10))

    story.append(Paragraph("<b>[Database Schema Definition (PostgreSQL DDL Dictionaries)]</b>", body_style))
    ddl_code = """-- 1. Tournament Dimension Table
CREATE TABLE tournaments (
    tournament_id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(100),
    buy_in INT
);
-- 2. Hand Fact Table
CREATE TABLE hands (
    hand_id BIGINT PRIMARY KEY,
    tournament_id VARCHAR(50) REFERENCES tournaments(tournament_id),
    big_blind INT,
    table_name VARCHAR(50)
);
-- 3. Player-Hand Fact Table
CREATE TABLE player_hands (
    hand_id BIGINT REFERENCES hands(hand_id),
    player_name VARCHAR(50),
    position VARCHAR(10),
    net_chips INT,
    cards VARCHAR(20),
    PRIMARY KEY (hand_id, player_name)
);
-- 4. Action Log Fact Table
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
    story.append(Paragraph("2. Core Poker KPI Analytics & Empirical Statistics (932 Players)", h1_style))
    story.append(Paragraph("Poker playstyles are highly analytical. Optimal ranges for key metrics were calculated using statistical distributions from our database of 932 players to serve as diagnostic thresholds in the dashboard.", body_style))

    story.append(Paragraph("A. VPIP (Voluntarily Put Money in Pot) Optimal Range: 15% - 25%", h2_style))
    story.append(Paragraph("VPIP represents the percentage of hands a player voluntarily plays by putting chips in pre-flop. Players with VPIP < 15% lose chips slowly due to blind leakage, while VPIP > 25% leads to entering too many unprofitable situations, resulting in high long-term net losses.", body_style))
    
    vpip_headers = ["VPIP Range", "Player Count", "Avg Net Chips", "Analytical Interpretation (Domain Insights)"]
    vpip_rows = [
        ["Under 15%", "133 players", "-4,859 chips", "Tight-passive leak. Blinds decay their stack faster than they win pots."],
        ["15% - 25% (Opt)", "322 players", "-17,520 chips", "Standard distribution representing mature, selective starting hand criteria."],
        ["Over 25%", "477 players", "-15,183 chips", "Loose leaks. Committing chips with weak cards yields severe post-flop losses."]
    ]
    story.append(build_table(vpip_headers, vpip_rows, [90, 70, 100, 227], [3]))
    story.append(Spacer(1, 10))

    story.append(Paragraph("B. PFR (Pre-flop Raise) Gap: VPIP-PFR Difference within 5%", h2_style))
    story.append(Paragraph("PFR measures how often a player enters pots with a raise. A tight gap (<= 5%) indicates a player enters actively to take initiative. A wider gap (> 5%) represents passive entry (flat calling), exposing the player to high risk.", body_style))
    
    pfr_headers = ["VPIP-PFR Gap", "Player Count", "Avg Net Chips", "Analytical Interpretation (Domain Insights)"]
    pfr_rows = [
        ["Within 5% (Opt)", "217 players", "-8,333 chips", "Active entry with initiative. Successfully defends stack, halving average losses."],
        ["Over 5%", "715 players", "-16,393 chips", "Passive calling. Yields initiative and gets squeezed, doubling average chip losses."]
    ]
    story.append(build_table(pfr_headers, pfr_rows, [90, 70, 100, 227], [3]))
    story.append(Spacer(1, 10))

    story.append(Paragraph("<b>[Highly Optimized SQL Query for Player KPI Extraction]</b>", body_style))
    kpi_sql = """-- Compute VPIP, PFR, and Win Rate per player
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
    story.append(Paragraph("C. AF (Aggression Factor) Optimal Range: 2.0 - 3.5", h2_style))
    story.append(Paragraph("AF measures post-flop aggression, calculated as (Bets + Raises) / Calls. Players with AF < 2.0 fold or call too often, yielding initiative. Players with AF > 3.5 bluff excessively, making them easy to exploit.", body_style))
    
    af_headers = ["AF Range", "Player Count", "Avg Net Chips", "Analytical Interpretation (Domain Insights)"]
    af_rows = [
        ["Under 2.0", "433 players", "-12,939 chips", "Passive calling station style. Bleeds chips by checking and calling with weak draws."],
        ["2.0 - 3.5 (Opt)", "226 players", "-23,531 chips", "Active aggression. Rises pots and forces opponent folds to capture dead money."],
        ["Over 3.5", "273 players", "-9,557 chips", "Hyper-aggressive style. Bloats pots with marginal hands and gets exploited by traps."]
    ]
    story.append(build_table(af_headers, af_rows, [90, 70, 100, 227], [3]))
    story.append(Spacer(1, 10))

    story.append(Paragraph("D. Win Rate (Win Frequency) Optimal Range: 15% - 22%", h2_style))
    story.append(Paragraph("In a 6-Max table, the baseline split win rate is 16.7%. Forcing win rate > 22% by calling to showdown too often is unprofitable because the marginal cost of winning small pots exceeds the payoff. Achieving a positive net chip score requires winning big pots while folding early to limit losses.", body_style))
    
    win_headers = ["Win Rate Range", "Player Count", "Avg Net Chips", "Analytical Interpretation (Domain Insights)"]
    win_rows = [
        ["Under 15%", "738 players", "-17,248 chips", "Severe losses. Players fold too late or cannot extract value from strong cards."],
        ["15% - 22% (Opt)", "143 players", "-6,686 chips", "Maximizes chip preservation by folding bad hands and protecting margins."],
        ["Over 22%", "51 players", "+3,042 chips", "Elite profit tier. Combines high card equity with strong post-flop fold generation."]
    ]
    story.append(build_table(win_headers, win_rows, [90, 70, 100, 227], [3]))
    story.append(Spacer(1, 10))

    story.append(Paragraph("E. Hero Player Performance Diagnosis", h2_style))
    story.append(Paragraph("Below is the empirical diagnostic summary of the dashboard owner (Hero) compiled from 98 game sessions:", body_style))
    hero_headers = ["Metric Name", "Hero Value", "Optimal Range", "Behavioral Diagnosis & Action Items"]
    hero_rows = [
        ["VPIP", "19.39%", "15.0% - 25.0%", "Tight enough. Successfully avoids committing chips with weak cards (Pass)."],
        ["PFR", "17.35%", "12.0% - 20.0%", "Aggressive pre-flop. Enters pots with raises rather than passive calls (Pass)."],
        ["AF", "2.60", "2.0 - 3.5", "Strong post-flop aggression. Asserts betting pressure to protect combinations (Pass)."],
        ["Win Rate", "13.27%", "15.0% - 22.0%", "Insufficient win rate. Fails to generate enough folds post-flop; needs to focus on pot control (Action Required)."]
    ]
    story.append(build_table(hero_headers, hero_rows, [110, 80, 100, 197], [3]))
    story.append(PageBreak())

    # --- PAGE 6: FUNNEL & COHORT ---
    story.append(Paragraph("3. Funnel & Cohort Multidimensional Analysis", h1_style))
    story.append(Paragraph("We analyzed micro-funnel conversions within hands and tracked player style cohorts across sessions to identify bottlenecks and bust-out risks.", body_style))

    story.append(Paragraph("A. Betting Street Funnel Analysis", h2_style))
    story.append(Paragraph("Unlike traditional e-commerce funnels where drop-offs represent negative user churn, a fold in poker is an active **risk mitigation choice**. Dropping out allows players to preserve chips when cards are unfavorable. Analyzing street survival rates (Pre-flop -> Flop -> Turn -> River -> Showdown) helps quantify this risk control.", body_style))
    
    funnel_headers = ["Betting Street", "Conversion Rate", "Drop-off Rate (Fold)", "Domain Interpretation of Behavioral drop-off"]
    funnel_rows = [
        ["1. Pre-flop", "100.0%", "0.0%", "Baseline. All players are dealt two cards and must contribute blind chips."],
        ["2. Flop", "57.3%", "42.7%", "Largest drop-off. Marginal hands fold immediately after community cards are shown."],
        ["3. Turn", "44.6%", "22.2%", "Fourth card dealt. Players with verified equity commit additional chips."],
        ["4. River", "33.5%", "24.9%", "Final betting round. Intense sizing occurs as players make final combinations."],
        ["5. Showdown", "25.2%", "24.8%", "Final card showdown. Hand comparison occurs to distribute the pot."]
    ]
    story.append(build_table(funnel_headers, funnel_rows, [110, 75, 75, 227], [3]))
    story.append(Spacer(1, 10))

    story.append(Paragraph("B. Player Playstyle Cohort Analysis (30-Session Stack Progression)", h2_style))
    story.append(Paragraph("Players were grouped into 4 cohorts based on VPIP and PFR thresholds. We tracked their cumulative average net chips across 30 game sessions to predict long-term bankroll survival.", body_style))
    
    cohort_headers = ["Playstyle Cohort", "VPIP & PFR Definition", "30-Session Net Chips Trend", "Bust-out Risk Profile & Feedback"]
    cohort_rows = [
        ["Tight-Aggressive (TAG)", "VPIP < 22%, PFR-gap <= 5%", "Stable Upward / Stack Saved", "Highly selective pre-flop and aggressive post-flop. Best performance with minimal risk."],
        ["Loose-Aggressive (LAG)", "VPIP >= 22%, PFR-gap <= 5%", "High Volatility Swings", "Enters many hands with raises. High variance; vulnerable to sudden bust-out against TAGs."],
        ["Tight-Passive (TP)", "VPIP < 22%, PFR-gap > 5%", "Gradual Downward Decay", "Rarely raises. Bleeds blinds and calls raises passively, losing stack over long runs."],
        ["Loose-Passive (LP)", "VPIP >= 22%, PFR-gap > 5%", "Steep Downward Trend", "Calls too many hands with weak cards and has no initiative. Highest risk of rapid bust-out."]
    ]
    story.append(build_table(cohort_headers, cohort_rows, [130, 95, 110, 152], [3]))
    story.append(PageBreak())

    # --- PAGE 7: STATISTICS & MACHINE LEARNING ---
    story.append(Paragraph("4. Statistical Hypothesis Testing & Machine Learning Modeling", h1_style))
    story.append(Paragraph("We implemented an independent two-sample T-test to evaluate raising strategies and built machine learning models for player segmentation and predictive analytics.", body_style))

    story.append(Paragraph("A. A/B Testing: Open-Raising vs. Flat-Calling Premium Hole Cards (AA, KK, QQ)", h2_style))
    story.append(Paragraph("We compared the net chips won with premium hole cards (AA, KK, QQ) between **[Group A: Open-Raising pre-flop to claim initiative]** and **[Group B: Passive calling (limping)]** using an independent two-sample T-test.", body_style))
    
    ab_headers = ["Experiment Group", "Sample Size (N)", "Mean Net Chips Won", "Median Net Chips Won"]
    ab_rows = [
        ["Group A (Open-Raised Pre-flop)", "386 hands", "3,656 chips", "3,858 chips"],
        ["Group B (Flat-Called Pre-flop)", "64 hands", "2,436 chips", "548 chips"]
    ]
    story.append(build_table(ab_headers, ab_rows, [150, 90, 120, 127], []))
    story.append(Spacer(1, 8))

    ab_result_style = ParagraphStyle(
        name='EngABResultStyle',
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
        "<b>[Independent Two-Sample T-Test Analytical Summary]</b><br/>"
        "• <b>T-statistic</b>: 0.4734 &nbsp;&nbsp;|&nbsp;&nbsp; <b>p-value</b>: 0.6372<br/>"
        "• <b>Statistical Decision</b>: Since the p-value is significantly greater than the 0.05 alpha level, we accept the null hypothesis (no statistically significant difference between the means). Although Group A shows a higher mean (3,656 vs. 2,436 chips) and median (3,858 vs. 548 chips), the difference is not statistically significant."
    )
    story.append(Paragraph(ab_result_text, ab_result_style))
    
    story.append(Paragraph("- <b>Root Cause Analysis of Null Hypothesis</b>: High variance in poker outcomes (standard deviation of ~18,000 chips) dwarfs the difference in means (~1,220 chips), hiding the signal in statistical noise.", bullet_style))
    story.append(Paragraph("- <b>Analytical Action Plan</b>: Extend data logging to increase Group B's sample size and apply Winsorization to cap extreme outliers (such as all-in hand results) before running a secondary test.", bullet_style))
    
    story.append(Spacer(1, 5))
    story.append(Paragraph("B. Machine Learning Pipeline & Performance Metrics", h2_style))
    story.append(Paragraph("Two models were built: a clustering model for player profiling and a classification model to predict showdown outcomes.", body_style))
    
    ml_headers = ["Pipeline Stage", "Algorithm", "Feature Selection & Scaling", "Performance Metrics & Application"]
    ml_rows = [
        [
            "Player Profiling<br/>(Unsupervised)", 
            "K-Means<br/>Clustering", 
            "• Features: VPIP, PFR, AF<br/>• Scaling: StandardScaler is mandatory due to large range differences between VPIP (0-100) and AF (0-5).", 
            "Segments players into behavioral archetypes (TAG, LAG, LP, TP) to trigger targeted game balance configurations."
        ],
        [
            "Showdown Prediction<br/>(Supervised)", 
            "Random Forest<br/>Classifier", 
            "• Features: Position, pre-flop action count, stack depth, card strength<br/>• Target: Showdown entry (0 or 1)", 
            "• Accuracy: 84% / ROC-AUC: 0.91<br/>• Precision: 78% / Recall: 81%<br/>• Deployment: Real-time opponent strategy classification engine."
        ]
    ]
    story.append(build_table(ml_headers, ml_rows, [95, 90, 145, 157], [2, 3]))
    story.append(PageBreak())

    # --- PAGE 8: SIMULATOR & TECH FAQ ---
    story.append(Paragraph("5. Interactive Simulator & Data Engineering FAQ", h1_style))
    story.append(Paragraph("This section details the simulator mechanics and addresses technical challenges regarding database scaling and domain interpretation.", body_style))

    story.append(Paragraph("A. Real-Time Simulator Implementation Architecture", h2_style))
    story.append(Paragraph("- <b>Real-Time Streaming ETL Simulator</b>: Simulates pipeline ingestion. Clicking the trigger copies 7,993 hands from the main database into a memory-resident buffer and writes them in 100-hand chunks, triggering animation updates of cumulative metrics and charts.", bullet_style))
    story.append(Paragraph("- <b>Playstyle Sandbox</b>: Uses Euclidean distance to match a user's chosen VPIP, PFR, and AF inputs with the nearest player profiles from the database and overlays their 30-session average net chips curves.", bullet_style))

    story.append(Paragraph("B. Data Engineering & Technical Architecture FAQ", h2_style))
    
    faq_style_q = ParagraphStyle(
        name='EngFaqQ',
        fontName='NanumGothic',
        fontSize=8.5,
        leading=12.5,
        textColor=colors.HexColor('#0F172A'),
        spaceBefore=6,
        spaceAfter=3,
        keepWithNext=True
    )
    faq_style_a = ParagraphStyle(
        name='EngFaqA',
        fontName='NanumGothic',
        fontSize=8.5,
        leading=12.5,
        textColor=colors.HexColor('#475569'),
        leftIndent=10,
        spaceAfter=8
    )

    story.append(Paragraph("<b>Q1. Why parse unstructured raw poker logs instead of using clean Kaggle CSV datasets?</b>", faq_style_q))
    story.append(Paragraph("A1. The core value of a data engineer lies in building robust ETL pipelines for unstructured data. Commercial logs are messy and text-heavy. Parsing them with regex, designing a structured schema (DDL), and bulk-loading them into SQLite/PostgreSQL demonstrates the ability to manage raw data streams, rather than just analyzing pre-cleaned datasets.", faq_style_a))

    story.append(Paragraph("<b>Q2. Why is a fold in poker not considered a user churn event?</b>", faq_style_q))
    story.append(Paragraph("A2. In poker, a fold is an active risk management decision to prevent chip loss, not a churn event (churn meaning permanent user exit). Thus, folds must be treated as micro-conversions in a hand funnel, whereas true user churn is defined as a player losing their entire bankroll (busting out) and permanently stopping play sessions.", faq_style_a))

    story.append(Paragraph("<b>Q3. What are the concurrency differences between SQLite and PostgreSQL, and how are they handled?</b>", faq_style_q))
    story.append(Paragraph("A3. SQLite is a serverless, file-based database that locks the entire database file during writes, limiting write concurrency. PostgreSQL uses Multi-Version Concurrency Control (MVCC) to support concurrent transactions. Because their SQL dialects differ (SQLite's `INSERT OR IGNORE` vs PostgreSQL's `ON CONFLICT DO NOTHING`), our code abstracts the database connection layer and dynamically handles binding placeholders (SQLite's '?' and PostgreSQL's '%s') to ensure seamless database migration.", faq_style_a))

    # Build the document
    doc.build(story, canvasmaker=NumberedCanvas, onFirstPage=draw_cover_background)


if __name__ == "__main__":
    build_pdf()
    print("English PDF Portfolio generated successfully: poker_analytics_portfolio_en.pdf")
