
import streamlit as st
import pandas as pd
import plotly.express as px
import sqlite3


# =====================================================
# 1. PAGE CONFIGURATION
# =====================================================

st.set_page_config(
    page_title="Student Grade Management System",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)


# =====================================================
# 2. DATABASE CONFIGURATION
# =====================================================

DB_NAME = "student_records.db"


def get_connection():
    return sqlite3.connect(DB_NAME)


def initialize_database():

    with get_connection() as conn:

        conn.execute("""
            CREATE TABLE IF NOT EXISTS students (
                name TEXT PRIMARY KEY COLLATE NOCASE,
                marks REAL NOT NULL,
                grade TEXT NOT NULL
            )
        """)


# =====================================================
# 3. LOAD STUDENTS FROM DATABASE
# =====================================================

def load_students():

    students = {}

    with get_connection() as conn:

        rows = conn.execute("""
            SELECT name, marks, grade
            FROM students
            ORDER BY name
        """).fetchall()

    for name, marks, grade in rows:

        students[name] = {
            "Marks": marks,
            "Grade": grade
        }

    return students


# =====================================================
# 4. INITIALIZE DATABASE AND SESSION STATE
# =====================================================

initialize_database()

# Load records only when a new session starts.
# Existing session data is not overwritten on reruns.

if "students" not in st.session_state:

    st.session_state["students"] = load_students()


# =====================================================
# 5. CUSTOM CSS
# =====================================================

st.markdown("""
<style>

.stApp {
    background-color: #F4F7FC;
}

.main-title {
    font-size: 36px;
    font-weight: 800;
    color: #172554;
    text-align: center;
    padding: 15px;
}

.sub-title {
    text-align: center;
    color: #64748B;
    font-size: 16px;
    margin-bottom: 25px;
}

div[data-testid="stMetric"] {
    background: linear-gradient(135deg, #FFFFFF, #EAF1FF);
    border: 1px solid #DCE6F5;
    padding: 20px;
    border-radius: 15px;
    box-shadow: 0 3px 12px rgba(0,0,0,0.05);
}

div[data-testid="stMetricLabel"] {
    color: #475569;
    font-weight: 600;
}

div[data-testid="stMetricValue"] {
    color: #1D4ED8;
    font-weight: 800;
}

</style>
""", unsafe_allow_html=True)


# =====================================================
# 6. GRADE CALCULATION
# =====================================================

def calculate_grade(mark):

    if mark >= 90:
        return "A"

    elif mark >= 80:
        return "B"

    elif mark >= 70:
        return "C"

    elif mark >= 60:
        return "D"

    else:
        return "E"


# =====================================================
# 7. SAVE STUDENTS TO DATABASE
# =====================================================

def save_students_to_database(new_students):

    with get_connection() as conn:

        conn.executemany(
            """
            INSERT INTO students (name, marks, grade)
            VALUES (?, ?, ?)
            """,
            [
                (name, details["Marks"], details["Grade"])
                for name, details in new_students.items()
            ]
        )


# =====================================================
# 8. GET STUDENT DATAFRAME
# =====================================================

def get_dataframe():

    records = []

    for name, details in st.session_state["students"].items():

        records.append({
            "Student Name": name,
            "Marks": details["Marks"],
            "Grade": details["Grade"]
        })

    return pd.DataFrame(
        records,
        columns=["Student Name", "Marks", "Grade"]
    )


# =====================================================
# 9. APPLICATION HEADER
# =====================================================

st.markdown(
    '<div class="main-title">'
    '🎓 Student Grade Management System'
    '</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="sub-title">'
    'Student Marks Management & Academic Performance Analysis'
    '</div>',
    unsafe_allow_html=True
)


# =====================================================
# 10. SIDEBAR NAVIGATION
# =====================================================

st.sidebar.title("🎓 Student Portal")

menu = st.sidebar.radio(
    "Navigation",
    [
        "Dashboard",
        "Add Students",
        "Student Results",
        "Performance Analysis"
    ]
)

st.sidebar.markdown("---")

st.sidebar.metric(
    "Total Students",
    len(st.session_state["students"])
)

st.sidebar.caption("Data storage: SQLite + Session State")


# =====================================================
# 11. DASHBOARD
# =====================================================

