from flask import Flask, request, jsonify
from flask_cors import CORS
from models import db, AppUsage
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

DB_USER = os.getenv("DATABASE_USERNAME")
DB_PASSWORD = os.getenv("DATABASE_PASSWORD")
DB_HOST = os.getenv("DATABASE_HOST")
DB_PORT = os.getenv("DATABASE_PORT")
DB_NAME = os.getenv("DATABASE_NAME")

app.config['SQLALCHEMY_DATABASE_URI'] = (
    f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)


@app.route('/api/usage/start', methods=['POST'])
def start_usage():
    data = request.json

    usage = AppUsage(
        user_id=data.get('user_id'),
        country=data.get('country'),
        latitude=data.get('latitude'),
        longitude=data.get('longitude'),
        device_brand=data.get('device_brand'),
        device_model=data.get('device_model'),
        os_version=data.get('os_version'),
        platform=data.get('platform'),
        app_version=data.get('app_version'),
        start_time=datetime.utcnow()
    )

    db.session.add(usage)
    db.session.commit()

    return jsonify({
        "message": "Usage commncé",
        "usage_id": usage.id
    }), 201

@app.route('/api/usage/stop', methods=['POST'])
def stop_usage():
    data = request.json
    usage_id = data.get('usage_id')

    usage = AppUsage.query.get(usage_id)
    if not usage:
        return jsonify({"error": "Usage not found"}), 404

    usage.end_time = datetime.utcnow()
    usage.duration_seconds = int(
        (usage.end_time - usage.start_time).total_seconds()
    )

    db.session.commit()

    return jsonify({
        "message": "Usage stopped",
        "duration": usage.duration_seconds
    })

@app.route('/api/admin/stats', methods=['POST'])
def admin_stats():
    data = request.json

    if not data or data.get("password") != 'FERFE@z#85241zefFDSF':
        return jsonify({"error": "Unauthorized"}), 401

    usages = AppUsage.query.order_by(AppUsage.start_time.desc()).all()

    result = []
    for u in usages:
        result.append({
            "id": str(u.id),
            "user_id": u.user_id,
            "country": u.country,
            "latitude": u.latitude,
            "longitude": u.longitude,
            "device_brand": u.device_brand,
            "device_model": u.device_model,
            "os_version": u.os_version,
            "platform": u.platform,
            "app_version": u.app_version,
            "start_time": u.start_time,
            "end_time": u.end_time,
            "duration_seconds": u.duration_seconds
        })

    return jsonify({
        "total_records": len(result),
        "data": result
    }), 200


if __name__ == '__main__':
    app.run(debug=True)
