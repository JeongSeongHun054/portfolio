-- =========================================================================
-- iGaming 포커 로그 데이터 적재용 SQLite 데이터베이스 스키마 (schema.sql)
-- =========================================================================
-- 이 스키마는 비정형 텍스트 포커 로그를 관계형 데이터베이스로 변환하여 저장하기 위한 것입니다.
-- 데이터 분석가 직무에서 SQL 실력을 보여주기 위해 관계형 모델링(RDBMS)을 올바르게 설계하는 것이 중요합니다.
-- 각 테이블과 컬럼에는 왜 이 설계가 필요하고, 게임 분석 지표(KPI)와 어떻게 연결되는지 상세히 설명되어 있습니다.

-- -------------------------------------------------------------------------
-- 1. tournaments (토너먼트 마스터 테이블)
-- -------------------------------------------------------------------------
-- * 설계 목적: 게임이 진행된 토너먼트의 고유 정보를 저장합니다.
-- * 실무 활용: 플랫폼 관기자 시점에서 어떤 종류의 토너먼트(예: Turbo, Hyper)가 유저에게 가장 인기 있고,
--   어느 시간대에 트래픽이 높은지 분석하는 기준 차원(Dimension) 테이블 역할을 합니다.
CREATE TABLE IF NOT EXISTS tournaments (
    tournament_id TEXT PRIMARY KEY,        -- 토너먼트의 고유 식별 번호 (예: '246182292')
    name TEXT                              -- 토너먼트의 명칭 및 규칙 정보 (예: 'Daily Turbo $1 Hold''em No Limit')
);

-- -------------------------------------------------------------------------
-- 2. players (플레이어 마스터 테이블)
-- -------------------------------------------------------------------------
-- * 설계 목적: 고유한 플레이어 목록을 관리합니다.
-- * 실무 활용: 유저 분석 시 회원(User) 테이블에 해당하며, 고유 사용자 수(DAU/MAU)나 
--   플레이어 성향 군집화(Clustering) 시 기준 테이블로 활용됩니다.
CREATE TABLE IF NOT EXISTS players (
    player_name TEXT PRIMARY KEY           -- 플레이어의 고유 닉네임 또는 익명화된 해시값 (예: 'Hero', '97906ffe')
);

-- -------------------------------------------------------------------------
-- 3. hands (핸드 메타데이터 테이블)
-- -------------------------------------------------------------------------
-- * 설계 목적: 한 게임(Hand) 단위를 나타냅니다. 포커에서는 카드가 새로 딜링되어 승패가 날 때까지를 'Hand'라고 부릅니다.
-- * 실무 활용: 각 판당 판돈(Total Pot)의 분포를 분석하거나, 시간의 흐름에 따른 게임 진행 속도(Level 상승 추이) 분석,
--   게임의 최종 보드판(Board, 커뮤니티 카드) 상황에 따른 유저 행동 양상 분석에 활용됩니다.
CREATE TABLE IF NOT EXISTS hands (
    hand_id TEXT PRIMARY KEY,              -- 핸드 고유 식별 번호 (예: 'TM5288651169')
    tournament_id TEXT,                     -- 해당 핸드가 속한 토너먼트 ID (tournaments 테이블 참조)
    level TEXT,                            -- 블라인드 레벨 (예: 'Level 6 (140/280)')
    small_blind INTEGER,                   -- 스몰 블라인드 강제 배팅 금액 (기본 판돈 분석용)
    big_blind INTEGER,                     -- 빅 블라인드 강제 배팅 금액 (기본 판돈 분석용)
    timestamp TEXT,                        -- 게임이 시작된 날짜 및 시간 (시간대별 트래픽/플레이 빈도 분석용)
    total_pot INTEGER,                     -- 해당 게임에서 형성된 총 팟(판돈) 크기 (매출 및 판돈 분포 분석용)
    rake INTEGER,                          -- 게임사(플랫폼)가 가져가는 수수료 (플랫폼의 주요 수수료 수익원)
    board TEXT,                            -- 커뮤니티에 깔린 5장의 카드 (예: 'Kc 2h 4s Qh 6h', 안 깔렸으면 NULL)
    button_seat INTEGER,                   -- 딜러 버튼 위치의 시트 번호 (포지션 계산용)
    FOREIGN KEY(tournament_id) REFERENCES tournaments(tournament_id)
);

