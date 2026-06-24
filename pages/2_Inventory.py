"""
Page 3: 재고 현황
상품별: 생산계획 | 현재재고(OK) | 출고예정 | 남는재고(+/-)
"""

import streamlit as st
import pandas as pd
from datetime import timedelta
import datetime
from styles import inject_global_styles, render_page_subtitle, COLORS
from sidebar import ensure_session_state, render_sidebar, render_brand_header
from sku_registry import SkuRegistry
from data_config import DAILY_PRODUCTION_EA, PBOX_UNIT, TOTAL_SKU_TYPES, get_sku_allocation_pbox, calc_savings

st.set_page_config(page_title="재고 현황 | SCM", page_icon="◆",
                   layout="wide", initial_sidebar_state="expanded")

inject_global_styles()
ensure_session_state()
render_sidebar()
render_brand_header()

st.markdown("# 재고 현황")
render_page_subtitle("INVENTORY STATUS · INSPECTION OK → STOCK · PRODUCTION vs DISPATCH")

st.markdown(
    f'<div style="background:#F0FDF4;border-left:4px solid {COLORS["status_ok"]};'
    f'border-radius:6px;padding:14px 20px;margin-top:8px;margin-bottom:4px;">'
    f'<span style="font-size:14px;font-weight:700;color:{COLORS["status_ok"]};">✅ 재고 반영 원칙</span>'
    f'<span style="font-size:13px;color:{COLORS["text_secondary"]};margin-left:12px;">'
    f'[3. 재고 검수]에서 <strong>AI Vision OK 판정</strong>을 받은 P-Box만 재고로 인정합니다. '
    f'NG 차단 수량은 재고에서 제외되어 <strong style="color:{COLORS["status_danger"]};">부족분</strong>으로 표시됩니다.'
    f'</span></div>',
    unsafe_allow_html=True,
)

@st.cache_data(ttl=60)
def load_data():
    df = pd.read_csv("data/inspection_history.csv")
    df["inspected_at"] = pd.to_datetime(df["inspected_at"])
    df["date"] = df["inspected_at"].dt.date
    return df

df = load_data()
registry = SkuRegistry()
today = datetime.date.today()  # 실제 오늘 날짜 사용

# ─── 필터 ───
f1, f2, _ = st.columns([1, 1, 2])
with f1:
    period = st.selectbox("조회 기간", ["최근 7일", "최근 30일", "전체"], index=1)
with f2:
    view_mode = st.selectbox("보기 방식", ["재고 요약표", "SKU별 상세", "매장별 현황"])

if period == "최근 7일":
    df_f = df[df["date"] >= today - timedelta(days=6)]
elif period == "최근 30일":
    df_f = df[df["date"] >= today - timedelta(days=29)]
else:
    df_f = df.copy()

df_ok = df_f[df_f["verdict"] == "OK"]
df_ng = df_f[df_f["verdict"] != "OK"]

# ─── KPI ───
st.markdown("")
k1, k2, k3, k4 = st.columns(4)

def kpi(col, label, val, unit, sub, color):
    col.markdown(
        f'<div style="background:{COLORS["bg_panel"]};border:1px solid {COLORS["border_subtle"]};'
        f'border-top:3px solid {color};border-radius:6px;padding:16px;">'
        f'<div style="font-size:12px;color:{COLORS["text_muted"]};margin-bottom:6px;">{label}</div>'
        f'<div style="font-size:26px;font-weight:700;color:{COLORS["text_primary"]};line-height:1;">'
        f'{val}<span style="font-size:13px;color:{COLORS["text_tertiary"]};margin-left:3px;">{unit}</span></div>'
        f'<div style="font-size:12px;color:{color};margin-top:4px;">{sub}</div>'
        f'</div>', unsafe_allow_html=True)

kpi(k1, "총 P-Box 검수",  f"{len(df_f):,}",    "Case", period,           COLORS["accent_cobalt"])
kpi(k2, "입고 가능 재고",  f"{len(df_ok):,}",   "Case", "OK 판정 완료",    COLORS["status_ok"])
kpi(k3, "NG 차단",         f"{len(df_ng):,}",   "Case", "출고 불가 차단",  COLORS["status_warning"])
kpi(k4, "취급 SKU",        f"{df_ok['expected_sku_name'].nunique()}", "종", "현재 재고 품목", COLORS["accent_gold"])

st.markdown("")
st.markdown("---")

