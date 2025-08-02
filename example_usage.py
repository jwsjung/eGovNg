#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
사업자 휴폐업 조회 시스템 사용 예제
"""

from business_status_checker import BusinessStatusChecker
import json


def example_single_check():
    """단일 사업자 조회 예제"""
    print("=== 단일 사업자 조회 예제 ===")
    
    checker = BusinessStatusChecker()
    
    # 예제 사업자등록번호들 (실제 조회 시에는 유효한 번호를 사용하세요)
    test_numbers = [
        "123-45-67890",  # 포맷된 형태
        "1234567890",    # 포맷되지 않은 형태
        "123-45-67891",  # 잘못된 체크섬
    ]
    
    for business_number in test_numbers:
        print(f"\n조회 대상: {business_number}")
        result = checker.check_single_business(business_number)
        
        print(f"사업자등록번호: {result['business_number']}")
        print(f"상태: {result.get('status_text', result['status'])}")
        print(f"메시지: {result['message']}")
        print(f"조회시간: {result['checked_at']}")
        print("-" * 50)


def example_multiple_check():
    """복수 사업자 조회 예제"""
    print("=== 복수 사업자 조회 예제 ===")
    
    checker = BusinessStatusChecker()
    
    # 예제 사업자등록번호 목록
    business_numbers = [
        "123-45-67890",
        "987-65-43210",
        "555-55-55555",
        "invalid-number",
        "1234567890"
    ]
    
    print(f"조회할 사업자 수: {len(business_numbers)}")
    
    results = checker.check_multiple_businesses(business_numbers)
    
    # 결과 출력
    for i, result in enumerate(results, 1):
        print(f"\n[{i}] {result['business_number']}")
        print(f"상태: {result.get('status_text', result['status'])}")
        print(f"메시지: {result['message']}")
    
    # 결과를 파일로 저장
    json_file = checker.export_to_json(results, "example_results.json")
    csv_file = checker.export_to_csv(results, "example_results.csv")
    
    print(f"\n결과가 저장되었습니다:")
    print(f"JSON: {json_file}")
    print(f"CSV: {csv_file}")


def example_validation():
    """사업자등록번호 유효성 검증 예제"""
    print("=== 사업자등록번호 유효성 검증 예제 ===")
    
    checker = BusinessStatusChecker()
    
    test_cases = [
        ("123-45-67890", "올바른 형태"),
        ("1234567890", "하이픈 없는 형태"),
        ("123-45-6789", "자릿수 부족"),
        ("123-45-678901", "자릿수 초과"),
        ("abc-de-fghij", "문자 포함"),
        ("123-45-67891", "잘못된 체크섬"),
    ]
    
    for business_number, description in test_cases:
        is_valid = checker.validate_business_number(business_number)
        formatted = checker.format_business_number(business_number)
        
        print(f"입력: {business_number:15} ({description})")
        print(f"유효성: {'유효' if is_valid else '무효':5} | 포맷: {formatted}")
        print("-" * 60)


def example_api_response_parsing():
    """API 응답 파싱 예제 (시뮬레이션)"""
    print("=== API 응답 파싱 예제 ===")
    
    checker = BusinessStatusChecker()
    
    # 가상의 API 응답 예제들
    sample_responses = [
        ("정상사업자로 확인되었습니다.", "ACTIVE"),
        ("휴업자로 등록되어 있습니다.", "SUSPENDED"),
        ("폐업자로 확인되었습니다.", "CLOSED"),
        ("등록되지 않은 사업자등록번호입니다.", "NOT_FOUND"),
        ("알 수 없는 응답입니다.", "UNKNOWN")
    ]
    
    for response_text, expected_status in sample_responses:
        result = checker._parse_response(response_text, "123-45-67890")
        
        print(f"응답: {response_text}")
        print(f"파싱 결과: {result['status']} ({result.get('status_text', '')})")
        print(f"예상 상태: {expected_status}")
        print(f"일치: {'O' if result['status'] == expected_status else 'X'}")
        print("-" * 60)


def example_file_processing():
    """파일 처리 예제"""
    print("=== 파일 처리 예제 ===")
    
    # 예제 입력 파일 생성
    input_filename = "example_business_numbers.txt"
    example_numbers = [
        "123-45-67890",
        "987-65-43210",
        "555-55-55555",
        "1234567890",
        "invalid-number"
    ]
    
    # 입력 파일 생성
    with open(input_filename, 'w', encoding='utf-8') as f:
        for number in example_numbers:
            f.write(f"{number}\n")
    
    print(f"입력 파일 생성: {input_filename}")
    print("파일 내용:")
    with open(input_filename, 'r', encoding='utf-8') as f:
        print(f.read())
    
    # 파일에서 사업자번호 읽기 및 조회
    checker = BusinessStatusChecker()
    
    with open(input_filename, 'r', encoding='utf-8') as f:
        business_numbers = [line.strip() for line in f if line.strip()]
    
    print(f"파일에서 읽은 사업자번호 수: {len(business_numbers)}")
    
    results = checker.check_multiple_businesses(business_numbers)
    
    # 결과 통계
    status_count = {}
    for result in results:
        status = result['status']
        status_count[status] = status_count.get(status, 0) + 1
    
    print("\n조회 결과 통계:")
    for status, count in status_count.items():
        print(f"{status}: {count}개")


if __name__ == "__main__":
    print("사업자 휴폐업 조회 시스템 예제 실행\n")
    
    # 각 예제 실행
    example_validation()
    print("\n" + "="*70 + "\n")
    
    example_single_check()
    print("\n" + "="*70 + "\n")
    
    example_multiple_check()
    print("\n" + "="*70 + "\n")
    
    example_api_response_parsing()
    print("\n" + "="*70 + "\n")
    
    example_file_processing()
    
    print("\n모든 예제가 완료되었습니다.")