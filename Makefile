.PHONY: install test clean run-sql run-mybatis run-dir help

# Python 명령어 자동 감지
PYTHON_CHECK := $(shell which python3 2>/dev/null)
PYTHON3_EXISTS := $(strip $(PYTHON_CHECK))

# 환경 변수로 Python 명령어 지정 가능, 없으면 자동 감지 결과 사용
ifdef PYTHON_CMD
    PYTHON := $(PYTHON_CMD)
else
    ifeq ($(PYTHON3_EXISTS),)
        PYTHON := python
    else
        PYTHON := python3
    endif
endif

# pip 명령어도 동일하게 처리
PIP_CHECK := $(shell which pip3 2>/dev/null)
PIP3_EXISTS := $(strip $(PIP_CHECK))

ifdef PIP_CMD
    PIP := $(PIP_CMD)
else
    ifeq ($(PIP3_EXISTS),)
        PIP := pip
    else
        PIP := pip3
    endif
endif

PROJECT = oracle_to_postgres_analyzer
SAMPLE_DIR = ./samples
OUTPUT_DIR = ./output
TEST_DIR = ./tests
SRC_DIR = ./src

# 기본 명령어
help:
	@echo "Oracle to PostgreSQL Query Analyzer 사용 가이드"
	@echo ""
	@echo "현재 사용 중인 Python: $(PYTHON)"
	@echo "현재 사용 중인 pip: $(PIP)"
	@echo ""
	@echo "Python 명령어 변경: make install PYTHON_CMD=python3"
	@echo "pip 명령어 변경: make install PIP_CMD=pip3"
	@echo ""
	@echo "사용 가능한 명령어:"
	@echo "  make install        : 필요한 패키지 설치"
	@echo "  make install-dev    : 개발에 필요한 패키지 설치"
	@echo "  make test           : 테스트 실행"
	@echo "  make clean          : 임시 파일 및 캐시 삭제"
	@echo "  make run-sql        : 일반 SQL 쿼리 분석기 실행"
	@echo "  make run-mybatis    : MyBatis 동적 쿼리 분석기 실행"
	@echo "  make run-dir        : 디렉토리 분석 도구 실행 (ARGS='디렉토리경로 [출력파일]')"
	@echo "  make analyze-samples: 샘플 파일 분석"
	@echo ""
	@echo "예시:"
	@echo "  make run-dir ARGS='./samples output_report.md'"

# 설치 명령어
install:
	$(PIP) install -e .

install-dev:
	$(PIP) install -e ".[dev]"
	$(PIP) install pytest pytest-cov flake8

# 테스트 명령어
test:
	@mkdir -p $(OUTPUT_DIR)
	$(PYTHON) -m pytest $(TEST_DIR) -v

# 정리 명령어
clean:
	@rm -rf __pycache__
	@rm -rf $(SRC_DIR)/__pycache__
	@rm -rf .pytest_cache
	@rm -rf .coverage
	@rm -rf build/
	@rm -rf dist/
	@rm -rf *.egg-info
	@echo "정리 완료"

# 실행 명령어 - 직접 파이썬 파일 실행
run-sql:
	$(PYTHON) $(SRC_DIR)/query_complexity_analyzer.py

run-mybatis:
	$(PYTHON) $(SRC_DIR)/mybatis_query_analyzer.py

run-dir:
	@mkdir -p $(OUTPUT_DIR)
	$(PYTHON) $(SRC_DIR)/sql_directory_analyzer.py $(ARGS)

# 샘플 분석
analyze-samples:
	@mkdir -p $(OUTPUT_DIR)
	@echo "샘플 파일 분석 중... ($(PYTHON) 사용)"
	$(PYTHON) $(SRC_DIR)/sql_directory_analyzer.py $(SAMPLE_DIR) $(OUTPUT_DIR)/sample_analysis.md
	@echo "분석 완료. 결과는 $(OUTPUT_DIR)/sample_analysis.md 파일에서 확인하세요."

# 기본 명령어
.DEFAULT_GOAL := help
