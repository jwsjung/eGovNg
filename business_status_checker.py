#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
사업자등록번호 휴폐업 조회 시스템
국세청 사업자등록번호 상태조회 API를 사용하여 사업자의 휴폐업 상태를 확인하는 기능
"""

import requests
import json
import re
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class BusinessInfo:
    """사업자 정보를 담는 데이터클래스"""
    business_number: str
    company_name: str
    ceo_name: str
    status: str
    status_date: str
    address: str
    business_type: str
    
    def __str__(self):
        return f"""
사업자등록번호: {self.business_number}
상호명: {self.company_name}
대표자명: {self.ceo_name}
상태: {self.status}
상태변경일: {self.status_date}
주소: {self.address}
업종: {self.business_type}
"""


class BusinessStatusChecker:
    """사업자등록번호 휴폐업 조회 클래스"""
    
    def __init__(self):
        """초기화"""
        # 국세청 사업자등록번호 상태조회 API URL
        self.api_url = "https://api.odcloud.kr/api/nts-businessman/v1/status"
        # API 키는 환경변수나 설정파일에서 읽어오는 것을 권장
        self.service_key = None
    
    def set_api_key(self, api_key: str):
        """API 키 설정"""
        self.service_key = api_key
    
    def validate_business_number(self, business_number: str) -> bool:
        """사업자등록번호 형식 및 체크섬 검증"""
        # 숫자만 추출
        number = re.sub(r'[^0-9]', '', business_number)
        
        # 10자리 숫자인지 확인
        if len(number) != 10:
            return False
        
        # 체크섬 검증 (국세청 공식 알고리즘)
        check_array = [1, 3, 7, 1, 3, 7, 1, 3, 5]
        sum_val = 0
        
        # 처음 9자리에 대한 계산
        for i in range(9):
            sum_val += int(number[i]) * check_array[i]
        
        # 8번째 자리에 대한 추가 계산
        sum_val += (int(number[8]) * 5) // 10
        
        # 체크섬 계산
        check_digit = (10 - (sum_val % 10)) % 10
        
        return check_digit == int(number[9])
    
    def format_business_number(self, business_number: str) -> str:
        """사업자등록번호를 xxx-xx-xxxxx 형식으로 포맷팅"""
        number = re.sub(r'[^0-9]', '', business_number)
        if len(number) == 10:
            return f"{number[:3]}-{number[3:5]}-{number[5:]}"
        return business_number
    
    def check_single_business(self, business_number: str) -> Optional[Dict]:
        """단일 사업자등록번호 조회"""
        if not self.service_key:
            raise ValueError("API 키가 설정되지 않았습니다. set_api_key()를 먼저 호출하세요.")
        
        # 사업자등록번호 유효성 검증
        if not self.validate_business_number(business_number):
            raise ValueError(f"유효하지 않은 사업자등록번호입니다: {business_number}")
        
        # 숫자만 추출
        clean_number = re.sub(r'[^0-9]', '', business_number)
        
        # API 요청 파라미터
        params = {
            'serviceKey': self.service_key,
            'b_no': clean_number
        }
        
        try:
            response = requests.get(self.api_url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get('status_code') == 'OK':
                if data.get('data') and len(data['data']) > 0:
                    business_data = data['data'][0]
                    return {
                        'business_number': self.format_business_number(clean_number),
                        'company_name': business_data.get('tax_type', ''),
                        'ceo_name': business_data.get('ceo_nm', ''),
                        'status': self._get_status_description(business_data.get('b_stt_cd', '')),
                        'status_code': business_data.get('b_stt_cd', ''),
                        'status_date': business_data.get('b_stt_dt', ''),
                        'address': business_data.get('tax_type_cd', ''),
                        'business_type': business_data.get('tax_type', ''),
                        'query_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    }
                else:
                    return None
            else:
                raise Exception(f"API 오류: {data.get('message', '알 수 없는 오류')}")
                
        except requests.exceptions.RequestException as e:
            raise Exception(f"네트워크 오류: {str(e)}")
        except json.JSONDecodeError:
            raise Exception("API 응답 파싱 오류")
    
    def check_multiple_businesses(self, business_numbers: List[str]) -> List[Dict]:
        """여러 사업자등록번호 일괄 조회"""
        results = []
        
        for number in business_numbers:
            try:
                result = self.check_single_business(number)
                if result:
                    results.append(result)
                else:
                    results.append({
                        'business_number': self.format_business_number(number),
                        'error': '조회 결과가 없습니다.'
                    })
            except Exception as e:
                results.append({
                    'business_number': self.format_business_number(number),
                    'error': str(e)
                })
        
        return results
    
    def _get_status_description(self, status_code: str) -> str:
        """상태 코드를 한글 설명으로 변환"""
        status_map = {
            '01': '계속사업자',
            '02': '휴업자',
            '03': '폐업자',
            '': '상태불명'
        }
        return status_map.get(status_code, f'알 수 없는 상태({status_code})')
    
    def export_to_csv(self, results: List[Dict], filename: str = None):
        """조회 결과를 CSV 파일로 내보내기"""
        import csv
        
        if not filename:
            filename = f"business_status_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        if not results:
            print("내보낼 데이터가 없습니다.")
            return
        
        with open(filename, 'w', newline='', encoding='utf-8-sig') as csvfile:
            fieldnames = ['business_number', 'company_name', 'ceo_name', 'status', 
                         'status_date', 'address', 'business_type', 'query_time', 'error']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            for result in results:
                writer.writerow(result)
        
        print(f"결과가 {filename} 파일로 저장되었습니다.")


def main():
    """메인 함수 - 사용 예시"""
    checker = BusinessStatusChecker()
    
    # API 키 설정 (실제 사용시에는 환경변수나 설정파일에서 읽어오세요)
    # checker.set_api_key("YOUR_API_KEY_HERE")
    
    print("=" * 50)
    print("사업자등록번호 휴폐업 조회 시스템")
    print("=" * 50)
    
    while True:
        print("\n1. 단일 사업자등록번호 조회")
        print("2. 여러 사업자등록번호 일괄 조회")
        print("3. 파일에서 사업자등록번호 읽어와서 조회")
        print("4. 종료")
        
        choice = input("\n선택하세요 (1-4): ").strip()
        
        try:
            if choice == '1':
                business_number = input("사업자등록번호를 입력하세요: ").strip()
                result = checker.check_single_business(business_number)
                
                if result:
                    print("\n" + "=" * 40)
                    print("조회 결과:")
                    print("=" * 40)
                    for key, value in result.items():
                        if key != 'error':
                            print(f"{key}: {value}")
                else:
                    print("조회 결과가 없습니다.")
            
            elif choice == '2':
                numbers_input = input("사업자등록번호들을 쉼표로 구분하여 입력하세요: ").strip()
                business_numbers = [num.strip() for num in numbers_input.split(',')]
                
                results = checker.check_multiple_businesses(business_numbers)
                
                print("\n" + "=" * 40)
                print("일괄 조회 결과:")
                print("=" * 40)
                
                for i, result in enumerate(results, 1):
                    print(f"\n[{i}] {result.get('business_number', '')}")
                    if 'error' in result:
                        print(f"오류: {result['error']}")
                    else:
                        for key, value in result.items():
                            if key not in ['business_number', 'error']:
                                print(f"  {key}: {value}")
                
                # CSV로 내보내기 옵션
                save_csv = input("\n결과를 CSV 파일로 저장하시겠습니까? (y/n): ").strip().lower()
                if save_csv == 'y':
                    checker.export_to_csv(results)
            
            elif choice == '3':
                filename = input("사업자등록번호가 포함된 파일명을 입력하세요: ").strip()
                try:
                    with open(filename, 'r', encoding='utf-8') as f:
                        lines = f.readlines()
                    
                    business_numbers = []
                    for line in lines:
                        # 각 줄에서 사업자등록번호 추출 (10자리 숫자)
                        numbers = re.findall(r'\d{10}', line.strip())
                        business_numbers.extend(numbers)
                    
                    if not business_numbers:
                        print("파일에서 유효한 사업자등록번호를 찾을 수 없습니다.")
                        continue
                    
                    print(f"파일에서 {len(business_numbers)}개의 사업자등록번호를 찾았습니다.")
                    results = checker.check_multiple_businesses(business_numbers)
                    checker.export_to_csv(results)
                    
                except FileNotFoundError:
                    print("파일을 찾을 수 없습니다.")
                except Exception as e:
                    print(f"파일 읽기 오류: {e}")
            
            elif choice == '4':
                print("프로그램을 종료합니다.")
                break
            
            else:
                print("잘못된 선택입니다. 1-4 중에서 선택하세요.")
                
        except Exception as e:
            print(f"오류 발생: {e}")


if __name__ == "__main__":
    main()