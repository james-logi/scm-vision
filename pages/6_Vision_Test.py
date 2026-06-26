"""
Page 6: 비전 검사 테스트 & 상품 관리 v3
- 탭 1: 수동 이미지 업로드
- 탭 2: 폴더 자동 스캔 (10초 간격)
- 검사 이력 자동 저장 → inspection_log.py 공유
"""

import streamlit as st
import json
import os
import base64
import time as time_module
import glob
import io
from PIL import Image, ImageDraw, ImageFont
from styles import inject_global_styles, render_page_subtitle, COLORS
from sidebar import render_brand_header
from sidebar import ensure_session_state, render_sidebar
from sku_registry import SkuRegistry
from inspection_log import InspectionLog

st.set_page_config(
    page_title="비전 검사 테스트 | AI Vision",
    page_icon="◆",
    layout="wide",
    initial_sidebar_state="expanded",
)

inject_global_styles()
ensure_session_state()
render_sidebar()
render_brand_header()

st.markdown("# 비전 검사")
render_page_subtitle("VISION INSPECTION · AI POWERED · SESSION BASED ACTIVATION")


# ─────────────────────────────────────────────
# Vision 활성화 상태 (세션 기반 — 창 닫으면 자동 해제)
# ─────────────────────────────────────────────
if "vision_activated" not in st.session_state:
    st.session_state.vision_activated = False

# 비밀번호 가져오기
def get_vision_password():
    try:
        pw = st.secrets.get("VISION_PASSWORD", "")
        if pw:
            return pw
    except Exception:
        pass
    return os.environ.get("VISION_PASSWORD", os.environ.get("APP_PASSWORD", "vision2026"))

# ── 비활성화 상태: 잠금 화면 ──
if not st.session_state.vision_activated:
    st.markdown("")
    col_l, col_c, col_r = st.columns([1, 2, 1])
    with col_c:
        st.markdown(
            f'<div style="background:{COLORS["bg_panel"]};'
            f'border:2px solid {COLORS["border_subtle"]};'
            f'border-radius:12px;padding:40px 32px;text-align:center;">'
            f'<div style="font-size:56px;margin-bottom:16px;">🔒</div>'
            f'<div style="font-family:\'Noto Serif KR\',serif;font-size:22px;'
            f'font-weight:700;color:{COLORS["text_primary"]};margin-bottom:8px;">'
            f'Vision AI 비활성화 상태</div>'
            f'<div style="font-size:13px;color:{COLORS["text_secondary"]};'
            f'line-height:1.7;margin-bottom:24px;">'
            f'AI 비전 검사 기능은 인증된 사용자만 사용할 수 있습니다.<br>'
            f'비밀번호를 입력하면 이 브라우저 세션에서 활성화됩니다.<br>'
            f'<span style="color:{COLORS["text_muted"]};font-size:12px;">'
            f'(브라우저 창을 닫으면 자동 비활성화)</span>'
            f'</div>'
            f'</div>',
            unsafe_allow_html=True,
        )
        st.markdown("")
        pw_input = st.text_input(
            "비밀번호",
            type="password",
            placeholder="비밀번호를 입력하세요",
            label_visibility="collapsed",
        )
        if st.button("🔓 Vision AI 활성화", width="stretch", type="primary"):
            if pw_input == get_vision_password():
                st.session_state.vision_activated = True
                st.session_state.vision_result = None
                st.session_state.uploader_key = 0
                st.rerun()
            else:
                st.error("비밀번호가 올바르지 않습니다.")

        # SKU 목록은 잠금 상태에서도 열람 가능
        st.markdown("")
        st.markdown(
            f'<div style="font-family:\'IBM Plex Mono\',monospace;font-size:10px;'
            f'color:{COLORS["text_tertiary"]};letter-spacing:0.05em;margin-top:20px;">'
            f'등록된 SKU 목록은 아래에서 확인 가능합니다 ↓</div>',
            unsafe_allow_html=True,
        )
    st.markdown("")
    st.markdown("---")

    # 잠금 상태에서도 SKU 목록 열람 가능
    st.markdown(
        f'<div style="font-family:\'IBM Plex Mono\',monospace;font-size:10px;'
        f'color:{COLORS["text_tertiary"]};letter-spacing:0.08em;margin-bottom:10px;">'
        f'REGISTERED SKU LIST (읽기 전용)</div>',
        unsafe_allow_html=True,
    )
    _registry_ro = SkuRegistry()
    for sku in _registry_ro.list_active():
        with st.container(border=True):
            c1, c2 = st.columns([0.6, 3])
            with c1:
                st.markdown(
                    f'<div style="font-family:\'IBM Plex Mono\',monospace;font-size:11px;'
                    f'color:{COLORS["accent_cobalt"]};">{sku.sku_id}</div>',
                    unsafe_allow_html=True)
            with c2:
                st.markdown(
                    f'<div style="font-family:\'Noto Serif KR\',serif;font-size:14px;'
                    f'font-weight:700;color:{COLORS["text_primary"]};">{sku.sku_name}</div>'
                    f'<div style="font-size:11px;color:{COLORS["text_muted"]};">'
                    f'{sku.display_structure()}</div>',
                    unsafe_allow_html=True)
    st.stop()

