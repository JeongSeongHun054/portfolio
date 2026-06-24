-- =========================================================================
-- iGaming 플랫폼 핵심 KPI 분석 SQL 스크립트 (kpi_analytics.sql)
-- =========================================================================
-- * 목적: ETL로 적재된 데이터베이스를 바탕으로 플레이어별 게임 성향 및 지표(KPI)를 산출합니다.
-- * 왜 이 쿼리 구조를 사용했는가?
--   - CTE(Common Table Expression, WITH 구문): 복잡한 분석을 단계별로 쪼개어 가독성을 극대화합니다. BigQuery 등 현대 DW에서 협업 시 필수적인 작성 스타일입니다.
--   - 분모가 0인 케이스 방지(Division by Zero): 데이터가 적어 Call 횟수가 0인 경우, 에러를 방지하기 위해 CASE 문이나 NULLIF 처리를 적용합니다.

WITH 
-- -------------------------------------------------------------------------
-- CTE 1. 플레이어별 참여 핸드 수 및 기본 손익 요약
-- -------------------------------------------------------------------------
player_base AS (
    SELECT 
        player_name,
        COUNT(DISTINCT hand_id) AS total_hands,                           -- 플레이어가 카드를 받고 참여한 총 게임 수
        SUM(CASE WHEN chips_won > 0 THEN 1 ELSE 0 END) AS won_hands,       -- 칩 손익이 플러스인 핸드 수 (이긴 횟수)
        SUM(chips_won) AS net_chips_won                                   -- 획득하거나 잃은 칩의 합계 (최종 수익 지표)
    FROM hand_players
    GROUP BY player_name
),

-- -------------------------------------------------------------------------
-- CTE 2. 프리플랍(Pre-flop) 단계 자발적 액션 분석 (VPIP, PFR 계산용)
-- -------------------------------------------------------------------------
-- * 개념 설명:
--   - VPIP (Voluntarily Put Money in Pot): 블라인드 강제 배팅을 제외하고, 자신의 의지로 칩을 팟에 넣은(Call 또는 Raise) 핸드 비율.
--     이 수치가 높을수록 많은 판에 참여하는 'Loose(루즈)'한 성향이며, 낮을수록 좋은 카드만 골라서 하는 'Tight(타이트)'한 성향입니다.
--   - PFR (Pre-flop Raise): 프리플랍 단계에서 먼저 레이즈(배팅액을 올림)를 한 핸드 비율.
--     이 수치가 높을수록 주도권을 잡으려는 'Aggressive(공격적)' 성향입니다.
preflop_actions AS (
    SELECT 
        player_name,
        -- 프리플랍 단계에서 자발적으로 칩을 넣은 핸드 수 계산 (Call, Bet, Raise)
        COUNT(DISTINCT CASE WHEN street = 'preflop' AND action_type IN ('calls', 'bets', 'raises') THEN hand_id END) AS vpip_hands,
        -- 프리플랍 단계에서 레이즈를 한 핸드 수 계산
        COUNT(DISTINCT CASE WHEN street = 'preflop' AND action_type = 'raises' THEN hand_id END) AS pfr_hands
    FROM actions
    GROUP BY player_name
),

-- -------------------------------------------------------------------------
-- CTE 3. 포스트플랍(Flop, Turn, River) 단계 액션 수 카운팅 (AF 계산용)
-- -------------------------------------------------------------------------
-- * 개념 설명:
--   - AF (Aggression Factor): 플랍 이후 단계에서 상대방에게 압박을 주는 베팅(Bet)과 레이즈(Raise) 횟수를, 수동적으로 따라가는 콜(Call) 횟수로 나눈 값입니다.
--     공식: (Bet 수 + Raise 수) / (Call 수)
--     이 값이 3.0 이상이면 매우 공격적(Aggressive), 1.0 이하면 매우 수동적(Passive)인 유저로 분류되어 플레이어 파산 확률 및 행동 패턴 분석에 중요 지표로 쓰입니다.
postflop_actions AS (
    SELECT 
        player_name,
        -- 공격적 액션(Bet, Raise) 횟수 합산
        SUM(CASE WHEN street IN ('flop', 'turn', 'river') AND action_type IN ('bets', 'raises') THEN 1 ELSE 0 END) AS agg_actions,
        -- 수동적 액션(Call) 횟수 합산
        SUM(CASE WHEN street IN ('flop', 'turn', 'river') AND action_type = 'calls' THEN 1 ELSE 0 END) AS passive_actions
    FROM actions
    GROUP BY player_name
)

