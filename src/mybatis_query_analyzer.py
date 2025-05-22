#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Oracle 쿼리 복잡도 분석기 (MyBatis 동적 쿼리 지원)
Oracle SQL 쿼리와 MyBatis 동적 쿼리의 복잡도를 0-10 척도로 평가하는 도구
"""

import xml.etree.ElementTree as ET

# 기존 SQL 복잡도 분석 함수 가져오기
try:
    # 패키지로 설치된 경우
    from .query_complexity_analyzer import calculate_query_complexity, get_complexity_description
except ImportError:
    # 직접 실행하는 경우
    from query_complexity_analyzer import calculate_query_complexity, get_complexity_description

def analyze_mybatis_dynamic_query(xml_content):
    """
    MyBatis XML에서 동적 쿼리의 복잡도를 분석
    
    Args:
        xml_content (str): MyBatis XML 내용
        
    Returns:
        tuple: (기본 SQL, 동적 복잡도 점수, 최대 복잡도 SQL 추정)
    """
    try:
        # XML 파싱
        root = ET.fromstring(xml_content)
    except ET.ParseError:
        # XML 파싱 오류 처리
        return "", 0, ""
    
    # 동적 태그 카운트
    dynamic_tags = {
        'if': 0,
        'choose': 0,
        'when': 0,
        'otherwise': 0,
        'foreach': 0,
        'where': 0,
        'set': 0,
        'trim': 0,
        'bind': 0
    }
    
    # 기본 SQL 추출 (동적 태그 제외)
    base_sql = ""
    max_complexity_sql = ""
    
    # 동적 태그 중첩 깊이
    max_nesting_depth = 0
    
    # 동적 태그 분석 함수
    def analyze_element(element, depth=0):
        nonlocal max_nesting_depth
        nonlocal base_sql
        nonlocal max_complexity_sql
        
        # 현재 깊이가 최대 깊이보다 크면 업데이트
        max_nesting_depth = max(max_nesting_depth, depth)
        
        # 태그 이름 (네임스페이스 제거)
        tag = element.tag
        if '}' in tag:
            tag = tag.split('}', 1)[1]
        
        # 동적 태그 카운트 증가
        if tag in dynamic_tags:
            dynamic_tags[tag] += 1
        
        # 텍스트 내용 처리
        if element.text and element.text.strip():
            text = element.text.strip()
            base_sql += " " + text
            max_complexity_sql += " " + text
        
        # 자식 요소 처리
        for child in element:
            child_tag = child.tag
            if '}' in child_tag:
                child_tag = child_tag.split('}', 1)[1]
            
            # 동적 태그인 경우
            if child_tag in dynamic_tags:
                # 기본 SQL에는 포함하지 않음
                # 최대 복잡도 SQL에는 내용 포함
                if child.text and child.text.strip():
                    max_complexity_sql += " " + child.text.strip()
                
                # 자식 요소 재귀 처리
                analyze_element(child, depth + 1)
            else:
                # 일반 태그인 경우 양쪽 모두에 포함
                analyze_element(child, depth)
        
        # 꼬리 텍스트 처리
        if element.tail and element.tail.strip():
            tail = element.tail.strip()
            base_sql += " " + tail
            max_complexity_sql += " " + tail
    
    # 루트 요소부터 분석 시작
    analyze_element(root)
    
    # 동적 쿼리 복잡도 점수 계산
    dynamic_complexity = 0
    
    # 1. 동적 태그 수에 따른 복잡도
    total_dynamic_tags = sum(dynamic_tags.values())
    if total_dynamic_tags <= 2:
        dynamic_complexity += 0.5
    elif total_dynamic_tags <= 5:
        dynamic_complexity += 1.0
    elif total_dynamic_tags <= 10:
        dynamic_complexity += 1.5
    else:
        dynamic_complexity += 2.0
    
    # 2. 중첩 깊이에 따른 복잡도
    if max_nesting_depth == 1:
        dynamic_complexity += 0.3
    elif max_nesting_depth == 2:
        dynamic_complexity += 0.7
    elif max_nesting_depth == 3:
        dynamic_complexity += 1.2
    else:
        dynamic_complexity += 2.0
    
    # 3. 특정 복잡한 태그 사용에 따른 추가 복잡도
    if dynamic_tags['foreach'] > 0:
        dynamic_complexity += min(1.0, dynamic_tags['foreach'] * 0.3)
    
    if dynamic_tags['choose'] > 0:
        dynamic_complexity += min(0.8, dynamic_tags['choose'] * 0.2)
    
    # 최대 3.0으로 제한
    dynamic_complexity = min(3.0, dynamic_complexity)
    
    return base_sql.strip(), dynamic_complexity, max_complexity_sql.strip()

def analyze_mybatis_query(xml_content):
    """
    MyBatis XML 쿼리를 분석하고 복잡도 결과를 계산
    
    Args:
        xml_content (str): MyBatis XML 쿼리 내용
        
    Returns:
        dict: 복잡도 분석 결과
    """
    # 동적 쿼리 분석
    base_sql, dynamic_complexity, max_complexity_sql = analyze_mybatis_dynamic_query(xml_content)
    
    # 기본 SQL과 최대 복잡도 SQL의 복잡도 계산
    try:
        base_complexity, base_scores = calculate_query_complexity(base_sql)
    except:
        base_complexity, base_scores = 0, {}
    
    try:
        max_complexity, max_scores = calculate_query_complexity(max_complexity_sql)
    except:
        max_complexity, max_scores = 0, {}
    
    # 동적 복잡도 점수 추가
    if 'dynamic_complexity' not in max_scores:
        max_scores['dynamic_complexity'] = dynamic_complexity
    
    # 최종 복잡도 계산 (최대 복잡도 SQL + 동적 복잡도)
    final_complexity = min(10, max_complexity + (dynamic_complexity * 0.5))
    
    return {
        'base_sql': base_sql,
        'max_complexity_sql': max_complexity_sql,
        'base_complexity': base_complexity,
        'max_complexity': max_complexity,
        'dynamic_complexity': dynamic_complexity,
        'final_complexity': round(final_complexity, 1),
        'detailed_scores': max_scores
    }

def analyze_query(query, is_mybatis_xml=False):
    """
    쿼리를 분석하고 복잡도 결과를 출력
    
    Args:
        query (str): 분석할 SQL 쿼리 또는 MyBatis XML
        is_mybatis_xml (bool): MyBatis XML 형식 여부
        
    Returns:
        tuple: (복잡도 점수, 복잡도 설명, 세부 점수 딕셔너리)
    """
    if is_mybatis_xml:
        result = analyze_mybatis_query(query)
        complexity_score = result['final_complexity']
        description = get_complexity_description(complexity_score)
        detailed_scores = result['detailed_scores']
        
        print(f"쿼리 복잡도 점수: {complexity_score}/10 - {description}")
        print(f"기본 SQL 복잡도: {result['base_complexity']}/10")
        print(f"동적 쿼리 복잡도: {result['dynamic_complexity']}/3.0")
        print("\n세부 평가 요소:")
        for category, score in detailed_scores.items():
            print(f"- {category}: {score}")
        
        return complexity_score, description, detailed_scores
    else:
        complexity_score, detailed_scores = calculate_query_complexity(query)
        description = get_complexity_description(complexity_score)
        
        print(f"쿼리 복잡도 점수: {complexity_score}/10 - {description}")
        print("\n세부 평가 요소:")
        for category, score in detailed_scores.items():
            print(f"- {category}: {score}")
        
        return complexity_score, description, detailed_scores

def main():
    """
    메인 함수: 사용자 입력에 따라 분석 수행
    """
    print("Oracle 쿼리 복잡도 분석기 (MyBatis 동적 쿼리 지원)")
    print("1. 일반 SQL 쿼리 분석")
    print("2. MyBatis XML 쿼리 분석")
    
    choice = input("선택하세요 (1-2): ")
    
    if choice == '1':
        print("SQL 쿼리를 입력하세요 (입력 종료는 빈 줄에서 Ctrl+D 또는 Ctrl+Z):")
        lines = []
        try:
            while True:
                line = input()
                lines.append(line)
        except EOFError:
            pass
        
        query = "\n".join(lines)
        if query.strip():
            complexity_score, description, detailed_scores = analyze_query(query)
            
            # 결과를 파일로 저장할지 물어봄
            user_input = input("\n분석 결과를 파일로 저장하시겠습니까? (y/n): ").strip().lower()
            if user_input == 'y' or user_input == 'yes':
                default_output = "sql_analysis_report.md"
                output_file = input(f"출력 파일 경로를 입력하세요 (기본값: {default_output}): ").strip()
                if not output_file:
                    output_file = default_output
                    
                # 마크다운 형식으로 보고서 생성
                report = []
                report.append("# Oracle SQL 쿼리 복잡도 분석 보고서")
                report.append(f"\n## 복잡도 점수: {complexity_score}/10 - {description}")
                report.append("\n## 세부 평가 요소:")
                for category, score in detailed_scores.items():
                    report.append(f"- {category}: {score}")
                
                report.append("\n## 분석된 쿼리:")
                report.append("```sql")
                report.append(query)
                report.append("```")
                
                # 파일로 저장
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write("\n".join(report))
                print(f"보고서가 {output_file}에 저장되었습니다.")
    
    elif choice == '2':
        print("MyBatis XML 쿼리를 입력하세요 (입력 종료는 빈 줄에서 Ctrl+D 또는 Ctrl+Z):")
        lines = []
        try:
            while True:
                line = input()
                lines.append(line)
        except EOFError:
            pass
        
        xml_content = "\n".join(lines)
        if xml_content.strip():
            complexity_score, description, detailed_scores = analyze_query(xml_content, is_mybatis_xml=True)
            
            # 결과를 파일로 저장할지 물어봄
            user_input = input("\n분석 결과를 파일로 저장하시겠습니까? (y/n): ").strip().lower()
            if user_input == 'y' or user_input == 'yes':
                default_output = "mybatis_analysis_report.md"
                output_file = input(f"출력 파일 경로를 입력하세요 (기본값: {default_output}): ").strip()
                if not output_file:
                    output_file = default_output
                    
                # 마크다운 형식으로 보고서 생성
                report = []
                report.append("# MyBatis 동적 쿼리 복잡도 분석 보고서")
                report.append(f"\n## 복잡도 점수: {complexity_score}/10 - {description}")
                
                # MyBatis 특화 정보
                result = analyze_mybatis_query(xml_content)
                report.append(f"- 기본 SQL 복잡도: {result['base_complexity']}/10")
                report.append(f"- 최대 SQL 복잡도: {result['max_complexity']}/10")
                report.append(f"- 동적 쿼리 복잡도: {result['dynamic_complexity']}/3.0")
                
                report.append("\n## 세부 평가 요소:")
                for category, score in detailed_scores.items():
                    report.append(f"- {category}: {score}")
                
                report.append("\n## 분석된 쿼리:")
                report.append("```xml")
                report.append(xml_content)
                report.append("```")
                
                # 파일로 저장
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write("\n".join(report))
                print(f"보고서가 {output_file}에 저장되었습니다.")
    
    else:
        print("잘못된 선택입니다.")

if __name__ == "__main__":
    # 예시 MyBatis XML 쿼리로 테스트
    example_xml = """
    <select id="findEmployeesByDepartment" resultType="Employee">
        SELECT 
            employee_id, 
            first_name, 
            last_name, 
            salary
        FROM 
            employees
        WHERE 
            1=1
            <if test="departmentId != null">
                AND department_id = #{departmentId}
            </if>
            <if test="minSalary != null">
                AND salary >= #{minSalary}
            </if>
            <choose>
                <when test="orderBy == 'salary'">
                    ORDER BY salary DESC
                </when>
                <when test="orderBy == 'name'">
                    ORDER BY last_name ASC, first_name ASC
                </when>
                <otherwise>
                    ORDER BY employee_id
                </otherwise>
            </choose>
    </select>
    """
    
    print("예시 MyBatis XML 쿼리 분석 결과:")
    analyze_query(example_xml, is_mybatis_xml=True)
    
    print("\n사용자 쿼리 분석을 시작하려면 스크립트를 직접 실행하세요.")
    print("사용법: python mybatis_query_analyzer.py")
