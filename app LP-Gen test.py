"""
Streamlit Web Application: LP-Generator Coupling Alignment Precision Tool
Standard: EGAT Mae Moh Power Plant Unit 8-13
Reference: Alignment & Eccentricity Manual (EGAT Mechanical Maintenance)
"""

from typing import Tuple
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
import pandas as pd
import streamlit as st

# ตั้งค่าระบบแสดงผล
st.set_page_config(
    page_title="EGAT MM 8-13 Alignment Precision Tool",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# รองรับฟอนต์ภาษาไทยสำหรับระบบ Windows
plt.rcParams['font.sans-serif'] = ['Tahoma', 'Leelawadee UI', 'DejaVu Sans']
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['axes.unicode_minus'] = False

# สไตล์ตกแต่งระดับ Industrial Dashboard
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #0A192F 0%, #172A45 50%, #203A43 100%);
        padding: 20px 26px;
        border-radius: 12px;
        color: #FFFFFF;
        margin-bottom: 22px;
        border-left: 7px solid #FF9800;
        box-shadow: 0 4px 14px rgba(0,0,0,0.18);
    }
    .main-header h1 {
        color: #FFFFFF;
        font-size: 25px;
        margin: 0;
        font-weight: 700;
        letter-spacing: 0.5px;
    }
    .main-header p {
        color: #CFD8DC;
        font-size: 14px;
        margin: 6px 0 0 0;
    }
    div[data-testid="stExpander"] {
        border-radius: 10px;
        border: 1px solid #E0E0E0;
        background-color: #FAFAFA;
        margin-bottom: 10px;
    }
    .status-card {
        background-color: #FFFFFF;
        border: 1px solid #CFD8DC;
        border-radius: 8px;
        padding: 12px 16px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.04);
    }
</style>
""", unsafe_allow_html=True)

# ค่าควบคุมมาตรฐาน กฟผ. แม่เมาะ
TARGET_RADIAL_OFFSET_MM = -0.100  # Catenary Curve Target (mm)
TARGET_AXIAL_GAP_MM = 0.000       # Target Face Gap (mm)
TOLERANCE_RADIAL_DIV = 3          # เกณฑ์ความคลาดเคลื่อนผลต่างเกจ Radial ไม่เกิน 3 ขีด

# =========================================================================
# Session State Initialization
# =========================================================================
default_states = {
    'd_coupling': 800.0,
    'l_brg4': 550.0,
    'l_gen_f': 1850.0,
    'l_gen_m': 3890.0,
    'l_gen_r': 5150.0,
    # Radial อ่านเป็นเลขจำนวนเต็มดิบเกจวัด (ขีด)
    'r_top': 0,
    'r_bottom': -48,
    'r_left': -36,
    'r_right': -11,
    # Axial อ่านเป็นค่ามิลลิเมตรจริงจากสไลซ์เกจคู่
    'g1_0': 19.170, 'g2_0': 19.240,
    'g1_90': 19.360, 'g2_90': 19.260,
    'g1_180': 19.250, 'g2_180': 19.340,
    'g1_270': 19.360, 'g2_270': 19.215,
}

for key, val in default_states.items():
    if key not in st.session_state:
        st.session_state[key] = val


# =========================================================================
# Drawing Functions
# =========================================================================
def draw_dial_crosshair(ax, title_text, center_symbol, t_val, b_val, l_val, r_val, dial_color, badge_title, badge_desc, is_radial_raw=False):
    """
    วาดไดอะแกรมเกจวัดกากบาท (+) ตรงกลาง
    """
    ax.set_aspect('equal')
    ax.set_xlim(-2.35, 2.35)
    ax.set_ylim(-2.60, 2.40)
    ax.axis('off')

    is_target = "TARGET" in title_text or "เป้าหมาย" in title_text
    header_bg = "#E8F5E9" if is_target else "#FFEBEE"
    header_bdr = "#2E7D32" if is_target else "#C62828"

    # 1. แถบหัวข้อด้านบน
    ax.text(0, 2.08, title_text, ha='center', va='center', fontsize=11, fontweight='bold', color=header_bdr,
            bbox=dict(boxstyle='round,pad=0.42', facecolor=header_bg, edgecolor=header_bdr, lw=1.6))

    # 2. ตัวเรือนเกจวัดวงกลม
    outer_ring = patches.Circle((0, 0), 0.88, edgecolor=dial_color, facecolor='#FAFAFA', linewidth=3.2, zorder=1)
    inner_ring = patches.Circle((0, 0), 0.82, edgecolor='#CFD8DC', facecolor='#FFFFFF', linewidth=1.2, zorder=2)
    ax.add_patch(outer_ring)
    ax.add_patch(inner_ring)

    # 3. ขีดสเกลเกจวัด 12 จุด
    for angle in np.linspace(0, 2 * np.pi, 12, endpoint=False):
        x_in, y_in = 0.73 * np.cos(angle), 0.73 * np.sin(angle)
        x_out, y_out = 0.81 * np.cos(angle), 0.81 * np.sin(angle)
        ax.plot([x_in, x_out], [y_in, y_out], color='#B0BEC5', lw=1.2, zorder=2)

    # 4. เส้นกากบาทเครื่องหมายบวก (+)
    ax.plot([-0.78, 0.78], [0, 0], color=dial_color, lw=2.0, linestyle='-', alpha=0.75, zorder=3)
    ax.plot([0, 0], [-0.78, 0.78], color=dial_color, lw=2.0, linestyle='-', alpha=0.75, zorder=3)

    # 5. วงกลมศูนย์กลาง Hub พร้อมสัญลักษณ์ A หรือ R
    hub = patches.Circle((0, 0), 0.25, facecolor='#FFFFFF', edgecolor=dial_color, lw=2.2, zorder=4)
    ax.add_patch(hub)
    ax.text(0, 0.0, center_symbol, ha='center', va='center', fontsize=18, fontweight='bold',
            color=dial_color, zorder=5)

    sub_label = "ค่าดิบเกจ" if is_radial_raw else "แสดงผลต่าง mm"
    ax.text(0, -0.48, sub_label, ha='center', va='center', fontsize=8, fontweight='bold',
            color='#78909C', zorder=3)

    # 6. ค่าอ่าน 4 ทิศทาง
    if is_radial_raw:
        t_str = f"{int(t_val):+d}" if t_val is not None else "--"
        b_str = f"{int(b_val):+d}" if b_val is not None else "--"
        l_str = f"{int(l_val):+d}" if l_val is not None else "--"
        r_str = f"{int(r_val):+d}" if r_val is not None else "--"
    else:
        t_str = f"{t_val:+.3f}" if t_val is not None else "--"
        b_str = f"{b_val:+.3f}" if b_val is not None else "--"
        l_str = f"{l_val:+.3f}" if l_val is not None else "--"
        r_str = f"{r_val:+.3f}" if r_val is not None else "--"

    ax.text(0, 1.15, f"บน (Top)\n{t_str}", ha='center', va='bottom', fontsize=9.5, fontweight='bold')
    ax.text(0, -1.15, f"{b_str}\nล่าง (Bottom)", ha='center', va='top', fontsize=9.5, fontweight='bold')
    ax.text(-1.08, 0, f"ซ้าย (L)\n{l_str}", ha='right', va='center', fontsize=9.5, fontweight='bold')
    ax.text(1.08, 0, f"ขวา (R)\n{r_str}", ha='left', va='center', fontsize=9.5, fontweight='bold')

    # 7. กล่องสรุปผลทางกลศาสตร์ด้านล่าง
    txt_box = f"{badge_title}\n[{badge_desc}]"
    ax.text(0, -1.95, txt_box, ha='center', va='top', fontsize=9.5, fontweight='bold', color=header_bdr,
            bbox=dict(boxstyle='round,pad=0.42', facecolor=header_bg, edgecolor=header_bdr, lw=1.5))


def draw_coupling_physical_setup(ax, choice: str):
    """
    ไดอะแกรมแท่นติดตั้งเกจตาม Solution 1, 2, 3
    """
    ax.set_aspect('equal')
    ax.set_xlim(-1.6, 8.2)
    ax.set_ylim(-3.5, 4.0)
    ax.axis('off')

    gen_color = '#1565C0' if choice in ['1', '2'] else '#E65100'
    ax.add_patch(patches.Rectangle((-1.0, -0.6), 2.4, 1.2, facecolor=gen_color, edgecolor='#0D47A1', linewidth=2.5))
    ax.add_patch(patches.Rectangle((1.4, -1.6), 0.8, 3.2, facecolor=gen_color, edgecolor='#0D47A1', linewidth=2.5))
    ax.text(0.2, 0.0, "Gen", ha='center', va='center', color='white', fontsize=16, fontweight='bold')

    lp_color = '#D84315' if choice in ['1', '2'] else '#1565C0'
    ax.add_patch(patches.Rectangle((4.6, -0.6), 2.4, 1.2, facecolor=lp_color, edgecolor='#BF360C', linewidth=2.5))
    ax.add_patch(patches.Rectangle((3.8, -1.6), 0.8, 3.2, facecolor=lp_color, edgecolor='#BF360C', linewidth=2.5))
    ax.text(5.8, 0.0, "LP", ha='center', va='center', color='white', fontsize=16, fontweight='bold')

    bracket_color = '#37474F'

    if choice in ['1', '2']:
        rim_x, rim_y, rim_r = 4.2, 2.2, 0.45
        ax.plot([1.8, 1.8, rim_x, rim_x], [1.6, 3.1, 3.1, rim_y + rim_r], color=bracket_color, lw=2.5)
        ax.add_patch(patches.Circle((rim_x, rim_y), rim_r, facecolor='#FF9800', edgecolor=bracket_color, lw=2.2))
        ax.annotate("", xy=(rim_x, 1.6), xytext=(rim_x, rim_y - rim_r), arrowprops=dict(arrowstyle="->", color=bracket_color, lw=2.5))
        ax.text(4.9, rim_y, "Rim (Radial)\n[Target LP Face]", fontsize=9.5, fontweight='bold', color=bracket_color, va='center')

        ax.plot([2.2, 2.55], [0.55, 0.55], color=bracket_color, lw=2.5)
        ax.add_patch(patches.Circle((3.0, 0.55), 0.45, facecolor='#FF9800', edgecolor=bracket_color, lw=2.2))
        ax.annotate("", xy=(3.8, 0.55), xytext=(3.45, 0.55), arrowprops=dict(arrowstyle="->", color=bracket_color, lw=2.5))
        ax.text(3.0, 1.18, "G1 (Top)", ha='center', va='bottom', fontsize=11, fontweight='bold', color=bracket_color)

        ax.plot([2.2, 2.55], [-0.85, -0.85], color=bracket_color, lw=2.5)
        ax.add_patch(patches.Circle((3.0, -0.85), 0.45, facecolor='#FF9800', edgecolor=bracket_color, lw=2.2))
        ax.annotate("", xy=(3.8, -0.85), xytext=(3.45, -0.85), arrowprops=dict(arrowstyle="->", color=bracket_color, lw=2.5))
        ax.text(3.0, -1.48, "G2 (Bottom)", ha='center', va='top', fontsize=11, fontweight='bold', color=bracket_color)
    else:
        rim_x, rim_y, rim_r = 1.8, 2.2, 0.45
        ax.plot([4.2, 4.2, rim_x, rim_x], [1.6, 3.1, 3.1, rim_y + rim_r], color=bracket_color, lw=2.5)
        ax.add_patch(patches.Circle((rim_x, rim_y), rim_r, facecolor='#FF9800', edgecolor=bracket_color, lw=2.2))
        ax.annotate("", xy=(rim_x, 1.6), xytext=(rim_x, rim_y - rim_r), arrowprops=dict(arrowstyle="->", color=bracket_color, lw=2.5))
        ax.text(0.9, rim_y, "Rim (Radial)\n[Target Gen Face]", fontsize=9.5, fontweight='bold', color=bracket_color, va='center', ha='right')

        ax.plot([3.8, 3.45], [0.55, 0.55], color=bracket_color, lw=2.5)
        ax.add_patch(patches.Circle((3.0, 0.55), 0.45, facecolor='#FF9800', edgecolor=bracket_color, lw=2.2))
        ax.annotate("", xy=(2.2, 0.55), xytext=(2.55, 0.55), arrowprops=dict(arrowstyle="->", color=bracket_color, lw=2.5))
        ax.text(3.0, 1.18, "G1 (Top)", ha='center', va='bottom', fontsize=11, fontweight='bold', color=bracket_color)

        ax.plot([3.8, 3.45], [-0.85, -0.85], color=bracket_color, lw=2.5)
        ax.add_patch(patches.Circle((3.0, -0.85), 0.45, facecolor='#FF9800', edgecolor=bracket_color, lw=2.2))
        ax.annotate("", xy=(2.2, -0.85), xytext=(2.55, -0.85), arrowprops=dict(arrowstyle="->", color=bracket_color, lw=2.5))
        ax.text(3.0, -1.48, "G2 (Bottom)", ha='center', va='top', fontsize=11, fontweight='bold', color=bracket_color)

    if choice == '1':
        status_txt = (
            "[SOLUTION 1: ปรับเฉพาะ LP Bearing 4]\n"
            "* ฝั่ง Generator ล็อกแน่น 100% (เป็นฐานอ้างอิง)\n"
            "* ขยับปรับชิมเฉพาะแท่น LP Brg.4 เพื่อดึงเพลาเข้าหา Generator"
        )
        bg_col, bdr_col = "#E8F5E9", "#2E7D32"
    elif choice == '2':
        status_txt = (
            "[SOLUTION 2: แบ่งสัดส่วนปรับร่วมกัน 50:50]\n"
            "* แบ่งภาระการปรับ: LP Brg.4 (50%) + ขาตั้ง Generator 6 จุด (50%)\n"
            "* เพลาทั้งสองฝั่งเคลื่อนที่เข้าหาแนวศูนย์กลางเป้าหมายคนละครึ่งทาง"
        )
        bg_col, bdr_col = "#FFFDE7", "#F57F17"
    else:
        status_txt = (
            "[SOLUTION 3: ปรับเฉพาะขาตั้ง Generator 6 ขา]\n"
            "* ฝั่ง Turbine LP ล็อกแน่น 100% (เป็นฐานอ้างอิง)\n"
            "* ขยับปรับชิมเฉพาะขาตั้ง Generator 6 จุดเพื่อดึงเพลาเข้าหา LP"
        )
        bg_col, bdr_col = "#FFEBEE", "#C62828"

    ax.text(3.0, -2.6, status_txt, ha='center', va='center', fontsize=10.5, fontweight='bold',
            bbox=dict(boxstyle='round,pad=0.55', facecolor=bg_col, edgecolor=bdr_col, lw=1.8))


# =========================================================================
# Application Layout
# =========================================================================
st.markdown("""
<div class="main-header">
    <h1>⚡ ระบบคำนวณและจำลองการตั้งศูนย์เพลา LP - Generator</h1>
    <p>ฝ่ายบำรุงรักษา โรงไฟฟ้าแม่เมาะ ยูนิต 8-13 | Precision Shaft Alignment Tool (ตามหลักการคู่มือ กฟผ.)</p>
