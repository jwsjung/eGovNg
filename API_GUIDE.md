# 사업자휴폐업조회 API 가이드

## 개요

이 모듈은 한국 국세청의 사업자등록번호 상태조회 API를 활용하여 사업자의 휴업/폐업 상태를 조회하는 기능을 제공합니다.

## 설치 및 설정

### 1. 의존성 설치

```bash
pip install -r requirements.txt
```

또는 개별 설치:

```bash
pip install requests lxml
```

### 2. 모듈 import

```python
from business_status_checker import BusinessStatusChecker
```

## 주요 기능

### BusinessStatusChecker 클래스

사업자휴폐업조회의 핵심 클래스입니다.

#### 초기화

```python
checker = BusinessStatusChecker()
```

#### 주요 메소드

##### 1. `validate_business_number(business_number: str) -> bool`

사업자등록번호의 유효성을 검사합니다.

**매개변수:**
- `business_number` (str): 검사할 사업자등록번호

**반환값:**
- `bool`: 유효한 사업자등록번호인지 여부

**예제:**
```python
checker = BusinessStatusChecker()
is_valid = checker.validate_business_number("110-81-25813")
print(is_valid)  # True 또는 False
```

##### 2. `format_business_number(business_number: str) -> str`

사업자등록번호를 표준 형식(xxx-xx-xxxxx)으로 포맷팅합니다.

**매개변수:**
- `business_number` (str): 포맷팅할 사업자등록번호

**반환값:**
- `str`: 포맷팅된 사업자등록번호

**예제:**
```python
formatted = checker.format_business_number("1108125813")
print(formatted)  # "110-81-25813"
```

##### 3. `check_business_status(business_number: str) -> Dict[str, Any]`

개별 사업자등록번호의 상태를 조회합니다.

**매개변수:**
- `business_number` (str): 조회할 사업자등록번호

**반환값:**
- `Dict[str, Any]`: 조회 결과 딕셔너리

**응답 구조:**
```python
{
    'success': bool,              # 조회 성공 여부
    'business_number': str,       # 조회한 사업자등록번호
    'status': str,               # 사업자 상태 ('정상', '휴업', '폐업', '미등록' 등)
    'company_name': str,         # 회사명 (조회된 경우)
    'registration_date': str,    # 개업일자
    'closure_date': str,         # 폐업일자 (폐업된 경우)
    'message': str,              # 응답 메시지
    'query_time': str,           # 조회 시간
    'error': str                 # 오류 메시지 (오류 발생시)
}
```

**예제:**
```python
result = checker.check_business_status("110-81-25813")
if result['success']:
    print(f"상태: {result['status']}")
    print(f"메시지: {result['message']}")
else:
    print(f"오류: {result['error']}")
```

##### 4. `check_multiple_businesses(business_numbers: list) -> Dict[str, Dict[str, Any]]`

여러 사업자등록번호를 일괄 조회합니다.

**매개변수:**
- `business_numbers` (list): 조회할 사업자등록번호 리스트

**반환값:**
- `Dict[str, Dict[str, Any]]`: 각 사업자번호별 조회 결과

**예제:**
```python
numbers = ["110-81-25813", "123-45-67890"]
results = checker.check_multiple_businesses(numbers)

for business_number, result in results.items():
    print(f"번호: {business_number}")
    print(f"상태: {result.get('status', '오류')}")
```

## 사용 예제

### 기본 사용법

```python
from business_status_checker import BusinessStatusChecker

# 인스턴스 생성
checker = BusinessStatusChecker()

# 단일 조회
result = checker.check_business_status("110-81-25813")
print(result)
```

### 여러 번호 일괄 조회

```python
# 여러 번호 조회
business_numbers = [
    "110-81-25813",
    "123-45-67890",
    "987-65-43210"
]

results = checker.check_multiple_businesses(business_numbers)

# 결과 처리
for business_number, result in results.items():
    if result['success']:
        print(f"{business_number}: {result['status']}")
    else:
        print(f"{business_number}: 오류 - {result['error']}")
```

