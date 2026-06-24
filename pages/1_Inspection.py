"""
Page 4: 출고 검수
날짜별 재고에서 출고 처리 확인 — 검수 완료 재고의 출고 가능 여부 확인
"""

import streamlit as st
import pandas as pd
from datetime import timedelta
from styles import inject_global_styles, render_page_subtitle, COLORS
from sidebar import ensure_session_state, render_sidebar, render_brand_header
from sku_registry import SkuRegistry

st.set_page_config(page_title="출고 검수 | SCM", page_icon="◆",
                   layout="wide", initial_sidebar_state="expanded")

inject_global_styles()
ensure_session_state()
render_sidebar()
render_brand_header()

st.markdown("# 출고 검수")
render_page_subtitle("DISPATCH INSPECTION · DATE BASED INVENTORY · CONFIRM DISPATCH READY")

@st.cache_data(ttl=60)
def load_data():
    df = pd.read_csv("data/inspection_history.csv")
    df["inspected_at"] = pd.to_datetime(df["inspected_at"])
    df["date"] = df["inspected_at"].dt.date
    return df

df = load_data()
today = df["date"].max()

# ─── 필터 ───
f1, f2, f3 = st.columns([1, 1, 1])
with f1:
    period = st.selectbox("조회 기간",
        ["오늘", "최근 3일", "최근 7일", "최근 30일"], index=2)
with f2:
    skus = ["전체"] + sorted(df["expected_sku_name"].dropna().unique().tolist())
    sel_sku = st.selectbox("상품", skus)
with f3:
    verdict_filter = st.selectbox("검수 결과",
        ["전체", "출고 가능(OK)", "출고 불가(NG)"])

if period == "오늘":
    df_f = df[df["date"] == today]
elif period == "최근 3일":
    df_f = df[df["date"] >= today - timedelta(days=2)]
elif period == "최근 7일":
    df_f = df[df["date"] >= today - timedelta(days=6)]
else:
    df_f = df[df["date"] >= today - timedelta(days=29)]

if sel_sku != "전체":
    df_f = df_f[df_f["expected_sku_name"] == sel_sku]
if verdict_filter == "출고 가능(OK)":
    df_f = df_f[df_f["verdict"] == "OK"]
elif verdict_filter == "출고 불가(NG)":
    df_f = df_f[df_f["verdict"] != "OK"]

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

total = len(df_f)
ok    = len(df_ok)
ng    = len(df_ng)
acc   = ok/total*100 if total > 0 else 0

kpi(k1, "검수 건수",    f"{total:,}", "건",  period,              COLORS["accent_cobalt"])
kpi(k2, "출고 가능",    f"{ok:,}",    "Case","OK — 출고 확정 가능", COLORS["status_ok"])
kpi(k3, "출고 불가",    f"{ng:,}",    "Case","NG — 출고 차단",     COLORS["status_warning"])
kpi(k4, "검수 정확도",  f"{acc:.1f}", "%",   "AI Vision 판정",     COLORS["accent_gold"])

st.markdown("")
st.markdown("---")

# ─── 탭 ───
tab1, tab2, tab3 = st.tabs(["📅 날짜별 출고 확인", "📦 상품별 출고 재고", "🚫 NG 상세 내역"])

# ────────────────────────────────────
with tab1:
    st.markdown(
        f'<div style="font-size:15px;font-weight:700;color:{COLORS["text_primary"]};'
        f'margin-bottom:12px;">날짜별 검수 재고 — 출고 처리 확인</div>',
        unsafe_allow_html=True)

    daily = df_f.groupby("date").agg(
        total=("crate_id","count"),
        ok=("verdict", lambda x: (x=="OK").sum()),
        ng=("verdict", lambda x: (x!="OK").sum()),
    ).reset_index().sort_values("date", ascending=False)
    daily["ok_rate"] = (daily["ok"] / daily["total"] * 100).round(1)
    daily["출고가능"] = daily["ok"].apply(lambda x: f"{x:,} Case")
    daily["출고불가"] = daily["ng"].apply(lambda x: f"{x:,} Case")
    daily["검수정확도"] = daily["ok_rate"].apply(lambda x: f"{x}%")
    daily["출고확인"] = daily["ok"].apply(
        lambda x: "✅ 출고 가능" if x > 0 else "⏸ 재고 없음")

    # 헤더
    h = st.columns([1.2, 1, 1, 1, 1, 1.2])
    for col, label in zip(h, ["날짜","총 검수","출고 가능","출고 불가","검수 정확도","출고 확인"]):
        col.markdown(
            f'<div style="font-size:12px;font-weight:700;color:{COLORS["text_muted"]};'
            f'padding:8px 4px;border-bottom:2px solid {COLORS["border_strong"]};'
            f'text-align:center;">{label}</div>', unsafe_allow_html=True)

    for _, row in daily.iterrows():
        ok_color = COLORS["status_ok"] if row["ng"] == 0 else COLORS["status_warning"]
        r = st.columns([1.2, 1, 1, 1, 1, 1.2])
        values = [
            (str(row["date"]),        COLORS["text_primary"],   False),
            (f'{int(row["total"]):,} Case', COLORS["text_secondary"], False),
            (f'{int(row["ok"]):,} Case',    COLORS["status_ok"],      True),
            (f'{int(row["ng"]):,} Case',    COLORS["status_warning"] if row["ng"]>0 else COLORS["text_muted"], True),
            (f'{row["ok_rate"]}%',    COLORS["accent_gold"],    True),
            (row["출고확인"],          ok_color,                 True),
        ]
        for col, (val, color, center) in zip(r, values):
            align = "center" if center else "left"
            col.markdown(
                f'<div style="padding:10px 4px;border-bottom:1px solid {COLORS["border_subtle"]};'
                f'text-align:{align};font-size:14px;color:{color};font-weight:500;">'
                f'{val}</div>', unsafe_allow_html=True)

