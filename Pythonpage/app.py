from flask import Flask, request, jsonify
import signal
import subprocess
import os
import platform

app = Flask(__name__)

process = None

@app.after_request
def after_request(response):
    response.headers['Content-Type'] = 'text/html; charset=UTF-8'
    return response

@app.route('/')
def index():
    return open("index.html", encoding="utf-8").read()

@app.route('/run_ntrip', methods=['POST'])
def run_ntrip():
    global process

    arquivo = request.form.get('arquivo', '').strip()
    user = request.form.get('user', '').strip()
    password = request.form.get('password', '').strip()
    host = request.form.get('host', '').strip()
    port = request.form.get('port', '').strip()
    mountpoint = request.form.get('mountpoint', '').strip()
    latitude = request.form.get('latitude', '').strip()
    longitude = request.form.get('longitude', '').strip()
    altitude = request.form.get('altitude', '').strip()
    ntimer = request.form.get('ntimer', '').strip()
    enviapos = request.form.get('enviapos', '').strip()

    if not user or not password:
        return jsonify({"error": "User and Password are required!"}), 400

    if enviapos == 'N':
        command = [
            "python3", "NtripClient.py",
            "--user=" + user,
            "--password=" + password,
            "--maxtime=" + ntimer,
            host, port, mountpoint,
            "-f", os.path.join("C:/Users/Hugen/Documents/", arquivo + ".rtcm")
        ]
    elif enviapos == 'S':
        command = [
            "python3", "NtripClient.py",
            "--user=" + user,
            "--password=" + password,
            "--latitude=" + latitude,
            "--longitude=" + longitude,
            "--height=" + altitude,
            "--maxtime=" + ntimer,
            host, port, mountpoint,
            "-f", os.path.join("C:/Users/Hugen/Documents/", arquivo + ".rtcm")
        ]
    
    try:
        if platform.system() == "Windows":
            process = subprocess.Popen(
                command,
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP
            )
        else:
            process = subprocess.Popen(
                command,
                preexec_fn=os.setsid
            )

        return jsonify({"message": "NTRIP Client started successfully!"}), 200

    except Exception as e:
        return jsonify({"error": f"Error starting NTRIP Client: {str(e)}"}), 500
        
@app.route('/translate_rinex', methods=['POST'])
def translate_rinex():
    global process

    arquivo = request.form.get('arquivo')

    command = [
        "python3", "openRTK.py",
        "--input=" + arquivo,
        "--output=" + arquivo + "_obs",
        "--nav=" + arquivo + "_nav",
        "--gnav=" + arquivo + "_gnav",
        "--qnav=" + arquivo + "_qnav",
    ]

    try:
        if platform.system() == "Windows":
            process = subprocess.Popen(
                command,
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP
            )
        else:
            process = subprocess.Popen(
                command,
                preexec_fn=os.setsid
            )

        return jsonify({"message": "Tradução feita"}), 200

    except Exception as e:
        return jsonify({"error": f"Error starting NTRIP Client: {str(e)}"}), 500
    

from flask import send_from_directory

@app.route('/documents/<path:filename>')
def download_file(filename):
    documents_folder = 'C:/Users/Hugen/documents'
    print("Requested file:", filename)
    return send_from_directory(documents_folder, filename, as_attachment=True)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True, threaded=True)

