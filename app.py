"""Academic Record Manager: Python + Pandas + CSV + Streamlit."""
from pathlib import Path
import pandas as pd
import streamlit as st

DATA_FILE = Path(__file__).with_name("academic_records.csv")
FIELDS = ["record_id", "student_name", "program", "semester", "attendance_pct",
          "quiz_score", "assignment_score", "exam_score", "total_score", "status", "grade"]
PROGRAMS = ["BCA", "B.Sc. IT", "B.Tech CSE", "B.Com. IT", "B.Voc. IT"]

st.set_page_config(page_title="Academic Record Manager", page_icon="📚", layout="wide")


def read_records():
    """Load records from CSV; create an empty table if it is missing."""
    if not DATA_FILE.exists():
        return pd.DataFrame(columns=FIELDS)
    data = pd.read_csv(DATA_FILE)
    for field in FIELDS:
        if field not in data.columns:
            data[field] = ""
    return data[FIELDS]


def write_records(data):
    """Save records to CSV."""
    data.to_csv(DATA_FILE, index=False)


def next_record_id(data):
    """Return the next numeric record ID."""
    if data.empty:
        return 2001
    ids = pd.to_numeric(data["record_id"], errors="coerce")
    return int(ids.max()) + 1 if ids.notna().any() else 2001


def calculate_result(quiz, assignment, exam):
    total = round(float(quiz) + float(assignment) + float(exam), 1)
    grade = "A" if total >= 85 else "B" if total >= 70 else "C" if total >= 55 else "D" if total >= 40 else "F"
    return total, grade, "Pass" if total >= 40 else "Fail"


def make_record(record_id, values):
    total, grade, status = calculate_result(values["quiz_score"], values["assignment_score"], values["exam_score"])
    return {
        "record_id": int(record_id),
        "student_name": values["student_name"].strip(),
        "program": values["program"],
        "semester": int(values["semester"]),
        "attendance_pct": float(values["attendance_pct"]),
        "quiz_score": float(values["quiz_score"]),
        "assignment_score": float(values["assignment_score"]),
        "exam_score": float(values["exam_score"]),
        "total_score": total,
        "status": status,
        "grade": grade,
    }


def add_record(values):
    data = read_records()
    data = pd.concat([data, pd.DataFrame([make_record(next_record_id(data), values)])], ignore_index=True)
    write_records(data)


def edit_record(record_id, values):
    data = read_records()
    mask = pd.to_numeric(data["record_id"], errors="coerce") == int(record_id)
    if mask.any():
        updated = make_record(record_id, values)
        for field in FIELDS:
            data.loc[mask, field] = updated[field]
        write_records(data)


def remove_record(record_id):
    data = read_records()
    data = data[pd.to_numeric(data["record_id"], errors="coerce") != int(record_id)]
    write_records(data)


def record_form(existing=None, key="record_form"):
    existing = existing or {}
    with st.form(key):
        name = st.text_input("Student name", str(existing.get("student_name", "")))
        old_program = existing.get("program", PROGRAMS[0])
        pidx = PROGRAMS.index(old_program) if old_program in PROGRAMS else 0
        program = st.selectbox("Programme", PROGRAMS, index=pidx)
        c1, c2 = st.columns(2)
        semester = c1.selectbox("Semester", [1, 2, 3, 4, 5, 6, 7, 8],
                                index=max(0, min(7, int(existing.get("semester", 3)) - 1)))
        attendance = c2.slider("Attendance (%)", 0.0, 100.0,
                               float(existing.get("attendance_pct", 75.0)), step=0.5)
        a, b, c = st.columns(3)
        quiz = a.number_input("Quiz / 10", 0.0, 10.0, float(existing.get("quiz_score", 7.0)), step=0.5)
        assignment = b.number_input("Assignment / 30", 0.0, 30.0, float(existing.get("assignment_score", 18.0)), step=0.5)
        exam = c.number_input("Exam / 60", 0.0, 60.0, float(existing.get("exam_score", 35.0)), step=0.5)
        submitted = st.form_submit_button("Save record", type="primary")
    return submitted, {"student_name": name, "program": program, "semester": semester,
                       "attendance_pct": attendance, "quiz_score": quiz,
                       "assignment_score": assignment, "exam_score": exam}


