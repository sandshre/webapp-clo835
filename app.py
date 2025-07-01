from flask import Flask, render_template, request, g
from pymysql import connections
import os
import random
import argparse

app = Flask(__name__)

# Load configuration from environment variables or fallback to defaults
DB_CONFIG = {
    "host": os.environ.get("DBHOST", "localhost"),
    "user": os.environ.get("DBUSER", "root"),
    "password": os.environ.get("DBPWD", "passwors"),
    "database": os.environ.get("DATABASE", "employees"),
    "port": int(os.environ.get("DBPORT", 3306))
}

DEFAULT_COLOR = os.environ.get("APP_COLOR", "lime")
COLOR_PALETTE = {
    "red": "#e74c3c",
    "green": "#16a085",
    "blue": "#89CFF0",
    "blue2": "#30336b",
    "pink": "#f4c2c2",
    "darkblue": "#130f40",
    "lime": "#C1FF9C",
}
AVAILABLE_COLORS = ",".join(COLOR_PALETTE.keys())
COLOR = random.choice(list(COLOR_PALETTE.keys()))  # Can be overridden later

# Create and cache a DB connection for current app context
def get_db_connection():
    if 'db_conn' not in g:
        try:
            g.db_conn = connections.Connection(
                host=DB_CONFIG["host"],
                port=DB_CONFIG["port"],
                user=DB_CONFIG["user"],
                password=DB_CONFIG["password"],
                db=DB_CONFIG["database"]
            )
        except Exception as err:
            print("Failed to connect to DB:", err)
            raise
    return g.db_conn

# Cleanup DB connection after each request
@app.teardown_appcontext
def close_db_connection(exception):
    db_conn = g.pop('db_conn', None)
    if db_conn:
        db_conn.close()

# Routes
@app.route("/", methods=["GET", "POST"])
def index():
    return render_template("addemp.html", color=COLOR_PALETTE[COLOR])

@app.route("/about", methods=["GET", "POST"])
def about():
    return render_template("about.html", color=COLOR_PALETTE[COLOR])

@app.route("/addemp", methods=["POST"])
def add_employee():
    emp_data = (
        request.form["emp_id"],
        request.form["first_name"],
        request.form["last_name"],
        request.form["primary_skill"],
        request.form["location"]
    )

    insert_query = "INSERT INTO employee VALUES (%s, %s, %s, %s, %s)"
    db_conn = get_db_connection()
    cursor = db_conn.cursor()

    try:
        cursor.execute(insert_query, emp_data)
        db_conn.commit()
        emp_name = f"{emp_data[1]} {emp_data[2]}"
    finally:
        cursor.close()

    print("Employee data inserted successfully.")
    return render_template("addempoutput.html", name=emp_name, color=COLOR_PALETTE[COLOR])

@app.route("/getemp", methods=["GET", "POST"])
def get_employee_form():
    return render_template("getemp.html", color=COLOR_PALETTE[COLOR])

@app.route("/fetchdata", methods=["GET", "POST"])
def fetch_employee():
    emp_id = request.form["emp_id"]
    query = "SELECT emp_id, first_name, last_name, primary_skill, location FROM employee WHERE emp_id=%s"

    db_conn = get_db_connection()
    cursor = db_conn.cursor()

    try:
        cursor.execute(query, (emp_id,))
        result = cursor.fetchone()
    except Exception as e:
        print("Error fetching data:", e)
        result = None
    finally:
        cursor.close()

    if result:
        return render_template("getempoutput.html",
                               id=result[0],
                               fname=result[1],
                               lname=result[2],
                               interest=result[3],
                               location=result[4],
                               color=COLOR_PALETTE[COLOR])
    else:
        return render_template("getempoutput.html", error="No employee found", color=COLOR_PALETTE[COLOR])

# Entry point
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--color', help="Override color theme")
    args = parser.parse_args()

    if args.color:
        print(f"Color from CLI argument = {args.color}")
        COLOR = args.color
        if DEFAULT_COLOR:
            print(f"Environment color {DEFAULT_COLOR} overridden by CLI argument.")
    elif DEFAULT_COLOR:
        print(f"No CLI color provided. Using environment color = {DEFAULT_COLOR}")
        COLOR = DEFAULT_COLOR
    else:
        print(f"No CLI or environment color set. Randomly selected color = {COLOR}")

    if COLOR not in COLOR_PALETTE:
        print(f"Unsupported color: '{COLOR}'. Supported colors: {AVAILABLE_COLORS}")
        exit(1)

    app.run(host="0.0.0.0", port=8080, debug=True)