-- -------------------------------------------------------------------------
-- 메인 쿼리: CTE들을 결합하여 최종 플레이어 프로필 분석 보고서 작성
-- -------------------------------------------------------------------------
SELECT 
    pb.player_name,
    pb.total_hands,
    
    -- VPIP(%) 계산: (자발적 참여 핸드 수 / 총 참여 핸드 수) * 100
    -- 데이터 정합성을 위해 NULL 값을 0으로 변환하고 소수점 둘째 자리까지 반올림
    ROUND(COALESCE(pa.vpip_hands, 0) * 100.0 / pb.total_hands, 2) AS vpip_percent,
    
    -- PFR(%) 계산: (선제 레이즈 핸드 수 / 총 참여 핸드 수) * 100
    ROUND(COALESCE(pa.pfr_hands, 0) * 100.0 / pb.total_hands, 2) AS pfr_percent,
    
    -- AF (공격성 수치) 계산: 공격적 액션 수 / 수동적 액션 수
    -- 분모인 passive_actions(Call 횟수)가 0인 경우 division by zero 에러가 나므로,
    -- 만약 Call이 0이고 Bet/Raise가 있으면 임의의 값(예: 99.99) 또는 NULL을 반환하도록 분기 처리합니다.
    CASE 
        WHEN COALESCE(pfa.passive_actions, 0) = 0 THEN 
            CASE WHEN COALESCE(pfa.agg_actions, 0) > 0 THEN 99.99 ELSE 0.0 END
        ELSE ROUND(pfa.agg_actions * 1.0 / pfa.passive_actions, 2)
    END AS aggression_factor,
    
    -- Win Rate(%) 계산: (승리한 핸드 수 / 총 참여 핸드 수) * 100
    ROUND(pb.won_hands * 100.0 / pb.total_hands, 2) AS win_rate,
    
    -- 순 손익 칩
    pb.net_chips_won,
    
    -- 성향 분류 (Profiling): VPIP와 PFR의 차이 및 절대치 기준
    -- * Loose-Passive (전화기, Fish): 많은 판에 들어가서 콜만 받아줌 (VPIP는 높으나 PFR이 현저히 낮음)
    -- * Tight-Aggressive (상어, Reg): 좋은 카드만 골라서 주도적으로 공격함 (VPIP는 낮으나 참여 시 PFR이 높음)
    -- * Loose-Aggressive (미치광이, Maniac): 많은 판에 들어가서 레이즈를 남발함 (VPIP도 높고 PFR도 높음)
    -- * Tight-Passive (바위, Rock): 극단적으로 카드만 기다리며 수동적임 (VPIP와 PFR 둘 다 낮음)
    CASE 
        WHEN (pa.vpip_hands * 100.0 / pb.total_hands) >= 30.0 AND (pa.pfr_hands * 100.0 / pb.total_hands) < 15.0 THEN 'Loose-Passive'
        WHEN (pa.vpip_hands * 100.0 / pb.total_hands) >= 30.0 AND (pa.pfr_hands * 100.0 / pb.total_hands) >= 15.0 THEN 'Loose-Aggressive'
        WHEN (pa.vpip_hands * 100.0 / pb.total_hands) < 30.0 AND (pa.pfr_hands * 100.0 / pb.total_hands) >= (pa.vpip_hands * 80.0 / pb.total_hands) THEN 'Tight-Aggressive'
        WHEN (pa.vpip_hands * 100.0 / pb.total_hands) < 15.0 THEN 'Tight-Passive'
        ELSE 'Neutral'
    END AS player_style

FROM player_base pb
LEFT JOIN preflop_actions pa ON pb.player_name = pa.player_name
LEFT JOIN postflop_actions pfa ON pb.player_name = pfa.player_name
-- 최소 30핸드 이상 플레이한 고신뢰도 유저들만 필터링하여 노이즈 제거 (데이터 분석의 신뢰성 향상 기법)
WHERE pb.total_hands >= 30
ORDER BY pb.total_hands DESC, pb.net_chips_won DESC;
