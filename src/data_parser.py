import os
import re
import sqlite3
import glob
from datetime import datetime

# =========================================================================
# PostgreSQL 데이터베이스 드라이버 예외 임포트 처리
# =========================================================================
# * 설계 목적: 
#   - psycopg2 라이브러리가 로컬에 설치되어 있지 않더라도 스크립트 실행이 중단되지 않고
#     안전하게 SQLite 모드로 Fallback 실행되도록 환경적 격리를 구현합니다.
#   - 이는 다양한 실행 환경 및 시스템 설정에 유연하게 대응하기 위한 방어적 프로그래밍의 기본입니다.
try:
    import psycopg2
    from psycopg2 import extras
    POSTGRES_AVAILABLE = True
except ImportError:
    POSTGRES_AVAILABLE = False

# =========================================================================
# 데이터베이스 연동 설정 환경 변수 (Dual DB 모드)
# =========================================================================
# * DB_TYPE: "sqlite" 또는 "postgres" 중 적재할 타겟 데이터베이스를 지정합니다.
DB_TYPE = "sqlite" 

# SQLite 설정
SQLITE_DB_PATH = "../poker_data.db"
SQLITE_SCHEMA_PATH = "schema.sql"

# PostgreSQL 설정 (사용자 로컬/서버 정보에 맞게 세팅 가능하도록 정의)
# * 실무 팁: 보통 로컬이나 개발 환경에서는 config 또는 .env 파일을 로딩하여 사용합니다.
PG_CONN_INFO = {
    "host": "localhost",
    "port": 5432,
    "user": "postgres",
    "password": "postgres",
    "database": "poker_db"
}
PG_SCHEMA_PATH = "schema_pg.sql"

# =========================================================================
# 비정형 텍스트 로그 매칭용 정규표현식(Regex) 패턴 정의
# =========================================================================
RAW_DATA_DIR = "../raw_hh"

HEADER_PATTERN = re.compile(
    r"Poker Hand #(?P<hand_id>\S+): Tournament #(?P<tournament_id>\d+), (?P<tournament_name>.*?) - Level(?P<level>\d+)\((?P<sb>\d+)/(?P<bb>\d+)\) - (?P<timestamp>\d{4}/\d{2}/\d{2} \d{2}:\d{2}:\d{2})"
)
BUTTON_PATTERN = re.compile(
    r"Table '\d+' \d+-max Seat #(?P<button_seat>\d+) is the button"
)
SEAT_PATTERN = re.compile(
    r"Seat (?P<seat_num>\d+): (?P<player_name>.*?) \((?P<chips>[\d,]+) in chips\)"
)
POST_PATTERN = re.compile(
    r"^(?P<player_name>.*?): posts (?P<post_type>small blind|big blind|the ante) (?P<amount>\d+)$"
)
DEALT_PATTERN = re.compile(
    r"^Dealt to (?P<player_name>.*?) \[(?P<cards>.*?)\]$"
)
ACTION_PATTERN = re.compile(
    r"^(?P<player_name>.*?): (?P<action>folds|checks|calls|bets|raises)(?:\s+(?P<amount_info>.*?))?$"
)
SHOWS_PATTERN = re.compile(
    r"^(?P<player_name>.*?): shows \[(?P<cards>.*?)\]"
)
COLLECTED_PATTERN = re.compile(
    r"^(?P<player_name>.*?) collected (?P<amount>[\d,]+) from pot"
)
SUMMARY_POT_PATTERN = re.compile(
    r"Total pot (?P<total_pot>[\d,]+) \| Rake (?P<rake>[\d,]+)"
)
BOARD_PATTERN = re.compile(
    r"Board \[(?P<board>.*?)\]"
)


def calculate_positions(button_seat, seated_players):
    """
    포지션(Position)을 버튼(BTN) 시트 기반으로 동적 순환 계산합니다.
    """
    sorted_players = sorted(seated_players, key=lambda x: x['seat_num'])
    n_players = len(sorted_players)
    if n_players == 0:
        return {}

    btn_idx = 0
    for i, p in enumerate(sorted_players):
        if p['seat_num'] == button_seat:
            btn_idx = i
            break
        elif p['seat_num'] > button_seat:
            btn_idx = i
            break
    else:
        btn_idx = 0

    positions = {}
    if n_players == 2:
        btn_player = sorted_players[btn_idx]['player_name']
        bb_player = sorted_players[(btn_idx + 1) % 2]['player_name']
        positions[btn_player] = 'BTN/SB'
        positions[bb_player] = 'BB'
    else:
        for step in range(n_players):
            idx = (btn_idx + step) % n_players
            p_name = sorted_players[idx]['player_name']
            
            if step == 0:
                positions[p_name] = 'BTN'
            elif step == 1:
                positions[p_name] = 'SB'
            elif step == 2:
                positions[p_name] = 'BB'
            elif step == n_players - 1:
                positions[p_name] = 'CO'
            elif step == 3:
                positions[p_name] = 'UTG'
            else:
                positions[p_name] = f'MP{step-3}' if n_players > 6 else 'MP'
                
    return positions


