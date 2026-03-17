from flask import Flask, request, jsonify
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

app = Flask(__name__)

# === GOOGLE SHEETS SETUP ===
scope = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]
creds = Credentials.from_service_account_file("credentials.json", scopes=scope)
client = gspread.authorize(creds)

sheet_data = client.open("DATA_HK").worksheet("DATA")
sheet_user = client.open("DATA_HK").worksheet("USER_HK")

# === LOGIN ===
@app.route("/login", methods=["POST"])
@app.route("/login", methods=["POST"])
def login():
    data = request.json

    # 🔥 FIX: bersihkan input
    email = str(data.get("email")).strip().lower()
    password = str(data.get("password")).strip()

    users = sheet_user.get_all_records()

    for user in users:
        # 🔥 FIX: bersihkan data dari sheet
        saved_email = str(user["Email"]).strip().lower()
        saved_password = str(user["Password"]).strip()

        print("INPUT:", email, password)
        print("SHEET:", saved_email, saved_password)

        if saved_email == email:
            if saved_password == password:
                return jsonify({
                    "status": "success",
                    "nama": user.get("Nama HK", ""),
                    "role": user.get("Role", "")
                })
            else:
                return jsonify({
                    "status": "error",
                    "message": "Password salah"
                }), 401

    return jsonify({
        "status": "error",
        "message": "Email tidak terdaftar"
    }), 404

# === INPUT DATA HK ===
@app.route("/input", methods=["POST"])
def input_data():
    data = request.json

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    row = [
        now,
        data.get("nama"),
        data.get("kamar"),
        data.get("status_awal"),
        data.get("pekerjaan"),
        str(data.get("detail")),
        str(data.get("amenities")),
        str(data.get("laundry")),
        data.get("catatan")
    ]

    sheet_data.append_row(row)

    return jsonify({"status": "success"})

# === GET USER (ADMIN) ===
@app.route("/users", methods=["GET"])
def get_users():
    users = sheet_user.get_all_records()
    return jsonify(users)

# === UPDATE USER (ADMIN) ===
@app.route("/update-user", methods=["POST"])
def update_user():
    data = request.json
    email = data.get("email")

    records = sheet_user.get_all_records()

    for i, user in enumerate(records, start=2):
        if user["Email"] == email:
            sheet_user.update(f"B{i}", data.get("nama"))
            sheet_user.update(f"C{i}", data.get("password"))
            return jsonify({"status": "updated"})

    return jsonify({"status": "not found"}), 404

# === RUN ===
if __name__ == "__main__":
    app.run(debug=True)