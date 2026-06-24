# -*- coding: utf-8 -*-
import os
import sys

# src 디렉토리를 파이썬 경로에 추가하여 모듈 임포트 호환성 보장
src_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "src"))
if src_dir not in sys.path:
    sys.path.append(src_dir)

# 메인 app.py 실행 (Streamlit은 임포트 시 탑다운으로 모든 코드를 실행함)
import app
