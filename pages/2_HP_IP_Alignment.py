"""
Streamlit Web Application: HP-IP Coupling Alignment Precision Tool (100% Zoom Balanced Edition)
Case: IP - LP - Generator Already Aligned (FIXED 100%) | Installing & Aligning HP Rotor
Calculation & Drawing Method: 100% Strictly Based on "Alignment & Eccentricity" Manual
Author: นายสมเกียรติ สมหล่อ (แผนกกังหันไอน้ำ กองกังหัน ฝ่ายบำรุงรักษาเครื่องกล กฟผ.)
Plant Standard: EGAT Mae Moh Power Plant Unit 8-13 (หปกร-ธ.)
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
import streamlit as st

# ตั้งค่าระบบแสดงผล (เปิดแถบ Sidebar อัตโนมัติเพื่อให้สลับหน้าได้สะดวก)
st.set_page_config(
    page_title="EGAT Mae Moh 8-13 | HP-IP Alignment",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial', 'Helvetica']
plt.rcParams['axes.unicode_minus'] = False

# =========================================================================
# Industrial Power Plant CSS (Original Layout + Proportioned for 100% Zoom)
# =========================================================================
st.markdown("""
<style>
    /* จัดระยะขอบหน้าจอให้พอดี 100% */
    .block-container {
        padding-top: 0.7rem !important;
        padding-bottom: 0.5rem !important;
        padding-left: 1.5rem !important;
        padding-right: 1.5rem !important;
        max-width: 100% !important;
    }
    header[data-testid="stHeader"] {
        height: 1.8rem !important;
        background: transparent !important;
    }
    .stApp {
        background-color: #F0F4F8;
    }
    div[data-testid="stVerticalBlock"] > div {
        gap: 0.32rem !important;
    }
    /* Header Banner รูปแบบเดิม ปรับความสูงให้พอดี */
    .pp-header {
        background: linear-gradient(135deg, #0B192C 0%, #1E3E62 65%, #0F2C59 100%);
        padding: 8px 20px;
        border-radius: 10px;
        color: #FFFFFF;
        margin-bottom: 4px;
        border-bottom: 3.5px solid #FFB000;
        box-shadow: 0 3px 10px rgba(11, 25, 44, 0.18);
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .pp-header-title {
        font-size: 17.5px;
        font-weight: 800;
        color: #FFFFFF;
        margin: 0;
    }
    .pp-header-sub {
        font-size: 11.5px;
        color: #FFD54F;
        margin: 1px 0 0 0;
        font-weight: 600;
    }
    .pp-badge {
        background-color: #FFB000;
        color: #0B192C;
        padding: 4px 12px;
        border-radius: 15px;
        font-weight: 800;
        font-size: 11px;
        white-space: nowrap;
    }
    .section-title-compact {
        font-size: 15px;
        font-weight: 800;
        color: #0B192C;
        margin: 0 0 2px 0;
    }
    .sheet-title {
        background: linear-gradient(90deg, #1E3E62 0%, #2B547E 100%);
        color: #FFFFFF;
        padding: 5px 8px;
        text-align: center;
        font-weight: 700;
        font-size: 12.5px;
        border-radius: 7px 7px 0 0;
        margin-top: 2px;
    }
    .calc-box {
        background-color: #E8F5E9;
        border: 1.5px solid #4CAF50;
        border-radius: 6px;
        height: 29px;
        line-height: 26px;
        text-align: center;
        font-weight: 800;
        color: #1B5E20;
        font-size: 12.5px;
    }
    .calc-box-empty {
        background-color: #ECEFF1;
        border: 1px dashed #B0BEC5;
        border-radius: 6px;
        height: 29px;
        line-height: 27px;
        text-align: center;
        color: #90A4AE;
        font-size: 12.5px;
    }
    /* ปรับสัดส่วน Number Input คงปุ่ม +/- รูปแบบเดิมแต่ไม่เบียดช่อง */
    div[data-testid="stNumberInput"] label p {
        font-size: 11.5px !important;
        font-weight: 700 !important;
        margin-bottom: 1px !important;
    }
    div[data-testid="stNumberInput"] div[data-baseweb="input"] {
        height: 29px !important;
    }
    div[data-testid="stNumberInput"] input {
        padding: 2px 4px !important;
        font-size: 12px !important;
        font-weight: 700 !important;
        height: 29px !important;
    }
    div[data-testid="stNumberInput"] button {
        width: 20px !important;
        height: 29px !important;
        padding: 0 !important;
    }
    /* ปรับขนาด Radio และปุ่มกด */
    .stRadio > div {
        gap: 0.2rem !important;
    }
    .stRadio label p {
        font-size: 12.5px !important;
    }
    .stButton button {
        height: 31px !important;
        padding: 0 8px !important;
        font-size: 12px !important;
        font-weight: 700 !important;
    }
    /* ปรับการ์ดใบสั่งงานทั้ง 3 ใบให้สูงเท่ากันและพอดีจอ */
    div[data-testid="stHorizontalBlock"] {
        align-items: stretch !important;
    }
    .tech-card {
        background-color: #FFFFFF;
        border-radius: 10px;
        padding: 10px 12px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
        border-top: 5px solid #1565C0;
        height: 100%;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }
    .tech-card-fixed {
        border-top: 5px solid #546E7A;
        background-color: #F8FAFC;
    }
    .tech-card-adjust {
        border-top: 5px solid #FF6F00;
    }
    .brg-name {
        font-size: 14.5px;
        font-weight: 800;
        color: #0B192C;
        margin-bottom: 1px;
    }
    .brg-arm {
        font-size: 11px;
        color: #607D8B;
        font-weight: 600;
        margin-bottom: 6px;
        border-bottom: 1px solid #ECEFF1;
        padding-bottom: 3px;
    }
    .action-row {
        background-color: #F1F8E9;
        border-left: 4px solid #2E7D32;
        padding: 6px 8px;
        border-radius: 6px;
        margin-bottom: 5px;
    }
    .action-row-down {
        background-color: #FFEBEE;
        border-left: 4px solid #C62828;
        padding: 6px 8px;
        border-radius: 6px;
        margin-bottom: 5px;
    }
    .action-row-horiz {
        background-color: #E3F2FD;
        border-left: 4px solid #1565C0;
        padding: 6px 8px;
        border-radius: 6px;
        margin-bottom: 0px;
    }
    .action-row-lock {
        background-color: #ECEFF1;
        border-left: 4px solid #607D8B;
        padding: 18px 8px;
        border-radius: 6px;
        text-align: center;
        font-weight: 700;
        color: #455A64;
        flex-grow: 1;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
    }
    .action-label {
        font-size: 11px;
        color: #455A64;
        font-weight: 700;
    }
    .action-val {
        font-size: 13px;
        font-weight: 800;
        color: #102027;
        margin-top: 1px;
    }
    .shim-detail {
        font-size: 10.5px;
        color: #37474F;
        margin-top: 2px;
        font-weight: 600;
        line-height: 1.25;
    }
    .khid-tag {
        display: inline-block;
        background-color: #263238;
        color: #FFD54F;
        font-size: 10px;
        font-weight: 700;
        padding: 1.5px 7px;
        border-radius: 8px;
        margin-top: 3px;
    }
</style>
""", unsafe_allow_html=True)

# เกณฑ์ความคลาดเคลื่อนตามคู่มือ (0.02 - 0.03 mm)
TOLERANCE_CHECK_MM = 0.030

# =========================================================================
# Session State Initialization
# =========================================================================
input_keys = [
    'd_coupling', 'l_brg2', 'l_brg1',
    'r_top', 'r_bottom', 'r_left', 'r_right',
    'g1_top', 'g2_top',
    'g1_left', 'g2_left',
    'g1_bot', 'g2_bot',
    'g1_right', 'g2_right',
]

for key in input_keys:
    if key not in st.session_state:
        st.session_state[key] = None


# =========================================================================
# ฟังก์ชันเปลี่ยนค่า TIR เป็นค่าแสดงความแตกต่างเทียบศูนย์ (0)
# =========================================================================
def convert_tir_to_zero_diff(t_val: float, b_val: float, l_val: float, r_val: float, lock_top_zero: bool = False):
    if lock_top_zero:
        add_tb = -t_val
    else:
        add_tb = -min(t_val, b_val)

    z_t = t_val + add_tb
    z_b = b_val + add_tb

    add_lr = -min(l_val, r_val)
    z_l = l_val + add_lr
    z_r = r_val + add_lr

    return z_t, z_b, z_l, z_r, add_tb, add_lr


# =========================================================================
# แผนผังชุดเพลา HP -> [IP - LP - GEN FIXED] (รูปแบบเดิม ปรับสัดส่วนพอดี 100%)
# =========================================================================
def render_powerplant_schematic(lock_brg1: bool):
    hp_col = "#E65100"
    fixed_col = "#1565C0"
    b1_col = "#546E7A" if lock_brg1 else "#FF6F00"
    hp_badge = "HP ROTOR | 🔧 ปรับเฉพาะ Brg.2" if lock_brg1 else "HP ROTOR | 🔧 ปรับ Brg.1 & Brg.2"

    svg_html = (
        f'<div style="background:#FFFFFF; border-radius:10px; padding:8px 14px; border:1px solid #CFD8DC; box-shadow:0 2px 8px rgba(0,0,0,0.04); margin-bottom:4px;">'
        f'<div style="font-size:12px; font-weight:800; color:#1E3E62; margin-bottom:3px; display:flex; justify-content:space-between; flex-wrap:wrap;">'
        f'<span>🏭 แผนผังชุดเพลา HP – [IP – LP – GEN FIXED] (EGAT MAE MOH UNIT 8-13)</span>'
        f'<span style="color:#1565C0;">หลักการ: ยึด IP–LP–Gen เป็นหลักคงที่ 100%</span>'
        f'</div>'
        f'<svg viewBox="0 0 1000 165" width="100%" height="auto" xmlns="http://www.w3.org/2000/svg">'
        f'<rect x="15" y="138" width="970" height="21" rx="4" fill="#263238" />'
        f'<text x="500" y="152" fill="#FFFFFF" font-size="10.5" font-weight="bold" text-anchor="middle" letter-spacing="0.5">TURBINE-GENERATOR CONCRETE PEDESTAL (IP - LP - GEN ALIGNED &amp; LOCKED)</text>'
        f'<rect x="45" y="84" width="910" height="12" fill="#90A4AE" stroke="#37474F" stroke-width="1.5"/>'
        # HP ROTOR
        f'<polygon points="75,56 235,44 235,132 75,120" fill="{hp_col}" fill-opacity="0.16" stroke="{hp_col}" stroke-width="2.5"/>'
        f'<line x1="115" y1="53" x2="115" y2="123" stroke="{hp_col}" stroke-width="2"/>'
        f'<line x1="155" y1="50" x2="155" y2="126" stroke="{hp_col}" stroke-width="2"/>'
        f'<line x1="195" y1="47" x2="195" y2="129" stroke="{hp_col}" stroke-width="2"/>'
        f'<rect x="52" y="5" width="215" height="21" rx="10.5" fill="{hp_col}"/>'
        f'<text x="159" y="19" fill="#FFFFFF" font-size="10" font-weight="bold" text-anchor="middle">{hp_badge}</text>'
        # HP-IP COUPLING
        f'<rect x="278" y="63" width="10" height="52" rx="2" fill="#D32F2F"/>'
        f'<rect x="292" y="63" width="10" height="52" rx="2" fill="#1565C0"/>'
        f'<line x1="290" y1="50" x2="290" y2="132" stroke="#D32F2F" stroke-width="1.8" stroke-dasharray="4,3"/>'
        f'<rect x="234" y="31" width="112" height="18" rx="5" fill="#D32F2F"/>'
        f'<text x="290" y="43" fill="#FFFFFF" font-size="9.5" font-weight="bold" text-anchor="middle">HP-IP COUPLING</text>'
        # IP ROTOR
        f'<polygon points="340,52 495,42 495,134 340,124" fill="{fixed_col}" fill-opacity="0.14" stroke="{fixed_col}" stroke-width="2.2"/>'
        f'<text x="417" y="77" fill="{fixed_col}" font-size="11.5" font-weight="bold" text-anchor="middle">IP ROTOR</text>'
        f'<rect x="520" y="67" width="8" height="44" fill="#37474F"/>'
        f'<rect x="531" y="67" width="8" height="44" fill="#37474F"/>'
        # LP ROTOR
        f'<polygon points="565,48 700,38 700,137 565,127" fill="{fixed_col}" fill-opacity="0.14" stroke="{fixed_col}" stroke-width="2.2"/>'
        f'<text x="632" y="77" fill="{fixed_col}" font-size="11.5" font-weight="bold" text-anchor="middle">LP ROTOR</text>'
        f'<rect x="722" y="67" width="8" height="44" fill="#37474F"/>'
        f'<rect x="733" y="67" width="8" height="44" fill="#37474F"/>'
        # GENERATOR
        f'<rect x="765" y="42" width="165" height="92" rx="7" fill="{fixed_col}" fill-opacity="0.14" stroke="{fixed_col}" stroke-width="2.2"/>'
        f'<text x="847" y="77" fill="{fixed_col}" font-size="11.5" font-weight="bold" text-anchor="middle">GENERATOR</text>'
        # FIXED BANNER
        f'<rect x="345" y="5" width="580" height="21" rx="10.5" fill="{fixed_col}"/>'
        f'<text x="635" y="19" fill="#FFFFFF" font-size="10.5" font-weight="bold" text-anchor="middle">🔒 IP – LP – GENERATOR | ALIGNED &amp; LOCKED (เพลาหลักคงที่ไม่มีการปรับ)</text>'
        # BEARINGS
        f'<polygon points="60,96 42,138 78,138" fill="{b1_col}" stroke="#263238" stroke-width="1.8"/>'
        f'<text x="60" y="131" fill="#FFFFFF" font-size="9.5" font-weight="bold" text-anchor="middle">Brg.1</text>'
        f'<polygon points="252,96 234,138 270,138" fill="#FF6F00" stroke="#263238" stroke-width="1.8"/>'
        f'<text x="252" y="131" fill="#FFFFFF" font-size="9.5" font-weight="bold" text-anchor="middle">Brg.2</text>'
        f'<polygon points="505,96 487,138 523,138" fill="#546E7A" stroke="#263238" stroke-width="1.6"/>'
        f'<text x="505" y="131" fill="#FFFFFF" font-size="9.5" font-weight="bold" text-anchor="middle">Brg.3</text>'
        f'<polygon points="710,96 692,138 728,138" fill="#546E7A" stroke="#263238" stroke-width="1.6"/>'
        f'<text x="710" y="131" fill="#FFFFFF" font-size="9.5" font-weight="bold" text-anchor="middle">Brg.4</text>'
        f'<polygon points="752,96 734,138 770,138" fill="#546E7A" stroke="#263238" stroke-width="1.6"/>'
        f'<text x="752" y="131" fill="#FFFFFF" font-size="9.5" font-weight="bold" text-anchor="middle">Brg.5</text>'
        f'<polygon points="942,96 924,138 960,138" fill="#546E7A" stroke="#263238" stroke-width="1.6"/>'
        f'<text x="942" y="131" fill="#FFFFFF" font-size="9.5" font-weight="bold" text-anchor="middle">Brg.6</text>'
        f'</svg>'
        f'</div>'
    )
    st.markdown(svg_html, unsafe_allow_html=True)


# =========================================================================
# ฟังก์ชันวาดรูปกากบาท Dial Gauge (R และ A)
# =========================================================================
def draw_dial_crosshair(ax, title_text, center_symbol, t_val, b_val, l_val, r_val, dial_color, badge_title, badge_desc, is_radial=False):
    ax.set_aspect('equal')
    ax.set_xlim(-2.45, 2.45)
    ax.set_ylim(-2.65, 2.45)
    ax.axis('off')

    is_zero_ref = "ZERO-REFERENCED" in title_text.upper()
    header_bg, header_bdr = ("#E3F2FD", "#1565C0") if is_zero_ref else ("#FFEBEE", "#C62828")

    ax.text(0, 2.10, title_text, ha='center', va='center', fontsize=10.5, fontweight='bold', color=header_bdr,
            bbox=dict(boxstyle='round,pad=0.42', facecolor=header_bg, edgecolor=header_bdr, lw=1.6))

    outer_ring = patches.Circle((0, 0), 0.88, edgecolor=dial_color, facecolor='#FAFAFA', linewidth=3.2, zorder=1)
    inner_ring = patches.Circle((0, 0), 0.82, edgecolor='#CFD8DC', facecolor='#FFFFFF', linewidth=1.2, zorder=2)
    ax.add_patch(outer_ring)
    ax.add_patch(inner_ring)

    ax.plot([-0.78, 0.78], [0, 0], color=dial_color, lw=2.0, linestyle='-', alpha=0.75, zorder=3)
    ax.plot([0, 0], [-0.78, 0.78], color=dial_color, lw=2.0, linestyle='-', alpha=0.75, zorder=3)

    hub = patches.Circle((0, 0), 0.25, facecolor='#FFFFFF', edgecolor=dial_color, lw=2.2, zorder=4)
    ax.add_patch(hub)
    ax.text(0, 0.0, center_symbol, ha='center', va='center', fontsize=18, fontweight='bold', color=dial_color, zorder=5)

    sub_unit = "Unit: mm (HP on IP)" if is_radial else "Diff: mm"
    ax.text(0, -0.48, sub_unit, ha='center', va='center', fontsize=8, fontweight='bold', color='#78909C', zorder=3)

    fmt = "+.2f" if is_radial else "+.3f"
    t_str = f"{t_val:{fmt}}" if abs(t_val) > 1e-9 else ("0.00" if is_radial else "0.000")
    b_str = f"{b_val:{fmt}}" if abs(b_val) > 1e-9 else ("0.00" if is_radial else "0.000")
    l_str = f"{l_val:{fmt}}" if abs(l_val) > 1e-9 else ("0.00" if is_radial else "0.000")
    r_str = f"{r_val:{fmt}}" if abs(r_val) > 1e-9 else ("0.00" if is_radial else "0.000")

    ax.text(0, 1.15, f"Top\n{t_str}", ha='center', va='bottom', fontsize=9.5, fontweight='bold')
    ax.text(0, -1.15, f"{b_str}\nBot", ha='center', va='top', fontsize=9.5, fontweight='bold')
    ax.text(-1.08, 0, f"Left\n{l_str}", ha='right', va='center', fontsize=9.5, fontweight='bold')
    ax.text(1.08, 0, f"Right\n{r_str}", ha='left', va='center', fontsize=9.5, fontweight='bold')

    txt_box = f"{badge_title}\n[{badge_desc}]"
    ax.text(0, -1.95, txt_box, ha='center', va='top', fontsize=9.2, fontweight='bold', color=header_bdr,
            bbox=dict(boxstyle='round,pad=0.42', facecolor=header_bg, edgecolor=header_bdr, lw=1.5))


# =========================================================================
# ฟังก์ชันวาดการติดตั้ง Dial Gauge
# =========================================================================
def draw_coupling_physical_setup(ax):
    ax.set_aspect('equal')
    ax.set_xlim(-2.2, 8.6)
    ax.set_ylim(-3.8, 4.3)
    ax.axis('off')

    ax.add_patch(patches.Rectangle((-1.8, -2.35), 10.0, 6.35, fill=False, edgecolor='#1E88E5', linewidth=1.6))
    ax.text(3.2, 3.72, "HP. - IP. COUPLING", ha='center', va='center', fontsize=12.5, fontweight='bold', color='#212121', family='serif')
    ax.text(-1.55, -2.10, "VIEW FROM GOV. END (LOOKING TOWARD GEN)", ha='left', va='center', fontsize=9.0, fontweight='bold', color='#212121', family='serif')

    hp_color = '#D84315'
    ip_color = '#1565C0'

    ax.add_patch(patches.Rectangle((-0.2, -0.65), 2.3, 1.3, facecolor=hp_color, fill=True, alpha=0.18, edgecolor='#212121', linewidth=2.0))
    ax.add_patch(patches.Rectangle((2.1, -1.55), 0.75, 3.1, facecolor=hp_color, fill=True, alpha=0.25, edgecolor='#212121', linewidth=2.2))
    ax.text(0.85, 0.0, "HP. TURBINE\n(ADJUST)", ha='center', va='center', color='#102027', fontsize=9.5, fontweight='bold', family='serif')

    ax.add_patch(patches.Rectangle((4.30, -0.65), 2.3, 1.3, facecolor=ip_color, fill=True, alpha=0.18, edgecolor='#212121', linewidth=2.0))
    ax.add_patch(patches.Rectangle((3.55, -1.55), 0.75, 3.1, facecolor=ip_color, fill=True, alpha=0.25, edgecolor='#212121', linewidth=2.2))
    ax.text(5.55, 0.0, "IP. TURBINE\n(FIXED REFERENCE)", ha='center', va='center', color='#102027', fontsize=9.5, fontweight='bold', family='serif')

    ax.plot([-0.7, 7.1], [0, 0], color='#455A64', lw=1.1, linestyle='-.')
    ax.annotate("", xy=(1.25, 0.80), xytext=(0.45, 0.80),
                arrowprops=dict(arrowstyle="->", connectionstyle="arc3,rad=-0.55", color='#212121', lw=1.5))
    ax.annotate("", xy=(5.95, 0.80), xytext=(5.15, 0.80),
                arrowprops=dict(arrowstyle="->", connectionstyle="arc3,rad=-0.55", color='#212121', lw=1.5))

    b_col = '#212121'
    ax.plot([2.475, 2.475, 3.925, 3.925], [1.55, 3.15, 3.15, 2.68], color=b_col, lw=1.8)
    ax.add_patch(patches.Circle((3.925, 2.38), 0.30, facecolor='#FF9800', edgecolor=b_col, lw=1.8, zorder=4))
    ax.text(3.925, 2.38, "R", ha='center', va='center', fontsize=9.5, fontweight='bold', color=b_col, zorder=5)
    ax.annotate("", xy=(3.925, 1.55), xytext=(3.925, 2.08), arrowprops=dict(arrowstyle="->", color=b_col, lw=1.8))
    ax.text(3.20, 3.25, "Radial (Rim)", ha='center', va='bottom', fontsize=8.8, fontweight='bold', color='#1565C0')

    ax.plot([2.65, 2.65, 5.15, 5.15, 4.92], [1.55, 3.32, 3.32, 1.32, 1.32], color=b_col, lw=1.8)
    ax.add_patch(patches.Circle((4.62, 1.32), 0.30, facecolor='#FF9800', edgecolor=b_col, lw=1.8, zorder=4))
    ax.text(4.62, 1.32, "G1", ha='center', va='center', fontsize=8.8, fontweight='bold', color=b_col, zorder=5)
    ax.annotate("", xy=(4.30, 1.32), xytext=(4.32, 1.32), arrowprops=dict(arrowstyle="->", color=b_col, lw=1.8))
    ax.text(5.28, 1.32, "G1 (Top Axial)", ha='left', va='center', fontsize=8.8, fontweight='bold', color='#D84315')

    ax.plot([2.475, 2.475, 5.15, 5.15, 4.92], [-1.55, -2.02, -2.02, -1.32, -1.32], color=b_col, lw=1.8)
    ax.add_patch(patches.Circle((4.62, -1.32), 0.30, facecolor='#FF9800', edgecolor=b_col, lw=1.8, zorder=4))
    ax.text(4.62, -1.32, "G2", ha='center', va='center', fontsize=8.8, fontweight='bold', color=b_col, zorder=5)
    ax.annotate("", xy=(4.30, -1.32), xytext=(4.32, -1.32), arrowprops=dict(arrowstyle="->", color=b_col, lw=1.8))
    ax.text(5.28, -1.32, "G2 (Bot Axial)", ha='left', va='center', fontsize=8.8, fontweight='bold', color='#D84315')

    status_txt = (
        "[MANUAL STANDARD: Mount Dial Gauge on HP -> Probe IP (FIXED REFERENCE)]\n"
        "* IP Rotor (with LP & Gen) is fixed as the reference centerline (no adjustment).\n"
        "* Sign Convention: (+) = Shaft probed is HIGHER / CLOSER | (-) = LOWER / FURTHER."
    )
    ax.text(3.2, -3.05, status_txt, ha='center', va='center', fontsize=9.0, fontweight='bold',
            bbox=dict(boxstyle='round,pad=0.52', facecolor="#E8F5E9", edgecolor="#2E7D32", lw=1.8))


# =========================================================================
# ฟังก์ชันวาดรูปประกอบค่า Alignment ตามวิธีเขียนรูปในคู่มือ
# =========================================================================
def draw_manual_book_diagram(ax, title, pos_lbl, neg_lbl,
                             ax_gap_mm, open_at_neg, hp_above_pos_mm,
                             lock_brg1, hp_action_list, sub_note):
    ax.set_aspect('equal')
    ax.axis('off')

    ax.plot([-5.2, 4.2], [0, 0], color='black', linestyle='--', linewidth=1.5, zorder=1)
    ax.text(4.15, 0.08, 'IP - LP - Generator Centerline (FIXED)', ha='right', va='bottom', fontsize=8.5, style='italic', color='#1565C0')

    flange_half_h = 0.85
    sq = 0.14

    hp_vis_off = 0.50 if hp_above_pos_mm > 0 else (-0.50 if hp_above_pos_mm < 0 else 0.0)
    hp_tilt = 0.24 if open_at_neg else (-0.24 if ax_gap_mm != 0 else 0.0)

    hp_cx = -0.55
    hp_top_x, hp_top_y = hp_cx + hp_tilt, hp_vis_off + flange_half_h
    hp_bot_x, hp_bot_y = hp_cx - hp_tilt, hp_vis_off - flange_half_h

    hp_col = '#D84315'
    ax.plot([hp_top_x, hp_bot_x], [hp_top_y, hp_bot_y], color=hp_col, linewidth=3.5, zorder=4)
    ax.plot(hp_cx, hp_vis_off, 'ko', markersize=5, zorder=5)

    dx_hp, dy_hp = -flange_half_h, hp_tilt
    norm_hp = np.hypot(dx_hp, dy_hp)
    ux_hp, uy_hp = dx_hp / norm_hp, dy_hp / norm_hp

    hp_end_x = hp_cx + ux_hp * 4.4
    hp_end_y = hp_vis_off + uy_hp * 4.4
    ax.plot([hp_cx, hp_end_x], [hp_vis_off, hp_end_y], color=hp_col, linewidth=3.2, zorder=3)

    fx_hp, fy_hp = hp_tilt / norm_hp, flange_half_h / norm_hp
    p1 = (hp_cx + ux_hp * sq, hp_vis_off + uy_hp * sq)
    p2 = (p1[0] + fx_hp * sq, p1[1] + fy_hp * sq)
    p3 = (hp_cx + fx_hp * sq, hp_vis_off + fy_hp * sq)
    ax.plot([p1[0], p2[0], p3[0]], [p1[1], p2[1], p3[1]], color='black', linewidth=1.1, zorder=5)

    ax.text(hp_cx + ux_hp * 2.45, hp_vis_off + uy_hp * 2.45 + 0.30, "HP TURBINE [ADJUST]",
            ha='center', va='bottom', fontsize=10, fontweight='bold', color=hp_col)

    positions_vis = [1.35, 3.75]
    for idx, (dist_v, (lbl_pt, act_pt)) in enumerate(zip(positions_vis, hp_action_list)):
        px = hp_cx + ux_hp * dist_v
        py = hp_vis_off + uy_hp * dist_v
        is_b1_locked = (idx == 1 and lock_brg1)
        tri_col = '#90A4AE' if is_b1_locked else '#FF9800'
        txt_col = '#37474F' if is_b1_locked else '#2E7D32'
        bg_c = '#ECEFF1' if is_b1_locked else '#E8F5E9'
        bd_c = '#78909C' if is_b1_locked else '#2E7D32'

        ax.plot(px, py - 0.11, marker='^', markersize=10, color=tri_col, markeredgecolor='black', zorder=6)
        ax.text(px, py - 0.25, f"{lbl_pt}\n{act_pt}", ha='center', va='top', fontsize=8.3, fontweight='bold',
                color=txt_col, bbox=dict(boxstyle='round,pad=0.25', facecolor=bg_c, edgecolor=bd_c, lw=1.1))

    ip_cx = 0.55
    ip_col = '#1565C0'
    ax.plot([ip_cx, ip_cx], [-flange_half_h, flange_half_h], color=ip_col, linewidth=3.5, zorder=4)
    ax.plot(ip_cx, 0, 'ko', markersize=5, zorder=5)
    ax.plot([ip_cx, ip_cx + 3.4], [0, 0], color=ip_col, linewidth=3.2, zorder=3)
    ax.plot([ip_cx + sq, ip_cx + sq, ip_cx], [0, sq, sq], color='black', linewidth=1.1, zorder=5)

    b3_x = ip_cx + 2.1
    ax.plot(b3_x, -0.11, marker='^', markersize=10, color='#90A4AE', markeredgecolor='black', zorder=6)
    ax.text(b3_x, 0.25, "IP TURBINE [FIXED]", ha='center', va='bottom', fontsize=10, fontweight='bold', color=ip_col)
    ax.text(b3_x, -0.25, "IP Brg.3 (4,085 mm)\nFIXED (0.000 mm)", ha='center', va='top', fontsize=8.4, fontweight='bold',
            color='#37474F',
            bbox=dict(boxstyle='round,pad=0.25', facecolor='#ECEFF1', edgecolor='#78909C', lw=1.1))

    dim_y = max(hp_top_y, flange_half_h) + 0.42
    ax.plot([hp_top_x, hp_top_x], [hp_top_y, dim_y + 0.12], color='black', linewidth=1.0)
    ax.plot([ip_cx, ip_cx], [flange_half_h, dim_y + 0.12], color='black', linewidth=1.0)
    ax.annotate('', xy=(hp_top_x, dim_y), xytext=(hp_top_x - 0.40, dim_y), arrowprops=dict(arrowstyle='->', color='black', lw=1.2))
    ax.annotate('', xy=(ip_cx, dim_y), xytext=(ip_cx + 0.40, dim_y), arrowprops=dict(arrowstyle='->', color='black', lw=1.2))
    ax.plot([hp_top_x, ip_cx], [dim_y, dim_y], color='black', linewidth=1.0)
    ax.text((hp_top_x + ip_cx) / 2, dim_y + 0.10, f"Axial = {abs(ax_gap_mm):.3f} mm",
            ha='center', va='bottom', fontsize=9.2, fontweight='bold', color='#8E24AA')

    dim_x = 0.0
    ax.plot([hp_cx, dim_x + 0.12], [hp_vis_off, hp_vis_off], color='black', linewidth=1.0)
    ax.plot([dim_x - 0.12, ip_cx], [0, 0], color='black', linewidth=1.0)
    y_hi, y_lo = max(hp_vis_off, 0.0), min(hp_vis_off, 0.0)
    if abs(y_hi - y_lo) > 0.05:
        ax.annotate('', xy=(dim_x, y_hi), xytext=(dim_x, y_hi + 0.35), arrowprops=dict(arrowstyle='->', color='black', lw=1.2))
        ax.annotate('', xy=(dim_x, y_lo), xytext=(dim_x, y_lo - 0.35), arrowprops=dict(arrowstyle='->', color='black', lw=1.2))
        ax.plot([dim_x, dim_x], [y_lo, y_hi], color='black', linewidth=1.0)
        ax.text(dim_x + 0.10, (y_hi + y_lo) / 2 + 0.15, f"TIR/2\n{abs(hp_above_pos_mm):.3f}",
                ha='left', va='center', fontsize=8.4, fontweight='bold', color='#C62828',
                bbox=dict(boxstyle='round,pad=0.15', facecolor='white', edgecolor='none', alpha=0.85))

    ax.text(-1.25, 1.25, pos_lbl, fontsize=13, fontweight='bold', color='black')
    ax.text(-1.25, -1.55, neg_lbl, fontsize=13, fontweight='bold', color='black')

    ax.text(4.15, -2.45, sub_note, ha='right', va='bottom', fontsize=8.4,
            bbox=dict(boxstyle='round,pad=0.38', facecolor='#FFFDE7', edgecolor='#FBC02D', lw=1.2))

    ax.set_title(title, fontsize=11.5, fontweight='bold', pad=12, color='#0A192F')
    ax.set_xlim(-5.3, 4.3)
    ax.set_ylim(-2.60, 2.25)


# =========================================================================
# Header Banner
# =========================================================================
st.markdown("""
<div class="pp-header">
    <div>
        <div class="pp-header-title">⚡ ระบบคำนวณตั้งศูนย์เพลา HP – IP COUPLING (IP–LP–GEN Fixed)</div>
        <div class="pp-header-sub">แผนกบำรุงรักษากังหัน (หปกร-ธ.) โรงไฟฟ้าแม่เมาะ MMT08-13</div>
    </div>
    <div class="pp-badge">EGAT MANUAL STANDARD</div>
</div>
""", unsafe_allow_html=True)

col_input, col_view = st.columns([1.12, 1.88], gap="medium")

# =========================================================================
# Left Panel: ใบกรอกข้อมูลรูปแบบเดิม (Proportioned for 100% Zoom)
# =========================================================================
with col_input:
    st.markdown('<div class="section-title-compact">📝 1. เลือกรูปแบบการปรับ & ป้อนค่าการวัด</div>', unsafe_allow_html=True)

    mode_options = [
        "โหมด 1: ปรับทั้ง HP Brg.1 และ Brg.2 (ทฤษฎีสามเหลี่ยมคล้ายสมบูรณ์)",
        "โหมด 2: ล็อก HP Brg.1 เป็นจุดหมุน — ปรับเฉพาะ Brg.2"
    ]
    mode_selected = st.radio("แนวทางการปรับ Bearing ชุดเพลา HP:", mode_options, key="hp_adjust_mode", label_visibility="collapsed")
    lock_brg1 = mode_selected.startswith("โหมด 2")

    b_col1, b_col2 = st.columns(2)
    if b_col1.button("📋 โหลดค่าตัวอย่าง", use_container_width=True):
        st.session_state.d_coupling = 650.0
        st.session_state.l_brg2 = 405.0
        st.session_state.l_brg1 = 3930.0
        st.session_state.r_top = 0.00
        st.session_state.r_bottom = -0.24
        st.session_state.r_left = -0.10
        st.session_state.r_right = -0.14
        st.session_state.g1_top, st.session_state.g2_top = 18.450, 18.510
        st.session_state.g1_left, st.session_state.g2_left = 18.420, 18.410
        st.session_state.g1_bot, st.session_state.g2_bot = 18.520, 18.440
        st.session_state.g1_right, st.session_state.g2_right = 18.460, 18.470
        st.rerun()

    if b_col2.button("🗑️ ล้างค่าทั้งหมด (Reset)", use_container_width=True):
        for k in input_keys:
            st.session_state[k] = None
        st.rerun()

    with st.expander("📏 ระยะแขน HP Rotor (ตามแบบแปลน 8-13)", expanded=True):
        m1, m2, m3 = st.columns(3)
        with m1:
            st.number_input("โตแปลน D (mm)", value=None, placeholder="650", step=10.0, key="d_coupling")
        with m2:
            st.number_input("ถึง Brg.2 (mm)", value=None, placeholder="405", step=5.0, key="l_brg2")
        with m3:
            st.number_input("ถึง Brg.1 (mm)", value=None, placeholder="3930", step=5.0, key="l_brg1")

    st.markdown('<div class="sheet-title">ตารางบันทึกค่า Coupling HP–IP (หน่วย: mm)</div>', unsafe_allow_html=True)

    st.markdown("<div style='font-size:12.5px; font-weight:700; margin-top:1px;'>1) ค่าแนวรัศมี (Radial - จับ HP จี้ IP)</div>", unsafe_allow_html=True)
    rc1, rc2, rc3, rc4 = st.columns(4)
    with rc1:
        st.number_input("Top", value=None, placeholder="0.00", step=0.01, format="%.2f", key="r_top")
    with rc2:
        st.number_input("Bot", value=None, placeholder="-0.24", step=0.01, format="%.2f", key="r_bottom")
    with rc3:
        st.number_input("Left", value=None, placeholder="-0.10", step=0.01, format="%.2f", key="r_left")
    with rc4:
        st.number_input("Right", value=None, placeholder="-0.14", step=0.01, format="%.2f", key="r_right")

    st.markdown("<div style='font-size:12.5px; font-weight:700; margin-top:1px;'>2) ค่าแนวแกนแปลน (Axial - ใช้เกจ 2 ตัว G1, G2)</div>", unsafe_allow_html=True)
    h1, h2, h3, h4 = st.columns([0.85, 1.2, 1.2, 0.95])
    h1.markdown("<div style='font-size:11.5px; font-weight:700;'>Position</div>", unsafe_allow_html=True)
    h2.markdown("<div style='font-size:11.5px; font-weight:700;'>G1</div>", unsafe_allow_html=True)
    h3.markdown("<div style='font-size:11.5px; font-weight:700;'>G2</div>", unsafe_allow_html=True)
    h4.markdown("<div style='font-size:11.5px; font-weight:700;'>(G1-G2)/2</div>", unsafe_allow_html=True)

    def calc_half_diff(v1, v2):
        if v1 is not None and v2 is not None:
            return (v1 - v2) / 2.0
        return None

    # Top
    a1_1, a1_2, a1_3, a1_4 = st.columns([0.85, 1.2, 1.2, 0.95])
    a1_1.markdown("<div style='padding-top:4px; font-size:12.5px; font-weight:bold;'>Top</div>", unsafe_allow_html=True)
    a1_2.number_input("Top G1", value=None, placeholder="G1", label_visibility="collapsed", step=0.005, format="%.3f", key="g1_top")
    a1_3.number_input("Top G2", value=None, placeholder="G2", label_visibility="collapsed", step=0.005, format="%.3f", key="g2_top")
    raw_a_top = calc_half_diff(st.session_state.g1_top, st.session_state.g2_top)
    a1_4.markdown(f"<div class='calc-box'>{raw_a_top:.3f}</div>" if raw_a_top is not None else "<div class='calc-box-empty'>--</div>", unsafe_allow_html=True)

    # Left
    a2_1, a2_2, a2_3, a2_4 = st.columns([0.85, 1.2, 1.2, 0.95])
    a2_1.markdown("<div style='padding-top:4px; font-size:12.5px; font-weight:bold;'>Left</div>", unsafe_allow_html=True)
    a2_2.number_input("Left G1", value=None, placeholder="G1", label_visibility="collapsed", step=0.005, format="%.3f", key="g1_left")
    a2_3.number_input("Left G2", value=None, placeholder="G2", label_visibility="collapsed", step=0.005, format="%.3f", key="g2_left")
    raw_a_left = calc_half_diff(st.session_state.g1_left, st.session_state.g2_left)
    a2_4.markdown(f"<div class='calc-box'>{raw_a_left:.3f}</div>" if raw_a_left is not None else "<div class='calc-box-empty'>--</div>", unsafe_allow_html=True)

    # Bottom
    a3_1, a3_2, a3_3, a3_4 = st.columns([0.85, 1.2, 1.2, 0.95])
    a3_1.markdown("<div style='padding-top:4px; font-size:12.5px; font-weight:bold;'>Bottom</div>", unsafe_allow_html=True)
    a3_2.number_input("Bot G1", value=None, placeholder="G1", label_visibility="collapsed", step=0.005, format="%.3f", key="g1_bot")
    a3_3.number_input("Bot G2", value=None, placeholder="G2", label_visibility="collapsed", step=0.005, format="%.3f", key="g2_bot")
    raw_a_bottom = calc_half_diff(st.session_state.g1_bot, st.session_state.g2_bot)
    a3_4.markdown(f"<div class='calc-box'>{raw_a_bottom:.3f}</div>" if raw_a_bottom is not None else "<div class='calc-box-empty'>--</div>", unsafe_allow_html=True)

    # Right
    a4_1, a4_2, a4_3, a4_4 = st.columns([0.85, 1.2, 1.2, 0.95])
    a4_1.markdown("<div style='padding-top:4px; font-size:12.5px; font-weight:bold;'>Right</div>", unsafe_allow_html=True)
    a4_2.number_input("Right G1", value=None, placeholder="G1", label_visibility="collapsed", step=0.005, format="%.3f", key="g1_right")
    a4_3.number_input("Right G2", value=None, placeholder="G2", label_visibility="collapsed", step=0.005, format="%.3f", key="g2_right")
    raw_a_right = calc_half_diff(st.session_state.g1_right, st.session_state.g2_right)
    a4_4.markdown(f"<div class='calc-box'>{raw_a_right:.3f}</div>" if raw_a_right is not None else "<div class='calc-box-empty'>--</div>", unsafe_allow_html=True)


# =========================================================================
# Right Panel: แผนผัง & การคำนวณตามคู่มือ อ.สมเกียรติ สมหล่อ
# =========================================================================
with col_view:
    render_powerplant_schematic(lock_brg1)

    all_filled = all(st.session_state[k] is not None for k in input_keys)

    if not all_filled:
        missing_count = sum(1 for k in input_keys if st.session_state[k] is None)
        st.info(
            f"👈 **กรุณาป้อนตัวเลขจากใบงาน HP–IP Coupling ทางด้านซ้ายให้ครบ** (หรือกดปุ่ม **'📋 โหลดค่าตัวอย่าง'**)\n\n"
            f"สถานะการป้อนข้อมูลปัจจุบัน: กรอกแล้ว **{len(input_keys) - missing_count} / {len(input_keys)}** ช่อง"
        )
        st.stop()

    if st.session_state.d_coupling <= 0 or st.session_state.l_brg1 <= st.session_state.l_brg2:
        st.error("❌ ค่าขนาดแปลน D ต้องมากกว่า 0 และระยะถึง Brg.1 ต้องมากกว่าระยะถึง Brg.2")
        st.stop()

    d_coupling = float(st.session_state.d_coupling)
    l_brg2 = float(st.session_state.l_brg2)
    l_brg1 = float(st.session_state.l_brg1)
    span_b1_b2 = l_brg1 - l_brg2

    r_top = float(st.session_state.r_top)
    r_bottom = float(st.session_state.r_bottom)
    r_left = float(st.session_state.r_left)
    r_right = float(st.session_state.r_right)

    # ขั้นตอนที่ 1: ตรวจสอบความถูกต้อง (T + B = L + R)
    sum_r_tb = r_top + r_bottom
    sum_r_lr = r_left + r_right
    diff_r_mm = abs(sum_r_tb - sum_r_lr)
    valid_r = diff_r_mm <= TOLERANCE_CHECK_MM

    sum_a_tb = raw_a_top + raw_a_bottom
    sum_a_lr = raw_a_left + raw_a_right
    diff_a_mm = abs(sum_a_tb - sum_a_lr)
    valid_a = diff_a_mm <= TOLERANCE_CHECK_MM

    # ขั้นตอนที่ 2: เปลี่ยนค่า T.I.R. เทียบศูนย์ (0) โดยล็อก Top = 0.00 ในแนว Radial
    z_r_top, z_r_bot, z_r_left, z_r_right, add_r_tb, add_r_lr = convert_tir_to_zero_diff(
        r_top, r_bottom, r_left, r_right, lock_top_zero=True
    )
    z_a_top, z_a_bot, z_a_left, z_a_right, add_a_tb, add_a_lr = convert_tir_to_zero_diff(
        raw_a_top, raw_a_bottom, raw_a_left, raw_a_right, lock_top_zero=False
    )

    # ขั้นตอนที่ 3: วิเคราะห์ตำแหน่งเพลา HP เทียบกับ IP (FIXED)
    delta_ax_tb = raw_a_bottom - raw_a_top
    delta_ax_lr = raw_a_left - raw_a_right

    hp_below_ip_mm = (r_top - r_bottom) / 2.0
    hp_left_of_ip_mm = (r_left - r_right) / 2.0

    # ขั้นตอนที่ 4: คำนวณระยะปรับ (Axial ก่อน แล้วรวม Radial)
    if not lock_brg1:
        ax_v_b2 = (delta_ax_tb * l_brg2) / d_coupling
        ax_v_b1 = (delta_ax_tb * l_brg1) / d_coupling
        rad_v_b2 = hp_below_ip_mm
        rad_v_b1 = hp_below_ip_mm

        total_v_b2 = ax_v_b2 + rad_v_b2
        total_v_b1 = ax_v_b1 + rad_v_b1

        ax_h_b2 = (delta_ax_lr * l_brg2) / d_coupling
        ax_h_b1 = (delta_ax_lr * l_brg1) / d_coupling
        rad_h_b2 = -hp_left_of_ip_mm
        rad_h_b1 = -hp_left_of_ip_mm

        total_h_b2 = ax_h_b2 + rad_h_b2
        total_h_b1 = ax_h_b1 + rad_h_b1
    else:
        ax_v_b1, rad_v_b1, total_v_b1 = 0.0, 0.0, 0.0
        ax_h_b1, rad_h_b1, total_h_b1 = 0.0, 0.0, 0.0

        ax_v_b2 = (delta_ax_tb * span_b1_b2) / d_coupling
        rad_v_b2 = hp_below_ip_mm * (span_b1_b2 / l_brg1)
        total_v_b2 = ax_v_b2 + rad_v_b2

        ax_h_b2 = (delta_ax_lr * span_b1_b2) / d_coupling
        rad_h_b2 = (-hp_left_of_ip_mm) * (span_b1_b2 / l_brg1)
        total_h_b2 = ax_h_b2 + rad_h_b2

    if not valid_r:
        st.warning(f"⚠️ **คำเตือนการตรวจสอบค่า:** ค่า Radial $(T+B) = {sum_r_tb:+.2f}$ ต่างจาก $(L+R) = {sum_r_lr:+.2f}$ อยู่ **{diff_r_mm:.2f} mm** (เกิน 0.03 mm)")
    if not valid_a:
        st.warning(f"⚠️ **คำเตือนการตรวจสอบค่า:** ค่า Axial $(T+B) = {sum_a_tb:+.3f}$ ต่างจาก $(L+R) = {sum_a_lr:+.3f}$ อยู่ **{diff_a_mm:.3f} mm** (เกิน 0.03 mm)")

    # =====================================================================
    # การ์ดใบสั่งงานปรับ Shim ที่ Bearing แบบ 4 จุด
    # =====================================================================
    st.markdown('<div class="section-title-compact">🛠️ ใบสั่งงานปรับ Shim ที่ Bearing (หลักการปรับ Bearing 4 จุด)</div>', unsafe_allow_html=True)

    def render_tech_card(col, brg_title, subtitle_txt, v_mm, h_mm, is_fixed, lock_reason=""):
        with col:
            if is_fixed:
                card_html = (
                    f'<div class="tech-card tech-card-fixed">'
                    f'<div>'
                    f'<div class="brg-name">🔒 {brg_title}</div>'
                    f'<div class="brg-arm">{subtitle_txt}</div>'
                    f'</div>'
                    f'<div class="action-row-lock">'
                    f'ยึดแน่นคงที่ (FIXED)<br>'
                    f'<span style="font-size:11.5px; font-weight:normal; margin-top:4px;">{lock_reason}</span>'
                    f'</div>'
                    f'</div>'
                )
                st.markdown(card_html, unsafe_allow_html=True)
            else:
                v_class = "action-row" if v_mm >= 0 else "action-row-down"
                v_icon = "⬆️" if v_mm >= 0 else "⬇️"
                if v_mm >= 0:
                    v_dir = f"ปรับ Bearing ขึ้นบน (T) = {v_mm:.3f} mm"
                    v_shim_rule = f"เอา Shim บน (T) ออก {v_mm:.3f} → ใส่ล่าง (B) +{v_mm:.3f} mm"
                else:
                    v_dir = f"ปรับ Bearing ลงล่าง (B) = {abs(v_mm):.3f} mm"
                    v_shim_rule = f"เอา Shim ล่าง (B) ออก {abs(v_mm):.3f} → ใส่บน (T) +{abs(v_mm):.3f} mm"
                v_khid = f"{abs(v_mm)*100:.1f} ขีด"

                h_icon = "⬅️" if h_mm >= 0 else "➡️"
                if h_mm >= 0:
                    h_dir = f"ปรับ Bearing ไปซ้าย (L) = {h_mm:.3f} mm"
                    h_shim_rule = f"เอา Shim ซ้าย (L) ออก {h_mm:.3f} → ใส่ขวา (R) +{h_mm:.3f} mm"
                else:
                    h_dir = f"ปรับ Bearing ไปขวา (R) = {abs(h_mm):.3f} mm"
                    h_shim_rule = f"เอา Shim ขวา (R) ออก {abs(h_mm):.3f} → ใส่ซ้าย (L) +{abs(h_mm):.3f} mm"
                h_khid = f"{abs(h_mm)*100:.1f} ขีด"

                card_html = (
                    f'<div class="tech-card tech-card-adjust">'
                    f'<div>'
                    f'<div class="brg-name">🔧 {brg_title}</div>'
                    f'<div class="brg-arm">{subtitle_txt}</div>'
                    f'</div>'
                    f'<div>'
                    f'<div class="{v_class}">'
                    f'<div class="action-label">{v_icon} แนวดิ่ง (T &amp; B)</div>'
                    f'<div class="action-val">{v_dir}</div>'
                    f'<div class="shim-detail">📌 {v_shim_rule}</div>'
                    f'<span class="khid-tag">≈ {v_khid} (1 ขีด = 0.01 mm)</span>'
                    f'</div>'
                    f'<div class="action-row-horiz">'
                    f'<div class="action-label">{h_icon} แนวนอน (L &amp; R)</div>'
                    f'<div class="action-val">{h_dir}</div>'
                    f'<div class="shim-detail">📌 {h_shim_rule}</div>'
                    f'<span class="khid-tag">≈ {h_khid} (1 ขีด = 0.01 mm)</span>'
                    f'</div>'
                    f'</div>'
                    f'</div>'
                )
                st.markdown(card_html, unsafe_allow_html=True)

    card_c1, card_c2, card_c3 = st.columns(3, gap="small")
    render_tech_card(
        card_c1, "HP Bearing 1 (ไกล)", f"ระยะแขน L = {l_brg1:,.0f} mm",
        total_v_b1, total_h_b1, is_fixed=lock_brg1, lock_reason="ล็อกเป็นจุดหมุน"
    )
    render_tech_card(
        card_c2, "HP Bearing 2 (ใกล้)", f"ระยะแขน L = {l_brg2:,.0f} mm",
        total_v_b2, total_h_b2, is_fixed=False
    )
    render_tech_card(
        card_c3, "IP Bearing 3 (เพลาหลัก)", "ชุดเพลา IP-LP-Gen (Aligned แล้ว)",
        0.0, 0.0, is_fixed=True, lock_reason="เพลาหลักคงที่ไม่มีการปรับ"
    )

    # =====================================================================
    # แท็บแสดงรายละเอียดตามคู่มือทั้ง 4 แท็บ
    # =====================================================================
    tab1, tab2, tab3, tab4 = st.tabs([
        "📐 รูปเขียนประกอบค่า Alignment",
        "📋 แปลงค่า TIR เทียบศูนย์ 0",
        "🔍 จุดติดตั้ง Dial Gauge",
        "📝 ลำดับคำนวณ & สามเหลี่ยมคล้าย"
    ])

    with tab1:
        fig2 = plt.figure(figsize=(12, 13.5), dpi=130)
        gs = fig2.add_gridspec(3, 1, height_ratios=[1.25, 1.25, 0.85], hspace=0.28)
        ax_side = fig2.add_subplot(gs[0])
        ax_top = fig2.add_subplot(gs[1])
        ax_bar = fig2.add_subplot(gs[2])

        hp_act_v_list = [
            (f"Brg.2 ({l_brg2:.0f})", f"T={total_v_b2:+.3f}" if total_v_b2 >= 0 else f"B={abs(total_v_b2):.3f}"),
            (f"Brg.1 ({l_brg1:.0f})", "FIXED (Pivot)" if lock_brg1 else (f"T={total_v_b1:+.3f}" if total_v_b1 >= 0 else f"B={abs(total_v_b1):.3f}")),
        ]
        note_tb_box = (
            f"• Axial Gap (T-B) = {abs(delta_ax_tb):.3f} mm | Radial (TIR/2) = {abs(hp_below_ip_mm):.3f} mm\n"
            f"• Vector Brg.1 = {total_v_b1:+.3f} mm | Vector Brg.2 = {total_v_b2:+.3f} mm | IP = FIXED"
        )
        draw_manual_book_diagram(
            ax_side,
            title="1. SIDE VIEW (T - B) | IP = FIXED Reference",
            pos_lbl="T", neg_lbl="B",
            ax_gap_mm=delta_ax_tb, open_at_neg=(delta_ax_tb >= 0),
            hp_above_pos_mm=-hp_below_ip_mm,
            lock_brg1=lock_brg1, hp_action_list=hp_act_v_list, sub_note=note_tb_box
        )

        hp_act_h_list = [
            (f"Brg.2 ({l_brg2:.0f})", f"L={total_h_b2:+.3f}" if total_h_b2 >= 0 else f"R={abs(total_h_b2):.3f}"),
            (f"Brg.1 ({l_brg1:.0f})", "FIXED (Pivot)" if lock_brg1 else (f"L={total_h_b1:+.3f}" if total_h_b1 >= 0 else f"R={abs(total_h_b1):.3f}")),
        ]
        note_lr_box = (
            f"• Axial Gap (L-R) = {abs(delta_ax_lr):.3f} mm | Radial (TIR/2) = {abs(hp_left_of_ip_mm):.3f} mm\n"
            f"• Vector Brg.1 = {total_h_b1:+.3f} mm | Vector Brg.2 = {total_h_b2:+.3f} mm | IP = FIXED"
        )
        draw_manual_book_diagram(
            ax_top,
            title="2. TOP VIEW (L - R) | IP = FIXED Reference",
            pos_lbl="L", neg_lbl="R",
            ax_gap_mm=delta_ax_lr, open_at_neg=(delta_ax_lr < 0),
            hp_above_pos_mm=hp_left_of_ip_mm,
            lock_brg1=lock_brg1, hp_action_list=hp_act_h_list, sub_note=note_lr_box
        )

        labels = [f"HP Bearing 1 ({l_brg1:.0f})", f"HP Bearing 2 ({l_brg2:.0f})", "IP Bearing 3 (FIXED)"]
        shims = [total_v_b1, total_v_b2, 0.0]
        colors = ['#2E7D32' if s > 0 else ('#C62828' if s < 0 else '#9E9E9E') for s in shims]

        bars = ax_bar.bar(labels, shims, color=colors, width=0.35, edgecolor='black', zorder=3)
        ax_bar.axhline(0, color='black', linewidth=1.2)
        ax_bar.set_ylabel("Vertical Adjustment (mm)", fontsize=10, fontweight='bold')
        ax_bar.set_title("3. Summary of Vertical Bearing Adjustment (T = +, B = -)", fontsize=11.5, fontweight='bold', pad=10)
        ax_bar.grid(axis='y', linestyle=':', alpha=0.6)

        max_val = max(abs(s) for s in shims) if any(abs(s) > 0 for s in shims) else 0.05
        ax_bar.set_ylim(-max_val * 1.55 - 0.05, max_val * 1.55 + 0.05)

        for bar, s_val in zip(bars, shims):
            h = bar.get_height()
            va_align = 'bottom' if h >= 0 else 'top'
            y_pos = h + (0.015 if h >= 0 else -0.015)
            action_word = "MOVE UP (T)" if s_val > 0 else ("MOVE DOWN (B)" if s_val < 0 else "FIXED")
            ax_bar.text(bar.get_x() + bar.get_width() / 2., y_pos, f"{s_val:+.3f} mm\n({action_word})",
                        ha='center', va=va_align, fontsize=9.5, fontweight='bold')

        st.pyplot(fig2)

    with tab2:
        st.subheader("📋 การเปลี่ยนค่า T.I.R. ให้เป็นค่าแสดงความแตกต่างเทียบศูนย์ (0)")
        st.caption("แถวบน = ค่าดิบ (T.I.R.) | แถวล่าง = ค่าเทียบศูนย์ (Radial ล็อก Top = 0.00 และปรับฝั่งน้อยแกนซ้าย–ขวาเป็น 0.00)")

        fig1 = plt.figure(figsize=(15, 11.2))

        ax1 = fig1.add_subplot(2, 2, 1)
        draw_dial_crosshair(
            ax1, "[1] Raw Axial Input (G1 - G2) / 2", "A",
            raw_a_top, raw_a_bottom, raw_a_left, raw_a_right, '#C62828',
            f"Check: T+B={sum_a_tb:+.3f} | L+R={sum_a_lr:+.3f}",
            f"Diff = {diff_a_mm:.3f} mm ({'PASS' if valid_a else 'CHECK'})", is_radial=False
        )

        ax2 = fig1.add_subplot(2, 2, 2)
        draw_dial_crosshair(
            ax2, "[2] Raw Radial Input (T.I.R.)", "R",
            r_top, r_bottom, r_left, r_right, '#C62828',
            f"Check: T+B={sum_r_tb:+.2f} | L+R={sum_r_lr:+.2f}",
            f"Diff = {diff_r_mm:.2f} mm ({'PASS' if valid_r else 'CHECK'})", is_radial=True
        )

        ax3 = fig1.add_subplot(2, 2, 3)
        draw_dial_crosshair(
            ax3, "[3] Zero-Referenced Axial", "A",
            z_a_top, z_a_bot, z_a_left, z_a_right, '#1565C0',
            f"Add TB: ({add_a_tb:+.3f}) | Add LR: ({add_a_lr:+.3f})",
            f"V-Open = {abs(delta_ax_tb):.3f} mm | H-Open = {abs(delta_ax_lr):.3f} mm", is_radial=False
        )

        ax4 = fig1.add_subplot(2, 2, 4)
        draw_dial_crosshair(
            ax4, "[4] Zero-Referenced Radial (Top = 0.00)", "R",
            z_r_top, z_r_bot, z_r_left, z_r_right, '#1565C0',
            f"Add TB: ({add_r_tb:+.2f}) | Add LR: ({add_r_lr:+.2f})",
            f"V-TIR = {abs(r_top-r_bottom):.2f} mm | H-TIR = {abs(r_left-r_right):.2f} mm", is_radial=True
        )

        plt.subplots_adjust(top=0.94, bottom=0.06, hspace=0.38, wspace=0.25)
        st.pyplot(fig1)

    with tab3:
        st.subheader("🔍 รูปแสดงการยึดและจี้ Dial Gauge ระหว่างเพลา HP และ IP")
        fig3 = plt.figure(figsize=(14, 6.2))
        ax_setup = fig3.add_subplot(1, 1, 1)
        draw_coupling_physical_setup(ax_setup)
        st.pyplot(fig3)

    with tab4:
        st.subheader("📝 ลำดับขั้นในการคำนวณหาค่าที่จะต้องปรับ")

        with st.expander("🔹 ขั้นตอนที่ 1: ตรวจสอบความถูกต้องของค่าที่อ่านได้ (T + B = L + R)", expanded=True):
            c_v1, c_v2 = st.columns(2)
            with c_v1:
                st.markdown("**1.1 แนว RADIAL (หน่วย: mm):**")
                st.latex(rf"T + B = ({r_top:+.2f}) + ({r_bottom:+.2f}) = {sum_r_tb:+.2f}\text{{ mm}}")
                st.latex(rf"L + R = ({r_left:+.2f}) + ({r_right:+.2f}) = {sum_r_lr:+.2f}\text{{ mm}}")
                st.write(f"ผลต่าง $= {diff_r_mm:.2f}$ mm ({'✅ ถูกต้อง (คลาดเคลื่อนไม่เกิน 0.03 mm)' if valid_r else '❌ คลาดเคลื่อนเกินเกณฑ์มาตรฐาน'})")
            with c_v2:
                st.markdown("**1.2 แนว AXIAL (หน่วย: mm):**")
                st.latex(rf"T + B = ({raw_a_top:+.3f}) + ({raw_a_bottom:+.3f}) = {sum_a_tb:+.3f}\text{{ mm}}")
                st.latex(rf"L + R = ({raw_a_left:+.3f}) + ({raw_a_right:+.3f}) = {sum_a_lr:+.3f}\text{{ mm}}")
                st.write(f"ผลต่าง $= {diff_a_mm:.3f}$ mm ({'✅ ถูกต้อง' if valid_a else '❌ คลาดเคลื่อนเกินเกณฑ์'})")

        with st.expander("🔹 ขั้นตอนที่ 2: เปลี่ยนค่า T.I.R. เป็นค่าแสดงความแตกต่างเทียบศูนย์ (0)", expanded=True):
            col_z1, col_z2 = st.columns(2)
            with col_z1:
                st.markdown("**2.1 แนว RADIAL:**")
                st.write(f"- แกนบน–ล่าง: นำ $({add_r_tb:+.2f})$ บวกเข้าทั้งบนและล่าง $\\implies T = {z_r_top:.2f}, B = {z_r_bot:+.2f}$")
                st.write(f"- แกนซ้าย–ขวา: นำ $({add_r_lr:+.2f})$ บวกเข้าทั้งซ้ายและขวา $\\implies L = {z_r_left:+.2f}, R = {z_r_right:+.2f}$")
                st.latex(rf"\text{{ตำแหน่งจริงแนวดิ่ง (หาร 2): }} \frac{{T - B}}{{2}} = \frac{{({r_top:+.2f}) - ({r_bottom:+.2f})}}{{2}} = {hp_below_ip_mm:+.3f}\text{{ mm}}")
                st.latex(rf"\text{{ตำแหน่งจริงแนวนอน (หาร 2): }} \frac{{L - R}}{{2}} = \frac{{({r_left:+.2f}) - ({r_right:+.2f})}}{{2}} = {hp_left_of_ip_mm:+.3f}\text{{ mm}}")
            with col_z2:
                st.markdown("**2.2 แนว AXIAL:**")
                st.write(f"- แกนบน–ล่าง: นำ $({add_a_tb:+.3f})$ บวกเข้าทั้งบนและล่าง $\\implies T = {z_a_top:.3f}, B = {z_a_bot:+.3f}$")
                st.write(f"- แกนซ้าย–ขวา: นำ $({add_a_lr:+.3f})$ บวกเข้าทั้งซ้ายและขวา $\\implies L = {z_a_left:.3f}, R = {z_a_right:+.3f}$")
                st.latex(rf"\text{{ผลต่างแนวแกนบน–ล่าง: }} \Delta X_{{TB}} = B - T = {delta_ax_tb:+.3f}\text{{ mm}}")
                st.latex(rf"\text{{ผลต่างแนวแกนซ้าย–ขวา: }} \Delta X_{{LR}} = L - R = {delta_ax_lr:+.3f}\text{{ mm}}")

        with st.expander("🔹 ขั้นตอนที่ 3: ลำดับขั้นในการคำนวณหาค่าที่จะต้องปรับ (Axial ก่อน แล้วรวม Radial)", expanded=True):
            st.markdown("ใช้ทฤษฎีบทที่ 62 (สามเหลี่ยมคล้าย): $\\frac{QR}{PR} = \\frac{BC}{AC} = \\frac{DE}{AE}$")
            col_s1, col_s2 = st.columns(2)
            with col_s1:
                st.markdown("### 1) แนวบนและล่าง (T & B)")
                if not lock_brg1:
                    st.latex(rf"\text{{Brg.2}}_{{\text{{Axial}}}} = \frac{{({delta_ax_tb:+.3f}) \times {l_brg2:.0f}}}{{{d_coupling:.0f}}} = {ax_v_b2:+.3f}\text{{ mm}}")
                    st.latex(rf"\text{{Brg.1}}_{{\text{{Axial}}}} = \frac{{({delta_ax_tb:+.3f}) \times {l_brg1:.0f}}}{{{d_coupling:.0f}}} = {ax_v_b1:+.3f}\text{{ mm}}")
                    st.latex(rf"\text{{Brg.2}}_{{\text{{รวม}}}} = ({ax_v_b2:+.3f}) + ({rad_v_b2:+.3f}) = \mathbf{{{total_v_b2:+.3f}\text{{ mm}}}}")
                    st.latex(rf"\text{{Brg.1}}_{{\text{{รวม}}}} = ({ax_v_b1:+.3f}) + ({rad_v_b1:+.3f}) = \mathbf{{{total_v_b1:+.3f}\text{{ mm}}}}")
                else:
                    st.latex(rf"\text{{Brg.1}} = \mathbf{{0.000\text{{ mm}}}} \text{{ (ล็อกเป็นจุดหมุน ระยะห่างถึง Brg.2}} = {span_b1_b2:.0f}\text{{ mm)}}")
                    st.latex(rf"\text{{Brg.2}}_{{\text{{Axial}}}} = \frac{{({delta_ax_tb:+.3f}) \times {span_b1_b2:.0f}}}{{{d_coupling:.0f}}} = {ax_v_b2:+.3f}\text{{ mm}}")
                    st.latex(rf"\text{{Brg.2}}_{{\text{{Radial}}}} = ({hp_below_ip_mm:+.3f}) \times \frac{{{span_b1_b2:.0f}}}{{{l_brg1:.0f}}} = {rad_v_b2:+.3f}\text{{ mm}}")
                    st.latex(rf"\text{{Brg.2}}_{{\text{{รวม}}}} = ({ax_v_b2:+.3f}) + ({rad_v_b2:+.3f}) = \mathbf{{{total_v_b2:+.3f}\text{{ mm}}}}")

            with col_s2:
                st.markdown("### 2) แนวซ้ายและขวา (L & R)")
                if not lock_brg1:
                    st.latex(rf"\text{{Brg.2}}_{{\text{{Axial}}}} = \frac{{({delta_ax_lr:+.3f}) \times {l_brg2:.0f}}}{{{d_coupling:.0f}}} = {ax_h_b2:+.3f}\text{{ mm}}")
                    st.latex(rf"\text{{Brg.1}}_{{\text{{Axial}}}} = \frac{{({delta_ax_lr:+.3f}) \times {l_brg1:.0f}}}{{{d_coupling:.0f}}} = {ax_h_b1:+.3f}\text{{ mm}}")
                    st.latex(rf"\text{{Brg.2}}_{{\text{{รวม}}}} = ({ax_h_b2:+.3f}) + ({rad_h_b2:+.3f}) = \mathbf{{{total_h_b2:+.3f}\text{{ mm}}}}")
                    st.latex(rf"\text{{Brg.1}}_{{\text{{รวม}}}} = ({ax_h_b1:+.3f}) + ({rad_h_b1:+.3f}) = \mathbf{{{total_h_b1:+.3f}\text{{ mm}}}}")
                else:
                    st.latex(rf"\text{{Brg.1}} = \mathbf{{0.000\text{{ mm}}}} \text{{ (ล็อกเป็นจุดหมุน)}}")
                    st.latex(rf"\text{{Brg.2}}_{{\text{{Axial}}}} = \frac{{({delta_ax_lr:+.3f}) \times {span_b1_b2:.0f}}}{{{d_coupling:.0f}}} = {ax_h_b2:+.3f}\text{{ mm}}")
                    st.latex(rf"\text{{Brg.2}}_{{\text{{Radial}}}} = ({-hp_left_of_ip_mm:+.3f}) \times \frac{{{span_b1_b2:.0f}}}{{{l_brg1:.0f}}} = {rad_h_b2:+.3f}\text{{ mm}}")
                    st.latex(rf"\text{{Brg.2}}_{{\text{{รวม}}}} = ({ax_h_b2:+.3f}) + ({rad_h_b2:+.3f}) = \mathbf{{{total_h_b2:+.3f}\text{{ mm}}}}")

        with st.expander("🔹 ขั้นตอนที่ 4: สรุป Vector และวิธีการปรับ Shim ที่ Bearing 4 จุด", expanded=True):
            st.markdown("หลักการปรับ: *\"ให้เอา Shim ด้านที่เราต้องการจะปรับออกไป เท่ากับจำนวนที่คำนวณมาได้แล้วนำมาใส่ยังด้านตรงข้าม\"*")
            v_col1, v_col2 = st.columns(2)
            with v_col1:
                st.markdown(f"**Vector Brg.2 (ระยะ {l_brg2:.0f} mm):**")
                st.write(f"- แนวดิ่ง: **{'T' if total_v_b2 >= 0 else 'B'} = {abs(total_v_b2)*100:.1f} ขีด ({abs(total_v_b2):.3f} mm)**")
                st.write(f"- แนวนอน: **{'L' if total_h_b2 >= 0 else 'R'} = {abs(total_h_b2)*100:.1f} ขีด ({abs(total_h_b2):.3f} mm)**")
            with v_col2:
                st.markdown(f"**Vector Brg.1 (ระยะ {l_brg1:.0f} mm):**")
                if lock_brg1:
                    st.write("- **FIXED (0.000 mm) — ล็อกเป็นจุดหมุน**")
                else:
                    st.write(f"- แนวดิ่ง: **{'T' if total_v_b1 >= 0 else 'B'} = {abs(total_v_b1)*100:.1f} ขีด ({abs(total_v_b1):.3f} mm)**")
                    st.write(f"- แนวนอน: **{'L' if total_h_b1 >= 0 else 'R'} = {abs(total_h_b1)*100:.1f} ขีด ({abs(total_h_b1):.3f} mm)**")
