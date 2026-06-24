"""
data_config.py — 시스템 공통 데이터 설정
"""

import random

# ── 핵심 파라미터 ──
TOTAL_SKU_TYPES        = 60       # 전체 빵 종류
DAILY_PRODUCTION_EA    = 50_000   # 하루 총 생산량 (낱개 EA)
AVG_PRICE_PER_EA       = 2_000    # 빵 1개 평균 소비자가 (원)
PBOX_UNIT              = 12       # 기본값 (SKU별 실제 값은 SKU_SPECS 참고)
DAILY_PRODUCTION_PBOX  = DAILY_PRODUCTION_EA // PBOX_UNIT

# ── SKU별 스펙 ──
# pack_size     : 판매 묶음 단위 (EA)
# packs_per_box : P-Box당 묶음 수
# ea_per_box    : P-Box당 낱개 수 (= pack_size × packs_per_box)
# unit          : 검수 표시 단위
SKU_SPECS = {
    "버거킹 햄버거번": {
        "pack_size":     6,       # 6개 = 1묶음
        "packs_per_box": 3,       # P-Box = 3묶음
        "ea_per_box":    18,      # = 6 × 3
        "unit":          "묶음",
        "price_per_pack": 6 * AVG_PRICE_PER_EA,  # 묶음당 소비자가
    },
    "곰곰 데일리식빵": {
        "pack_size":     1,       # 낱개 판매
        "packs_per_box": 8,       # P-Box = 8EA
        "ea_per_box":    8,
        "unit":          "EA",
        "price_per_pack": AVG_PRICE_PER_EA,
    },
}

# 기본 스펙 (미등록 SKU용)
DEFAULT_SKU_SPEC = {
    "pack_size": 1, "packs_per_box": 12,
    "ea_per_box": 12, "unit": "EA",
    "price_per_pack": AVG_PRICE_PER_EA,
}

def get_sku_spec(sku_name: str) -> dict:
    return SKU_SPECS.get(sku_name, DEFAULT_SKU_SPEC)

def get_display_unit(sku_name: str) -> str:
    return get_sku_spec(sku_name)["unit"]

def get_packs_per_box(sku_name: str) -> int:
    return get_sku_spec(sku_name)["packs_per_box"]

def get_ea_per_box(sku_name: str) -> int:
    return get_sku_spec(sku_name)["ea_per_box"]

def calc_savings(ng_count: int, sku_name: str = None) -> int:
    """
    NG 차단 절감액 계산
    NG 1건 = P-Box 1개 = packs_per_box × price_per_pack
    """
    if sku_name:
        spec = get_sku_spec(sku_name)
        return ng_count * spec["packs_per_box"] * spec["price_per_pack"]
    # SKU 미지정: 평균 계산
    total = sum(
        s["packs_per_box"] * s["price_per_pack"]
        for s in SKU_SPECS.values()
    ) / len(SKU_SPECS)
    return int(ng_count * total)

def calc_iri(ng_count: int, total_count: int) -> float:
    if total_count == 0:
        return 0.0
    return round(ng_count / total_count * 100, 2)

def get_sku_allocation(sku_names: list, seed: int = 42) -> dict:
    """
    등록 SKU별 하루 생산량 할당 (EA 기준)
    총합 = DAILY_PRODUCTION_EA × (등록수/전체 60종)
    """
    rng = random.Random(seed)
    n = len(sku_names)
    if n == 0:
        return {}

    base_ea     = DAILY_PRODUCTION_EA // TOTAL_SKU_TYPES
    ratio       = n / TOTAL_SKU_TYPES
    target_total = int(DAILY_PRODUCTION_EA * ratio)
    raw         = [base_ea * (0.6 + rng.random() * 0.8) for _ in sku_names]
    total_raw   = sum(raw)

    allocation = {}
    for i, sku in enumerate(sku_names):
        ea   = int(raw[i] / total_raw * target_total)
        spec = get_sku_spec(sku)
        allocation[sku] = {
            "ea":    ea,
            "pbox":  ea // spec["ea_per_box"],
            "packs": ea // spec["pack_size"],
            "unit":  spec["unit"],
        }
    return allocation

def get_sku_allocation_pbox(sku_names: list, seed: int = 42) -> dict:
    alloc = get_sku_allocation(sku_names, seed)
    return {k: v["pbox"] for k, v in alloc.items()}