# ── 활성화 상태: 상단 배지 + 비활성화 버튼 ──
act_col1, act_col2 = st.columns([5, 1])
with act_col1:
    st.markdown(
        f'<div style="background:{COLORS["bg_panel"]};'
        f'border-left:4px solid {COLORS["accent_gold"]};border-radius:6px;'
        f'padding:12px 20px;margin-top:16px;margin-bottom:16px;">'
        f'<span style="font-size:16px;">🟢</span>'
        f'<span style="font-family:\'IBM Plex Mono\',monospace;font-size:11px;'
        f'color:{COLORS["accent_gold"]};font-weight:700;margin-left:8px;'
        f'letter-spacing:0.05em;">VISION AI 활성화됨</span>'
        f'<span style="font-size:12px;color:{COLORS["text_muted"]};margin-left:12px;">'
        f'이 세션에서만 유효 · 창을 닫으면 자동 비활성화</span>'
        f'</div>',
        unsafe_allow_html=True,
    )
with act_col2:
    if st.button("🔒 비활성화", key="deactivate_btn"):
        st.session_state.vision_activated = False
        st.rerun()

# ─── 세션 상태 ───
for k, v in {
    "vision_result": None,
    "vision_elapsed": 0.0,
    "uploader_key": 0,
    "edit_sku_id": None,
    "scan_running": False,
    "scan_folder": "",
    "scan_processed": [],
    "scan_last_result": None,
    "scan_current_file": "",
}.items():
    if k not in st.session_state:
        st.session_state[k] = v

registry = SkuRegistry()


# ─── 공용 함수 ───
def build_prompt():
    skus = registry.list_active()
    block = ""
    for s in skus:
        block += f"- {s.sku_id}: {s.sku_name}\n"
        block += f"  구조: {s.display_structure()} / 기대수량: {s.expected_total_units()}개\n"
        if hasattr(s, "visual_features") and s.visual_features:
            block += f"  시각적 특징: {s.visual_features}\n"
        if hasattr(s, "label_text") and s.label_text:
            block += f"  라벨: {s.label_text}\n"
    return f"""당신은 식품 제조 공장의 P-Box 검수 AI입니다. 이미지의 P-Box 안 제품을 분석하세요.

[등록 SKU]
{block}
[판정 규칙]
- 수량 불일치만 NG (포장 뒤집힘/상태로 NG 판정 금지)
- 등록 SKU 미매칭 시 UNCLASSIFIED

[수량 카운팅 핵심 규칙 — 반드시 준수]
- 박스의 행×열 그리드 구조를 먼저 파악하세요 (예: 5×2=10개)
- 그리드 구조상 칸이 채워져 있으면, 라벨이 안 보여도 동일 제품으로 카운트하세요
- 제품 뒷면/옆면이 노출되어도 다른 SKU가 아닙니다. 같은 제품의 반대면입니다
- 뒤집힌 제품에서 다른 문구가 보여도 동일 SKU로 처리하세요
- 그리드 구조 계산값이 기대 수량과 일치하면 그 값을 primary_count로 사용하세요
- 개별 라벨 확인보다 그리드 구조 파악을 우선시하세요

JSON만 반환:
{{"verdict":"OK|NG|UNCLASSIFIED","sku_id":"매칭ID or null","sku_name":"상품명","primary_count":숫자,"confidence":0-100,"analysis":"한국어 2-3문장. 행×열 구조와 카운팅 근거 명시","items":[{{"id":1,"x_pct":숫자,"y_pct":숫자,"w_pct":숫자,"h_pct":숫자}}]}}

items 규칙:
- 감지된 제품 각각의 위치를 이미지 크기 대비 퍼센트(0-100)로 반환
- x_pct, y_pct: 좌측상단 좌표, w_pct, h_pct: 폭/높이
- 개수가 많으면 대표 위치만 반환 가능 (최대 20개)"""


