#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
간단한 사업자등록번호 휴폐업 조회 스크립트
명령행에서 빠르게 사업자등록번호를 조회할 수 있습니다.
"""

import argparse
import sys
import os
from business_status_checker import BusinessStatusChecker


def main():
    parser = argparse.ArgumentParser(description='사업자등록번호 휴폐업 조회')
    parser.add_argument('business_numbers', nargs='+', 
                       help='조회할 사업자등록번호 (하나 이상)')
    parser.add_argument('--api-key', '-k', 
                       help='API 키 (환경변수 BUSINESS_API_KEY에서도 읽어옴)')
    parser.add_argument('--output', '-o', 
                       help='결과를 저장할 CSV 파일명')
    parser.add_argument('--quiet', '-q', action='store_true',
                       help='간단한 출력만 표시')
    
    args = parser.parse_args()
    
    # API 키 설정
    api_key = args.api_key or os.environ.get('BUSINESS_API_KEY')
    if not api_key:
        print("오류: API 키가 필요합니다. --api-key 옵션을 사용하거나 BUSINESS_API_KEY 환경변수를 설정하세요.")
        print("API 키는 공공데이터포털(data.go.kr)에서 발급받을 수 있습니다.")
        return 1
    
    checker = BusinessStatusChecker()
    checker.set_api_key(api_key)
    
    try:
        if len(args.business_numbers) == 1:
            # 단일 조회
            result = checker.check_single_business(args.business_numbers[0])
            if result:
                if args.quiet:
                    print(f"{result['business_number']}: {result['status']}")
                else:
                    print("사업자등록번호 조회 결과:")
                    print("-" * 30)
                    for key, value in result.items():
                        if key != 'error':
                            print(f"{key}: {value}")
            else:
                print("조회 결과가 없습니다.")
                return 1
        else:
            # 일괄 조회
            results = checker.check_multiple_businesses(args.business_numbers)
            
            if args.quiet:
                for result in results:
                    if 'error' in result:
                        print(f"{result['business_number']}: 오류 - {result['error']}")
                    else:
                        print(f"{result['business_number']}: {result['status']}")
            else:
                print(f"일괄 조회 결과 ({len(results)}건):")
                print("=" * 50)
                for i, result in enumerate(results, 1):
                    print(f"\n[{i}] {result.get('business_number', '')}")
                    if 'error' in result:
                        print(f"  오류: {result['error']}")
                    else:
                        print(f"  상태: {result['status']}")
                        print(f"  상호명: {result.get('company_name', '')}")
                        print(f"  대표자: {result.get('ceo_name', '')}")
            
            # CSV 저장
            if args.output:
                checker.export_to_csv(results, args.output)
        
        return 0
        
    except Exception as e:
        print(f"오류: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())