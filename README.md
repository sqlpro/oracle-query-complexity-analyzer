# Oracle to PostgreSQL Query Analyzer

Oracle SQL 쿼리와 MyBatis 동적 쿼리의 복잡도를 분석하여 Oracle에서 PostgreSQL로의 마이그레이션 계획을 지원하는 도구입니다.

## 개요

이 프로젝트는 Oracle 데이터베이스에서 PostgreSQL(특히 Aurora PostgreSQL)로의 마이그레이션 과정에서 쿼리 변환 작업의 복잡도를 평가하기 위한 도구를 제공합니다. 일반 SQL 쿼리와 MyBatis 동적 쿼리 모두를 분석할 수 있으며, 0-10 척도의 복잡도 점수와 세부 평가 요소를 제공합니다.

## 빠른 시작

### 필수 요구사항

- Python 3.6 이상
- make (선택 사항, 편의를 위한 명령어 제공)

### 설치 및 실행

```bash
# 저장소 클론
git clone https://github.com/yourusername/oracle-to-postgres-analyzer.git
cd oracle-to-postgres-analyzer

# 필요한 패키지 설치 (자동으로 python/python3 감지)
make install

# 특정 Python 버전 지정
make install PYTHON_CMD=python3.9 PIP_CMD=pip3.9

# 또는 pip를 직접 사용
pip install -e .
```

### 사용 방법

#### Makefile을 사용한 실행

```bash
# 도움말 보기 (현재 사용 중인 Python/pip 버전 확인 가능)
make help

# 일반 SQL 쿼리 분석
make run-sql

# 특정 Python 버전으로 실행
make run-sql PYTHON_CMD=python3.9

# MyBatis 동적 쿼리 분석
make run-mybatis

# 디렉토리 내 모든 SQL 파일 분석
make run-dir ARGS='/path/to/sql/files output_report.md'

# 샘플 파일 분석
make analyze-samples
```

#### 직접 실행

```bash
# 일반 SQL 쿼리 분석
python -m oracle_to_postgres_analyzer.src.query_complexity_analyzer

# MyBatis 동적 쿼리 분석
python -m oracle_to_postgres_analyzer.src.mybatis_query_analyzer

# 디렉토리 내 모든 SQL 파일 분석
python -m oracle_to_postgres_analyzer.src.sql_directory_analyzer /path/to/sql/files output_report.md
```

## 주요 기능

- Oracle SQL 쿼리의 복잡도 분석
- MyBatis 동적 쿼리 분석
- 디렉토리 내 모든 SQL 파일 일괄 분석
- 복잡도 보고서 생성

## 복잡도 평가 요소

쿼리 복잡도는 다음 요소를 기반으로 평가됩니다:

1. **구조적 복잡성**
   - 테이블 조인 수
   - 서브쿼리 중첩 깊이
   - WITH 절(CTE) 사용
   - UNION/INTERSECT/MINUS 연산자 사용

2. **Oracle 특화 기능**
   - CONNECT BY 계층적 쿼리
   - 분석 함수(OVER, PARTITION BY 등)
   - PIVOT/UNPIVOT
   - MODEL 절

3. **함수 및 표현식**
   - 집계 함수 사용
   - 사용자 정의 함수 호출
   - CASE 표현식 복잡도
   - 정규식 및 문자열 처리

4. **데이터 처리 볼륨**
   - 쿼리 길이 및 복잡성

5. **실행 계획 복잡성**
   - 조인 및 서브쿼리 구조
   - 정렬 및 그룹화

6. **PostgreSQL 변환 난이도**
   - Oracle 특화 문법 사용 정도
   - PostgreSQL에서 직접 대체 불가능한 기능

7. **동적 쿼리 복잡도** (MyBatis 쿼리만 해당)
   - 동적 태그 수
   - 태그 중첩 깊이
   - 특정 복잡한 태그(foreach, choose 등) 사용

## 복잡도 레벨

- **0-1**: 매우 간단 (Very Simple)
- **1-3**: 간단 (Simple)
- **3-5**: 중간 (Moderate)
- **5-7**: 복잡 (Complex)
- **7-9**: 매우 복잡 (Very Complex)
- **9-10**: 극도로 복잡 (Extremely Complex)

## 프로젝트 구조

```
oracle_to_postgres_analyzer/
├── Makefile                   # 빠른 실행을 위한 명령어 모음
├── README.md                  # 프로젝트 개요 및 사용 방법
├── setup.py                   # 패키지 설치 설정
├── src/                       # 소스 코드 디렉토리
│   ├── __init__.py            # 패키지 초기화 파일
│   ├── query_complexity_analyzer.py  # 일반 SQL 쿼리 분석기
│   ├── mybatis_query_analyzer.py     # MyBatis 동적 쿼리 분석기
│   └── sql_directory_analyzer.py     # 디렉토리 분석 도구
├── samples/                   # 샘플 SQL 파일
│   ├── sample_01.sql          # 기본 MyBatis 동적 쿼리 샘플
│   ├── sample_02.sql          # 일반 Oracle SQL 쿼리 샘플
│   └── complex_mybatis_query.sql  # 복잡한 MyBatis 동적 쿼리 샘플
└── docs/                      # 문서
    ├── usage_guide.md         # 상세 사용 가이드
    └── migration_guide.md     # Oracle에서 PostgreSQL로의 마이그레이션 가이드
```

## 샘플 분석 예시

```bash
# 샘플 파일 분석
make analyze-samples
```

이 명령어는 `samples` 디렉토리의 모든 SQL 파일을 분석하고 `output/sample_analysis.md` 파일에 결과를 저장합니다.

## 상세 문서

더 자세한 정보는 다음 문서를 참조하세요:

- [사용 가이드](docs/usage_guide.md)
- [마이그레이션 가이드](docs/migration_guide.md)

## 기여

이슈와 풀 리퀘스트는 환영합니다. 대규모 변경사항은 먼저 이슈를 열어 논의해주세요.

## 라이선스

MIT