def annotate_image(image_bytes, items, verdict, count=0, sku_name=""):
    """감지된 제품에 넘버링 박스 + 판정 배너를 그려서 반환"""
    try:
        img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        W, H = img.size

        # 판정별 색상 (RGB)
        color_map = {
            "OK":           (5, 150, 105),
            "NG":           (220, 38, 38),
            "UNCLASSIFIED": (100, 116, 139),
        }
        box_color = color_map.get(verdict, color_map["UNCLASSIFIED"])

        # ── 상단 배너 (판정 결과) ──
        banner_h = max(40, H // 14)
        banner = Image.new("RGB", (W, banner_h), box_color)
        img.paste(banner, (0, 0))

        draw = ImageDraw.Draw(img)

        try:
            font_b = ImageFont.truetype(
                "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
                max(16, banner_h // 2))
            font_n = ImageFont.truetype(
                "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
                max(14, W // 55))
        except Exception:
            font_b = ImageFont.load_default()
            font_n = font_b

        verdict_label = {"OK": "✓  OK", "NG": "✗  NG", "UNCLASSIFIED": "?  미분류"}.get(verdict, verdict)
        label = f"  {verdict_label}   |   {count}개 감지   |   {sku_name}" if sku_name else f"  {verdict_label}   |   {count}개 감지"
        draw.text((12, banner_h // 5), label, fill=(255, 255, 255), font=font_b)

        # ── 아이템별 박스 + 번호 ──
        lw = max(2, W // 180)
        for item in items:
            try:
                x1 = int(item["x_pct"] / 100 * W)
                y1 = int(item["y_pct"] / 100 * H)
                x2 = int(x1 + item["w_pct"] / 100 * W)
                y2 = int(y1 + item["h_pct"] / 100 * H)
                x1, y1 = max(0, x1), max(banner_h, y1)
                x2, y2 = min(W - 1, x2), min(H - 1, y2)
                if x2 <= x1 or y2 <= y1:
                    continue

                # 테두리 박스
                for i in range(lw):
                    draw.rectangle([x1+i, y1+i, x2-i, y2-i], outline=box_color)

                # 번호 배지 배경
                num = str(item["id"])
                bw = max(26, W // 35)
                bh = max(22, H // 30)
                bx = x1
                by = max(banner_h, y1 - bh)
                draw.rectangle([bx, by, bx+bw, by+bh], fill=box_color)
                draw.text((bx + 4, by + 2), num, fill=(255, 255, 255), font=font_n)
            except Exception:
                continue

        buf = io.BytesIO()
        img.save(buf, format="JPEG", quality=92)
        return buf.getvalue()

    except Exception as e:
        # 실패 시 배너만이라도 붙여서 반환
        try:
            img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
            W, H = img.size
            color_map = {"OK":(5,150,105),"NG":(220,38,38),"UNCLASSIFIED":(100,116,139)}
            c = color_map.get(verdict,(100,116,139))
            banner_h = max(40, H//14)
            banner = Image.new("RGB",(W,banner_h),c)
            img.paste(banner,(0,0))
            draw = ImageDraw.Draw(img)
            label = f"  {verdict}  |  {count}개"
            draw.text((12,8), label, fill=(255,255,255))
            buf = io.BytesIO()
            img.save(buf, format="JPEG", quality=92)
            return buf.getvalue()
        except Exception:
            return image_bytes


def match_preloaded(fname):
    mapping = {"burger_001": "burger_001.json", "burger_002": "burger_002.json",
               "bread_001": "bread_001.json", "bread_002": "bread_002.json"}
    fl = fname.lower()
    for k, jf in mapping.items():
        if k in fl:
            p = os.path.join("data/vision_responses", jf)
            if os.path.exists(p):
                with open(p, encoding="utf-8") as f:
                    r = json.load(f)
                r["source"] = "preloaded"
                return r
    return None


def call_api(image_bytes, fname):
    cost_guard = os.environ.get("COST_GUARD_ENABLED", "True").lower() == "true"
    if cost_guard:
        return {"verdict": "UNCLASSIFIED", "primary_count": 0, "confidence": 0,
                "sku_id": None, "sku_name": "미분류",
                "analysis": "Cost Guard 활성화. COST_GUARD_ENABLED=False 설정 필요.",
                "source": "cost_guard"}
    try:
        import anthropic

        # API 키: Streamlit Secrets → 환경변수 순서로 읽기
        api_key = None
        try:
            api_key = st.secrets.get("ANTHROPIC_API_KEY", "")
        except Exception:
            pass
        if not api_key:
            api_key = os.environ.get("ANTHROPIC_API_KEY", "")

        if not api_key:
            return {"verdict": "UNCLASSIFIED", "primary_count": 0, "confidence": 0,
                    "sku_id": None, "sku_name": "미분류",
                    "analysis": "API 키가 설정되지 않았습니다. Secrets 또는 환경변수를 확인하세요.",
                    "source": "no_key"}

        ext = fname.rsplit(".", 1)[-1].lower()
        mt = {"jpg": "image/jpeg", "jpeg": "image/jpeg", "png": "image/png"}.get(ext, "image/jpeg")
        b64 = base64.b64encode(image_bytes).decode()
        client = anthropic.Anthropic(api_key=api_key)
        resp = client.messages.create(
            model="claude-sonnet-4-6", max_tokens=1024,
            messages=[{"role": "user", "content": [
                {"type": "image", "source": {"type": "base64", "media_type": mt, "data": b64}},
                {"type": "text", "text": build_prompt()},
            ]}]
        )
        raw = resp.content[0].text.strip()
        if "```json" in raw:
            raw = raw.split("```json")[1].split("```")[0].strip()
        elif "```" in raw:
            raw = raw.split("```")[1].split("```")[0].strip()
        r = json.loads(raw)
        r["source"] = "claude_api"
        return r
    except Exception as e:
        return {"verdict": "UNCLASSIFIED", "primary_count": 0, "confidence": 0,
                "sku_id": None, "sku_name": "미분류",
                "analysis": f"오류: {str(e)[:100]}", "source": "error"}


def analyze(image_bytes, fname):
    t0 = time_module.time()
    r = match_preloaded(fname) or call_api(image_bytes, fname)
    elapsed = round(time_module.time() - t0, 2)

    # items 유무와 관계없이 항상 어노테이션 이미지 생성
    r["annotated_image"] = annotate_image(
        image_bytes,
        r.get("items", []),
        r.get("verdict", "UNCLASSIFIED"),
        r.get("primary_count", 0),
        r.get("sku_name", ""),
    )
    return r, elapsed


def render_result_card(result, elapsed):
    verdict = result.get("verdict", "UNCLASSIFIED")
    is_classified = verdict != "UNCLASSIFIED" and result.get("sku_id")
    is_ok = verdict == "OK"

    if is_classified:
        icon, label = ("✅", "정상") if is_ok else ("⚠️", "수량 불일치")
        color = COLORS["status_ok"] if is_ok else COLORS["status_warning"]
        with st.container(border=True):
            st.markdown(
                f'<div style="text-align:center;">'
                f'<div style="font-size:56px;">{icon}</div>'
                f'<div style="font-family:\'Noto Serif KR\',serif;font-size:32px;'
                f'font-weight:900;color:{color};">{label}</div>'
                f'</div>', unsafe_allow_html=True)
        with st.container(border=True):
            st.markdown(
                f'<div><span style="font-family:\'IBM Plex Mono\',monospace;font-size:10px;'
                f'color:{COLORS["text_tertiary"]};">IDENTIFIED</span><br>'
                f'<span style="font-family:\'Noto Serif KR\',serif;font-size:18px;'
                f'font-weight:700;color:{COLORS["text_primary"]};">{result.get("sku_name")}</span>'
                f'<span style="font-size:11px;color:{COLORS["text_muted"]};'
                f'margin-left:8px;">{result.get("sku_id")}</span></div>',
                unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            with st.container(border=True):
                st.markdown(
                    f'<div style="text-align:center;">'
                    f'<div style="font-size:10px;color:{COLORS["text_tertiary"]};">수량</div>'
                    f'<div style="font-size:28px;font-weight:700;color:{COLORS["accent_gold"]};">'
                    f'{result.get("primary_count", 0)}</div>'
                    f'<div style="font-size:10px;color:{COLORS["text_muted"]};">EA</div>'
                    f'</div>', unsafe_allow_html=True)
        with c2:
            with st.container(border=True):
                st.markdown(
                    f'<div style="text-align:center;">'
                    f'<div style="font-size:10px;color:{COLORS["text_tertiary"]};">신뢰도</div>'
                    f'<div style="font-size:28px;font-weight:700;color:{COLORS["accent_cobalt"]};">'
                    f'{result.get("confidence", 0)}</div>'
                    f'<div style="font-size:10px;color:{COLORS["text_muted"]};">%</div>'
                    f'</div>', unsafe_allow_html=True)
    else:
        with st.container(border=True):
            st.markdown(
                f'<div style="text-align:center;">'
                f'<div style="font-size:56px;">❓</div>'
                f'<div style="font-family:\'Noto Serif KR\',serif;font-size:32px;'
                f'font-weight:900;color:{COLORS["accent_gold"]};">기타</div>'
                f'<div style="font-size:12px;color:{COLORS["text_secondary"]};margin-top:6px;">'
                f'등록되지 않은 상품</div>'
                f'</div>', unsafe_allow_html=True)

    src_label = {"preloaded": "📚 사전 라이브러리",
                 "claude_api": "🤖 Claude Vision API",
                 "cost_guard": "🔒 Cost Guard",
                 "error": "❌ 오류"}.get(result.get("source", ""), "")
    if result.get("analysis"):
        st.markdown(
            f'<div style="font-size:12px;color:{COLORS["text_secondary"]};'
            f'line-height:1.6;margin-top:12px;">'
            f'<span style="font-family:\'IBM Plex Mono\',monospace;font-size:10px;'
            f'color:{COLORS["text_tertiary"]};">▸ ANALYSIS</span><br>'
            f'{result.get("analysis")}</div>', unsafe_allow_html=True)
    st.markdown(
        f'<div style="font-family:\'IBM Plex Mono\',monospace;font-size:10px;'
        f'color:{COLORS["text_muted"]};margin-top:8px;">'
        f'소스: {src_label} · ⏱ {elapsed}초</div>', unsafe_allow_html=True)


# ═══════════════════════════════════════
# 탭 구조
# ═══════════════════════════════════════
tab1, tab2 = st.tabs(["📷 수동 업로드", "📁 폴더 자동 스캔"])


# ───────────────────────────────────────
# TAB 1: 수동 업로드
# ───────────────────────────────────────
with tab1:
    up_col, res_col = st.columns([1, 1.2])

    with up_col:
        uploaded = st.file_uploader(
            "P-Box 이미지 업로드 (JPG/PNG)",
            type=["jpg", "jpeg", "png"],
            key=f"vu_{st.session_state.uploader_key}",
        )
        if uploaded:
            # 새 업로드 → 바이트 저장 후 표시
            img_bytes = uploaded.read()
            uploaded.seek(0)
            st.session_state.vision_preview_bytes = img_bytes
            st.session_state.vision_preview_name = uploaded.name
            st.image(img_bytes, use_container_width=True)
            st.caption(f"{uploaded.name} · {uploaded.size/1024:.1f} KB")
            if st.button("🔍 검사 시작", width="stretch", key="btn_manual"):
                with st.spinner("분석 중..."):
                    r, elapsed = analyze(img_bytes, uploaded.name)
                    st.session_state.vision_result = r
                    st.session_state.vision_elapsed = elapsed
                    st.session_state.vision_image_bytes = img_bytes
                    st.session_state.vision_image_name = uploaded.name
                    InspectionLog.save(r, uploaded.name, elapsed)
                st.rerun()
        elif st.session_state.get("vision_preview_bytes"):
            # 검사 완료 후 어노테이션 이미지 표시
            result = st.session_state.get("vision_result")
            ann = result.get("annotated_image") if result else None
            display_img = ann if ann else st.session_state.vision_preview_bytes
            caption = "📍 AI Vision 판정 결과" if ann else st.session_state.get("vision_preview_name","")
            st.image(display_img, use_container_width=True, caption=caption)
        else:
            st.markdown(
                f'<div style="background:{COLORS["bg_panel"]};'
                f'border:2px dashed {COLORS["border_subtle"]};'
                f'border-radius:8px;padding:48px 24px;text-align:center;">'
                f'<div style="font-size:48px;">📦</div>'
                f'<div style="font-size:13px;color:{COLORS["text_secondary"]};margin-top:8px;">'
                f'이미지를 드래그하거나 클릭해서 업로드</div>'
                f'</div>', unsafe_allow_html=True)

    with res_col:
        r = st.session_state.vision_result
        if r:
            render_result_card(r, st.session_state.vision_elapsed)
            if st.button("↻ 새 이미지 테스트", key="btn_reset"):
                st.session_state.vision_result = None
                st.session_state.vision_preview_bytes = None
                st.session_state.vision_preview_name = None
                st.session_state.uploader_key += 1
                st.rerun()
        else:
            with st.container(border=True):
                st.markdown(
                    f'<div style="text-align:center;padding:48px 0;">'
                    f'<div style="font-size:56px;color:{COLORS["text_muted"]};">◌</div>'
                    f'<div style="font-size:13px;color:{COLORS["text_muted"]};margin-top:8px;">'
                    f'분석 대기 중</div></div>', unsafe_allow_html=True)


# ───────────────────────────────────────
# TAB 2: 폴더 자동 스캔
# ───────────────────────────────────────
with tab2:
    st.markdown(
        f'<div style="background:{COLORS["bg_panel"]};'
        f'border-left:4px solid {COLORS["accent_cobalt"]};border-radius:6px;'
        f'padding:14px 20px;margin-bottom:16px;">'
        f'<div style="font-size:13px;color:{COLORS["text_secondary"]};line-height:1.7;">'
        f'폴더 경로를 등록하고 스캔을 시작하면, 해당 폴더의 이미지를 '
        f'<strong style="color:{COLORS["accent_cobalt"]};">10초 간격</strong>으로 한 장씩 검사합니다. '
        f'검사한 이미지는 다시 검사하지 않습니다. '
        f'결과는 자동으로 이력 DB에 저장됩니다.'
        f'</div></div>', unsafe_allow_html=True)

    # 폴더 경로 입력
    folder_path = st.text_input(
        "📁 스캔할 폴더 경로",
        value=st.session_state.scan_folder,
        placeholder="예: C:/Users/jjame/Pictures/pbox_images  또는  /home/user/images",
        key="folder_input",
    )

    # 폴더 유효성 확인
    folder_valid = os.path.isdir(folder_path) if folder_path else False
    if folder_path:
        if folder_valid:
            imgs = sorted(glob.glob(os.path.join(folder_path, "*.jpg")) +
                         glob.glob(os.path.join(folder_path, "*.jpeg")) +
                         glob.glob(os.path.join(folder_path, "*.png")))
            remaining = [f for f in imgs if f not in st.session_state.scan_processed]
            st.markdown(
                f'<div style="font-family:\'IBM Plex Mono\',monospace;font-size:11px;'
                f'color:{COLORS["status_ok"]};">✓ 폴더 확인됨 · 이미지 {len(imgs)}장 '
                f'(미처리 {len(remaining)}장)</div>', unsafe_allow_html=True)
        else:
            st.markdown(
                f'<div style="font-family:\'IBM Plex Mono\',monospace;font-size:11px;'
                f'color:{COLORS["status_warning"]};">⚠ 폴더를 찾을 수 없습니다</div>',
                unsafe_allow_html=True)

    # 스캔 제어 버튼
    ctrl_col1, ctrl_col2 = st.columns(2)
    with ctrl_col1:
        if not st.session_state.scan_running:
            if st.button("▶ 스캔 시작", key="btn_scan_start",
                        width="stretch", disabled=not folder_valid):
                st.session_state.scan_folder = folder_path
                st.session_state.scan_running = True
                st.session_state.scan_processed = []
                st.rerun()
        else:
            if st.button("⏹ 스캔 중지", key="btn_scan_stop",
                        width="stretch", type="primary"):
                st.session_state.scan_running = False
                st.rerun()

    with ctrl_col2:
        if st.button("🔄 처리 목록 초기화", key="btn_scan_reset", width="stretch"):
            st.session_state.scan_processed = []
            st.session_state.scan_last_result = None
            st.rerun()

    # ─── 자동 스캔 실행 ───
    if st.session_state.scan_running and folder_valid:
        imgs = sorted(glob.glob(os.path.join(folder_path, "*.jpg")) +
                     glob.glob(os.path.join(folder_path, "*.jpeg")) +
                     glob.glob(os.path.join(folder_path, "*.png")))
        remaining = [f for f in imgs if f not in st.session_state.scan_processed]

        if not remaining:
            st.info("✅ 폴더의 모든 이미지 처리 완료. 새 이미지를 추가하거나 초기화 후 재시작하세요.")
            st.session_state.scan_running = False
        else:
            next_file = remaining[0]
            fname = os.path.basename(next_file)

            # 현재 처리 중 표시
            progress_pct = len(st.session_state.scan_processed) / len(imgs) if imgs else 0
            st.progress(progress_pct,
                text=f"처리중: {fname} ({len(st.session_state.scan_processed)}/{len(imgs)})")

            scan_area = st.empty()
            with scan_area.container():
                s_col1, s_col2 = st.columns([1, 1.2])
                with s_col1:
                    st.image(next_file, caption=fname, use_container_width=True)
                with s_col2:
                    with st.spinner(f"분석 중: {fname}"):
                        with open(next_file, "rb") as f:
                            img_bytes = f.read()
                        r, elapsed = analyze(img_bytes, fname)
                        st.session_state.scan_processed.append(next_file)
                        st.session_state.scan_last_result = r
                        InspectionLog.save(r, fname, elapsed)
                    render_result_card(r, elapsed)

            # 10초 대기 후 다음 이미지
            with st.empty():
                for i in range(10, 0, -1):
                    st.markdown(
                        f'<div style="font-family:\'IBM Plex Mono\',monospace;'
                        f'font-size:12px;color:{COLORS["text_tertiary"]};'
                        f'text-align:center;margin-top:8px;">'
                        f'다음 이미지까지 {i}초...</div>', unsafe_allow_html=True)
                    time_module.sleep(1)
            st.rerun()

    # 마지막 스캔 결과 표시 (스캔 중지 후)
    if not st.session_state.scan_running and st.session_state.scan_last_result:
        st.markdown("---")
        st.markdown(
            f'<div style="font-family:\'IBM Plex Mono\',monospace;font-size:10px;'
            f'color:{COLORS["text_tertiary"]};margin-bottom:8px;">LAST SCAN RESULT</div>',
            unsafe_allow_html=True)
        render_result_card(
            st.session_state.scan_last_result,
            st.session_state.get("vision_elapsed", 0))

    # 처리된 파일 목록
    if st.session_state.scan_processed:
        with st.expander(f"처리된 파일 목록 ({len(st.session_state.scan_processed)}장)"):
            for f in reversed(st.session_state.scan_processed[-20:]):
                st.markdown(
                    f'<div style="font-size:11px;color:{COLORS["text_muted"]};">'
                    f'✓ {os.path.basename(f)}</div>', unsafe_allow_html=True)


# ═══════════════════════════════════════
# 미분류 → 새 SKU 등록
# ═══════════════════════════════════════
last_r = st.session_state.vision_result or st.session_state.scan_last_result
if last_r and last_r.get("verdict") == "UNCLASSIFIED":
    st.markdown("---")
    st.markdown(
        f'<div style="font-family:\'IBM Plex Mono\',monospace;font-size:10px;'
        f'color:{COLORS["accent_gold"]};letter-spacing:0.08em;margin-bottom:10px;">'
        f'NEW SKU REGISTRATION</div>', unsafe_allow_html=True)
    with st.container(border=True):
        r1, r2 = st.columns(2)
        with r1:
            new_name = st.text_input("상품명", placeholder="예: 미니샌드 연유크림", key="reg_name")
            new_loading = st.selectbox("적재 방식", ["unit_based", "pack_based"],
                format_func=lambda x: "개별 적재" if x == "unit_based" else "포장 적재",
                key="reg_loading")
        with r2:
            new_cat = st.text_input("카테고리", placeholder="예: 샌드위치, 크림빵", key="reg_cat")
            new_visual = st.text_area("시각적 특징",
                placeholder="예: 검정 라벨 '미니샌드', 5봉지씩 묶음 포장",
                height=80, key="reg_visual")
        r3, r4 = st.columns(2)
        with r3:
            if new_loading == "pack_based":
                new_packs = st.number_input("묶음 수", min_value=1, value=2, key="reg_packs")
                new_perpack = st.number_input("팩당 개수", min_value=1, value=5, key="reg_perpack")
            else:
                new_units = st.number_input("박스당 개수", min_value=1, value=10, key="reg_units")
        with r4:
            new_label = st.text_input("라벨 텍스트", key="reg_label")

        if st.button("📦 새 SKU 등록", key="btn_register", width="stretch"):
            if not new_name or not new_visual:
                st.error("상품명과 시각적 특징을 입력해주세요.")
            else:
                existing = [s.sku_id for s in registry.list_active()]
                max_n = max([int(s.split("-")[1]) for s in existing if "-" in s], default=0)
                new_id = f"SKU-{max_n + 1:03d}"
                if new_loading == "pack_based":
                    registry.register(sku_id=new_id, sku_name=new_name,
                        loading_type="pack_based", unit_per_pack=new_perpack,
                        packs_per_box=new_packs, label_text=new_label or new_name,
                        visual_features=new_visual, category=new_cat or "기타")
                else:
                    registry.register(sku_id=new_id, sku_name=new_name,
                        loading_type="unit_based", units_per_box=new_units,
                        label_text=new_label or new_name,
                        visual_features=new_visual, category=new_cat or "기타")
                st.success(f"✅ {new_id} · {new_name} 등록 완료!")
                st.balloons()


# ═══════════════════════════════════════
# 등록된 SKU 목록 (수정/삭제)
# ═══════════════════════════════════════
st.markdown("---")
st.markdown(
    f'<div style="font-family:\'IBM Plex Mono\',monospace;font-size:10px;'
    f'color:{COLORS["text_tertiary"]};letter-spacing:0.08em;margin-bottom:10px;">'
    f'REGISTERED SKU LIST · ✏️ 수정 · 🗑️ 삭제</div>', unsafe_allow_html=True)

for sku in registry.list_active():
    is_editing = (st.session_state.edit_sku_id == sku.sku_id)
    with st.container(border=True):
        if is_editing:
            st.markdown(
                f'<div style="font-family:\'IBM Plex Mono\',monospace;font-size:10px;'
                f'color:{COLORS["accent_gold"]};">✏️ 수정 모드 · {sku.sku_id}</div>',
                unsafe_allow_html=True)
            e1, e2 = st.columns(2)
            with e1:
                en = st.text_input("상품명", value=sku.sku_name, key=f"en_{sku.sku_id}")
                ec = st.text_input("카테고리",
                    value=sku.category if hasattr(sku, "category") and sku.category else "",
                    key=f"ec_{sku.sku_id}")
            with e2:
                ev = st.text_area("시각적 특징",
                    value=sku.visual_features if hasattr(sku, "visual_features") and sku.visual_features else "",
                    height=70, key=f"ev_{sku.sku_id}")
                el = st.text_input("라벨 텍스트",
                    value=sku.label_text if hasattr(sku, "label_text") and sku.label_text else "",
                    key=f"el_{sku.sku_id}")
            sv, cv = st.columns(2)
            with sv:
                if st.button("💾 저장", key=f"save_{sku.sku_id}", width="stretch"):
                    jp = "data/sku_registry.json"
                    if os.path.exists(jp):
                        with open(jp, encoding="utf-8") as f:
                            d = json.load(f)
                        for item in d.get("skus", []):
                            if item["sku_id"] == sku.sku_id:
                                item.update({"sku_name": en, "category": ec,
                                            "visual_features": ev, "label_text": el})
                                break
                        with open(jp, "w", encoding="utf-8") as f:
                            json.dump(d, f, ensure_ascii=False, indent=2)
                    st.session_state.edit_sku_id = None
                    st.success(f"✅ {sku.sku_id} 저장 완료")
                    st.rerun()
            with cv:
                if st.button("✗ 취소", key=f"cancel_{sku.sku_id}", width="stretch"):
                    st.session_state.edit_sku_id = None
                    st.rerun()
        else:
            c1, c2, c3, c4 = st.columns([0.6, 2.8, 0.3, 0.3])
            with c1:
                st.markdown(
                    f'<div style="font-family:\'IBM Plex Mono\',monospace;font-size:11px;'
                    f'color:{COLORS["accent_cobalt"]};">{sku.sku_id}</div>',
                    unsafe_allow_html=True)
            with c2:
                cat = f' · <span style="color:{COLORS["text_muted"]};">{sku.category}</span>' \
                      if hasattr(sku, "category") and sku.category else ""
                st.markdown(
                    f'<div style="font-family:\'Noto Serif KR\',serif;font-size:14px;'
                    f'font-weight:700;color:{COLORS["text_primary"]};">{sku.sku_name}{cat}</div>'
                    f'<div style="font-size:11px;color:{COLORS["text_muted"]};">'
                    f'{sku.display_structure()}</div>', unsafe_allow_html=True)
            with c3:
                if st.button("✏️", key=f"edit_{sku.sku_id}"):
                    st.session_state.edit_sku_id = sku.sku_id
                    st.rerun()
            with c4:
                if st.button("🗑️", key=f"del_{sku.sku_id}"):
                    jp = "data/sku_registry.json"
                    if os.path.exists(jp):
                        with open(jp, encoding="utf-8") as f:
                            d = json.load(f)
                        for item in d.get("skus", []):
                            if item["sku_id"] == sku.sku_id:
                                item["is_active"] = False
                                break
                        with open(jp, "w", encoding="utf-8") as f:
                            json.dump(d, f, ensure_ascii=False, indent=2)
                    st.success(f"🗑️ {sku.sku_name} 삭제됨")
                    st.rerun()
