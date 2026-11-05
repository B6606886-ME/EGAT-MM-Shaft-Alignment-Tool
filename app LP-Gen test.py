"""
Streamlit Web Application: LP-Generator Coupling Alignment Precision Tool
Standard: EGAT Mae Moh Power Plant Unit 8-13
- High Legibility: No text overlapping, English-only for diagram stability
- Generator Fixed Baseline on Right side (0 level)
- Turbine Deflected & Tilted on Left side (EGAT manual standard)
- Tab 3: Connected Coupling Dial Setup Diagram (Gen - LP, G1, G2, Rim) & Simulated Targets
"""

from typing import Tuple
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
import streamlit as st

# Page Configuration
st.set_page_config(
    page_title="EGAT MM 8-13 Alignment Precision Tool",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Power Plant Industrial Styling
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #0A192F 0%, #172A45 100%);
        padding: 18px 24px;
        border-radius: 12px;
        color: #FFFFFF;
        margin-bottom: 20px;
        border-left: 6px solid #FF9800;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }
    .main-header h1 {
        color: #FFFFFF;
        font-size: 24px;
        margin: 0;
        font-weight: 700;
    }
    .main-header p {
        color: #B0BEC5;
        font-size: 13.5px;
        margin: 4px 0 0 0;
    }
    .stButton>button {
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.2s ease;
    }
</style>
""", unsafe_allow_html=True)

TARGET_RADIAL_OFFSET = -0.10
TARGET_AXIAL_GAP = 0.00
TOLERANCE_LIMIT = 0.02

# =========================================================================
# Session State Management
# =========================================================================
if 'confirmed_step1' not in st.session_state: st.session_state.confirmed_step1 = False
if 'confirmed_step2' not in st.session_state: st.session_state.confirmed_step2 = False
if 'confirmed_step3' not in st.session_state: st.session_state.confirmed_step3 = False
if 'is_calculated' not in st.session_state: st.session_state.is_calculated = False

if 'd_coupling' not in st.session_state: st.session_state.d_coupling = None
if 'l_brg4' not in st.session_state: st.session_state.l_brg4 = None
if 'l_gen_f' not in st.session_state: st.session_state.l_gen_f = None
if 'l_gen_m' not in st.session_state: st.session_state.l_gen_m = None
if 'l_gen_r' not in st.session_state: st.session_state.l_gen_r = None

if 'r_top' not in st.session_state: st.session_state.r_top = None
if 'r_bottom' not in st.session_state: st.session_state.r_bottom = None
if 'r_left' not in st.session_state: st.session_state.r_left = None
if 'r_right' not in st.session_state: st.session_state.r_right = None

for ang in ['0', '90', '180', '270']:
    if f'g1_{ang}' not in st.session_state: st.session_state[f'g1_{ang}'] = None
    if f'g2_{ang}' not in st.session_state: st.session_state[f'g2_{ang}'] = None

if 'solution_choice' not in st.session_state: st.session_state.solution_choice = '1'


# =========================================================================
# Helper Functions
# =========================================================================
def validate_dial(top: float, bottom: float, left: float, right: float, tol: float = 0.02) -> Tuple[bool, float]:
    diff = abs((top + bottom) - (left + right))
    return diff <= tol, diff


def draw_single_dial(ax, title, t_val, b_val, l_val, r_val, dial_color):
    ax.set_aspect('equal')
    ax.set_xlim(-1.8, 1.8)
    ax.set_ylim(-1.8, 1.8)
    ax.axis('off')

    circle = patches.Circle((0, 0), 1.0, edgecolor=dial_color, facecolor='#FAFAFA', linewidth=2.5)
    ax.add_patch(circle)
    ax.text(0, 0, title, ha='center', va='center', fontsize=11, fontweight='bold', color=dial_color)

    arc = patches.Arc((0, 0), 1.45, 1.45, angle=0, theta1=30, theta2=110, color='gray', linestyle='--', linewidth=1.5)
    ax.add_patch(arc)
    ax.annotate("", xy=(-0.25, 0.70), xytext=(-0.15, 0.72), arrowprops=dict(arrowstyle="->", color="gray", lw=1.5))

    t_str = f"{t_val:+.3f}" if t_val is not None else "--"
    b_str = f"{b_val:+.3f}" if b_val is not None else "--"
    l_str = f"{l_val:+.3f}" if l_val is not None else "--"
    r_str = f"{r_val:+.3f}" if r_val is not None else "--"

    ax.text(0, 1.22, f"Top (T)\n{t_str}", ha='center', va='bottom', fontsize=10, fontweight='bold')
    ax.text(0, -1.22, f"{b_str}\nBottom (B)", ha='center', va='top', fontsize=10, fontweight='bold')
    ax.text(-1.22, 0, f"Left (L)\n{l_str}", ha='right', va='center', fontsize=10, fontweight='bold')
    ax.text(1.22, 0, f"Right (R)\n{r_str}", ha='left', va='center', fontsize=10, fontweight='bold')


def draw_coupling_physical_setup(ax, choice: str):
    """Draw physical coupling dial configuration with fully connected bracket."""
    ax.set_aspect('equal')
    ax.set_xlim(-1.5, 8.0)
    ax.set_ylim(-3.5, 3.8)
    ax.axis('off')

    # Generator (Left)
    ax.add_patch(patches.Rectangle((-1.0, -0.6), 2.4, 1.2, facecolor='#E65100', edgecolor='#5D2000', linewidth=2.5))
    ax.add_patch(patches.Rectangle((1.4, -1.6), 0.8, 3.2, facecolor='#E65100', edgecolor='#5D2000', linewidth=2.5))
    ax.text(0.2, 0.0, "Gen", ha='center', va='center', color='white', fontsize=16, fontweight='bold')

    # Turbine LP (Right)
    ax.add_patch(patches.Rectangle((4.6, -0.6), 2.4, 1.2, facecolor='#E65100', edgecolor='#5D2000', linewidth=2.5))
    ax.add_patch(patches.Rectangle((3.8, -1.6), 0.8, 3.2, facecolor='#E65100', edgecolor='#5D2000', linewidth=2.5))
    ax.text(5.8, 0.0, "LP", ha='center', va='center', color='white', fontsize=16, fontweight='bold')

    # 1. Radial Rim Gauge Bracket (เชื่อมต่อสมบูรณ์ ไม่ขาด)
    rim_x = 4.2
    rim_y = 2.2
    rim_r = 0.45
    # ลากเส้นจากหน้าแปลน Gen ขึ้นไป -> หักฉากขวา -> ต่อสนิทเข้าขอบบนหน้าปัดที่ (rim_x, rim_y + rim_r)
    ax.plot([1.8, 1.8, rim_x, rim_x], [1.6, 3.1, 3.1, rim_y + rim_r], color='#5D2000', lw=2.5)
    
    # หน้าปัดเกจ Rim
    ax.add_patch(patches.Circle((rim_x, rim_y), rim_r, facecolor='#E65100', edgecolor='#5D2000', lw=2.5))
    # ก้านวัดลงมาแตะที่หน้าแปลน LP
    ax.annotate("", xy=(rim_x, 1.6), xytext=(rim_x, rim_y - rim_r), arrowprops=dict(arrowstyle="->", color="#5D2000", lw=2.5))
    ax.text(4.9, rim_y, "Rim (Radial)\n[Offset = 2x]", fontsize=10, fontweight='bold', color='#5D2000', va='center')

    # 2. Axial Gauge G1 (Top)
    ax.plot([2.2, 2.55], [0.55, 0.55], color='#5D2000', lw=2.5)
    ax.add_patch(patches.Circle((3.0, 0.55), 0.45, facecolor='#E65100', edgecolor='#5D2000', lw=2.5))
    ax.annotate("", xy=(3.8, 0.55), xytext=(3.45, 0.55), arrowprops=dict(arrowstyle="->", color="#5D2000", lw=2.5))
    ax.text(3.0, 1.2, "G1", ha='center', va='bottom', fontsize=13, fontweight='bold', color='#5D2000')

    # 3. Axial Gauge G2 (Bottom)
    ax.plot([2.2, 2.55], [-0.85, -0.85], color='#5D2000', lw=2.5)
    ax.add_patch(patches.Circle((3.0, -0.85), 0.45, facecolor='#E65100', edgecolor='#5D2000', lw=2.5))
    ax.annotate("", xy=(3.8, -0.85), xytext=(3.45, -0.85), arrowprops=dict(arrowstyle="->", color="#5D2000", lw=2.5))
    ax.text(3.0, -1.5, "G2", ha='center', va='top', fontsize=13, fontweight='bold', color='#5D2000')

    if choice == '1':
        status_txt = (
            "[SOLUTION 1: LP Bearing 4 Only]\n"
            "* Generator is 100% FIXED (Baseline Reference)\n"
            "* Adjust shims ONLY at LP Brg.4 to correct Gap and Offset"
        )
        bg_col = "#E8F5E9"
        bdr_col = "#2E7D32"
    elif choice == '2':
        status_txt = (
            "[SOLUTION 2: Shared Adjustment (50:50)]\n"
            "* Shared correction: LP Brg.4 + Generator 6 Legs\n"
            "* Both LP and Generator move towards centerline"
        )
        bg_col = "#FFFDE7"
        bdr_col = "#F57F17"
    else:
        status_txt = (
            "[SOLUTION 3: Generator 6 Legs Only]\n"
            "* Turbine/LP is 100% FIXED\n"
            "* Adjust shims ONLY at Generator 6 Legs to meet LP shaft"
        )
        bg_col = "#FFEBEE"
        bdr_col = "#C62828"

    ax.text(3.0, -2.5, status_txt, ha='center', va='center', fontsize=11, fontweight='bold',
            bbox=dict(boxstyle='round,pad=0.6', facecolor=bg_col, edgecolor=bdr_col, lw=1.8))


# =========================================================================
# Application Header
# =========================================================================
st.markdown("""
<div class="main-header">
    <h1>Shaft Alignment Precision & Simulation System</h1>
    <p>EGAT Mae Moh Power Plant Unit 8-13 | LP - Generator Precision Tool (Fixed Generator Standard)</p>
</div>
""", unsafe_allow_html=True)

step_cols = st.columns(4)
step_cols[0].markdown(f"**1. Machine Dimensions:** {'✅ Confirmed' if st.session_state.confirmed_step1 else '⏳ Pending'}")
step_cols[1].markdown(f"**2. Radial Gauge (Rim):** {'✅ Confirmed' if st.session_state.confirmed_step2 else '⏳ Pending'}")
step_cols[2].markdown(f"**3. Axial Gauge (Face):** {'✅ Confirmed' if st.session_state.confirmed_step3 else '⏳ Pending'}")
step_cols[3].markdown(f"**4. Calculation:** {'⚡ Completed' if st.session_state.is_calculated else '⏳ Pending'}")
st.write("---")

col_input, col_view = st.columns([1.15, 1.85], gap="large")

with col_input:
    # Step 1
    with st.expander("📍 Step 1: Machine Geometry (LP - Generator)", expanded=not st.session_state.confirmed_step1):
        d_val = st.number_input("Coupling Flange Diameter D (mm)", value=st.session_state.d_coupling, placeholder="e.g., 800.0", format="%.1f", disabled=st.session_state.confirmed_step1)
        b4_val = st.number_input("Distance to LP Brg.4 (mm)", value=st.session_state.l_brg4, placeholder="e.g., 550.0", format="%.1f", disabled=st.session_state.confirmed_step1)
        gf_val = st.number_input("Distance to Gen Front Leg (mm)", value=st.session_state.l_gen_f, placeholder="e.g., 1850.0", format="%.1f", disabled=st.session_state.confirmed_step1)
        gm_val = st.number_input("Distance to Gen Mid Leg (mm)", value=st.session_state.l_gen_m, placeholder="e.g., 3890.0", format="%.1f", disabled=st.session_state.confirmed_step1)
        gr_val = st.number_input("Distance to Gen Rear Leg (mm)", value=st.session_state.l_gen_r, placeholder="e.g., 5150.0", format="%.1f", disabled=st.session_state.confirmed_step1)

        btn1, btn2 = st.columns(2)
        if not st.session_state.confirmed_step1:
            if btn1.button("Confirm Dimensions ➔", type="primary", use_container_width=True):
                if None in [d_val, b4_val, gf_val, gm_val, gr_val]:
                    st.error("Please fill in all machine geometry fields.")
                else:
                    st.session_state.d_coupling = float(d_val)
                    st.session_state.l_brg4 = float(b4_val)
                    st.session_state.l_gen_f = float(gf_val)
                    st.session_state.l_gen_m = float(gm_val)
                    st.session_state.l_gen_r = float(gr_val)
                    st.session_state.confirmed_step1 = True
                    st.rerun()
        else:
            if btn2.button("✏️ Edit Dimensions", use_container_width=True):
                st.session_state.confirmed_step1 = False
                st.session_state.is_calculated = False
                st.rerun()

    # Step 2
    with st.expander("📍 Step 2: Radial Rim Gauge Readings", expanded=(st.session_state.confirmed_step1 and not st.session_state.confirmed_step2)):
        r1, r2 = st.columns(2)
        with r1:
            rt_val = st.number_input("Top (T) mm", value=st.session_state.r_top, placeholder="e.g., 0.000", format="%.3f", disabled=st.session_state.confirmed_step2)
            rl_val = st.number_input("Left (L) mm", value=st.session_state.r_left, placeholder="e.g., -0.200", format="%.3f", disabled=st.session_state.confirmed_step2)
        with r2:
            rb_val = st.number_input("Bottom (B) mm", value=st.session_state.r_bottom, placeholder="e.g., -0.310", format="%.3f", disabled=st.session_state.confirmed_step2)
            rr_val = st.number_input("Right (R) mm", value=st.session_state.r_right, placeholder="e.g., -0.120", format="%.3f", disabled=st.session_state.confirmed_step2)

        btn1, btn2 = st.columns(2)
        if not st.session_state.confirmed_step2:
            if btn1.button("Confirm Rim Values ➔", type="primary", use_container_width=True):
                if None in [rt_val, rb_val, rl_val, rr_val]:
                    st.error("Please fill in all 4 radial gauge positions.")
                else:
                    r_pass, r_err = validate_dial(rt_val, rb_val, rl_val, rr_val, TOLERANCE_LIMIT)
                    st.session_state.r_top = float(rt_val)
                    st.session_state.r_bottom = float(rb_val)
                    st.session_state.r_left = float(rl_val)
                    st.session_state.r_right = float(rr_val)
                    st.session_state.confirmed_step2 = True
                    if not r_pass:
                        st.warning(f"Warning: |(T+B)-(L+R)| = {r_err:.3f} mm exceeds tolerance (0.02 mm).")
                    st.rerun()
        else:
            if btn2.button("✏️ Edit Rim Values", use_container_width=True):
                st.session_state.confirmed_step2 = False
                st.session_state.is_calculated = False
                st.rerun()

    # Step 3
    with st.expander("📍 Step 3: Axial Slice Gauge Readings", expanded=(st.session_state.confirmed_step2 and not st.session_state.confirmed_step3)):
        st.caption("Dual dial gauge method: Formula = (Gauge 1 - Gauge 2) / 2")
        f1, f2 = st.columns(2)
        with f1:
            g1_0_val = st.number_input("Face 0° (Top) Gauge 1", value=st.session_state.g1_0, placeholder="e.g., 14.95", format="%.3f", disabled=st.session_state.confirmed_step3)
            g2_0_val = st.number_input("Face 0° (Top) Gauge 2", value=st.session_state.g2_0, placeholder="e.g., 14.96", format="%.3f", disabled=st.session_state.confirmed_step3)
            g1_90_val = st.number_input("Face 90° (Left) Gauge 1", value=st.session_state.g1_90, placeholder="e.g., 14.96", format="%.3f", disabled=st.session_state.confirmed_step3)
            g2_90_val = st.number_input("Face 90° (Left) Gauge 2", value=st.session_state.g2_90, placeholder="e.g., 14.95", format="%.3f", disabled=st.session_state.confirmed_step3)
        with f2:
            g1_180_val = st.number_input("Face 180° (Bottom) Gauge 1", value=st.session_state.g1_180, placeholder="e.g., 14.97", format="%.3f", disabled=st.session_state.confirmed_step3)
            g2_180_val = st.number_input("Face 180° (Bottom) Gauge 2", value=st.session_state.g2_180, placeholder="e.g., 14.96", format="%.3f", disabled=st.session_state.confirmed_step3)
            g1_270_val = st.number_input("Face 270° (Right) Gauge 1", value=st.session_state.g1_270, placeholder="e.g., 14.98", format="%.3f", disabled=st.session_state.confirmed_step3)
            g2_270_val = st.number_input("Face 270° (Right) Gauge 2", value=st.session_state.g2_270, placeholder="e.g., 15.00", format="%.3f", disabled=st.session_state.confirmed_step3)

        btn1, btn2 = st.columns(2)
        if not st.session_state.confirmed_step3:
            if btn1.button("Confirm Face Values ➔", type="primary", use_container_width=True):
                check_face = [g1_0_val, g2_0_val, g1_90_val, g2_90_val, g1_180_val, g2_180_val, g1_270_val, g2_270_val]
                if None in check_face:
                    st.error("Please fill in all 4 axial gauge positions.")
                else:
                    st.session_state.g1_0 = float(g1_0_val); st.session_state.g2_0 = float(g2_0_val)
                    st.session_state.g1_90 = float(g1_90_val); st.session_state.g2_90 = float(g2_90_val)
                    st.session_state.g1_180 = float(g1_180_val); st.session_state.g2_180 = float(g2_180_val)
                    st.session_state.g1_270 = float(g1_270_val); st.session_state.g2_270 = float(g2_270_val)
                    st.session_state.confirmed_step3 = True
                    st.rerun()
        else:
            if btn2.button("✏️ Edit Face Values", use_container_width=True):
                st.session_state.confirmed_step3 = False
                st.session_state.is_calculated = False
                st.rerun()

    # Step 4
    with st.expander("📍 Step 4: Adjustment Strategy & Execution", expanded=st.session_state.confirmed_step3):
        sol_options = [
            "Solution 1: Adjust LP Brg.4 Only (Generator 100% Fixed) - Recommended",
            "Solution 2: Shared Adjustment (LP Brg.4 + Generator 6 Legs, 50:50)",
            "Solution 3: Adjust Generator 6 Legs Only (Turbine 100% Fixed)"
        ]
        sol_choice = st.radio("Select Alignment Strategy:", sol_options, index=int(st.session_state.solution_choice) - 1)
        st.session_state.solution_choice = sol_choice[9]

        st.write("")
        if st.button("⚡ Calculate & Process Shims", type="primary", use_container_width=True):
            if not (st.session_state.confirmed_step1 and st.session_state.confirmed_step2 and st.session_state.confirmed_step3):
                st.error("⚠️ Please confirm Steps 1, 2, and 3 before running calculation.")
            else:
                st.session_state.is_calculated = True
                st.success("✅ Alignment calculation complete.")
                st.rerun()

    if st.button("🔄 Reset All Data", use_container_width=True):
        for k in list(st.session_state.keys()):
            del st.session_state[k]
        st.rerun()


# =========================================================================
# Output View & Tab Routing
# =========================================================================
with col_view:
    a_top = (st.session_state.g1_0 - st.session_state.g2_0) / 2.0 if st.session_state.confirmed_step3 else None
    a_bottom = (st.session_state.g1_180 - st.session_state.g2_180) / 2.0 if st.session_state.confirmed_step3 else None
    a_left = (st.session_state.g1_90 - st.session_state.g2_90) / 2.0 if st.session_state.confirmed_step3 else None
    a_right = (st.session_state.g1_270 - st.session_state.g2_270) / 2.0 if st.session_state.confirmed_step3 else None

    if st.session_state.is_calculated:
        delta_x_v = (a_bottom - a_top) - TARGET_AXIAL_GAP
        actual_offset_v = (st.session_state.r_bottom - st.session_state.r_top) / 2.0
        delta_y_v = actual_offset_v - TARGET_RADIAL_OFFSET

        delta_x_h = (a_right - a_left) - 0.00
        actual_offset_h = (st.session_state.r_right - st.session_state.r_left) / 2.0
        delta_y_h = actual_offset_h - 0.00

        lift_brg4 = - (delta_x_v * st.session_state.l_brg4) / st.session_state.d_coupling

        if st.session_state.solution_choice == '1':
            shim_b4 = lift_brg4 + delta_y_v
            shim_f = shim_m = shim_r = 0.0
        elif st.session_state.solution_choice == '2':
            alpha = 0.5
            shim_b4 = (lift_brg4 * (1 - alpha)) + (delta_y_v * (1 - alpha))
            shim_f = ((alpha * delta_x_v * st.session_state.l_gen_f) / st.session_state.d_coupling) + (alpha * delta_y_v)
            shim_m = ((alpha * delta_x_v * st.session_state.l_gen_m) / st.session_state.d_coupling) + (alpha * delta_y_v)
            shim_r = ((alpha * delta_x_v * st.session_state.l_gen_r) / st.session_state.d_coupling) + (alpha * delta_y_v)
        else:
            shim_b4 = 0.0
            shim_f = ((delta_x_v * st.session_state.l_gen_f) / st.session_state.d_coupling) + delta_y_v
            shim_m = ((delta_x_v * st.session_state.l_gen_m) / st.session_state.d_coupling) + delta_y_v
            shim_r = ((delta_x_v * st.session_state.l_gen_r) / st.session_state.d_coupling) + delta_y_v

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Vertical Gap (ΔX)", f"{delta_x_v:+.3f} mm", "Bottom OPEN" if delta_x_v > 0 else "Bottom CLOSED")
        m2.metric("Vertical Offset (ΔY)", f"{delta_y_v:+.3f} mm", "Gen HIGHER than Target" if delta_y_v > 0 else "Gen LOWER than Target")
        m3.metric("LP Brg.4 Shim", f"{shim_b4:+.3f} mm", "Add Shim (+)" if shim_b4 > 0 else ("Remove Shim (-)" if shim_b4 < 0 else "Fixed"))
        m4.metric("Horizontal Offset", f"{delta_y_h:+.3f} mm", "Shifted RIGHT" if delta_y_h > 0 else "Shifted LEFT")

    view_tab1, view_tab2, view_tab3 = st.tabs([
        "📋 Inspection Sheet & Dial Report",
        "📐 Deflection Diagrams & Shim Action",
        "🔍 Solution Dial Setup & Measurement Diagram"
    ])

    # Tab 1
    with view_tab1:
        st.subheader("Inspection Sheet & Dial Gauges (EGAT Mae Moh Power Plant Unit 8-13)")
        fig1 = plt.figure(figsize=(14, 7))

        ax_d_face_before = fig1.add_subplot(2, 2, 1)
        draw_single_dial(ax_d_face_before, "Axial (Face) Before", a_top, a_bottom, a_left, a_right, '#B22222')

        ax_d_rim_before = fig1.add_subplot(2, 2, 2)
        draw_single_dial(ax_d_rim_before, "Radial (Rim) Before", st.session_state.r_top, st.session_state.r_bottom, st.session_state.r_left, st.session_state.r_right, '#B22222')

        ax_d_face_after = fig1.add_subplot(2, 2, 3)
        draw_single_dial(ax_d_face_after, "Axial (Face) Target", 0.0, TARGET_AXIAL_GAP, 0.0, 0.0, '#006400')

        ax_d_rim_after = fig1.add_subplot(2, 2, 4)
        draw_single_dial(ax_d_rim_after, "Radial (Rim) Target", 0.0, 2.0 * TARGET_RADIAL_OFFSET, TARGET_RADIAL_OFFSET, TARGET_RADIAL_OFFSET, '#006400')

        fig1.text(0.08, 0.02, 
                 f"Measurement Tool: Axial: Slice gauge (Formula: (G1 - G2)/2) | Radial: Dial gauge\n"
                 f"Criteria Standard: Look to Generator | R, A <= 0.02 mm | Offset Target: Generator {TARGET_RADIAL_OFFSET:+.2f} mm | Standard: EGAT Mae Moh Unit 8-13",
                 fontsize=10, style='italic', bbox=dict(boxstyle='round,pad=0.5', facecolor='#F5F5F5', edgecolor='gray'))

        plt.tight_layout(rect=[0, 0.06, 1, 0.95])
        st.pyplot(fig1)

    # Tab 2: Deflection Diagrams with Anti-Collision Scaling
    with view_tab2:
        if not st.session_state.is_calculated:
            st.info("💡 Please complete Steps 1–3 and click '⚡ Calculate & Process Shims' to generate deflection diagrams.")
        else:
            fig2, (ax_side, ax_top, ax_bar) = plt.subplots(
                3, 1, figsize=(15, 12.5), gridspec_kw={'height_ratios': [1.2, 1.2, 0.85]}
            )
            fig2.subplots_adjust(top=0.90, bottom=0.08, hspace=0.48, left=0.08, right=0.96)
            fig2.suptitle(f"FIELD ALIGNMENT DIAGRAMS & SHIM ACTION - [SOLUTION {st.session_state.solution_choice}] (Generator as Reference)",
                          fontsize=13.5, fontweight='bold', color='#0D47A1', y=0.96)

            flange_h = 2.0
            gap_x = 420.0
            gen_end_x = float(st.session_state.l_gen_r) + 400.0

            def draw_alignment_plane(ax, title, delta_x, delta_y, is_vertical=True):
                ax.axhline(0, color='gray', linestyle='--', linewidth=1.5)

                gen_x = np.array([gap_x, gap_x + st.session_state.l_gen_f, gap_x + st.session_state.l_gen_m, gap_x + st.session_state.l_gen_r, gen_end_x])
                ax.plot(gen_x, np.zeros_like(gen_x), color='#1565C0', linewidth=4.5)
                ax.plot([gap_x, gap_x], [-flange_h, flange_h], color='#0D47A1', linewidth=5.5)
                ax.text(gap_x + st.session_state.l_gen_m / 2, 1.6, "GENERATOR (FIXED BASELINE)", ha='center', fontsize=11, fontweight='bold', color='#1565C0')

                gen_legs = [
                    (gap_x + st.session_state.l_gen_f, f"Gen-F\n(L={st.session_state.l_gen_f:.0f})"),
                    (gap_x + st.session_state.l_gen_m, f"Gen-M\n(L={st.session_state.l_gen_m:.0f})"),
                    (gap_x + st.session_state.l_gen_r, f"Gen-R\n(L={st.session_state.l_gen_r:.0f})")
                ]
                for gx, glabel in gen_legs:
                    ax.plot([gx, gx], [-0.6, 0.0], color='#0D47A1', linewidth=2.5)
                    ax.scatter([gx], [-0.6], s=120, marker='s', color='#0D47A1', zorder=5)
                    ax.text(gx, -0.9, glabel, ha='center', va='top', fontsize=9.5, fontweight='bold')

                vis_offset = 0.70 if delta_y < 0 else -0.70
                turb_center_y = vis_offset

                tilt_dir = 1.0 if delta_x >= 0 else -1.0
                tilt_x = tilt_dir * 50.0

                fl_top_x = 0.0 + tilt_x
                fl_top_y = turb_center_y + flange_h
                fl_bot_x = 0.0 - tilt_x
                fl_bot_y = turb_center_y - flange_h

                ax.plot([fl_top_x, fl_bot_x], [fl_top_y, fl_bot_y], color='#BF360C', linewidth=5.5)

                brg_x = -float(st.session_state.l_brg4)
                turb_end_x = brg_x - 200.0
                turb_brg_y = turb_center_y - (tilt_dir * 0.45)
                turb_end_y = turb_center_y - (tilt_dir * 0.65)

                ax.plot([turb_end_x, 0.0], [turb_end_y, turb_center_y], color='#D84315', linewidth=4.5)
                ax.text(brg_x / 2, turb_center_y + 0.5, "TURBINE (LP)", ha='center', fontsize=11, fontweight='bold', color='#D84315')

                ax.plot([brg_x, brg_x], [turb_brg_y - 0.6, turb_brg_y], color='#4E342E', linewidth=3)
                ax.scatter([brg_x], [turb_brg_y - 0.6], s=140, marker='^', color='#4E342E', zorder=5)
                ax.text(brg_x, turb_brg_y - 0.9, f"LP Brg.4\n(L={st.session_state.l_brg4:.0f} mm)", ha='center', va='top', fontsize=9.5, fontweight='bold')

                lbl_top = "T" if is_vertical else "L"
                lbl_bot = "B" if is_vertical else "R"
                ax.text(fl_top_x - 90, fl_top_y, lbl_top, fontsize=12, fontweight='bold', color='#BF360C')
                ax.text(fl_bot_x - 90, fl_bot_y, lbl_bot, fontsize=12, fontweight='bold', color='#BF360C')

                # Gap measurement indicator
                gap_y = fl_top_y if delta_x >= 0 else fl_bot_y
                meas_x = fl_top_x if delta_x >= 0 else fl_bot_x
                ax.plot([meas_x, gap_x], [gap_y + 0.35, gap_y + 0.35], color='purple', linestyle='-', lw=1.8)
                ax.plot([meas_x, meas_x], [gap_y, gap_y + 0.50], color='purple', lw=1.5)
                ax.plot([gap_x, gap_x], [gap_y, gap_y + 0.50], color='purple', lw=1.5)
                ax.text((meas_x + gap_x) / 2.0, gap_y + 0.55, f"Gap (ΔX) = {delta_x:+.3f} mm", ha='center', va='bottom', fontsize=9.5, fontweight='bold', color='purple',
                        bbox=dict(boxstyle='round,pad=0.25', facecolor='#F3E5F5', edgecolor='purple', alpha=0.9))

                # Offset measurement indicator
                mid_dim_x = gap_x / 2.0
                ax.plot([0.0, gap_x], [turb_center_y, turb_center_y], color='brown', linestyle=':', lw=1.5)
                ax.annotate("", xy=(mid_dim_x, 0.0), xytext=(mid_dim_x, turb_center_y),
                            arrowprops=dict(arrowstyle="<->", color="brown", lw=2.0))
                ax.text(mid_dim_x + 30, turb_center_y / 2.0, f"Offset (ΔY) = {delta_y:+.3f} mm", ha='left', va='center', fontsize=9.5, fontweight='bold', color='brown',
                        bbox=dict(boxstyle='round,pad=0.25', facecolor='#FFF8E1', edgecolor='brown', alpha=0.9))

                ax.set_title(title, fontsize=11.5, fontweight='bold', pad=14)
                ax.set_xlim(-float(st.session_state.l_brg4) - 300, gen_end_x + 250)
                ax.set_ylim(-3.0, 3.8)
                ax.set_yticks([-2, 0, 2])
                if is_vertical:
                    ax.set_ylabel("Vertical Deflection\n(Exaggerated)", fontsize=10, fontweight='bold')
                    ax.set_yticklabels(["- (Down)", "0 (Gen Ref)", "+ (Up)"], fontsize=9.5)
                else:
                    ax.set_ylabel("Horizontal Shift\n(Exaggerated)", fontsize=10, fontweight='bold')
                    ax.set_yticklabels(["- (Left)", "0 (Gen Ref)", "+ (Right)"], fontsize=9.5)
                ax.grid(True, linestyle=':', alpha=0.5)

            draw_alignment_plane(ax_side, "1. SIDE VIEW (Vertical Plane: Turbine relative to Fixed Generator)", delta_x_v, delta_y_v, is_vertical=True)
            draw_alignment_plane(ax_top, "2. TOP VIEW (Horizontal Plane: Turbine relative to Fixed Generator)", delta_x_h, delta_y_h, is_vertical=False)

            labels = ["LP Bearing 4", "Gen Front (1,2)", "Gen Mid (3,4)", "Gen Rear (5,6)"]
            shims = [shim_b4, shim_f, shim_m, shim_r]
            colors = ['#2E7D32' if s > 0 else ('#C62828' if s < 0 else '#9E9E9E') for s in shims]

            bars = ax_bar.bar(labels, shims, color=colors, width=0.4, edgecolor='black', zorder=3)
            ax_bar.axhline(0, color='black', linewidth=1.2)
            ax_bar.set_ylabel("Shim (mm)", fontsize=10, fontweight='bold')
            ax_bar.set_title(f"3. Field Shim Action Required for [SOLUTION {st.session_state.solution_choice}]", fontsize=11.5, fontweight='bold', pad=8)
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

    # Tab 3: Solution Dial Setup & Measurement Diagram
    with view_tab3:
        if not st.session_state.is_calculated:
            st.info("💡 Please complete Steps 1–3 and click '⚡ Calculate & Process Shims' to inspect gauge setup and simulation.")
        else:
            st.subheader(f"Coupling Setup & Expected Measurement for [SOLUTION {st.session_state.solution_choice}]")
            
            fig3 = plt.figure(figsize=(15, 9.8))
            
            # Diagram: Physical Coupling Setup
            ax_setup = fig3.add_subplot(2, 2, (1, 2))
            draw_coupling_physical_setup(ax_setup, st.session_state.solution_choice)

            # Simulated Target Dials (Cleaned Spacing)
            ax_exp_face = fig3.add_subplot(2, 2, 3)
            draw_single_dial(ax_exp_face, "Expected Axial (Face)", 0.000, TARGET_AXIAL_GAP, 0.000, 0.000, '#006400')
            ax_exp_face.text(0, -1.75, f"Strategy: Solution {st.session_state.solution_choice}\nAxial Gap = 0.000 mm", 
                             ha='center', va='top', fontsize=10, fontweight='bold', color='#006400')

            ax_exp_rim = fig3.add_subplot(2, 2, 4)
            draw_single_dial(ax_exp_rim, "Expected Radial (Rim)", 0.000, 2.0 * TARGET_RADIAL_OFFSET, TARGET_RADIAL_OFFSET, TARGET_RADIAL_OFFSET, '#006400')
            ax_exp_rim.text(0, -1.75, f"Offset = -0.100 mm (Gen Down)\nDial Bottom = {2.0 * TARGET_RADIAL_OFFSET:+.3f} mm", 
                            ha='center', va='top', fontsize=10, fontweight='bold', color='#006400')

            plt.subplots_adjust(top=0.96, bottom=0.12, hspace=0.38)
            st.pyplot(fig3)
