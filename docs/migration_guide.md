# Oracle에서 PostgreSQL로의 마이그레이션 가이드

이 문서는 Oracle 데이터베이스에서 PostgreSQL(특히 Aurora PostgreSQL)로 마이그레이션하는 과정에서 쿼리 변환에 초점을 맞춘 가이드입니다.

## 목차

1. [마이그레이션 개요](#마이그레이션-개요)
2. [쿼리 복잡도에 따른 접근 방식](#쿼리-복잡도에-따른-접근-방식)
3. [Oracle 특화 기능 대체 방법](#oracle-특화-기능-대체-방법)
4. [MyBatis 동적 쿼리 변환 전략](#mybatis-동적-쿼리-변환-전략)
5. [성능 최적화 고려사항](#성능-최적화-고려사항)

## 마이그레이션 개요

Oracle에서 PostgreSQL로의 마이그레이션은 다음 단계로 진행됩니다:

1. **평가 및 계획**
   - 데이터베이스 크기 및 복잡도 평가
   - 쿼리 복잡도 분석 (본 도구 사용)
   - 마이그레이션 전략 및 일정 수립

2. **스키마 변환**
   - 테이블, 뷰, 인덱스 등의 구조 변환
   - 데이터 타입 매핑
   - 제약 조건 변환

3. **쿼리 변환**
   - SQL 문법 차이 해결
   - Oracle 특화 기능 대체
   - 성능 최적화

4. **데이터 마이그레이션**
   - 초기 데이터 로드
   - 변경 데이터 캡처 및 동기화
   - 데이터 검증

5. **테스트 및 최적화**
   - 기능 테스트
   - 성능 테스트
   - 튜닝 및 최적화

6. **전환 및 운영**
   - 최종 전환
   - 모니터링 및 문제 해결
   - 운영 안정화

## 쿼리 복잡도에 따른 접근 방식

Oracle to PostgreSQL Query Analyzer의 복잡도 점수에 따라 다음과 같은 접근 방식을 권장합니다:

### 매우 간단 (0-1)
- 직접 변환 가능
- 기본 문법 차이만 수정 (예: NVL → COALESCE)
- 자동화 도구로 변환 가능

### 간단 (1-3)
- 약간의 수정 필요
- 일부 함수 대체 필요
- 대부분 자동화 도구로 변환 가능

### 중간 (3-5)
- 일부 재작성 필요
- Oracle 특화 기능 대체 필요
- 자동화 + 수동 검토 필요

### 복잡 (5-7)
- 상당한 재작성 필요
- 복잡한 기능 대체 및 로직 수정
- 주로 수동 변환 필요

### 매우 복잡 (7-9)
- 대부분 재작성 필요
- 깊은 Oracle 의존성 해결 필요
- 전문가 검토 필수

### 극도로 복잡 (9-10)
- 완전한 재설계 필요
- 비즈니스 로직 재검토
- 새로운 접근 방식 고려

## Oracle 특화 기능 대체 방법

### 1. ROWNUM
Oracle:
```sql
SELECT * FROM employees WHERE ROWNUM <= 10;
```

PostgreSQL:
```sql
SELECT * FROM employees LIMIT 10;
```

### 2. CONNECT BY
Oracle:
```sql
SELECT employee_id, manager_id, level
FROM employees
START WITH manager_id IS NULL
CONNECT BY PRIOR employee_id = manager_id;
```

PostgreSQL:
```sql
WITH RECURSIVE emp_hierarchy AS (
  SELECT employee_id, manager_id, 1 as level
  FROM employees
  WHERE manager_id IS NULL
  UNION ALL
  SELECT e.employee_id, e.manager_id, eh.level + 1
  FROM employees e
  JOIN emp_hierarchy eh ON e.manager_id = eh.employee_id
)
SELECT * FROM emp_hierarchy;
```

### 3. DECODE
Oracle:
```sql
SELECT DECODE(status, 'A', 'Active', 'I', 'Inactive', 'Unknown') FROM orders;
```

PostgreSQL:
```sql
SELECT CASE status WHEN 'A' THEN 'Active' WHEN 'I' THEN 'Inactive' ELSE 'Unknown' END FROM orders;
```

### 4. NVL / NVL2
Oracle:
```sql
SELECT NVL(commission, 0), NVL2(commission, 'Has Commission', 'No Commission') FROM employees;
```

PostgreSQL:
```sql
SELECT COALESCE(commission, 0), 
       CASE WHEN commission IS NOT NULL THEN 'Has Commission' ELSE 'No Commission' END 
FROM employees;
```

### 5. PIVOT
Oracle:
```sql
SELECT * FROM (
  SELECT product, category, amount FROM sales
)
PIVOT (
  SUM(amount) FOR category IN ('Electronics', 'Clothing', 'Food')
);
```

PostgreSQL:
```sql
SELECT product,
       SUM(CASE WHEN category = 'Electronics' THEN amount ELSE 0 END) as "Electronics",
       SUM(CASE WHEN category = 'Clothing' THEN amount ELSE 0 END) as "Clothing",
       SUM(CASE WHEN category = 'Food' THEN amount ELSE 0 END) as "Food"
FROM sales
GROUP BY product;
```

## MyBatis 동적 쿼리 변환 전략

MyBatis 동적 쿼리 변환 시 고려해야 할 사항:

1. **기본 SQL 변환**
   - 기본 SQL 문을 PostgreSQL 문법으로 변환
   - Oracle 특화 기능 대체

2. **동적 태그 처리**
   - 대부분의 MyBatis 동적 태그는 그대로 사용 가능
   - `<if>`, `<choose>`, `<when>`, `<otherwise>`, `<foreach>` 등

3. **Oracle 특화 함수 대체**
   - 동적 태그 내의 Oracle 함수를 PostgreSQL 함수로 대체
   - 예: `TO_DATE` → `TO_DATE` 또는 `TO_TIMESTAMP`

4. **페이지네이션 변경**
   - ROWNUM 기반 페이지네이션을 LIMIT/OFFSET으로 변경

5. **날짜 함수 처리**
   - Oracle 날짜 함수를 PostgreSQL 호환 함수로 변경
   - 날짜 형식 문자열 차이 고려

## 성능 최적화 고려사항

PostgreSQL로 마이그레이션 후 성능 최적화를 위한 고려사항:

1. **인덱스 전략**
   - Oracle과 PostgreSQL의 인덱스 동작 차이 이해
   - 적절한 인덱스 재설계

2. **실행 계획 분석**
   - `EXPLAIN ANALYZE`를 사용한 쿼리 실행 계획 분석
   - 병목 지점 식별 및 최적화

3. **파티셔닝**
   - PostgreSQL의 파티셔닝 기능 활용
   - 대용량 테이블 성능 최적화

4. **통계 정보 관리**
   - 정기적인 `ANALYZE` 실행
   - 통계 정보 최신 상태 유지

5. **쿼리 재작성**
   - PostgreSQL에 최적화된 쿼리 패턴 적용
   - 공통 테이블 표현식(CTE) 활용

6. **연결 풀링**
   - 효율적인 연결 관리
   - 적절한 풀 크기 설정
