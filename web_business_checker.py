#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
웹 기반 사업자등록번호 휴폐업 조회 시스템
Flask를 사용하여 웹 인터페이스를 제공합니다.
"""

from flask import Flask, render_template, request, jsonify, send_file
import os
import tempfile
from business_status_checker import BusinessStatusChecker

app = Flask(__name__)

# 전역 checker 인스턴스
checker = BusinessStatusChecker()

@app.route('/')
def index():
    """메인 페이지"""
    return render_template('index.html')

@app.route('/api/check', methods=['POST'])
def check_business():
    """사업자등록번호 조회 API"""
    try:
        data = request.get_json()
        
        if not data or 'business_numbers' not in data:
            return jsonify({'error': '사업자등록번호가 필요합니다.'}), 400
        
        api_key = data.get('api_key') or os.environ.get('BUSINESS_API_KEY')
        if not api_key:
            return jsonify({'error': 'API 키가 필요합니다.'}), 400
        
        checker.set_api_key(api_key)
        
        business_numbers = data['business_numbers']
        if isinstance(business_numbers, str):
            business_numbers = [business_numbers]
        
        results = checker.check_multiple_businesses(business_numbers)
        
        return jsonify({
            'success': True,
            'results': results,
            'count': len(results)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/export', methods=['POST'])
def export_csv():
    """CSV 내보내기 API"""
    try:
        data = request.get_json()
        
        if not data or 'results' not in data:
            return jsonify({'error': '내보낼 데이터가 필요합니다.'}), 400
        
        # 임시 파일 생성
        temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False)
        temp_file.close()
        
        checker.export_to_csv(data['results'], temp_file.name)
        
        return send_file(temp_file.name, 
                        as_attachment=True, 
                        download_name='business_status.csv',
                        mimetype='text/csv')
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/validate', methods=['POST'])
def validate_business_number():
    """사업자등록번호 유효성 검증 API"""
    try:
        data = request.get_json()
        
        if not data or 'business_number' not in data:
            return jsonify({'error': '사업자등록번호가 필요합니다.'}), 400
        
        is_valid = checker.validate_business_number(data['business_number'])
        formatted_number = checker.format_business_number(data['business_number'])
        
        return jsonify({
            'valid': is_valid,
            'formatted': formatted_number
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # templates 디렉토리가 없으면 생성
    if not os.path.exists('templates'):
        os.makedirs('templates')
    
    # 개발 서버 실행
    app.run(debug=True, host='0.0.0.0', port=5000)