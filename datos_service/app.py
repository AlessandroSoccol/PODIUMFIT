from flask import Flask, jsonify

app = Flask(__name__)


@app.get("/health")
def health():
    return jsonify({"status": "ok", "service": "datos"}), 200


@app.route("/datos", methods=["GET"])
def obtener_datos():
    return jsonify({
        "equipo": "Los four",
        "proyecto": "PodiumFit",
        "servicio": "Microservicio extraído exitosamente",
        "status": 200
    }), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
