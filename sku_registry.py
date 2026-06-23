"""
출고 재고 검수 관리 - SKU Registry
====================================
SKU를 동적으로 등록·조회·관리하는 모듈.

핵심 설계 원칙:
1. 한 박스 = 단일 SKU만 (혼입은 NG)
2. SKU는 언제든 추가 가능 (코드 수정 불필요)
3. 두 가지 적재 구조 지원:
   - pack_based : 박스 안에 비닐 포장이 N개, 각 포장에 빵 M개 (예: 햄버거번)
   - unit_based : 박스 안에 빵 봉지가 N개 직접 적재 (예: 식빵)

사용 예시:
    registry = SkuRegistry()
    registry.register(
        sku_id="SKU-001",
        sku_name="버거킹 햄버거번",
        loading_type="pack_based",
        unit_per_pack=6,
        packs_per_box=4,
        label_text="버거킹 햄버거번",
    )
    sku = registry.get("SKU-001")
    print(sku.expected_total_units())   # 24
"""

import json
from pathlib import Path
from dataclasses import dataclass, asdict, field
from typing import Optional


# ============================================================
# 데이터 클래스
# ============================================================
@dataclass
class Sku:
    """단일 SKU 정의"""

    sku_id: str
    sku_name: str

    # 적재 구조 : "pack_based" or "unit_based"
    loading_type: str

    # ── pack_based 전용 필드 ──
    # 박스 안에 비닐 포장이 들어가고, 그 포장 안에 빵이 들어있는 구조
    unit_per_pack: Optional[int] = None      # 포장 1개당 빵 개수 (예: 6)
    packs_per_box: Optional[int] = None      # 박스 1개당 포장 수 (예: 4)

    # ── unit_based 전용 필드 ──
    # 박스 안에 빵 봉지가 곧 1단위 (식빵 1봉 = 1개)
    units_per_box: Optional[int] = None      # 박스 1개당 봉지 수 (예: 8)

    # ── 공통 검증 정보 ──
    label_text: str = ""                     # OCR로 매칭할 라벨 텍스트
    visual_features: str = ""                # Claude Vision에 줄 시각적 특징
    category: str = ""                       # 분류 (식빵, 햄버거번 등)
    expiry_format: str = "YY.MM.DD"          # 유통기한 OCR 형식
    reference_images: list = field(default_factory=list)  # 참조 이미지 경로

    # ── 메타 정보 ──
    registered_at: str = ""                  # 등록 일시
    is_active: bool = True                   # 사용 중 여부

    def __post_init__(self):
        """등록 시 적재 구조 유효성 검증"""
        if self.loading_type == "pack_based":
            if self.unit_per_pack is None or self.packs_per_box is None:
                raise ValueError(
                    f"pack_based 타입은 unit_per_pack과 packs_per_box가 필요합니다 ({self.sku_id})"
                )
        elif self.loading_type == "unit_based":
            if self.units_per_box is None:
                raise ValueError(
                    f"unit_based 타입은 units_per_box가 필요합니다 ({self.sku_id})"
                )
        else:
            raise ValueError(
                f"loading_type은 'pack_based' 또는 'unit_based'여야 합니다 ({self.loading_type})"
            )

    def expected_total_units(self) -> int:
        """박스 1개에 기대되는 총 빵 개수 (EA 단위)"""
        if self.loading_type == "pack_based":
            return self.unit_per_pack * self.packs_per_box
        else:
            return self.units_per_box

    def display_structure(self) -> str:
        """발표·UX에 표시할 적재 구조 설명"""
        if self.loading_type == "pack_based":
            return f"{self.packs_per_box}개 포장 × {self.unit_per_pack}개입 = 총 {self.expected_total_units()}개"
        else:
            return f"{self.units_per_box}봉지 = 총 {self.expected_total_units()}개"


