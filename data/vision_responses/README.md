# Vision Responses Library

> 이 폴더는 **사전 검증된 Claude Vision 응답**을 저장합니다.
> 본 시스템은 비용 0원 정책에 따라 Real API를 호출하지 않으며,
> 모든 검수 결과는 이 폴더의 JSON 파일에서 재생됩니다.

---

## 📁 파일 명명 규칙

이미지 파일명(확장자 제외)을 그대로 JSON 파일명으로 사용합니다.

```
업로드 이미지: 이미지_0072_20260429065523.jpg
응답 JSON  : 이미지_0072_20260429065523.json
```

이렇게 하면 `inspect_crate()`가 이미지 파일명을 키로 자동 매칭합니다.

---

## 🛠 응답 라이브러리 추가 절차 (D5 작업)

### 1단계 — Claude.ai 열기
[claude.ai](https://claude.ai)에 접속합니다. (Pro 미구독 무료 계정도 가능)

### 2단계 — 이미지 업로드
검수할 박스 이미지를 1장 업로드합니다.

### 3단계 — 프롬프트 입력
`vision_inspector.py`의 `build_inspection_prompt()` 함수로 생성한 프롬프트를 그대로 복사해서 붙여넣습니다.

빠른 생성 방법:
```python
from vision_inspector import build_inspection_prompt
from sku_registry import SkuRegistry

reg = SkuRegistry()
sku = reg.get("SKU-001")  # 또는 SKU-002

crate_info = {
    "crate_id": "CRT-20260429-001",
    "expected_sku_id": sku.sku_id,
    "expected_sku_name": sku.sku_name,
    "expected_qty": sku.expected_total_units(),
}

sku_list = [
    {
        "sku_id": s.sku_id,
        "sku_name": s.sku_name,
        "category": s.category,
        "similar_skus": "",
    }
    for s in reg.list_active()
]

print(build_inspection_prompt(crate_info, sku_list))
```

### 4단계 — Claude.ai 응답 받기
Claude가 JSON 형식으로 답변합니다. JSON만 복사합니다.

### 5단계 — 파일로 저장
응답 JSON을 다음 구조로 감싸서 저장합니다:

```json
{
  "image_filename": "이미지_0072_20260429065523.jpg",
  "scenario_name": "정상 적재 (햄버거번 24개)",
  "ground_truth": {
    "sku_id": "SKU-001",
    "total_units": 24
  },
  "verified_at": "2026-05-24",
  "verified_by": "James Jeong via Claude.ai",
  "inspection_result": {
    "crate_id": "CRT-20260429-001",
    "surface_count": { "SKU-001": 16 },
    "estimated_total": { "SKU-001": 24 },
    "primary_sku": "SKU-001",
    "primary_count": 24,
    "expected_match": true,
    "qty_match": true,
    "confidence": 93,
    "contamination_risk": {
      "detected": false,
      "suspected_skus": [],
      "reasoning": "혼입 없음"
    },
    "verdict": "OK",
    "recommendation": "정상 적재 확인. 출고 가능합니다."
  }
}
```

### 6단계 — 검증
```bash
python test_cost_guard.py
```
응답이 `verified_library`로 매칭되는지 확인합니다.

---

## 📊 권장 작업 분량

D5 1시간 안에 처리 가능한 범위:

| 이미지 수 | 작업 시간 | 권장도 |
|----------|----------|--------|
| 2장 (각 SKU 1장씩) | 15분 | 최소한 |
| 4장 (각 SKU 정상+NG) | 30분 | **권장** |
| 6장 이상 | 45분+ | 시간 여유 시 |

**현실적 추천**: 발표 시연용 4장만 작업하시고, 시연 시나리오에 맞추는 게 가장 효율적입니다.

---

## 💡 정직한 발표 멘트

발표에서 이 구조를 정직하게 설명할 수 있습니다:

> "본 프로토타입은 학내 발표용으로 비용 0원 정책 하에 개발되었습니다.
> Vision 검수 응답은 사전에 Claude.ai 인터페이스를 통해 검증된
> 결과를 라이브러리화하여 활용합니다.
>
> 운영 환경에서는 동일한 프롬프트로 Claude API를 직접 호출하도록
> `inspect_crate_image()` 함수가 그대로 준비되어 있으며,
> 환경 변수 하나의 변경으로 활성화됩니다."

학술적이고 실무적이며, 진정성 있는 표현입니다.

---

## 🚫 비용 발생 방지 안전장치

`vision_inspector.py`의 `COST_GUARD_ENABLED = True`는 절대 변경하지 마세요.
이 설정이 Real API 호출을 차단합니다.

차단 동작 확인:
```bash
python test_cost_guard.py
```
