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
# pip를 사용한 설치
pip install oracle-to-postgres-analyzer

# 또는 소스에서 직접 설치
git clone https://github.com/yourusername/oracle-to-postgres-analyzer.git
cd oracle-to-postgres-analyzer
pip install -e .
```

## 기본 사용법

### 1. 단일 SQL 쿼리 분석

```bash
# 명령줄에서 직접 실행
analyze-sql

# 또는 모듈로 실행
python -m oracle_to_postgres_analyzer.src.query_complexity_analyzer
```

실행 후 프롬프트에 분석할 SQL 쿼리를 입력하세요. 입력을 마치려면 빈 줄에서 Ctrl+D(Unix) 또는 Ctrl+Z(Windows)를 누르세요.

### 2. MyBatis 동적 쿼리 분석

```bash
# 명령줄에서 직접 실행
analyze-mybatis

# 또는 모듈로 실행
python -m oracle_to_postgres_analyzer.src.mybatis_query_analyzer
```

실행 후 프롬프트에 분석할 MyBatis XML 쿼리를 입력하세요.

### 3. 디렉토리 내 모든 SQL 파일 분석

```bash
# 명령줄에서 직접 실행
analyze-sql-dir /path/to/sql/files output_report.md

# 또는 모듈로 실행
python -m oracle_to_postgres_analyzer.src.sql_directory_analyzer /path/to/sql/files output_report.md
```

## 고급 사용법

### Python 코드에서 사용하기

```python
from oracle_to_postgres_analyzer.src.query_complexity_analyzer import analyze_query
from oracle_to_postgres_analyzer.src.mybatis_query_analyzer import analyze_query as analyze_mybatis_query

# 일반 SQL 쿼리 분석
with open('query.sql', 'r') as f:
    sql_query = f.read()
    
score, description, details = analyze_query(sql_query)
print(f"복잡도: {score}/10 - {description}")

# MyBatis 동적 쿼리 분석
with open('mybatis_query.xml', 'r') as f:
    xml_query = f.read()
    
score, description, details = analyze_mybatis_query(xml_query, is_mybatis_xml=True)
print(f"복잡도: {score}/10 - {description}")
```

### 대규모 프로젝트 분석

대규모 프로젝트에서는 다음과 같이 사용할 수 있습니다:

```bash
# 모든 SQL 파일 분석 및 보고서 생성
analyze-sql-dir /path/to/project/sql output_report.md

# 특정 패턴의 파일만 분석 (쉘 스크립트 사용)
find /path/to/project -name "*.sql" | grep "oracle" > oracle_files.txt
for file in $(cat oracle_files.txt); do
    analyze-sql-dir $(dirname $file) $(basename $file)_report.md
done
```

## 결과 해석

### 복잡도 점수

복잡도 점수는 0-10 척도로 표시되며, 다음과 같이 해석할 수 있습니다:

- **0-1**: 매우 간단 - PostgreSQL로 직접 변환 가능
- **1-3**: 간단 - 약간의 수정만 필요
- **3-5**: 중간 - 일부 재작성 필요
- **5-7**: 복잡 - 상당한 재작성 필요
- **7-9**: 매우 복잡 - 대부분 재작성 필요
- **9-10**: 극도로 복잡 - 완전한 재설계 필요

### 세부 평가 요소

각 세부 평가 요소는 특정 측면의 복잡도를 나타냅니다:

- **structural_complexity**: 쿼리의 구조적 복잡성
- **oracle_specific_features**: Oracle 특화 기능 사용 정도
- **functions_expressions**: 함수 및 표현식 복잡도
- **data_volume**: 데이터 처리 볼륨 추정
- **execution_complexity**: 실행 계획 복잡성 추정
- **postgres_conversion**: PostgreSQL 변환 난이도
- **dynamic_complexity**: MyBatis 동적 쿼리 복잡도 (MyBatis 쿼리만 해당)

## 문제 해결

### 일반적인 오류

1. **XML 파싱 오류**
   - 문제: `ET.ParseError: not well-formed (invalid token)`
   - 해결: XML 형식이 올바른지 확인하세요. 특히 `<`, `>` 문자가 제대로 이스케이프되었는지 확인하세요.

2. **모듈을 찾을 수 없음**
   - 문제: `ModuleNotFoundError: No module named 'oracle_to_postgres_analyzer'`
   - 해결: 패키지가 올바르게 설치되었는지 확인하거나, 프로젝트 루트 디렉토리에서 실행하세요.

3. **sqlparse 오류**
   - 문제: `ImportError: No module named 'sqlparse'`
   - 해결: `pip install sqlparse` 명령으로 필요한 라이브러리를 설치하세요.

### 지원 및 문의

문제가 계속되면 GitHub 이슈를 통해 문의하세요: https://github.com/yourusername/oracle-to-postgres-analyzer/issues
