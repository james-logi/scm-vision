"""
출고 재고 검수 관리 - 30일치 시뮬레이션 데이터 생성기 (v2)
=============================================================

시나리오 (재정의):
  생산동에서 LINE-1 ~ LINE-6 (6개 라인)이 각각 P-Box 단위로
  빵을 적재해 컨베이어를 통해 물류동으로 흘려보낸다.
  물류동 입고 게이트에서 AI 비전이 P-Box의 SKU와 수량을
  자동 검수하여 WMS에 실시간 반영한다.

생성 데이터:
  inspection_history.csv : 30일치 입고 검수 이력
  daily_summary.csv       : 일자별 집계
  line_stats.csv          : 라인별 30일 통계
"""

import csv
import random
from datetime import datetime, timedelta
from pathlib import Path
from collections import defaultdict

random.seed(42)

# ============================================================
# 설정
# ============================================================
START_DATE = datetime(2026, 4, 16, 0, 0)
DAYS = 30
OUTPUT_DIR = Path(__file__).parent

SKUS = [
    {"id": "SKU-001", "name": "버거킹 햄버거번", "category": "햄버거번", "units_per_box": 18},
    {"id": "SKU-002", "name": "곰곰 데일리식빵", "category": "식빵", "units_per_box": 8},
]

LINES = [
    {"id": "LINE-1", "name": "메인 라인 1", "shift": "day",
     "base_error_rate": 0.010, "primary_skus": ["SKU-001"], "throughput": "high"},
    {"id": "LINE-2", "name": "메인 라인 2", "shift": "day",
     "base_error_rate": 0.012, "primary_skus": ["SKU-001"], "throughput": "high"},
    {"id": "LINE-3", "name": "서브 라인 1", "shift": "day",
     "base_error_rate": 0.018, "primary_skus": ["SKU-001", "SKU-002"], "throughput": "mid"},
    {"id": "LINE-4", "name": "서브 라인 2", "shift": "day",
     "base_error_rate": 0.020, "primary_skus": ["SKU-001", "SKU-002"], "throughput": "mid"},
    {"id": "LINE-5", "name": "식빵 전용 라인", "shift": "day",
     "base_error_rate": 0.008, "primary_skus": ["SKU-002"], "throughput": "mid"},
    {"id": "LINE-6", "name": "야간 라인", "shift": "night",
     "base_error_rate": 0.030, "primary_skus": ["SKU-001", "SKU-002"], "throughput": "low"},
]

STORES = ["강남점", "종로점", "홍대점", "잠실점", "분당점", "수원점", "일산점", "수원공장직영점"]

SKU_STORE_AFFINITY = {
    "SKU-001": ["강남점", "분당점", "잠실점", "홍대점"],
    "SKU-002": ["종로점", "수원점", "일산점", "수원공장직영점"],
}


# ============================================================
# 오류율 계산 (시스템 관점)
# ============================================================
def get_error_probability(line, hour):
    base = line["base_error_rate"]
    multiplier = 1.0
    if line["shift"] == "night":
        if 2 <= hour < 6:
            multiplier = 1.6
    if line["shift"] == "day":
        if 14 <= hour < 16:
            multiplier = 1.3
    return base * multiplier


def get_error_type():
    roll = random.random()
    if roll < 0.70:
        return "NG_QTY_SHORT"
    elif roll < 0.85:
        return "NG_QTY_EXCESS"
    elif roll < 0.95:
        return "NG_CONTAMINATION"
    else:
        return "NG_SKU_MISMATCH"


def pick_store_for_sku(sku_id):
    if random.random() < 0.75:
        return random.choice(SKU_STORE_AFFINITY[sku_id])
    return random.choice(STORES)


