# -*- coding: utf-8 -*-
import re
import os
import sys
import time
from deep_translator import GoogleTranslator

# Windows cp949 인코딩으로 인한 이모지 출력 크래시 방지
try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

# 1. 포커 및 통계 도메인 용어 사전 (오역 방지용)
GLOSSARY = {
    "핵심 지표 요약 (Overview)": "Key Metrics Summary (Overview)",
    "플레이어 프로파일링 (Profiling)": "Player Profiling",
    "퍼널 & 코호트 분석 (Funnel & Cohort)": "Funnel & Cohort Analysis",
    "A/B 테스트 가설 검정 (A/B Test)": "A/B Testing & Hypothesis Testing",
    "시나리오 시뮬레이터 (Simulator)": "Scenario Simulator",
    "플랫폼 활성 지표 요약": "Platform Activation Metrics Summary",
    "자발적 참여율 (VPIP)": "Voluntarily Put Money in Pot (VPIP)",
    "선제 공격률 (PFR)": "Pre-flop Raise (PFR)",
    "공격성 수치 (AF)": "Aggression Factor (AF)",
    "참여 승률 (Win Rate)": "Win Rate",
    "자발적 칩 베팅률": "Voluntarily Put Money in Pot (VPIP)",
    "선제 공격률": "Pre-flop Raise (PFR)",
    "공격성 수치": "Aggression Factor (AF)",
    "참여 승률": "Win Rate",
    "플레이 스타일": "Playstyle",
    "독립표본 T-검정": "Independent Two-Sample T-Test",
    "유의 확률": "p-value",
    "검정 통계량": "T-statistic",
    "귀무가설": "Null Hypothesis",
    "대립가설": "Alternative Hypothesis",
    "유의수준": "Significance Level",
    "토너먼트 종류": "Tournament Styles",
    "게임 단계 (블라인드)": "Game Stages (Blinds)",
    "최소 플레이 판수": "Min Hands Played",
    "플레이어 포지션": "Player Positions",
    "데이터베이스 연동 설정": "Database Integration Settings",
    "글로벌 필터 (Tableau 스타일)": "Global Filters (Tableau Style)",
    "아키텍처 기술 스택": "Architecture Tech Stack",
    "실시간 데이터 적재": "Real-time Data Ingestion",
    "플레이 스타일 샌드박스": "Playstyle Sandbox",
    "기본 통계량": "Basic Statistics",
    "누적 칩스": "Cumulative Chips",
    "총 플레이 판수": "Total Hands Played",
    "평균 획득 칩": "Average Chips Won",
    "중앙값 칩": "Median Chips",
    "표본 수": "Sample Size",
    "검증 결과": "Verification Results",
    "최댓값 (max)": "Maximum (max)",
    "최소값 (min)": "Minimum (min)",
}

translator = GoogleTranslator(source='ko', target='en')


def has_korean(s):
    return any(ord('가') <= ord(c) <= ord('힣') for c in s)


def is_sql_query(s):
    keywords = {'select', 'with', 'from', 'join', 'where', 'group by', 'having', 'order by'}
    s_lower = s.lower()
    match_count = sum(1 for kw in keywords if kw in s_lower)
    return match_count >= 2


def get_sql_translation_units(sql_str):
    units = []
    lines = sql_str.split('\n')
    for line in lines:
        stripped = line.strip()
        if stripped.startswith('--') or stripped.startswith('#'):
            comment_text = stripped.lstrip('-# ').strip()
            if has_korean(comment_text):
                units.append(comment_text)
        else:
            matches = re.findall(r'(?:\\?["\'])([^\'"\\]*[\uac00-\ud7a3]+[^\'"\\]*)(?:\\?["\'])', line)
            for m in matches:
                units.append(m)
    return units


