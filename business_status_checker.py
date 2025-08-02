#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
사업자휴폐업조회 모듈

국세청 홈택스 사업자등록번호 상태조회 API를 활용하여
사업자의 휴업/폐업 상태를 조회하는 기능을 제공합니다.

Usage:
    from business_status_checker import BusinessStatusChecker
    
    checker = BusinessStatusChecker()
    result = checker.check_business_status("123-45-67890")
    print(result)
"""

import requests
import json
import re
from typing import Dict, Any, Optional
from datetime import datetime


class BusinessStatusChecker:
    """사업자휴폐업조회 클래스"""
    
    def __init__(self):
        """초기화"""
        self.base_url = "https://teht.hometax.go.kr/wqAction.do"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Content-Type': 'application/xml',
            'Accept': 'application/xml, text/xml, */*',
            'Referer': 'https://teht.hometax.go.kr/websquare/websquare.html'
        }
        
    def validate_business_number(self, business_number: str) -> bool:
        """
        사업자등록번호 유효성 검사
        
        Args:
            business_number (str): 사업자등록번호 (xxx-xx-xxxxx 또는 xxxxxxxxxx 형식)
            
        Returns:
            bool: 유효한 사업자등록번호인지 여부
        """
        # 하이픈 제거
        clean_number = re.sub(r'[-\s]', '', business_number)
        
        # 10자리 숫자인지 확인
        if not re.match(r'^\d{10}$', clean_number):
            return False
            
        # 체크섬 검증
        weights = [1, 3, 7, 1, 3, 7, 1, 3, 5]
        total = sum(int(clean_number[i]) * weights[i] for i in range(9))
        
        check_digit = (10 - (total % 10)) % 10
        
        return int(clean_number[9]) == check_digit
    
    def format_business_number(self, business_number: str) -> str:
        """
        사업자등록번호를 표준 형식(xxx-xx-xxxxx)으로 포맷팅
        
        Args:
            business_number (str): 사업자등록번호
            
        Returns:
            str: 포맷팅된 사업자등록번호
        """
        clean_number = re.sub(r'[-\s]', '', business_number)
        return f"{clean_number[:3]}-{clean_number[3:5]}-{clean_number[5:]}"
    
    def check_business_status(self, business_number: str) -> Dict[str, Any]:
        """
        사업자휴폐업상태 조회
        
        Args:
            business_number (str): 사업자등록번호
            
        Returns:
            Dict[str, Any]: 조회 결과
                - success (bool): 조회 성공 여부
                - business_number (str): 조회한 사업자등록번호
                - status (str): 사업자 상태 ('정상', '휴업', '폐업', '미등록' 등)
                - company_name (str): 회사명 (조회된 경우)
                - registration_date (str): 개업일자
                - closure_date (str): 폐업일자 (폐업된 경우)
                - message (str): 응답 메시지
                - error (str): 오류 메시지 (오류 발생시)
        """
        try:
            # 사업자등록번호 유효성 검사
            if not self.validate_business_number(business_number):
                return {
                    'success': False,
                    'business_number': business_number,
                    'error': '유효하지 않은 사업자등록번호입니다.'
                }
            
            # 사업자등록번호 포맷팅
            formatted_number = self.format_business_number(business_number)
            clean_number = re.sub(r'[-\s]', '', business_number)
            
            # API 요청 데이터 구성
            xml_data = f"""<?xml version="1.0" encoding="UTF-8"?>
<map id="ATTABZAA001R08">
    <pubcUserNo>{clean_number}</pubcUserNo>
    <inqrTrgtClCd>1</inqrTrgtClCd>
    <txprDscmNo>{clean_number}</txprDscmNo>
    <dongCode>01</dongCode>
    <psbSearch>Y</psbSearch>
    <map id="userReqInfoVO"/>
</map>"""
            
            # API 호출
            response = requests.post(
                self.base_url,
                data=xml_data.encode('utf-8'),
                headers=self.headers,
                timeout=30
            )
            
            response.raise_for_status()
            
            # XML 응답 파싱
            response_text = response.text
            
            # 기본 결과 구조
            result = {
                'success': False,
                'business_number': formatted_number,
                'status': '',
                'company_name': '',
                'registration_date': '',
                'closure_date': '',
                'message': '',
                'query_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            # XML에서 주요 정보 추출
            if 'trtCntn' in response_text:
                # 정상적인 응답
                result['success'] = True
                
                # 상태 정보 추출
                if '계속사업자' in response_text:
                    result['status'] = '정상'
                    result['message'] = '정상적으로 사업중인 사업자입니다.'
                elif '휴업자' in response_text:
                    result['status'] = '휴업'
                    result['message'] = '현재 휴업중인 사업자입니다.'
                elif '폐업자' in response_text:
                    result['status'] = '폐업'
                    result['message'] = '폐업한 사업자입니다.'
                else:
                    result['status'] = '미확인'
                    result['message'] = '사업자 상태를 확인할 수 없습니다.'
                
                # 사업자명 추출 (있는 경우)
                if 'txprNm' in response_text:
                    import xml.etree.ElementTree as ET
                    try:
                        root = ET.fromstring(response_text)
                        name_elem = root.find('.//txprNm')
                        if name_elem is not None and name_elem.text:
                            result['company_name'] = name_elem.text.strip()
                    except:
                        pass
                        
            elif '등록되지 않은' in response_text or '해당 자료가 없습니다' in response_text:
                result['status'] = '미등록'
                result['message'] = '등록되지 않은 사업자등록번호입니다.'
                
            else:
                result['error'] = '조회 중 오류가 발생했습니다.'
                
            return result
            
        except requests.exceptions.RequestException as e:
            return {
                'success': False,
                'business_number': business_number,
                'error': f'네트워크 오류: {str(e)}'
            }
        except Exception as e:
            return {
                'success': False,
                'business_number': business_number,
                'error': f'조회 중 오류 발생: {str(e)}'
            }
    
    def check_multiple_businesses(self, business_numbers: list) -> Dict[str, Dict[str, Any]]:
        """
        여러 사업자등록번호 일괄 조회
        
        Args:
            business_numbers (list): 사업자등록번호 리스트
            
        Returns:
            Dict[str, Dict[str, Any]]: 각 사업자번호별 조회 결과
        """
        results = {}
        
        for business_number in business_numbers:
            results[business_number] = self.check_business_status(business_number)
            
        return results


def main():
    """메인 함수 - 사용 예제"""
    checker = BusinessStatusChecker()
    
    # 테스트용 사업자등록번호 (실제 존재하지 않는 번호)
    test_numbers = [
        "123-45-67890",  # 유효하지 않은 번호
        "110-81-25813",  # 테스트용 번호
    ]
    
    print("=== 사업자휴폐업조회 테스트 ===")
    print()
    
    for business_number in test_numbers:
        print(f"조회 대상: {business_number}")
        result = checker.check_business_status(business_number)
        
        print(f"성공 여부: {result['success']}")
        print(f"사업자번호: {result['business_number']}")
        
        if result['success']:
            print(f"상태: {result['status']}")
            print(f"메시지: {result['message']}")
            if result['company_name']:
                print(f"사업자명: {result['company_name']}")
        else:
            print(f"오류: {result.get('error', '알 수 없는 오류')}")
        
        print("-" * 50)


if __name__ == "__main__":
    main()