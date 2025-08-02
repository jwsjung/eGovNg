# 🏢 사업자등록번호 휴폐업 조회 시스템

국세청 사업자등록번호 상태조회 API를 사용하여 사업자의 휴폐업 상태를 확인하는 Python 기반 시스템입니다.

## ✨ 주요 기능

- **사업자등록번호 유효성 검증**: 체크섬 알고리즘을 통한 정확한 검증
- **단일/일괄 조회**: 하나 또는 여러 사업자등록번호를 동시에 조회
- **다양한 인터페이스**: CLI, 웹 인터페이스, 라이브러리 형태로 제공
- **CSV 내보내기**: 조회 결과를 CSV 파일로 저장
- **실시간 조회**: 국세청 API를 통한 실시간 상태 확인

## 📋 상태 분류

- **계속사업자**: 정상 영업 중인 사업자
- **휴업자**: 일시적으로 영업을 중단한 사업자
- **폐업자**: 사업을 완전히 종료한 사업자

## 🚀 설치 및 설정

### 1. 종속성 설치

```bash
pip install -r requirements.txt
```

### 2. API 키 발급

1. [공공데이터포털](https://data.go.kr)에 접속
2. 회원가입 및 로그인
3. "국세청_사업자등록번호 상태조회 서비스" 검색
4. 활용신청 후 API 키 발급

### 3. API 키 설정 (선택사항)

환경변수로 API 키를 설정하면 매번 입력할 필요가 없습니다:

```bash
export BUSINESS_API_KEY="발급받은_API_키"
```

## 💻 사용 방법

### 1. 대화형 프로그램 (추천)

```bash
python business_status_checker.py
```

메뉴 기반 인터페이스로 쉽게 사업자등록번호를 조회할 수 있습니다.

### 2. 명령행 인터페이스

```bash
# 단일 조회
python simple_business_checker.py 123-45-67890 --api-key YOUR_API_KEY

# 여러 조회
python simple_business_checker.py 1234567890 9876543210 --api-key YOUR_API_KEY

# 간단한 출력
python simple_business_checker.py 1234567890 --quiet --api-key YOUR_API_KEY

# CSV 파일로 저장
python simple_business_checker.py 1234567890 9876543210 --output results.csv --api-key YOUR_API_KEY
```

### 3. 웹 인터페이스

```bash
python web_business_checker.py
```

웹 브라우저에서 `http://localhost:5000`에 접속하여 사용할 수 있습니다.

### 4. Python 라이브러리로 사용

```python
from business_status_checker import BusinessStatusChecker

# 인스턴스 생성 및 API 키 설정
checker = BusinessStatusChecker()
checker.set_api_key("YOUR_API_KEY")

# 단일 조회
result = checker.check_single_business("123-45-67890")
print(result)

# 여러 조회
results = checker.check_multiple_businesses(["1234567890", "9876543210"])
for result in results:
    print(result)

# CSV 내보내기
checker.export_to_csv(results, "business_status.csv")
```

## 📁 파일 구조

```
├── business_status_checker.py     # 메인 라이브러리 및 대화형 프로그램
├── simple_business_checker.py     # 명령행 인터페이스
├── web_business_checker.py        # 웹 서버
├── templates/
│   └── index.html                 # 웹 인터페이스 템플릿
├── requirements.txt               # Python 종속성
└── README.md                      # 이 파일
```

## 🔧 고급 사용법

### 파일에서 사업자등록번호 읽어오기

사업자등록번호가 포함된 텍스트 파일이 있다면:

```bash
# 파일 예시 (business_numbers.txt)
삼성전자 1234567890
LG전자: 9876543210
현대자동차 (555-66-77888)
```

대화형 프로그램에서 "3. 파일에서 사업자등록번호 읽어와서 조회" 옵션을 선택하여 일괄 처리할 수 있습니다.

### API 응답 구조

```python
{
    'business_number': '123-45-67890',     # 포맷팅된 사업자등록번호
    'company_name': '회사명',               # 상호명
    'ceo_name': '대표자명',                 # 대표자명
    'status': '계속사업자',                 # 사업자 상태
    'status_code': '01',                   # 상태 코드
    'status_date': '20231201',             # 상태 변경일
    'address': '주소',                     # 사업장 주소
    'business_type': '업종',               # 업종
    'query_time': '2023-12-01 12:00:00'   # 조회 시간
}
```

### 오류 처리

- **유효하지 않은 사업자등록번호**: 체크섬 검증 실패
- **API 키 오류**: 잘못되거나 만료된 API 키
- **네트워크 오류**: 인터넷 연결 또는 서버 문제
- **할당량 초과**: API 호출 한도 초과

## 📊 사업자등록번호 체크섬 알고리즘

이 프로그램은 국세청 공식 체크섬 알고리즘을 사용하여 사업자등록번호의 유효성을 검증합니다:

1. 처음 9자리 숫자에 가중치 [1,3,7,1,3,7,1,3,5]를 곱함
2. 8번째 자리에 5를 곱한 값을 10으로 나눈 몫을 더함
3. 합계를 10으로 나눈 나머지를 10에서 뺀 값이 마지막 자리와 일치해야 함

## 🌐 웹 인터페이스 기능

- **반응형 디자인**: 모바일과 데스크톱에서 모두 사용 가능
- **일괄 조회**: 여러 사업자등록번호를 한 번에 처리
- **실시간 통계**: 조회 결과를 시각적으로 표시
- **CSV 다운로드**: 브라우저에서 직접 결과 다운로드
- **API 키 저장**: 브라우저 로컬 스토리지에 API 키 저장

## ⚠️ 주의사항

1. **API 키 보안**: API 키를 코드에 하드코딩하지 마세요
2. **호출 제한**: 공공데이터포털 API는 일일 호출 제한이 있습니다
3. **개인정보 보호**: 조회 결과에는 개인정보가 포함될 수 있으니 적절히 관리하세요
4. **최신 정보**: API 응답은 실시간이 아닐 수 있으니 참고용으로만 사용하세요

## 🐛 문제 해결

### 자주 발생하는 오류

1. **"API 키가 필요합니다"**
   - API 키를 올바르게 입력했는지 확인
   - 환경변수 `BUSINESS_API_KEY` 설정 확인

2. **"유효하지 않은 사업자등록번호"**
   - 10자리 숫자인지 확인
   - 체크섬이 올바른지 확인

3. **"네트워크 오류"**
   - 인터넷 연결 상태 확인
   - 방화벽 설정 확인

## 📄 라이선스

이 프로젝트는 교육 및 연구 목적으로 제작되었습니다. 상업적 이용 시에는 별도의 라이선스가 필요할 수 있습니다.

## 🤝 기여하기

버그 신고나 기능 개선 제안은 언제나 환영합니다!

## 📞 지원

- 공공데이터포털 고객센터: 1644-3210
- 국세청 사업자등록번호 조회: https://teht.hometax.go.kr

---

**면책조항**: 이 도구는 정보 제공 목적으로만 사용되며, 공식적인 사업자 상태 확인은 관련 기관에 직접 문의하시기 바랍니다.
