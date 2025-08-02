#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
사업자 휴폐업 조회 시스템
국세청 사업자등록정보 진위확인 서비스를 이용한 사업자 상태 조회
"""

import requests
import json
from datetime import datetime
from typing import Dict, List, Optional
import re


class BusinessStatusChecker:
    """사업자 휴폐업 상태 조회 클래스"""
    
    def __init__(self):
        self.base_url = "https://teht.hometax.go.kr/wqAction.do"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Language': 'ko-KR,ko;q=0.9,en;q=0.8',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'X-Requested-With': 'XMLHttpRequest'
        })
    
    def validate_business_number(self, business_number: str) -> bool:
        """사업자등록번호 유효성 검증"""
        # 하이픈 제거 및 숫자만 추출
        clean_number = re.sub(r'[^0-9]', '', business_number)
        
        if len(clean_number) != 10:
            return False
        
        # 사업자등록번호 체크섬 검증
        check_digits = [1, 3, 7, 1, 3, 7, 1, 3, 5]
        sum_val = 0
        
        for i in range(9):
            sum_val += int(clean_number[i]) * check_digits[i]
        
        sum_val += int(int(clean_number[8]) * 5 / 10)
        check_digit = (10 - (sum_val % 10)) % 10
        
        return check_digit == int(clean_number[9])
    
    def format_business_number(self, business_number: str) -> str:
        """사업자등록번호 포맷팅 (XXX-XX-XXXXX)"""
        clean_number = re.sub(r'[^0-9]', '', business_number)
        if len(clean_number) == 10:
            return f"{clean_number[:3]}-{clean_number[3:5]}-{clean_number[5:]}"
        return business_number
    
    def check_single_business(self, business_number: str) -> Dict:
        """단일 사업자 상태 조회"""
        if not self.validate_business_number(business_number):
            return {
                'business_number': business_number,
                'status': 'INVALID',
                'message': '유효하지 않은 사업자등록번호입니다.',
                'checked_at': datetime.now().isoformat()
            }
        
        clean_number = re.sub(r'[^0-9]', '', business_number)
        
        try:
            # 국세청 API 호출
            data = {
                'actionId': 'ATTABZAA001R08',
                'screenId': 'UTEABAAA13',
                'popupYn': 'false',
                'realScreenId': '',
                'bizno': clean_number
            }
            
            response = self.session.post(self.base_url, data=data, timeout=10)
            response.raise_for_status()
            
            # 응답 파싱
            result = self._parse_response(response.text, business_number)
            return result
            
        except requests.RequestException as e:
            return {
                'business_number': business_number,
                'status': 'ERROR',
                'message': f'조회 중 오류가 발생했습니다: {str(e)}',
                'checked_at': datetime.now().isoformat()
            }
    
    def check_multiple_businesses(self, business_numbers: List[str]) -> List[Dict]:
        """복수 사업자 상태 조회"""
        results = []
        for business_number in business_numbers:
            result = self.check_single_business(business_number)
            results.append(result)
        return results
    
    def _parse_response(self, response_text: str, business_number: str) -> Dict:
        """응답 데이터 파싱"""
        try:
            # 실제 국세청 API 응답 형태에 따라 파싱 로직 조정 필요
            # 여기서는 일반적인 형태로 구현
            
            # 기본 결과 구조
            result = {
                'business_number': self.format_business_number(business_number),
                'raw_business_number': business_number,
                'checked_at': datetime.now().isoformat()
            }
            
            # 응답에서 상태 정보 추출 (실제 API 응답에 따라 수정 필요)
            if '정상사업자' in response_text or '계속사업자' in response_text:
                result.update({
                    'status': 'ACTIVE',
                    'status_text': '정상사업자',
                    'message': '정상적으로 운영중인 사업자입니다.'
                })
            elif '휴업자' in response_text:
                result.update({
                    'status': 'SUSPENDED',
                    'status_text': '휴업자',
                    'message': '현재 휴업중인 사업자입니다.'
                })
            elif '폐업자' in response_text:
                result.update({
                    'status': 'CLOSED',
                    'status_text': '폐업자',
                    'message': '폐업된 사업자입니다.'
                })
            elif '등록되지 않은' in response_text or '존재하지 않는' in response_text:
                result.update({
                    'status': 'NOT_FOUND',
                    'status_text': '미등록',
                    'message': '등록되지 않은 사업자등록번호입니다.'
                })
            else:
                result.update({
                    'status': 'UNKNOWN',
                    'status_text': '확인불가',
                    'message': '상태를 확인할 수 없습니다.'
                })
            
            return result
            
        except Exception as e:
            return {
                'business_number': self.format_business_number(business_number),
                'status': 'PARSE_ERROR',
                'message': f'응답 파싱 중 오류가 발생했습니다: {str(e)}',
                'checked_at': datetime.now().isoformat()
            }
    
    def export_to_json(self, results: List[Dict], filename: str = None) -> str:
        """결과를 JSON 파일로 저장"""
        if filename is None:
            filename = f"business_status_check_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        return filename
    
    def export_to_csv(self, results: List[Dict], filename: str = None) -> str:
        """결과를 CSV 파일로 저장"""
        import csv
        
        if filename is None:
            filename = f"business_status_check_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        if not results:
            return filename
        
        fieldnames = ['business_number', 'status', 'status_text', 'message', 'checked_at']
        
        with open(filename, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for result in results:
                writer.writerow({k: result.get(k, '') for k in fieldnames})
        
        return filename


def main():
    """메인 실행 함수"""
    print("=== 사업자 휴폐업 조회 시스템 ===\n")
    
    checker = BusinessStatusChecker()
    
    while True:
        print("1. 단일 사업자 조회")
        print("2. 복수 사업자 조회 (파일)")
        print("3. 복수 사업자 조회 (직접 입력)")
        print("4. 종료")
        
        choice = input("\n선택해주세요 (1-4): ").strip()
        
        if choice == '1':
            business_number = input("사업자등록번호를 입력하세요: ").strip()
            if business_number:
                print("\n조회 중...")
                result = checker.check_single_business(business_number)
                print_result(result)
        
        elif choice == '2':
            filename = input("사업자등록번호가 포함된 파일명을 입력하세요: ").strip()
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    business_numbers = [line.strip() for line in f if line.strip()]
                
                print(f"\n{len(business_numbers)}개 사업자 조회 중...")
                results = checker.check_multiple_businesses(business_numbers)
                
                for result in results:
                    print_result(result)
                
                # 결과 저장
                save_choice = input("\n결과를 파일로 저장하시겠습니까? (y/n): ").strip().lower()
                if save_choice == 'y':
                    json_file = checker.export_to_json(results)
                    csv_file = checker.export_to_csv(results)
                    print(f"결과가 저장되었습니다: {json_file}, {csv_file}")
                    
            except FileNotFoundError:
                print("파일을 찾을 수 없습니다.")
            except Exception as e:
                print(f"파일 처리 중 오류가 발생했습니다: {e}")
        
        elif choice == '3':
            print("사업자등록번호를 입력하세요 (완료하려면 빈 줄 입력):")
            business_numbers = []
            while True:
                number = input().strip()
                if not number:
                    break
                business_numbers.append(number)
            
            if business_numbers:
                print(f"\n{len(business_numbers)}개 사업자 조회 중...")
                results = checker.check_multiple_businesses(business_numbers)
                
                for result in results:
                    print_result(result)
                
                # 결과 저장
                save_choice = input("\n결과를 파일로 저장하시겠습니까? (y/n): ").strip().lower()
                if save_choice == 'y':
                    json_file = checker.export_to_json(results)
                    csv_file = checker.export_to_csv(results)
                    print(f"결과가 저장되었습니다: {json_file}, {csv_file}")
        
        elif choice == '4':
            print("프로그램을 종료합니다.")
            break
        
        else:
            print("잘못된 선택입니다.")
        
        print("\n" + "="*50 + "\n")


def print_result(result: Dict):
    """조회 결과 출력"""
    print(f"\n사업자등록번호: {result['business_number']}")
    print(f"상태: {result.get('status_text', result['status'])}")
    print(f"메시지: {result['message']}")
    print(f"조회시간: {result['checked_at']}")
    print("-" * 40)


if __name__ == "__main__":
    main()