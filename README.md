# 🛡️ AI-Powered Attendance Monitoring System

[![Django](https://img.shields.io/badge/Django-5.0+-092e20?style=for-the-badge&logo=django)](https://www.djangoproject.com/)
[![OpenCV](https://img.shields.io/badge/OpenCV-Face%20Rec-5C3EE8?style=for-the-badge&logo=opencv)](https://opencv.org/)
[![WebSockets](https://img.shields.io/badge/Channels-Real--Time-white?style=for-the-badge&logo=socket.io&logoColor=black)](https://channels.readthedocs.io/)
[![Deployment](https://img.shields.io/badge/Render-Live-46E3B7?style=for-the-badge&logo=render)](https://render.com/)

A modern, secure, and enterprise-ready attendance tracking solution. This system leverages **Face Recognition**, **Device Fingerprinting**, and **Real-Time WebSockets** to eliminate proxy attendance and "buddy punching."

---

## 🌟 Key Features

### 📸 Smart Security
- **Selfie Verification**: Uses OpenCV's **LBPH (Local Binary Patterns Histograms)** to match live selfies against profile pictures with high precision.
- **Device Lock**: Fingerprints browser hardware (CPU, RAM, Resolution) and locks sessions to specific devices.
- **Anti-Fraud**: Rejects logins from unrecognized devices or unmatched faces.

### ⚡ Real-Time Monitoring
- **Admin Toasts**: Instant WebSocket notifications on the Admin Dashboard whenever an employee marks attendance.
- **Live Status**: Track who's "Present", "Late", or "Pending" without page refreshes.

### 📅 Enterprise Management
- **Shift Tracking**: Automated "Late" flagging based on custom shift timings (e.g., Morning/Night).
- **Leave Module**: Comprehensive system for employees to apply for Sick/Casual leaves with Admin approval workflows.
- **Professional Dashboard**: Interactive charts (Chart.js) showing attendance trends and leave balances.

---

## 🚀 Tech Stack

- **Backend**: Python 3.14+, Django 5.0
- **Real-time**: Django Channels & Daphne (ASGI)
- **AI/Vision**: OpenCV-Contrib, NumPy
- **Frontend**: HTML5, CSS3 (Modern UI), JavaScript (ES6)
- **Database**: SQLite (Development), Production Ready
- **Static/Media**: WhiteNoise & Cloud Storage Support

---

## 🛠️ Installation & Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/kavyakundar004/attendance_monitor.git
   cd attendance_monitor
   ```

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Initialize the Project**:
   Run our custom setup command to create the admin and default data:
   ```bash
   cd home/webapp/attendance_monitor
   python manage.py migrate
   python manage.py setup_project
   ```

4. **Run Locally**:
   ```bash
   python manage.py runserver
   ```

---

## 🔐 Admin Credentials (Default)
- **Username**: `admin`
- **Password**: `admin123`
- **Panel**: `http://127.0.0.1:8000/admin_dashboard/`

---

## ☁️ Deployment

This project is optimized for **Render**. 
- **Build Command**: `./build.sh`
- **Start Command**: `cd home/webapp/attendance_monitor && daphne attendance_monitor.asgi:application --port $PORT --bind 0.0.0.0`

---

## 📝 License
Distributed under the MIT License. See `LICENSE` for more information.

