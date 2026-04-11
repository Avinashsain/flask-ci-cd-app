"""Flask CI/CD Application with MongoDB"""

# Standard library imports
import os

# Third-party imports
from flask import Flask, render_template, request, redirect, url_for
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from dotenv import load_dotenv


mongo = PyMongo()


def create_app():
    """Application factory function"""

    load_dotenv()

    app = Flask(__name__)

    # Configuration
    app.config["MONGO_URI"] = os.getenv(
        "MONGO_URI", "mongodb://localhost:27017/test"
    )
    app.secret_key = os.getenv("SECRET_KEY", "defaultsecret")

    mongo.init_app(app)

    # ---------------- ROUTES ---------------- #

    @app.route("/")
    def index():
        """Home page"""
        students = mongo.db.students.find()
        return render_template("index.html", students=students)

    @app.route("/add", methods=["GET", "POST"])
    def add_student():
        """Add student"""
        if request.method == "POST":
            mongo.db.students.insert_one(
                {
                    "name": request.form["name"],
                    "email": request.form["email"],
                    "course": request.form["course"],
                }
            )
            return redirect(url_for("index"))
        return render_template("add_student.html")

    @app.route("/update/<student_id>", methods=["GET", "POST"])
    def update_student(student_id):
        """Update student"""
        student = mongo.db.students.find_one({"_id": ObjectId(student_id)})

        if request.method == "POST":
            mongo.db.students.update_one(
                {"_id": ObjectId(student_id)},
                {
                    "$set": {
                        "name": request.form["name"],
                        "email": request.form["email"],
                        "course": request.form["course"],
                    }
                },
            )
            return redirect(url_for("index"))

        return render_template("update_student.html", student=student)

    @app.route("/delete/<student_id>")
    def delete_student(student_id):
        """Delete student"""
        mongo.db.students.delete_one({"_id": ObjectId(student_id)})
        return redirect(url_for("index"))

    @app.route("/about")
    def about():
        """About page"""
        return render_template("about.html")

    return app


app = create_app()


if __name__ == "__main__":
    # ONLY for local development
    port = int(os.getenv("PORT", 5000))

    app.run(
        host="0.0.0.0",
        port=port,
        debug=False
    )