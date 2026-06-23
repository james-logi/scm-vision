"""
CrateCheck - Vision Inspection Module
Claude Vision API를 사용한 P-Box 빵 검수 프롬프트 설계

핵심 원칙:
1. SCM 컨텍스트 주입 (기대 SKU, 수량)
2. 구조화된 JSON 출력
3. 신뢰도 점수
4. 유사 SKU 혼동 가능성 체크
5. 표면/추정 분리
"""

import base64
import json
from pathlib import Path

try:
    import anthropic
except ImportError:
    anthropic = None  # 프롬프트 미리보기는 가능


# ===========================================
# 시스템 프롬프트 - Claude의 역할 정의
# ===========================================
SYSTEM_PROMPT = """당신은 베이커리 공장 물류센터의 검수 비전 시스템입니다.
P-Box(플라스틱 박스)에 담긴 빵을 위에서 촬영한 이미지를 분석합니다.

당신의 임무:
1. 박스 안에 보이는 빵의 종류와 수량을 정확히 식별
2. 표면에 보이는 빵과, 박스 깊이를 고려한 총 추정 수량을 분리
3. 외관이 유사한 SKU가 있을 경우 혼동 가능성 명시
4. 각 판단에 대한 신뢰도 점수(0-100) 제공

당신은 항상 지정된 JSON 스키마로만 응답합니다. 자연어 설명, 마크다운, 코드블록을 포함하지 않습니다.
JSON 외 텍스트는 절대 출력하지 마세요."""


# ===========================================
# 사용자 프롬프트 빌더
# ===========================================
def build_inspection_prompt(crate_info: dict, sku_master: list) -> str:
    """
    검수 요청 프롬프트 생성

    crate_info: {
        'crate_id': 'CRT-...',
        'expected_sku_id': 'SKU-001',
        'expected_sku_name': '초코크림빵',
        'expected_qty': 10,
    }
    sku_master: 전체 SKU 마스터 (유사 SKU 식별용)
    """

    # 기대 SKU와 외관이 유사할 수 있는 SKU 찾기
    expected_sku = next(
        (s for s in sku_master if s['sku_id'] == crate_info['expected_sku_id']),
        None
    )
    similar_sku_ids = (expected_sku.get('similar_skus') or '').split(',')
    similar_sku_ids = [s.strip() for s in similar_sku_ids if s.strip()]

    similar_skus_info = []
    for sid in similar_sku_ids:
        sim = next((s for s in sku_master if s['sku_id'] == sid), None)
        if sim:
            similar_skus_info.append(f"- {sim['sku_id']}: {sim['sku_name']} ({sim['category']})")

    similar_block = "\n".join(similar_skus_info) if similar_skus_info else "(없음)"

    # 전체 SKU 목록 (오인식 가능성 체크용)
    all_skus_block = "\n".join([
        f"- {s['sku_id']}: {s['sku_name']} ({s['category']})"
        for s in sku_master
    ])

    prompt = f"""아래 P-Box를 검수해주세요.

## 검수 대상 정보
- P-Box ID: {crate_info['crate_id']}
- 기대 SKU: {crate_info['expected_sku_id']} ({crate_info['expected_sku_name']})
- 기대 수량: {crate_info['expected_qty']}개

## ⚠️ 외관 유사 SKU (혼입 가능성 주의)
{similar_block}

## 전체 SKU 마스터 (오인식 가능성 체크용)
{all_skus_block}

## 응답 JSON 스키마
{{
  "crate_id": "{crate_info['crate_id']}",
  "surface_count": {{
    "<SKU_ID>": <표면에 보이는 수량>,
    ...
  }},
  "estimated_total": {{
    "<SKU_ID>": <박스 깊이·배열 패턴 기반 총 추정 수량>,
    ...
  }},
  "primary_sku": "<가장 많이 인식된 SKU_ID>",
  "primary_count": <primary_sku의 estimated_total 값>,
  "expected_match": <true/false: 기대 SKU와 일치하는가>,
  "qty_match": <true/false: 기대 수량과 일치하는가>,
  "confidence": <전체 판단 신뢰도 0-100>,
  "contamination_risk": {{
    "detected": <true/false: 다른 SKU 혼입 발견>,
    "suspected_skus": ["<SKU_ID>", ...],
    "reasoning": "<혼입 의심 근거 한국어 한 문장>"
  }},
  "verdict": "<OK | NG_QTY_SHORT | NG_QTY_EXCESS | NG_SKU_MISMATCH | NG_CONTAMINATION | NG_UNCLEAR>",
  "recommendation": "<작업자에게 보낼 한국어 안내 문장 (간결, 행동지향)>"
}}

## verdict 결정 규칙
- OK: 기대 SKU 일치 + 기대 수량 일치 + 혼입 없음
- NG_QTY_SHORT: 기대 SKU 맞으나 수량 부족
- NG_QTY_EXCESS: 기대 SKU 맞으나 수량 초과
- NG_SKU_MISMATCH: 기대와 완전히 다른 SKU
- NG_CONTAMINATION: 기대 SKU + 다른 SKU 혼입
- NG_UNCLEAR: 이미지 품질 등으로 판단 불가 (신뢰도 60 미만)

JSON만 응답하세요."""

    return prompt


