# Oracle to PostgreSQL 쿼리 복잡도 계산 공식

이 문서는 Oracle SQL 쿼리와 MyBatis 동적 쿼리의 복잡도를 계산하는 수식과 알고리즘을 설명합니다.

## 목차

1. [복잡도 점수 개요](#복잡도-점수-개요)
2. [일반 SQL 쿼리 복잡도 계산](#일반-sql-쿼리-복잡도-계산)
3. [MyBatis 동적 쿼리 복잡도 계산](#mybatis-동적-쿼리-복잡도-계산)
4. [복잡도 레벨 분류](#복잡도-레벨-분류)
5. [계산 예시](#계산-예시)

## 복잡도 점수 개요

복잡도 점수는 0-10 척도로 표현되며, 다양한 요소를 고려하여 계산됩니다. 점수가 높을수록 Oracle에서 PostgreSQL로의 변환이 더 복잡하고 어렵다는 것을 의미합니다.

## 일반 SQL 쿼리 복잡도 계산

일반 SQL 쿼리의 복잡도는 다음 6가지 카테고리의 점수를 합산하여 계산됩니다:

### 1. 구조적 복잡성 (Structural Complexity)

최대 점수: 3.5점

계산 공식:
```
structural_complexity = join_score + subquery_score + cte_score + set_operators_score
```

각 요소의 점수:
- **join_score**: 조인 수에 따른 점수
  - 0개: 0점
  - 1-2개: 1점
  - 3-4개: 2점
  - 5개 이상: 3점

- **subquery_score**: 서브쿼리 중첩 깊이에 따른 점수
  - 0단계: 0점
  - 1단계: 1점
  - 2단계: 2점
  - 3단계 이상: 3점 + min(2, 깊이-2)

- **cte_score**: WITH 절(CTE) 사용 수에 따른 점수
  - min(2, cte_count)

- **set_operators_score**: UNION/INTERSECT/MINUS 연산자 사용에 따른 점수
  - min(2, set_operators_count)

### 2. Oracle 특화 기능 (Oracle-Specific Features)

최대 점수: 3.0점

계산 공식:
```
oracle_specific_features = connect_by_score + analytic_functions_score + pivot_score + model_score
```

각 요소의 점수:
- **connect_by_score**: CONNECT BY 계층적 쿼리 사용 시 2점
- **analytic_functions_score**: 분석 함수 사용 수에 따른 점수
  - min(3, analytic_functions_count)
- **pivot_score**: PIVOT/UNPIVOT 사용 시 2점
- **model_score**: MODEL 절 사용 시 3점

### 3. 함수 및 표현식 (Functions & Expressions)

최대 점수: 2.0점

계산 공식:
```
functions_expressions = agg_functions_score + udf_score + case_score + regexp_score
```

각 요소의 점수:
- **agg_functions_score**: 집계 함수 사용 수에 따른 점수
  - min(2, agg_functions_count * 0.5)
- **udf_score**: 사용자 정의 함수 호출 추정 점수
  - min(2, max(0, potential_udf * 0.5))
- **case_score**: CASE 표현식 복잡도에 따른 점수
  - min(2, case_count * 0.5)
- **regexp_score**: 정규식 및 복잡한 문자열 처리 사용 시 1점

### 4. 데이터 처리 볼륨 (Data Volume)

최대 점수: 2.0점

계산 공식:
```
data_volume = query_length_score
```

쿼리 길이에 따른 점수:
- 200자 미만: 0.5점
- 200-499자: 1.0점
- 500-999자: 1.5점
- 1000자 이상: 2.0점

### 5. 실행 계획 복잡성 (Execution Complexity)

최대 점수: 1.5점

계산 공식:
```
execution_complexity = join_depth_score + order_by_score + group_by_score + having_score
```

각 요소의 점수:
- **join_depth_score**: 조인 수가 3개 초과 또는 서브쿼리 깊이가 1 초과 시 1점
- **order_by_score**: ORDER BY 사용 시 0.5점
- **group_by_score**: GROUP BY 사용 시 0.5점
- **having_score**: HAVING 사용 시 0.5점

### 6. PostgreSQL 변환 난이도 (PostgreSQL Conversion)

최대 점수: 2.0점

계산 공식:
```
postgres_conversion = oracle_specific_syntax_score + oracle_functions_score
```

각 요소의 점수:
- **oracle_specific_syntax_score**: Oracle 특화 문법 사용 시 각 1점
  - CONNECT BY, START WITH, PRIOR, MODEL, PIVOT/UNPIVOT, FLASHBACK, SYS_CONNECT_BY_PATH, ROWID, ROWNUM
- **oracle_functions_score**: Oracle 특화 함수 사용 시 각 0.5점
  - DECODE, NVL2, LISTAGG, REGEXP_, SYS_CONTEXT, EXTRACT 등

### 최종 복잡도 점수 계산

각 카테고리의 점수는 최대값으로 제한되며, 최종 복잡도 점수는 다음과 같이 계산됩니다:

```
total_score = sum(각 카테고리 점수)
max_possible_score = sum(각 카테고리 최대 점수) = 14.0
normalized_score = min(10, total_score * 10 / max_possible_score)
```

최종 복잡도 점수는 0-10 척도로 정규화되며, 소수점 첫째 자리까지 반올림됩니다.

## MyBatis 동적 쿼리 복잡도 계산

MyBatis 동적 쿼리의 복잡도는 일반 SQL 복잡도와 동적 쿼리 복잡도를 결합하여 계산됩니다.

### 동적 쿼리 복잡도 (Dynamic Complexity)

최대 점수: 3.0점

계산 공식:
```
dynamic_complexity = tags_count_score + nesting_depth_score + special_tags_score
```

각 요소의 점수:
- **tags_count_score**: 동적 태그 수에 따른 점수
  - 0-2개: 0.5점
  - 3-5개: 1.0점
  - 6-10개: 1.5점
  - 11개 이상: 2.0점

- **nesting_depth_score**: 태그 중첩 깊이에 따른 점수
  - 1단계: 0.3점
  - 2단계: 0.7점
  - 3단계: 1.2점
  - 4단계 이상: 2.0점

- **special_tags_score**: 특수 태그 사용에 따른 점수
  - foreach 태그: min(1.0, foreach_count * 0.3)
  - choose 태그: min(0.8, choose_count * 0.2)

### 최종 MyBatis 쿼리 복잡도 계산

MyBatis 쿼리의 최종 복잡도는 다음과 같이 계산됩니다:

```
base_sql_complexity = 기본 SQL의 복잡도 점수
max_sql_complexity = 최대 복잡도 SQL의 복잡도 점수
final_complexity = min(10, max_sql_complexity + (dynamic_complexity * 0.5))
```

여기서:
- **기본 SQL**: 동적 태그를 제외한 기본 SQL 문
- **최대 복잡도 SQL**: 모든 동적 태그의 내용을 포함한 SQL 문
- **동적 복잡도**: 동적 태그의 수, 중첩 깊이, 특수 태그 사용에 따른 복잡도

## 복잡도 레벨 분류

계산된 복잡도 점수는 다음과 같이 레벨로 분류됩니다:

| 점수 범위 | 복잡도 레벨 | 설명 |
|----------|------------|------|
| 0-1      | 매우 간단 (Very Simple) | PostgreSQL로 직접 변환 가능 |
| 1-3      | 간단 (Simple) | 약간의 수정만 필요 |
| 3-5      | 중간 (Moderate) | 일부 재작성 필요 |
| 5-7      | 복잡 (Complex) | 상당한 재작성 필요 |
| 7-9      | 매우 복잡 (Very Complex) | 대부분 재작성 필요 |
| 9-10     | 극도로 복잡 (Extremely Complex) | 완전한 재설계 필요 |

## 계산 예시

### 예시 1: 간단한 SQL 쿼리

```sql
SELECT employee_id, first_name, last_name
FROM employees
WHERE department_id = 10
```

복잡도 계산:
- 구조적 복잡성: 0점 (조인 없음, 서브쿼리 없음)
- Oracle 특화 기능: 0점 (특화 기능 없음)
- 함수 및 표현식: 0점 (함수 없음)
- 데이터 처리 볼륨: 0.5점 (짧은 쿼리)
- 실행 계획 복잡성: 0점 (단순 쿼리)
- PostgreSQL 변환 난이도: 0점 (변환 필요 없음)

총점: 0.5점
정규화 점수: 0.5 * 10 / 14 = 0.36 → 0.4점 (매우 간단)

### 예시 2: 복잡한 SQL 쿼리

```sql
WITH dept_stats AS (
    SELECT department_id, AVG(salary) as avg_salary
    FROM employees
    GROUP BY department_id
)
SELECT e.employee_id, e.first_name, e.last_name,
       RANK() OVER (PARTITION BY e.department_id ORDER BY e.salary DESC) as salary_rank,
       CASE WHEN e.salary > ds.avg_salary THEN 'Above Average' ELSE 'Below Average' END as status
FROM employees e
JOIN departments d ON e.department_id = d.department_id
JOIN dept_stats ds ON e.department_id = ds.department_id
WHERE ROWNUM <= 100
ORDER BY e.department_id, salary_rank
```

복잡도 계산:
- 구조적 복잡성: 3점 (2개 조인, CTE 사용)
- Oracle 특화 기능: 1점 (분석 함수 사용)
- 함수 및 표현식: 1점 (CASE 표현식, 집계 함수)
- 데이터 처리 볼륨: 1점 (중간 길이 쿼리)
- 실행 계획 복잡성: 1.5점 (조인, ORDER BY, GROUP BY)
- PostgreSQL 변환 난이도: 1점 (ROWNUM 사용)

총점: 8.5점
정규화 점수: 8.5 * 10 / 14 = 6.07 → 6.1점 (복잡)