# ═══════════════════════════
# 보기 방식 1: 재고 요약표
# ═══════════════════════════
if view_mode == "재고 요약표":
    st.markdown(
        f'<div style="font-size:16px;font-weight:700;color:{COLORS["text_primary"]};'
        f'margin-bottom:4px;">상품별 재고 현황</div>'
        f'<div style="font-size:13px;color:{COLORS["text_muted"]};margin-bottom:16px;">'
        f'생산계획 대비 현재 재고 및 출고 가능 여부를 확인합니다.</div>',
        unsafe_allow_html=True,
    )

    # 테이블 헤더
    cols = st.columns([2.5, 1.2, 1.2, 1.2, 1.4])
    headers = ["상품명", "생산계획 (Case)", "현재재고 (Case)", "출고예정 (Case)", "남는재고 (±)"]
    for col, h in zip(cols, headers):
        col.markdown(
            f'<div style="font-size:12px;font-weight:700;color:{COLORS["text_muted"]};'
            f'padding:8px 4px;border-bottom:2px solid {COLORS["border_strong"]};'
            f'text-align:center;">{h}</div>', unsafe_allow_html=True)

    # 집계 — 주문 기반 생산 (Order-Driven)
    sku_ok  = df_ok.groupby("expected_sku_name").agg(ok_count=("crate_id","count")).reset_index()
    sku_all = df_f.groupby("expected_sku_name").agg(all_count=("crate_id","count")).reset_index()

    merged = sku_ok.merge(sku_all, on="expected_sku_name", how="outer").fillna(0)

    # 생산계획 = 전체 검수 수량 (주문에 맞춰 생산)
    merged["prod_plan"] = merged["all_count"].astype(int)

    # 출고예정 = 생산계획과 동일 (주문량 기반)
    # 유통기한이 짧아 타이트하게 운영 → 출고예정 ≈ 생산계획
    merged["dispatch_plan"] = merged["prod_plan"]

    # 남는재고 = OK재고 - 출고예정
    # NG 발생 시 → 부족분(-) 발생
    merged["ok_count"]   = merged["ok_count"].astype(int)
    merged["remaining"]  = merged["ok_count"] - merged["dispatch_plan"]

    for _, row in merged.iterrows():
        rem = int(row["remaining"])
        rc  = COLORS["status_ok"] if rem >= 0 else COLORS["status_danger"]
        rb  = "#ECFDF5" if rem >= 0 else "#FEF2F2"
        rs  = "+" if rem >= 0 else ""

        r = st.columns([2.5, 1.2, 1.2, 1.2, 1.4])
        with r[0]:
            st.markdown(
                f'<div style="padding:12px 4px;border-bottom:1px solid {COLORS["border_subtle"]};">'
                f'<span style="font-size:15px;font-weight:600;color:{COLORS["text_primary"]};">'
                f'{row["expected_sku_name"]}</span></div>', unsafe_allow_html=True)
        for i, (val, color) in enumerate([
            (int(row["prod_plan"]),     COLORS["text_secondary"]),
            (int(row["ok_count"]),      COLORS["accent_cobalt"]),
            (int(row["dispatch_plan"]), COLORS["status_warning"]),
        ]):
            r[i+1].markdown(
                f'<div style="padding:12px 4px;border-bottom:1px solid {COLORS["border_subtle"]};'
                f'text-align:center;">'
                f'<div style="font-size:16px;font-weight:700;color:{color};">{val:,}</div>'
                f'</div>', unsafe_allow_html=True)
        with r[4]:
            st.markdown(
                f'<div style="padding:10px 4px;border-bottom:1px solid {COLORS["border_subtle"]};'
                f'text-align:center;">'
                f'<span style="background:{rb};color:{rc};font-size:15px;font-weight:700;'
                f'padding:4px 14px;border-radius:20px;">{rs}{rem:,}</span>'
                f'</div>', unsafe_allow_html=True)

    # 합계
    st.markdown("")
    tot_r = st.columns([2.5, 1.2, 1.2, 1.2, 1.4])
    with tot_r[0]:
        st.markdown(f'<div style="font-weight:700;font-size:15px;color:{COLORS["text_primary"]};'
                    f'padding:8px 4px;">합계</div>', unsafe_allow_html=True)
    for i, (val, color) in enumerate([
        (int(merged["prod_plan"].sum()),     COLORS["text_secondary"]),
        (int(merged["ok_count"].sum()),      COLORS["accent_cobalt"]),
        (int(merged["dispatch_plan"].sum()), COLORS["status_warning"]),
    ]):
        tot_r[i+1].markdown(
            f'<div style="text-align:center;font-weight:700;font-size:15px;'
            f'color:{color};padding:8px 4px;">{val:,}</div>', unsafe_allow_html=True)
    tr = int(merged["remaining"].sum())
    tc = COLORS["status_ok"] if tr >= 0 else COLORS["status_danger"]
    ts = "+" if tr >= 0 else ""
    tot_r[4].markdown(
        f'<div style="text-align:center;font-weight:700;font-size:15px;'
        f'color:{tc};padding:8px 4px;">{ts}{tr:,}</div>', unsafe_allow_html=True)

    st.markdown("")
    st.markdown(
        f'<div style="background:#FFF7ED;border-left:3px solid {COLORS["status_warning"]};'
        f'padding:12px 16px;border-radius:4px;font-size:13px;color:{COLORS["text_secondary"]};">'
        f'<strong>📦 주문 기반 생산 (Order-Driven)</strong> &nbsp;|&nbsp; '
        f'유통기한이 짧아 재고를 타이트하게 운영합니다. '
        f'출고예정 ≈ 생산계획이며, NG 발생 시 OK 재고가 부족해 '
        f'<span style="color:{COLORS["status_danger"]};font-weight:700;">부족분(−)</span>이 '
        f'발생합니다. 부족분은 추가 생산 또는 납기 조정이 필요합니다.'
        f'</div>', unsafe_allow_html=True)


