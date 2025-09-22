import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
import firebase_admin
from firebase_admin import credentials, db 

# ========================= # Page Config # =========================
st.set_page_config(page_title="Project Drishti", layout="wide", initial_sidebar_state="collapsed")

# ========================= # Custom Theme Styling # =========================
st.markdown("""
    <style>
    /* Whole page background */
    .reportview-container {
        background-color: #ffffff;
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #aa5ee0; /* Dark blue */
        color: white;
    }

    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3,
    [data-testid="stSidebar"] label, [data-testid="stSidebar"] span {
        color: white !important;
    }
    /* Make radio label text white */
    [data-testid="stSidebar"] .stRadio > label, 
    [data-testid="stSidebar"] .stRadio div {
        color: white !important;
        font: 28px !important;
        font-weight: bold !important;
    }

    [data-testid="stSidebar"] .stRadio span {
        color: white !important;
    }

    /* Main headers */
    h1, h2, h3 {
        color: #fcfcfc;
    }

    /* Dataframe table font */
    .stDataFrame {
        font-size: 20px;
    }
    </style>
""", unsafe_allow_html=True)

# ========================= # Sidebar with Logo # =========================
try:
    st.sidebar.image("logo.png", width=150)  # Upload this file to repo root
except Exception:
    st.sidebar.markdown("**Project Drishti**")
st.sidebar.title("Navigation")
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["Dashboard", "Upload Excel/CSV", "Student Attendance", "Student Marks", "Fees Status", "About"])

# ========================= # Title # =========================
st.title("🏫 Project Drishti – Student Success Early Warning System")
st.markdown("Helping educators move from **reactive** to **proactive** mentoring")

# ========================= # Upload Page # =========================
with tab2:
    st.header("Upload Student Data")
    uploaded_file = st.file_uploader("Choose an Excel or CSV file", type=["xlsx","xls","csv"])

    if uploaded_file is not None:
        try:
            if uploaded_file.name.endswith(("xlsx","xls")):
                df = pd.read_excel(uploaded_file)
            else:
                df = pd.read_csv(uploaded_file)

            st.success(f"✅ Loaded file with {df.shape[0]} rows and {df.shape[1]} columns.")
            st.write("Here is a sample of your data:")
            st.dataframe(df.head())
            st.session_state["data"] = df

        except Exception as e:
            st.error(f"Error reading file: {e}")

# ========================= # Dashboard Page # =========================
with tab1:
    if "data" not in st.session_state:
        st.warning("⚠️ Please upload student data first from the sidebar.")
    else:
        df = st.session_state["data"].copy()

        required_cols = ["StudentID", "Attendance", "Marks", "FeesDue"]
        missing = [c for c in required_cols if c not in df.columns]
        if missing:
            st.error(f"Missing columns: {missing}. Please upload correct file.")
        else:
            # === Risk Score Calculation ===
            df["FeesDeduction"] = df["FeesDue"] * 20
            df["RiskScore"] = 100 - (0.4*df["Attendance"] + 0.4*df["Marks"] + df["FeesDeduction"])
            df["RiskScore"] = df["RiskScore"].clip(lower=0).round(1)

            # === Assign Risk Levels ===
            def risk_level(score):
                if score >= 75:
                    return "High Risk"
                elif score >= 50:
                    return "Medium Risk"
                else:
                    return "Low Risk"

            df["Risk"] = df["RiskScore"].apply(risk_level)

            # === Color-coded Dataframe ===
            def highlight_risk(val):
                if val == "High Risk":
                    return "background-color: red; color: white;"
                elif val == "Medium Risk":
                    return "background-color: yellow; color: black;"
                elif val == "Low Risk":
                    return "background-color: lightgreen; color: black;"
                return ""

            st.subheader("📋 Student Risk Scores")
            st.dataframe(df.style.applymap(highlight_risk, subset=["Risk"]))

            # === Risk Distribution Pie Chart ===
            col1, col2 = st.columns([1, 1])
            with col1:
                st.subheader("Student Dropout Risk")
                st.markdown("### Risk Level Color Codes")
                st.markdown("""
                <div style="display: flex; justify-content: space-between; font-size: 18px;">
                <div style="text-align: left;">🔴 High Dropout Risk</div>
                <div style="text-align: center;">🟡 Medium Dropout Risk</div>
                <div style="text-align: right;">🟢 Low Dropout Risk</div>
                </div>
                """, unsafe_allow_html=True)
                risk_counts = df["Risk"].value_counts()
                fig1, ax1 = plt.subplots()
                colors = ['#90ee90', '#f5d90a', '#ff4b4b']  # red, yellow, lightgreen
                labels = [f"{risk} ({count})" for risk, count in risk_counts.items()]
                sizes = risk_counts.values.tolist()

                ax1.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
                ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
                st.pyplot(fig1)
            
             # === Sorted Risk Table (Scrollable, 5 rows visible) ===
            with col2:
                st.subheader("Students Sorted by Risk Level")

                risk_order = {"High Risk": 0, "Medium Risk": 1, "Low Risk": 2}
                sorted_df = df[["StudentID", "Risk", "RiskScore"]].copy()
                sorted_df["RiskOrder"] = sorted_df["Risk"].map(risk_order)
                sorted_df = sorted_df.sort_values(by=["RiskOrder", "RiskScore"], ascending=[True, False])
                sorted_df = sorted_df.drop(columns="RiskOrder").reset_index(drop=True)

            # Show as scrollable dataframe with ~5 rows visible
                row_height = 35  # px per row approx
                visible_rows = 5
                table_height = row_height * (visible_rows + 1)  # +1 for header

                st.dataframe(sorted_df, height=table_height)

# ========================= # Attendance Page # =========================
with tab3:
    if "data" not in st.session_state:
        st.warning("⚠️ Please upload student data first.")
    else:
        df = st.session_state["data"].copy()
        if "Attendance" not in df.columns:
            st.error("Attendance column missing in uploaded file.")
        else:
            st.header("📅 Student Attendance Overview")
            st.bar_chart(df.set_index("StudentID")["Attendance"])

# ========================= # Fees Status Page # =========================
with tab5:
    if "data" not in st.session_state:
        st.warning("⚠️ Please upload student data first.")
    else:
        df = st.session_state["data"].copy()
        if "FeesDue" not in df.columns:
            st.error("FeesDue column missing in uploaded file.")
        else:
            st.header("💰 Student Fees Status")

            # Color coding function
            def highlight_fees(val):
                if val == 0:
                    return "background-color: lightgreen; color: black;"
                else:
                    return "background-color: red; color: white;"

            st.dataframe(df[["StudentID", "FeesDue"]].style.applymap(highlight_fees, subset=["FeesDue"]))

# ========================= # Marks Page # =========================
with tab4:
    if "data" not in st.session_state:
        st.warning("⚠️ Please upload student data first.")
    else:
        df = st.session_state["data"].copy()
        if "Marks" not in df.columns:
            st.error("Marks column missing in uploaded file.")
        else:
            st.header("📊 Student Marks Overview")
            st.line_chart(df.set_index("StudentID")["Marks"])


# ========================= # About Page # =========================
with tab6:
    st.header("ℹ️ About Project Drishti")
    st.markdown("""
    **Drishti** is an early warning system for schools/colleges. It unifies student data and shows real-time **Student at Risk (StAR) scores**. 
    ### Features
    - **High Risk** students = 🔴 Red
    - **Medium Risk** students = 🟠 Orange
    - **Low Risk** students = 🟢 Green
    - Upload Excel/CSV files directly
    - Easy, intuitive portal look
    """)
