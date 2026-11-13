"""
Streamlit Web Application: LP-Generator Coupling Alignment Precision Tool
Standard: EGAT Mae Moh Power Plant Unit 8-13 (หปกร-ธ.)
Reference: Alignment & Eccentricity Manual (นายสมเกียรติ สมหล่อ - กฟผ.)
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
import streamlit as st

# ตั้งค่าระบบแสดงผล
st.set_page_config(
    page_title="EGAT Mae Moh 8-13 | LP-Gen Alignment Control",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ตั้งค่าฟอนต์มาตรฐานสากลสำหรับ Matplotlib
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial', 'Helvetica']
plt.rcParams['axes.unicode_minus'] = False

# =========================================================================
# Industrial Power Plant CSS Styling
# =========================================================================
st.markdown("""
<style>
    .stApp {
        background-color: #F0F4F8;
    }
    .pp-header {
        background: linear-gradient(135deg, #0B192C 0%, #1E3E62 65%, #0F2C59 100%);
        padding: 18px 26px;
        border-radius: 12px;
        color: #FFFFFF;
        margin-bottom: 18px;
        border-bottom: 5px solid #FFB000;
        box-shadow: 0 6px 16px rgba(11, 25, 44, 0.22);
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .pp-header-title {
        font-size: 24px;
        font-weight: 800;
        color: #FFFFFF;
        margin: 0;
        letter-spacing: 0.4px;
    }
    .pp-header-sub {
        font-size: 13.5px;
        color: #FFD54F;
        margin: 4px 0 0 0;
        font-weight: 600;
    }
    .pp-badge {
        background-color: #FFB000;
        color: #0B192C;
        padding: 6px 14px;
        border-radius: 20px;
        font-weight: 800;
        font-size: 13px;
        box-shadow: 0 2px 6px rgba(0,0,0,0.2);
    }
    .sheet-title {
        background: linear-gradient(90deg, #1E3E62 0%, #2B547E 100%);
        color: #FFFFFF;
        padding: 9px 12px;
        text-align: center;
        font-weight: 700;
        font-size: 15px;
        border-radius: 8px 8px 0 0;
        margin-top: 8px;
    }
    .calc-box {
        background-color: #E8F5E9;
        border: 1.5px solid #4CAF50;
        border-radius: 6px;
        padding: 6px 4px;
        text-align: center;
        font-weight: 800;
        color: #1B5E20;
        font-size: 14px;
        margin-top: 2px;
    }
    .calc-box-empty {
        background-color: #ECEFF1;
        border: 1px dashed #B0BEC5;
        border-radius: 6px;
        padding: 6px 4px;
        text-align: center;
        color: #90A4AE;
        font-size: 14px;
        margin-top: 2px;
    }
    .tech-card {
        background-color: #FFFFFF;
        border-radius: 12px;
        padding: 16px 18px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.07);
        border-top: 6px solid #1565C0;
        height: 100%;
    }
    .tech-card-fixed {
        border-top: 6px solid #546E7A;
        background-color: #F8FAFC;
    }
    .tech-card-adjust {
        border-top: 6px solid #FF6F00;
    }
    .brg-name {
        font-size: 18px;
        font-weight: 800;
        color: #0B192C;
        margin-bottom: 2px;
    }
    .brg-arm {
        font-size: 12.5px;
        color: #607D8B;
        font-weight: 600;
        margin-bottom: 12px;
        border-bottom: 1px solid #ECEFF1;
        padding-bottom: 6px;
    }
    .action-row {
        background-color: #F1F8E9;
        border-left: 4px solid #2E7D32;
        padding: 8px 10px;
        border-radius: 6px;
        margin-bottom: 8px;
    }
    .action-row-down {
        background-color: #FFEBEE;
        border-left: 4px solid #C62828;
        padding: 8px 10px;
        border-radius: 6px;
        margin-bottom: 8px;
    }
    .action-row-horiz {
        background-color: #E3F2FD;
        border-left: 4px solid #1565C0;
        padding: 8px 10px;
        border-radius: 6px;
        margin-bottom: 8px;
    }
    .action-row-lock {
        background-color: #ECEFF1;
        border-left: 4px solid #607D8B;
        padding: 14px 10px;
        border-radius: 6px;
        text-align: center;
        font-weight: 700;
        color: #455A64;
        margin-top: 10px;
    }
    .action-label {
        font-size: 12px;
        color: #455A64;
        font-weight: 700;
    }
    .action-val {
        font-size: 15.5px;
        font-weight: 800;
        color: #102027;
        margin-top: 2px;
    }
    .khid-tag {
        display: inline-block;
        background-color: #263238;
        color: #FFD54F;
        font-size: 12px;
        font-weight: 700;
        padding: 2px 8px;
        border-radius: 10px;
        margin-top: 4px;
    }
</style>
""", unsafe_allow_html=True)

# ค่าควบคุมมาตรฐาน กฟผ. แม่เมาะ (จับฐานเกจที่ Gen จี้ LP)
TARGET_GEN_DOWN_MM = 0.100        # Generator down 0.100 mm (Gen ต่ำกว่า LP 0.100 mm)
TARGET_AXIAL_GAP_MM = 0.000       # Target Face Gap (mm)
TOLERANCE_RADIAL_MM = 0.030       # เกณฑ์ความคลาดเคลื่อนผลต่าง Radial ไม่เกิน 0.03 mm (3 ขีด)

# =========================================================================
# Session State Initialization
# =========================================================================
input_keys = [
    'd_coupling', 'l_brg4', 'l_brg5', 'l_brg6',
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
# Zero-Reference Conversion (ตามหนังสือ: ทำให้ด้านที่น้อยกว่าเป็น 0 ทั้งสองแกน)
# =========================================================================
def convert_tir_to_zero_ref(t_val: float, b_val: float, l_val: float, r_val: float):
    min_tb = min(t_val, b_val)
    off_tb = -min_tb
    z_t = t_val + off_tb
    z_b = b_val + off_tb

    min_lr = min(l_val, r_val)
    off_lr = -min_lr
    z_l = l_val + off_lr
    z_r = r_val + off_lr

    return z_t, z_b, z_l, z_r, off_tb, off_lr


# =========================================================================
# Power Plant Turbine-Generator Schematic (SVG Banner)
# =========================================================================
def render_powerplant_schematic(choice_val: str):
    lp_fill = "#1565C0" if choice_val == '3' else "#E65100"
    lp_badge = "🔒 LOCKED (100%)" if choice_val == '3' else ("🔧 ปรับแก้ 100%" if choice_val == '1' else "🔧 ปรับร่วม 50%")

    gen_fill = "#1565C0" if choice_val == '1' else "#E65100"
    gen_badge = "🔒 LOCKED (100%)" if choice_val == '1' else ("🔧 ปรับแก้ 100%" if choice_val == '3' else "🔧 ปรับร่วม 50%")

    b4_col = "#546E7A" if choice_val == '3' else "#FF6F00"
    b56_col = "#546E7A" if choice_val == '1' else "#FF6F00"

    svg_html = (
        f'<div style="background:#FFFFFF; border-radius:12px; padding:14px 18px; border:1px solid #CFD8DC; box-shadow:0 3px 10px rgba(0,0,0,0.05); margin-bottom:14px;">'
        f'<div style="font-size:14px; font-weight:800; color:#1E3E62; margin-bottom:8px; display:flex; justify-content:space-between; flex-wrap:wrap;">'
        f'<span>🏭 แผนผังชุดเพลา LP TURBINE – GENERATOR (EGAT MAE MOH UNIT 8-13)</span>'
        f'<span style="color:#D84315;">เป้าหมาย: Generator ต่ำกว่า LP = 0.100 mm (10 ขีด)</span>'
        f'</div>'
        f'<svg viewBox="0 0 960 215" width="100%" height="auto" xmlns="http://www.w3.org/2000/svg">'
        f'<rect x="20" y="176" width="920" height="26" rx="5" fill="#263238" />'
        f'<text x="480" y="193" fill="#FFFFFF" font-size="12" font-weight="bold" text-anchor="middle" letter-spacing="0.5">TURBINE-GENERATOR CONCRETE PEDESTAL (แท่นฐานราก)</text>'
        f'<rect x="70" y="106" width="820" height="16" fill="#90A4AE" stroke="#37474F" stroke-width="1.5"/>'
        f'<polygon points="145,66 330,46 330,174 145,154" fill="{lp_fill}" fill-opacity="0.14" stroke="{lp_fill}" stroke-width="3"/>'
        f'<line x1="182" y1="62" x2="182" y2="158" stroke="{lp_fill}" stroke-width="2.8"/>'
        f'<line x1="220" y1="58" x2="220" y2="162" stroke="{lp_fill}" stroke-width="2.8"/>'
        f'<line x1="258" y1="54" x2="258" y2="166" stroke="{lp_fill}" stroke-width="2.8"/>'
        f'<line x1="296" y1="50" x2="296" y2="170" stroke="{lp_fill}" stroke-width="2.8"/>'
        f'<rect x="132" y="8" width="210" height="26" rx="13" fill="{lp_fill}"/>'
        f'<text x="237" y="25" fill="#FFFFFF" font-size="12" font-weight="bold" text-anchor="middle">LP TURBINE | {lp_badge}</text>'
        f'<rect x="423" y="82" width="11" height="64" rx="2" fill="#263238"/>'
        f'<rect x="438" y="82" width="11" height="64" rx="2" fill="#263238"/>'
        f'<line x1="436" y1="68" x2="436" y2="168" stroke="#D32F2F" stroke-width="2" stroke-dasharray="4,3"/>'
        f'<rect x="376" y="48" width="120" height="22" rx="6" fill="#D32F2F"/>'
        f'<text x="436" y="63" fill="#FFFFFF" font-size="11.5" font-weight="bold" text-anchor="middle">COUPLING (จุดวัด)</text>'
        f'<rect x="555" y="50" width="245" height="122" rx="10" fill="{gen_fill}" fill-opacity="0.14" stroke="{gen_fill}" stroke-width="3"/>'
        f'<line x1="590" y1="50" x2="590" y2="172" stroke="{gen_fill}" stroke-width="1.5" stroke-dasharray="4,3"/>'
        f'<line x1="765" y1="50" x2="765" y2="172" stroke="{gen_fill}" stroke-width="1.5" stroke-dasharray="4,3"/>'
        f'<text x="677" y="84" fill="{gen_fill}" font-size="16" font-weight="bold" text-anchor="middle" letter-spacing="1">GENERATOR</text>'
        f'<rect x="577" y="8" width="200" height="26" rx="13" fill="{gen_fill}"/>'
        f'<text x="677" y="25" fill="#FFFFFF" font-size="12" font-weight="bold" text-anchor="middle">GEN | {gen_badge}</text>'
        f'<polygon points="368,122 343,176 393,176" fill="{b4_col}" stroke="#263238" stroke-width="2"/>'
        f'<text x="368" y="164" fill="#FFFFFF" font-size="12" font-weight="bold" text-anchor="middle">Brg.4</text>'
        f'<polygon points="505,122 480,176 530,176" fill="{b56_col}" stroke="#263238" stroke-width="2"/>'
        f'<text x="505" y="164" fill="#FFFFFF" font-size="12" font-weight="bold" text-anchor="middle">Brg.5</text>'
        f'<polygon points="842,122 817,176 867,176" fill="{b56_col}" stroke="#263238" stroke-width="2"/>'
        f'<text x="842" y="164" fill="#FFFFFF" font-size="12" font-weight="bold" text-anchor="middle">Brg.6</text>'
        f'</svg>'
        f'</div>'
    )
    st.markdown(svg_html, unsafe_allow_html=True)


# =========================================================================
# Drawing Functions (Matplotlib)
# =========================================================================
def draw_dial_crosshair(ax, title_text, center_symbol, t_val, b_val, l_val, r_val, dial_color, badge_title, badge_desc, is_radial_raw=False):
    ax.set_aspect('equal')
    ax.set_xlim(-2.45, 2.45)
    ax.set_ylim(-2.65, 2.45)
    ax.axis('off')

    is_target = "TARGET" in title_text.upper() or "EXPECTED" in title_text.upper()
    is_zero_ref = "ZERO-REFERENCED" in title_text.upper()
    if is_target:
        header_bg, header_bdr = "#E8F5E9", "#2E7D32"
    elif is_zero_ref:
        header_bg, header_bdr = "#E3F2FD", "#1565C0"
    else:
        header_bg, header_bdr = "#FFEBEE", "#C62828"

    ax.text(0, 2.10, title_text, ha='center', va='center', fontsize=10.5, fontweight='bold', color=header_bdr,
            bbox=dict(boxstyle='round,pad=0.42', facecolor=header_bg, edgecolor=header_bdr, lw=1.6))

    outer_ring = patches.Circle((0, 0), 0.88, edgecolor=dial_color, facecolor='#FAFAFA', linewidth=3.2, zorder=1)
    inner_ring = patches.Circle((0, 0), 0.82, edgecolor='#CFD8DC', facecolor='#FFFFFF', linewidth=1.2, zorder=2)
    ax.add_patch(outer_ring)
    ax.add_patch(inner_ring)

    for angle in np.linspace(0, 2 * np.pi, 12, endpoint=False):
        x_in, y_in = 0.73 * np.cos(angle), 0.73 * np.sin(angle)
        x_out, y_out = 0.81 * np.cos(angle), 0.81 * np.sin(angle)
        ax.plot([x_in, x_out], [y_in, y_out], color='#B0BEC5', lw=1.2, zorder=2)

    ax.plot([-0.78, 0.78], [0, 0], color=dial_color, lw=2.0, linestyle='-', alpha=0.75, zorder=3)
    ax.plot([0, 0], [-0.78, 0.78], color=dial_color, lw=2.0, linestyle='-', alpha=0.75, zorder=3)

    hub = patches.Circle((0, 0), 0.25, facecolor='#FFFFFF', edgecolor=dial_color, lw=2.2, zorder=4)
    ax.add_patch(hub)
    ax.text(0, 0.0, center_symbol, ha='center', va='center', fontsize=18, fontweight='bold',
            color=dial_color, zorder=5)

    sub_label = "Unit: mm (Gen on LP)" if is_radial_raw else "Diff: mm"
    ax.text(0, -0.48, sub_label, ha='center', va='center', fontsize=8, fontweight='bold',
            color='#78909C', zorder=3)

    if is_radial_raw:
        t_str = f"{t_val:+.2f}" if t_val is not None else "--"
        b_str = f"{b_val:+.2f}" if b_val is not None else "--"
        l_str = f"{l_val:+.2f}" if l_val is not None else "--"
        r_str = f"{r_val:+.2f}" if r_val is not None else "--"
    else:
        t_str = f"{t_val:+.3f}" if t_val is not None else "--"
        b_str = f"{b_val:+.3f}" if b_val is not None else "--"
        l_str = f"{l_val:+.3f}" if l_val is not None else "--"
        r_str = f"{r_val:+.3f}" if r_val is not None else "--"

    ax.text(0, 1.15, f"Top\n{t_str}", ha='center', va='bottom', fontsize=9.5, fontweight='bold')
    ax.text(0, -1.15, f"{b_str}\nBot", ha='center', va='top', fontsize=9.5, fontweight='bold')
    ax.text(-1.08, 0, f"Left\n{l_str}", ha='right', va='center', fontsize=9.5, fontweight='bold')
    ax.text(1.08, 0, f"Right\n{r_str}", ha='left', va='center', fontsize=9.5, fontweight='bold')

    txt_box = f"{badge_title}\n[{badge_desc}]"
    ax.text(0, -1.95, txt_box, ha='center', va='top', fontsize=9.2, fontweight='bold', color=header_bdr,
            bbox=dict(boxstyle='round,pad=0.42', facecolor=header_bg, edgecolor=header_bdr, lw=1.5))


def draw_coupling_physical_setup(ax, choice: str):
    """Draw exact EGAT Mae Moh LP-Gen Coupling Dial Gauge Setup (View from Gov. End)"""
    ax.set_aspect('equal')
    ax.set_xlim(-2.2, 8.6)
    ax.set_ylim(-3.8, 4.3)
    ax.axis('off')

    ax.add_patch(patches.Rectangle((-1.8, -2.35), 10.0, 6.35, fill=False, edgecolor='#1E88E5', linewidth=1.6))
    ax.text(3.2, 3.72, "LP. - GEN. COUPLING", ha='center', va='center', fontsize=12.5, fontweight='bold', color='#212121', family='serif')
    ax.text(-1.55, -2.10, "VIEW FROM GOV. END", ha='left', va='center', fontsize=9.5, fontweight='bold', color='#212121', family='serif')

    gen_color = '#1565C0' if choice == '1' else '#D84315'
    lp_color = '#D84315' if choice in ['1', '2'] else '#1565C0'

    # Left: GENERATOR
    ax.add_patch(patches.Rectangle((-0.2, -0.65), 2.3, 1.3, facecolor=gen_color, fill=True, alpha=0.18, edgecolor='#212121', linewidth=2.0))
    ax.add_patch(patches.Rectangle((2.1, -1.55), 0.75, 3.1, facecolor=gen_color, fill=True, alpha=0.25, edgecolor='#212121', linewidth=2.2))
    ax.text(0.85, 0.0, "GENERATOR", ha='center', va='center', color='#102027', fontsize=10.5, fontweight='bold', family='serif')

    # Right: LP. TURBINE
    ax.add_patch(patches.Rectangle((4.30, -0.65), 2.3, 1.3, facecolor=lp_color, fill=True, alpha=0.18, edgecolor='#212121', linewidth=2.0))
    ax.add_patch(patches.Rectangle((3.55, -1.55), 0.75, 3.1, facecolor=lp_color, fill=True, alpha=0.25, edgecolor='#212121', linewidth=2.2))
    ax.text(5.55, 0.0, "LP. TURBINE", ha='center', va='center', color='#102027', fontsize=10.5, fontweight='bold', family='serif')

    ax.plot([-0.7, 7.1], [0, 0], color='#455A64', lw=1.1, linestyle='-.')
    ax.annotate("", xy=(1.25, 0.80), xytext=(0.45, 0.80),
                arrowprops=dict(arrowstyle="->", connectionstyle="arc3,rad=-0.55", color='#212121', lw=1.5))
    ax.annotate("", xy=(5.95, 0.80), xytext=(5.15, 0.80),
                arrowprops=dict(arrowstyle="->", connectionstyle="arc3,rad=-0.55", color='#212121', lw=1.5))

    b_col = '#212121'

    if choice in ['2', '3']:
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

        if choice == '2':
            status_txt = (
                "[SOLUTION 2: Shared 50:50 Adjustment (LP Brg.4 + Gen Brg.5 & 6)]\n"
                "* Standard Field Bridge Setup: Mounted on GENERATOR probing LP. TURBINE (Rim, G1, G2).\n"
                "* Shim corrections split 50:50 between LP Brg.4 and Gen Brg.5 & 6."
            )
            bg_col, bdr_col = "#FFFDE7", "#F57F17"
        else:
            status_txt = (
                "[SOLUTION 3: Adjust Gen Bearing 5 & 6 Only (LP. TURBINE FIXED 100%)]\n"
                "* Standard Field Bridge Setup: Mounted on GENERATOR probing LP. TURBINE (Fixed Reference).\n"
                "* All shim adjustments performed on Generator Brg.5 & 6."
            )
            bg_col, bdr_col = "#FFEBEE", "#C62828"
    else:
        ax.plot([3.925, 3.925, 2.475, 2.475], [1.55, 3.15, 3.15, 2.68], color=b_col, lw=1.8)
        ax.add_patch(patches.Circle((2.475, 2.38), 0.30, facecolor='#FF9800', edgecolor=b_col, lw=1.8, zorder=4))
        ax.text(2.475, 2.38, "R", ha='center', va='center', fontsize=9.5, fontweight='bold', color=b_col, zorder=5)
        ax.annotate("", xy=(2.475, 1.55), xytext=(2.475, 2.08), arrowprops=dict(arrowstyle="->", color=b_col, lw=1.8))
        ax.text(3.20, 3.25, "Radial (Rim)", ha='center', va='bottom', fontsize=8.8, fontweight='bold', color='#1565C0')

        ax.plot([3.75, 3.75, 1.25, 1.25, 1.48], [1.55, 3.32, 3.32, 1.32, 1.32], color=b_col, lw=1.8)
        ax.add_patch(patches.Circle((1.78, 1.32), 0.30, facecolor='#FF9800', edgecolor=b_col, lw=1.8, zorder=4))
        ax.text(1.78, 1.32, "G1", ha='center', va='center', fontsize=8.8, fontweight='bold', color=b_col, zorder=5)
        ax.annotate("", xy=(2.10, 1.32), xytext=(2.08, 1.32), arrowprops=dict(arrowstyle="->", color=b_col, lw=1.8))
        ax.text(1.12, 1.32, "G1 (Top Axial)", ha='right', va='center', fontsize=8.8, fontweight='bold', color='#D84315')

        ax.plot([3.925, 3.925, 1.25, 1.25, 1.48], [-1.55, -2.02, -2.02, -1.32, -1.32], color=b_col, lw=1.8)
        ax.add_patch(patches.Circle((1.78, -1.32), 0.30, facecolor='#FF9800', edgecolor=b_col, lw=1.8, zorder=4))
        ax.text(1.78, -1.32, "G2", ha='center', va='center', fontsize=8.8, fontweight='bold', color=b_col, zorder=5)
        ax.annotate("", xy=(2.10, -1.32), xytext=(2.08, -1.32), arrowprops=dict(arrowstyle="->", color=b_col, lw=1.8))
        ax.text(1.12, -1.32, "G2 (Bot Axial)", ha='right', va='center', fontsize=8.8, fontweight='bold', color='#D84315')

        status_txt = (
            "[SOLUTION 1: Adjust LP Bearing 4 Only (GENERATOR FIXED 100%)]\n"
            "* Manual Equivalent Setup: Probing GENERATOR flange as fixed reference.\n"
            "* Field Note: You may still input Gen-to-LP readings; software auto-inverts signs."
        )
        bg_col, bdr_col = "#E8F5E9", "#2E7D32"

    ax.text(3.2, -3.05, status_txt, ha='center', va='center', fontsize=9.2, fontweight='bold',
            bbox=dict(boxstyle='round,pad=0.52', facecolor=bg_col, edgecolor=bdr_col, lw=1.8))


def draw_perpendicular_manual_diagram(ax, title, pos_lbl, neg_lbl, choice_val,
                                      ax_open_mm, open_at_neg, rad_gen_high_mm,
                                      l_b4, lp_action_txt, gen_action_list, sub_note):
    """Draw 90-degree perpendicular shaft & flange geometry diagram"""
    ax.set_aspect('equal')
    ax.axis('off')

    ax.plot([-4.5, 5.2], [0, 0], color='black', linestyle='--', linewidth=1.5, zorder=1)
    ref_txt = {
        '1': 'Generator Centerline (FIXED 100%)',
        '2': 'Shared Target Centerline (50:50)',
        '3': 'Turbine LP Centerline (FIXED 100%)'
    }[choice_val]
    ax.text(5.15, 0.08, ref_txt, ha='right', va='bottom', fontsize=8.5, style='italic', color='#455A64')

    flange_half_h = 0.85
    sq = 0.14

    if choice_val == '1':
        ratio_lp, ratio_gen = 1.0, 0.0
    elif choice_val == '2':
        ratio_lp, ratio_gen = 0.5, 0.5
    else:
        ratio_lp, ratio_gen = 0.0, 1.0

    vis_shift = 0.50 if rad_gen_high_mm >= 0 else -0.50
    lp_vis_off = -vis_shift * ratio_lp
    gen_vis_off = vis_shift * ratio_gen

    base_tilt = 0.24 if open_at_neg else -0.24
    lp_tilt = base_tilt * ratio_lp
    gen_tilt = -base_tilt * ratio_gen

    # Left side: TURBINE (LP) - LP Brg.4
    lp_cx = -0.45
    lp_top_x, lp_top_y = lp_cx + lp_tilt, lp_vis_off + flange_half_h
    lp_bot_x, lp_bot_y = lp_cx - lp_tilt, lp_vis_off - flange_half_h

    lp_col = '#1565C0' if ratio_lp == 0 else '#D84315'
    ax.plot([lp_top_x, lp_bot_x], [lp_top_y, lp_bot_y], color=lp_col, linewidth=3.5, zorder=4)
    ax.plot(lp_cx, lp_vis_off, 'ko', markersize=5, zorder=5)

    dx_lp, dy_lp = -flange_half_h, lp_tilt
    norm_lp = np.hypot(dx_lp, dy_lp)
    ux_lp, uy_lp = dx_lp / norm_lp, dy_lp / norm_lp

    lp_end_x = lp_cx + ux_lp * 3.5
    lp_end_y = lp_vis_off + uy_lp * 3.5
    ax.plot([lp_cx, lp_end_x], [lp_vis_off, lp_end_y], color=lp_col, linewidth=3.2, zorder=3)

    fx_lp, fy_lp = lp_tilt / norm_lp, flange_half_h / norm_lp
    p1 = (lp_cx + ux_lp * sq, lp_vis_off + uy_lp * sq)
    p2 = (p1[0] + fx_lp * sq, p1[1] + fy_lp * sq)
    p3 = (lp_cx + fx_lp * sq, lp_vis_off + fy_lp * sq)
    ax.plot([p1[0], p2[0], p3[0]], [p1[1], p2[1], p3[1]], color='black', linewidth=1.1, zorder=5)

    b4_x = lp_cx + ux_lp * 2.2
    b4_y = lp_vis_off + uy_lp * 2.2
    ax.plot(b4_x, b4_y - 0.11, marker='^', markersize=10, color='#FF9800', markeredgecolor='black', zorder=6)
    lp_title = "TURBINE (LP) [FIXED]" if ratio_lp == 0 else f"TURBINE (LP) [{int(ratio_lp*100)}%]"
    ax.text(b4_x, b4_y + 0.25, lp_title, ha='center', va='bottom', fontsize=10, fontweight='bold', color=lp_col)
    ax.text(b4_x, b4_y - 0.25, f"LP Brg.4 ({l_b4:.0f})\n{lp_action_txt}", ha='center', va='top', fontsize=8.4, fontweight='bold',
            color='#37474F' if ratio_lp == 0 else '#2E7D32',
            bbox=dict(boxstyle='round,pad=0.25', facecolor='#ECEFF1' if ratio_lp == 0 else '#E8F5E9',
                      edgecolor='#78909C' if ratio_lp == 0 else '#2E7D32', lw=1.1))

    # Right side: GENERATOR - Gen Brg.5 & Brg.6
    gen_cx = 0.65
    gen_top_x, gen_top_y = gen_cx + gen_tilt, gen_vis_off + flange_half_h
    gen_bot_x, gen_bot_y = gen_cx - gen_tilt, gen_vis_off - flange_half_h

    gen_col = '#1565C0' if ratio_gen == 0 else '#D84315'
    ax.plot([gen_top_x, gen_bot_x], [gen_top_y, gen_bot_y], color=gen_col, linewidth=3.5, zorder=4)
    ax.plot(gen_cx, gen_vis_off, 'ko', markersize=5, zorder=5)

    dx_gen, dy_gen = flange_half_h, -gen_tilt
    norm_gen = np.hypot(dx_gen, dy_gen)
    ux_gen, uy_gen = dx_gen / norm_gen, dy_gen / norm_gen

    gen_end_x = gen_cx + ux_gen * 4.3
    gen_end_y = gen_vis_off + uy_gen * 4.3
    ax.plot([gen_cx, gen_end_x], [gen_vis_off, gen_end_y], color=gen_col, linewidth=3.2, zorder=3)

    fx_gen, fy_gen = gen_tilt / norm_gen, flange_half_h / norm_gen
    g1 = (gen_cx + ux_gen * sq, gen_vis_off + uy_gen * sq)
    g2 = (g1[0] + fx_gen * sq, g1[1] + fy_gen * sq)
    g3 = (gen_cx + fx_gen * sq, gen_vis_off + fy_gen * sq)
    ax.plot([g1[0], g2[0], g3[0]], [g1[1], g2[1], g3[1]], color='black', linewidth=1.1, zorder=5)

    gen_title = "GENERATOR [FIXED]" if ratio_gen == 0 else f"GENERATOR [{int(ratio_gen*100)}%]"
    ax.text(gen_cx + ux_gen * 2.55, gen_vis_off + uy_gen * 2.55 + 0.30, gen_title, ha='center', va='bottom',
            fontsize=10, fontweight='bold', color=gen_col)

    positions_vis = [1.45, 3.65]
    for dist_v, (lbl_pt, act_pt) in zip(positions_vis, gen_action_list):
        px = gen_cx + ux_gen * dist_v
        py = gen_vis_off + uy_gen * dist_v
        ax.plot(px, py - 0.11, marker='^', markersize=10, color='#FF9800', markeredgecolor='black', zorder=6)
        ax.text(px, py - 0.25, f"{lbl_pt}\n{act_pt}", ha='center', va='top', fontsize=8.3, fontweight='bold',
                color='#37474F' if ratio_gen == 0 else '#C62828',
                bbox=dict(boxstyle='round,pad=0.25', facecolor='#ECEFF1' if ratio_gen == 0 else '#FFEBEE',
                          edgecolor='#78909C' if ratio_gen == 0 else '#C62828', lw=1.1))

    # Axial dimension line
    dim_y = max(lp_top_y, gen_top_y) + 0.42
    ax.plot([lp_top_x, lp_top_x], [lp_top_y, dim_y + 0.12], color='black', linewidth=1.0)
    ax.plot([gen_top_x, gen_top_x], [gen_top_y, dim_y + 0.12], color='black', linewidth=1.0)
    ax.annotate('', xy=(lp_top_x, dim_y), xytext=(lp_top_x - 0.40, dim_y), arrowprops=dict(arrowstyle='->', color='black', lw=1.2))
    ax.annotate('', xy=(gen_top_x, dim_y), xytext=(gen_top_x + 0.40, dim_y), arrowprops=dict(arrowstyle='->', color='black', lw=1.2))
    ax.plot([lp_top_x, gen_top_x], [dim_y, dim_y], color='black', linewidth=1.0)
    ax.text((lp_top_x + gen_top_x) / 2, dim_y + 0.10, f"Axial Gap = {abs(ax_open_mm):.3f} mm",
            ha='center', va='bottom', fontsize=9.2, fontweight='bold', color='#8E24AA')

    # Radial dimension line
    dim_x = 0.08
    ax.plot([lp_cx, dim_x + 0.12], [lp_vis_off, lp_vis_off], color='black', linewidth=1.0)
    ax.plot([dim_x - 0.12, gen_cx], [gen_vis_off, gen_vis_off], color='black', linewidth=1.0)
    y_hi, y_lo = max(lp_vis_off, gen_vis_off), min(lp_vis_off, gen_vis_off)
    if abs(y_hi - y_lo) > 0.05:
        ax.annotate('', xy=(dim_x, y_hi), xytext=(dim_x, y_hi + 0.35), arrowprops=dict(arrowstyle='->', color='black', lw=1.2))
        ax.annotate('', xy=(dim_x, y_lo), xytext=(dim_x, y_lo - 0.35), arrowprops=dict(arrowstyle='->', color='black', lw=1.2))
        ax.plot([dim_x, dim_x], [y_lo, y_hi], color='black', linewidth=1.0)
        ax.text(dim_x + 0.10, (y_hi + y_lo) / 2 + 0.15, f"Offset\n{abs(rad_gen_high_mm):.3f}",
                ha='left', va='center', fontsize=8.4, fontweight='bold', color='#C62828',
                bbox=dict(boxstyle='round,pad=0.15', facecolor='white', edgecolor='none', alpha=0.85))

    ax.text(-1.25, 1.25, pos_lbl, fontsize=13, fontweight='bold', color='black')
    ax.text(-1.25, -1.55, neg_lbl, fontsize=13, fontweight='bold', color='black')

    ax.text(5.15, -2.45, sub_note, ha='right', va='bottom', fontsize=8.4,
            bbox=dict(boxstyle='round,pad=0.38', facecolor='#FFFDE7', edgecolor='#FBC02D', lw=1.2))

    ax.set_title(title, fontsize=11.5, fontweight='bold', pad=12, color='#0A192F')
    ax.set_xlim(-4.6, 5.3)
    ax.set_ylim(-2.60, 2.25)


# =========================================================================
# Header Banner (Power Plant Control Room Style)
# =========================================================================
st.markdown("""
<div class="pp-header">
    <div>
        <div class="pp-header-title">⚡ ระบบคำนวณและสั่งงานตั้งศูนย์เพลา LP TURBINE – GENERATOR</div>
        <div class="pp-header-sub">แผนกบำรุงรักษากังหัน (หปกร-ธ.) | โรงไฟฟ้าแม่เมาะ ยูนิต 8–13</div>
    </div>
    <div class="pp-badge">EGAT MM 8-13 STANDARD</div>
</div>
""", unsafe_allow_html=True)

col_input, col_view = st.columns([1.15, 1.85], gap="large")

# =========================================================================
# Left Panel: ใบกรอกข้อมูลหน้างาน
# =========================================================================
with col_input:
    st.markdown("### 📝 1. เลือกวิธีปรับตั้ง & ป้อนค่าหน้างาน")

    sol_options = [
        "Solution 1: ปรับเฉพาะ LP Brg.4 (ล็อก Gen คงที่)",
        "Solution 2: ปรับร่วมกัน 50:50 (LP Brg.4 + Gen Brg.5, 6)",
        "Solution 3: ปรับเฉพาะ Gen Brg.5 & 6 (ล็อก LP คงที่)"
    ]
    sol_selected = st.radio("เลือกแนวทางการจัดแผ่นชิม (Alignment Strategy):", sol_options, key="active_solution_radio")
    choice_val = sol_selected[9]

    b_col1, b_col2 = st.columns(2)
    if b_col1.button("📋 โหลดค่าตัวอย่างหน้างาน", use_container_width=True):
        st.session_state.d_coupling = 760.0
        st.session_state.l_brg4 = 550.0
        st.session_state.l_brg5 = 1100.0
        st.session_state.l_brg6 = 9790.0
        st.session_state.r_top = 0.00
        st.session_state.r_bottom = -0.31
        st.session_state.r_left = 0.20
        st.session_state.r_right = -0.12
        st.session_state.g1_top, st.session_state.g2_top = 19.220, 19.310
        st.session_state.g1_left, st.session_state.g2_left = 19.140, 19.140
        st.session_state.g1_bot, st.session_state.g2_bot = 19.310, 19.200
        st.session_state.g1_right, st.session_state.g2_right = 19.255, 19.265
        st.rerun()

    if b_col2.button("🗑️ ล้างค่าทั้งหมด (Reset)", use_container_width=True):
        for k in input_keys:
            st.session_state[k] = None
        st.rerun()

    with st.expander("📏 ระยะแขนและขนาดหน้าแปลน (mm)", expanded=True):
        m1, m2 = st.columns(2)
        with m1:
            st.number_input("โตหน้าแปลน D (mm)", value=None, placeholder="เช่น 760", step=10.0, key="d_coupling")
            st.number_input("ระยะถึง Gen Brg.5 (mm)", value=None, placeholder="เช่น 1100", step=10.0, key="l_brg5")
        with m2:
            st.number_input("ระยะถึง LP Brg.4 (mm)", value=None, placeholder="เช่น 550", step=10.0, key="l_brg4")
            st.number_input("ระยะถึง Gen Brg.6 (mm)", value=None, placeholder="เช่น 9790", step=10.0, key="l_brg6")

    st.markdown('<div class="sheet-title">ตารางบันทึกค่า Coupling LP-Gen (หน่วย: mm)</div>', unsafe_allow_html=True)

    st.markdown("**1) ค่าแนวรัศมี (Radial - จับ Gen จี้ LP)**")
    rc1, rc2, rc3, rc4 = st.columns(4)
    with rc1:
        st.number_input("Top", value=None, placeholder="0.00", step=0.01, format="%.2f", key="r_top")
    with rc2:
        st.number_input("Bot", value=None, placeholder="-0.31", step=0.01, format="%.2f", key="r_bottom")
    with rc3:
        st.number_input("Left", value=None, placeholder="0.20", step=0.01, format="%.2f", key="r_left")
    with rc4:
        st.number_input("Right", value=None, placeholder="-0.12", step=0.01, format="%.2f", key="r_right")

    st.markdown("**2) ค่าแนวแกนหน้าแปลน (Axial)**")
    h1, h2, h3, h4 = st.columns([0.9, 1.15, 1.15, 1.05])
    h1.markdown("**Position**")
    h2.markdown("**G1**")
    h3.markdown("**G2**")
    h4.markdown("**(G1-G2)/2**")

    def calc_half_diff(v1, v2):
        if v1 is not None and v2 is not None:
            return (v1 - v2) / 2.0
        return None

    # แถว Top
    a1_1, a1_2, a1_3, a1_4 = st.columns([0.9, 1.15, 1.15, 1.05])
    a1_1.markdown("<div style='padding-top:8px; font-weight:bold;'>Top</div>", unsafe_allow_html=True)
    a1_2.number_input("Top G1", value=None, placeholder="G1", label_visibility="collapsed", step=0.005, format="%.3f", key="g1_top")
    a1_3.number_input("Top G2", value=None, placeholder="G2", label_visibility="collapsed", step=0.005, format="%.3f", key="g2_top")
    raw_a_top = calc_half_diff(st.session_state.g1_top, st.session_state.g2_top)
    a1_4.markdown(f"<div class='calc-box'>{raw_a_top:.3f}</div>" if raw_a_top is not None else "<div class='calc-box-empty'>--</div>", unsafe_allow_html=True)

    # แถว Left
    a2_1, a2_2, a2_3, a2_4 = st.columns([0.9, 1.15, 1.15, 1.05])
    a2_1.markdown("<div style='padding-top:8px; font-weight:bold;'>Left</div>", unsafe_allow_html=True)
    a2_2.number_input("Left G1", value=None, placeholder="G1", label_visibility="collapsed", step=0.005, format="%.3f", key="g1_left")
    a2_3.number_input("Left G2", value=None, placeholder="G2", label_visibility="collapsed", step=0.005, format="%.3f", key="g2_left")
    raw_a_left = calc_half_diff(st.session_state.g1_left, st.session_state.g2_left)
    a2_4.markdown(f"<div class='calc-box'>{raw_a_left:.3f}</div>" if raw_a_left is not None else "<div class='calc-box-empty'>--</div>", unsafe_allow_html=True)

    # แถว Bottom
    a3_1, a3_2, a3_3, a3_4 = st.columns([0.9, 1.15, 1.15, 1.05])
    a3_1.markdown("<div style='padding-top:8px; font-weight:bold;'>Bottom</div>", unsafe_allow_html=True)
    a3_2.number_input("Bot G1", value=None, placeholder="G1", label_visibility="collapsed", step=0.005, format="%.3f", key="g1_bot")
    a3_3.number_input("Bot G2", value=None, placeholder="G2", label_visibility="collapsed", step=0.005, format="%.3f", key="g2_bot")
    raw_a_bottom = calc_half_diff(st.session_state.g1_bot, st.session_state.g2_bot)
    a3_4.markdown(f"<div class='calc-box'>{raw_a_bottom:.3f}</div>" if raw_a_bottom is not None else "<div class='calc-box-empty'>--</div>", unsafe_allow_html=True)

    # แถว Right
    a4_1, a4_2, a4_3, a4_4 = st.columns([0.9, 1.15, 1.15, 1.05])
    a4_1.markdown("<div style='padding-top:8px; font-weight:bold;'>Right</div>", unsafe_allow_html=True)
    a4_2.number_input("Right G1", value=None, placeholder="G1", label_visibility="collapsed", step=0.005, format="%.3f", key="g1_right")
    a4_3.number_input("Right G2", value=None, placeholder="G2", label_visibility="collapsed", step=0.005, format="%.3f", key="g2_right")
    raw_a_right = calc_half_diff(st.session_state.g1_right, st.session_state.g2_right)
    a4_4.markdown(f"<div class='calc-box'>{raw_a_right:.3f}</div>" if raw_a_right is not None else "<div class='calc-box-empty'>--</div>", unsafe_allow_html=True)


# =========================================================================
# Right Panel: Power Plant Schematic & Technician Work Cards
# =========================================================================
with col_view:
    render_powerplant_schematic(choice_val)

    all_filled = all(st.session_state[k] is not None for k in input_keys)

    if not all_filled:
        missing_count = sum(1 for k in input_keys if st.session_state[k] is None)
        st.info(
            f"👈 **กรุณาป้อนตัวเลขจากใบงานหน้างานทางด้านซ้ายให้ครบ** (หรือกดปุ่ม **'📋 โหลดค่าตัวอย่างหน้างาน'** เพื่อทดสอบระบบ)\n\n"
            f"สถานะการป้อนข้อมูลปัจจุบัน: กรอกแล้ว **{len(input_keys) - missing_count} / {len(input_keys)}** ช่อง"
        )
        st.stop()

    if st.session_state.d_coupling <= 0:
        st.error("❌ ค่าขนาดหน้าแปลนคัปปลิ้ง D (mm) ต้องมากกว่า 0")
        st.stop()

    d_coupling = float(st.session_state.d_coupling)
    l_brg4 = float(st.session_state.l_brg4)
    l_brg5 = float(st.session_state.l_brg5)
    l_brg6 = float(st.session_state.l_brg6)

    r_top = float(st.session_state.r_top)
    r_bottom = float(st.session_state.r_bottom)
    r_left = float(st.session_state.r_left)
    r_right = float(st.session_state.r_right)

    # =====================================================================
    # 1. แปลงค่าเทียบศูนย์ (min_val -> 0 ทั้ง 2 แกน ตามหนังสือ)
    # =====================================================================
    zero_r_top, zero_r_bot, zero_r_left, zero_r_right, off_r_tb, off_r_lr = convert_tir_to_zero_ref(
        r_top, r_bottom, r_left, r_right
    )
    zero_a_top, zero_a_bot, zero_a_left, zero_a_right, off_a_tb, off_a_lr = convert_tir_to_zero_ref(
        raw_a_top, raw_a_bottom, raw_a_left, raw_a_right
    )

    # =====================================================================
    # 2. ตรวจสอบสมการเกจวัด (T + B = L + R)
    # =====================================================================
    diff_r_mm = abs((r_top + r_bottom) - (r_left + r_right))
    valid_r = diff_r_mm <= TOLERANCE_RADIAL_MM

    diff_a_mm = abs((raw_a_top + raw_a_bottom) - (raw_a_left + raw_a_right))
    valid_a = diff_a_mm <= 0.025

    # =====================================================================
    # 3. หาตำแหน่งจริงของเพลา (กฎหาร 2 — จับฐานเกจที่ Gen จี้ LP)
    # =====================================================================
    lp_above_gen_mm = (zero_r_top - zero_r_bot) / 2.0      # +0.155 mm (LP สูงกว่า Gen)
    gen_above_lp_mm = -lp_above_gen_mm                     # -0.155 mm (Gen ต่ำกว่า LP)

    # เป้าหมายแม่เมาะ: ต้องการให้ Gen ต่ำกว่า LP = 0.100 mm (หรือ LP สูงกว่า Gen = +0.100 mm)
    lp_radial_corr_mm = TARGET_GEN_DOWN_MM - lp_above_gen_mm   # 0.100 - 0.155 = -0.055 mm
    gen_radial_corr_mm = -lp_radial_corr_mm                    # +0.055 mm

    # แนวนอน (L & R): LP เยื้องไปทางซ้าย (L) ของ Gen = +0.160 mm
    lp_left_of_gen_mm = (zero_r_left - zero_r_right) / 2.0 # +0.160 mm

    # ระยะเปิดอ้าหน้าแปลน Axial:
    delta_x_v = (raw_a_bottom - raw_a_top) - TARGET_AXIAL_GAP_MM   # > 0 = ด้านล่างอ้า (+0.100 mm)
    delta_gap_lr = raw_a_left - raw_a_right                        # > 0 = ด้านซ้ายอ้า (+0.005 mm)

    target_radial_bottom_mm = 2.0 * TARGET_GEN_DOWN_MM
    target_radial_side_mm = TARGET_GEN_DOWN_MM

    # =====================================================================
    # 4. คำนวณระยะปรับตั้งที่ Bearing (ทำ Axial ก่อน แล้วรวมกับ Radial)
    # (+ คือ หนุน Shim ขึ้น / เลื่อนไปทางซ้าย L, - คือ ถอน Shim ออก / เลื่อนไปทางขวา R)
    # =====================================================================
    def calc_adjustments(arm_len_mm, is_lp_side=False):
        ax_v = (delta_x_v * arm_len_mm) / d_coupling
        ax_h = (delta_gap_lr * arm_len_mm) / d_coupling
        if is_lp_side:
            v_move = (+ax_v) + lp_radial_corr_mm
            h_move = (+ax_h) - lp_left_of_gen_mm
        else:
            v_move = (-ax_v) + gen_radial_corr_mm
            h_move = (-ax_h) + lp_left_of_gen_mm
        return ax_v, ax_h, v_move, h_move

    lp_ax_v, lp_ax_h, lp_v_full, lp_h_full = calc_adjustments(l_brg4, is_lp_side=True)
    b5_ax_v, b5_ax_h, b5_v_full, b5_h_full = calc_adjustments(l_brg5, is_lp_side=False)
    b6_ax_v, b6_ax_h, b6_v_full, b6_h_full = calc_adjustments(l_brg6, is_lp_side=False)

    if choice_val == '1':
        r_lp, r_gen = 1.0, 0.0
    elif choice_val == '2':
        r_lp, r_gen = 0.5, 0.5
    else:
        r_lp, r_gen = 0.0, 1.0

    shim_b4, shift_b4 = r_lp * lp_v_full, r_lp * lp_h_full
    shim_b5, shift_b5 = r_gen * b5_v_full, r_gen * b5_h_full
    shim_b6, shift_b6 = r_gen * b6_v_full, r_gen * b6_h_full

    gen_results = [
        ("Gen Brg.5", l_brg5, b5_ax_v, b5_ax_h, shim_b5, shift_b5),
        ("Gen Brg.6", l_brg6, b6_ax_v, b6_ax_h, shim_b6, shift_b6),
    ]

    if not valid_r:
        st.warning(f"⚠️ **คำเตือนตรวจเช็กค่า Radial:** ผลรวม $(T+B) = {r_top+r_bottom:+.2f}$ ต่างจาก $(L+R) = {r_left+r_right:+.2f}$ อยู่ **{diff_r_mm:.2f} mm** (เกินเกณฑ์มาตรฐาน 0.03 mm ควรทวนสอบตัวเลขหน้างาน)")

    # =====================================================================
    # การ์ดใบสั่งงานช่างหน้างาน 3 ใบ
    # =====================================================================
    st.markdown(f"### 🛠️ ใบสั่งงานปรับตั้งแผ่นชิมหน้างาน [Solution {choice_val}]")

    def render_tech_card(col, brg_title, arm_len, v_mm, h_mm, is_fixed):
        with col:
            if is_fixed:
                card_html = (
                    f'<div class="tech-card tech-card-fixed">'
                    f'<div class="brg-name">🔒 {brg_title}</div>'
                    f'<div class="brg-arm">ระยะแขน L = {arm_len:,.0f} mm (ฐานอ้างอิงหลัก)</div>'
                    f'<div class="action-row-lock">'
                    f'ยึดแน่นคงที่ (FIXED)<br>'
                    f'<span style="font-size:12px; font-weight:normal;">ไม่ต้องขยับหรือเปลี่ยนแผ่นชิม</span>'
                    f'</div>'
                    f'</div>'
                )
                st.markdown(card_html, unsafe_allow_html=True)
            else:
                v_class = "action-row" if v_mm >= 0 else "action-row-down"
                v_icon = "⬆️" if v_mm >= 0 else "⬇️"
                v_text = f"หนุนชิมล่าง (B) เพิ่ม +{v_mm:.3f} mm" if v_mm >= 0 else f"ถอนชิมล่าง (B) ออก -{abs(v_mm):.3f} mm"
                v_khid = f"{abs(v_mm)*100:.1f} ขีด"

                h_icon = "⬅️" if h_mm >= 0 else "➡️"
                h_text = f"เลื่อนไปทางซ้าย (L) +{h_mm:.3f} mm" if h_mm >= 0 else f"เลื่อนไปทางขวา (R) {abs(h_mm):.3f} mm"
                h_khid = f"{abs(h_mm)*100:.1f} ขีด"

                card_html = (
                    f'<div class="tech-card tech-card-adjust">'
                    f'<div class="brg-name">🔧 {brg_title}</div>'
                    f'<div class="brg-arm">ระยะแขนจาก Coupling L = {arm_len:,.0f} mm</div>'
                    f'<div class="{v_class}">'
                    f'<div class="action-label">{v_icon} แนวดิ่ง (บน – ล่าง : T & B)</div>'
                    f'<div class="action-val">{v_text}</div>'
                    f'<span class="khid-tag">≈ {v_khid} (0.01 mm/ขีด)</span>'
                    f'</div>'
                    f'<div class="action-row-horiz">'
                    f'<div class="action-label">{h_icon} แนวนอน (ซ้าย – ขวา : L & R)</div>'
                    f'<div class="action-val">{h_text}</div>'
                    f'<span class="khid-tag">≈ {h_khid} (0.01 mm/ขีด)</span>'
                    f'</div>'
                    f'</div>'
                )
                st.markdown(card_html, unsafe_allow_html=True)

    card_c1, card_c2, card_c3 = st.columns(3)
    render_tech_card(card_c1, "LP Bearing 4", l_brg4, shim_b4, shift_b4, is_fixed=(choice_val == '3'))
    render_tech_card(card_c2, "Gen Bearing 5", l_brg5, shim_b5, shift_b5, is_fixed=(choice_val == '1'))
    render_tech_card(card_c3, "Gen Bearing 6", l_brg6, shim_b6, shift_b6, is_fixed=(choice_val == '1'))

    st.write("")

    # =====================================================================
    # แท็บแสดงรายละเอียดเชิงวิศวกรรม 4 แท็บ
    # =====================================================================
    tab1, tab2, tab3, tab4 = st.tabs([
        "📐 ไดอะแกรมเขียนแบบตั้งฉาก 90°",
        "📋 วิเคราะห์เกจ & ค่าเทียบศูนย์ 0",
        "🔍 จุดติดตั้ง Dial Gauge",
        "📝 วิธีทำและ Solve มือละเอียด"
    ])

    # ---------------------------------------------------------------------
    # Tab 1: ไดอะแกรมตั้งฉาก 90 องศา + กราฟแท่งสรุป Shim
    # ---------------------------------------------------------------------
    with tab1:
        fig2 = plt.figure(figsize=(12, 13.5), dpi=130)
        gs = fig2.add_gridspec(3, 1, height_ratios=[1.25, 1.25, 0.85], hspace=0.28)
        ax_side = fig2.add_subplot(gs[0])
        ax_top = fig2.add_subplot(gs[1])
        ax_bar = fig2.add_subplot(gs[2])

        lp_act_v = f"Add +{shim_b4:.3f} mm" if shim_b4 > 0 else ("FIXED" if choice_val == '3' else f"{shim_b4:.3f} mm")
        gen_act_v_list = [
            (f"Brg.5 ({l_brg5:.0f})", "FIXED" if choice_val == '1' else f"{shim_b5:+.3f} mm"),
            (f"Brg.6 ({l_brg6:.0f})", "FIXED" if choice_val == '1' else f"{shim_b6:+.3f} mm"),
        ]
        note_tb_box = (
            f"• Axial Gap (T-B) = {delta_x_v:+.3f} mm | LP Radial Corr = {lp_radial_corr_mm:+.3f} mm\n"
            f"• LP Brg.4 = {shim_b4:+.3f} mm | Gen Brg.5 = {shim_b5:+.3f} mm | Gen Brg.6 = {shim_b6:+.3f} mm"
        )
        draw_perpendicular_manual_diagram(
            ax_side,
            title=f"1. SIDE VIEW (T - B) | Solution {choice_val} (Perpendicular 90° Geometry)",
            pos_lbl="T", neg_lbl="B", choice_val=choice_val,
            ax_open_mm=delta_x_v, open_at_neg=(delta_x_v >= 0),
            rad_gen_high_mm=gen_above_lp_mm,
            l_b4=l_brg4, lp_action_txt=lp_act_v, gen_action_list=gen_act_v_list, sub_note=note_tb_box
        )

        lp_act_h = f"Shift R {abs(shift_b4):.3f}" if shift_b4 < 0 else (f"Shift L +{shift_b4:.3f}" if shift_b4 > 0 else "FIXED")
        gen_act_h_list = [
            (f"Brg.5 ({l_brg5:.0f})", "FIXED" if choice_val == '1' else (f"L +{shift_b5:.3f}" if shift_b5 >= 0 else f"R {abs(shift_b5):.3f}")),
            (f"Brg.6 ({l_brg6:.0f})", "FIXED" if choice_val == '1' else (f"L +{shift_b6:.3f}" if shift_b6 >= 0 else f"R {abs(shift_b6):.3f}")),
        ]
        note_lr_box = (
            f"• Axial Gap (L-R) = {delta_gap_lr:+.4f} mm | LP Left Offset = {lp_left_of_gen_mm:+.3f} mm\n"
            f"• LP Brg.4 = {shift_b4:+.3f} mm | Gen Brg.5 = {shift_b5:+.3f} mm | Gen Brg.6 = {shift_b6:+.3f} mm"
        )
        draw_perpendicular_manual_diagram(
            ax_top,
            title=f"2. TOP VIEW (L - R) | Look to Generator (Solution {choice_val})",
            pos_lbl="L", neg_lbl="R", choice_val=choice_val,
            ax_open_mm=delta_gap_lr, open_at_neg=(delta_gap_lr < 0),
            rad_gen_high_mm=-lp_left_of_gen_mm,
            l_b4=l_brg4, lp_action_txt=lp_act_h, gen_action_list=gen_act_h_list, sub_note=note_lr_box
        )

        labels = ["LP Bearing 4", "Gen Bearing 5", "Gen Bearing 6"]
        shims = [shim_b4, shim_b5, shim_b6]
        colors = ['#2E7D32' if s > 0 else ('#C62828' if s < 0 else '#9E9E9E') for s in shims]

        bars = ax_bar.bar(labels, shims, color=colors, width=0.35, edgecolor='black', zorder=3)
        ax_bar.axhline(0, color='black', linewidth=1.2)
        ax_bar.set_ylabel("Vertical Shim (mm)", fontsize=10, fontweight='bold')
        ax_bar.set_title(f"3. Vertical Shim Adjustment Summary at Bearings [SOLUTION {choice_val}]", fontsize=11.5, fontweight='bold', pad=10)
        ax_bar.grid(axis='y', linestyle=':', alpha=0.6)

        max_val = max(abs(s) for s in shims) if any(abs(s) > 0 for s in shims) else 0.05
        ax_bar.set_ylim(-max_val * 1.55 - 0.05, max_val * 1.55 + 0.05)

        for bar, s_val in zip(bars, shims):
            h = bar.get_height()
            va_align = 'bottom' if h >= 0 else 'top'
            y_pos = h + (0.015 if h >= 0 else -0.015)
            action_word = "ADD SHIM (+)" if s_val > 0 else ("REMOVE SHIM (-)" if s_val < 0 else "FIXED")
            ax_bar.text(bar.get_x() + bar.get_width() / 2., y_pos, f"{s_val:+.3f} mm\n({action_word})",
                        ha='center', va=va_align, fontsize=9.5, fontweight='bold')

        st.pyplot(fig2)

    # ---------------------------------------------------------------------
    # Tab 2: ใบบันทึกผลและวิเคราะห์เกจ
    # ---------------------------------------------------------------------
    with tab2:
        st.subheader("📋 ใบบันทึกผลและวิเคราะห์เกจ (Inspection Sheet & Zero-Reference Analysis)")
        st.caption("แถวบน = ค่าดิบที่อ่านได้จากตาราง/Dial Gauge | แถวล่าง = ค่าแปลงเทียบศูนย์ (0) เพื่อให้ฝั่งที่น้อยกว่าเป็น 0 ทั้งสองแกน")

        c1, c2 = st.columns(2)
        with c1:
            st.info(f"**1. แนวแกนหน้าแปลน (Axial Face Gap):**\n"
                    f"- บน-ล่าง (T&B): {'หน้าแปลนล่างอ้า' if delta_x_v > 0 else ('หน้าแปลนบนอ้า' if delta_x_v < 0 else 'ขนาน')} **{abs(delta_x_v):.3f} mm** ($T={zero_a_top:.3f}, B={zero_a_bot:.3f}$)\n"
                    f"- ซ้าย-ขวา (L&R): {'หน้าแปลนซ้ายอ้า' if delta_gap_lr > 0 else ('หน้าแปลนขวาอ้า' if delta_gap_lr < 0 else 'ขนาน')} **{abs(delta_gap_lr):.4f} mm** ($L={zero_a_left:.3f}, R={zero_a_right:.3f}$)\n"
                    f"- เช็กผลรวม $(T+B)-(L+R)$ = **{diff_a_mm:.4f} mm** [{'✅ ผ่านเกณฑ์ <= 0.025 mm' if valid_a else '⚠️ เกินเกณฑ์'}]")
        with c2:
            if valid_r:
                st.success(f"**2. แนวรัศมีเพลา (Radial Rim TIR):**\n"
                           f"- ตรวจสอบ $(T+B)-(L+R)$ = **{diff_r_mm:.2f} mm** (✅ ผ่านเกณฑ์ <= 0.03 mm)\n"
                           f"- ค่าเทียบศูนย์ (Zero-Referenced): $T={zero_r_top:+.2f}, B={zero_r_bot:+.2f}$ | $L={zero_r_left:+.2f}, R={zero_r_right:+.2f}$")
            else:
                st.error(f"**2. แนวรัศมีเพลา (Radial Rim TIR):**\n"
                         f"- ตรวจสอบ $(T+B)-(L+R)$ = **{diff_r_mm:.2f} mm** (❌ เกินเกณฑ์ 0.03 mm: $T+B={r_top+r_bottom:+.2f}$, $L+R={r_left+r_right:+.2f}$)\n"
                         f"- ค่าเทียบศูนย์ (Zero-Referenced): $T={zero_r_top:+.2f}, B={zero_r_bot:+.2f}$ | $L={zero_r_left:+.2f}, R={zero_r_right:+.2f}$")

        fig1 = plt.figure(figsize=(15, 11.2))

        ax1 = fig1.add_subplot(2, 2, 1)
        face_desc_en = "Bottom Flange OPEN" if delta_x_v > 0 else ("Top Flange OPEN" if delta_x_v < 0 else "Flanges Parallel")
        draw_dial_crosshair(
            ax1, "[1] Raw Axial Input (G1 - G2) / 2", "A",
            raw_a_top, raw_a_bottom, raw_a_left, raw_a_right, '#C62828',
            f"Vertical Gap (B - T) = {delta_x_v:+.3f} mm", face_desc_en, is_radial_raw=False
        )

        ax2 = fig1.add_subplot(2, 2, 2)
        rim_desc_en = f"LP HIGHER than Gen by {abs(lp_above_gen_mm):.3f} mm" if lp_above_gen_mm >= 0 else f"LP LOWER than Gen by {abs(lp_above_gen_mm):.3f} mm"
        draw_dial_crosshair(
            ax2, "[2] Raw Radial Input (Dial Gauge)", "R",
            r_top, r_bottom, r_left, r_right, '#C62828',
            f"True Vertical Offset = {abs(lp_above_gen_mm):.3f} mm", rim_desc_en, is_radial_raw=True
        )

        ax3 = fig1.add_subplot(2, 2, 3)
        draw_dial_crosshair(
            ax3, "[3] Zero-Referenced Axial (Closed = 0.000)", "A",
            zero_a_top, zero_a_bot, zero_a_left, zero_a_right, '#1565C0',
            f"V-Gap = {abs(delta_x_v):.3f} mm | H-Gap = {abs(delta_gap_lr):.3f} mm",
            "Closed Side Set to 0.000 mm", is_radial_raw=False
        )

        ax4 = fig1.add_subplot(2, 2, 4)
        draw_dial_crosshair(
            ax4, "[4] Zero-Referenced Radial TIR (Min = 0.00)", "R",
            zero_r_top, zero_r_bot, zero_r_left, zero_r_right, '#1565C0',
            f"Vertical: T={zero_r_top:+.2f}, B={zero_r_bot:+.2f} mm",
            f"Horizontal: L={zero_r_left:+.2f}, R={zero_r_right:+.2f} mm", is_radial_raw=True
        )

        plt.subplots_adjust(top=0.94, bottom=0.06, hspace=0.38, wspace=0.25)
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
            ax_exp_face, "Expected Face Gauge (Target Axial)", "A",
            0.000, TARGET_AXIAL_GAP_MM, 0.000, 0.000, '#2E7D32',
            f"Strategy: Solution {choice_val}", f"Target Axial Gap = {TARGET_AXIAL_GAP_MM:+.3f} mm", is_radial_raw=False
        )

        ax_exp_rim = fig3.add_subplot(2, 2, 4)
        draw_dial_crosshair(
            ax_exp_rim, "Expected Rim Gauge (Target Radial - Gen on LP)", "R",
            0.00, target_radial_bottom_mm, target_radial_side_mm, target_radial_side_mm, '#2E7D32',
            f"Target: Gen down {TARGET_GEN_DOWN_MM:.3f} mm", f"Expected Bottom Reading = {target_radial_bottom_mm:+.2f} mm", is_radial_raw=True
        )

        plt.subplots_adjust(top=0.95, bottom=0.08, hspace=0.38, wspace=0.25)
        st.pyplot(fig3)

    # ---------------------------------------------------------------------
    # Tab 4: วิธีทำและ Solve มือละเอียดตามตำรา (อ่านง่ายเป็นขั้นเป็นตอน)
    # ---------------------------------------------------------------------
    with tab4:
        st.subheader(f"📝 วิธีทำและ Solve มือละเอียด [SOLUTION {choice_val}]")

        with st.expander("🔹 ขั้นตอนที่ 1: ตรวจสอบความถูกต้องของค่าที่อ่านได้ (T + B = L + R) และแปลงค่าเทียบศูนย์ (0)", expanded=True):
            c_v1, c_v2 = st.columns(2)
            with c_v1:
                st.markdown("**1.1 แนวรัศมี (RADIAL):**")
                st.write(f"- เช็กผลรวม: $T + B = ({r_top:+.2f}) + ({r_bottom:+.2f}) = {r_top + r_bottom:+.2f}\\text{{ mm}}$ | $L + R = ({r_left:+.2f}) + ({r_right:+.2f}) = {r_left + r_right:+.2f}\\text{{ mm}}$")
                st.write(f"- แปลงเทียบศูนย์ (`min -> 0`): **$T = {zero_r_top:+.2f}, B = {zero_r_bot:+.2f}$** และ **$L = {zero_r_left:+.2f}, R = {zero_r_right:+.2f}\\text{{ mm}}$**")
                st.write(f"- ตำแหน่งจริง (หาร 2): **LP อยู่สูงกว่า Gen $= {lp_above_gen_mm:.3f}\\text{{ mm}}$** (เป้าหมายต้องการให้ LP สูงกว่า Gen $= {TARGET_GEN_DOWN_MM:.3f}\\text{{ mm}}$ $\\rightarrow$ **LP สูงเกินเป้าหมายอยู่ `{abs(lp_radial_corr_mm):.3f} mm`**) และ **LP เยื้องไปทางซ้าย (`L`) ของ Gen $= {lp_left_of_gen_mm:.3f}\\text{{ mm}}$**")
            with c_v2:
                st.markdown("**1.2 แนวแกนหน้าแปลน (AXIAL):**")
                st.write(f"- แปลงเทียบศูนย์ (`min -> 0`): **$T = {zero_a_top:.3f}, B = {zero_a_bot:.3f}$** และ **$L = {zero_a_left:.3f}, R = {zero_a_right:.3f}\\text{{ mm}}$**")
                v_open_txt = f"หน้าแปลนด้านล่างอ้า `{abs(delta_x_v):.3f} mm`" if delta_x_v > 0 else (f"หน้าแปลนด้านบนอ้า `{abs(delta_x_v):.3f} mm`" if delta_x_v < 0 else "หน้าแปลนขนานแนวดิ่ง (`0.000 mm`)")
                h_open_txt = f"หน้าแปลนด้านซ้ายอ้า `{abs(delta_gap_lr):.3f} mm`" if delta_gap_lr > 0 else (f"หน้าแปลนด้านขวาอ้า `{abs(delta_gap_lr):.3f} mm`" if delta_gap_lr < 0 else "หน้าแปลนขนานแนวนอน (`0.000 mm`)")
                st.write(f"- แนวดิ่ง: {v_open_txt}")
                st.write(f"- แนวนอน: {h_open_txt}")

        st.markdown("---")

        if choice_val == '1':
            st.markdown(f"### 1. กรณี Solution 1: ปรับเฉพาะ LP Brg.4 (`L4 = {l_brg4:.0f} mm`, `D = {d_coupling:.0f} mm`) — ล็อก Gen คงที่")

            st.markdown("* **แนวดิ่ง (บน–ล่าง):**")
            v_gap_dir = "ล่าง" if delta_x_v >= 0 else "บน"
            v_ax_act = "ยก LP Brg.4 ขึ้น" if lp_ax_v >= 0 else "ลด LP Brg.4 ลง"
            v_rad_act = "ลด LP Brg.4 ลง" if lp_radial_corr_mm < 0 else "ยก LP Brg.4 ขึ้น"
            v_net_act = "หนุนขึ้น" if shim_b4 >= 0 else "ถอนออก"
            st.markdown(
                f"  1. ปิดช่องอ้าหน้าแปลน{v_gap_dir} (`{abs(delta_x_v):.3f} mm`): ต้อง **{v_ax_act}** "
                f"$\\frac{{{delta_x_v:+.3f} \\times {l_brg4:.0f}}}{{{d_coupling:.0f}}} = \\mathbf{{{lp_ax_v:+.4f}\\text{{ mm}}}}$\n"
                f"  2. แก้ Radial ({'ลด LP ที่สูงเกินเป้าหมาย' if lp_radial_corr_mm < 0 else 'ยก LP ให้ได้ตามเป้าหมาย'} `{abs(lp_radial_corr_mm):.3f} mm`): ต้อง **{v_rad_act}** $\\mathbf{{{lp_radial_corr_mm:+.4f}\\text{{ mm}}}}$\n"
                f"  3. **รวมสุทธิ LP Brg.4 แนวดิ่ง:** $({lp_ax_v:+.4f}) + ({lp_radial_corr_mm:+.4f}) = \\mathbf{{{shim_b4:+.3f}\\text{{ mm}}}}$ *({v_net_act} {abs(shim_b4)*100:.1f} ขีด)*"
            )

            st.markdown("* **แนวนอน (ซ้าย–ขวา):**")
            h_gap_dir = "ซ้าย" if delta_gap_lr >= 0 else "ขวา"
            h_ax_act = "ดัน LP Brg.4 ไปทางซ้าย (`+L`)" if lp_ax_h >= 0 else "ดัน LP Brg.4 ไปทางขวา (`-R`)"
            h_rad_act = "ดัน LP Brg.4 ไปทางขวา (`-R`)" if lp_left_of_gen_mm >= 0 else "ดัน LP Brg.4 ไปทางซ้าย (`+L`)"
            h_net_act = "เลื่อนไปทางซ้าย L" if shift_b4 >= 0 else "เลื่อนไปทางขวา R"
            st.markdown(
                f"  1. ปิดช่องอ้าหน้าแปลน{h_gap_dir} (`{abs(delta_gap_lr):.3f} mm`): ต้อง **{h_ax_act}** "
                f"$\\frac{{{delta_gap_lr:+.3f} \\times {l_brg4:.0f}}}{{{d_coupling:.0f}}} = \\mathbf{{{lp_ax_h:+.4f}\\text{{ mm}}}}$\n"
                f"  2. แก้ Radial (ดึง LP ที่เยื้อง{'ซ้าย' if lp_left_of_gen_mm >= 0 else 'ขวา'} `{abs(lp_left_of_gen_mm):.3f} mm` กลับมา): ต้อง **{h_rad_act}** $\\mathbf{{{-lp_left_of_gen_mm:+.4f}\\text{{ mm}}}}$\n"
                f"  3. **รวมสุทธิ LP Brg.4 แนวนอน:** $({lp_ax_h:+.4f}) + ({-lp_left_of_gen_mm:+.4f}) = \\mathbf{{{shift_b4:+.3f}\\text{{ mm}}}}$ *({h_net_act} {abs(shift_b4)*100:.1f} ขีด)*"
            )

        elif choice_val == '3':
            st.markdown(f"### 3. กรณี Solution 3: ปรับเฉพาะ Gen Brg.5 & Brg.6 (`L5 = {l_brg5:.0f} mm`, `L6 = {l_brg6:.0f} mm`, `D = {d_coupling:.0f} mm`) — ล็อก LP คงที่")

            st.markdown("* **แนวดิ่ง (บน–ล่าง):**")
            v_gap_dir = "ล่าง" if delta_x_v >= 0 else "บน"
            v_ax_act = "กดท้าย Gen ลง" if delta_x_v >= 0 else "ยกท้าย Gen ขึ้น"
            v_rad_act = "ยก Gen ขึ้น" if gen_radial_corr_mm >= 0 else "กด Gen ลง"
            st.markdown(
                f"  1. ปิดช่องอ้าหน้าแปลน{v_gap_dir} (`{abs(delta_x_v):.3f} mm`): ต้อง **{v_ax_act}**\n"
                f"     - Gen Brg.5: $-\\frac{{{delta_x_v:+.3f} \\times {l_brg5:.0f}}}{{{d_coupling:.0f}}} = \\mathbf{{{-b5_ax_v:+.4f}\\text{{ mm}}}}$\n"
                f"     - Gen Brg.6: $-\\frac{{{delta_x_v:+.3f} \\times {l_brg6:.0f}}}{{{d_coupling:.0f}}} = \\mathbf{{{-b6_ax_v:+.4f}\\text{{ mm}}}}$\n"
                f"  2. แก้ Radial (ชดเชย Catenary Curve `{abs(gen_radial_corr_mm):.3f} mm`): ต้อง **{v_rad_act}** $\\mathbf{{{gen_radial_corr_mm:+.4f}\\text{{ mm}}}}$ เท่ากันทั้ง 2 จุด\n"
                f"  3. **รวมสุทธิแนวดิ่ง:**\n"
                f"     - **Gen Brg.5:** $({-b5_ax_v:+.4f}) + ({gen_radial_corr_mm:+.4f}) = \\mathbf{{{shim_b5:+.3f}\\text{{ mm}}}}$ *({'หนุนขึ้น' if shim_b5>=0 else 'ถอนออก'} {abs(shim_b5)*100:.1f} ขีด)*\n"
                f"     - **Gen Brg.6:** $({-b6_ax_v:+.4f}) + ({gen_radial_corr_mm:+.4f}) = \\mathbf{{{shim_b6:+.3f}\\text{{ mm}}}}$ *({'หนุนขึ้น' if shim_b6>=0 else 'ถอนออก'} {abs(shim_b6)*100:.1f} ขีด)*"
            )

            st.markdown("* **แนวนอน (ซ้าย–ขวา):**")
            h_gap_dir = "ซ้าย" if delta_gap_lr >= 0 else "ขวา"
            h_ax_act = "ดันท้าย Gen ไปทางขวา (`-R`)" if delta_gap_lr >= 0 else "ดันท้าย Gen ไปทางซ้าย (`+L`)"
            h_rad_act = "เลื่อน Gen ไปทางซ้าย (`+L`)" if lp_left_of_gen_mm >= 0 else "เลื่อน Gen ไปทางขวา (`-R`)"
            st.markdown(
                f"  1. ปิดช่องอ้าหน้าแปลน{h_gap_dir} (`{abs(delta_gap_lr):.3f} mm`): ต้อง **{h_ax_act}**\n"
                f"     - Gen Brg.5: $-\\frac{{{delta_gap_lr:+.3f} \\times {l_brg5:.0f}}}{{{d_coupling:.0f}}} = \\mathbf{{{-b5_ax_h:+.4f}\\text{{ mm}}}}$\n"
                f"     - Gen Brg.6: $-\\frac{{{delta_gap_lr:+.3f} \\times {l_brg6:.0f}}}{{{d_coupling:.0f}}} = \\mathbf{{{-b6_ax_h:+.4f}\\text{{ mm}}}}$\n"
                f"  2. แก้ Radial (LP เยื้อง{'ซ้าย' if lp_left_of_gen_mm >= 0 else 'ขวา'} Gen อยู่ `{abs(lp_left_of_gen_mm):.3f} mm`): ต้อง **{h_rad_act}** $\\mathbf{{{lp_left_of_gen_mm:+.4f}\\text{{ mm}}}}$ เท่ากันทั้ง 2 จุด\n"
                f"  3. **รวมสุทธิแนวนอน:**\n"
                f"     - **Gen Brg.5:** $({-b5_ax_h:+.4f}) + ({lp_left_of_gen_mm:+.4f}) = \\mathbf{{{shift_b5:+.3f}\\text{{ mm}}}}$ *({'เลื่อนไปทางซ้าย L' if shift_b5>=0 else 'เลื่อนไปทางขวา R'} {abs(shift_b5)*100:.1f} ขีด)*\n"
                f"     - **Gen Brg.6:** $({-b6_ax_h:+.4f}) + ({lp_left_of_gen_mm:+.4f}) = \\mathbf{{{shift_b6:+.3f}\\text{{ mm}}}}$ *({'เลื่อนไปทางซ้าย L' if shift_b6>=0 else 'เลื่อนไปทางขวา R'} {abs(shift_b6)*100:.1f} ขีด)*"
            )

        else:
            st.markdown(f"### 2. กรณี Solution 2: แบ่งสัดส่วนปรับร่วมกัน 50:50 (`LP Brg.4` 50% + `Gen Brg.5, 6` 50%)")
            st.markdown("* **แนวดิ่ง (บน–ล่าง) — แบ่งครึ่ง 50% ของแต่ละฝั่ง:**")
            st.markdown(
                f"  1. **LP Bearing 4 (50%):** $0.5 \\times [({lp_ax_v:+.4f}) + ({lp_radial_corr_mm:+.4f})] = \\mathbf{{{shim_b4:+.3f}\\text{{ mm}}}}$ *({'หนุนขึ้น' if shim_b4>=0 else 'ถอนออก'} {abs(shim_b4)*100:.1f} ขีด)*\n"
                f"  2. **Gen Bearing 5 (50%):** $0.5 \\times [({-b5_ax_v:+.4f}) + ({gen_radial_corr_mm:+.4f})] = \\mathbf{{{shim_b5:+.3f}\\text{{ mm}}}}$ *({'หนุนขึ้น' if shim_b5>=0 else 'ถอนออก'} {abs(shim_b5)*100:.1f} ขีด)*\n"
                f"  3. **Gen Bearing 6 (50%):** $0.5 \\times [({-b6_ax_v:+.4f}) + ({gen_radial_corr_mm:+.4f})] = \\mathbf{{{shim_b6:+.3f}\\text{{ mm}}}}$ *({'หนุนขึ้น' if shim_b6>=0 else 'ถอนออก'} {abs(shim_b6)*100:.1f} ขีด)*"
            )
            st.markdown("* **แนวนอน (ซ้าย–ขวา) — แบ่งครึ่ง 50% ของแต่ละฝั่ง:**")
            st.markdown(
                f"  1. **LP Bearing 4 (50%):** $0.5 \\times [({lp_ax_h:+.4f}) + ({-lp_left_of_gen_mm:+.4f})] = \\mathbf{{{shift_b4:+.3f}\\text{{ mm}}}}$ *({'เลื่อนซ้าย L' if shift_b4>=0 else 'เลื่อนขวา R'} {abs(shift_b4)*100:.1f} ขีด)*\n"
                f"  2. **Gen Bearing 5 (50%):** $0.5 \\times [({-b5_ax_h:+.4f}) + ({lp_left_of_gen_mm:+.4f})] = \\mathbf{{{shift_b5:+.3f}\\text{{ mm}}}}$ *({'เลื่อนซ้าย L' if shift_b5>=0 else 'เลื่อนขวา R'} {abs(shift_b5)*100:.1f} ขีด)*\n"
                f"  3. **Gen Bearing 6 (50%):** $0.5 \\times [({-b6_ax_h:+.4f}) + ({lp_left_of_gen_mm:+.4f})] = \\mathbf{{{shift_b6:+.3f}\\text{{ mm}}}}$ *({'เลื่อนซ้าย L' if shift_b6>=0 else 'เลื่อนขวา R'} {abs(shift_b6)*100:.1f} ขีด)*"
            )
