from flask import Flask, render_template_string, request, redirect, url_for, session
import requests
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
from werkzeug.security import check_password_hash

# .env laden
load_dotenv()
API_KEY = os.getenv("RESCUETIME_API_KEY")

# Passwort-Hash laden
def get_pass_hash():
    with open(".passwd") as f:
        return f.read().strip()

PASS_HASH = get_pass_hash()

app = Flask(__name__)
app.secret_key = os.urandom(24)  # für Session; für Produktion besser festlegen

# Login-Seite
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        pw = request.form.get("password", "")
        if check_password_hash(PASS_HASH, pw):
            session["logged_in"] = True
            return redirect(url_for("show_top10"))
        else:
            return render_template_string(LOGIN_TEMPLATE, error="Falsches Passwort!")
    return render_template_string(LOGIN_TEMPLATE, error=None)

# Logout
@app.route("/logout")
def logout():
    session.pop("logged_in", None)
    return redirect(url_for("login"))

# Geschützte Seite
@app.route("/")
def show_top10():
    if not session.get("logged_in"):
        return redirect(url_for("login"))

    # --- RescueTime wie vorher ---
    end_date = datetime.today()
    start_date = end_date - timedelta(days=7)
    url = (
        "https://www.rescuetime.com/anapi/data?"
        f"key={API_KEY}"
        f"&perspective=interval"
        f"&restrict_kind=activity"
        f"&resolution_time=day"
        f"&restrict_begin={start_date.strftime('%Y-%m-%d')}"
        f"&restrict_end={end_date.strftime('%Y-%m-%d')}"
        "&format=json"
    )
    r = requests.get(url)
    data = r.json()
    headers = data["row_headers"]
    rows = data["rows"]

    from collections import defaultdict
    daily = defaultdict(list)
    for row in rows:
        date = row[0]
        activity = row[3]
        seconds = row[1]
        daily[date].append((activity, seconds))

    html = '''
    <h1>RescueTime Top 10 (letzte 7 Tage)</h1>
    <a href="{{ url_for('logout') }}">Logout</a>
    {% for date in dates %}
        <h2>{{date}}</h2>
        <table border="1" cellpadding="5">
        <tr><th>Domain/App</th><th>Stunden</th></tr>
        {% for act, sec in daily[date] %}
            <tr>
                <td>{{act}}</td>
                <td>{{sec}}</td>
            </tr>
        {% endfor %}
        </table>
    {% endfor %}
    '''
    for date in daily:
        daily[date] = sorted(daily[date], key=lambda x: x[1], reverse=True)[:10]
        daily[date] = [(act, round(sec / 3600, 2)) for act, sec in daily[date]]

    return render_template_string(html, daily=daily, dates=sorted(daily.keys()))

LOGIN_TEMPLATE = '''
    <h1>Login</h1>
    {% if error %}
      <p style="color:red;">{{ error }}</p>
    {% endif %}
    <form method="post">
      <input type="password" name="password" placeholder="Passwort" required>
      <input type="submit" value="Login">
    </form>
'''

import os
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(debug=True, host="0.0.0.0", port=port)
