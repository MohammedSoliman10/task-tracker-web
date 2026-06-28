import json
import os
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

TASKS_FILE = "tasks.json"

def load_tasks():
    if not os.path.exists(TASKS_FILE):
        return []
    with open(TASKS_FILE, "r") as f:
        return json.load(f)

def save_tasks(tasks):
    with open(TASKS_FILE, "w") as f:
        json.dump(tasks, f, indent=4)

@app.route("/")
def index():
    tasks = load_tasks()
    return render_template("index.html", tasks=tasks)

@app.route("/filter/<status>")
def filter_tasks(status):
    tasks = load_tasks()
    filtered = [task for task in tasks if task["status"] == status]
    return render_template("index.html", tasks=filtered, current_filter=status)

@app.route("/add", methods=["POST"])
def add_task():
    description = request.form.get("description")
    if description:
        tasks = load_tasks()
        new_id = len(tasks) + 1
        new_task = {
            "id": new_id,
            "description": description,
            "status": "todo",
            "createdAt": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "updatedAt": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        tasks.append(new_task)
        save_tasks(tasks)
    return redirect(url_for("index"))

@app.route("/delete/<int:task_id>")
def delete_task(task_id):
    tasks = load_tasks()
    tasks = [task for task in tasks if task["id"] != task_id]
    for i, task in enumerate(tasks):
        task["id"] = i + 1
    save_tasks(tasks)
    return redirect(url_for("index"))

@app.route("/mark-in-progress/<int:task_id>")
def mark_in_progress(task_id):
    tasks = load_tasks()
    for task in tasks:
        if task["id"] == task_id:
            task["status"] = "in-progress"
            task["updatedAt"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    save_tasks(tasks)
    return redirect(url_for("index"))

@app.route("/mark-done/<int:task_id>")
def mark_done(task_id):
    tasks = load_tasks()
    for task in tasks:
        if task["id"] == task_id:
            task["status"] = "done"
            task["updatedAt"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    save_tasks(tasks)
    return redirect(url_for("index"))

@app.route("/update/<int:task_id>", methods=["POST"])
def update_task(task_id):
    new_description = request.form.get("description")
    if new_description:
        tasks = load_tasks()
        for task in tasks:
            if task["id"] == task_id:
                task["description"] = new_description
                task["updatedAt"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        save_tasks(tasks)
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True)