def rebuild_sql_query(sql_str, translation_map):
    lines = sql_str.split('\n')
    new_lines = []
    for line in lines:
        stripped = line.strip()
        if stripped.startswith('--') or stripped.startswith('#'):
            comment_marker = '-- ' if stripped.startswith('--') else '# '
            comment_text = stripped.lstrip('-# ').strip()
            if comment_text in translation_map:
                translated = translation_map[comment_text]
                new_lines.append(line.replace(comment_text, translated))
            else:
                new_lines.append(line)
        else:
            matches = re.findall(r'(?:\\?["\'])([^\'"\\]*[\uac00-\ud7a3]+[^\'"\\]*)(?:\\?["\'])', line)
            new_line = line
            for m in matches:
                if m in translation_map:
                    translated = translation_map[m]
                    new_line = new_line.replace(m, translated)
            new_lines.append(new_line)
    return '\n'.join(new_lines)


def translate_batch_with_protection(texts):
    if not texts:
        return []

    # 각 텍스트별로 f-string 변수 {variable} 보호 처리
    protected_texts = []
    variables_map = []
    
    for text in texts:
        variables = re.findall(r'\{[^}]+\}', text)
        variables_map.append(variables)
        
        temp_text = text
        for i, var in enumerate(variables):
            temp_text = temp_text.replace(var, f"__VAR_{i}__")
        protected_texts.append(temp_text)

    # 배치 단위로 번역 실행 (속도 최적화 및 429 에러 방지)
    translated_protected = []
    try:
        translated_protected = translator.translate_batch(protected_texts)
    except Exception as e:
        print(f"Batch translation failed: {e}. Falling back to individual translation with sleep...")
        # 개별로 대피하여 슬립을 주며 재전송
        for text in protected_texts:
            try:
                translated_protected.append(translator.translate(text))
                time.sleep(0.3)
            except Exception as e2:
                print(f"Individual translation failed: {e2}")
                translated_protected.append(text)

    # 보호 처리 복원
    final_translations = []
    for idx, trans_text in enumerate(translated_protected):
        orig_variables = variables_map[idx]
        restored_text = trans_text
        for i, var in enumerate(orig_variables):
            restored_text = re.sub(rf'__[vV][aA][rR]_{i}__', var, restored_text)
        final_translations.append(restored_text)

    return final_translations


