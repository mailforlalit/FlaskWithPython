from flask import Flask, render_template, request, redirect, session
from database import get_connection, create_table
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key='secretkey'

# Create table when app starts
create_table()

# -------------------------
# Registration Page
# -------------------------
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = generate_password_hash(request.form["password"])
        conn = get_connection()
        conn.execute(
            "INSERT INTO users (username, password) VALUES (?, ?)",
            (username, password)
        )
        conn.commit()
        conn.close()

        return redirect("/login")

    return render_template("register.html")

# -------------------------
# Login Page
# -------------------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        conn = get_connection()
        user = conn.execute(
            "SELECT * FROM users WHERE username = ?", (username,)
        ).fetchone()
        conn.close()

        if user and check_password_hash(user["password"], password):
            session["user_id"] = user["id"]
            return redirect("/dashboard")

    return render_template("login.html")


# -------------------------
# Logout
# -------------------------
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

# -------------------------
# Dashboard Page
# -------------------------
@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect("/login")

    conn = get_connection()
    students = conn.execute("SELECT * FROM students where user_id= ?", (session["user_id"],)).fetchall()
    user=conn.execute("SELECT * FROM users WHERE id= ?", (session["user_id"],)).fetchone()
    conn.close()

    return render_template("dashboard.html", students=students , user=user)


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
        user_id = session["user_id"]

        conn = get_connection()
        conn.execute(
            "INSERT INTO students (name, course, user_id) VALUES (?, ?, ?)",
            (name, course, user_id)
        )
        conn.commit()
        conn.close()

        conn = get_connection()
        students = conn.execute("SELECT * FROM students where user_id= ?", (session["user_id"],)).fetchall()
        user = conn.execute("SELECT * FROM users WHERE id= ?", (session["user_id"],)).fetchone()
        conn.close()

        return render_template("dashboard.html", students=students, user=user)

    return render_template("create_student.html")


# -------------------------
# View Students (READ)
# -------------------------
@app.route("/students")
def students():
    conn = get_connection()
    user_id = session["user_id"]
    students = conn.execute("SELECT * FROM students where user_id= ?", (user_id)).fetchall()
    conn.close()

    return render_template("view_students.html",
                           students=students)
# -------------------------
# Update Students (READ)
# -------------------------
@app.route( "/update/<int:id>", methods=["GET", "POST"])
def updateStudents(id):
    conn = get_connection()

    if request.method == "POST":
        name = request.form["name"]
        course = request.form["course"]

        conn.execute(
            "UPDATE students SET name = ? , course = ? WHERE id = ?",
            (name, course, id)
        )

        conn.commit()
        conn.close()
    return redirect("/dashboard")

@app.route("/edit/<int:id>", methods=["GET", "POST"])
def editStudents(id):
    print("ID is : ")
    print(id)
    conn = get_connection()
    if 'user_id' not in session:
        return redirect("/login")
    student = conn.execute("SELECT * FROM students WHERE id = ?", (id,)).fetchone()
    conn.close()
    return render_template("edit.html", student=student)

# -------------------------
#  delete Students (READ)
# -------------------------
@app.route("/delete/<int:id>")
def delete_student(id):
    conn = get_connection()
    if 'user_id' not in session:
        return redirect("/login")
    conn.execute("DELETE FROM students WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    return redirect("/dashboard")

if __name__ == "__main__":
    app.run(debug=True)