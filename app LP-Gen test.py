"""
Streamlit Web Application: LP-Generator Coupling Alignment Precision Tool
Standard: EGAT Mae Moh Power Plant Unit 8-13
- Entire interface in English
- Facility title: "EGAT Mae Moh Power Plant Unit 8-13"
- Step-by-step confirmation & edit buttons for every step
- Dedicated "Calculate & Process Shims" button on the final step
- Default blank input fields
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

# Standard Maintenance Criteria for EGAT Mae Moh Unit 8-13
TARGET_RADIAL_OFFSET = -0.10  # Generator down 0.10 mm (-0.10 mm)
TARGET_AXIAL_GAP = 0.00       # Coupling faces parallel
TOLERANCE_LIMIT = 0.02        # Dial acceptance tolerance <= 0.02 mm

# =========================================================================
# Session State Management
# =========================================================================
if 'confirmed_step1' not in st.session_state: st.session_state.confirmed_step1 = False
if 'confirmed_step2' not in st.session_state: st.session_state.confirmed_step2 = False
if 'confirmed_step3' not in st.session_state: st.session_state.confirmed_step3 = False
if 'is_calculated' not in st.session_state: st.session_state.is_calculated = False

# Machine Dimensions
if 'd_coupling' not in st.session_state: st.session_state.d_coupling = None
if 'l_brg4' not in st.session_state: st.session_state.l_brg4 = None
if 'l_gen_f' not in st.session_state: st.session_state.l_gen_f = None
if 'l_gen_m' not in st.session_state: st.session_state.l_gen_m = None
if 'l_gen_r' not in st.session_state: st.session_state.l_gen_r = None

# Radial Rim Gauge Readings
if 'r_top' not in st.session_state: st.session_state.r_top = None
if 'r_bottom' not in st.session_state: st.session_state.r_bottom = None
if 'r_left' not in st.session_state: st.session_state.r_left = None
if 'r_right' not in st.session_state: st.session_state.r_right = None

# Axial Face Gauge Readings
for ang in ['0', '90', '180', '270']:
    if f'g1_{ang}' not in st.session_state: st.session_state[f'g1_{ang}'] = None
    if f'g2_{ang}' not in st.session_state: st.session_state[f'g2_{ang}'] = None

# Adjustment Strategy
if 'solution_choice' not in st.session_state: st.session_state.solution_choice = '1'


# =========================================================================
# Calculation & Visualization Functions
# =========================================================================
def validate_dial(top: float, bottom: float, left: float, right: float, tol: float = 0.02) -> Tuple[bool, float]:
    diff = abs((top + bottom) - (left + right))
    return diff <= tol, diff


def draw_single_dial(ax, title, t_val, b_val, l_val, r_val, dial_color):
    ax.set_aspect('equal')
    ax.set_xlim(-1.6, 1.6)
    ax.set_ylim(-1.6, 1.6)
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

    ax.text(0, 1.18, f"Top (T)\n{t_str}", ha='center', va='bottom', fontsize=9.5, fontweight='bold')
    ax.text(0, -1.18, f"{b_str}\nBottom (B)", ha='center', va='top', fontsize=9.5, fontweight='bold')
    ax.text(-1.18, 0, f"Left (L)\n{l_str}", ha='right', va='center', fontsize=9.5, fontweight='bold')
    ax.text(1.18, 0, f"Right (R)\n{r_str}", ha='left', va='center', fontsize=9.5, fontweight='bold')


# =========================================================================
# APPLICATION HEADER
# =========================================================================
st.markdown("""
<div class="main-header">
    <h1>Shaft Alignment Precision & Simulation System</h1>
    <p>EGAT Mae Moh Power Plant Unit 8-13 | LP - Generator Precision Tool (Fixed Generator Standard)</p>
