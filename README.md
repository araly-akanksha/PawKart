# PawKart Local Development Setup Guide

Welcome to the PawKart developer team! This guide will help you set up your local environment so you can run both the frontend and backend locally, and how to troubleshoot the common "Server Offline" error.

---

## 1. Prerequisites

Before cloning the repository, ensure you have the following installed on your machine:
- **Git**: To clone the repository and push your changes.
- **Python 3.8+**: Required for the FastAPI backend and AI forecasting models.
- **VS Code**: Recommended code editor.
- **VS Code "Live Server" Extension**: Highly recommended for serving the frontend files locally.

---

## 2. Environment Variable Setup

1. Clone the repository to your local machine:
   ```bash
   git clone https://github.com/araly-akanksha/PawKart.git
   cd PawKart
   ```

2. Navigate to the `backend` directory:
   ```bash
   cd backend
   ```

3. Create your local `.env` file:
   Copy the provided `.env.example` to a new file named `.env`:
   - On Windows: `copy .env.example .env`
   - On Mac/Linux: `cp .env.example .env`

4. Edit `.env` and fill in your database credentials:
   ```env
   DATABASE_URL=postgresql://user:password@localhost:5432/pawkart_db
   ```
   *(Note: If the team is currently defaulting to local SQLite for development, this step might be optional, but always ensure your `.env` is properly configured before running database migrations).*

---

## 3. Commands to Start Backend

The backend is built with FastAPI. It serves the REST API and connects to our database.

1. Open a new terminal and navigate to the backend folder:
   ```bash
   cd PawKart/backend
   ```
2. (Optional but recommended) Create and activate a Python virtual environment:
   ```bash
   # Windows
   python -m venv venv
   .\venv\Scripts\activate
   # Mac/Linux
   python3 -m venv venv
   source venv/bin/activate
   ```
3. Install the required Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Start the FastAPI development server:
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```
   *Leave this terminal running. You can view the API documentation at [http://localhost:8000/docs](http://localhost:8000/docs).*

---

## 4. Commands to Start Frontend

The frontend consists of static Vanilla JavaScript and HTML files. 

1. Open the `PawKart/Store-Owner-Panel/HTML` folder in your code editor (e.g., VS Code).
2. Start a local server to serve the HTML files. 
   - **Using VS Code Live Server (Recommended):** Right-click `index.html` and select "Open with Live Server". This will open `http://127.0.0.1:5500/index.html` in your browser.
   - **Using Python:** If you don't use VS Code, open a terminal in the `HTML` folder and run:
     ```bash
     python -m http.server 5500
     ```
     Then open your browser to `http://localhost:5500`.

---

## 5. Troubleshooting: 'Server Offline' Issue

If you open the frontend and see a **"Server Offline"** error message in the product grid, the frontend JavaScript is failing to `fetch()` data from the backend.

### Check 1: Is the backend actually running?
Ensure that your backend terminal is still open and running `uvicorn`. If it crashed due to a database connection error, check your `.env` file.

### Check 2: Are you running on different laptops/devices?
Currently, the frontend JavaScript files (`script.js`, `dashboard.js`, `admin.js`) have hardcoded `fetch` requests pointing to `http://localhost:8000`.
- **Localhost means "this exact machine."**
- If you start the backend on Laptop A, and try to view the frontend on Laptop B, Laptop B will try to look for the backend on *itself* (localhost) and fail.

**How to fix for cross-device testing:**
1. Find the local IP address of the machine running the backend (e.g., `192.168.1.5`).
2. Ensure the backend was started with `--host 0.0.0.0`.
3. Open the frontend JS files (`script.js`, `dashboard.js`, `admin.js`) in your editor.
4. Use **Find and Replace** to replace `http://localhost:8000` with `http://192.168.1.5:8000`.
5. Reload the frontend. The "Server Offline" error should disappear. 

*(Note: Before committing your code back to the main repository, please avoid committing your personal IP address changes. We will be migrating to a global config variable soon!)*
