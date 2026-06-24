-- =========================================================================
-- iGaming 포커 로그 데이터 적재용 PostgreSQL 데이터베이스 스키마 (schema_pg.sql)
-- =========================================================================
-- * 목적: PostgreSQL 서버에 데이터를 적재하기 위한 전용 스키마 정의 파일입니다.
-- * SQLite 스키마(schema.sql)와의 핵심 차이점 및 기술적 특징 요약:
--   1) 키 자동 증가(Auto-increment) 구현:
--      - SQLite: 'INTEGER PRIMARY KEY AUTOINCREMENT' 문법을 사용합니다.
--      - PostgreSQL: 'SERIAL PRIMARY KEY' 문법을 사용합니다. 내부적으로 시퀀스(Sequence) 객체를 생성하여 동작합니다.
--   2) 데이터 무결성 및 성능 최적화:
--      - PostgreSQL은 동시성(Concurrency) 제어 및 트랜잭션 격리 수준이 SQLite보다 훨씬 고도화되어 있어 실무용 대용량 환경에 쓰입니다.
--      - 이에 최적화된 자료형(TEXT, INTEGER 등) 및 외래키 제약조건을 선언합니다.

-- -------------------------------------------------------------------------
-- 1. tournaments (토너먼트 마스터 테이블)
-- -------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS tournaments (
    tournament_id VARCHAR(100) PRIMARY KEY, -- 토너먼트 ID (PK)
    name VARCHAR(255)                       -- 토너먼트 명
);

-- -------------------------------------------------------------------------
-- 2. players (플레이어 마스터 테이블)
-- -------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS players (
    player_name VARCHAR(100) PRIMARY KEY   -- 플레이어 닉네임 (PK)
);

-- -------------------------------------------------------------------------
-- 3. hands (핸드 메타데이터 테이블)
-- -------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS hands (
    hand_id VARCHAR(100) PRIMARY KEY,      -- 핸드 고유 ID (PK)
    tournament_id VARCHAR(100),            -- 토너먼트 ID (FK)
    level VARCHAR(100),                    -- 블라인드 레벨
    small_blind INTEGER,                   -- 스몰 블라인드 금액
    big_blind INTEGER,                     -- 빅 블라인드 금액
    timestamp TIMESTAMP,                   -- 게임 시작 일시 (PostgreSQL 전용 TIMESTAMP 타입 적용)
    total_pot INTEGER,                     -- 총 팟 크기
    rake INTEGER,                          -- 수수료 (매출액)
    board VARCHAR(100),                    -- 커뮤니티 카드
    button_seat INTEGER,                   -- 딜러 버튼 시트 번호
    FOREIGN KEY(tournament_id) REFERENCES tournaments(tournament_id) ON DELETE CASCADE
);

-- -------------------------------------------------------------------------
-- 4. hand_players (핸드 참여 플레이어 상태 테이블)
-- -------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS hand_players (
    hand_id VARCHAR(100),                  -- 핸드 ID (FK)
    player_name VARCHAR(100),              -- 플레이어 명 (FK)
    seat_number INTEGER,                   -- 시트 번호
    chips_start INTEGER,                   -- 시작 칩
    hole_cards VARCHAR(20),                -- 홀 카드
    position VARCHAR(20),                  -- 계산된 포지션
    is_hero INTEGER,                       -- Hero 여부 (1: True, 0: False)
    chips_won INTEGER,                     -- 게임 결과 손익 (+/-)
    PRIMARY KEY (hand_id, player_name),
    FOREIGN KEY(hand_id) REFERENCES hands(hand_id) ON DELETE CASCADE,
    FOREIGN KEY(player_name) REFERENCES players(player_name) ON DELETE CASCADE
);

-- -------------------------------------------------------------------------
-- 5. actions (상세 베팅 액션 로그 테이블)
-- -------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS actions (
    -- PostgreSQL에서는 SQLite의 AUTOINCREMENT 대신 SERIAL을 사용하여 자동으로 순차 값을 증가시킵니다.
    action_id SERIAL PRIMARY KEY,          -- 액션 시퀀스 고유 ID (자동 증가 PK)
    hand_id VARCHAR(100),                  -- 핸드 ID (FK)
    street VARCHAR(50),                    -- 베팅 단계 ('preflop', 'flop' 등)
    player_name VARCHAR(100),              -- 플레이어 명 (FK)
    action_type VARCHAR(50),               -- 행동 종류 ('folds', 'calls' 등)
    amount INTEGER,                        -- 배팅 칩 금액 (없으면 NULL)
    is_all_in INTEGER,                     -- 올인 여부 (1: True, 0: False)
    FOREIGN KEY(hand_id) REFERENCES hands(hand_id) ON DELETE CASCADE,
    FOREIGN KEY(player_name) REFERENCES players(player_name) ON DELETE CASCADE
);

-- 인덱스 설계 (PostgreSQL용)
-- 실무에서는 SELECT 쿼리 성능을 높이기 위해 자주 조회되는 FK나 조건 컬럼에 B-Tree 인덱스를 반드시 생성해야 합니다.
CREATE INDEX IF NOT EXISTS idx_actions_hand_id ON actions(hand_id);
CREATE INDEX IF NOT EXISTS idx_actions_player_name ON actions(player_name);
CREATE INDEX IF NOT EXISTS idx_hand_players_hand_id ON hand_players(hand_id);
CREATE INDEX IF NOT EXISTS idx_hand_players_player_name ON hand_players(player_name);