# ===========================================
# Claude Vision 호출 함수
# ===========================================
def inspect_crate_image(
    image_path: str,
    crate_info: dict,
    sku_master: list,
    client=None,
):
    """
    P-Box 이미지 검수 실행

    Returns: 검수 결과 dict (위 JSON 스키마)
    """
    if client is None:
        client = anthropic.Anthropic()

    # 이미지 인코딩
    image_data = base64.standard_b64encode(
        Path(image_path).read_bytes()
    ).decode("utf-8")

    # 파일 확장자로 미디어 타입 결정
    ext = Path(image_path).suffix.lower()
    media_type = {
        '.jpg': 'image/jpeg',
        '.jpeg': 'image/jpeg',
        '.png': 'image/png',
        '.webp': 'image/webp',
    }.get(ext, 'image/jpeg')

    # 프롬프트 생성
    user_prompt = build_inspection_prompt(crate_info, sku_master)

    # API 호출
    response = client.messages.create(
        model="claude-opus-4-5",  # Vision 정확도가 가장 중요한 부분
        max_tokens=1500,
        system=SYSTEM_PROMPT,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": media_type,
                            "data": image_data,
                        },
                    },
                    {
                        "type": "text",
                        "text": user_prompt,
                    },
                ],
            }
        ],
    )

    # JSON 파싱
    raw_text = response.content[0].text.strip()

    # 안전한 JSON 추출 (혹시 마크다운 코드블록이 끼면 제거)
    if raw_text.startswith("```"):
        raw_text = raw_text.split("```")[1]
        if raw_text.startswith("json"):
            raw_text = raw_text[4:]
        raw_text = raw_text.strip()

    try:
        result = json.loads(raw_text)
    except json.JSONDecodeError as e:
        # 디버깅용: 실패 시 원본 반환
        result = {
            "error": f"JSON parse failed: {e}",
            "raw_response": raw_text,
            "verdict": "NG_UNCLEAR",
            "confidence": 0,
        }

    return result