# ============================================================
# 메인 생성
# ============================================================
def generate_inspections():
    inspections = []
    crate_counter = 0

    for day_offset in range(DAYS):
        current_date = START_DATE + timedelta(days=day_offset)
        is_weekend = current_date.weekday() >= 5

        for line in LINES:
            if line["throughput"] == "high":
                volume = random.randint(20, 28) if not is_weekend else random.randint(6, 12)
            elif line["throughput"] == "mid":
                volume = random.randint(12, 20) if not is_weekend else random.randint(4, 8)
            else:
                volume = random.randint(8, 14) if not is_weekend else random.randint(2, 6)

            for _ in range(volume):
                if line["shift"] == "day":
                    hour = random.choices(
                        list(range(6, 22)),
                        weights=[3, 5, 8, 9, 9, 8, 7, 6, 7, 9, 9, 7, 5, 4, 3, 2],
                    )[0]
                else:
                    hour = random.choices(
                        list(range(0, 6)) + list(range(22, 24)),
                        weights=[3, 3, 4, 4, 3, 2, 2, 2],
                    )[0]

                sku_id = random.choice(line["primary_skus"])
                sku = next(s for s in SKUS if s["id"] == sku_id)

                minute = random.randint(0, 59)
                second = random.randint(0, 59)
                inspected_at = current_date.replace(hour=hour, minute=minute, second=second)

                has_error = random.random() < get_error_probability(line, hour)
                crate_counter += 1
                crate_id = f"CRT-{current_date.strftime('%Y%m%d')}-{crate_counter % 10000:04d}"
                expected_qty = sku["units_per_box"]

                if has_error:
                    error_type = get_error_type()
                    if error_type == "NG_QTY_SHORT":
                        detected_qty = expected_qty - random.randint(1, 2)
                        detected_sku = sku_id
                        contamination = ""
                    elif error_type == "NG_QTY_EXCESS":
                        detected_qty = expected_qty + random.randint(1, 2)
                        detected_sku = sku_id
                        contamination = ""
                    elif error_type == "NG_CONTAMINATION":
                        detected_qty = expected_qty
                        detected_sku = sku_id
                        other = [s["id"] for s in SKUS if s["id"] != sku_id]
                        contamination = random.choice(other) if other else ""
                    else:
                        detected_qty = expected_qty
                        other = [s["id"] for s in SKUS if s["id"] != sku_id]
                        detected_sku = random.choice(other) if other else sku_id
                        contamination = ""
                    verdict = error_type
                    confidence = random.randint(82, 96)
                else:
                    detected_qty = expected_qty
                    detected_sku = sku_id
                    contamination = ""
                    verdict = "OK"
                    confidence = random.randint(91, 99)

                inspections.append({
                    "crate_id": crate_id,
                    "inspected_at": inspected_at.strftime("%Y-%m-%d %H:%M:%S"),
                    "line_no": line["id"],
                    "line_name": line["name"],
                    "shift": line["shift"],
                    "expected_sku": sku_id,
                    "expected_sku_name": sku["name"],
                    "expected_qty": expected_qty,
                    "detected_sku": detected_sku,
                    "detected_qty": detected_qty,
                    "contamination_sku": contamination,
                    "verdict": verdict,
                    "confidence": confidence,
                    "destination_store": pick_store_for_sku(sku_id),
                })

    return inspections


def generate_daily_summary(inspections):
    by_day = defaultdict(lambda: {"total": 0, "ng": 0, "ok": 0})
    for r in inspections:
        day = r["inspected_at"][:10]
        by_day[day]["total"] += 1
        if r["verdict"] == "OK":
            by_day[day]["ok"] += 1
        else:
            by_day[day]["ng"] += 1

    summary = []
    for day in sorted(by_day):
        d = by_day[day]
        error_rate = (d["ng"] / d["total"] * 100) if d["total"] > 0 else 0
        accuracy = (d["ok"] / d["total"] * 100) if d["total"] > 0 else 0
        summary.append({
            "date": day,
            "total_inspections": d["total"],
            "ok_count": d["ok"],
            "ng_count": d["ng"],
            "error_rate_pct": round(error_rate, 2),
            "accuracy_pct": round(accuracy, 2),
        })
    return summary