st.title("📚 Academic Record Manager")
st.caption("Manage student academic records using a simple CSV-backed application.")
records = read_records()
overview, browse, create, manage, summary = st.tabs(
    ["Overview", "Records", "New Record", "Manage Record", "Academic Summary"]
)

with overview:
    st.subheader("Class overview")
    count = len(records)
    avg_score = pd.to_numeric(records["total_score"], errors="coerce").mean()
    pass_count = int((records["status"] == "Pass").sum()) if count else 0
    pass_rate = pass_count / count * 100 if count else 0
    avg_attendance = pd.to_numeric(records["attendance_pct"], errors="coerce").mean()
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Records", count)
    m2.metric("Average score", f"{avg_score:.1f}" if pd.notna(avg_score) else "—")
    m3.metric("Pass rate", f"{pass_rate:.1f}%")
    m4.metric("Mean attendance", f"{avg_attendance:.1f}%" if pd.notna(avg_attendance) else "—")
    if records.empty:
        st.info("No records yet. Use New Record to add the first one.")
    else:
        st.markdown("**Students by programme**")
        st.bar_chart(records["program"].value_counts())
        st.markdown("**Latest records**")
        st.dataframe(records.tail(8), use_container_width=True, hide_index=True)

with browse:
    st.subheader("Find and review records")
    if records.empty:
        st.info("No records available.")
    else:
        query = st.text_input("Search by name or record ID")
        programs = st.multiselect("Programme filter", PROGRAMS)
        status_filter = st.selectbox("Result filter", ["All", "Pass", "Fail"])
        view = records.copy()
        if query.strip():
            q = query.strip()
            view = view[view["student_name"].astype(str).str.contains(q, case=False, na=False) |
                        view["record_id"].astype(str).str.contains(q, na=False)]
        if programs:
            view = view[view["program"].isin(programs)]
        if status_filter != "All":
            view = view[view["status"] == status_filter]
        st.write(f"**{len(view)}** record(s) match.")
        st.dataframe(view, use_container_width=True, hide_index=True)
        st.download_button("Export displayed records", view.to_csv(index=False),
                           file_name="academic_records_export.csv", mime="text/csv")

with create:
    st.subheader("Create a student record")
    submitted, values = record_form(key="new_record_form")
    if submitted:
        if not values["student_name"].strip():
            st.error("Enter a student name before saving.")
        else:
            add_record(values)
            st.success("Record saved.")
            st.rerun()

with manage:
    st.subheader("Update or remove a record")
    current = read_records()
    if current.empty:
        st.info("Add a record before editing or removing one.")
    else:
        ids = pd.to_numeric(current["record_id"], errors="coerce").dropna().astype(int).tolist()
        chosen = st.selectbox("Choose record", ids)
        row = current[pd.to_numeric(current["record_id"], errors="coerce") == chosen].iloc[0].to_dict()
        st.markdown("**Edit details**")
        submitted, values = record_form(row, key=f"edit_record_{chosen}")
        if submitted:
            if not values["student_name"].strip():
                st.error("Enter a student name before saving.")
            else:
                edit_record(chosen, values)
                st.success("Record updated.")
                st.rerun()
        st.divider()
        confirm = st.checkbox(f"Confirm removal of record {chosen} ({row['student_name']})")
        if st.button("Remove selected record", disabled=not confirm):
            remove_record(chosen)
            st.success("Record removed.")
            st.rerun()

with summary:
    st.subheader("Academic summary")
    current = read_records()
    if current.empty:
        st.info("The summary appears after records are added.")
    else:
        numeric = ["quiz_score", "assignment_score", "exam_score", "total_score", "attendance_pct"]
        st.dataframe(current[numeric].apply(pd.to_numeric, errors="coerce").describe().round(2),
                     use_container_width=True)
        st.markdown("**Grade distribution**")
        st.bar_chart(current["grade"].value_counts())