</div>
""", unsafe_allow_html=True)

# Step Progress Bar
step_cols = st.columns(4)
step_cols[0].markdown(f"**1. Machine Dimensions:** {'✅ Confirmed' if st.session_state.confirmed_step1 else '⏳ Pending'}")
step_cols[1].markdown(f"**2. Radial Gauge (Rim):** {'✅ Confirmed' if st.session_state.confirmed_step2 else '⏳ Pending'}")
step_cols[2].markdown(f"**3. Axial Gauge (Face):** {'✅ Confirmed' if st.session_state.confirmed_step3 else '⏳ Pending'}")
step_cols[3].markdown(f"**4. Calculation:** {'⚡ Completed' if st.session_state.is_calculated else '⏳ Pending'}")
st.write("---")

# =========================================================================
# Main Layout: 2 Columns
# =========================================================================
col_input, col_view = st.columns([1.15, 1.85], gap="large")

with col_input:
    # ---------------------------------------------------------------------
    # Step 1: Machine Dimensions
    # ---------------------------------------------------------------------
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
                    st.session_state.d_coupling = d_val
                    st.session_state.l_brg4 = b4_val
                    st.session_state.l_gen_f = gf_val
                    st.session_state.l_gen_m = gm_val
                    st.session_state.l_gen_r = gr_val
                    st.session_state.confirmed_step1 = True
                    st.rerun()
        else:
            if btn2.button("✏️ Edit Dimensions", use_container_width=True):
                st.session_state.confirmed_step1 = False
                st.session_state.is_calculated = False
                st.rerun()

    # ---------------------------------------------------------------------
    # Step 2: Radial Rim Gauge Readings
    # ---------------------------------------------------------------------
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
                    st.session_state.r_top = rt_val
                    st.session_state.r_bottom = rb_val
                    st.session_state.r_left = rl_val
                    st.session_state.r_right = rr_val
                    st.session_state.confirmed_step2 = True
                    if not r_pass:
                        st.warning(f"Warning: |(T+B)-(L+R)| = {r_err:.3f} mm exceeds tolerance (0.02 mm).")
                    st.rerun()
        else:
            if btn2.button("✏️ Edit Rim Values", use_container_width=True):
                st.session_state.confirmed_step2 = False
                st.session_state.is_calculated = False
                st.rerun()

    # ---------------------------------------------------------------------
    # Step 3: Axial Face Gauge Readings
    # ---------------------------------------------------------------------
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
                    st.session_state.g1_0 = g1_0_val; st.session_state.g2_0 = g2_0_val
                    st.session_state.g1_90 = g1_90_val; st.session_state.g2_90 = g2_90_val
                    st.session_state.g1_180 = g1_180_val; st.session_state.g2_180 = g2_180_val
                    st.session_state.g1_270 = g1_270_val; st.session_state.g2_270 = g2_270_val
                    st.session_state.confirmed_step3 = True
                    st.rerun()
        else:
            if btn2.button("✏️ Edit Face Values", use_container_width=True):
                st.session_state.confirmed_step3 = False
                st.session_state.is_calculated = False
                st.rerun()

    # ---------------------------------------------------------------------
    # Step 4: Strategy Selection & Final Calculation
    # ---------------------------------------------------------------------
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
                st.success("✅ Alignment calculation complete. Deflection diagrams updated.")
                st.rerun()

    # Full Reset Button
    if st.button("🔄 Reset All Data", use_container_width=True):
        for k in list(st.session_state.keys()):
            del st.session_state[k]
        st.rerun()


# =========================================================================
# Right Column: Live Gauge Monitoring & Diagrams
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

        # Metric Summary Cards
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Vertical Gap (ΔX)", f"{delta_x_v:+.3f} mm", "Bottom OPEN" if delta_x_v > 0 else "Bottom CLOSED")
        m2.metric("Vertical Offset (ΔY)", f"{delta_y_v:+.3f} mm", "Gen HIGHER than Target" if delta_y_v > 0 else "Gen LOWER than Target")
        m3.metric("LP Brg.4 Shim", f"{shim_b4:+.3f} mm", "Add Shim (+)" if shim_b4 > 0 else ("Remove Shim (-)" if shim_b4 < 0 else "Fixed"))
        m4.metric("Horizontal Offset", f"{delta_y_h:+.3f} mm", "Shifted RIGHT" if delta_y_h > 0 else "Shifted LEFT")

    view_tab1, view_tab2 = st.tabs(["📋 Inspection Sheet & Dial Report", "📐 Deflection Diagrams & Shim Action"])

    # ---------------------------------------------------------------------
    # Tab 1: Inspection Sheet Report (Window 1)
    # ---------------------------------------------------------------------
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
                 fontsize=9.5, style='italic', bbox=dict(boxstyle='round,pad=0.5', facecolor='#F5F5F5', edgecolor='gray'))

        plt.tight_layout(rect=[0, 0.06, 1, 0.95])
        st.pyplot(fig1)

    # ---------------------------------------------------------------------
    # Tab 2: Deflection Diagrams & Field Shim Action (Window 2)
    # ---------------------------------------------------------------------
    with view_tab2:
        if not st.session_state.is_calculated:
            st.info("💡 Please complete Steps 1–3 and click '⚡ Calculate & Process Shims' to generate shaft deflection diagrams and shim requirements.")
        else:
            fig2, (ax_side, ax_top, ax_bar) = plt.subplots(
                3, 1, figsize=(15, 12), gridspec_kw={'height_ratios': [1.2, 1.2, 0.85]}
            )
            fig2.subplots_adjust(top=0.91, bottom=0.07, hspace=0.38, left=0.08, right=0.96)
            fig2.suptitle(f"FIELD ALIGNMENT DIAGRAMS & SHIM ACTION - [SOLUTION {st.session_state.solution_choice}] (EGAT Mae Moh Unit 8-13)",
                          fontsize=13.5, fontweight='bold', color='#0D47A1', y=0.96)

            flange_h = 2.4
            gap_x = 420.0
            gen_end_x = st.session_state.l_gen_r + 400.0

            # 1. SIDE VIEW
            ax_side.axhline(0, color='gray', linestyle='--', linewidth=1.5, label='Turbine Centerline (Baseline)')
            ax_side.plot([-st.session_state.l_brg4 - 250, 0], [0, 0], color='#D84315', linewidth=4.5)
            ax_side.plot([0, 0], [-flange_h, flange_h], color='#BF360C', linewidth=5.5)
            ax_side.text(-st.session_state.l_brg4/2, 0.45, "TURBINE (LP)", ha='center', fontsize=10, fontweight='bold', color='#D84315')

            ax_side.plot([-st.session_state.l_brg4, -st.session_state.l_brg4], [-0.8, 0], color='#4E342E', linewidth=3)
            ax_side.scatter([-st.session_state.l_brg4], [-0.8], s=160, marker='^', color='#4E342E', zorder=5)
            ax_side.text(-st.session_state.l_brg4, -1.2, f"LP Brg.4\n(L={st.session_state.l_brg4:.0f} mm)", ha='center', va='top', fontsize=8.5, fontweight='bold')

            vis_ang_v = 0.8 if delta_x_v >= 0 else -0.8
            vis_offset_v = -0.7 if delta_y_v < 0 else 0.7
            fl_top_x = gap_x - (vis_ang_v * 100.0)
            fl_bot_x = gap_x + (vis_ang_v * 100.0)
            ax_side.plot([fl_top_x, fl_bot_x], [vis_offset_v + flange_h, vis_offset_v - flange_h], color='#0D47A1', linewidth=5.5)

            slope_v = (vis_ang_v * 2.0) / st.session_state.l_gen_r
            gen_x = np.array([gap_x, gap_x + st.session_state.l_gen_f, gap_x + st.session_state.l_gen_m, gap_x + st.session_state.l_gen_r, gen_end_x])
            gen_y_v = vis_offset_v + slope_v * (gen_x - gap_x)
            ax_side.plot(gen_x, gen_y_v, color='#1565C0', linewidth=4.5, label='Generator Shaft')
            ax_side.text(gap_x + st.session_state.l_gen_m/2, 2.0, "GENERATOR", ha='center', fontsize=10, fontweight='bold', color='#1565C0')

            gen_legs = [(gap_x + st.session_state.l_gen_f, f"Gen-F\n(L={st.session_state.l_gen_f:.0f})", gen_y_v[1]), 
                        (gap_x + st.session_state.l_gen_m, f"Gen-M\n(L={st.session_state.l_gen_m:.0f})", gen_y_v[2]), 
                        (gap_x + st.session_state.l_gen_r, f"Gen-R\n(L={st.session_state.l_gen_r:.0f})", gen_y_v[3])]
            for gx, glabel, gy in gen_legs:
                ax_side.plot([gx, gx], [gy - 0.7, gy], color='#0D47A1', linewidth=2.5)
                ax_side.scatter([gx], [gy - 0.7], s=140, marker='s', color='#0D47A1', zorder=5)
                ax_side.text(gx, gy - 1.0, glabel, ha='center', va='top', fontsize=8.5, fontweight='bold')

            ax_side.plot([0, gap_x + 150], [0, 0], color='gray', linestyle=':', lw=1.2)
            ax_side.plot([gap_x, gap_x + 150], [vis_offset_v, vis_offset_v], color='#0D47A1', linestyle=':', lw=1.2)
            ax_side.annotate("", xy=(gap_x + 120, 0), xytext=(gap_x + 120, vis_offset_v), arrowprops=dict(arrowstyle="<->", color="brown", lw=2.2))
            v_off_txt = "Gen LOWER than Target" if delta_y_v < 0 else "Gen HIGHER than Target"
            ax_side.text(gap_x + 150, vis_offset_v / 2.0, f" Vertical Offset (ΔY) = {delta_y_v:+.3f} mm\n [{v_off_txt}]",
                         ha='left', va='center', fontsize=9.5, fontweight='bold', color='brown',
                         bbox=dict(boxstyle='round,pad=0.3', facecolor='#FFF8E1', edgecolor='brown', alpha=0.9))

            ax_side.annotate("", xy=(0, -flange_h - 0.2), xytext=(fl_bot_x, -flange_h - 0.2), arrowprops=dict(arrowstyle="<->", color="purple", lw=2.2))
            v_gap_txt = "Bottom OPEN" if delta_x_v > 0 else "Bottom CLOSED"
            ax_side.text(fl_bot_x / 2.0, -flange_h - 0.65, f"Vertical Gap (ΔX) = {delta_x_v:+.3f} mm\n[{v_gap_txt}]",
                         ha='center', va='top', fontsize=9.5, fontweight='bold', color='purple',
                         bbox=dict(boxstyle='round,pad=0.3', facecolor='#F3E5F5', edgecolor='purple', alpha=0.9))

            ax_side.set_title("1. SIDE VIEW (Vertical Plane: Top vs Bottom)", fontsize=11, fontweight='bold', pad=10)
            ax_side.set_xlim(-st.session_state.l_brg4 - 350, gen_end_x + 300)
            ax_side.set_ylim(-3.8, 3.2)
            ax_side.set_ylabel("Vertical Deflection\n(Exaggerated)", fontsize=9, fontweight='bold')
            ax_side.set_yticks([-2, 0, 2])
            ax_side.set_yticklabels(["- (Down)", "0 (Ref)", "+ (Up)"], fontsize=8.5)
            ax_side.grid(True, linestyle=':', alpha=0.5)

            # 2. TOP VIEW
            ax_top.axhline(0, color='gray', linestyle='--', linewidth=1.5, label='Shaft Centerline (Baseline)')
            ax_top.plot([-st.session_state.l_brg4 - 250, 0], [0, 0], color='#D84315', linewidth=4.5)
            ax_top.plot([0, 0], [-flange_h, flange_h], color='#BF360C', linewidth=5.5)
            ax_top.text(-st.session_state.l_brg4/2, 0.45, "TURBINE (LP)", ha='center', fontsize=10, fontweight='bold', color='#D84315')

            ax_top.plot([-st.session_state.l_brg4, -st.session_state.l_brg4], [-0.8, 0], color='#4E342E', linewidth=3)
            ax_top.scatter([-st.session_state.l_brg4], [-0.8], s=160, marker='^', color='#4E342E', zorder=5)
            ax_top.text(-st.session_state.l_brg4, -1.2, f"LP Brg.4\n(L={st.session_state.l_brg4:.0f} mm)", ha='center', va='top', fontsize=8.5, fontweight='bold')

            vis_ang_h = 0.8 if delta_x_h >= 0 else -0.8
            vis_offset_h = 0.7 if delta_y_h > 0 else -0.7
            fl_left_x = gap_x - (vis_ang_h * 100.0)
            fl_right_x = gap_x + (vis_ang_h * 100.0)
            ax_top.plot([fl_left_x, fl_right_x], [vis_offset_h + flange_h, vis_offset_h - flange_h], color='#0D47A1', linewidth=5.5)

            slope_h = (vis_ang_h * 2.0) / st.session_state.l_gen_r
            gen_y_h = vis_offset_h + slope_h * (gen_x - gap_x)
            ax_top.plot(gen_x, gen_y_h, color='#1565C0', linewidth=4.5, label='Generator Shaft')
            ax_top.text(gap_x + st.session_state.l_gen_m/2, 2.0, "GENERATOR", ha='center', fontsize=10, fontweight='bold', color='#1565C0')

            for gx, glabel, gy in gen_legs:
                ax_top.plot([gx, gx], [gy - 0.7, gy], color='#0D47A1', linewidth=2.5)
                ax_top.scatter([gx], [gy - 0.7], s=140, marker='s', color='#0D47A1', zorder=5)
                ax_top.text(gx, gy - 1.0, glabel, ha='center', va='top', fontsize=8.5, fontweight='bold')

            ax_top.plot([0, gap_x + 150], [0, 0], color='gray', linestyle=':', lw=1.2)
            ax_top.plot([gap_x, gap_x + 150], [vis_offset_h, vis_offset_h], color='#0D47A1', linestyle=':', lw=1.2)
            ax_top.annotate("", xy=(gap_x + 120, 0), xytext=(gap_x + 120, vis_offset_h), arrowprops=dict(arrowstyle="<->", color="brown", lw=2.2))
            h_off_txt = "Gen Shifted RIGHT" if delta_y_h > 0 else "Gen Shifted LEFT"
            ax_top.text(gap_x + 150, vis_offset_h / 2.0, f" Horizontal Offset (ΔY) = {delta_y_h:+.3f} mm\n [{h_off_txt}]",
                        ha='left', va='center', fontsize=9.5, fontweight='bold', color='brown',
                        bbox=dict(boxstyle='round,pad=0.3', facecolor='#FFF8E1', edgecolor='brown', alpha=0.9))

            ax_top.annotate("", xy=(0, -flange_h - 0.2), xytext=(fl_right_x, -flange_h - 0.2), arrowprops=dict(arrowstyle="<->", color="purple", lw=2.2))
            h_gap_txt = "Right OPEN" if delta_x_h > 0 else "Left OPEN"
            ax_top.text(fl_right_x / 2.0, -flange_h - 0.65, f"Horizontal Gap (ΔX) = {delta_x_h:+.3f} mm\n[{h_gap_txt}]",
                        ha='center', va='top', fontsize=9.5, fontweight='bold', color='purple',
                        bbox=dict(boxstyle='round,pad=0.3', facecolor='#F3E5F5', edgecolor='purple', alpha=0.9))

            ax_top.set_title("2. TOP VIEW (Horizontal Plane: Left vs Right)", fontsize=11, fontweight='bold', pad=10)
            ax_top.set_xlim(-st.session_state.l_brg4 - 350, gen_end_x + 300)
            ax_top.set_ylim(-3.8, 3.2)
            ax_top.set_ylabel("Horizontal Shift\n(Exaggerated)", fontsize=9, fontweight='bold')
            ax_top.set_yticks([-2, 0, 2])
            ax_top.set_yticklabels(["- (Left)", "0 (Center)", "+ (Right)"], fontsize=8.5)
            ax_top.grid(True, linestyle=':', alpha=0.5)

            # 3. FIELD SHIM ACTION BAR CHART
            labels = ["LP Bearing 4", "Gen Front Leg (1,2)", "Gen Mid Leg (3,4)", "Gen Rear Leg (5,6)"]
            shims = [shim_b4, shim_f, shim_m, shim_r]
            colors = ['#2E7D32' if s > 0 else ('#C62828' if s < 0 else '#9E9E9E') for s in shims]

            bars = ax_bar.bar(labels, shims, color=colors, width=0.42, edgecolor='black', zorder=3)
            ax_bar.axhline(0, color='black', linewidth=1.2)
            ax_bar.set_ylabel("Shim Adjustment (mm)\n[+ Add / - Remove]", fontsize=9.5, fontweight='bold')
            ax_bar.set_title(f"3. Field Shim Action Required for [SOLUTION {st.session_state.solution_choice}]", fontsize=11, fontweight='bold', pad=8)
            ax_bar.grid(axis='y', linestyle=':', alpha=0.6)

            max_val = max(abs(s) for s in shims) if any(abs(s) > 0 for s in shims) else 0.05
            ax_bar.set_ylim(-max_val * 1.5 - 0.04, max_val * 1.5 + 0.04)

            for bar, s_val in zip(bars, shims):
                h = bar.get_height()
                va_align = 'bottom' if h >= 0 else 'top'
                y_pos = h + (0.005 if h >= 0 else -0.005)
                action_word = "ADD (+)" if s_val > 0 else ("REMOVE (-)" if s_val < 0 else "FIXED")
                ax_bar.text(bar.get_x() + bar.get_width()/2., y_pos, f"{s_val:+.3f} mm\n({action_word})", ha='center', va=va_align, fontsize=9.5, fontweight='bold')

            st.pyplot(fig2)