# ✈️ Flights Posting API

A modern FastAPI-based backend for managing and posting flight-related data.

---

## ⚙️ Requirements

- **Python** `3.13.5`  
  > 🔧 If you face errors, make sure to update your Python version.

---

## 🚀 Getting Started

### 1. 🐍 Create and activate a virtual environment

#### On **Linux / macOS**:
```bash
python3.13 -m venv venv
source venv/bin/activate
```

#### On **Windows (CMD)**:
```cmd
python -m venv venv
venv\Scripts\activate
```

#### On **Windows (PowerShell)**:
```powershell
python -m venv venv
venv\Scripts\Activate.ps1
```

### 2. 📦 Install dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 3. 🔐 Set up environment variables

Create a `.env` file:

```bash
cp .env.example .env
```

Then edit `.env` and fill in the required values.

### 4. 🧪 Run the development server

```bash
uvicorn app.main:app --reload
```

- Open your browser at: http://127.0.0.1:8000
- Access interactive API docs at: http://127.0.0.1:8000/docs
- Alternative API docs at: http://127.0.0.1:8000/redocs

---

## 🧹 Code Formatting

To automatically format and lint your code with `ruff`:

```bash
ruff check . --fix
```

---

## 📁 Project Structure

```
app/
├── main.py          # FastAPI entry point
├── models/          # SQLAlchemy models
├── routes/          # API route definitions
├── handlers/        # Business logic
├── schemas/         # Pydantic schemas
└── config/          # App settings and env config
```

---

## 📝 Notes

- Use **Python 3.13.5** — this project may not be compatible with older versions.
- Consider using tools like uv for faster dependency installs.
- Make sure `.env` values are accurate, especially for database, JWT secrets, etc.
- Keep your virtual environment activated while working.

---