if menu == "Dashboard":

    st.header("📊 Dashboard Overview")

    if st.session_state["students"]:

        df = get_dataframe()

        col1, col2, col3, col4 = st.columns(4)

        col1.metric(
            "👨‍🎓 Total Students",
            len(df)
        )

        col2.metric(
            "📈 Average Marks",
            f"{df['Marks'].mean():.2f}"
        )

        col3.metric(
            "🏆 Highest Marks",
            f"{df['Marks'].max():.2f}"
        )

        col4.metric(
            "📉 Lowest Marks",
            f"{df['Marks'].min():.2f}"
        )

        st.markdown("---")

        st.subheader("📋 Student Records")

        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True
        )

        grade_data = (
            df["Grade"]
            .value_counts()
            .reindex(["A", "B", "C", "D", "E"], fill_value=0)
            .reset_index()
        )

        grade_data.columns = ["Grade", "Students"]

        fig = px.pie(
            grade_data,
            names="Grade",
            values="Students",
            title="Grade Distribution",
            hole=0.45,
            color_discrete_sequence=px.colors.qualitative.Set2
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    else:

        st.info("No student records available. Please add students.")


# =====================================================
# 12. ADD STUDENTS
# =====================================================

elif menu == "Add Students":

    st.header("➕ Add Student Details")

    st.write("Enter student details and click Save Students.")

    number = st.number_input(
        "Number of students to add",
        min_value=1,
        max_value=100,
        value=1,
        step=1
    )

    st.markdown("---")

    with st.form(
        key="student_entry_form"
    ):

        student_inputs = []

        for i in range(int(number)):

            st.subheader(f"👨‍🎓 Student {i + 1}")

            col1, col2 = st.columns(2)

            with col1:

                name = st.text_input(
                    "Student Name",
                    key=f"student_name_{i}"
                )

            with col2:

                marks = st.number_input(
                    "Student Marks",
                    min_value=0.0,
                    max_value=100.0,
                    value=0.0,
                    step=0.5,
                    key=f"student_marks_{i}"
                )

            student_inputs.append({
                "name": name.strip(),
                "marks": marks
            })

        save_button = st.form_submit_button(
            "💾 Save Students",
            use_container_width=True
        )

        if save_button:

            errors = []

            new_students = {}

            existing_names = {
                name.casefold()
                for name in st.session_state["students"]
            }

            # Validate all student inputs

            for student in student_inputs:

                name = student["name"]
                marks = student["marks"]

                if not name:

                    errors.append(
                        "Student name cannot be empty."
                    )

                elif not name.replace(" ", "").isalpha():

                    errors.append(
                        f"Invalid student name: {name}. "
                        "Only alphabets are allowed."
                    )

                elif (
                    name.casefold() in existing_names
                    or name.casefold() in {
                        s.casefold() for s in new_students
                    }
                ):

                    errors.append(
                        f"Student already exists: {name}"
                    )

                else:

                    new_students[name] = {
                        "Marks": marks,
                        "Grade": calculate_grade(marks)
                    }

            # Save records only if all inputs are valid

            if errors:

                for error in errors:
                    st.error(error)

            else:

                try:

                    # FIRST: Save permanently to SQLite

                    if new_students:
                        save_students_to_database(new_students)

                    # SECOND: Update session state

                    st.session_state["students"].update(
                        new_students
                    )

                    st.success(
                        f"Successfully saved "
                        f"{len(new_students)} student(s)!"
                    )

                    st.balloons()

                except sqlite3.IntegrityError:

                    st.error(
                        "One or more student records already exist "
                        "in the database. Please check the names."
                    )

                except sqlite3.Error as e:

                    st.error(
                        f"Database error: {e}"
                    )

    # Display all previously saved students

    st.markdown("---")

    st.subheader("📋 Saved Student Records")

    if st.session_state["students"]:

        saved_df = get_dataframe()

        st.dataframe(
            saved_df,
            use_container_width=True,
            hide_index=True
        )

        st.success(
            f"Total Saved Students: "
            f"{len(st.session_state['students'])}"
        )

    else:

        st.warning("No student records saved yet.")


# =====================================================
# 13. STUDENT RESULTS
# =====================================================

elif menu == "Student Results":

    st.header("📑 Student Result Report")

    if st.session_state["students"]:

        df = get_dataframe()

        search = st.text_input(
            "🔍 Search Student by Name"
        )

        if search:

            display_df = df[
                df["Student Name"].str.contains(
                    search,
                    case=False,
                    na=False
                )
            ]

        else:

            display_df = df

        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True
        )

        if search and display_df.empty:

            st.warning("Student not found.")

        csv = df.to_csv(
            index=False
        ).encode("utf-8")

        st.download_button(
            "📥 Download Student Results",
            data=csv,
            file_name="student_results.csv",
            mime="text/csv"
        )

    else:

        st.warning("No student records available!")


# =====================================================
# 14. PERFORMANCE ANALYSIS
# =====================================================

elif menu == "Performance Analysis":

    st.header("📈 Student Performance Analysis")

    if st.session_state["students"]:

        df = get_dataframe()

        col1, col2 = st.columns(2)

        with col1:

            fig1 = px.bar(
                df,
                x="Student Name",
                y="Marks",
                color="Grade",
                title="Student-wise Marks",
                text_auto=".1f",
                color_discrete_sequence=px.colors.qualitative.Bold
            )

            fig1.update_layout(
                yaxis_range=[0, 100],
                xaxis_title="Student Name",
                yaxis_title="Marks"
            )

            st.plotly_chart(
                fig1,
                use_container_width=True
            )

        with col2:

            grade_data = (
                df["Grade"]
                .value_counts()
                .reindex(["A", "B", "C", "D", "E"], fill_value=0)
                .reset_index()
            )

            grade_data.columns = ["Grade", "Students"]

            fig2 = px.bar(
                grade_data,
                x="Grade",
                y="Students",
                color="Grade",
                title="Grade-wise Student Count",
                text_auto=True
            )

            st.plotly_chart(
                fig2,
                use_container_width=True
            )

        st.subheader("🏆 Top 5 Performing Students")

        top_students = df.sort_values(
            by="Marks",
            ascending=False
        ).head(5)

        st.dataframe(
            top_students,
            use_container_width=True,
            hide_index=True
        )

        passed = len(df[df["Marks"] >= 60])

        failed = len(df[df["Marks"] < 60])

        col1, col2 = st.columns(2)

        col1.metric("✅ Passed Students", passed)

        col2.metric("❌ Students Below 60", failed)

    else:

        st.info("Add student records to view performance analysis.")


# =====================================================
# 15. FOOTER
# =====================================================

st.markdown("---")

st.markdown(
    """
    <div style="text-align:center; color:#64748B;">
        🎓 Student Grade Management System
        <br>
        Built using Python, Streamlit and SQLite
    </div>
    """,
    unsafe_allow_html=True
)
