from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    session,
    flash,
    send_file
)

import sqlite3
import os
from werkzeug.security import generate_password_hash, check_password_hash

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm


app = Flask(__name__)

app.secret_key = "resume_builder_secret_key_123"

DATABASE = "database.db"




def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():

    conn = get_db()

    
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)

    
    conn.execute("""
        CREATE TABLE IF NOT EXISTS resumes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,

            user_id INTEGER NOT NULL,

            name TEXT,
            email TEXT,
            phone TEXT,
            address TEXT,
            linkedin TEXT,
            github TEXT,

            career_objective TEXT,

            education TEXT,
            skills TEXT,
            experience TEXT,
            projects TEXT,
            certifications TEXT,
            achievements TEXT,

            template TEXT DEFAULT 'classic',

            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    conn.commit()
    conn.close()



@app.route("/")
def home():

    if "user_id" in session:
        return redirect(url_for("dashboard"))

    return redirect(url_for("login"))



@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")

        if not name or not email or not password:

            flash("Please fill all fields.", "error")

            return redirect(url_for("register"))

        hashed_password = generate_password_hash(password)

        conn = get_db()

        try:

            conn.execute("""
                INSERT INTO users
                (name, email, password)
                VALUES (?, ?, ?)
            """, (
                name,
                email,
                hashed_password
            ))

            conn.commit()
            conn.close()

            flash("Registration successful. Please login.", "success")

            return redirect(url_for("login"))

        except sqlite3.IntegrityError:

            conn.close()

            flash("Email already registered.", "error")

            return redirect(url_for("register"))

    return render_template("register.html")



@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")

        conn = get_db()

        user = conn.execute("""
            SELECT *
            FROM users
            WHERE email = ?
        """, (email,)).fetchone()

        conn.close()

        if user and check_password_hash(
            user["password"],
            password
        ):

            session["user_id"] = user["id"]
            session["user_name"] = user["name"]

            return redirect(url_for("dashboard"))

        flash("Invalid email or password.", "error")

    return render_template("login.html")



@app.route("/logout")
def logout():

    session.clear()

    return redirect(url_for("login"))



@app.route("/dashboard")
def dashboard():

    if "user_id" not in session:
        return redirect(url_for("login"))

    conn = get_db()

    resumes = conn.execute("""
        SELECT *
        FROM resumes
        WHERE user_id = ?
        ORDER BY id DESC
    """, (
        session["user_id"],
    )).fetchall()

    conn.close()

    return render_template(
        "dashboard.html",
        resumes=resumes
    )




@app.route("/create-resume", methods=["GET", "POST"])
def create_resume():

    if "user_id" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":

        name = request.form.get("name", "")
        email = request.form.get("email", "")
        phone = request.form.get("phone", "")
        address = request.form.get("address", "")
        linkedin = request.form.get("linkedin", "")
        github = request.form.get("github", "")

        career_objective = request.form.get(
            "career_objective",
            ""
        )

        education = request.form.get(
            "education",
            ""
        )

        skills = request.form.get(
            "skills",
            ""
        )

        experience = request.form.get(
            "experience",
            ""
        )

        projects = request.form.get(
            "projects",
            ""
        )

        certifications = request.form.get(
            "certifications",
            ""
        )

        achievements = request.form.get(
            "achievements",
            ""
        )

        template = request.form.get(
            "template",
            "classic"
        )

        conn = get_db()

        conn.execute("""
            INSERT INTO resumes (

                user_id,

                name,
                email,
                phone,
                address,
                linkedin,
                github,

                career_objective,

                education,
                skills,
                experience,
                projects,
                certifications,
                achievements,

                template

            )
            VALUES (
                ?, ?, ?, ?, ?, ?, ?, ?,
                ?, ?, ?, ?, ?, ?, ?
            )
        """, (

            session["user_id"],

            name,
            email,
            phone,
            address,
            linkedin,
            github,

            career_objective,

            education,
            skills,
            experience,
            projects,
            certifications,
            achievements,

            template
        ))

        conn.commit()
        conn.close()

        flash("Resume created successfully.", "success")

        return redirect(url_for("dashboard"))

    return render_template("create_resume.html")



@app.route("/edit-resume/<int:resume_id>", methods=["GET", "POST"])
def edit_resume(resume_id):

    if "user_id" not in session:
        return redirect(url_for("login"))

    conn = get_db()

    resume = conn.execute("""
        SELECT *
        FROM resumes
        WHERE id = ?
        AND user_id = ?
    """, (
        resume_id,
        session["user_id"]
    )).fetchone()

    if resume is None:

        conn.close()

        flash("Resume not found.", "error")

        return redirect(url_for("dashboard"))

    if request.method == "POST":

        name = request.form.get("name", "")
        email = request.form.get("email", "")
        phone = request.form.get("phone", "")
        address = request.form.get("address", "")
        linkedin = request.form.get("linkedin", "")
        github = request.form.get("github", "")

        career_objective = request.form.get(
            "career_objective",
            ""
        )

        education = request.form.get(
            "education",
            ""
        )

        skills = request.form.get(
            "skills",
            ""
        )

        experience = request.form.get(
            "experience",
            ""
        )

        projects = request.form.get(
            "projects",
            ""
        )

        certifications = request.form.get(
            "certifications",
            ""
        )

        achievements = request.form.get(
            "achievements",
            ""
        )

        template = request.form.get(
            "template",
            "classic"
        )

        conn.execute("""
            UPDATE resumes

            SET

                name = ?,
                email = ?,
                phone = ?,
                address = ?,
                linkedin = ?,
                github = ?,

                career_objective = ?,

                education = ?,
                skills = ?,
                experience = ?,
                projects = ?,
                certifications = ?,
                achievements = ?,

                template = ?

            WHERE id = ?

            AND user_id = ?

        """, (

            name,
            email,
            phone,
            address,
            linkedin,
            github,

            career_objective,

            education,
            skills,
            experience,
            projects,
            certifications,
            achievements,

            template,

            resume_id,

            session["user_id"]
        ))

        conn.commit()
        conn.close()

        flash("Resume updated successfully.", "success")

        return redirect(url_for(
            "dashboard"
        ))

    conn.close()

    return render_template(
        "edit_resume.html",
        resume=resume
    )



@app.route("/delete-resume/<int:resume_id>")
def delete_resume(resume_id):

    if "user_id" not in session:
        return redirect(url_for("login"))

    conn = get_db()

    conn.execute("""
        DELETE FROM resumes
        WHERE id = ?
        AND user_id = ?
    """, (
        resume_id,
        session["user_id"]
    ))

    conn.commit()
    conn.close()

    flash(
        "Resume deleted successfully.",
        "success"
    )

    return redirect(url_for("dashboard"))




@app.route("/preview/<int:resume_id>")
def preview(resume_id):

    if "user_id" not in session:
        return redirect(url_for("login"))

    conn = get_db()

    resume = conn.execute("""
        SELECT *
        FROM resumes

        WHERE id = ?

        AND user_id = ?
    """, (
        resume_id,
        session["user_id"]
    )).fetchone()

    conn.close()

    if resume is None:

        flash(
            "Resume not found.",
            "error"
        )

        return redirect(
            url_for("dashboard")
        )

    return render_template(
        "preview.html",
        resume=resume
    )



@app.route("/download/<int:resume_id>")
def download_pdf(resume_id):

    if "user_id" not in session:
        return redirect(url_for("login"))

    conn = get_db()

    resume = conn.execute("""
        SELECT *
        FROM resumes

        WHERE id = ?

        AND user_id = ?
    """, (
        resume_id,
        session["user_id"]
    )).fetchone()

    conn.close()

    if resume is None:

        flash(
            "Resume not found.",
            "error"
        )

        return redirect(
            url_for("dashboard")
        )

    filename = f"resume_{resume_id}.pdf"

    filepath = os.path.join(
        os.getcwd(),
        filename
    )

    pdf = canvas.Canvas(
        filepath,
        pagesize=A4
    )

    width, height = A4

    left = 20 * mm
    y = height - 20 * mm

    
    pdf.setFont(
        "Helvetica-Bold",
        20
    )

    pdf.drawString(
        left,
        y,
        resume["name"] or "Resume"
    )

    y -= 10 * mm

    # CONTACT
    pdf.setFont(
        "Helvetica",
        9
    )

    contact = []

    if resume["email"]:
        contact.append(
            resume["email"]
        )

    if resume["phone"]:
        contact.append(
            resume["phone"]
        )

    if resume["address"]:
        contact.append(
            resume["address"]
        )

    pdf.drawString(
        left,
        y,
        " | ".join(contact)
    )

    y -= 12 * mm

    # SECTION FUNCTION
    def add_section(title, text):

        nonlocal y

        if not text:
            return

        if y < 35 * mm:

            pdf.showPage()

            y = height - 20 * mm

        pdf.setFont(
            "Helvetica-Bold",
            12
        )

        pdf.drawString(
            left,
            y,
            title
        )

        y -= 7 * mm

        pdf.setFont(
            "Helvetica",
            9
        )

        lines = text.split("\n")

        for line in lines:

            words = line.split()

            current = ""

            for word in words:

                test = (
                    current + " " + word
                ).strip()

                if pdf.stringWidth(
                    test,
                    "Helvetica",
                    9
                ) > 170 * mm:

                    pdf.drawString(
                        left,
                        y,
                        current
                    )

                    y -= 5 * mm

                    current = word

                else:

                    current = test

            if current:

                pdf.drawString(
                    left,
                    y,
                    current
                )

                y -= 5 * mm

        y -= 5 * mm

    add_section(
        "CAREER OBJECTIVE",
        resume["career_objective"]
    )

    add_section(
        "EDUCATION",
        resume["education"]
    )

    add_section(
        "SKILLS",
        resume["skills"]
    )

    add_section(
        "EXPERIENCE",
        resume["experience"]
    )

    add_section(
        "PROJECTS",
        resume["projects"]
    )

    add_section(
        "CERTIFICATIONS",
        resume["certifications"]
    )

    add_section(
        "ACHIEVEMENTS",
        resume["achievements"]
    )

    pdf.save()

    return send_file(
        filepath,
        as_attachment=True,
        download_name=filename
    )



if __name__ == "__main__":

    init_db()

    app.run(
        debug=True,
        host="0.0.0.0",
        port=5000
    )