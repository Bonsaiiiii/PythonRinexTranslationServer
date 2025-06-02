from flask import Flask, request, jsonify
import signal
import subprocess
import os
import platform

app = Flask(__name__)

process = None

@app.route('/')
def index():
    return open("index.html").read()

@app.route('/run_ntrip', methods=['POST'])
def run_ntrip():
    global process

    arquivo = request.form.get('arquivo')
    user = request.form.get('user')
    password = request.form.get('password')
    host = request.form.get('host')
    port = request.form.get('port')
    mountpoint = request.form.get('mountpoint')
    ntimer = request.form.get('ntimer')

    if not user or not password:
        return jsonify({"error": "User and Password are required!"}), 400

    command = [
        "python3", "NtripClient.py",
        "--user=" + user,
        "--password=" + password,
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

@app.route('/stop_ntrip', methods=['POST'])
def stop_ntrip():
    global process

    if process is None:
        return jsonify({"error": "NTRIP Client is not running!"}), 400

    try:
        if platform.system() == "Windows":
            process.send_signal(signal.CTRL_BREAK_EVENT)
        else:
            os.killpg(os.getpgid(process.pid), signal.SIGTERM)

        process.wait(timeout=5)
        process = None
        return jsonify({"message": "NTRIP Client stopped successfully!"}), 200

    except Exception as e:
        return jsonify({"error": f"Failed to stop NTRIP Client: {str(e)}"}), 500
        
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

