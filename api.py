import os
from flask import Flask, request, jsonify
from flask import send_file
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import download
from yt_dlp import YoutubeDL
from sqlalchemy.dialects.postgresql import psycopg2

app = Flask(__name__)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
CORS(app)

# Explicitly specify the PostgreSQL dialect
dialect = 'postgresql+psycopg2'

# Construct the database URL
db_url = f"{dialect}://default:mtiTvX8qCyk4@ep-bold-water-a1hya62n.ap-southeast-1.aws.neon.tech:5432/verceldb?sslmode=require"

# Set the SQLAlchemy database URI
app.config["SQLALCHEMY_DATABASE_URI"] = db_url

# Initialize SQLAlchemy with the Flask application
db = SQLAlchemy(app)

class History(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String)
    image = db.Column(db.String)
    link = db.Column(db.String)

    def __repr__(self):
        return f"-\nID:{self.id}\nTITLE:{self.title}\nIMAGE:{self.image}\nLINK:{self.link}\n-"

@app.route("/", methods=["GET"])
def main_route():
    return jsonify({"error": "Wrong URL"})

# Define other routes and functionalities as before...

@app.route("/history", methods=["GET"])
def history():
    db_query = History.query.order_by(History.id.desc()).all()
    result = []
    for row in db_query:
        result.append(
            {"id": row.id, "title": row.title, "image": row.image, "link": row.link}
        )
    return jsonify(result)

@app.route("/extract_info", methods=["POST"])
def extract_info():
    data = request.json
    with YoutubeDL() as ydl:
        try:
            if "youtu" in data:
                info = ydl.extract_info(data, download=False, process=False)
                ydl.sanitize_info(info)
                save_view = History(
                    title=info["title"],
                    image=info["thumbnail"],
                    link=info["original_url"],
                )
                db.session.add(save_view)
                db.session.commit()
                return jsonify(info)
            else:
                info = ydl.extract_info(data, download=False)
                save_view = History(
                    title=info["title"],
                    image=info["thumbnail"],
                    link=info["original_url"],
                )
                db.session.add(save_view)
                db.session.commit()
                return jsonify(ydl.sanitize_info(info))
        except Exception as e:
            error_message = f"An error occurred: {str(e)}"
            return jsonify({"error": error_message}), 500


@app.route("/get_me_link", methods=["POST"])
def get_download_link():
    data = request.json
    print(data)
    file = download.get_file(data["url"], data["type"])
    return {"url": "https://namkit-8c9bfd4e30aa.herokuapp.com/serve_file/" + file}


@app.route("/serve_file/<file>")
def serve_file(file):
    path = os.getcwd()
    download_file = path + "/files/" + file
    return send_file(download_file, as_attachment=True)

port = int(os.environ.get("PORT", 5000))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=port)
