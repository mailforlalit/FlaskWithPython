from flask import Flask, render_template, request
from database import get_connection, create_table

app = Flask(__name__)

# Create table when app starts
create_table()


# -------------------------
# Home Page
# -------------------------
@app.route("/")
def home():
    return render_template("home.html")


# -------------------------
# Add Student (CREATE)
# -------------------------
@app.route("/add", methods=["GET", "POST"])
def add_student():
    if request.method == "POST":
        name = request.form["name"]
        course = request.form["course"]

        conn = get_connection()
        conn.execute(
            "INSERT INTO students (name, course) VALUES (?, ?)",
            (name, course)
        )
        conn.commit()
        conn.close()

        return render_template("add_student.html", message="Student Added Successfully!")

    return render_template("add_student.html")


# -------------------------
# View Students (READ)
# -------------------------
@app.route("/students")
def students():
    conn = get_connection()
    students = conn.execute("SELECT * FROM students").fetchall()
    conn.close()

    return render_template("students.html",
                           students=students)


if __name__ == "__main__":
    app.run(debug=True)