# ============================================================
# Registry
# ============================================================
class SkuRegistry:
    """SKU 등록·조회·저장 관리"""

    def __init__(self, storage_path: str = "data/sku_registry.json"):
        self.storage_path = Path(storage_path)
        self._skus: dict[str, Sku] = {}
        self._load()

    def _load(self):
        """파일에서 등록된 SKU들 불러오기. 파일 없으면 기본 SKU 자동 생성."""
        if self.storage_path.exists():
            with open(self.storage_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            for sku_dict in data.get("skus", []):
                sku = Sku(**sku_dict)
                self._skus[sku.sku_id] = sku
        else:
            # 파일이 없으면 기본 SKU 생성 후 저장
            self._create_defaults()

    def _create_defaults(self):
        """기본 SKU-001, SKU-002 생성 (최초 실행 시 한 번만)"""
        self.register(
            sku_id="SKU-001", sku_name="버거킹 햄버거번",
            loading_type="pack_based", unit_per_pack=6, packs_per_box=4,
            label_text="버거킹 햄버거번",
            visual_features="둥근 모양의 햄버거번, 표면에 깨 토핑, 비닐 포장에 빨간색 BURGER KING 로고",
            category="햄버거번", expiry_format="YY.MM.DD",
        )
        self.register(
            sku_id="SKU-002", sku_name="곰곰 데일리식빵",
            loading_type="unit_based", units_per_box=8,
            label_text="데일리식빵",
            visual_features="직사각형 슬라이스 식빵, 비닐 봉지에 흰 라벨 + 파란색 'Daily Bread' 문구, 'gomgom' 브랜드명",
            category="식빵", expiry_format="YY.MM.DD",
        )

    def _save(self):
        """파일에 저장"""
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        data = {
            "skus": [asdict(sku) for sku in self._skus.values()]
        }
        with open(self.storage_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def register(
        self,
        sku_id: str,
        sku_name: str,
        loading_type: str,
        unit_per_pack: Optional[int] = None,
        packs_per_box: Optional[int] = None,
        units_per_box: Optional[int] = None,
        label_text: str = "",
        visual_features: str = "",
        category: str = "",
        expiry_format: str = "YY.MM.DD",
        reference_images: Optional[list] = None,
    ) -> Sku:
        """새 SKU 등록"""
        from datetime import datetime

        if sku_id in self._skus and self._skus[sku_id].is_active:
            raise ValueError(f"이미 등록된 SKU입니다: {sku_id}")

        sku = Sku(
            sku_id=sku_id,
            sku_name=sku_name,
            loading_type=loading_type,
            unit_per_pack=unit_per_pack,
            packs_per_box=packs_per_box,
            units_per_box=units_per_box,
            label_text=label_text,
            visual_features=visual_features,
            category=category,
            expiry_format=expiry_format,
            reference_images=reference_images or [],
            registered_at=datetime.now().isoformat(timespec="seconds"),
            is_active=True,
        )
        self._skus[sku_id] = sku
        self._save()
        return sku

    def get(self, sku_id: str) -> Optional[Sku]:
        """SKU 조회"""
        return self._skus.get(sku_id)

    def list_active(self) -> list[Sku]:
        """활성 SKU 전체 조회"""
        return [s for s in self._skus.values() if s.is_active]

    def deactivate(self, sku_id: str):
        """SKU 비활성화 (삭제 대신)"""
        if sku_id in self._skus:
            self._skus[sku_id].is_active = False
            self._save()

    def update(self, sku_id: str, **kwargs):
        """SKU 정보 수정"""
        if sku_id not in self._skus:
            raise ValueError(f"존재하지 않는 SKU: {sku_id}")
        sku = self._skus[sku_id]
        for key, value in kwargs.items():
            if hasattr(sku, key):
                setattr(sku, key, value)
        self._save()
        return sku


# ============================================================
# 실제 등록 — 현재 가지고 있는 이미지의 두 SKU
# ============================================================
def initialize_default_skus():
    """우리가 가진 이미지를 바탕으로 초기 SKU 등록"""
    registry = SkuRegistry()

    # 기존 등록 정리 (재실행 시 깨끗하게)
    registry._skus.clear()

    # SKU-001 : 버거킹 햄버거번 (pack_based)
    registry.register(
        sku_id="SKU-001",
        sku_name="버거킹 햄버거번",
        loading_type="pack_based",
        unit_per_pack=6,
        packs_per_box=4,
        label_text="버거킹 햄버거번",
        visual_features="둥근 모양의 햄버거번, 표면에 깨 토핑, 비닐 포장에 빨간색 BURGER KING 로고",
        category="햄버거번",
        expiry_format="YY.MM.DD",
    )

    # SKU-002 : 곰곰 데일리식빵 F2 (unit_based)
    registry.register(
        sku_id="SKU-002",
        sku_name="곰곰 데일리식빵",
        loading_type="unit_based",
        units_per_box=8,
        label_text="데일리식빵",
        visual_features="직사각형 슬라이스 식빵, 비닐 봉지에 흰 라벨 + 파란색 'Daily Bread' 문구, 'gomgom' 브랜드명",
        category="식빵",
        expiry_format="YY.MM.DD",
    )

    return registry


# ============================================================
# 실행
# ============================================================
if __name__ == "__main__":
    print("=" * 60)
    print("SKU Registry 초기화")
    print("=" * 60)

    registry = initialize_default_skus()

    print(f"\n등록된 SKU 수: {len(registry.list_active())}")
    print("\n📋 등록 SKU 목록:")
    print(f"{'SKU ID':<12} {'이름':<20} {'유형':<14} {'적재 구조':<35}")
    print("-" * 85)

    for sku in registry.list_active():
        print(
            f"{sku.sku_id:<12} {sku.sku_name:<18} "
            f"{sku.loading_type:<14} {sku.display_structure():<35}"
        )

    print(f"\n💾 저장 위치: {registry.storage_path}")
    print("\n✅ SKU Registry 준비 완료. 언제든 새 SKU를 추가할 수 있습니다.")
    print("   예: registry.register(sku_id='SKU-003', ...)")
