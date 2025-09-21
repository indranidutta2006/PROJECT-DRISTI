import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

# ========================= # Page Config # =========================
st.set_page_config(page_title="Project Drishti", layout="wide", initial_sidebar_state="expanded")

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
        font-size: 14px;
    }
    </style>
""", unsafe_allow_html=True)

# ========================= # Sidebar with Logo # =========================
try:
    st.sidebar.image("logo.png", width=150)  # Upload this file to repo root
except Exception:
    st.sidebar.markdown("**Project Drishti**")
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Dashboard", "Upload Excel/CSV", "Student Attendance", "Student Marks", "Fees Status", "About"])

# ========================= # Title # =========================
st.title("🏫 Project Drishti – Student Success Early Warning System")
st.markdown("Helping educators move from **reactive** to **proactive** mentoring")

# ========================= # Upload Page # =========================
if page == "Upload Data":
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
elif page == "Dashboard":
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
                    return "background-color: orange; color: black;"
                elif val == "Low Risk":
                    return "background-color: lightgreen; color: black;"
                return ""

            st.subheader("📋 Student Risk Scores")
            st.dataframe(df.style.applymap(highlight_risk, subset=["Risk"]))

            # === Risk Distribution Pie Chart ===
            st.subheader("🥧 Risk Distribution (Pie Chart)")
            risk_counts = df["Risk"].value_counts()
            fig1, ax1 = plt.subplots()
            colors = ['#90ee90', '#ffa500', '#ff4b4b']  # red, orange, lightgreen
            labels = [f"{risk} ({count})" for risk, count in risk_counts.items()]
            sizes = risk_counts.values.tolist()

            ax1.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
            ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
            st.pyplot(fig1)
            
             # === Sorted Risk Table with Slider ===
            st.subheader("📊 Students Sorted by Risk Level")

            risk_order = {"High Risk": 0, "Medium Risk": 1, "Low Risk": 2}
            sorted_df = df[["StudentID", "Risk", "RiskScore"]].copy()
            sorted_df["RiskOrder"] = sorted_df["Risk"].map(risk_order)
            sorted_df = sorted_df.sort_values(by=["RiskOrder", "RiskScore"], ascending=[True, False])
            sorted_df = sorted_df.drop(columns="RiskOrder").reset_index(drop=True)

            # Slider to navigate students
            total_students = len(sorted_df)
            start_index = st.slider(
            "Scroll through students",
            min_value=0,
            max_value=max(0, total_students - 5),
            value=0,
            step=5
            )

            # Show 5 students at a time
            st.table(sorted_df.iloc[start_index:start_index + 5])

# ========================= # Attendance Page # =========================
elif page == "Student Attendance":
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
elif page == "Fees Status":
    if "data" not in st.session_state:
        st.warning("⚠️ Please upload student data first.")
    else:
        df = st.session_state["data"].copy()
        if "FeesDue" not in df.columns:
            st.error("FeesDue column missing in uploaded file.")
        else:
            st.header("💰 Student Fees Status")
            st.dataframe(df[["StudentID", "FeesDue"]])
            st.bar_chart(df.set_index("StudentID")["FeesDue"])

# ========================= # Marks Page # =========================
elif page == "Student Marks":
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
elif page == "About":
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