def parse_hand_history(hand_text):
    """
    한 개의 핸드 텍스트 블록을 파싱하여 정형화된 데이터 딕셔너리로 반환합니다.
    """
    lines = [line.strip() for line in hand_text.strip().split('\n') if line.strip()]
    if not lines:
        return None

    hand_data = {
        'hand': {},
        'tournament': {},
        'players': set(),
        'hand_players': [],
        'actions': []
    }

    header_match = HEADER_PATTERN.match(lines[0])
    if not header_match:
        return None
    
    h_info = header_match.groupdict()
    hand_id = h_info['hand_id']
    dt_str = h_info['timestamp'].replace('/', '-')
    
    hand_data['hand'] = {
        'hand_id': hand_id,
        'tournament_id': h_info['tournament_id'],
        'level': h_info['level'],
        'small_blind': int(h_info['sb']),
        'big_blind': int(h_info['bb']),
        'timestamp': dt_str,
        'total_pot': 0,
        'rake': 0,
        'board': None,
        'button_seat': 0
    }
    
    hand_data['tournament'] = {
        'tournament_id': h_info['tournament_id'],
        'name': h_info['tournament_name']
    }

    street = 'preflop'
    button_seat = 0
    seated_players = []
    player_chips_start = {}
    player_hole_cards = {}
    player_put_in_pot = {}
    player_collected = {}

    for line in lines[1:]:
        btn_match = BUTTON_PATTERN.match(line)
        if btn_match:
            button_seat = int(btn_match.group('button_seat'))
            hand_data['hand']['button_seat'] = button_seat
            continue

        seat_match = SEAT_PATTERN.match(line)
        if seat_match:
            s_num = int(seat_match.group('seat_num'))
            p_name = seat_match.group('player_name')
            chips = int(seat_match.group('chips').replace(',', ''))
            
            seated_players.append({'seat_num': s_num, 'player_name': p_name})
            player_chips_start[p_name] = chips
            player_put_in_pot[p_name] = 0
            player_collected[p_name] = 0
            hand_data['players'].add(p_name)
            continue

        if '*** HOLE CARDS ***' in line:
            street = 'preflop'
            continue
        elif '*** FLOP ***' in line:
            street = 'flop'
            cards_match = re.search(r'\[(.*?)\]', line)
            if cards_match:
                hand_data['hand']['board'] = cards_match.group(1)
            continue
        elif '*** TURN ***' in line:
            street = 'turn'
            cards_match = re.findall(r'\[(.*?)\]', line)
            if len(cards_match) >= 2:
                hand_data['hand']['board'] = cards_match[0] + " " + cards_match[1]
            continue
        elif '*** RIVER ***' in line:
            street = 'river'
            cards_match = re.findall(r'\[(.*?)\]', line)
            if len(cards_match) >= 2:
                hand_data['hand']['board'] = cards_match[0] + " " + cards_match[1]
            continue
        elif '*** SHOWDOWN ***' in line:
            street = 'showdown'
            continue
        elif '*** SUMMARY ***' in line:
            street = 'summary'
            continue

        if street != 'summary':
            dealt_match = DEALT_PATTERN.match(line)
            if dealt_match:
                p_name = dealt_match.group('player_name')
                cards = dealt_match.group('cards')
                player_hole_cards[p_name] = cards
                continue

            post_match = POST_PATTERN.match(line)
            if post_match:
                p_name = post_match.group('player_name')
                p_type = post_match.group('post_type')
                amount = int(post_match.group('amount'))
                
                act_type = 'posts_ante'
                if p_type == 'small blind':
                    act_type = 'posts_sb'
                elif p_type == 'big blind':
                    act_type = 'posts_bb'
                
                hand_data['actions'].append({
                    'hand_id': hand_id,
                    'street': street,
                    'player_name': p_name,
                    'action_type': act_type,
                    'amount': amount,
                    'is_all_in': 0
                })
                player_put_in_pot[p_name] = player_put_in_pot.get(p_name, 0) + amount
                continue

            act_match = ACTION_PATTERN.match(line)
            if act_match:
                p_name = act_match.group('player_name')
                act = act_match.group('action')
                amt_info = act_match.group('amount_info')
                
                amount = None
                is_all_in = 1 if amt_info and 'all-in' in amt_info else 0
                
                if amt_info:
                    if act == 'raises':
                        raise_to_match = re.search(r'to\s+([\d,]+)', amt_info)
                        if raise_to_match:
                            amount = int(raise_to_match.group(1).replace(',', ''))
                    else:
                        num_match = re.search(r'([\d,]+)', amt_info)
                        if num_match:
                            amount = int(num_match.group(1).replace(',', ''))
                
                hand_data['actions'].append({
                    'hand_id': hand_id,
                    'street': street,
                    'player_name': p_name,
                    'action_type': act,
                    'amount': amount,
                    'is_all_in': is_all_in
                })
                
                if amount is not None:
                    player_put_in_pot[p_name] = player_put_in_pot.get(p_name, 0) + amount
                continue

            show_match = SHOWS_PATTERN.match(line)
            if show_match:
                p_name = show_match.group('player_name')
                cards = show_match.group('cards')
                player_hole_cards[p_name] = cards
                hand_data['actions'].append({
                    'hand_id': hand_id,
                    'street': street,
                    'player_name': p_name,
                    'action_type': 'shows',
                    'amount': None,
                    'is_all_in': 0
                })
                continue

            coll_match = COLLECTED_PATTERN.match(line)
            if coll_match:
                p_name = coll_match.group('player_name')
                amount = int(coll_match.group('amount').replace(',', ''))
                player_collected[p_name] = player_collected.get(p_name, 0) + amount
                hand_data['actions'].append({
                    'hand_id': hand_id,
                    'street': street,
                    'player_name': p_name,
                    'action_type': 'collected',
                    'amount': amount,
                    'is_all_in': 0
                })
                continue

        else:
            sum_pot_match = SUMMARY_POT_PATTERN.match(line)
            if sum_pot_match:
                t_pot = int(sum_pot_match.group('total_pot').replace(',', ''))
                rake = int(sum_pot_match.group('rake').replace(',', ''))
                hand_data['hand']['total_pot'] = t_pot
                hand_data['hand']['rake'] = rake
                continue
            
            board_match = BOARD_PATTERN.match(line)
            if board_match:
                hand_data['hand']['board'] = board_match.group('board')
                continue

            if line.startswith('Seat '):
                won_match = re.search(r'Seat \d+: (?P<p_name>.*?) showed \[(?P<cards>.*?)\] and won \((?P<won_amt>[\d,]+)\)', line)
                if won_match:
                    p_name = won_match.group('p_name')
                    p_name = re.sub(r'\s*\(.*?\)', '', p_name).strip()
                    cards = won_match.group('cards')
                    won_amt = int(won_match.group('won_amt').replace(',', ''))
                    player_hole_cards[p_name] = cards
                    player_collected[p_name] = won_amt
                
                won_coll_match = re.search(r'Seat \d+: (?P<p_name>.*?) collected \((?P<won_amt>[\d,]+)\)', line)
                if won_coll_match:
                    p_name = won_coll_match.group('p_name')
                    p_name = re.sub(r'\s*\(.*?\)', '', p_name).strip()
                    won_amt = int(won_coll_match.group('won_amt').replace(',', ''))
                    player_collected[p_name] = won_amt

                showed_lost_match = re.search(r'Seat \d+: (?P<p_name>.*?) showed \[(?P<cards>.*?)\] and lost', line)
                if showed_lost_match:
                    p_name = showed_lost_match.group('p_name')
                    p_name = re.sub(r'\s*\(.*?\)', '', p_name).strip()
                    cards = showed_lost_match.group('cards')
                    player_hole_cards[p_name] = cards

    player_positions = calculate_positions(button_seat, seated_players)
    n_players = len(seated_players)

    for p in seated_players:
        p_name = p['player_name']
        start_chips = player_chips_start.get(p_name, 0)
        hole_cards = player_hole_cards.get(p_name, None)
        pos = player_positions.get(p_name, 'MP')
        
        put_in = player_put_in_pot.get(p_name, 0)
        collected = player_collected.get(p_name, 0)
        
        if collected > 0 and put_in == 0:
            put_in = int(hand_data['hand']['total_pot'] / n_players) if n_players > 0 else 0
            
        chips_won = collected - put_in

        hand_data['hand_players'].append({
            'hand_id': hand_id,
            'player_name': p_name,
            'seat_number': p['seat_num'],
            'chips_start': start_chips,
            'hole_cards': hole_cards,
            'position': pos,
            'is_hero': 1 if p_name == 'Hero' else 0,
            'chips_won': chips_won
        })

    return hand_data


