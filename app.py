from flask import Flask, render_template, request, redirect, flash, Response, session
import sqlite3
from datetime import datetime

app = Flask(__name__)
app.secret_key = "devtrack123"

# ---------------- Login ---------------

@app.route("/", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        conn = sqlite3.connect("bugs.db")
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM users WHERE username=? AND password=?",
            (username, password)
        )

        user = cursor.fetchone()
        print("Username:", repr(username))
        print("Password:", repr(password))
        print("User:", user)
        conn.close()

        if user:
            session["username"] = username
            flash("✅ Login Successful!")
            return redirect("/dashboard")
        else:
            flash("❌ Invalid Username or Password")
            return redirect("/")

    return render_template("login.html")
# ---------------- Register ----------------

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        conn = sqlite3.connect("bugs.db")
        cursor = conn.cursor()

        try:
            cursor.execute(
                "INSERT INTO users(username, password) VALUES(?, ?)",
                (username, password)
            )

            conn.commit()
            flash("✅ Account Created Successfully!")

            conn.close()

            return redirect("/")

        except sqlite3.IntegrityError:

            flash("❌ Username Already Exists!")

            conn.close()

            return redirect("/register")

    return render_template("register.html")

# ---------------- Forgot Password ----------------

@app.route("/forgotpassword", methods=["GET", "POST"])
def forgot_password():

    if request.method == "POST":

        username = request.form["username"]

        conn = sqlite3.connect("bugs.db")
        cursor = conn.cursor()

        cursor.execute(
            "SELECT password FROM users WHERE username=?",
            (username,)
        )

        user = cursor.fetchone()

        conn.close()

        if user:
            flash(f"Your Password is: {user[0]}")
        else:
            flash("❌ Username Not Found!")

        return redirect("/forgotpassword")

    return render_template("forgot_password.html")


# ---------------- Dashboard ----------------

@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():

    if "username" not in session:
        flash("Please Login First")
        return redirect("/")

    conn = sqlite3.connect("bugs.db")
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM bugs")
    total = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM bugs WHERE status='Open'")
    open_bugs = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM bugs WHERE status='Closed'")
    closed_bugs = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM users")
    total_users = cursor.fetchone()[0]

    conn.close()
    current_date = datetime.now().strftime("%d-%m-%Y %I:%M %p")
    return render_template(
    "dashboard.html",
    total=total,
    open_bugs=open_bugs,
    closed_bugs=closed_bugs,
    total_users=total_users,
    username=session["username"],
    current_date=current_date
)

# ---------------- Add Bug ----------------

@app.route("/addbug")
def add_bug():
    return render_template("add_bug.html")


# ---------------- Save Bug ----------------

@app.route("/savebug", methods=["POST"])
def save_bug():

    title = request.form["title"]
    description = request.form["description"]
    priority = request.form["priority"]
    status = request.form["status"]
    created_at = datetime.now().strftime("%d-%m-%Y %I:%M %p")
    conn = sqlite3.connect("bugs.db")
    cursor = conn.cursor()

    cursor.execute(
    "INSERT INTO bugs(title, description, priority, status, created_at) VALUES(?,?,?,?,?)",
    (title, description, priority, status, created_at)
)

    conn.commit()
    conn.close()

    flash("✅ Bug Added Successfully!")

    return redirect("/viewbugs")


# ---------------- View Bugs ----------------

@app.route("/viewbugs")
def view_bugs():

    search = request.args.get("search")
    status = request.args.get("status")

    conn = sqlite3.connect("bugs.db")
    cursor = conn.cursor()

    query = "SELECT * FROM bugs WHERE 1=1"
    params = []

    if search:
        query += " AND title LIKE ?"
        params.append("%" + search + "%")

    if status:
        query += " AND status = ?"
        params.append(status)

    cursor.execute(query, params)

    bugs = cursor.fetchall()

    conn.close()

    return render_template("view_bugs.html", bugs=bugs)


# ---------------- Edit Bug ----------------

@app.route("/editbug/<int:id>")
def edit_bug(id):

    conn = sqlite3.connect("bugs.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM bugs WHERE id=?", (id,))
    bug = cursor.fetchone()
    conn.close()

    return render_template("edit_bug.html", bug=bug)


# ---------------- Update Bug ----------------

@app.route("/updatebug/<int:id>", methods=["POST"])
def update_bug(id):

    title = request.form["title"]
    description = request.form["description"]
    priority = request.form["priority"]
    status = request.form["status"]

    conn = sqlite3.connect("bugs.db")
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE bugs
        SET title=?, description=?, priority=?, status=?
        WHERE id=?
    """, (title, description, priority, status, id))

    conn.commit()
    conn.close()

    flash("✅ Bug Updated Successfully!")

    return redirect("/viewbugs")


# ---------------- Delete Bug ----------------

@app.route("/deletebug/<int:id>")
def delete_bug(id):

    conn = sqlite3.connect("bugs.db")
    cursor = conn.cursor()

    cursor.execute("DELETE FROM bugs WHERE id=?", (id,))

    conn.commit()
    conn.close()

    flash("🗑️ Bug Deleted Successfully!")

    return redirect("/viewbugs")


# ---------------- Export CSV ----------------

@app.route("/export")
def export_csv():


    conn = sqlite3.connect("bugs.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM bugs")
    bugs = cursor.fetchall()

    conn.close()

    csv_data = "ID,Title,Description,Priority,Status\n"

    for bug in bugs:
        csv_data += f"{bug[0]},{bug[1]},{bug[2]},{bug[3]},{bug[4]}\n"

    return Response(
        csv_data,
        mimetype="text/csv",
        headers={
            "Content-Disposition": "attachment; filename=bugs.csv"
        }
    )


# ---------------- Change Password ----------------

@app.route("/changepassword", methods=["GET", "POST"])
def change_password():

    if "username" not in session:
        flash("Please Login First")
        return redirect("/")

    if request.method == "POST":

        old_password = request.form["old_password"]
        new_password = request.form["new_password"]
        confirm_password = request.form["confirm_password"]

        if new_password != confirm_password:
            flash("❌ New Password and Confirm Password do not match!")
            return redirect("/changepassword")

        username = session["username"]

        conn = sqlite3.connect("bugs.db")
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM users WHERE username=? AND password=?",
            (username, old_password)
        )

        user = cursor.fetchone()

        if user:

            cursor.execute(
                "UPDATE users SET password=? WHERE username=?",
                (new_password, username)
            )

            conn.commit()
            flash("✅ Password Changed Successfully!")

        else:

            flash("❌ Old Password is Incorrect!")

        conn.close()

        return redirect("/changepassword")

    return render_template("change_password.html")



@app.route("/logout")
def logout():
    session.pop("username", None)
    flash("👋 Logged Out Successfully!")
    return redirect("/")

# ---------------- Run App ----------------

if __name__ == "__main__":
    app.run(debug=True)