-- -------------------------------------------------------------------------
-- 4. hand_players (핸드 참여 플레이어 상태 테이블)
-- -------------------------------------------------------------------------
-- * 설계 목적: 하나의 핸드(게임)에 참여한 플레이어들의 시작 상태와 매칭 결과를 저장합니다. (1:N 관계)
-- * 실무 활용: 
--   1) 플레이어의 게임 시작 전 칩(Chips)을 통해 '플레이어 자산 등급(Whale, Dolphins, Minnows)' 분석 가능.
--   2) 획득한 칩(chips_won)을 통해 최종 손익 계산 및 유저 잔존율(Retention) 영향 분석 가능.
--   3) hole_cards(플레이어가 받은 2장 카드)를 기반으로 유저의 '베팅 성향'과 '실제 카드 세기'의 상관관계 파악 가능.
CREATE TABLE IF NOT EXISTS hand_players (
    hand_id TEXT,                          -- 핸드 고유 ID (hands 테이블 참조)
    player_name TEXT,                      -- 참여 플레이어 이름 (players 테이블 참조)
    seat_number INTEGER,                   -- 테이블 상의 시트 번호 (1~8)
    chips_start INTEGER,                   -- 게임 시작 시 플레이어가 들고 있던 칩 개수 (초기 자산 상태)
    hole_cards TEXT,                       -- 플레이어가 배분받은 2장의 카드 (예: 'Ah Ad', 알려지지 않았으면 NULL)
    position TEXT,                         -- 딜러 버튼과의 거리로 계산된 포지션 (예: 'SB', 'BB', 'BTN', 'UTG', 'CO' 등)
    is_hero INTEGER,                       -- 분석 대상 본인(Hero) 여부 (1: True, 0: False)
    chips_won INTEGER,                     -- 이 핸드에서 최종적으로 획득하거나 잃은 칩 순액 (+/-)
    PRIMARY KEY (hand_id, player_name),
    FOREIGN KEY(hand_id) REFERENCES hands(hand_id),
    FOREIGN KEY(player_name) REFERENCES players(player_name)
);

-- -------------------------------------------------------------------------
-- 5. actions (상세 베팅 액션 로그 테이블)
-- -------------------------------------------------------------------------
-- * 설계 목적: 각 핸드 내에서 플레이어들이 취한 모든 행동(폴드, 콜, 레이즈 등)을 시간 순서대로 기록합니다.
-- * 실무 활용: __포트폴리오의 심장__ 역할을 하는 테이블입니다.
--   1) Funnel(퍼널) 분석: street('preflop', 'flop', 'turn', 'river') 단계별로 folds(이탈)하는 플레이어 비율을 추적합니다.
--   2) KPI 계산: VPIP(자발적 참여율), PFR(선제 공격율) 등을 계산할 때, 프리플랍 단계의 'raises', 'calls' 액션을 카운팅합니다.
--   3) A/B Test: 특정 베팅 액션(예: 프리플랍에서 크게 레이즈 vs 작게 레이즈)에 따른 상대방의 폴드율(이탈율) 차이를 검증합니다.
CREATE TABLE IF NOT EXISTS actions (
    action_id INTEGER PRIMARY KEY AUTOINCREMENT, -- 액션 시퀀스 고유 번호 (자동 증가)
    hand_id TEXT,                          -- 핸드 고유 ID (hands 테이블 참조)
    street TEXT,                           -- 베팅 단계 ('preflop', 'flop', 'turn', 'river', 'showdown')
    player_name TEXT,                      -- 행동을 한 플레이어 이름 (players 테이블 참조)
    action_type TEXT,                      -- 행동 종류 ('posts_sb', 'posts_bb', 'posts_ante', 'folds', 'calls', 'bets', 'raises', 'checks', 'shows', 'collected')
    amount INTEGER,                        -- 베팅 또는 레이즈한 칩의 크기 (베팅을 안 한 경우는 NULL)
    is_all_in INTEGER,                     -- 올인 여부 (1: All-in, 0: Normal)
    FOREIGN KEY(hand_id) REFERENCES hands(hand_id),
    FOREIGN KEY(player_name) REFERENCES players(player_name)
);

-- 데이터 쿼리 성능 향상을 위한 인덱스 설계
-- 실무에서는 수백만 건의 데이터를 다룰 때 인덱스가 유무가 쿼리 속도를 결정합니다.
CREATE INDEX IF NOT EXISTS idx_actions_hand_id ON actions(hand_id);
CREATE INDEX IF NOT EXISTS idx_actions_player_name ON actions(player_name);
CREATE INDEX IF NOT EXISTS idx_hand_players_hand_id ON hand_players(hand_id);
CREATE INDEX IF NOT EXISTS idx_hand_players_player_name ON hand_players(player_name);