# ===========================================
# 검수 결과 → UX 메시지 변환
# ===========================================
VERDICT_DISPLAY = {
    "OK": {
        "emoji": "✅",
        "label": "정상",
        "color": "green",
        "action": "출고 가능",
    },
    "NG_QTY_SHORT": {
        "emoji": "⚠️",
        "label": "수량 부족",
        "color": "orange",
        "action": "빵 추가 후 재검수",
    },
    "NG_QTY_EXCESS": {
        "emoji": "⚠️",
        "label": "수량 초과",
        "color": "orange",
        "action": "초과분 제거 후 재검수",
    },
    "NG_SKU_MISMATCH": {
        "emoji": "🚨",
        "label": "SKU 불일치",
        "color": "red",
        "action": "박스 라벨 재확인",
    },
    "NG_CONTAMINATION": {
        "emoji": "🚨",
        "label": "다른 빵 혼입",
        "color": "red",
        "action": "혼입 빵 분리 작업",
    },
    "NG_UNCLEAR": {
        "emoji": "❓",
        "label": "판독 불가",
        "color": "gray",
        "action": "재촬영 필요",
    },
}


# ===========================================
# Mock 모드 - 비용 0원으로 데모 동작
# ===========================================
import time
import hashlib

def inspect_crate_mock(
    image_path: str,
    crate_info: dict,
    sku_master: list,
    mock_dir: str = "data",
    simulate_delay: float = 1.2,
) -> dict:
    """
    실제 API 호출 없이 사전 저장된 응답을 재생.

    매칭 규칙:
    1. crate_id가 'CRT-DEMO-001'이면 정상 응답
    2. crate_id가 'CRT-DEMO-002'이면 수량부족 응답
    3. 파일명에 'short' / 'shortage' / '부족' 포함 → 수량부족
    4. 파일명에 'normal' / '정상' 포함 → 정상
    5. 그 외: 파일 해시 짝/홀수로 분기 (랜덤성)
    """
    # 데모 효과를 위한 지연 (실제 API 호출처럼 보이게)
    if simulate_delay > 0:
        time.sleep(simulate_delay)

    image_name = Path(image_path).stem.lower()
    crate_id = crate_info.get('crate_id', '').upper()

    # 파일명 또는 crate_id 기반 매칭
    is_short = (
        'short' in image_name
        or 'shortage' in image_name
        or '부족' in image_name
        or crate_id.endswith('002')
    )

    is_normal = (
        'normal' in image_name
        or '정상' in image_name
        or crate_id.endswith('001')
    )

    # 결정되지 않으면 파일 해시로 랜덤 분기
    if not is_short and not is_normal:
        try:
            file_hash = hashlib.md5(Path(image_path).read_bytes()).hexdigest()
            is_short = int(file_hash[0], 16) % 2 == 1
        except Exception:
            is_short = False

    # 해당하는 mock 파일 로드
    mock_file = (
        f"{mock_dir}/mock_response_short.json"
        if is_short
        else f"{mock_dir}/mock_response_normal.json"
    )

    with open(mock_file, 'r', encoding='utf-8') as f:
        mock_data = json.load(f)

    result = mock_data['inspection_result']

    # crate_id를 실제 crate_info의 값으로 덮어쓰기 (재사용 가능하게)
    result['crate_id'] = crate_info.get('crate_id', result.get('crate_id'))

    return result


# ===========================================
# 통합 진입점 - 비용 0원 모드 전용
# ===========================================
# ⚠️ 본 시스템은 학내 발표·시뮬레이션을 위한 캡스톤 프로젝트입니다.
#    Real API 호출은 의도적으로 차단되어 있으며, 모든 검수는 사전에
#    Claude.ai로 검증한 응답을 재생하는 방식으로 동작합니다.
#    이는 비용 0원, 인터넷 의존성 없음, 결과 일관성 100% 확보를 위함입니다.
# ===========================================

# 비용 발생 방지를 위한 안전장치
COST_GUARD_ENABLED = True  # 절대 False로 바꾸지 마세요