</div>
""", unsafe_allow_html=True)

col_input, col_view = st.columns([1.1, 1.9], gap="large")

with col_input:
    st.subheader("⚙️ ข้อมูลการวัดจริง (Field Inputs)")

    sol_options = [
        "Solution 1: LP Bearing 4 Only (Gen Fixed)",
        "Solution 2: Shared 50:50 (LP + Gen Legs)",
        "Solution 3: Generator Legs Only (LP Fixed)"
    ]
    sol_selected = st.radio("เลือกวิธีการจัดตั้งชิม (Strategy):", sol_options, key="active_solution_radio")
    choice_val = sol_selected[9]

    with st.expander("📍 1. มิติทางกลเพลาและคัปปลิ้ง (Machine Geometry)", expanded=False):
        st.session_state.d_coupling = st.number_input("เส้นผ่านศูนย์กลางหน้าแปลนคัปปลิ้ง D (mm)", value=float(st.session_state.d_coupling), step=10.0)
        st.session_state.l_brg4 = st.number_input("ระยะจากคัปปลิ้งถึง LP Brg.4 (mm)", value=float(st.session_state.l_brg4), step=10.0)
        st.session_state.l_gen_f = st.number_input("ระยะถึงขา Gen คู่หน้า (mm)", value=float(st.session_state.l_gen_f), step=10.0)
        st.session_state.l_gen_m = st.number_input("ระยะถึงขา Gen คู่กลาง (mm)", value=float(st.session_state.l_gen_m), step=10.0)
        st.session_state.l_gen_r = st.number_input("ระยะถึงขา Gen คู่หลัง (mm)", value=float(st.session_state.l_gen_r), step=10.0)

    with st.expander("📍 2. ค่าเกจวัดแนวรัศมี (Radial Rim Readings)", expanded=True):
        st.caption("🔢 กรอกตัวเลขดิบตามเกจวัด Dial Gauge (หน่วยขีด ไม่ต้องแปลงทศนิยม)")
        r1, r2 = st.columns(2)
        with r1:
            st.session_state.r_top = st.number_input("Top (T) ขีด", value=int(st.session_state.r_top), step=1)
            st.session_state.r_left = st.number_input("Left (L) ขีด", value=int(st.session_state.r_left), step=1)
        with r2:
            st.session_state.r_bottom = st.number_input("Bottom (B) ขีด", value=int(st.session_state.r_bottom), step=1)
            st.session_state.r_right = st.number_input("Right (R) ขีด", value=int(st.session_state.r_right), step=1)

    with st.expander("📍 3. ค่าเกจวัดแนวแกนหน้าแปลน (Axial Slice Readings)", expanded=True):
        st.caption("📏 ค่าที่อ่านได้จริงจากสไลซ์เกจคู่ (mm): คำนวณค่าเฉลี่ย (G1 + G2) / 2")
        f1, f2 = st.columns(2)
        with f1:
            st.session_state.g1_0 = st.number_input("0° (Top) เข็มนอก G1", value=float(st.session_state.g1_0), step=0.01, format="%.3f")
            st.session_state.g2_0 = st.number_input("0° (Top) เข็มใน G2", value=float(st.session_state.g2_0), step=0.01, format="%.3f")
            st.session_state.g1_90 = st.number_input("90° (Left) เข็มนอก G1", value=float(st.session_state.g1_90), step=0.01, format="%.3f")
            st.session_state.g2_90 = st.number_input("90° (Left) เข็มใน G2", value=float(st.session_state.g2_90), step=0.01, format="%.3f")
        with f2:
            st.session_state.g1_180 = st.number_input("180° (Bottom) เข็มนอก G1", value=float(st.session_state.g1_180), step=0.01, format="%.3f")
            st.session_state.g2_180 = st.number_input("180° (Bottom) เข็มใน G2", value=float(st.session_state.g2_180), step=0.01, format="%.3f")
            st.session_state.g1_270 = st.number_input("270° (Right) เข็มนอก G1", value=float(st.session_state.g1_270), step=0.01, format="%.3f")
            st.session_state.g2_270 = st.number_input("270° (Right) เข็มใน G2", value=float(st.session_state.g2_270), step=0.01, format="%.3f")

    st.write("**โหลดชุดข้อมูลด่วนสำหรับทดสอบ:**")
    btn_c1, btn_c2 = st.columns(2)
    if btn_c1.button("📋 ข้อมูลตัวอย่างมาตรฐาน", use_container_width=True):
        st.session_state.r_top = 0
        st.session_state.r_bottom = -31
        st.session_state.r_left = -20
        st.session_state.r_right = -12
        st.session_state.g1_0, st.session_state.g2_0 = 14.95, 14.96
        st.session_state.g1_180, st.session_state.g2_180 = 14.97, 14.96
        st.session_state.g1_90, st.session_state.g2_90 = 14.96, 14.95
        st.session_state.g1_270, st.session_state.g2_270 = 14.98, 15.00
        st.rerun()

    if btn_c2.button("📑 ข้อมูลใบบันทึกจริง (MM-T)", use_container_width=True):
        st.session_state.r_top = 0
        st.session_state.r_bottom = -48
        st.session_state.r_left = -36
        st.session_state.r_right = -11
        st.session_state.g1_0, st.session_state.g2_0 = 19.170, 19.240
        st.session_state.g1_180, st.session_state.g2_180 = 19.250, 19.340
        st.session_state.g1_90, st.session_state.g2_90 = 19.360, 19.260
        st.session_state.g1_270, st.session_state.g2_270 = 19.360, 19.215
        st.rerun()


# =========================================================================
# Output View & Visual Dashboard
# =========================================================================
with col_view:
    # 1. คำนวณค่าเฉลี่ยฝั่ง Axial (mm) ตามใบบันทึกการวัดจริง ทั้ง 4 ทิศทาง
    raw_a_top = (st.session_state.g1_0 + st.session_state.g2_0) / 2.0
    raw_a_bottom = (st.session_state.g1_180 + st.session_state.g2_180) / 2.0
    raw_a_left = (st.session_state.g1_90 + st.session_state.g2_90) / 2.0
    raw_a_right = (st.session_state.g1_270 + st.session_state.g2_270) / 2.0

    # ระยะอ้าหน้าแปลน (Gap Differences):
    delta_x_v = (raw_a_bottom - raw_a_top) - TARGET_AXIAL_GAP_MM
    delta_gap_lr = raw_a_left - raw_a_right
    gap_lr_mm = abs(delta_gap_lr)

    # ค่าความแตกต่างบนไดอะแกรมกากบาท Axial (เทียบด้านน้อยเป็น 0)
    norm_a_top = 0.000 if raw_a_bottom >= raw_a_top else (raw_a_top - raw_a_bottom)
    norm_a_bottom = (raw_a_bottom - raw_a_top) if raw_a_bottom >= raw_a_top else 0.000
    norm_a_left = (raw_a_left - raw_a_right) if raw_a_left >= raw_a_right else 0.000
    norm_a_right = 0.000 if raw_a_left >= raw_a_right else (raw_a_right - raw_a_left)

    # 2. คำนวณตรวจเช็กความเที่ยงตรงเกจ Radial (เกณฑ์ไม่เกิน 3 ขีด)
    diff_r_raw = abs((st.session_state.r_top + st.session_state.r_bottom) - (st.session_state.r_left + st.session_state.r_right))
    valid_r = diff_r_raw <= TOLERANCE_RADIAL_DIV

    # 3. แปลงค่า Radial เกจวัดดิบเป็นระยะเยื้องศูนย์จริง (mm) ตามกฎหาร 2
    actual_offset_v = ((st.session_state.r_bottom - st.session_state.r_top) / 2.0) * 0.01
    delta_y_v = actual_offset_v - TARGET_RADIAL_OFFSET_MM  # ระยะที่ Gen อยู่ต่ำกว่าเป้าหมาย

    r_lr_diff_div = st.session_state.r_right - st.session_state.r_left
    actual_offset_h = (r_lr_diff_div / 2.0) * 0.01

    target_radial_raw_bottom = int(round((2.0 * TARGET_RADIAL_OFFSET_MM) / 0.01))
    target_radial_raw_side = int(round(TARGET_RADIAL_OFFSET_MM / 0.01))

    # 4. คำนวณตามระเบียบวิธีของคู่มือ กฟผ. ทั้งแนวบน-ล่าง (T&B) และ ซ้าย-ขวา (L&R)
    # ข้อ 1: ปรับค่า Axial ในแนวบนและล่าง (T & B) ด้วยสามเหลี่ยมคล้าย
    lift_brg4 = - (delta_x_v * st.session_state.l_brg4) / st.session_state.d_coupling
    lift_gen_f = (delta_x_v * st.session_state.l_gen_f) / st.session_state.d_coupling
    lift_gen_m = (delta_x_v * st.session_state.l_gen_m) / st.session_state.d_coupling
    lift_gen_r = (delta_x_v * st.session_state.l_gen_r) / st.session_state.d_coupling

    # ข้อ 2: รวมผลกับ Radial
    if choice_val == '1':
        shim_b4 = lift_brg4 + delta_y_v
        shim_f = shim_m = shim_r = 0.0
    elif choice_val == '2':
        alpha = 0.5
        shim_b4 = alpha * (lift_brg4 + delta_y_v)
        shim_f = (1.0 - alpha) * (lift_gen_f - delta_y_v)
        shim_m = (1.0 - alpha) * (lift_gen_m - delta_y_v)
        shim_r = (1.0 - alpha) * (lift_gen_r - delta_y_v)
    else:
        shim_b4 = 0.0
        shim_f = lift_gen_f - delta_y_v
        shim_m = lift_gen_m - delta_y_v
        shim_r = lift_gen_r - delta_y_v

    # ข้อ 3: ปรับค่า Axial ในแนวซ้ายและขวา (L & R) ด้วยสามเหลี่ยมคล้าย
    shift_ax_b4 = - (delta_gap_lr * st.session_state.l_brg4) / st.session_state.d_coupling
    shift_ax_f = (delta_gap_lr * st.session_state.l_gen_f) / st.session_state.d_coupling
    shift_ax_m = (delta_gap_lr * st.session_state.l_gen_m) / st.session_state.d_coupling
    shift_ax_r = (delta_gap_lr * st.session_state.l_gen_r) / st.session_state.d_coupling

    # ข้อ 4: รวมผลกับ Radial
    if choice_val == '1':
        shift_b4 = shift_ax_b4 - actual_offset_h
        shift_f = shift_m = shift_r = 0.0
    elif choice_val == '2':
        alpha = 0.5
        shift_b4 = alpha * (shift_ax_b4 - actual_offset_h)
        shift_f = (1.0 - alpha) * (shift_ax_f - actual_offset_h)
        shift_m = (1.0 - alpha) * (shift_ax_m - actual_offset_h)
        shift_r = (1.0 - alpha) * (shift_ax_r - actual_offset_h)
    else:
        shift_b4 = 0.0
        shift_f = shift_ax_f - actual_offset_h
        shift_m = shift_ax_m - actual_offset_h
        shift_r = shift_ax_r - actual_offset_h

    # ---------------------------------------------------------------------
    # สรุปผลการปรับตั้งจริง (Field Action Work Order)
    # ---------------------------------------------------------------------
    st.subheader(f"📋 สรุปผลการปรับตั้ง Alignment จริง [Solution {choice_val}]")

    # 1. กล่องสรุปสภาวะหน้าแปลน
    c_st1, c_st2 = st.columns(2)
    with c_st1:
        gap_v_label = "ล่างอ้า (Bottom OPEN)" if delta_x_v > 0 else ("บนอ้า (Top OPEN)" if delta_x_v < 0 else "ขนานสนิท")
        gen_v_label = f"Gen ต่ำกว่าเป้าหมาย {abs(delta_y_v):.3f} mm" if delta_y_v < 0 else f"Gen สูงกว่าเป้าหมาย {delta_y_v:.3f} mm"
        st.markdown(f"""
        <div class="status-card" style="border-left: 5px solid #1565C0;">
            <div style="font-size: 13px; color: #546E7A; font-weight: bold;">↕️ สภาวะแนวดิ่ง (Vertical Plane: Top & Bottom)</div>
            <div style="font-size: 15px; font-weight: bold; margin-top: 4px; color: #0D47A1;">
                ระยะอ้าหน้าแปลน Gap = {delta_x_v:+.3f} mm [{gap_v_label}]
            </div>
            <div style="font-size: 13.5px; color: #37474F; margin-top: 2px;">
                เยื้องศูนย์จริง Offset = {actual_offset_v:+.3f} mm &nbsp;|&nbsp; <b>{gen_v_label}</b>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with c_st2:
        gap_h_label = "ซ้ายอ้า (Left OPEN)" if delta_gap_lr > 0 else ("ขวาอ้า (Right OPEN)" if delta_gap_lr < 0 else "ขนานสนิท")
        gen_h_label = f"Gen เยื้องขวา {abs(actual_offset_h):.3f} mm" if actual_offset_h > 0 else (f"Gen เยื้องซ้าย {abs(actual_offset_h):.3f} mm" if actual_offset_h < 0 else "ตรงศูนย์")
        st.markdown(f"""
        <div class="status-card" style="border-left: 5px solid #2E7D32;">
            <div style="font-size: 13px; color: #546E7A; font-weight: bold;">↔️ สภาวะแนวนอน (Horizontal Plane: Left & Right)</div>
            <div style="font-size: 15px; font-weight: bold; margin-top: 4px; color: #1B5E20;">
                ระยะอ้าหน้าแปลน Gap = {delta_gap_lr:+.4f} mm [{gap_h_label}]
            </div>
            <div style="font-size: 13.5px; color: #37474F; margin-top: 2px;">
                เยื้องศูนย์จริง Offset = {actual_offset_h:+.3f} mm &nbsp;|&nbsp; <b>{gen_h_label}</b>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.write("")

    # 2. ฟังก์ชันแสดงคำสั่งปรับ Shim
    def fmt_shim_vertical(val_mm, is_fixed=False):
        if is_fixed or abs(val_mm) < 0.0005:
            return "🔒 ยึดแน่นคงที่ (0.000 mm)"
        if val_mm > 0:
            return f"หนุน Shim ด้านล่าง (B) เพิ่ม +{val_mm:.3f} mm"
        return f"ถอน Shim ด้านล่าง (B) ออก -{abs(val_mm):.3f} mm"

    def fmt_shim_horizontal(val_mm, is_fixed=False):
        if is_fixed or abs(val_mm) < 0.0005:
            return "🔒 ยึดแน่นคงที่ (0.000 mm)"
        if val_mm > 0:
            return f"เอา Shim ซ้าย (L) ออก {abs(val_mm):.3f} mm ย้ายไปใส่ขวา (R)"
        return f"เอา Shim ขวา (R) ออก {abs(val_mm):.3f} mm ย้ายไปใส่ซ้าย (L)"

    def fmt_vector(v_val, h_val, is_fixed=False):
        if is_fixed:
            return "ฐานอ้างอิงคงที่"
        v_str = f"T={v_val*100:+.1f}" if v_val >= 0 else f"B={abs(v_val)*100:.1f}"
        h_str = f"L={h_val*100:+.1f}" if h_val >= 0 else f"R={abs(h_val)*100:.1f}"
        return f"{v_str}, {h_str} (ขีด)"

    summary_data = [
        {
            "ตำแหน่งแบริ่ง": "LP Bearing 4",
            "ระยะแขน L": f"{st.session_state.l_brg4:.0f} mm",
            "การปรับ Shim แนวบน-ล่าง (T & B)": fmt_shim_vertical(shim_b4, is_fixed=(choice_val == '3')),
            "การปรับ Shim แนวซ้าย-ขวา (L & R)": fmt_shim_horizontal(shift_b4, is_fixed=(choice_val == '3')),
            "Vector สรุป": fmt_vector(shim_b4, shift_b4, is_fixed=(choice_val == '3'))
        },
        {
            "ตำแหน่งแบริ่ง": "Gen ขาคู่หน้า (Legs 1, 2)",
            "ระยะแขน L": f"{st.session_state.l_gen_f:.0f} mm",
            "การปรับ Shim แนวบน-ล่าง (T & B)": fmt_shim_vertical(shim_f, is_fixed=(choice_val == '1')),
            "การปรับ Shim แนวซ้าย-ขวา (L & R)": fmt_shim_horizontal(shift_f, is_fixed=(choice_val == '1')),
            "Vector สรุป": fmt_vector(shim_f, shift_f, is_fixed=(choice_val == '1'))
        },
        {
            "ตำแหน่งแบริ่ง": "Gen ขาคู่กลาง (Legs 3, 4)",
            "ระยะแขน L": f"{st.session_state.l_gen_m:.0f} mm",
            "การปรับ Shim แนวบน-ล่าง (T & B)": fmt_shim_vertical(shim_m, is_fixed=(choice_val == '1')),
            "การปรับ Shim แนวซ้าย-ขวา (L & R)": fmt_shim_horizontal(shift_m, is_fixed=(choice_val == '1')),
            "Vector สรุป": fmt_vector(shim_m, shift_m, is_fixed=(choice_val == '1'))
        },
        {
            "ตำแหน่งแบริ่ง": "Gen ขาคู่หลัง (Legs 5, 6)",
            "ระยะแขน L": f"{st.session_state.l_gen_r:.0f} mm",
            "การปรับ Shim แนวบน-ล่าง (T & B)": fmt_shim_vertical(shim_r, is_fixed=(choice_val == '1')),
            "การปรับ Shim แนวซ้าย-ขวา (L & R)": fmt_shim_horizontal(shift_r, is_fixed=(choice_val == '1')),
            "Vector สรุป": fmt_vector(shim_r, shift_r, is_fixed=(choice_val == '1'))
        }
    ]

    df_summary = pd.DataFrame(summary_data)
    st.table(df_summary)

    # แท็บแสดงผล
    tab1, tab2, tab3, tab4 = st.tabs([
        "📐 ไดอะแกรมเพลา & การจัดชิม (Deflection & Shim)",
        "📋 ใบบันทึกผลและวิเคราะห์เกจ (Inspection Sheet & Dial Analysis)",
        "🔍 ไดอะแกรมติดตั้งเกจ (Dial Setup)",
        "📝 ตรวจสอบขั้นตอนการคำนวณ (Calculation Verification)"
    ])

    # ---------------------------------------------------------------------
    # Tab 1: Deflection Diagrams
    # ---------------------------------------------------------------------
    with tab1:
        fig2, (ax_side, ax_top, ax_bar) = plt.subplots(
            3, 1, figsize=(15, 12.8), gridspec_kw={'height_ratios': [1.2, 1.2, 0.85]}
        )
        fig2.subplots_adjust(top=0.90, bottom=0.08, hspace=0.48, left=0.08, right=0.96)
        fig2.suptitle(f"FIELD ALIGNMENT DIAGRAMS & SHIM ACTION - [SOLUTION {choice_val}]",
                      fontsize=14, fontweight='bold', color='#0D47A1', y=0.96)

        flange_h = 2.0
        gap_x = 420.0
        gen_end_x = float(st.session_state.l_gen_r) + 400.0

        def draw_alignment_plane(ax, title, delta_gap, delta_offset, choice, is_vertical=True):
            ax.axhline(0, color='gray', linestyle='--', linewidth=1.5, label='Centerline Baseline')

            if choice == '1':
                ratio_lp, ratio_gen = 1.0, 0.0
            elif choice == '2':
                ratio_lp, ratio_gen = 0.5, 0.5
            else:
                ratio_lp, ratio_gen = 0.0, 1.0

            # Generator (Right)
            gen_tilt_dir = -1.0 if delta_gap >= 0 else 1.0
            gen_center_y = (0.70 if delta_offset > 0 else -0.70) * ratio_gen
            gen_slope = (gen_tilt_dir * 0.00025) * ratio_gen

            gen_x = np.array([gap_x, gap_x + st.session_state.l_gen_f, gap_x + st.session_state.l_gen_m, gap_x + st.session_state.l_gen_r, gen_end_x])
            gen_y = gen_center_y + gen_slope * (gen_x - gap_x)

            ax.plot(gen_x, gen_y, color='#1565C0', linewidth=4.5)
            ax.plot([gap_x, gap_x], [gen_center_y - flange_h, gen_center_y + flange_h], color='#0D47A1', linewidth=5.5)

            gen_state_lbl = "GENERATOR (FIXED BASELINE)" if ratio_gen == 0 else f"GENERATOR (ADJUSTING {int(ratio_gen*100)}%)"
            ax.text(gap_x + st.session_state.l_gen_m / 2, gen_y[2] + 1.6, gen_state_lbl, ha='center', fontsize=10.5, fontweight='bold', color='#1565C0')

            gen_legs = [
                (gap_x + st.session_state.l_gen_f, gen_y[1], f"Gen-F\n(L={st.session_state.l_gen_f:.0f})"),
                (gap_x + st.session_state.l_gen_m, gen_y[2], f"Gen-M\n(L={st.session_state.l_gen_m:.0f})"),
                (gap_x + st.session_state.l_gen_r, gen_y[3], f"Gen-R\n(L={st.session_state.l_gen_r:.0f})")
            ]
            for gx, gy_leg, glabel in gen_legs:
                ax.plot([gx, gx], [gy_leg - 0.6, gy_leg], color='#0D47A1', linewidth=2.5)
                ax.scatter([gx], [gy_leg - 0.6], s=120, marker='s', color='#0D47A1', zorder=5)
                ax.text(gx, gy_leg - 0.9, glabel, ha='center', va='top', fontsize=9, fontweight='bold')

            # Turbine LP (Left)
            turb_vis_offset = (0.70 if delta_offset < 0 else -0.70) * ratio_lp
            turb_tilt_dir = 1.0 if delta_gap >= 0 else -1.0
            tilt_x = turb_tilt_dir * 50.0 * ratio_lp

            fl_top_x = 0.0 + tilt_x
            fl_top_y = turb_vis_offset + flange_h
            fl_bot_x = 0.0 - tilt_x
            fl_bot_y = turb_vis_offset - flange_h

            ax.plot([fl_top_x, fl_bot_x], [fl_top_y, fl_bot_y], color='#BF360C', linewidth=5.5)

            brg_x = -float(st.session_state.l_brg4)
            turb_end_x = brg_x - 200.0
            turb_brg_y = turb_vis_offset - (turb_tilt_dir * 0.45 * ratio_lp)
            turb_end_y = turb_vis_offset - (turb_tilt_dir * 0.65 * ratio_lp)

            ax.plot([turb_end_x, 0.0], [turb_end_y, turb_vis_offset], color='#D84315', linewidth=4.5)
            lp_state_lbl = "TURBINE (LP FIXED)" if ratio_lp == 0 else f"TURBINE (LP ADJUSTING {int(ratio_lp*100)}%)"
            ax.text(brg_x / 2, turb_vis_offset + 0.6, lp_state_lbl, ha='center', fontsize=10.5, fontweight='bold', color='#D84315')

            ax.plot([brg_x, brg_x], [turb_brg_y - 0.6, turb_brg_y], color='#4E342E', linewidth=3)
            ax.scatter([brg_x], [turb_brg_y - 0.6], s=140, marker='^', color='#4E342E', zorder=5)
            ax.text(brg_x, turb_brg_y - 0.9, f"LP Brg.4\n(L={st.session_state.l_brg4:.0f} mm)", ha='center', va='top', fontsize=9, fontweight='bold')

            lbl_top = "T" if is_vertical else "L"
            lbl_bot = "B" if is_vertical else "R"
            ax.text(fl_top_x - 90, fl_top_y, lbl_top, fontsize=12, fontweight='bold', color='#BF360C')
            ax.text(fl_bot_x - 90, fl_bot_y, lbl_bot, fontsize=12, fontweight='bold', color='#BF360C')

            if is_vertical:
                gap_y = fl_bot_y if delta_gap >= 0 else fl_top_y
                meas_x = fl_bot_x if delta_gap >= 0 else fl_top_x
                y_offset = -0.35 if delta_gap >= 0 else 0.35
                va_pos = 'top' if delta_gap >= 0 else 'bottom'
                gap_title = f"Gap บน-ล่าง (T&B) = {delta_gap:+.3f} mm"
            else:
                gap_y = fl_top_y if delta_gap >= 0 else fl_bot_y
                meas_x = fl_top_x if delta_gap >= 0 else fl_bot_x
                y_offset = 0.35 if delta_gap >= 0 else -0.35
                va_pos = 'bottom' if delta_gap >= 0 else 'top'
                gap_title = f"Gap ซ้าย-ขวา (L&R) = {delta_gap:+.4f} mm"

            ax.plot([meas_x, gap_x], [gap_y + y_offset, gap_y + y_offset], color='purple', linestyle='-', lw=1.8)
            ax.plot([meas_x, meas_x], [gap_y, gap_y + y_offset * 1.3], color='purple', lw=1.5)
            ax.plot([gap_x, gap_x], [gap_y, gap_y + y_offset * 1.3], color='purple', lw=1.5)
            ax.text((meas_x + gap_x) / 2.0, gap_y + y_offset * 1.4, gap_title, ha='center', va=va_pos, fontsize=9.5, fontweight='bold', color='purple',
                    bbox=dict(boxstyle='round,pad=0.25', facecolor='#F3E5F5', edgecolor='purple', alpha=0.9))

            mid_dim_x = gap_x / 2.0
            ax.plot([0.0, gap_x], [turb_vis_offset, turb_vis_offset], color='brown', linestyle=':', lw=1.5)
            ax.annotate("", xy=(mid_dim_x, gen_center_y), xytext=(mid_dim_x, turb_vis_offset),
                        arrowprops=dict(arrowstyle="<->", color="brown", lw=2.0))
            
            offset_title = f"Offset แนวดิ่ง (V) = {delta_offset:+.3f} mm" if is_vertical else f"Offset แนวนอน (H) = {delta_offset:+.3f} mm"
            ax.text(mid_dim_x + 30, (turb_vis_offset + gen_center_y) / 2.0, offset_title, ha='left', va='center', fontsize=9.5, fontweight='bold', color='brown',
                    bbox=dict(boxstyle='round,pad=0.25', facecolor='#FFF8E1', edgecolor='brown', alpha=0.9))

            ax.set_title(title, fontsize=11.5, fontweight='bold', pad=14)
            ax.set_xlim(-float(st.session_state.l_brg4) - 300, gen_end_x + 250)
            ax.set_ylim(-3.0, 3.8)
            ax.set_yticks([-2, 0, 2])
            if is_vertical:
                ax.set_ylabel("Vertical Deflection\n(Exaggerated)", fontsize=10, fontweight='bold')
                ax.set_yticklabels(["- (Down)", "0 (Ref)", "+ (Up)"], fontsize=9.5)
            else:
                ax.set_ylabel("Horizontal Shift\n(Exaggerated)", fontsize=10, fontweight='bold')
                ax.set_yticklabels(["- (Right)", "0 (Ref)", "+ (Left)"], fontsize=9.5)
            ax.grid(True, linestyle=':', alpha=0.5)

        draw_alignment_plane(ax_side, f"1. SIDE VIEW (ระนาบแนวดิ่ง: บน-ล่าง T&B) - [SOLUTION {choice_val}]", delta_x_v, delta_y_v, choice_val, is_vertical=True)
        draw_alignment_plane(ax_top, f"2. TOP VIEW (ระนาบแนวนอน: ซ้าย-ขวา L&R) - [SOLUTION {choice_val}]", delta_gap_lr, actual_offset_h, choice_val, is_vertical=False)

        labels = ["LP Bearing 4", "Gen Front (1,2)", "Gen Mid (3,4)", "Gen Rear (5,6)"]
        shims = [shim_b4, shim_f, shim_m, shim_r]
        colors = ['#2E7D32' if s > 0 else ('#C62828' if s < 0 else '#9E9E9E') for s in shims]

        bars = ax_bar.bar(labels, shims, color=colors, width=0.4, edgecolor='black', zorder=3)
        ax_bar.axhline(0, color='black', linewidth=1.2)
        ax_bar.set_ylabel("Shim (mm)", fontsize=10, fontweight='bold')
        ax_bar.set_title(f"3. Field Shim Action Required for [SOLUTION {choice_val}]", fontsize=11.5, fontweight='bold', pad=8)
        ax_bar.grid(axis='y', linestyle=':', alpha=0.6)

        max_val = max(abs(s) for s in shims) if any(abs(s) > 0 for s in shims) else 0.05
        ax_bar.set_ylim(-max_val * 1.5 - 0.03, max_val * 1.5 + 0.03)

        for bar, s_val in zip(bars, shims):
            h = bar.get_height()
            va_align = 'bottom' if h >= 0 else 'top'
            y_pos = h + (0.003 if h >= 0 else -0.003)
            action_word = "ADD (+)" if s_val > 0 else ("REMOVE (-)" if s_val < 0 else "FIXED")
            ax_bar.text(bar.get_x() + bar.get_width() / 2., y_pos, f"{s_val:+.3f} mm\n({action_word})", ha='center', va=va_align, fontsize=10, fontweight='bold')

        st.pyplot(fig2)

    # ---------------------------------------------------------------------
    # Tab 2: ใบบันทึกผลและวิเคราะห์เกจ
    # ---------------------------------------------------------------------
    with tab2:
        st.subheader("📋 ใบบันทึกผลและวิเคราะห์เกจ (Inspection Sheet & Dial Analysis)")
        st.caption("แถวบน = ค่าอ่านเกจวัดจริงก่อนปรับ (แปลงเทียบศูนย์) | แถวล่าง = ค่าเกจวัดเป้าหมายมาตรฐาน")

        c1, c2 = st.columns(2)
        with c1:
            st.info(f"**1. แนวแกนหน้าแปลน (Axial Face Gap):**\n"
                    f"- บน-ล่าง (T&B): {'หน้าแปลนล่างอ้า' if delta_x_v > 0 else 'หน้าแปลนบนอ้า'} **{abs(delta_x_v):.3f} mm** (บน {raw_a_top:.3f} / ล่าง {raw_a_bottom:.3f})\n"
                    f"- ซ้าย-ขวา (L&R): {'หน้าแปลนซ้ายอ้า' if raw_a_left > raw_a_right else 'หน้าแปลนขวาอ้า'} **{gap_lr_mm:.4f} mm** (ซ้าย {raw_a_left:.3f} / ขวา {raw_a_right:.4f})")
        with c2:
            st.warning(f"**2. แนวรัศมีเพลา (Radial Rim TIR):**\n"
                       f"- บน-ล่าง (T&B): {'เพลา Gen ต่ำกว่าเป้าหมาย' if delta_y_v < 0 else 'เพลา Gen สูงกว่าเป้าหมาย'} **{abs(delta_y_v):.3f} mm**\n"
                       f"- ตรวจสอบความเที่ยงตรง (T+B)-(L+R) = **{diff_r_raw} ขีด** [{'✅ ผ่านเกณฑ์ <= 3 ขีด' if valid_r else '❌ เกินเกณฑ์ 3 ขีด'}]")

        fig1 = plt.figure(figsize=(15, 10.8))

        # 1. Axial Before
        ax1 = fig1.add_subplot(2, 2, 1)
        face_desc_th = "หน้าแปลนล่างอ้า (Bottom OPEN)" if delta_x_v > 0 else ("หน้าแปลนบนอ้า (Top OPEN)" if delta_x_v < 0 else "ขนานพอดี")
        draw_dial_crosshair(
            ax1,
            "[1] ความแตกต่างแนวแกน ก่อนปรับ (Axial Face Before)",
            "A",
            norm_a_top, norm_a_bottom, norm_a_left, norm_a_right,
            '#C62828',
            f"ระยะอ้าจริง Gap = {delta_x_v:+.3f} mm",
            face_desc_th,
            is_radial_raw=False
        )

        # 2. Radial Before
        ax2 = fig1.add_subplot(2, 2, 2)
        rim_desc_th = f"Gen ต่ำกว่าเป้าหมาย {abs(delta_y_v):.3f} mm" if delta_y_v < 0 else f"Gen สูงกว่าเป้าหมาย {delta_y_v:+.3f} mm"
        draw_dial_crosshair(
            ax2,
            "[2] ขอบเพลาแนวรัศมี ก่อนปรับ (Radial Rim Before)",
            "R",
            st.session_state.r_top, st.session_state.r_bottom, st.session_state.r_left, st.session_state.r_right,
            '#C62828',
            f"เยื้องศูนย์จริง Offset = {actual_offset_v:+.3f} mm",
            rim_desc_th,
            is_radial_raw=True
        )

        # 3. Axial Target
        ax3 = fig1.add_subplot(2, 2, 3)
        draw_dial_crosshair(
            ax3,
            "[3] เป้าหมายแนวแกน หลังปรับ (Axial Face Target)",
            "A",
            0.0, TARGET_AXIAL_GAP_MM, 0.0, 0.0,
            '#2E7D32',
            f"เป้าหมาย Gap = {TARGET_AXIAL_GAP_MM:+.3f} mm",
            "หน้าแปลนขนานสนิทสมบูรณ์",
            is_radial_raw=False
        )

        # 4. Radial Target
        ax4 = fig1.add_subplot(2, 2, 4)
        draw_dial_crosshair(
            ax4,
            "[4] เป้าหมายแนวรัศมี หลังปรับ (Radial Rim Target)",
            "R",
            0,
            target_radial_raw_bottom,
            target_radial_raw_side,
            target_radial_raw_side,
            '#2E7D32',
            f"เป้าหมาย Offset = {TARGET_RADIAL_OFFSET_MM:+.3f} mm",
            "Gen ต่ำกว่า LP 0.10 mm (ชดเชยตกท้องช้าง)",
            is_radial_raw=True
        )

        fig1.text(0.08, 0.015,
                  "เกณฑ์มาตรฐาน กฟผ. แม่เมาะ: เกจวัด Radial อ่านเป็นเลขจำนวนเต็มดิบ (ตรวจเช็กผลต่าง <= 3 ขีด) | กล่องข้อความ = ระยะทางกลจริง (mm)",
                  fontsize=9.5, style='italic', bbox=dict(boxstyle='round,pad=0.5', facecolor='#F5F5F5', edgecolor='gray'))

        plt.subplots_adjust(top=0.95, bottom=0.08, hspace=0.38, wspace=0.25)
        st.pyplot(fig1)

    # ---------------------------------------------------------------------
    # Tab 3: Dial Setup Diagram
    # ---------------------------------------------------------------------
    with tab3:
        st.subheader(f"🔍 ไดอะแกรมติดตั้งเกจและการจำลองเป้าหมาย [Solution {choice_val}]")

        fig3 = plt.figure(figsize=(15, 9.8))

        ax_setup = fig3.add_subplot(2, 2, (1, 2))
        draw_coupling_physical_setup(ax_setup, choice_val)

        ax_exp_face = fig3.add_subplot(2, 2, 3)
        draw_dial_crosshair(
            ax_exp_face,
            "เกจวัดจำลองแนวแกน (Expected Face)",
            "A",
            0.000, TARGET_AXIAL_GAP_MM, 0.000, 0.000,
            '#2E7D32',
            f"Strategy: Solution {choice_val}",
            f"เป้าหมาย Gap = {TARGET_AXIAL_GAP_MM:+.3f} mm",
            is_radial_raw=False
        )

        ax_exp_rim = fig3.add_subplot(2, 2, 4)
        draw_dial_crosshair(
            ax_exp_rim,
            "เกจวัดจำลองแนวรัศมี (Expected Rim)",
            "R",
            0, target_radial_raw_bottom, target_radial_raw_side, target_radial_raw_side,
            '#2E7D32',
            f"Offset = {TARGET_RADIAL_OFFSET_MM:+.3f} mm (Gen ต่ำกว่า)",
            f"เข็มล่างชี้เลขดิบ = {target_radial_raw_bottom:+d} ขีด",
            is_radial_raw=True
        )

        plt.subplots_adjust(top=0.95, bottom=0.08, hspace=0.38, wspace=0.25)
        st.pyplot(fig3)

    # ---------------------------------------------------------------------
    # Tab 4: ขั้นตอนการคำนวณอย่างละเอียดตามหนังสือ อ.สมเกียรติ สมหล่อ
    # ---------------------------------------------------------------------
    with tab4:
        st.subheader("📝 ขั้นตอนและวิธีการคำนวณตามหนังสือ \"Alignment & Eccentricity\"")
        st.caption("อ้างอิงตามหนังสือของ นายสมเกียรติ สมหล่อ แสดงครบทั้งแนวบน-ล่าง (T & B) และแนวซ้าย-ขวา (L & R)")

        # ตอนที่ 1: ตรวจสอบความถูกต้องของเกจและแปลงค่าเทียบศูนย์
        with st.expander("🔹 ตอนที่ 1: การตรวจสอบค่า Alignment และแปลงเป็นค่าแสดงความแตกต่างเทียบศูนย์", expanded=True):
            st.markdown(
                "**หลักการ:** ค่าที่อ่านได้ในตำแหน่งตรงข้ามกัน เมื่อรวมกันตามเครื่องหมายต้องใกล้เคียงกัน ($T + B = L + R$) ผิดพลาดได้ไม่เกิน 3 ขีด"
            )
            col_t1, col_t2 = st.columns(2)
            with col_t1:
                st.markdown("**1.1 ตรวจสอบแนว RADIAL (เกจวัดดิบ):**")
                st.latex(rf"T + B = ({st.session_state.r_top}) + ({st.session_state.r_bottom}) = {st.session_state.r_top + st.session_state.r_bottom}")
                st.latex(rf"L + R = ({st.session_state.r_left}) + ({st.session_state.r_right}) = {st.session_state.r_left + st.session_state.r_right}")
                st.write(f"ผลต่าง $|(T+B) - (L+R)| = |({st.session_state.r_top + st.session_state.r_bottom}) - ({st.session_state.r_left + st.session_state.r_right})| = {diff_r_raw}$ ขีด")
                if valid_r:
                    st.success(f"✅ ผลต่าง = {diff_r_raw} ขีด (ไม่เกิน 3 ขีด ตามเกณฑ์มาตรฐาน) $\\rightarrow$ **ค่าถูกต้อง นำไปคำนวณต่อได้**")
                else:
                    st.error(f"❌ ผลต่าง = {diff_r_raw} ขีด เกินเกณฑ์ 3 ขีด $\\rightarrow$ ต้องตรวจเช็กการวัดใหม่")

                st.markdown("**แปลงค่า TIR แนว Radial เทียบศูนย์:**")
                st.write(f"- **แนวบน-ล่าง (T & B):** $T = 0$, $B = {st.session_state.r_bottom - st.session_state.r_top:+d}$ ขีด")
                st.write(f"- **แนวซ้าย-ขวา (L & R):** นำ $({-st.session_state.r_left:+d})$ บวกเข้าทั้งซ้ายและขวา $\\rightarrow L = 0$, $R = {r_lr_diff_div:+d}$ ขีด")

            with col_t2:
                st.markdown("**1.2 ตรวจสอบแนว AXIAL (ครบทั้ง บน-ล่าง และ ซ้าย-ขวา):**")
                st.write("**แนวบน-ล่าง (T & B):**")
                st.latex(rf"T = \frac{{{st.session_state.g1_0:.3f} + {st.session_state.g2_0:.3f}}}{{2}} = {raw_a_top:.3f}\text{{ mm}}, \quad B = \frac{{{st.session_state.g1_180:.3f} + {st.session_state.g2_180:.3f}}}{{2}} = {raw_a_bottom:.3f}\text{{ mm}}")
                st.write(rf"ผลต่างช่องว่างแนวบน-ล่าง $(B - T) = {raw_a_bottom:.3f} - {raw_a_top:.3f} = \mathbf{{{delta_x_v:+.3f}\text{{ mm}}}}$ ({'ล่างอ้า' if delta_x_v >= 0 else 'บนอ้า'})")

                st.write("**แนวซ้าย-ขวา (L & R):**")
                st.latex(rf"L = \frac{{{st.session_state.g1_90:.3f} + {st.session_state.g2_90:.3f}}}{{2}} = {raw_a_left:.3f}\text{{ mm}}, \quad R = \frac{{{st.session_state.g1_270:.3f} + {st.session_state.g2_270:.3f}}}{{2}} = {raw_a_right:.4f}\text{{ mm}}")
                st.write(rf"ผลต่างช่องว่างแนวซ้าย-ขวา $(L - R) = {raw_a_left:.3f} - {raw_a_right:.4f} = \mathbf{{{delta_gap_lr:+.4f}\text{{ mm}}}}$ ({'ซ้ายอ้า' if delta_gap_lr >= 0 else 'ขวาอ้า'})")

        # ตอนที่ 2: กฎการหาร 2 ของ Radial
        with st.expander("🔹 ตอนที่ 2: การหาตำแหน่งจริงของเพลาจากเกจ Radial ทั้ง T&B และ L&R", expanded=True):
            st.markdown(
                "**ทฤษฎีในหนังสือ:** *"
                "ค่าที่เราอ่านได้จาก Dial Gauge ในแนว Radial จะเป็น 2 เท่าของตำแหน่งจริงของเพลา เมื่อจะนำค่ามาทำการปรับจะต้องทำการหารด้วย 2 เสียก่อนเสมอ"
                "*"
            )
            c_r1, c_r2 = st.columns(2)
            with c_r1:
                st.markdown("**2.1 แนวบน-ล่าง (T & B):**")
                st.latex(rf"\text{{ตำแหน่งเพลาผิดไปจริง}} = \frac{{{st.session_state.r_bottom - st.session_state.r_top}}}{{2}} = {(st.session_state.r_bottom - st.session_state.r_top)/2.0:+.1f}\text{{ ขีด}} = {actual_offset_v:+.3f}\text{{ mm}}")
                st.latex(rf"\Delta Y_{{TB}} = ({actual_offset_v:+.3f}) - (\text{{เป้า }}{TARGET_RADIAL_OFFSET_MM:+.3f}) = {delta_y_v:+.3f}\text{{ mm}}")
                st.write(f"👉 **เพลา Gen อยู่ต่ำกว่าเกณฑ์เป้าหมาย {abs(delta_y_v):.3f} mm**")

            with c_r2:
                st.markdown("**2.2 แนวซ้าย-ขวา (L & R):**")
                st.latex(rf"\text{{ตำแหน่งเพลาผิดไปจริง}} = \frac{{{r_lr_diff_div:+d}}}{{2}} = {r_lr_diff_div/2.0:+.1f}\text{{ ขีด}} = {actual_offset_h:+.3f}\text{{ mm}}")
                st.latex(rf"\Delta Y_{{LR}} = {actual_offset_h:+.3f}\text{{ mm}} \quad (\text{{เทียบเป้า }} 0.000\text{{ mm}})")
                st.write(f"👉 **เพลาเบี่ยงไปทาง{'ขวา (R)' if actual_offset_h >= 0 else 'ซ้าย (L)'} {abs(actual_offset_h):.3f} mm**")

        # ตอนที่ 3: คำนวณ 4 ขั้นตอนตามหนังสือ
        with st.expander(f"🔹 ตอนที่ 3: ขั้นตอนการคำนวณหาค่าที่จะต้องปรับ 4 ขั้นตอน [SOLUTION {choice_val}]", expanded=True):
            st.markdown(
                "**หลักการสำคัญ:** *\"ในการปรับค่า Alignment จะต้องยึดถือหลักว่า จะต้องปรับค่าแนวแกน (Axial) ก่อน แล้วจึงค่อยปรับค่าตามแนวตั้งฉาก (Radial)\"*\n\n"
                r"ตามทฤษฎีบทที่ 62 สามเหลี่ยมคล้าย: $\frac{QR}{PQ} = \frac{BC}{AC} = \frac{DE}{AD}$"
            )
            st.markdown("---")

            col_step_tb, col_step_lr = st.columns(2)

            with col_step_tb:
                st.markdown("### 1️⃣ แนวบนและล่าง (T & B)")
                st.markdown("**ข้อ 1. ปรับค่า Axial ในแนวบนและล่าง (T & B) ด้วยสามเหลี่ยมคล้าย:**")
                st.latex(r"\frac{\Delta X_{TB}}{D} = \frac{X}{L_1} = \frac{Y}{L_2}")
                if choice_val in ['1', '2']:
                    st.latex(rf"X_{{\text{{LP Brg.4}}}} = -\frac{{{delta_x_v:+.3f} \times {st.session_state.l_brg4:.0f}}}{{{st.session_state.d_coupling:.0f}}} = {lift_brg4:+.3f}\text{{ mm}} \quad \text{{...(1)}}")
                if choice_val in ['2', '3']:
                    st.latex(rf"X_{{\text{{Gen-F}}}} = \frac{{{delta_x_v:+.3f} \times {st.session_state.l_gen_f:.0f}}}{{{st.session_state.d_coupling:.0f}}} = {lift_gen_f:+.3f}\text{{ mm}} \quad \text{{...(1)}}")
                    st.latex(rf"Y_{{\text{{Gen-M}}}} = \frac{{{delta_x_v:+.3f} \times {st.session_state.l_gen_m:.0f}}}{{{st.session_state.d_coupling:.0f}}} = {lift_gen_m:+.3f}\text{{ mm}}")
                    st.latex(rf"Z_{{\text{{Gen-R}}}} = \frac{{{delta_x_v:+.3f} \times {st.session_state.l_gen_r:.0f}}}{{{st.session_state.d_coupling:.0f}}} = {lift_gen_r:+.3f}\text{{ mm}} \quad \text{{...(2)}}")

                st.markdown("**ข้อ 2. ปรับค่า Radial ในแนวบนและล่าง (T & B):**")
                st.caption(r"นำค่าจากข้อ 1 มารวมกับระยะเยื้องศูนย์จริงแนวบน-ล่าง $\Delta Y_{TB}$")
                if choice_val == '1':
                    st.latex(rf"\text{{Shim}}_{{\text{{LP Brg.4}}}} = ({lift_brg4:+.3f}) + ({delta_y_v:+.3f}) = \mathbf{{{shim_b4:+.3f}\text{{ mm}}}}")
                elif choice_val == '2':
                    st.latex(rf"\text{{Shim}}_{{\text{{LP Brg.4 (50\%)}}}} = 0.5 \times [({lift_brg4:+.3f}) + ({delta_y_v:+.3f})] = \mathbf{{{shim_b4:+.3f}\text{{ mm}}}}")
                    st.latex(rf"\text{{Shim}}_{{\text{{Gen-F (50\%)}}}} = 0.5 \times [({lift_gen_f:+.3f}) - ({delta_y_v:+.3f})] = \mathbf{{{shim_f:+.3f}\text{{ mm}}}}")
                    st.latex(rf"\text{{Shim}}_{{\text{{Gen-R (50\%)}}}} = 0.5 \times [({lift_gen_r:+.3f}) - ({delta_y_v:+.3f})] = \mathbf{{{shim_r:+.3f}\text{{ mm}}}}")
                else:
                    st.latex(rf"\text{{Shim}}_{{\text{{Gen-F}}}} = ({lift_gen_f:+.3f}) - ({delta_y_v:+.3f}) = \mathbf{{{shim_f:+.3f}\text{{ mm}}}}")
                    st.latex(rf"\text{{Shim}}_{{\text{{Gen-M}}}} = ({lift_gen_m:+.3f}) - ({delta_y_v:+.3f}) = \mathbf{{{shim_m:+.3f}\text{{ mm}}}}")
                    st.latex(rf"\text{{Shim}}_{{\text{{Gen-R}}}} = ({lift_gen_r:+.3f}) - ({delta_y_v:+.3f}) = \mathbf{{{shim_r:+.3f}\text{{ mm}}}}")

            with col_step_lr:
                st.markdown("### 2️⃣ แนวซ้ายและขวา (L & R)")
                st.markdown("**ข้อ 3. ปรับค่า Axial ในแนวซ้ายและขวา (L & R) ด้วยสามเหลี่ยมคล้าย:**")
                st.latex(r"\frac{\Delta X_{LR}}{D} = \frac{X}{L_1} = \frac{Y}{L_2}")
                if choice_val in ['1', '2']:
                    st.latex(rf"X_{{\text{{LP Brg.4}}}} = -\frac{{{delta_gap_lr:+.4f} \times {st.session_state.l_brg4:.0f}}}{{{st.session_state.d_coupling:.0f}}} = {shift_ax_b4:+.3f}\text{{ mm}} \quad \text{{...(3)}}")
                if choice_val in ['2', '3']:
                    st.latex(rf"X_{{\text{{Gen-F}}}} = \frac{{{delta_gap_lr:+.4f} \times {st.session_state.l_gen_f:.0f}}}{{{st.session_state.d_coupling:.0f}}} = {shift_ax_f:+.3f}\text{{ mm}} \quad \text{{...(3)}}")
                    st.latex(rf"Y_{{\text{{Gen-M}}}} = \frac{{{delta_gap_lr:+.4f} \times {st.session_state.l_gen_m:.0f}}}{{{st.session_state.d_coupling:.0f}}} = {shift_ax_m:+.3f}\text{{ mm}}")
                    st.latex(rf"Z_{{\text{{Gen-R}}}} = \frac{{{delta_gap_lr:+.4f} \times {st.session_state.l_gen_r:.0f}}}{{{st.session_state.d_coupling:.0f}}} = {shift_ax_r:+.3f}\text{{ mm}} \quad \text{{...(3)}}")

                st.markdown("**ข้อ 4. ปรับค่า Radial ตามแนวซ้ายและขวา (L & R):**")
                st.caption(r"นำค่าจากข้อ 3 มาหักล้างกับระยะเยื้องศูนย์จริงแนวซ้าย-ขวา $\Delta Y_{LR}$")
                if choice_val == '1':
                    st.latex(rf"\text{{ปรับซ้าย-ขวา}}_{{\text{{LP Brg.4}}}} = ({shift_ax_b4:+.3f}) - ({actual_offset_h:+.3f}) = \mathbf{{{shift_b4:+.3f}\text{{ mm}}}}")
                elif choice_val == '2':
                    st.latex(rf"\text{{ปรับซ้าย-ขวา}}_{{\text{{LP Brg.4 (50\%)}}}} = 0.5 \times [({shift_ax_b4:+.3f}) - ({actual_offset_h:+.3f})] = \mathbf{{{shift_b4:+.3f}\text{{ mm}}}}")
                    st.latex(rf"\text{{ปรับซ้าย-ขวา}}_{{\text{{Gen-F (50\%)}}}} = 0.5 \times [({shift_ax_f:+.3f}) - ({actual_offset_h:+.3f})] = \mathbf{{{shift_f:+.3f}\text{{ mm}}}}")
                    st.latex(rf"\text{{ปรับซ้าย-ขวา}}_{{\text{{Gen-R (50\%)}}}} = 0.5 \times [({shift_ax_r:+.3f}) - ({actual_offset_h:+.3f})] = \mathbf{{{shift_r:+.3f}\text{{ mm}}}}")
                else:
                    st.latex(rf"\text{{ปรับซ้าย-ขวา}}_{{\text{{Gen-F}}}} = ({shift_ax_f:+.3f}) - ({actual_offset_h:+.3f}) = \mathbf{{{shift_f:+.3f}\text{{ mm}}}}")
                    st.latex(rf"\text{{ปรับซ้าย-ขวา}}_{{\text{{Gen-M}}}} = ({shift_ax_m:+.3f}) - ({actual_offset_h:+.3f}) = \mathbf{{{shift_m:+.3f}\text{{ mm}}}}")
                    st.latex(rf"\text{{ปรับซ้าย-ขวา}}_{{\text{{Gen-R}}}} = ({shift_ax_r:+.3f}) - ({actual_offset_h:+.3f}) = \mathbf{{{shift_r:+.3f}\text{{ mm}}}}")

            # สรุปเป็น Vector
            st.markdown("---")
            st.markdown("### 🏁 สรุปเขียนเป็น Vector (หน่วย mm และ 1/100 mm)")
            v_col1, v_col2 = st.columns(2)
            with v_col1:
                dir_v_b4 = "T (ขึ้น/หนุนชิม)" if shim_b4 >= 0 else "B (ลง/ถอนชิม)"
                dir_h_b4 = "L (ไปทางซ้าย)" if shift_b4 >= 0 else "R (ไปทางขวา)"
                st.info(
                    f"**LP Bearing 4:**\n"
                    f"- แนวดิ่ง ({dir_v_b4}): **{abs(shim_b4):.3f} mm** ({abs(shim_b4)*100:.1f} ขีด)\n"
                    f"- แนวนอน ({dir_h_b4}): **{abs(shift_b4):.3f} mm** ({abs(shift_b4)*100:.1f} ขีด)"
                )
            with v_col2:
                dir_v_f = "T (หนุนชิม)" if shim_f >= 0 else "B (ถอนชิม)"
                dir_h_f = "L (ไปทางซ้าย)" if shift_f >= 0 else "R (ไปทางขวา)"
                dir_h_r = "L (ไปทางซ้าย)" if shift_r >= 0 else "R (ไปทางขวา)"
                st.success(
                    f"**Generator Legs (F / M / R):**\n"
                    f"- แนวดิ่ง ({dir_v_f}): หน้า **{abs(shim_f):.3f}** | กลาง **{abs(shim_m):.3f}** | หลัง **{abs(shim_r):.3f} mm**\n"
                    f"- แนวนอน (ซ้าย-ขวา): หน้า **{abs(shift_f):.3f} ({dir_h_f})** | กลาง **{abs(shift_m):.3f}** | หลัง **{abs(shift_r):.3f} mm ({dir_h_r})**"
                )
