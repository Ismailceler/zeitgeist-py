from flask import Flask, render_template, request
from flask_assets import Bundle, Environment
import libsql_experimental as libsql
import os
from dotenv import load_dotenv
from datetime import datetime 
 
load_dotenv() 
app = Flask(__name__)
url = os.getenv("TURSO_DATABASE_URL")
auth_token = os.getenv("TURSO_AUTH_TOKEN")
conn = libsql.connect("zeitgeist.db", sync_url=url, auth_token=auth_token)

conn.execute("CREATE TABLE IF NOT EXISTS sleep (id INTEGER PRIMARY KEY AUTOINCREMENT, start_day DATETIME NOT NULL, end_day DATETIME)")
#conn.execute("INSERT INTO sleep(start_day) VALUES('{0}')".format(datetime.now().strftime("%Y-%m-%d %H:%M")))
#conn.execute("UPDATE sleep SET end_day = '{0}' WHERE end IS NULL".format(datetime.now().strftime("%Y-%m-%d %H:%M")))
conn.execute("CREATE TABLE IF NOT EXISTS buckets (id INTEGER PRIMARY KEY AUTOINCREMENT, bucket_name TEXT NOT NULL, shorthand TEXT NOT NULL)")
conn.execute("CREATE TABLE IF NOT EXISTS investments (id INTEGER PRIMARY KEY AUTOINCREMENT, day DATE NOT NULL, minutes INTEGER NOT NULL, bucket_ID INTEGER, FOREIGN KEY(bucket_ID) REFERENCES buckets(id))")

conn.commit()

conn.sync()


def getdatedata():
    today = datetime.today()
    week_num = today.isocalendar()[1]
    weekday_name = datetime.now().strftime("%A")
    year = today.year
    return [weekday_name, week_num, year]

def getbuckets():
   return conn.execute("select * from buckets").fetchall()

def getinvestments():
    return conn.execute("select i.id, i.day, i.minutes, b.bucket_name from investments i left join buckets b on b.id = i.bucket_id").fetchall()
def getcurrentweekinvestments():
    return conn.execute("select i.id, i.day, i.minutes, b.bucket_name from investments i left join buckets b on b.id = i.bucket_id where strftime('%W', i.day) == strftime('%W',date('now')) and strftime('%Y', i.day) == strftime('%Y', date('now'))").fetchall()

def addinvestment(minutes, bucket):
    print(datetime.today().strftime('%Y-%m-%d'))

    conn.execute("INSERT INTO investments(day, minutes, bucket_id) VALUES('{0}', {1}, {2})".format(datetime.today().strftime('%Y-%m-%d'), minutes, bucket))
    conn.commit()
    conn.sync()

assets = Environment(app)
js = Bundle("src/*.js", output="dist/main.js")

assets.register("js", js)
js.build()

@app.route("/")
def zeitgeist():
    buckets = getbuckets()
    investments = getcurrentweekinvestments()
    weekdata = getdatedata()
    return render_template("index.html", buckets=buckets, weekdata=weekdata, investments=investments)

@app.route("/invest", methods=["POST"])
def invest():
    minutes = request.form.get("minutes")
    bucket = request.form.get("bucket")
    addinvestment(minutes, bucket)
    buckets = getbuckets()
    investments = getinvestments()
    weekdata = getdatedata()
    return render_template("index.html", buckets=buckets, weekdata=weekdata, investments=investments)
    

if __name__ == "__main__":
    app.run(debug=True)