# ────────────────────────────────────
with tab2:
    st.markdown(
        f'<div style="font-size:15px;font-weight:700;color:{COLORS["text_primary"]};'
        f'margin-bottom:12px;">상품별 출고 가능 재고 현황</div>',
        unsafe_allow_html=True)

    sku_summary = df_f.groupby("expected_sku_name").agg(
        total=("crate_id","count"),
        ok=("verdict", lambda x: (x=="OK").sum()),
        ng=("verdict", lambda x: (x!="OK").sum()),
        qty=("detected_qty","sum"),
    ).reset_index()

    h2 = st.columns([2, 1, 1, 1, 1])
    for col, label in zip(h2, ["상품명","총 검수","출고 가능","출고 불가","개별 수량(EA)"]):
        col.markdown(
            f'<div style="font-size:12px;font-weight:700;color:{COLORS["text_muted"]};'
            f'padding:8px 4px;border-bottom:2px solid {COLORS["border_strong"]};'
            f'text-align:center;">{label}</div>', unsafe_allow_html=True)

    for _, row in sku_summary.iterrows():
        r2 = st.columns([2, 1, 1, 1, 1])
        with r2[0]:
            st.markdown(
                f'<div style="padding:12px 4px;border-bottom:1px solid {COLORS["border_subtle"]};">'
                f'<span style="font-size:15px;font-weight:600;color:{COLORS["text_primary"]};">'
                f'{row["expected_sku_name"]}</span></div>', unsafe_allow_html=True)
        for col, val, color in [
            (r2[1], f'{int(row["total"]):,}', COLORS["text_secondary"]),
            (r2[2], f'{int(row["ok"]):,}',    COLORS["status_ok"]),
            (r2[3], f'{int(row["ng"]):,}',    COLORS["status_warning"] if row["ng"]>0 else COLORS["text_muted"]),
            (r2[4], f'{int(row["qty"]):,}',   COLORS["accent_gold"]),
        ]:
            col.markdown(
                f'<div style="padding:12px 4px;border-bottom:1px solid {COLORS["border_subtle"]};'
                f'text-align:center;font-size:15px;font-weight:700;color:{color};">'
                f'{val}</div>', unsafe_allow_html=True)

# ────────────────────────────────────
with tab3:
    st.markdown(
        f'<div style="font-size:15px;font-weight:700;color:{COLORS["text_primary"]};'
        f'margin-bottom:12px;">NG 판정 — 출고 차단 내역</div>',
        unsafe_allow_html=True)

    if df_ng.empty:
        st.success("조회 기간 내 NG 건수가 없습니다.")
    else:
        ng_disp = df_ng[["date","line_no","expected_sku_name","verdict",
                          "expected_qty","detected_qty"]].copy()
        ng_disp.columns = ["날짜","라인","상품명","판정","기대수량","검출수량"]
        ng_disp = ng_disp.sort_values("날짜", ascending=False)

        verdict_map = {
            "NG_QTY_SHORT":    "수량 부족",
            "NG_QTY_EXCESS":   "수량 초과",
            "NG_CONTAMINATION":"혼입 불량",
            "NG_SKU_MISMATCH": "SKU 불일치",
        }
        ng_disp["판정"] = ng_disp["판정"].map(verdict_map).fillna(ng_disp["판정"])

        st.dataframe(ng_disp, use_container_width=True, hide_index=True, height=400)

        st.markdown(
            f'<div style="background:#FEF2F2;border-left:3px solid {COLORS["status_danger"]};'
            f'padding:12px 16px;border-radius:4px;font-size:13px;'
            f'color:{COLORS["status_danger"]};margin-top:12px;">'
            f'⚠ 위 {len(df_ng)}건은 출고 차단되었습니다. '
            f'재검수 또는 폐기 처리가 필요합니다.'
            f'</div>', unsafe_allow_html=True)