def get_connection(db_type):
    """
    지정된 DB 타입(sqlite/postgres)에 따라 커넥션 객체와 SQL 문법 플레이스홀더를 반환합니다.
    * 리턴값: (connection_object, placeholder_string, db_dialect)
    """
    if db_type == "postgres":
        if not POSTGRES_AVAILABLE:
            raise ImportError("psycopg2 라이브러리가 설치되어 있지 않아 PostgreSQL을 실행할 수 없습니다. pip install psycopg2-binary를 실행해 주세요.")
        
        # PostgreSQL 서버 연결 시도
        conn = psycopg2.connect(
            host=PG_CONN_INFO["host"],
            port=PG_CONN_INFO["port"],
            user=PG_CONN_INFO["user"],
            password=PG_CONN_INFO["password"],
            database=PG_CONN_INFO["database"]
        )
        return conn, "%s", "postgres"
    else:
        # SQLite 연결
        conn = sqlite3.connect(SQLITE_DB_PATH)
        return conn, "?", "sqlite"


def execute_schema_script(conn, schema_path):
    """
    선택된 데이터베이스에 스키마 파일(DDL)을 실행하여 테이블 구조를 초기화합니다.
    """
    if not os.path.exists(schema_path):
        print(f"경고: {schema_path} 파일을 찾을 수 없어 테이블 생성 단계를 건너뜁니다.")
        return
        
    with open(schema_path, 'r', encoding='utf-8') as f:
        schema_sql = f.read()
        
    cursor = conn.cursor()
    
    # SQLite와 PostgreSQL의 DDL 스크립트 실행 함수 분기
    if hasattr(conn, "executescript"):
        # SQLite
        cursor.executescript(schema_sql)
    else:
        # PostgreSQL (psycopg2는 executescript가 없으므로 execute로 직접 실행)
        cursor.execute(schema_sql)
        
    conn.commit()
    print(f"데이터베이스 스키마 생성 완료 ({schema_path} 적용)")


