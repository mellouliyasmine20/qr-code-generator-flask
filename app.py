import os
import json
import uuid
from datetime import datetime
import qrcode
from flask import Flask, render_template, request

app = Flask(__name__)

QR_FOLDER = os.path.join("static", "qrcodes")
HISTORY_FILE = "history.json"


def load_history():
    """Charge l'historique depuis le fichier JSON (liste vide si le fichier n'existe pas encore)."""
    if not os.path.exists(HISTORY_FILE):
        return []
    with open(HISTORY_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_history(history):
    """Sauvegarde la liste d'historique dans le fichier JSON."""
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)


@app.route("/")
def index():
    history = load_history()
    return render_template("index.html", history=history)


@app.route("/generate", methods=["POST"])
def generate():
    data = request.form.get("data", "").strip()
    fill_color = request.form.get("fill_color") or "black"
    back_color = request.form.get("back_color") or "white"
    history = load_history()

    if not data:
        return render_template("index.html", error="Le texte ou le lien ne peut pas être vide.", history=history)

    qr = qrcode.QRCode(
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color=fill_color, back_color=back_color)

    # Nom de fichier unique grâce à uuid4()
    filename = f"qr_{uuid.uuid4().hex[:8]}.png"
    filepath = os.path.join(QR_FOLDER, filename)
    img.save(filepath)

    # On ajoute cette génération à l'historique
    history.insert(0, {
        "data": data,
        "filename": filename,
        "fill_color": fill_color,
        "back_color": back_color,
        "date": datetime.now().strftime("%d/%m/%Y %H:%M"),
    })
    save_history(history)

    return render_template("index.html", qr_image=filename, data=data, history=history)


if __name__ == "__main__":
    app.run(debug=True)