def generate_line_stats(inspections):
    by_line = defaultdict(lambda: {
        "total": 0, "ng": 0,
        "ng_by_type": defaultdict(int),
        "ng_by_hour": defaultdict(int),
        "sku_counts": defaultdict(int),
    })

    for r in inspections:
        l = r["line_no"]
        by_line[l]["total"] += 1
        by_line[l]["sku_counts"][r["expected_sku"]] += 1
        if r["verdict"] != "OK":
            by_line[l]["ng"] += 1
            by_line[l]["ng_by_type"][r["verdict"]] += 1
            hour = int(r["inspected_at"][11:13])
            by_line[l]["ng_by_hour"][hour] += 1

    stats = []
    for line in LINES:
        l_id = line["id"]
        d = by_line[l_id]
        error_rate = (d["ng"] / d["total"] * 100) if d["total"] > 0 else 0
        peak_hour = max(d["ng_by_hour"].items(), key=lambda x: x[1], default=(None, 0))[0]
        top_error = max(d["ng_by_type"].items(), key=lambda x: x[1], default=(None, 0))[0]
        primary_sku = max(d["sku_counts"].items(), key=lambda x: x[1], default=(None, 0))[0]

        if error_rate > 2.5:
            status = "주의"
        elif error_rate > 1.5:
            status = "보통"
        else:
            status = "정상"

        stats.append({
            "line_no": l_id,
            "line_name": line["name"],
            "shift": line["shift"],
            "total_inspections": d["total"],
            "ng_count": d["ng"],
            "error_rate_pct": round(error_rate, 2),
            "peak_ng_hour": peak_hour if peak_hour is not None else "",
            "top_error_type": top_error if top_error else "",
            "primary_sku": primary_sku if primary_sku else "",
            "status": status,
        })

    return stats


def save_csv(rows, path, fieldnames=None):
    if fieldnames is None and rows:
        fieldnames = list(rows[0].keys())
    with open(path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main():
    print("=" * 60)
    print("출고 재고 검수 관리 - v2 (작업자 → 라인 기반)")
    print("=" * 60)

    print(f"\n기간: {START_DATE.date()} ~ {(START_DATE + timedelta(days=DAYS-1)).date()}")
    print(f"라인: {len(LINES)}개 / SKU: {len(SKUS)}종")

    print("\n검수 이력 생성 중...")
    inspections = generate_inspections()
    print(f"  → 총 {len(inspections):,}건")

    daily = generate_daily_summary(inspections)
    lines_stats = generate_line_stats(inspections)

    print("\n파일 저장...")
    save_csv(inspections, OUTPUT_DIR / "inspection_history.csv")
    print(f"  ✓ inspection_history.csv")
    save_csv(daily, OUTPUT_DIR / "daily_summary.csv")
    print(f"  ✓ daily_summary.csv")
    save_csv(lines_stats, OUTPUT_DIR / "line_stats.csv")
    print(f"  ✓ line_stats.csv")

    total = len(inspections)
    ng = sum(1 for r in inspections if r["verdict"] != "OK")
    print(f"\n전체 검수: {total:,}건 / NG: {ng}건 ({ng/total*100:.2f}%)")

    print(f"\n라인별 통계:")
    print(f"  {'라인':<10} {'명':<18} {'시프트':<8} {'총검수':>7} {'NG':>5} {'오류율':>8} {'상태':>6}")
    print(f"  {'-'*72}")
    for s in lines_stats:
        print(
            f"  {s['line_no']:<10} {s['line_name']:<16} {s['shift']:<8} "
            f"{s['total_inspections']:>7} {s['ng_count']:>5} "
            f"{s['error_rate_pct']:>7.2f}% {s['status']:>7}"
        )

    print("\n오류 유형 분포:")
    error_types = defaultdict(int)
    for r in inspections:
        if r["verdict"] != "OK":
            error_types[r["verdict"]] += 1
    for et, cnt in sorted(error_types.items(), key=lambda x: -x[1]):
        print(f"  {et:<25} {cnt:>3}건 ({cnt/ng*100:.1f}%)")

    print("\n✅ 완료")


if __name__ == "__main__":
    main()
