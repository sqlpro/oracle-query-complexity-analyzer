# Oracle to PostgreSQL Query Analyzer 사용 가이드

이 문서는 Oracle to PostgreSQL Query Analyzer의 상세한 사용 방법을 설명합니다.

## 목차

1. [설치](#설치)
2. [기본 사용법](#기본-사용법)
3. [고급 사용법](#고급-사용법)
4. [결과 해석](#결과-해석)
5. [문제 해결](#문제-해결)

## 설치

### 필수 요구사항

- Python 3.6 이상
- sqlparse 라이브러리

### 설치 방법

```bash
# 저장소 클론
git clone https://github.com/sqlpro/oracle-query-complexity-analyzer.git
cd oracle-query-complexity-analyzer

# 필요한 패키지 설치 (자동으로 python/python3 감지)
make install

# 특정 Python 버전 지정
make install PYTHON_CMD=python3.9 PIP_CMD=pip3.9

# 또는 pip를 직접 사용
pip install -e .
```

## 기본 사용법

### 1. 단일 SQL 쿼리 분석

```bash
# Makefile을 사용한 실행
make run-sql

# 또는 직접 실행
python src/query_complexity_analyzer.py
```

실행 후 프롬프트에 분석할 SQL 쿼리를 입력하세요. 입력을 마치려면 빈 줄에서 Ctrl+D(Unix) 또는 Ctrl+Z(Windows)를 누르세요.

분석이 완료되면 결과를 파일로 저장할지 여부를 물어봅니다. 'y'를 선택하면 마크다운 형식의 보고서 파일이 생성됩니다.

### 2. MyBatis 동적 쿼리 분석

```bash
# Makefile을 사용한 실행
make run-mybatis

# 또는 직접 실행
python src/mybatis_query_analyzer.py
```

실행 후 메뉴에서 '2. MyBatis XML 쿼리 분석'을 선택하고, 프롬프트에 분석할 MyBatis XML 쿼리를 입력하세요.

분석이 완료되면 결과를 파일로 저장할지 여부를 물어봅니다. 'y'를 선택하면 마크다운 형식의 보고서 파일이 생성됩니다.

### 3. 디렉토리 내 모든 SQL 파일 분석

```bash
# Makefile을 사용한 실행
make run-dir ARGS='/path/to/sql/files output_report.md'

# 출력 파일 경로 없이 실행 (대화형으로 저장 여부 결정)
make run-dir ARGS='/path/to/sql/files'

# 또는 직접 실행
python src/sql_directory_analyzer.py /path/to/sql/files output_report.md
```

출력 파일 경로를 지정하지 않으면, 분석 후 결과를 파일로 저장할지 여부를 물어봅니다.

### 4. 샘플 파일 분석

```bash
# 샘플 파일 분석 및 결과 저장
make analyze-samples
```

이 명령어는 `samples` 디렉토리의 모든 SQL 파일을 분석하고 `output/sample_analysis.md` 파일에 결과를 저장합니다.

## 고급 사용법

### Python 코드에서 사용하기

```python
# 일반 SQL 쿼리 분석
from src.query_complexity_analyzer import analyze_query

with open('query.sql', 'r') as f:
    sql_query = f.read()
    
score, description, details = analyze_query(sql_query)
print(f"복잡도: {score}/10 - {description}")

# MyBatis 동적 쿼리 분석
from src.mybatis_query_analyzer import analyze_query as analyze_mybatis_query

with open('mybatis_query.xml', 'r') as f:
    xml_query = f.read()
    
score, description, details = analyze_mybatis_query(xml_query, is_mybatis_xml=True)
print(f"복잡도: {score}/10 - {description}")

# 디렉토리 분석
from src.sql_directory_analyzer import analyze_directory, generate_report

results = analyze_directory('/path/to/sql/files')
generate_report(results, 'output_report.md')
```

### 특정 Python 버전 사용

Makefile은 시스템에 python3가 설치되어 있는지 자동으로 감지하여 사용합니다. 특정 Python 버전을 사용하려면:

```bash
# Python 3.9 사용
make run-sql PYTHON_CMD=python3.9

# Python 3.8 사용
make run-mybatis PYTHON_CMD=python3.8

# 가상 환경의 Python 사용
make run-dir ARGS='/path/to/sql/files' PYTHON_CMD=/path/to/venv/bin/python
```

### 대규모 프로젝트 분석

대규모 프로젝트에서는 다음과 같이 사용할 수 있습니다:

```bash
# 모든 SQL 파일 분석 및 보고서 생성
make run-dir ARGS='/path/to/project/sql output_report.md'

# 특정 패턴의 파일만 분석 (쉘 스크립트 사용)
find /path/to/project -name "*.sql" | grep "oracle" > oracle_files.txt
mkdir -p analysis_reports

for file in $(cat oracle_files.txt); do
    dir=$(dirname $file)
    filename=$(basename $file)
    make run-dir ARGS="$dir analysis_reports/${filename%.sql}_report.md"
done
```

## 결과 해석

### 복잡도 점수

복잡도 점수는 0-10 척도로 표시되며, 다음과 같이 해석할 수 있습니다:

- **0-1**: 매우 간단 (Very Simple) - PostgreSQL로 직접 변환 가능
- **1-3**: 간단 (Simple) - 약간의 수정만 필요
- **3-5**: 중간 (Moderate) - 일부 재작성 필요
- **5-7**: 복잡 (Complex) - 상당한 재작성 필요
- **7-9**: 매우 복잡 (Very Complex) - 대부분 재작성 필요
- **9-10**: 극도로 복잡 (Extremely Complex) - 완전한 재설계 필요

### 세부 평가 요소

각 세부 평가 요소는 특정 측면의 복잡도를 나타냅니다:

- **structural_complexity**: 쿼리의 구조적 복잡성
- **oracle_specific_features**: Oracle 특화 기능 사용 정도
- **functions_expressions**: 함수 및 표현식 복잡도
- **data_volume**: 데이터 처리 볼륨 추정
- **execution_complexity**: 실행 계획 복잡성 추정
- **postgres_conversion**: PostgreSQL 변환 난이도
- **dynamic_complexity**: MyBatis 동적 쿼리 복잡도 (MyBatis 쿼리만 해당)

### 보고서 형식

생성된 마크다운 보고서는 다음 정보를 포함합니다:

1. **요약 정보**
   - 분석된 파일 수
   - MyBatis 동적 쿼리 및 일반 SQL 쿼리 수
   - 복잡도 분포

2. **파일별 상세 분석**
   - 복잡도 점수 및 설명
   - 쿼리 유형 (MyBatis 또는 일반 SQL)
   - 세부 평가 요소 점수

## 문제 해결

### 일반적인 오류

1. **모듈을 찾을 수 없음**
   - 문제: `ModuleNotFoundError: No module named 'xxx'`
   - 해결: 프로젝트 루트 디렉토리에서 실행하거나, 직접 파일 경로를 사용하여 실행하세요.
   ```bash
   python src/query_complexity_analyzer.py
   ```

2. **XML 파싱 오류**
   - 문제: `ET.ParseError: not well-formed (invalid token)`
   - 해결: XML 형식이 올바른지 확인하세요. 특히 `<`, `>` 문자가 제대로 이스케이프되었는지 확인하세요.

3. **sqlparse 오류**
   - 문제: `ImportError: No module named 'sqlparse'`
   - 해결: `pip install sqlparse` 명령으로 필요한 라이브러리를 설치하세요.

4. **파일 권한 오류**
   - 문제: `PermissionError: [Errno 13] Permission denied`
   - 해결: 출력 파일을 저장할 디렉토리에 쓰기 권한이 있는지 확인하세요.

### 지원 및 문의

문제가 계속되면 GitHub 이슈를 통해 문의하세요: https://github.com/sqlpro/oracle-query-complexity-analyzer/issues
