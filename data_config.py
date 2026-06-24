"""
data_config.py — 시스템 공통 데이터 설정
실제 운영 파라미터 기반으로 전 페이지에서 import하여 사용
"""

import random

# ── 핵심 파라미터 ──
TOTAL_SKU_TYPES        = 60      # 전체 빵 종류
DAILY_PRODUCTION_EA    = 50_000  # 하루 총 생산량 (낱개 EA)
AVG_PRICE_PER_EA       = 2_000   # 빵 1개 평균 소비자가 (원)
PBOX_UNIT              = 12      # P-Box 1개당 빵 수량 (EA)
DAILY_PRODUCTION_PBOX  = DAILY_PRODUCTION_EA // PBOX_UNIT  # ≈ 4,167 Case/일

# ── SKU별 생산량 할당 ──
def get_sku_allocation(sku_names: list, seed: int = 42) -> dict:
    """
    등록된 SKU 목록에 대해 하루 총 생산량(EA)을 임의 할당.
    - 총합 = DAILY_PRODUCTION_EA (50,000)
    - 각 SKU 편차 ±30% (랜덤하지만 seed 고정으로 재현 가능)
    - 미등록 SKU 할당분: 나머지를 (TOTAL_SKU_TYPES - 등록수)로 예비
    """
    rng = random.Random(seed)
    n = len(sku_names)
    if n == 0:
        return {}

    # 기본 할당: 전체를 등록 SKU 수로 나눔 (미등록분 포함)
    base_ea = DAILY_PRODUCTION_EA // TOTAL_SKU_TYPES  # 833 EA / SKU 기준

    # 각 SKU에 ±40% 랜덤 변동 적용
    raw = [base_ea * (0.6 + rng.random() * 0.8) for _ in sku_names]
    total_raw = sum(raw)

    # 등록 SKU가 전체에서 차지하는 비율만큼 스케일 보정
    ratio = (n / TOTAL_SKU_TYPES)
    target_total = int(DAILY_PRODUCTION_EA * ratio)

    allocation = {}
    for i, sku in enumerate(sku_names):
        ea = int(raw[i] / total_raw * target_total)
        allocation[sku] = {
            "ea":   ea,
            "pbox": ea // PBOX_UNIT,
        }
    return allocation


def get_sku_allocation_pbox(sku_names: list, seed: int = 42) -> dict:
    """P-Box 단위 할당 반환"""
    alloc = get_sku_allocation(sku_names, seed)
    return {k: v["pbox"] for k, v in alloc.items()}


def calc_savings(ng_count: int) -> int:
    """NG 차단 절감액 계산 (NG 1건 = P-Box 1개 = PBOX_UNIT EA × AVG_PRICE)"""
    return ng_count * PBOX_UNIT * AVG_PRICE_PER_EA


def calc_iri(ng_count: int, total_count: int) -> float:
    """IRI (재고 부정확성) 계산 — NG가 발생한 비율"""
    if total_count == 0:
        return 0.0
    return round(ng_count / total_count * 100, 2)