### 상태별 분류

```python
# 상태별로 분류
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
```

## 상태 코드

조회 결과로 반환되는 주요 상태 코드:

- **정상**: 현재 정상 영업 중인 사업자
- **휴업**: 현재 휴업 상태인 사업자
- **폐업**: 폐업한 사업자
- **미등록**: 등록되지 않은 사업자등록번호
- **미확인**: 상태를 확인할 수 없는 경우

## 오류 처리

### 일반적인 오류 유형

1. **유효하지 않은 사업자등록번호**
   ```python
   result = checker.check_business_status("123-45-67890")
   # result['error'] = "유효하지 않은 사업자등록번호입니다."
   ```

2. **네트워크 오류**
   ```python
   # 인터넷 연결 문제 등
   # result['error'] = "네트워크 오류: ..."
   ```

3. **API 응답 오류**
   ```python
   # API 서버 문제 등
   # result['error'] = "조회 중 오류가 발생했습니다."
   ```

### 오류 처리 패턴

```python
result = checker.check_business_status(business_number)

if result['success']:
    # 성공적인 조회
    print(f"상태: {result['status']}")
    print(f"메시지: {result['message']}")
    
    if result['company_name']:
        print(f"사업자명: {result['company_name']}")
else:
    # 오류 발생
    print(f"조회 실패: {result.get('error', '알 수 없는 오류')}")
```

## 사업자등록번호 유효성 검사

### 체크섬 알고리즘

한국의 사업자등록번호는 10자리 숫자로 구성되며, 마지막 자리는 체크섬입니다.

```python
# 유효성 검사 예제
test_numbers = [
    "110-81-25813",  # 유효
    "123-45-67890",  # 무효 (체크섬 오류)
    "1108125813",    # 유효 (하이픈 없음)
    "abc-de-fghij",  # 무효 (숫자가 아님)
]

for number in test_numbers:
    is_valid = checker.validate_business_number(number)
    print(f"{number}: {'유효' if is_valid else '무효'}")
```

## 성능 고려사항

### 요청 제한

- API 호출에는 적절한 지연(delay)을 두는 것이 좋습니다.
- 대량 조회시에는 배치 처리를 고려하세요.

### 캐싱

자주 조회하는 사업자등록번호의 경우 결과를 캐싱하여 성능을 향상시킬 수 있습니다.

```python
import time
from functools import lru_cache

class CachedBusinessStatusChecker(BusinessStatusChecker):
    @lru_cache(maxsize=1000)
    def check_business_status_cached(self, business_number: str):
        return self.check_business_status(business_number)
```

## 주의사항

1. **개인정보 보호**: 사업자등록번호는 개인정보에 해당할 수 있으므로 적절한 보안 조치를 취하세요.

2. **API 사용 정책**: 국세청 API의 사용 정책을 준수하세요.

3. **네트워크 연결**: 인터넷 연결이 필요합니다.

4. **결과 신뢰성**: API 결과는 참조용이며, 법적 효력을 갖지 않습니다.

## 문제 해결

### 자주 발생하는 문제

1. **"유효하지 않은 사업자등록번호" 오류**
   - 사업자등록번호 형식을 확인하세요 (10자리 숫자)
   - 체크섬이 올바른지 확인하세요

2. **네트워크 연결 오류**
   - 인터넷 연결을 확인하세요
   - 방화벽 설정을 확인하세요

3. **API 응답 오류**
   - 잠시 후 다시 시도해보세요
   - API 서버 상태를 확인하세요

### 디버깅

```python
import logging

# 로깅 설정
logging.basicConfig(level=logging.DEBUG)

# 상세한 오류 정보 확인
try:
    result = checker.check_business_status("110-81-25813")
except Exception as e:
    logging.error(f"조회 중 오류 발생: {e}")
```

## 라이선스

이 모듈은 교육 및 개발 목적으로 제공됩니다. 상업적 사용시에는 관련 법규를 확인하시기 바랍니다.

## 지원

문제가 발생하거나 개선 사항이 있으시면 이슈를 등록해주세요.