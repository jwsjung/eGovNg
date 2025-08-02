#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
사업자휴폐업조회 사용 예제

이 파일은 business_status_checker.py 모듈의 사용법을 보여주는 예제입니다.
"""

from business_status_checker import BusinessStatusChecker
import json


def example_single_check():
    """단일 사업자등록번호 조회 예제"""
    print("=== 단일 사업자등록번호 조회 예제 ===")
    
    checker = BusinessStatusChecker()
    
    # 예제 사업자등록번호 (실제 사용시에는 실제 번호를 입력하세요)
    business_number = "110-81-25813"
    
    print(f"조회 대상: {business_number}")
    result = checker.check_business_status(business_number)
    
    # 결과 출력
    print(json.dumps(result, ensure_ascii=False, indent=2))
    print()


def example_multiple_check():
    """여러 사업자등록번호 일괄 조회 예제"""
    print("=== 여러 사업자등록번호 일괄 조회 예제 ===")
    
    checker = BusinessStatusChecker()
    
    # 예제 사업자등록번호 리스트
    business_numbers = [
        "110-81-25813",
        "123-45-67890",  # 유효하지 않은 번호
        "987-65-43210",  # 또 다른 테스트 번호
    ]
    
    results = checker.check_multiple_businesses(business_numbers)
    
    # 결과 출력
    for business_number, result in results.items():
        print(f"사업자번호: {business_number}")
        print(f"상태: {result.get('status', '오류')}")
        print(f"메시지: {result.get('message', result.get('error', ''))}")
        print("-" * 40)
    print()


def example_validation():
    """사업자등록번호 유효성 검사 예제"""
    print("=== 사업자등록번호 유효성 검사 예제 ===")
    
    checker = BusinessStatusChecker()
    
    test_numbers = [
        "110-81-25813",   # 유효한 형식
        "1108125813",     # 하이픈 없는 형식
        "123-45-67890",   # 체크섬이 맞지 않는 번호
        "12345",          # 너무 짧은 번호
        "abc-de-fghij",   # 숫자가 아닌 문자
    ]
    
    for number in test_numbers:
        is_valid = checker.validate_business_number(number)
        formatted = checker.format_business_number(number) if is_valid else "N/A"
        print(f"번호: {number:15} | 유효성: {is_valid:5} | 포맷팅: {formatted}")
    print()


def example_error_handling():
    """오류 처리 예제"""
    print("=== 오류 처리 예제 ===")
    
    checker = BusinessStatusChecker()
    
    # 잘못된 사업자등록번호로 테스트
    invalid_numbers = [
        "",               # 빈 문자열
        "123",           # 너무 짧음
        "abcdefghij",    # 문자가 포함됨
        "123-45-67890",  # 체크섬 오류
    ]
    
    for number in invalid_numbers:
        print(f"테스트 번호: '{number}'")
        result = checker.check_business_status(number)
        
        if not result['success']:
            print(f"오류: {result.get('error', '알 수 없는 오류')}")
        else:
            print("예상과 다르게 성공했습니다.")
        print("-" * 30)
    print()


def example_result_processing():
    """조회 결과 처리 예제"""
    print("=== 조회 결과 처리 예제 ===")
    
    checker = BusinessStatusChecker()
    
    # 여러 번호를 조회하고 상태별로 분류
    business_numbers = [
        "110-81-25813",
        "123-45-67890",
        "987-65-43210",
    ]
    
    results = checker.check_multiple_businesses(business_numbers)
    
    # 상태별 분류
    status_groups = {
        '정상': [],
        '휴업': [],
        '폐업': [],
        '미등록': [],
        '오류': []
    }
    
    for business_number, result in results.items():
        if result['success']:
            status = result['status']
            status_groups.setdefault(status, []).append(business_number)
        else:
            status_groups['오류'].append(business_number)
    
    # 결과 출력
    for status, numbers in status_groups.items():
        if numbers:
            print(f"{status}: {', '.join(numbers)}")
    print()


def interactive_example():
    """대화형 조회 예제"""
    print("=== 대화형 사업자등록번호 조회 ===")
    print("사업자등록번호를 입력하세요 (종료하려면 'quit' 입력)")
    
    checker = BusinessStatusChecker()
    
    while True:
        try:
            business_number = input("사업자등록번호: ").strip()
            
            if business_number.lower() in ['quit', 'exit', 'q']:
                print("조회를 종료합니다.")
                break
            
            if not business_number:
                print("사업자등록번호를 입력해주세요.")
                continue
            
            result = checker.check_business_status(business_number)
            
            print(f"\n조회 결과:")
            print(f"  사업자번호: {result['business_number']}")
            
            if result['success']:
                print(f"  상태: {result['status']}")
                print(f"  메시지: {result['message']}")
                if result['company_name']:
                    print(f"  사업자명: {result['company_name']}")
                if result['query_time']:
                    print(f"  조회시간: {result['query_time']}")
            else:
                print(f"  오류: {result.get('error', '알 수 없는 오류')}")
            
            print("-" * 50)
            
        except KeyboardInterrupt:
            print("\n\n조회를 중단합니다.")
            break
        except Exception as e:
            print(f"오류가 발생했습니다: {e}")


def main():
    """메인 함수"""
    print("사업자휴폐업조회 시스템 예제")
    print("=" * 50)
    print()
    
    # 각 예제 실행
    example_validation()
    example_single_check()
    example_multiple_check()
    example_error_handling()
    example_result_processing()
    
    # 대화형 예제 (선택사항)
    print("대화형 조회를 시작하시겠습니까? (y/n): ", end="")
    choice = input().strip().lower()
    if choice in ['y', 'yes', '예', 'ㅇ']:
        interactive_example()


if __name__ == "__main__":
    main()