# ═══════════════════════════
# 보기 방식 2: SKU별 상세
# ═══════════════════════════
elif view_mode == "SKU별 상세":
    for sku_name in sorted(df_ok["expected_sku_name"].unique()):
        sku_df = df_ok[df_ok["expected_sku_name"] == sku_name]
        with st.container(border=True):
            c1, c2, c3 = st.columns([2.5, 1, 1])
            with c1:
                st.markdown(
                    f'<div style="font-size:16px;font-weight:700;color:{COLORS["text_primary"]};'
                    f'padding:4px 0;">{sku_name}</div>', unsafe_allow_html=True)
            with c2:
                st.markdown(
                    f'<div style="text-align:center;">'
                    f'<div style="font-size:12px;color:{COLORS["text_muted"]};">재고 (Case)</div>'
                    f'<div style="font-size:24px;font-weight:700;color:{COLORS["accent_cobalt"]};">'
                    f'{len(sku_df):,}</div></div>', unsafe_allow_html=True)
            with c3:
                st.markdown(
                    f'<div style="text-align:center;">'
                    f'<div style="font-size:12px;color:{COLORS["text_muted"]};">수량 (EA)</div>'
                    f'<div style="font-size:24px;font-weight:700;color:{COLORS["accent_gold"]};">'
                    f'{int(sku_df["detected_qty"].sum()):,}</div></div>', unsafe_allow_html=True)

# ═══════════════════════════
# 보기 방식 3: 매장별 현황
# ═══════════════════════════
elif view_mode == "매장별 현황":
    st.markdown(
        f'<div style="font-size:16px;font-weight:700;color:{COLORS["text_primary"]};'
        f'margin-bottom:12px;">매장별 출고 대기 현황</div>', unsafe_allow_html=True)

    store_df = df_ok.groupby("destination_store").agg(
        pbox=("crate_id", "count"),
        units=("detected_qty", "sum"),
    ).reset_index().sort_values("pbox", ascending=False)

    max_p = store_df["pbox"].max() if len(store_df) > 0 else 1
    for _, row in store_df.iterrows():
        pct = int(row["pbox"] / max_p * 100)
        st.markdown(
            f'<div style="display:flex;gap:12px;align-items:center;'
            f'padding:8px 0;border-bottom:1px solid {COLORS["border_subtle"]};">'
            f'<div style="min-width:80px;font-size:14px;color:{COLORS["text_secondary"]};">'
            f'{row["destination_store"]}</div>'
            f'<div style="flex:1;height:8px;background:{COLORS["bg_elevated"]};'
            f'border-radius:4px;overflow:hidden;">'
            f'<div style="height:100%;width:{pct}%;background:{COLORS["accent_cobalt"]};'
            f'border-radius:4px;"></div></div>'
            f'<div style="min-width:110px;text-align:right;font-size:14px;'
            f'color:{COLORS["text_secondary"]};">'
            f'<strong>{int(row["pbox"])}</strong> Case '
            f'<span style="color:{COLORS["text_muted"]};">/ {int(row["units"]):,} EA</span>'
            f'</div></div>', unsafe_allow_html=True)
