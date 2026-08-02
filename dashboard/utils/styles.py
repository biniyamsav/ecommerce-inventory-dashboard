# utils/styles.py

import streamlit as st


# =====================================================
# Color Palette (single source of truth)
# =====================================================

COLORS = {
    "primary": "#6366F1",      # indigo — headers, primary actions
    "success": "#34D399",      # positive deltas
    "danger": "#F87171",       # negative deltas
    "warning": "#FBBF24",      # low stock / alerts
    "background": "#0B1224",
    "surface": "#111827",
    "card_bg": "#111827",
    "border": "rgba(255,255,255,0.08)",
    "text_primary": "#F8FAFC",
    "text_secondary": "#A5B4FC",
    "muted": "#94A3B8",
}

# Consistent chart color sequence (pass to any px chart via color_discrete_sequence)
CHART_COLORS = [
    "#6366F1", "#34D399", "#FBBF24", "#F87171",
    "#38BDF8", "#A78BFA", "#FB7185", "#84CC16",
]


# =====================================================
# Global CSS Injection
# =====================================================

def inject_custom_css():
    """Call once at the top of app.py, before anything else renders."""
    st.markdown(
        f"""
        <style>
            :root {{
                color-scheme: dark;
            }}

            .block-container {{
                padding-top: 2rem;
                padding-bottom: 2rem;
                background: {COLORS['background']};
            }}

            .main {{
                color: {COLORS['text_primary']};
            }}

            h1, h2, h3, h4, h5, h6 {{
                color: {COLORS['text_primary']};
                font-weight: 700;
            }}

            p, span, label, div, li {{
                color: {COLORS['muted']};
            }}

            .streamlit-expanderHeader {{
                color: {COLORS['text_primary']} !important;
            }}

            .stButton>button {{
                background-color: {COLORS['primary']} !important;
                color: #FFFFFF !important;
                border-radius: 12px !important;
                border: none !important;
                padding: 0.85rem 1rem !important;
                box-shadow: 0 24px 40px rgba(99, 102, 241, 0.16) !important;
                font-weight: 600 !important;
            }}

            .stButton>button:hover {{
                background-color: #4F46E5 !important;
            }}

            .kpi-card {{
                background-color: {COLORS['surface']};
                border: 1px solid {COLORS['border']};
                border-radius: 18px;
                padding: 20px 24px;
                box-shadow: 0 18px 45px rgba(15, 23, 42, 0.28);
            }}

            .kpi-label {{
                font-size: 0.75rem;
                font-weight: 700;
                color: {COLORS['text_secondary']};
                letter-spacing: 0.08em;
                text-transform: uppercase;
                margin-bottom: 10px;
            }}

            .kpi-value {{
                font-size: 2.05rem;
                font-weight: 700;
                color: {COLORS['text_primary']};
                line-height: 1.1;
            }}

            .kpi-delta-up {{
                color: {COLORS['success']};
                font-size: 0.95rem;
                font-weight: 700;
                margin-top: 8px;
            }}

            .kpi-delta-down {{
                color: {COLORS['danger']};
                font-size: 0.95rem;
                font-weight: 700;
                margin-top: 8px;
            }}

            .nav-card {{
                background: rgba(255, 255, 255, 0.04);
                border: 1px solid rgba(255, 255, 255, 0.08);
                border-radius: 18px;
                padding: 24px;
                min-height: 190px;
                transition: transform 0.18s ease, border-color 0.18s ease, background 0.18s ease;
            }}

            .nav-card:hover {{
                transform: translateY(-4px);
                border-color: rgba(99, 102, 241, 0.35);
                background: rgba(99, 102, 241, 0.08);
            }}

            .nav-card h3 {{
                margin-top: 0;
                color: #FFFFFF;
                font-size: 1.25rem;
            }}

            .nav-card p {{
                color: {COLORS['muted']};
                line-height: 1.6;
                margin-bottom: 16px;
            }}

            .hero-panel {{
                background: linear-gradient(135deg, rgba(99, 102, 241, 0.16), rgba(15, 23, 42, 0.98));
                border: 1px solid rgba(255, 255, 255, 0.08);
                border-radius: 24px;
                padding: 40px;
                margin-bottom: 2rem;
            }}

            .hero-eyebrow {{
                color: {COLORS['success']};
                font-weight: 700;
                letter-spacing: 0.2em;
                text-transform: uppercase;
                margin-bottom: 1rem;
            }}

            .hero-title {{
                color: #FFFFFF;
                font-size: 3rem;
                margin: 0 0 1rem 0;
                line-height: 1.05;
            }}

            .hero-text {{
                color: {COLORS['muted']};
                font-size: 1.05rem;
                line-height: 1.8;
                margin-bottom: 1.8rem;
            }}

            .section-pill {{
                display: inline-flex;
                border-radius: 999px;
                padding: 10px 18px;
                margin-right: 10px;
                margin-bottom: 10px;
                background: rgba(255,255,255,0.05);
                color: #FFFFFF;
                border: 1px solid rgba(255,255,255,0.08);
                font-weight: 600;
                text-decoration: none;
            }}

            .section-pill.selected {{
                background: rgba(99, 102, 241, 0.18);
                border-color: rgba(99, 102, 241, 0.35);
                color: #FFFFFF;
            }}

            .section-header {{
                display: flex;
                align-items: center;
                justify-content: space-between;
                gap: 1rem;
            }}

            .section-header .section-copy {{
                color: {COLORS['muted']};
                margin: 0;
            }}
        </style>
        """,
        unsafe_allow_html=True,
    )


# =====================================================
# Custom KPI Card (HTML) — replaces the st.metric placeholder
# =====================================================

def render_kpi_card(label, value, delta=None, delta_positive=True):
    """
    label: str -> "Revenue"
    value: str -> "$1.25M"
    delta: str or None -> "+12.3%"
    delta_positive: bool -> controls arrow + color
    """
    delta_html = ""
    if delta is not None:
        arrow = "▲" if delta_positive else "▼"
        css_class = "kpi-delta-up" if delta_positive else "kpi-delta-down"
        delta_html = f'<div class="{css_class}">{arrow} {delta}</div>'

    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-label">{label}</div>
            <div class="kpi-value">{value}</div>
            {delta_html}
        </div>
        """,
        unsafe_allow_html=True,
    )