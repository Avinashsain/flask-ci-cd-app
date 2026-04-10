from flask import Flask, render_template, request, redirect, url_for
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from dotenv import load_dotenv
import os

# Initialize Mongo (without app first)
mongo = PyMongo()

def create_app():
    # Load env variables
    load_dotenv()

    app = Flask(__name__)

    # Safe config (no crash if env missing )
    app.config["MONGO_URI"] = os.getenv("MONGO_URI", "mongodb://localhost:27017/test")
    app.secret_key = os.getenv("SECRET_KEY", "defaultsecret")

    # Initialize Mongo with app
    mongo.init_app(app)

    # ---------------- ROUTES ---------------- #

    @app.route('/')
    def index():
        students = mongo.db.students.find()
        return render_template('index.html', students=students)

    @app.route('/add', methods=['GET', 'POST'])
    def add_student():
        if request.method == 'POST':
            mongo.db.students.insert_one({
                "name": request.form['name'],
                "email": request.form['email'],
                "course": request.form['course']
            })
            return redirect(url_for('index'))
        return render_template('add_student.html')

    @app.route('/update/<student_id>', methods=['GET', 'POST'])
    def update_student(student_id):
        student = mongo.db.students.find_one({"_id": ObjectId(student_id)})
        if request.method == 'POST':
            mongo.db.students.update_one(
                {"_id": ObjectId(student_id)},
                {"$set": {
                    "name": request.form['name'],
                    "email": request.form['email'],
                    "course": request.form['course']
                }}
            )
            return redirect(url_for('index'))
        return render_template('update_student.html', student=student)

    @app.route('/delete/<student_id>')
    def delete_student(student_id):
        mongo.db.students.delete_one({"_id": ObjectId(student_id)})
        return redirect(url_for('index'))

    return app


# Create app instance for Gunicorn before the if __name__ == '__main__' block
app = create_app()


# Run only for local development
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)