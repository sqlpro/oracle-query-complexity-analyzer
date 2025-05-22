#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
SQL 파일 복잡도 분석기
특정 폴더의 모든 SQL 파일을 분석하여 복잡도 보고서 생성
"""

import os
import sys
import re
from collections import defaultdict

# 기존 분석기 임포트
try:
    # 패키지로 설치된 경우
    from .query_complexity_analyzer import calculate_query_complexity, get_complexity_description
    from .mybatis_query_analyzer import analyze_mybatis_query
except ImportError:
    # 직접 실행하는 경우
    from query_complexity_analyzer import calculate_query_complexity, get_complexity_description
    from mybatis_query_analyzer import analyze_mybatis_query

def is_mybatis_xml(content):
    """
    내용이 MyBatis XML 형식인지 확인
    
    Args:
        content (str): 파일 내용
        
    Returns:
        bool: MyBatis XML 형식 여부
    """
    # 간단한 휴리스틱: XML 태그가 있는지 확인
    xml_pattern = r'<\s*(select|insert|update|delete)[\s>]'
    return bool(re.search(xml_pattern, content, re.IGNORECASE))

def analyze_sql_file(file_path):
    """
    SQL 파일을 분석하여 복잡도 계산
    
    Args:
        file_path (str): SQL 파일 경로
        
    Returns:
        dict: 분석 결과
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 파일 이름 추출
        file_name = os.path.basename(file_path)
        
        # MyBatis XML 형식인지 확인
        is_mybatis = is_mybatis_xml(content)
        
        if is_mybatis:
            # MyBatis 동적 쿼리 분석
            result = analyze_mybatis_query(content)
            complexity_score = result['final_complexity']
            description = get_complexity_description(complexity_score)
            
            return {
                'file_name': file_name,
                'file_path': file_path,
                'is_mybatis': True,
                'complexity_score': complexity_score,
                'description': description,
                'base_complexity': result['base_complexity'],
                'max_complexity': result['max_complexity'],
                'dynamic_complexity': result['dynamic_complexity'],
                'detailed_scores': result['detailed_scores']
            }
        else:
            # 일반 SQL 쿼리 분석
            complexity_score, detailed_scores = calculate_query_complexity(content)
            description = get_complexity_description(complexity_score)
            
            return {
                'file_name': file_name,
                'file_path': file_path,
                'is_mybatis': False,
                'complexity_score': complexity_score,
                'description': description,
                'detailed_scores': detailed_scores
            }
    
    except Exception as e:
        print(f"Error analyzing file {file_path}: {str(e)}")
        return {
            'file_name': os.path.basename(file_path),
            'file_path': file_path,
            'error': str(e)
        }

def analyze_directory(directory_path):
    """
    디렉토리 내의 모든 SQL 파일 분석
    
    Args:
        directory_path (str): 분석할 디렉토리 경로
        
    Returns:
        list: 각 파일의 분석 결과
    """
    results = []
    
    # 디렉토리 내의 모든 .sql 파일 찾기
    for root, _, files in os.walk(directory_path):
        for file in files:
            if file.endswith('.sql'):
                file_path = os.path.join(root, file)
                result = analyze_sql_file(file_path)
                results.append(result)
    
    return results

