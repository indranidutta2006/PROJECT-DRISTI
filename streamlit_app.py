import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# ========================= # Page Config # =========================
st.set_page_config(page_title="Project Drishti", layout="wide", initial_sidebar_state="collapsed")

# ========================= # Custom Theme Styling # =========================
st.markdown("""
    <style>
    [data-testid="stSidebar"] {
        background-color: #aa5ee0; 
        color: white;
    }
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3,
    [data-testid="stSidebar"] label, [data-testid="stSidebar"] span {
        color: white !important;
    }
    [data-testid="stSidebar"] .stRadio > label, 
    [data-testid="stSidebar"] .stRadio div {
        color: white !important;
        font-size: 20px !important;
        font-weight: bold !important;
    }
    </style>
""", unsafe_allow_html=True)

# ========================= # Sidebar with Logo # =========================
try:
    st.sidebar.image("logo.png", width=150)
except Exception:
    st.sidebar.markdown("**Project Drishti**")

st.sidebar.title("Navigation")
tab1, tab2, tab3, tab4, tab5, tab6, tab7,tab8 = st.tabs(
    ["Upload Excel/CSV", "Dashboard", "Attendance", "Marks", "Assignments", "Fees Status", "Student Details", "About"]
)

# ========================= # Upload Page # =========================
with tab1:
    st.header("Upload Student Data")
    uploaded_file = st.file_uploader("Choose an Excel or CSV file", type=["xlsx","xls","csv"])

    if uploaded_file is not None:
        try:
            if uploaded_file.name.endswith(("xlsx", "xls")):
                df = pd.read_excel(uploaded_file)
            else:
                df = pd.read_csv(uploaded_file, index_col=False)

            df.reset_index(drop=True, inplace=True)
            df = df.loc[:, ~df.columns.str.contains('^Unnamed', case=False, na=False)]

            # ✅ New required columns
            required_cols = [
                "StudentID", "Attendance", "LastSemMarks", "CurrentSemMarks",
                "BacklogAssignments", "AssignmentSubmission", "FeesDue"
            ]
            missing = [c for c in required_cols if c not in df.columns]

            if missing:
                st.error(f"Missing columns: {missing}. Please upload correct file.")
            else:
                st.session_state["data"] = df
                st.success(f"✅ Loaded file with {df.shape[0]} rows and {df.shape[1]} columns.")
                st.write("Here is a sample of your data:")
                st.dataframe(df.head())

        except Exception as e:
            st.error(f"Error reading file: {e}")

# ========================= # Dashboard Page # =========================
with tab2:
    st.title("🏫 Project Drishti – Student Success Early Warning System")
    st.markdown("Helping educators move from **reactive** to **proactive** mentoring")

    if "data" not in st.session_state:
        st.warning("⚠️ Please upload student data first.")
    else:
        df = st.session_state["data"].copy()

        # === Risk Score Calculation ===
        df["AvgMarks"] = (df["LastSemMarks"] + df["CurrentSemMarks"]) / 2
        df["FeesPenalty"] = df["FeesDue"] * 20
        df["RiskScore"] = 100 - (
            0.3 * df["Attendance"] +
            0.3 * df["AvgMarks"] +
            0.2 * df["AssignmentSubmission"] -
            5 * df["BacklogAssignments"] +
            df["FeesPenalty"]
        )
        df["RiskScore"] = df["RiskScore"].clip(lower=0).round(1)

        def risk_level(score):
            if score >= 75:
                return "High Risk"
            elif score >= 50:
                return "Medium Risk"
            else:
                return "Low Risk"

        df["Risk"] = df["RiskScore"].apply(risk_level)

        st.subheader("📋 Student Risk Scores")
        df_display = df.copy()
        df_display.insert(0, "Sl No", range(1, len(df_display) + 1))

        def highlight_risk(val):
            if val == "High Risk":
                return "background-color: red; color: white;"
            elif val == "Medium Risk":
                return "background-color: yellow; color: black;"
            else:
                return "background-color: lightgreen; color: black;"

        st.dataframe(df_display.style.applymap(highlight_risk, subset=["Risk"]), hide_index=True)

