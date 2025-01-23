from flask import Flask, render_template, request
from flask_assets import Bundle, Environment
import libsql_experimental as libsql
import os
from dotenv import load_dotenv
from datetime import datetime 

load_dotenv() 
url = os.getenv("TURSO_DATABASE_URL")
auth_token = os.getenv("TURSO_AUTH_TOKEN")
conn = libsql.connect("zeitgeist.db", sync_url=url, auth_token=auth_token)
conn.execute("CREATE TABLE IF NOT EXISTS sleep (id INTEGER PRIMARY KEY AUTOINCREMENT, start DATETIME NOT NULL, end DATETIME)")
conn.execute("INSERT INTO sleep(start) VALUES('{0}')".format(datetime.now().strftime("%Y-%m-%d %H:%M")))
conn.execute("UPDATE sleep SET end = '{0}' WHERE end IS NULL".format(datetime.now().strftime("%Y-%m-%d %H:%M")))

conn.commit()

conn.sync()

app = Flask(__name__)

assets = Environment(app)
js = Bundle("src/*.js", output="dist/main.js")

assets.register("js", js)
js.build()

@app.route("/")
def zeitgeist():
    return render_template("index.html")

@app.route("/invest", methods=["POST"])
def invest():
    minutes = request.form.get("minutes")
    bucket = request.form.get("bucket")
    result = [minutes, bucket]
    return render_template("index.html", zg=[result])


if __name__ == "__main__":
    app.run(debug=True)