def run_etl():
    """
    Dual DB 파이프라인 메인 실행 함수입니다.
    """
    print(f"=== [ETL Start] 데이터 적재 시작 (선택된 DB 엔진: {DB_TYPE.upper()}) ===")
    
    # DB 커넥션 및 방언 획득
    try:
        conn, ph, dialect = get_connection(DB_TYPE)
        print(f"데이터베이스 연결 성공 ({DB_TYPE.upper()})")
    except Exception as e:
        print(f"❌ 데이터베이스 연결 실패: {e}")
        if DB_TYPE == "postgres":
            print("💡 SQLite 모드로 자동 전환하여 재시도합니다.")
            conn, ph, dialect = get_connection("sqlite")
            global DB_TYPE_ACTUAL
            DB_TYPE_ACTUAL = "sqlite"
        else:
            return
    
    DB_TYPE_ACTUAL = DB_TYPE
    schema_path = PG_SCHEMA_PATH if DB_TYPE_ACTUAL == "postgres" else SQLITE_SCHEMA_PATH
    execute_schema_script(conn, schema_path)
    
    cursor = conn.cursor()
    txt_files = glob.glob(os.path.join(RAW_DATA_DIR, "*.txt"))
    print(f"파싱할 텍스트 로그 파일 개수: {len(txt_files)}개")

    total_hands_parsed = 0
    total_actions_inserted = 0

    # dialect별 충돌 처리(Upsert) SQL 선언 분기
    # * 왜 이렇게 설계했는가?
    #   - SQLite: 'INSERT OR IGNORE' 또는 'INSERT OR REPLACE' 같은 특화 문법을 지원합니다.
    #   - PostgreSQL: 표준 SQL 표준에 맞춘 'ON CONFLICT (PK) DO NOTHING/UPDATE' (Upsert) 문법을 사용합니다.
    #   - 이 둘을 하나의 코드 베이스에서 안전하게 대응하도록 SQL 구문 템플릿을 분기 구성합니다.
    if DB_TYPE_ACTUAL == "postgres":
        sql_tournament = f"INSERT INTO tournaments (tournament_id, name) VALUES ({ph}, {ph}) ON CONFLICT (tournament_id) DO NOTHING"
        sql_hand = f"""
            INSERT INTO hands 
            (hand_id, tournament_id, level, small_blind, big_blind, timestamp, total_pot, rake, board, button_seat) 
            VALUES ({ph}, {ph}, {ph}, {ph}, {ph}, {ph}, {ph}, {ph}, {ph}, {ph}) 
            ON CONFLICT (hand_id) DO UPDATE SET 
            total_pot = EXCLUDED.total_pot, rake = EXCLUDED.rake, board = EXCLUDED.board, button_seat = EXCLUDED.button_seat
        """
        sql_player = f"INSERT INTO players (player_name) VALUES ({ph}) ON CONFLICT (player_name) DO NOTHING"
        sql_hand_player = f"""
            INSERT INTO hand_players 
            (hand_id, player_name, seat_number, chips_start, hole_cards, position, is_hero, chips_won) 
            VALUES ({ph}, {ph}, {ph}, {ph}, {ph}, {ph}, {ph}, {ph}) 
            ON CONFLICT (hand_id, player_name) DO UPDATE SET 
            chips_won = EXCLUDED.chips_won, hole_cards = EXCLUDED.hole_cards
        """
        sql_action = f"INSERT INTO actions (hand_id, street, player_name, action_type, amount, is_all_in) VALUES ({ph}, {ph}, {ph}, {ph}, {ph}, {ph})"
    else:
        # SQLite
        sql_tournament = f"INSERT OR IGNORE INTO tournaments (tournament_id, name) VALUES ({ph}, {ph})"
        sql_hand = f"""
            INSERT OR REPLACE INTO hands 
            (hand_id, tournament_id, level, small_blind, big_blind, timestamp, total_pot, rake, board, button_seat) 
            VALUES ({ph}, {ph}, {ph}, {ph}, {ph}, {ph}, {ph}, {ph}, {ph}, {ph})
        """
        sql_player = f"INSERT OR IGNORE INTO players (player_name) VALUES ({ph})"
        sql_hand_player = f"""
            INSERT OR REPLACE INTO hand_players 
            (hand_id, player_name, seat_number, chips_start, hole_cards, position, is_hero, chips_won) 
            VALUES ({ph}, {ph}, {ph}, {ph}, {ph}, {ph}, {ph}, {ph})
        """
        sql_action = f"INSERT INTO actions (hand_id, street, player_name, action_type, amount, is_all_in) VALUES ({ph}, {ph}, {ph}, {ph}, {ph}, {ph})"

    # 파일 순회하며 파싱 및 트랜잭션 적재
    for file_path in txt_files:
        filename = os.path.basename(file_path)
        
        with open(file_path, 'r', encoding='utf-8-sig') as f:
            content = f.read()
            
        raw_hands = content.split("Poker Hand #")
        raw_hands = [h for h in raw_hands if h.strip()]
        
        for raw_h in raw_hands:
            hand_text = "Poker Hand #" + raw_h
            
            try:
                parsed = parse_hand_history(hand_text)
                if not parsed:
                    continue
                
                # 1. tournaments 테이블 적재
                cursor.execute(sql_tournament, (parsed['tournament']['tournament_id'], parsed['tournament']['name']))
                
                # 2. hands 테이블 적재
                cursor.execute(sql_hand, (
                    parsed['hand']['hand_id'], parsed['hand']['tournament_id'], parsed['hand']['level'],
                    parsed['hand']['small_blind'], parsed['hand']['big_blind'], parsed['hand']['timestamp'],
                    parsed['hand']['total_pot'], parsed['hand']['rake'], parsed['hand']['board'],
                    parsed['hand']['button_seat']
                ))
                
                # 3. players 테이블 적재
                for p_name in parsed['players']:
                    cursor.execute(sql_player, (p_name,))
                    
                # 4. hand_players 테이블 적재
                for hp in parsed['hand_players']:
                    cursor.execute(sql_hand_player, (
                        hp['hand_id'], hp['player_name'], hp['seat_number'], hp['chips_start'],
                        hp['hole_cards'], hp['position'], hp['is_hero'], hp['chips_won']
                    ))
                    
                # 5. actions 테이블 적재
                for act in parsed['actions']:
                    cursor.execute(sql_action, (
                        act['hand_id'], act['street'], act['player_name'],
                        act['action_type'], act['amount'], act['is_all_in']
                    ))
                    total_actions_inserted += 1
                
                total_hands_parsed += 1
                
            except Exception as e:
                # 에러 발생 시 롤백 및 로깅
                conn.rollback()
                print(f"에러 발생 (핸드 ID 파싱 중 생략): {e}")
                continue
        
        # 파일 단위 커밋
        conn.commit()

    conn.close()
    print("\n=== [ETL End] 데이터 적재 완료 ===")
    print(f"성공적으로 파싱 및 적재된 총 게임 판수(Hands): {total_hands_parsed}개")
    print(f"성공적으로 적재된 총 유저 베팅 액션 수(Actions): {total_actions_inserted}개")


if __name__ == "__main__":
    run_etl()