def inspect_crate(
    image_path: str,
    crate_info: dict,
    sku_master: list,
    response_dir: str = "data/vision_responses",
) -> dict:
    """
    검수 실행 통합 진입점.

    사전에 저장된 Vision 응답을 조회하여 반환합니다.
    실제 API 호출이 발생하지 않으므로 비용이 들지 않습니다.

    응답 라이브러리:
      data/vision_responses/{image_filename}.json

    응답이 없으면 inspect_crate_mock으로 폴백 (정상/부족 더미 응답)
    """
    # 1차: 실제 이미지 파일에 대응하는 사전 검증 응답 조회
    image_name = Path(image_path).stem
    response_file = Path(response_dir) / f"{image_name}.json"

    if response_file.exists():
        # 사전 검증된 응답 사용 (Claude.ai에서 받은 진짜 결과)
        with open(response_file, "r", encoding="utf-8") as f:
            response_data = json.load(f)

        # 자연스러운 데모를 위한 짧은 지연
        time.sleep(1.2)

        result = response_data.get("inspection_result", response_data)
        result["crate_id"] = crate_info.get("crate_id", result.get("crate_id"))
        result["_source"] = "verified_library"  # 디버깅용: 응답 출처 표시
        return result

    # 2차: 시나리오 기반 더미 응답 (정상 / 수량부족)
    return inspect_crate_mock(image_path, crate_info, sku_master, mock_dir="data")


def _blocked_real_api_call(*args, **kwargs):
    """
    Real API 호출 시도를 차단합니다.
    학내 발표용 캡스톤이라 API 비용을 발생시키지 않습니다.
    """
    raise RuntimeError(
        "🚫 비용 발생 방지: Real Claude API 호출은 차단되어 있습니다.\n"
        "   본 시스템은 사전 검증된 응답 라이브러리만 사용합니다.\n"
        "   - 응답 추가는 Claude.ai 인터페이스에서 받은 결과를\n"
        "     data/vision_responses/{이미지파일명}.json 으로 저장하세요.\n"
        "   - 운영 환경 코드는 inspect_crate_image()에 보존되어 있습니다."
    )


# Real API 함수를 차단 wrapper로 덮어쓰기
if COST_GUARD_ENABLED:
    inspect_crate_image_original = inspect_crate_image  # 코드 참고용 보존
    inspect_crate_image = _blocked_real_api_call


# ===========================================
# 테스트용 더미 데이터 (실제 이미지 없이 검증)
# ===========================================
DEMO_CRATE = {
    'crate_id': 'CRT-20260516-001',
    'expected_sku_id': 'SKU-001',
    'expected_sku_name': '초코크림빵',
    'expected_qty': 10,
}

DEMO_SKU_MASTER = [
    {'sku_id': 'SKU-001', 'sku_name': '초코크림빵', 'category': '크림빵', 'similar_skus': 'SKU-003'},
    {'sku_id': 'SKU-002', 'sku_name': '단팥빵', 'category': '앙금빵', 'similar_skus': 'SKU-005'},
    {'sku_id': 'SKU-003', 'sku_name': '모카크림빵', 'category': '크림빵', 'similar_skus': 'SKU-001'},
    {'sku_id': 'SKU-004', 'sku_name': '소보로빵', 'category': '토핑빵', 'similar_skus': 'SKU-006'},
    {'sku_id': 'SKU-005', 'sku_name': '통팥빵', 'category': '앙금빵', 'similar_skus': 'SKU-002'},
    {'sku_id': 'SKU-006', 'sku_name': '땅콩소보로', 'category': '토핑빵', 'similar_skus': 'SKU-004'},
    {'sku_id': 'SKU-007', 'sku_name': '햄치즈빵', 'category': '조리빵', 'similar_skus': ''},
    {'sku_id': 'SKU-008', 'sku_name': '단호박식빵', 'category': '식빵', 'similar_skus': ''},
]


if __name__ == "__main__":
    # 프롬프트가 어떻게 생성되는지 미리보기
    print("=" * 60)
    print("SYSTEM PROMPT:")
    print("=" * 60)
    print(SYSTEM_PROMPT)
    print()
    print("=" * 60)
    print("USER PROMPT (예시):")
    print("=" * 60)
    print(build_inspection_prompt(DEMO_CRATE, DEMO_SKU_MASTER))
