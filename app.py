import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Buffon's Needle",
    page_icon="📐",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=EB+Garamond:ital,wght@0,400;1,400&family=Fira+Mono&display=swap');

html, body, [class*="css"] { font-family: 'EB Garamond', Georgia, serif; }

.main { background-color: #1a2535; }
.block-container { padding-top: 2rem; padding-bottom: 2rem; }

/* Header */
.app-title {
    font-family: 'EB Garamond', serif;
    font-style: italic;
    font-size: 2.6rem;
    font-weight: 400;
    color: #e8e0d0;
    margin-bottom: 0;
    line-height: 1.1;
}
.app-subtitle {
    font-size: 0.8rem;
    letter-spacing: 0.18em;
    color: #475569;
    margin-top: 0.2rem;
    margin-bottom: 1.5rem;
}

/* Stat cards */
.stat-card {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 6px;
    padding: 14px 16px;
    margin-bottom: 0;
}
.stat-label {
    font-size: 0.68rem;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    color: #64748b;
    margin-bottom: 4px;
    font-family: 'Fira Mono', monospace;
}
.stat-value {
    font-family: 'Fira Mono', monospace;
    font-size: 1.35rem;
    font-weight: 600;
}
.pi-card {
    background: rgba(249,168,201,0.06);
    border: 1px solid rgba(249,168,201,0.18);
    border-radius: 6px;
    padding: 20px;
    text-align: center;
    margin-bottom: 1rem;
}
.pi-value {
    font-family: 'EB Garamond', serif;
    font-style: italic;
    font-size: 3.4rem;
    font-weight: 400;
    line-height: 1;
}
.pi-true {
    font-family: 'Fira Mono', monospace;
    font-size: 0.72rem;
    color: #475569;
    margin-top: 6px;
}
.pi-error {
    font-family: 'Fira Mono', monospace;
    font-size: 0.75rem;
    margin-top: 6px;
}
.formula-block {
    background: rgba(0,0,0,0.3);
    border-left: 3px solid #f9a8c9;
    padding: 10px 14px;
    margin: 10px 0;
    border-radius: 0 4px 4px 0;
    font-family: 'Fira Mono', monospace;
    font-size: 0.82rem;
    color: #fde68a;
}
.prose {
    font-size: 0.92rem;
    line-height: 1.75;
    color: #b0a898;
}
.divider {
    border: none;
    border-top: 1px solid rgba(255,255,255,0.08);
    margin: 1rem 0;
}
/* Sidebar */
section[data-testid="stSidebar"] {
    background: #141e2b;
    border-right: 1px solid rgba(255,255,255,0.07);
}
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] .stMarkdown p {
    color: #b0a898 !important;
    font-family: 'EB Garamond', serif;
}
/* Buttons */
.stButton > button {
    background: transparent;
    border: 1.5px solid #f9a8c9;
    color: #f9a8c9;
    font-family: 'EB Garamond', serif;
    font-size: 1rem;
    letter-spacing: 0.04em;
    border-radius: 4px;
    padding: 0.45rem 1.2rem;
    transition: all 0.18s;
    width: 100%;
}
.stButton > button:hover { background: rgba(249,168,201,0.12); }
.reset-btn > button {
    border-color: rgba(148,163,184,0.4) !important;
    color: #94a3b8 !important;
}
.reset-btn > button:hover { background: rgba(148,163,184,0.1) !important; }
</style>
""", unsafe_allow_html=True)

# ── Simulation logic ───────────────────────────────────────────────────────────
STRIPE_H = 70
BOARD_W = 600
BOARD_H = 420

def theoretical_p(ratio):
    if ratio <= 1:
        return (2 * ratio) / np.pi
    return (2 / np.pi) * (ratio - np.sqrt(ratio**2 - 1) + np.arcsin(1 / ratio))

def run_simulation(n, ratio):
    L = ratio * STRIPE_H
    cx = np.random.uniform(0, BOARD_W, n)
    cy = np.random.uniform(0, BOARD_H, n)
    angles = np.random.uniform(0, np.pi, n)
    half = L / 2
    y1 = cy - half * np.sin(angles)
    y2 = cy + half * np.sin(angles)
    x1 = cx - half * np.cos(angles)
    x2 = cx + half * np.cos(angles)
    near_line = np.round(cy / STRIPE_H) * STRIPE_H
    min_y = np.minimum(y1, y2)
    max_y = np.maximum(y1, y2)
    crossed = (min_y <= near_line) & (near_line <= max_y)
    return x1, y1, x2, y2, crossed

# ── Session state init ─────────────────────────────────────────────────────────
def init_state():
    defaults = {
        "total_drops": 0,
        "total_hits": 0,
        "history": [],          # list of (n, pi_est)
        "needle_x1": [],
        "needle_y1": [],
        "needle_x2": [],
        "needle_y2": [],
        "needle_hit": [],
        "last_ratio": 1.0,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_state()

def reset_sim():
    st.session_state.total_drops = 0
    st.session_state.total_hits = 0
    st.session_state.history = []
    st.session_state.needle_x1 = []
    st.session_state.needle_y1 = []
    st.session_state.needle_x2 = []
    st.session_state.needle_y2 = []
    st.session_state.needle_hit = []

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### ⚙️ Controls")
    st.markdown("---")

    ratio = st.slider(
        "Needle ÷ Board width ratio",
        min_value=0.10, max_value=2.00, value=1.00, step=0.01,
        help="L/d — ratio of needle length to the spacing between lines. Values >1 use the long-needle formula."
    )
    ratio_tag = "short needle" if ratio <= 1 else "long needle"
    st.caption(f"**{ratio:.2f}×** — {ratio_tag}")

    if ratio != st.session_state.last_ratio:
        reset_sim()
        st.session_state.last_ratio = ratio

    st.markdown("---")

    n_drops = st.number_input(
        "Needles per drop",
        min_value=1, max_value=10000, value=200, step=50,
        help="How many needles to add each time you press Drop"
    )
    st.slider("(drag to set)", min_value=1, max_value=10000,
              value=n_drops, step=1, key="_n_slider",
              label_visibility="collapsed")
    # keep number input and slider in sync
    n_drops = st.session_state.get("_n_slider", n_drops)

    st.markdown("---")

    col_drop, col_reset = st.columns([2, 1])
    with col_drop:
        drop_clicked = st.button(f"Drop {n_drops:,} needles", type="primary")
    with col_reset:
        st.markdown('<div class="reset-btn">', unsafe_allow_html=True)
        reset_clicked = st.button("↺ Reset")
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("---")
    MAX_DISPLAY = st.select_slider(
        "Max needles shown",
        options=[500, 1000, 2000, 5000],
        value=2000,
        help="Older needles are removed to keep rendering fast"
    )

# ── Handle actions ─────────────────────────────────────────────────────────────
if reset_clicked:
    reset_sim()

if drop_clicked:
    x1, y1, x2, y2, crossed = run_simulation(n_drops, ratio)
    st.session_state.needle_x1 = (st.session_state.needle_x1 + x1.tolist())[-MAX_DISPLAY:]
    st.session_state.needle_y1 = (st.session_state.needle_y1 + y1.tolist())[-MAX_DISPLAY:]
    st.session_state.needle_x2 = (st.session_state.needle_x2 + x2.tolist())[-MAX_DISPLAY:]
    st.session_state.needle_y2 = (st.session_state.needle_y2 + y2.tolist())[-MAX_DISPLAY:]
    st.session_state.needle_hit = (st.session_state.needle_hit + crossed.tolist())[-MAX_DISPLAY:]
    st.session_state.total_drops += n_drops
    st.session_state.total_hits += int(crossed.sum())
    td, th = st.session_state.total_drops, st.session_state.total_hits
    pi_est = (2 * ratio * td) / th if th > 0 else None
    st.session_state.history.append((td, pi_est))

# ── Derived stats ──────────────────────────────────────────────────────────────
td = st.session_state.total_drops
th = st.session_state.total_hits
th_prob = theoretical_p(ratio)
act_prob = th / td if td > 0 else None
pi_est = (2 * ratio * td) / th if th > 0 else None
pi_err = abs(pi_est - np.pi) if pi_est else None

if pi_err is None:
    pi_color = "#94a3b8"
elif pi_err < 0.02:
    pi_color = "#86efac"
elif pi_err < 0.1:
    pi_color = "#fde68a"
else:
    pi_color = "#fca5a5"

# ── Layout ─────────────────────────────────────────────────────────────────────
st.markdown('<p class="app-title">Buffon\'s Needle</p>', unsafe_allow_html=True)
st.markdown('<p class="app-subtitle">— A MONTE CARLO EXPERIMENT</p>', unsafe_allow_html=True)

left_col, right_col = st.columns([1.6, 1], gap="large")

# ══ LEFT: Visualization ════════════════════════════════════════════════════════
with left_col:

    # Build Plotly figure
    fig = go.Figure()

    # Board stripes
    n_lines = int(BOARD_H / STRIPE_H) + 1
    for i in range(n_lines - 1):
        if i % 2 == 0:
            fig.add_shape(type="rect", x0=0, y0=i * STRIPE_H, x1=BOARD_W, y1=(i + 1) * STRIPE_H,
                          fillcolor="rgba(255,255,255,0.025)", line_width=0, layer="below")

    # Chalk lines
    for i in range(n_lines):
        y = i * STRIPE_H
        fig.add_shape(type="line", x0=0, y0=y, x1=BOARD_W, y1=y,
                      line=dict(color="rgba(255,255,255,0.22)", width=1, dash="dot"), layer="below")

    # Needles
    if st.session_state.needle_x1:
        hits_mask = np.array(st.session_state.needle_hit)
        x1s = np.array(st.session_state.needle_x1)
        y1s = np.array(st.session_state.needle_y1)
        x2s = np.array(st.session_state.needle_x2)
        y2s = np.array(st.session_state.needle_y2)

        # Build line segments using None separators (efficient in Plotly)
        def build_segments(mask):
            xs, ys = [], []
            idxs = np.where(mask)[0]
            for i in idxs:
                xs += [x1s[i], x2s[i], None]
                ys += [y1s[i], y2s[i], None]
            return xs, ys

        hx, hy = build_segments(hits_mask)
        mx, my = build_segments(~hits_mask)

        if hx:
            fig.add_trace(go.Scatter(x=hx, y=hy, mode="lines",
                line=dict(color="rgba(249,168,201,0.72)", width=1.4),
                name="crossing", hoverinfo="skip"))
        if mx:
            fig.add_trace(go.Scatter(x=mx, y=my, mode="lines",
                line=dict(color="rgba(147,197,253,0.55)", width=1.4),
                name="miss", hoverinfo="skip"))

    fig.update_layout(
        paper_bgcolor="#16202e",
        plot_bgcolor="#16202e",
        margin=dict(l=0, r=0, t=0, b=0),
        height=BOARD_H,
        xaxis=dict(range=[0, BOARD_W], showgrid=False, zeroline=False,
                   showticklabels=False, fixedrange=True),
        yaxis=dict(range=[0, BOARD_H], showgrid=False, zeroline=False,
                   showticklabels=False, fixedrange=True, scaleanchor="x"),
        showlegend=True,
        legend=dict(
            orientation="h", yanchor="bottom", y=0.01, xanchor="right", x=0.99,
            font=dict(color="#64748b", size=11),
            bgcolor="rgba(0,0,0,0)",
        ),
        annotations=[] if st.session_state.needle_x1 else [dict(
            x=BOARD_W / 2, y=BOARD_H / 2, text="Press \"Drop Needles\" to begin",
            showarrow=False, font=dict(color="rgba(255,255,255,0.15)", size=13, family="EB Garamond"),
        )]
    )

    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    # Hit rate comparison bar
    if td > 0:
        st.markdown(f"""
        <div class="stat-card" style="margin-top:0">
          <div style="display:flex;justify-content:space-between;font-size:0.88rem;margin-bottom:8px;color:#94a3b8">
            <span>Theory P = <span style="font-family:Fira Mono,monospace;color:#fde68a">{th_prob*100:.2f}%</span></span>
            <span>Actual P = <span style="font-family:Fira Mono,monospace;color:#f9a8c9">{act_prob*100:.2f}%</span></span>
          </div>
          <div style="position:relative;height:10px;background:rgba(255,255,255,0.06);border-radius:5px;overflow:hidden">
            <div style="position:absolute;left:0;top:0;height:100%;width:{th_prob*100:.2f}%;background:rgba(253,230,138,0.2);border-radius:5px"></div>
            <div style="position:absolute;left:0;top:0;height:100%;width:{(act_prob or 0)*100:.2f}%;background:linear-gradient(90deg,#f9a8c9,#fb7185);border-radius:5px"></div>
          </div>
          <div style="font-size:0.7rem;color:#475569;text-align:right;margin-top:5px;font-family:Fira Mono,monospace">
            diff: {((act_prob or 0) - th_prob)*100:.2f}pp
          </div>
        </div>
        """, unsafe_allow_html=True)

# ══ RIGHT: Stats + chart ═══════════════════════════════════════════════════════
with right_col:

    # π hero card
    pi_display = f"{pi_est:.5f}" if pi_est else "—"
    err_line = f'<div class="pi-error" style="color:{pi_color}">error: {pi_err:.5f} {"🎯" if pi_err and pi_err < 0.01 else "📐" if pi_err and pi_err < 0.05 else ""}</div>' if pi_err is not None else ""
    st.markdown(f"""
    <div class="pi-card">
      <div class="stat-label" style="margin-bottom:8px">π estimate</div>
      <div class="pi-value" style="color:{pi_color};text-shadow:{'0 0 30px ' + pi_color + '55' if pi_est else 'none'}">{pi_display}</div>
      <div class="pi-true">true π = 3.14159265…</div>
      {err_line}
    </div>
    """, unsafe_allow_html=True)

    # Stat grid
    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f'<div class="stat-card"><div class="stat-label">Total drops</div><div class="stat-value" style="color:#e8e0d0">{td:,}</div></div>', unsafe_allow_html=True)
    with c2:
        st.markdown(f'<div class="stat-card"><div class="stat-label">Crossings</div><div class="stat-value" style="color:#f9a8c9">{th:,}</div></div>', unsafe_allow_html=True)
    st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
    c3, c4 = st.columns(2)
    with c3:
        st.markdown(f'<div class="stat-card"><div class="stat-label">Actual P</div><div class="stat-value" style="color:#f9a8c9">{f"{act_prob*100:.2f}%" if act_prob else "—"}</div></div>', unsafe_allow_html=True)
    with c4:
        st.markdown(f'<div class="stat-card"><div class="stat-label">Theory P</div><div class="stat-value" style="color:#fde68a">{th_prob*100:.2f}%</div></div>', unsafe_allow_html=True)

    st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)

    # Convergence chart
    st.markdown('<div class="stat-label" style="margin-bottom:6px">π convergence</div>', unsafe_allow_html=True)
    if len(st.session_state.history) > 1:
        hist_df = pd.DataFrame(st.session_state.history, columns=["n", "pi"])
        conv_fig = go.Figure()
        conv_fig.add_hline(y=np.pi, line=dict(color="rgba(253,230,138,0.4)", width=1, dash="dash"))
        conv_fig.add_trace(go.Scatter(
            x=hist_df["n"], y=hist_df["pi"],
            mode="lines", line=dict(color="#f9a8c9", width=1.8),
            name="π estimate", hovertemplate="n=%{x:,}<br>π≈%{y:.5f}<extra></extra>"
        ))
        conv_fig.update_layout(
            paper_bgcolor="rgba(255,255,255,0.04)",
            plot_bgcolor="rgba(0,0,0,0.15)",
            margin=dict(l=40, r=10, t=10, b=30),
            height=160,
            xaxis=dict(showgrid=False, tickfont=dict(color="#334155", size=9, family="Fira Mono"),
                       tickformat=","),
            yaxis=dict(range=[2.5, 3.8], showgrid=True,
                       gridcolor="rgba(255,255,255,0.04)",
                       tickfont=dict(color="#334155", size=9, family="Fira Mono")),
            showlegend=False,
        )
        st.plotly_chart(conv_fig, use_container_width=True, config={"displayModeBar": False})
        st.caption("— dashed line = true π")
    else:
        st.markdown('<div style="height:160px;display:flex;align-items:center;justify-content:center;color:#2d3a52;font-style:italic;font-size:0.9rem;background:rgba(255,255,255,0.03);border-radius:6px">Chart appears after first drop</div>', unsafe_allow_html=True)

    st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)

    # Formula / explanation tabs
    tab_formula, tab_how = st.tabs(["Formula", "How it works"])

    with tab_formula:
        st.markdown(f"""
        <p class="prose" style="margin-bottom:4px">For needle length <strong>L</strong>, board width <strong>d</strong>:</p>
        <div class="formula-block">P = 2L / (π·d) &nbsp; <span style="color:#64748b;font-size:0.75rem">when L ≤ d</span></div>
        <p class="prose" style="margin:6px 0">Solving for π:</p>
        <div class="formula-block">π ≈ 2L·n / (d · hits)</div>
        <p class="prose" style="margin-top:10px;font-size:0.82rem">
          Now: <span style="font-family:Fira Mono,monospace;color:#fde68a">L/d = {ratio:.2f}</span>,
          n = <span style="font-family:Fira Mono,monospace;color:#fde68a">{td:,}</span>,
          hits = <span style="font-family:Fira Mono,monospace;color:#f9a8c9">{th:,}</span>
        </p>
        """, unsafe_allow_html=True)

    with tab_how:
        st.markdown("""
        <div class="prose">
        <p style="margin-bottom:8px">Drop a needle of length <strong>L</strong> randomly onto a floor with parallel lines spaced <strong>d</strong> apart. What's the probability it crosses a line?</p>
        <p style="margin-bottom:8px">Georges-Louis Leclerc (Buffon) proved in <strong>1777</strong> that this probability involves π — giving us a physical way to estimate it.</p>
        <p>More drops → closer convergence to <strong>3.14159…</strong> Try 10,000 needles to see the law of large numbers in action!</p>
        </div>
        """, unsafe_allow_html=True)