# ========================= # Attendance Page # =========================
with tab3:
    if "data" in st.session_state:
        df = st.session_state["data"].copy()
        st.header("📅 Attendance Overview")
        st.bar_chart(df.set_index("StudentID")["Attendance"])

# ========================= # Marks Page # =========================
with tab4:
    if "data" in st.session_state:
        df = st.session_state["data"].copy()
        st.header("📊 Marks Overview")
        st.line_chart(df.set_index("StudentID")[["LastSemMarks", "CurrentSemMarks"]])

# ========================= # Assignments Page # =========================
with tab5:
    if "data" in st.session_state:
        df = st.session_state["data"].copy()
        st.header("📝 Assignments Overview")
        st.dataframe(df[["StudentID", "BacklogAssignments", "AssignmentSubmission"]])

# ========================= # Fees Status Page # =========================
with tab6:
    if "data" in st.session_state:
        df = st.session_state["data"].copy()
        st.header("💰 Student Fees Status")

        def highlight_fees(val):
            return "background-color: red; color: white;" if val == 1 else "background-color: lightgreen; color: white;"

        st.dataframe(df[["StudentID", "FeesDue"]].style.applymap(highlight_fees, subset=["FeesDue"]))

# ========================= # Student Details Page # =========================
with tab7:  # Student Tab
    if "data" not in st.session_state:
        st.warning("⚠️ Please upload student data first.")
    else:
        df = st.session_state["data"].copy()

        required_cols = ["StudentID", "Attendance", "LastSemMarks", "CurrentSemMarks", 
                         "BacklogAssignments", "AssignmentSubmission", "FeesDue"]
        missing = [c for c in required_cols if c not in df.columns]
        if missing:
            st.error(f"Missing columns: {missing}. Please upload correct file.")
        else:
            # === Risk Score Calculation (same logic as Dashboard) ===
            df["MarksAvg"] = (df["LastSemMarks"] + df["CurrentSemMarks"]) / 2
            df["AssignmentPenalty"] = df["BacklogAssignments"] * 5
            df["FeesDeduction"] = df["FeesDue"] * 20

            df["RiskScore"] = 100 - (
                0.3 * df["Attendance"] +
                0.3 * df["MarksAvg"] +
                0.2 * df["AssignmentSubmission"] -
                df["AssignmentPenalty"] -
                df["FeesDeduction"]
            )
            df["RiskScore"] = df["RiskScore"].clip(lower=0).round(1)

            def risk_level(score):
                if score >= 75:
                    return "High Risk"
                elif score >= 50:
                    return "Medium Risk"
                else:
                    return "Low Risk"

            df["Risk"] = df["RiskScore"].apply(risk_level)

            # === Student Lookup ===
            st.header("🔍 Individual Student Overview")
            student_id = st.selectbox("Select Student ID", df["StudentID"].unique())

            student = df[df["StudentID"] == student_id].iloc[0]

            st.subheader(f"📌 Student ID: {student_id}")
            st.write(f"**Attendance:** {student['Attendance']}%")
            st.write(f"**Last Sem Marks:** {student['LastSemMarks']}")
            st.write(f"**Current Sem Marks:** {student['CurrentSemMarks']}")
            st.write(f"**Backlog Assignments:** {student['BacklogAssignments']}")
            st.write(f"**Assignments Submitted:** {student['AssignmentSubmission']}%")
            st.write(f"**Fees Due:** {'Yes' if student['FeesDue']==1 else 'No'}")
            st.write(f"**Risk Score:** {student['RiskScore']}")
            st.markdown(f"**Dropout Risk:** "
                        f"<span style='color: {'red' if student['Risk']=='High Risk' else 'orange' if student['Risk']=='Medium Risk' else 'green'}; "
                        f"font-weight: bold;'>{student['Risk']}</span>", unsafe_allow_html=True)
# ========================= # About Page # =========================
with tab8:
    st.header("ℹ️ About Project Drishti")
    st.markdown("""
    **Drishti** is an early warning system for schools/colleges. It unifies student data and shows real-time **Student at Risk (StAR) scores**. 
    """)