def translate_app(input_path="src/app.py", output_path="src/app_en.py"):
    print(f"Reading {input_path}...")
    with open(input_path, "r", encoding="utf-8") as f:
        content = f.read()

    # 파이썬 문자열 리터럴 정규표현식
    string_pattern = re.compile(
        r'(f?r?(""".*?"""|\'\'\'.*?\'\'\'|"([^"\\]|\\.)*"|\'([^\'\\]|\\.)*\'))',
        re.DOTALL
    )

    matches = list(string_pattern.finditer(content))
    print(f"Found {len(matches)} string literals. Extracting Korean text...")

    # 1단계: 번역이 필요한 한국어 문자열과 인덱스 수집
    unique_korean_strings = set()
    matches_to_translate = []

    for match in matches:
        full_match = match.group(1)
        start, end = match.span(1)

        # 접두사 분리
        match_str = full_match
        prefix = ""
        if match_str.startswith('f'):
            prefix += 'f'
            match_str = match_str[1:]
        if match_str.startswith('r'):
            prefix += 'r'
            match_str = match_str[1:]

        # 따옴표 분리
        quote_char = ""
        if match_str.startswith('"""'):
            quote_char = '"""'
        elif match_str.startswith("'''"):
            quote_char = "'''"
        elif match_str.startswith('"'):
            quote_char = '"'
        elif match_str.startswith("'"):
            quote_char = "'"

        if not quote_char:
            continue

        inner_content = match_str[len(quote_char):-len(quote_char)]

        if has_korean(inner_content):
            if is_sql_query(inner_content):
                # SQL 쿼리는 내부의 한국어 주석과 따옴표 안 문자열만 번역 대상으로 수집
                units = get_sql_translation_units(inner_content)
                for unit in units:
                    unit_clean = unit.strip()
                    if unit_clean not in GLOSSARY:
                        unique_korean_strings.add(unit)
            else:
                inner_clean = inner_content.strip()
                # 용어 사전에 있으면 배수 제외
                if inner_clean not in GLOSSARY:
                    unique_korean_strings.add(inner_content)
            matches_to_translate.append((start, end, prefix, quote_char, inner_content))

    print(f"Unique Korean strings to translate: {len(unique_korean_strings)}")

    # 2단계: 일괄 번역 진행 (배치 처리)
    unique_list = list(unique_korean_strings)
    translation_map = {}
    
    # 사전에 정의된 용어 매핑을 기본으로 추가
    for k, v in GLOSSARY.items():
        translation_map[k] = v

    batch_size = 25
    for i in range(0, len(unique_list), batch_size):
        batch = unique_list[i : i + batch_size]
        print(f"Translating batch {i // batch_size + 1} / {(len(unique_list) - 1) // batch_size + 1}...")
        translated_batch = translate_batch_with_protection(batch)
        
        for orig, trans in zip(batch, translated_batch):
            translation_map[orig] = trans
        
        time.sleep(1.0) # 구글 서버 차단 방지를 위한 세션간 딜레이

    print("Translation phase finished. Reconstructing file...")

    # 3단계: 파일 재구성 (역순으로 오프셋 유지)
    new_content = content
    translated_count = 0

    for start, end, prefix, quote_char, inner_content in sorted(matches_to_translate, key=lambda x: x[0], reverse=True):
        if is_sql_query(inner_content):
            # SQL 쿼리는 내부 문자열들을 치환하여 재구성
            translated_inner = rebuild_sql_query(inner_content, translation_map)
        else:
            # 번역본 매핑 찾기
            # 공백이 있는 경우가 있으므로 스트립 버전도 체크
            inner_clean = inner_content.strip()
            if inner_content in translation_map:
                translated_inner = translation_map[inner_content]
            elif inner_clean in translation_map:
                translated_inner = translation_map[inner_clean]
            else:
                # 매핑 실패 시 개별 시도
                try:
                    translated_inner = translate_batch_with_protection([inner_content])[0]
                    translation_map[inner_content] = translated_inner
                except Exception:
                    translated_inner = inner_content

        # 이스케이프 보정
        if quote_char in ('"', '"""'):
            translated_inner = translated_inner.replace('"', '\\"')
        elif quote_char in ("'", "'''"):
            translated_inner = translated_inner.replace("'", "\\'")

        # 치환 문자열 구성
        replacement = f"{prefix}{quote_char}{translated_inner}{quote_char}"
        new_content = new_content[:start] + replacement + new_content[end:]
        translated_count += 1

    # Remove page config and language routing for English version to prevent duplication/recursion
    new_content = re.sub(
        r'st\.set_page_config\s*\([^)]*\)',
        'pass  # Page config set in app.py',
        new_content,
        flags=re.DOTALL
    )
    new_content = re.sub(
        r'# --- 다국어 설정 및 라우팅 ---.*?# ------------------------------',
        'pass  # Language routing managed in app.py',
        new_content,
        flags=re.DOTALL
    )

    # 4단계: app_en.main() 형태로 코드 구조화
    lines = new_content.split('\n')
    import_lines = []
    app_lines = []
    
    in_imports = True
    for line in lines:
        if line.startswith(('import ', 'from ')):
            import_lines.append(line)
        elif not line.strip() and in_imports:
            import_lines.append(line)
        else:
            in_imports = False
            app_lines.append(line)

    main_func_code = "\n".join(import_lines) + "\n\n"
    main_func_code += "def main():\n"
    for line in app_lines:
        if line.strip():
            main_func_code += "    " + line + "\n"
        else:
            main_func_code += "\n"

    # app_en.py 파일에 저장
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(main_func_code)

    print(f"Bilingual translation complete! {translated_count} strings processed. Saved to {output_path}")


if __name__ == "__main__":
    translate_app()
