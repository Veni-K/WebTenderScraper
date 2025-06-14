from flask import Flask, render_template, request, send_file
from scraper import scrape_tender_site
import os
import uuid

app = Flask(__name__)
SAVE_FOLDER = "scraped_data"
os.makedirs(SAVE_FOLDER, exist_ok=True)

@app.route("/", methods=["GET", "POST"])
def index():
    data = None
    filename = None
    message = None

    if request.method == "POST":
        url = request.form.get("url")
        df, error = scrape_tender_site(url)

        if error:
            message = error
        elif df is not None:
            filename = f"{uuid.uuid4().hex}.csv"
            file_path = os.path.join(SAVE_FOLDER, filename)
            df.to_csv(file_path, index=False)
            data = df.head(10).to_html(classes="table table-bordered", index=False, border=0)
        else:
            message = "No tender table found."

    return render_template("index.html", table=data, file=filename, message=message)

@app.route("/download/<file>")
def download(file):
    return send_file(os.path.join(SAVE_FOLDER, file), as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)
