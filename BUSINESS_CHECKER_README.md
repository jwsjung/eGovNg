# 사업자 휴폐업 조회 시스템

국세청 사업자등록정보 진위확인 서비스를 이용한 사업자 휴폐업 상태 조회 파이썬 라이브러리입니다.

## 주요 기능

- ✅ 사업자등록번호 유효성 검증 (체크섬 검증 포함)
- 🔍 단일/복수 사업자 상태 조회
- 📊 조회 결과 JSON/CSV 내보내기
- 📁 파일에서 대량 사업자번호 처리
- 🕐 상세한 조회 시간 기록

## 설치 방법

### 1. 필요한 패키지 설치

```bash
pip install -r requirements.txt
```

### 2. 직접 패키지 설치

```bash
pip install requests typing-extensions
```

## 사용 방법

### 1. 기본 사용법

```python
from business_status_checker import BusinessStatusChecker

# 인스턴스 생성
checker = BusinessStatusChecker()

# 단일 사업자 조회
result = checker.check_single_business("123-45-67890")
print(result)
```

### 2. 명령행 인터페이스

```bash
python business_status_checker.py
```

메뉴 옵션:
- `1`: 단일 사업자 조회
- `2`: 파일에서 복수 사업자 조회
- `3`: 직접 입력으로 복수 사업자 조회
- `4`: 종료

### 3. 복수 사업자 조회

```python
business_numbers = [
    "123-45-67890",
    "987-65-43210",
    "555-55-55555"
]

results = checker.check_multiple_businesses(business_numbers)

# 결과를 파일로 저장
json_file = checker.export_to_json(results)
csv_file = checker.export_to_csv(results)
```

### 4. 파일에서 사업자번호 읽기

텍스트 파일 생성 (예: `business_numbers.txt`):
```
123-45-67890
987-65-43210
555-55-55555
1234567890
```

파이썬 코드:
```python
# 파일에서 사업자번호 읽기
with open('business_numbers.txt', 'r', encoding='utf-8') as f:
    business_numbers = [line.strip() for line in f if line.strip()]

# 조회 실행
results = checker.check_multiple_businesses(business_numbers)
```

## API 참조

### BusinessStatusChecker 클래스

#### 주요 메서드

##### `validate_business_number(business_number: str) -> bool`
사업자등록번호의 유효성을 검증합니다.

```python
is_valid = checker.validate_business_number("123-45-67890")
```

##### `format_business_number(business_number: str) -> str`
사업자등록번호를 표준 형식(XXX-XX-XXXXX)으로 포맷팅합니다.

```python
formatted = checker.format_business_number("1234567890")
# 결과: "123-45-67890"
```

##### `check_single_business(business_number: str) -> Dict`
단일 사업자의 상태를 조회합니다.

**반환값 구조:**
```python
{
    'business_number': '123-45-67890',      # 포맷된 사업자번호
    'raw_business_number': '1234567890',    # 원본 입력값
    'status': 'ACTIVE',                     # 상태 코드
    'status_text': '정상사업자',            # 상태 텍스트
    'message': '정상적으로 운영중인 사업자입니다.',
    'checked_at': '2024-01-01T12:00:00'     # 조회 시간
}
```

**상태 코드:**
- `ACTIVE`: 정상사업자
- `SUSPENDED`: 휴업자
- `CLOSED`: 폐업자
- `NOT_FOUND`: 미등록 사업자
- `INVALID`: 유효하지 않은 사업자번호
- `ERROR`: 조회 오류
- `UNKNOWN`: 상태 불명

##### `check_multiple_businesses(business_numbers: List[str]) -> List[Dict]`
복수 사업자의 상태를 조회합니다.

```python
results = checker.check_multiple_businesses([
    "123-45-67890",
    "987-65-43210"
])
```

##### `export_to_json(results: List[Dict], filename: str = None) -> str`
조회 결과를 JSON 파일로 저장합니다.

```python
filename = checker.export_to_json(results, "my_results.json")
```

##### `export_to_csv(results: List[Dict], filename: str = None) -> str`
조회 결과를 CSV 파일로 저장합니다.

```python
filename = checker.export_to_csv(results, "my_results.csv")
```

## 예제 실행

### 예제 코드 실행
```bash
python example_usage.py
```

예제에는 다음 기능들이 포함되어 있습니다:
- 사업자등록번호 유효성 검증 테스트
- 단일/복수 사업자 조회 테스트  
- API 응답 파싱 테스트
- 파일 처리 테스트

## 에러 처리

### 일반적인 에러 상황

1. **유효하지 않은 사업자등록번호**
   ```python
   result = checker.check_single_business("invalid-number")
   # result['status'] == 'INVALID'
   ```

2. **네트워크 오류**
   ```python
   # 타임아웃이나 연결 오류 시
   # result['status'] == 'ERROR'
   ```

3. **API 응답 파싱 오류**
   ```python
   # 예상하지 못한 응답 형식일 때
   # result['status'] == 'PARSE_ERROR'
   ```

### 예외 처리 예제

```python
try:
    result = checker.check_single_business("123-45-67890")
    
    if result['status'] == 'ACTIVE':
        print("정상 운영 중인 사업자입니다.")
    elif result['status'] == 'SUSPENDED':
        print("현재 휴업 중인 사업자입니다.")
    elif result['status'] == 'CLOSED':
        print("폐업된 사업자입니다.")
    elif result['status'] == 'INVALID':
        print("유효하지 않은 사업자등록번호입니다.")
    else:
        print(f"조회 실패: {result['message']}")
        
except Exception as e:
    print(f"예외 발생: {e}")
```

## 성능 최적화

### 대량 조회 시 주의사항

1. **요청 간격 조절**: 국세청 서버 부하를 줄이기 위해 요청 간 적절한 딜레이를 두는 것을 권장합니다.

2. **세션 재사용**: `BusinessStatusChecker` 인스턴스는 내부적으로 `requests.Session`을 사용하여 연결을 재사용합니다.

3. **배치 처리**: 대량 데이터 처리 시 적절한 단위로 나누어 처리하세요.

```python
import time

# 대량 조회 시 딜레이 추가 예제
def check_with_delay(checker, business_numbers, delay=0.5):
    results = []
    for i, number in enumerate(business_numbers):
        result = checker.check_single_business(number)
        results.append(result)
        
        if i < len(business_numbers) - 1:  # 마지막이 아닌 경우
            time.sleep(delay)
    
    return results
```

## 라이선스

이 프로젝트는 오픈소스로 제공되며, 교육 및 연구 목적으로 자유롭게 사용할 수 있습니다.

## 주의사항

- 이 도구는 국세청의 공개 API를 사용하며, API 정책 변경에 따라 동작이 중단될 수 있습니다.
- 대량 조회 시 서버에 과도한 부하를 주지 않도록 주의하세요.
- 개인정보 및 사업자 정보는 관련 법규에 따라 적절히 처리하세요.
- 상업적 용도로 사용하기 전에 국세청의 이용약관을 확인하세요.

## 문의 및 기여

버그 리포트나 기능 개선 제안은 이슈로 등록해 주시기 바랍니다.