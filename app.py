from flask import Flask, render_template, request, redirect, url_for, session, flash, Response, jsonify
from flask_mysqldb import MySQL
from model.UserModal import UserModel
from model.CameraModel import CameraModel
from model.LogAktivitasModal import LogAktivitasModal
from werkzeug.security import check_password_hash, generate_password_hash
import cv2
import datetime

import time
from ultralytics import YOLO

app = Flask(__name__)
app.secret_key = 'sijaga'

# Konfigurasi koneksi MySQL
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'sijaga'

mysql = MySQL(app)
user_model = UserModel(mysql)
camera_model = CameraModel(mysql)
log_modal = LogAktivitasModal(mysql)


# Auth 
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = user_model.get_user_by_email(email)

        if user:
            hashed_password = user[2]  
            if check_password_hash(hashed_password, password):
                session['user_id'] = user[0]
                session['username'] = user[1]
                log_modal.log_activity(
                    event_type="LOGIN_SUCCESS",
                    message=f"'{user[1]}' berhasil masuk."
                )
                flash('Login berhasil!', 'success')
                return redirect(url_for('dashboard'))
        flash('Email atau password salah!', 'danger')
    return render_template('auth/login-page.html')


@app.route('/logout')
def logout():
    username = session.get('username', 'Unknown user')
    log_modal.log_activity(
        event_type="LOGOUT",
        message=f"'{username}' telah keluar."
    )
    session.clear()
    return redirect(url_for('login'))


@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('dashboard/dashboard-page.html')


@app.route('/manajeman-kamera')
def manajeman_kamera():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    data = camera_model.get_all()
    return render_template('dashboard/camera/manajeman-kamera-page.html',data=data)

@app.route('/store-camera', methods=['POST'])
def storeCamera():
    room = request.form['room']
    source = request.form['source']
    camera_model.save_camera(room, source)
    flash('Kamera berhasil ditambahkan.', 'success')
    return redirect(url_for('manajeman_kamera'))

@app.route('/admin/camera/delete/<int:id>', methods=['POST'])
def deletCamera(id):
    camera_model.delete_camera(id)
    flash('Kamera berhasil dihapus.', 'success')
    return redirect(url_for('manajeman_kamera'))

@app.route('/admin/camera/update', methods=['POST'])
def update_camera():
    id = request.form['id']
    room = request.form['room']
    source = request.form['source']
    camera_model.update_camera(id, room, source)
    flash('Data kamera berhasil diperbarui.', 'success')
    return redirect(url_for('manajeman_kamera'))

@app.route('/manajemen-user')
def manajemen_user():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user = user_model.get_user_all()
    return render_template('dashboard/users/manajeman-user-page.html',user=user)

@app.route('/log-aktivitas')
def logAktivitas():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    logs = log_modal.get_all_today()
    current_date = datetime.datetime.now().strftime('%A, %d %B %Y')
    return render_template('dashboard/log-aktivitas/log-aktivitas-page.html',logs=logs,current_date=current_date)

@app.route('/admin/user/create', methods=['POST'])
def createUser():
    name = request.form['name']
    email = request.form['email']
    role = request.form['role']
    password = request.form['password']
    hashed_password = generate_password_hash(password)
    if user_model.insert_user(name, email,role, hashed_password):
        flash('User berhasil ditambahkan!', 'success')
    else:
        flash('Gagal menambahkan user!', 'error')
    return redirect(url_for('manajemen_user'))

@app.route('/admin/user/delete/<int:id>', methods=['POST'])
def deleteUser(id):
    user_model.delete_user(id)
    flash('User berhasil dihapus.', 'success')
    return redirect(url_for('manajemen_user'))

@app.route('/admin/user/update', methods=['POST'])
def editUser():
    id = request.form['id']
    name = request.form['name']
    email = request.form['email']
    role = request.form['role']

    if user_model.update_user(id, name, email, role):
        flash('User berhasil diupdate!', 'success')
    else:
        flash('Gagal mengubah user!', 'error')
    return redirect(url_for('manajemen_user'))



@app.route('/log-deteksi')
def log_deteksi():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    current_date = datetime.datetime.now().strftime('%A, %d %B %Y')
    logs = [
        {"waktu": "2025-05-23 10:21", "lokasi": "Ruang Tamu", "deteksi": "Gerakan terdeteksi"},
        {"waktu": "2025-05-23 10:25", "lokasi": "Teras", "deteksi": "Tidak ada aktivitas"},
    ]
    return render_template('dashboard/history/log-deteksi-page.html', logs=logs,  current_date=current_date,)

@app.route('/live-monitoring')
def live_feed():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    cameras = camera_model.get_all()
    return render_template('dashboard/camera/live-monitoring-page.html', cameras=cameras)

@app.route('/camera/<int:id>')
def single_camera_view(id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    camera = camera_model.get_camera_by_id(id)
    if not camera:
        return "Camera not found", 404
    threat_detected = True 
    threat_type = "Senjata Api" if threat_detected else None

    return render_template(
        'dashboard/camera/camera-single-page.html',
        camera=camera,
        threat_detected=threat_detected,
        threat_type=threat_type
    )


camera_streams = {}
model = YOLO("models/my_model.pt")  
def gen_frames(cam_id, source):
    if str(source).strip() == "0":
        source_path = 0
    else:
        source_path = f"http://{source}:8080/video"
        # source_path = f"vidio.mp4"

    if cam_id not in camera_streams:
        camera_streams[cam_id] = cv2.VideoCapture(source_path)

    cap = camera_streams[cam_id]

    while True:
        success, frame = cap.read()
        if not success:
            cap.release()
            camera_streams.pop(cam_id, None)
            time.sleep(2)
            cap = cv2.VideoCapture(source_path)
            camera_streams[cam_id] = cap
            success, frame = cap.read()
            if not success:
                time.sleep(2)
                continue
        results = model.predict(frame, imgsz=640, conf=0.4, verbose=False)
        for r in results:
            for box in r.boxes:
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                cls = int(box.cls[0])
                label = model.names[cls]
                conf = box.conf[0]

                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 2)
                cv2.putText(frame, f'{label} {conf:.2f}', (x1, y1 - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


@app.route('/video_feed/<int:cam_id>')
def video_feed(cam_id):
    camera = camera_model.get_camera_by_id(cam_id)
    if not camera:
        return "Camera not found", 404

    source = camera["source"]
    return Response(gen_frames(cam_id, source),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

