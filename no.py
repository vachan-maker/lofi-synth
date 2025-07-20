from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/callback', methods=['POST'])
def callback():
    data = request.json
    print("🎧 Received callback:", data)
    # Save or handle the audio_url, etc.
    return jsonify({"status": "received"}), 200

if __name__ == "__main__":
    app.run(port=5000)