def generate_report(results, output_file=None):
    """
    분석 결과를 보고서로 생성
    
    Args:
        results (list): 분석 결과 목록
        output_file (str): 출력 파일 경로 (None인 경우 콘솔에 출력)
    """
    report = []
    report.append("# SQL 쿼리 복잡도 분석 보고서")
    report.append(f"\n분석 파일 수: {len(results)}")
    
    # 복잡도 레벨별 파일 수 집계
    complexity_counts = defaultdict(int)
    mybatis_count = 0
    regular_sql_count = 0
    error_count = 0
    
    for result in results:
        if 'error' in result:
            error_count += 1
            continue
            
        complexity_counts[result['description']] += 1
        if result['is_mybatis']:
            mybatis_count += 1
        else:
            regular_sql_count += 1
    
    report.append("\n## 요약")
    report.append(f"- MyBatis 동적 쿼리: {mybatis_count}개")
    report.append(f"- 일반 SQL 쿼리: {regular_sql_count}개")
    report.append(f"- 분석 오류: {error_count}개")
    
    report.append("\n### 복잡도 분포")
    
    # 복잡도 순서 정의
    complexity_order = {
        "매우 간단 (Very Simple)": 0,
        "간단 (Simple)": 1,
        "중간 (Moderate)": 2,
        "복잡 (Complex)": 3,
        "매우 복잡 (Very Complex)": 4,
        "극도로 복잡 (Extremely Complex)": 5
    }
    
    for description, count in sorted(complexity_counts.items(), 
                                   key=lambda x: complexity_order.get(x[0], 999)):
        percentage = (count / (len(results) - error_count)) * 100 if (len(results) - error_count) > 0 else 0
        report.append(f"- {description}: {count}개 ({percentage:.1f}%)")
    
    # 복잡도 순으로 정렬
    sorted_results = sorted([r for r in results if 'error' not in r], 
                           key=lambda x: x['complexity_score'], 
                           reverse=True)
    
    report.append("\n## 파일별 상세 분석")
    
    for result in sorted_results:
        file_name = result['file_name']
        complexity = result['complexity_score']
        description = result['description']
        
        report.append(f"\n### {file_name} - {complexity}/10 ({description})")
        
        if result['is_mybatis']:
            report.append(f"- 유형: MyBatis 동적 쿼리")
            report.append(f"- 기본 SQL 복잡도: {result['base_complexity']}/10")
            report.append(f"- 최대 SQL 복잡도: {result['max_complexity']}/10")
            report.append(f"- 동적 쿼리 복잡도: {result['dynamic_complexity']}/3.0")
        else:
            report.append(f"- 유형: 일반 SQL 쿼리")
        
        report.append("\n세부 평가 요소:")
        for category, score in result['detailed_scores'].items():
            report.append(f"- {category}: {score}")
    
    # 오류 발생 파일 목록
    error_files = [r for r in results if 'error' in r]
    if error_files:
        report.append("\n## 분석 오류 파일")
        for result in error_files:
            report.append(f"- {result['file_name']}: {result['error']}")
    
    # 보고서 출력 또는 파일 저장
    report_text = "\n".join(report)
    
    if output_file:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(report_text)
        print(f"보고서가 {output_file}에 저장되었습니다.")
    else:
        print(report_text)
    
    return report_text

def main():
    """
    메인 함수
    """
    if len(sys.argv) < 2:
        print("사용법: python sql_directory_analyzer.py <디렉토리_경로> [출력_파일_경로]")
        return
    
    directory_path = sys.argv[1]
    
    # 출력 파일 경로가 명령줄 인수로 제공되었는지 확인
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    # 출력 파일이 제공되지 않은 경우 사용자에게 물어봄
    if output_file is None:
        user_input = input("분석 결과를 파일로 저장하시겠습니까? (y/n): ").strip().lower()
        if user_input == 'y' or user_input == 'yes':
            default_output = os.path.join(os.path.dirname(directory_path), "analysis_report.md")
            output_file = input(f"출력 파일 경로를 입력하세요 (기본값: {default_output}): ").strip()
            if not output_file:
                output_file = default_output
    
    if not os.path.isdir(directory_path):
        print(f"오류: {directory_path}는 유효한 디렉토리가 아닙니다.")
        return
    
    print(f"{directory_path} 디렉토리의 SQL 파일 분석 중...")
    results = analyze_directory(directory_path)
    
    if not results:
        print("SQL 파일을 찾을 수 없습니다.")
        return
    
    generate_report(results, output_file)

if __name__ == "__main__":
    main()
