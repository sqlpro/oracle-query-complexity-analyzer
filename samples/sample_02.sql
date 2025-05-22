-- 일반 Oracle SQL 쿼리 샘플
-- 파일명: sample_02.sql
-- 설명: 부서별 직원 급여 통계 분석 쿼리

WITH dept_stats AS (
    SELECT 
        department_id,
        AVG(salary) as avg_salary,
        MAX(salary) as max_salary,
        MIN(salary) as min_salary,
        COUNT(*) as emp_count,
        STDDEV(salary) as salary_stddev
    FROM employees
    WHERE hire_date > TO_DATE('2010-01-01', 'YYYY-MM-DD')
    GROUP BY department_id
),
ranked_employees AS (
    SELECT 
        e.employee_id,
        e.first_name,
        e.last_name,
        e.department_id,
        e.salary,
        d.department_name,
        RANK() OVER (PARTITION BY e.department_id ORDER BY e.salary DESC) as salary_rank,
        ROW_NUMBER() OVER (PARTITION BY e.department_id ORDER BY e.hire_date) as seniority
    FROM employees e
    JOIN departments d ON e.department_id = d.department_id
    WHERE e.active_flag = 'Y'
)
SELECT 
    r.employee_id,
    r.first_name || ' ' || r.last_name as employee_name,
    r.department_name,
    r.salary,
    r.salary_rank,
    r.seniority,
    ds.avg_salary,
    ds.max_salary,
    ds.min_salary,
    ds.emp_count,
    ds.salary_stddev,
    CASE 
        WHEN r.salary > ds.avg_salary * 1.5 THEN 'High'
        WHEN r.salary < ds.avg_salary * 0.8 THEN 'Low'
        ELSE 'Average'
    END as salary_category,
    DECODE(r.salary_rank, 1, 'Top Earner', 'Regular') as earner_status,
    ROUND((r.salary - ds.avg_salary) / ds.salary_stddev, 2) as z_score
FROM ranked_employees r
JOIN dept_stats ds ON r.department_id = ds.department_id
WHERE r.salary_rank <= 5
ORDER BY r.department_id, r.salary_rank
