import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from backend import detect_drift

# -------------------------------
# Page Config
# -------------------------------
st.set_page_config(
    page_title="DriftWatch",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# -------------------------------
# THEME TOGGLE IN SESSION STATE
# -------------------------------
if "theme" not in st.session_state:
    st.session_state.theme = "Light Mode"

# -------------------------------
# DYNAMIC CSS BASED ON THEME
# -------------------------------
if st.session_state.theme == "Dark Mode":
    bg_color = "#0F1419"
    text_color = "#F0F2F5"
    card_bg = "#1E2533"
    accent = "#8B5CF6"
    secondary_accent = "#60A5FA"
    border_color = "#303B52"
    hover_color = "#2C3647"
    metric_text = "#60A5FA"
    chart_bg = "#1E2533"
else:
    bg_color = "#F8FAFC"
    text_color = "#0F1419"
    card_bg = "#FFFFFF"
    accent = "#6366F1"
    secondary_accent = "#3B82F6"
    border_color = "#E2E8F0"
    hover_color = "#F1F5F9"
    metric_text = "#3B82F6"
    chart_bg = "#FFFFFF"

# -------------------------------
# ENHANCED STYLING WITH ANIMATIONS
# -------------------------------
st.markdown(f"""
    <style>
    /* Root styling */
    * {{
        transition: background-color 0.3s ease, color 0.3s ease;
    }}

    /* App Background with animation */
    .stApp {{
        background: linear-gradient(135deg, {bg_color} 0%, {bg_color} 100%);
        color: {text_color};
        position: relative;
        overflow: hidden;
    }}

    /* Animated background particles */
    .stApp::before {{
        content: '';
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background-image: 
            radial-gradient(circle at 20% 50%, {accent}08 1px, transparent 1px),
            radial-gradient(circle at 60% 70%, {secondary_accent}08 1px, transparent 1px),
            radial-gradient(circle at 80% 10%, {accent}06 1px, transparent 1px),
            radial-gradient(circle at 40% 80%, {secondary_accent}06 1px, transparent 1px),
            radial-gradient(circle at 90% 40%, {accent}08 1px, transparent 1px);
        background-size: 200px 200px, 250px 250px, 180px 180px, 220px 220px, 240px 240px;
        background-position: 0 0, 40px 60px, 130px 270px, 70px 100px, 0 50px;
        animation: drift 20s linear infinite;
        pointer-events: none;
        z-index: 0;
    }}

    /* Main container */
    [data-testid="stAppViewContainer"] {{
        background: {bg_color};
        position: relative;
        z-index: 1;
    }}

    /* Floating data points animation */
    @keyframes drift {{
        0% {{ background-position: 0 0, 40px 60px, 130px 270px, 70px 100px, 0 50px; }}
        100% {{ background-position: 200px 200px, 240px 260px, 330px 470px, 270px 300px, 200px 250px; }}
    }}

    /* Ensure text is always readable */
    body, p, div {{
        color: {text_color} !important;
    }}

    /* Animations */
    @keyframes fadeIn {{
        from {{ opacity: 0; transform: translateY(15px); }}
        to {{ opacity: 1; transform: translateY(0); }}
    }}

    @keyframes slideInRight {{
        from {{ opacity: 0; transform: translateX(20px); }}
        to {{ opacity: 1; transform: translateX(0); }}
    }}

    @keyframes glow {{
        0%, 100% {{ box-shadow: 0px 0px 10px rgba(124, 58, 237, 0.3); }}
        50% {{ box-shadow: 0px 0px 20px rgba(124, 58, 237, 0.5); }}
    }}

    @keyframes floatUp {{
        0% {{ transform: translateY(0px) translateX(0); opacity: 0; }}
        10% {{ opacity: 0.3; }}
        90% {{ opacity: 0.3; }}
        100% {{ transform: translateY(-100vh) translateX(20px); opacity: 0; }}
    }}

    @keyframes floatRight {{
        0% {{ transform: translateX(0) translateY(0); opacity: 0; }}
        5% {{ opacity: 0.2; }}
        95% {{ opacity: 0.2; }}
        100% {{ transform: translateX(100vw) translateY(-30px); opacity: 0; }}
    }}

    @keyframes pulse {{
        0%, 100% {{ opacity: 0.6; }}
        50% {{ opacity: 1; }}
    }}

    @keyframes shimmer {{
        0% {{ background-position: -1000px 0; }}
        100% {{ background-position: 1000px 0; }}
    }}

    /* Floating dataset icons - creates depth effect */
    .stApp::after {{
        content: '📊 📈 📉 🔢 💾 🗂️ 📋 ⚙️';
        position: fixed;
        top: -100px;
        left: 0;
        width: 100%;
        font-size: 60px;
        opacity: 0;
        animation: floatUp 15s linear infinite;
        pointer-events: none;
        z-index: 0;
        letter-spacing: 100px;
        overflow: hidden;
    }}

    /* Header Container */
    .header-container {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 25px 0;
        margin-bottom: 10px;
        animation: fadeIn 0.8s ease-in-out;
    }}

    .header-content {{
        flex: 1;
    }}

    /* Title Styles */
    .main-title {{
        font-size: 48px;
        font-weight: 800;
        background: linear-gradient(135deg, {accent}, {secondary_accent});
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin: 0;
        padding: 0;
        animation: fadeIn 0.8s ease-in-out;
        letter-spacing: -1px;
        color: {accent};
    }}

    .sub-text {{
        font-size: 16px;
        color: {text_color};
        opacity: 0.85;
        margin: 8px 0 0 0;
        animation: fadeIn 1.2s ease-in-out;
        font-weight: 500;
    }}

    /* Cards */
    .card {{
        padding: 24px;
        border-radius: 16px;
        background: {card_bg};
        border: 1px solid {border_color};
        box-shadow: 0px 4px 20px rgba(0,0,0,0.08);
        transition: all 0.3s ease;
        animation: fadeIn 0.8s ease-in-out;
        color: {text_color};
    }}

    .card:hover {{
        transform: translateY(-8px);
        box-shadow: 0px 12px 40px rgba(124, 58, 237, 0.15);
        border-color: {accent};
    }}

    .hero-card {{
        padding: 32px;
        border-radius: 26px;
        background: linear-gradient(135deg, rgba(99, 102, 241, 0.16), rgba(59, 130, 246, 0.08));
        border: 1px solid rgba(99, 102, 241, 0.18);
        box-shadow: 0px 18px 60px rgba(99, 102, 241, 0.12);
        margin-bottom: 20px;
    }}

    .hero-badges {{
        display: flex;
        flex-wrap: wrap;
        gap: 10px;
        margin-top: 18px;
    }}

    .upload-card {{
        padding: 28px;
        border-radius: 20px;
        border: 1px solid {border_color};
        background: linear-gradient(180deg, {card_bg} 0%, {bg_color} 100%);
        box-shadow: 0px 12px 30px rgba(15, 20, 25, 0.08);
        margin-bottom: 20px;
    }}

    .metric-grid {{
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(210px, 1fr));
        gap: 18px;
        margin-top: 10px;
        margin-bottom: 10px;
    }}

    .chart-card {{
        padding: 20px;
        border-radius: 22px;
        border: 1px solid {border_color};
        background: {card_bg};
        box-shadow: 0px 12px 28px rgba(15, 20, 25, 0.06);
    }}

    .theme-toggle-container {{
        display: flex;
        justify-content: flex-end;
        align-items: flex-start;
        height: 100%;
    }}

    .hero-badges .info-badge {{
        background: {accent}15;
        border: 1px solid {accent}22;
        color: {accent};
    }}

    .stFileUploader > div {{
        border-radius: 18px !important;
    }}

    .stRadio > div {{
        border-radius: 16px !important;
        border: 1px solid {border_color} !important;
        padding: 18px;
        background: {hover_color};
    }}

    .stButton > button {{
        border-radius: 10px !important;
        font-weight: 600 !important;
        padding: 10px 24px !important;
        transition: all 0.3s ease !important;
        border: 1px solid {accent} !important;
        background: linear-gradient(135deg, {accent}, {secondary_accent}) !important;
        color: white !important;
    }}

    .stButton > button:hover {{
        transform: translateY(-2px) !important;
        box-shadow: 0px 8px 20px rgba(99, 102, 241, 0.3) !important;
    }}

    .card-metric {{
        padding: 20px;
        border-radius: 14px;
        background: {card_bg};
        text-align: center;
        border: 1px solid {border_color};
        box-shadow: 0px 2px 12px rgba(0,0,0,0.06);
        transition: all 0.3s ease;
        animation: fadeIn 0.8s ease-in-out;
        color: {text_color};
    }}

    .card-metric:hover {{
        transform: translateY(-6px);
        box-shadow: 0px 8px 24px rgba(99, 102, 241, 0.15);
    }}

    .card-metric b {{
        color: {text_color};
        font-size: 14px;
    }}

    .card-metric h3 {{
        color: {metric_text} !important;
        margin: 8px 0 !important;
    }}

    /* Section Titles */
    .section-title {{
        font-size: 24px;
        font-weight: 700;
        margin-top: 20px;
        margin-bottom: 20px;
        color: {accent};
        animation: slideInRight 0.6s ease-in-out;
        padding-bottom: 10px;
        border-bottom: 2px solid {accent};
        opacity: 0.95;
    }}

    /* Divider */
    .divider {{
        height: 1px;
        background: linear-gradient(90deg, rgba(0,0,0,0) 0%, {border_color} 50%, rgba(0,0,0,0) 100%);
        margin: 30px 0;
    }}

    /* Highlight Box */
    .highlight {{
        padding: 16px 20px;
        border-radius: 12px;
        background: {accent}15;
        border-left: 4px solid {accent};
        color: {text_color};
        font-weight: 500;
        animation: fadeIn 1s ease-in-out;
        box-shadow: 0px 2px 8px rgba(0,0,0,0.04);
    }}

    .highlight-success {{
        background: rgba(16, 185, 129, 0.1);
        border-left-color: #10B981;
        color: {text_color};
    }}

    .highlight-warning {{
        background: rgba(245, 158, 11, 0.1);
        border-left-color: #F59E0B;
        color: {text_color};
    }}

    .highlight-error {{
        background: rgba(239, 68, 68, 0.1);
        border-left-color: #EF4444;
        color: {text_color};
    }}

    /* Info badge */
    .info-badge {{
        display: inline-block;
        padding: 6px 12px;
        border-radius: 8px;
        background: {accent}25;
        color: {accent};
        font-size: 12px;
        font-weight: 600;
        margin: 5px 5px 5px 0;
    }}

    /* Custom button styling */
    .stButton > button {{
        border-radius: 10px !important;
        font-weight: 600 !important;
        padding: 10px 24px !important;
        transition: all 0.3s ease !important;
        border: 1px solid {accent} !important;
        background: linear-gradient(135deg, {accent}, {secondary_accent}) !important;
        color: white !important;
    }}

    .stButton > button:hover {{
        transform: translateY(-2px) !important;
        box-shadow: 0px 8px 20px rgba(99, 102, 241, 0.3) !important;
    }}

    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] button {{
        color: {text_color} !important;
        font-weight: 600 !important;
    }}

    .stTabs [aria-selected="true"] {{
        color: {accent} !important;
    }}

    /* Dataframe styling */
    .stDataFrame {{
        color: {text_color} !important;
    }}

    /* Metric label styling */
    [data-testid="stMetricLabel"] {{
        color: {text_color} !important;
        font-weight: 600 !important;
    }}

    /* Metric value styling */
    [data-testid="stMetricValue"] {{
        color: {metric_text} !important;
    }}

    /* Footer styles */
    .footer-wrapper {{
        margin-top: 50px;
        padding-top: 30px;
        border-top: 2px solid {border_color};
        text-align: center;
        animation: fadeIn 1.2s ease-in-out;
    }}

    .footer-content {{
        color: {text_color};
        opacity: 0.85;
        font-size: 14px;
        margin: 8px 0;
    }}

    .footer-heart {{
        color: #EF4444;
        animation: pulse 1.5s ease-in-out infinite;
    }}

    @keyframes pulse {{
        0%, 100% {{ opacity: 0.6; }}
        50% {{ opacity: 1; }}
    }}

    /* Theme toggle button styling */
    .theme-toggle {{
        font-size: 28px;
        cursor: pointer;
        transition: all 0.3s ease;
        padding: 8px;
        border-radius: 10px;
        background: {accent}15;
    }}

    .theme-toggle:hover {{
        transform: rotate(20deg) scale(1.15);
        background: {accent}25;
    }}

    /* File uploader */
    .stFileUploader {{
        color: {text_color} !important;
    }}

    /* Animated gradient background shifts */
    .stApp {{
        background: linear-gradient(-45deg, {bg_color}, {bg_color});
        background-size: 400% 400%;
        animation: gradientShift 15s ease infinite;
    }}

    @keyframes gradientShift {{
        0% {{ background-position: 0% 50%; }}
        50% {{ background-position: 100% 50%; }}
        100% {{ background-position: 0% 50%; }}
    }}

    /* Data flow animation - horizontal lines */
    [data-testid="stAppViewContainer"]::before {{
        content: '';
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: repeating-linear-gradient(
            90deg,
            transparent,
            transparent 200px,
            {accent}03 200px,
            {accent}03 210px
        );
        animation: flowRight 8s linear infinite;
        pointer-events: none;
        z-index: 0;
    }}

    @keyframes flowRight {{
        0% {{ transform: translateX(0); }}
        100% {{ transform: translateX(210px); }}
    }}

    /* Responsive Design */
    @media (max-width: 768px) {{
        .main-title {{
            font-size: 32px;
        }}
        
        .section-title {{
            font-size: 20px;
        }}
    }}

    </style>
""", unsafe_allow_html=True)

# -------------------------------
# HEADER WITH TOP-RIGHT THEME TOGGLE
# -------------------------------
# Create columns for header layout
header_col1, header_col2 = st.columns([5, 1])

with header_col1:
    st.markdown('<div class="header-container"><div class="hero-card">', unsafe_allow_html=True)
    st.markdown('<div class="main-title">📊 DriftWatch</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-text">Smart data drift monitoring with clean visuals, alerts, and downloadable reports.</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-badges"><span class="info-badge">Realtime insights</span><span class="info-badge">Auto drift detection</span><span class="info-badge">Download reports</span></div>', unsafe_allow_html=True)
    st.markdown('</div></div>', unsafe_allow_html=True)

with header_col2:
    st.markdown('<div class="theme-toggle-container">', unsafe_allow_html=True)
    if st.button("🌙" if st.session_state.theme == "Light Mode" else "☀️", key="theme_toggle", help="Toggle Dark/Light Mode"):
        st.session_state.theme = "Dark Mode" if st.session_state.theme == "Light Mode" else "Light Mode"
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

st.markdown(f'<div class="highlight" style="background: {secondary_accent}10; border-left-color: {secondary_accent};">🚀 Upload your dataset to detect and monitor data drift with interactive insights and visual analysis.</div>', unsafe_allow_html=True)

# -------------------------------
# File Upload Section
# -------------------------------
st.markdown('<div class="section-title">📂 Upload Your Dataset</div>', unsafe_allow_html=True)
st.markdown('<div class="upload-card">', unsafe_allow_html=True)
st.markdown(f'<div class="highlight" style="background: {accent}10; border-left-color: {accent};">📌 Accepted format: CSV files only • Recommended 100+ rows for best results</div>', unsafe_allow_html=True)
file = st.file_uploader("Choose a CSV file", type=["csv"], label_visibility="collapsed")
mode = st.radio(
    "Select Mode",
    ["Real Data", "Simulated Drift"],
    horizontal=True
)
st.markdown('</div>', unsafe_allow_html=True)

# -------------------------------
# Main Analysis Flow
# -------------------------------
if file:
    data = pd.read_csv(file)
    #data = pd.read_csv(file)

    if len(data) < 50:
        st.warning("⚠️ Dataset is small. Drift results may be less reliable.")
    # Display file info
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f'<div class="card-metric"><b>📊 Rows</b><br><h3 style="margin:5px 0; color:{metric_text}">{len(data)}</h3></div>', unsafe_allow_html=True)
    with col2:
        st.markdown(f'<div class="card-metric"><b>📋 Columns</b><br><h3 style="margin:5px 0; color:{metric_text}">{len(data.columns)}</h3></div>', unsafe_allow_html=True)
    with col3:
        st.markdown(f'<div class="card-metric"><b>✓ Status</b><br><h3 style="margin:5px 0; color:#10B981">Ready</h3></div>', unsafe_allow_html=True)

    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

    # Tabs for organization
    tab1, tab2, tab3 = st.tabs(["📊 Overview", "📋 Feature Drift", "📈 Visual Analysis"])

    # -------------------------------
    # TAB 1: Overview
    # -------------------------------
    with tab1:
        st.markdown('<div class="section-title">👀 Dataset Preview</div>', unsafe_allow_html=True)

        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.dataframe(data.head(10), use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

        st.markdown('<div class="highlight">🔍 <b>Ready to analyze?</b> Click the button below to run drift detection on your data.</div>', unsafe_allow_html=True)
        
        analyze_btn_col1, analyze_btn_col2, analyze_btn_col3 = st.columns([1, 1, 2])
        with analyze_btn_col1:
            if st.button("🚀 Run Drift Analysis", key="analyze_btn", use_container_width=True):
                with st.spinner("⏳ Analyzing data for drift patterns..."):
                    result = detect_drift(data,  simulate=(mode == "Simulated Drift"))
                    st.session_state["result"] = result

    # -------------------------------
    # RESULTS DISPLAY
    # -------------------------------
    if "result" in st.session_state:
        result = st.session_state["result"]

        # Results on Overview Tab
        with tab1:
            st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
            st.markdown('<div class="section-title">📊 Drift Detection Results</div>', unsafe_allow_html=True)

            metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)

            with metric_col1:
                st.markdown(f'<div class="card-metric">', unsafe_allow_html=True)
                st.markdown(f'<b style="color:{text_color}">📊 Drift Score</b><br><h2 style="margin:8px 0; color:{metric_text}">{result["overall_score"]:.2f}</h2>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)

            with metric_col2:
                st.markdown(f'<div class="card-metric">', unsafe_allow_html=True)
                st.markdown(f'<b style="color:{text_color}">🎯 Top Feature</b><br><p style="margin:8px 0; color:{metric_text}; font-weight: bold; font-size: 16px;">{result["top_feature"]}</p>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)

            with metric_col3:
                st.markdown(f'<div class="card-metric">', unsafe_allow_html=True)
                status_color = "#EF4444" if result["status"] == "High Drift" else "#F59E0B" if result["status"] == "Medium Drift" else "#10B981"
                st.markdown(f'<b style="color:{text_color}">⚡ Status</b><br><p style="margin:8px 0; color:{status_color}; font-weight: bold; font-size: 16px;">{result["status"]}</p>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)

            with metric_col4:
                st.markdown(f'<div class="card-metric">', unsafe_allow_html=True)
                st.markdown(f'<b style="color:{text_color}">🔍 Features Analyzed</b><br><h2 style="margin:8px 0; color:{metric_text}">{len(result["feature_drift"])}</h2>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
            
            st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

            # Status Alert
            if result["status"] == "High Drift":
                st.markdown('<div class="highlight highlight-error">🚨 <b>Alert:</b> High Drift Detected - Investigate data changes immediately</div>', unsafe_allow_html=True)
            elif result["status"] == "Medium Drift":
                st.markdown('<div class="highlight highlight-warning">⚠️ <b>Warning:</b> Medium Drift Detected - Monitor data closely</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="highlight highlight-success">✅ <b>Good News:</b> Low Drift - Data remains stable</div>', unsafe_allow_html=True)
            st.markdown(f"""
            <div class="highlight">
            📘 <b>How Drift is Calculated:</b><br>
            • PSI (Population Stability Index) measures distribution shift<br>
            • KS Test checks statistical difference between datasets<br>
            • Mean shift is normalized for fair comparison<br>
            </div>
            """, unsafe_allow_html=True)
        # -------------------------------
        # TAB 2: Feature Drift Details
        # -------------------------------
        with tab2:
            st.markdown('<div class="section-title">📋 Individual Feature Drift Analysis</div>', unsafe_allow_html=True)

            drift_df = pd.DataFrame(result["feature_drift"]).T
            
            st.markdown('<div class="highlight">📊 Detailed drift metrics for each feature in your dataset</div>', unsafe_allow_html=True)

            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.dataframe(drift_df, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

            st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

            st.markdown('<div class="section-title">📊 Statistical Comparison</div>', unsafe_allow_html=True)

            col1, col2 = st.columns(2)

            train = result["train"]
            new = result["new"]

            with col1:
                st.markdown('<div class="card">', unsafe_allow_html=True)
                st.markdown('<b>🎓 Training Dataset Statistics</b>', unsafe_allow_html=True)
                st.dataframe(train.describe(), use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)

            with col2:
                st.markdown('<div class="card">', unsafe_allow_html=True)
                st.markdown('<b>🔍 New Dataset Statistics</b>', unsafe_allow_html=True)
                st.dataframe(new.describe(), use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)

            st.markdown('<div class="highlight">💡 <b>Insight:</b> Differences in mean, std, min, max between training and new data indicate potential drift.</div>', unsafe_allow_html=True)
            st.download_button(
                "📥 Download Drift Report",
                drift_df.to_csv(),
                file_name="drift_report.csv"
            )
        # -------------------------------
        # TAB 3: Visual Analysis
        # -------------------------------
        with tab3:
            st.markdown('<div class="section-title">📈 Visual Drift Analysis</div>', unsafe_allow_html=True)

            train = result["train"]
            new = result["new"]
            feature = st.selectbox(
                "Select feature to visualize",
                list(train.columns),
                index=list(train.columns).index(result["top_feature"])
            )
            st.markdown(f'<div class="highlight">🔍 Visual comparison for <b>{feature}</b> (top drifting feature)</div>', unsafe_allow_html=True)

            col1, col2 = st.columns(2)

            # Set matplotlib style based on theme
            if st.session_state.theme == "Dark Mode":
                plt.style.use('dark_background')
                hist_color1, hist_color2 = "#8B5CF6", "#EC4899"
                text_color_plot = "#F0F2F5"
            else:
                plt.style.use('default')
                hist_color1, hist_color2 = "#6366F1", "#EC4899"
                text_color_plot = "#0F1419"

            feature_train = train[feature]
            feature_new = new[feature]
            is_numeric_feature = pd.api.types.is_numeric_dtype(feature_train)

            if not is_numeric_feature:
                combined = pd.Categorical(pd.concat([feature_train, feature_new], ignore_index=True))
                category_labels = combined.categories.astype(str).tolist()
                codes = combined.codes
                feature_train = pd.Series(codes[: len(feature_train)], index=feature_train.index)
                feature_new = pd.Series(codes[len(feature_train) :], index=feature_new.index)

            # Histogram / categorical counts
            with col1:
                st.markdown('<div class="card">', unsafe_allow_html=True)
                st.markdown(f'<b style="color:{text_color}">📊 Distribution Comparison (Histogram)</b>', unsafe_allow_html=True)
                fig1, ax1 = plt.subplots(figsize=(8, 5), facecolor=chart_bg)
                ax1.set_facecolor(chart_bg)

                if is_numeric_feature:
                    ax1.hist(feature_train, alpha=0.6, label="Training Data", bins=30, color=hist_color1, edgecolor="white", linewidth=0.5)
                    ax1.hist(feature_new, alpha=0.6, label="New Data", bins=30, color=hist_color2, edgecolor="white", linewidth=0.5)
                    ax1.set_xlabel("Value", fontsize=10, color=text_color_plot)
                else:
                    train_counts = feature_train.value_counts().sort_index()
                    new_counts = feature_new.value_counts().sort_index()
                    categories = sorted(set(train_counts.index).union(new_counts.index))
                    train_counts = train_counts.reindex(categories, fill_value=0)
                    new_counts = new_counts.reindex(categories, fill_value=0)
                    x = np.arange(len(categories))
                    width = 0.35
                    ax1.bar(x - width / 2, train_counts, width, label="Training Data", color=hist_color1, alpha=0.7)
                    ax1.bar(x + width / 2, new_counts, width, label="New Data", color=hist_color2, alpha=0.7)
                    ax1.set_xticks(x)
                    ax1.set_xticklabels([category_labels[i] for i in categories], rotation=45, ha='right', color=text_color_plot)
                    ax1.set_xlabel("Category", fontsize=10, color=text_color_plot)

                ax1.legend(fontsize=10, facecolor=chart_bg, edgecolor=text_color_plot)
                ax1.set_title(f"{feature} Distribution Comparison", fontsize=12, fontweight="bold", color=text_color_plot)
                ax1.set_ylabel("Frequency", fontsize=10, color=text_color_plot)
                ax1.grid(alpha=0.2, color=text_color_plot, linestyle='--')
                ax1.tick_params(colors=text_color_plot)
                plt.tight_layout()
                st.pyplot(fig1, width='stretch')
                st.markdown('</div>', unsafe_allow_html=True)

            # Box Plot / categorical counts comparison
            with col2:
                st.markdown('<div class="card">', unsafe_allow_html=True)
                st.markdown(f'<b style="color:{text_color}">📦 Box Plot Comparison</b>', unsafe_allow_html=True)
                fig2, ax2 = plt.subplots(figsize=(8, 5), facecolor=chart_bg)
                ax2.set_facecolor(chart_bg)

                if is_numeric_feature:
                    bp = ax2.boxplot([feature_train, feature_new], labels=["Training Data", "New Data"], patch_artist=True, widths=0.6)
                    bp["boxes"][0].set_facecolor(hist_color1)
                    bp["boxes"][0].set_alpha(0.7)
                    bp["boxes"][1].set_facecolor(hist_color2)
                    bp["boxes"][1].set_alpha(0.7)
                    for element in ["whiskers", "fliers", "means", "medians", "caps"]:
                        plt.setp(bp[element], color=text_color_plot, linewidth=1.5)
                    for patch in bp["boxes"]:
                        patch.set_edgecolor(text_color_plot)
                        patch.set_linewidth(1.5)
                    ax2.set_ylabel("Value", fontsize=10, color=text_color_plot)
                else:
                    train_counts = feature_train.value_counts().sort_index()
                    new_counts = feature_new.value_counts().sort_index()
                    categories = sorted(set(train_counts.index).union(new_counts.index))
                    train_counts = train_counts.reindex(categories, fill_value=0)
                    new_counts = new_counts.reindex(categories, fill_value=0)
                    diff = new_counts - train_counts
                    x = np.arange(len(categories))
                    bar_colors = [hist_color2 if v >= 0 else hist_color1 for v in diff]
                    ax2.bar(x, diff, color=bar_colors, edgecolor=text_color_plot, alpha=0.8)
                    ax2.axhline(0, color=text_color_plot, linewidth=1, linestyle='--')
                    ax2.set_xticks(x)
                    ax2.set_xticklabels([category_labels[i] for i in categories], rotation=45, ha='right', color=text_color_plot)
                    ax2.set_ylabel("Count difference", fontsize=10, color=text_color_plot)

                ax2.set_title(f"{feature} Box Plot Comparison", fontsize=12, fontweight="bold", color=text_color_plot)
                ax2.grid(alpha=0.2, axis='y', color=text_color_plot, linestyle='--')
                ax2.tick_params(colors=text_color_plot)
                plt.tight_layout()
                st.pyplot(fig2, width='stretch')
                st.markdown('</div>', unsafe_allow_html=True)

            st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

            st.markdown(f'<div class="highlight highlight-success">💡 <b>How to interpret:</b> Significant changes in distribution shape, mean, or variance indicate data drift. The more the distributions differ, the higher the drift.</div>', unsafe_allow_html=True)

else:
    st.markdown(f'<div class="highlight" style="text-align: center; padding: 60px 20px; background: {card_bg}; border: 2px dashed {border_color}; border-radius: 16px;"><h3 style="color:{text_color}; margin: 0;">👆 Start by uploading a CSV file</h3><p style="color:{text_color}; opacity: 0.8; margin-top: 10px;">Drag and drop or click to select your dataset to begin drift detection</p></div>', unsafe_allow_html=True)

# ================================
# FOOTER
# ================================
st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

st.markdown(f'''
    <div class="footer-wrapper">
        <div class="footer-content">
            <p style="margin: 0; color: {text_color};"><span class="footer-heart">❤️</span> Made with care for Data Quality</p>
            <p style="font-size: 13px; opacity: 0.7; margin-top: 8px; color: {text_color};"><b>Thank you for using DriftWatch!</b> 🙏</p>
            <p style="font-size: 11px; opacity: 0.6; margin-top: 10px; color: {text_color};">v1.0 | Data Drift Detection & Monitoring</p>
        </div>
    </div>
''', unsafe_allow_html=True)