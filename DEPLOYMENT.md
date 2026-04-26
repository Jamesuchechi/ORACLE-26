# ◈ ORACLE-26: Deployment Guide

This guide details the steps to deploy the ORACLE-26 Intelligence Terminal from scratch.

## 1. Prerequisites
- Python 3.10+
- Node.js 18+
- [Groq API Key](https://console.groq.com/) (Required for AI Analyst)

## 2. Infrastructure Setup
The project is designed to be split-deployed:
- **Backend (FastAPI)**: Deploy to [Railway](https://railway.app) or [Render](https://render.com).
- **Frontend (Vite/React)**: Deploy to [Vercel](https://vercel.com) or [Netlify](https://netlify.com).

## 3. Backend Deployment
1.  **Clone & Install**:
    ```bash
    git clone https://github.com/your-username/ORACLE-26.git
    cd ORACLE-26
    pip install -r requirements.txt
    ```
2.  **Environment Variables**:
    Set the following in your deployment platform:
    - `GROQ_API_KEY`: Your Groq key.
    - `CONFLUX_API_KEY`: Your custom X-API-Key (default: `conflux_dev_2026`).
3.  **Data Pipeline**:
    Run the bootstrap script to generate the initial signal vectors:
    ```bash
    python src/scripts/bootstrap_signals.py
    ```
4.  **Start API**:
    ```bash
    python api.py
    ```

## 4. Frontend Deployment
1.  **Navigate to Frontend**:
    ```bash
    cd frontend
    npm install
    ```
2.  **Environment Variables**:
    - `VITE_API_URL`: The URL of your deployed FastAPI backend.
3.  **Build & Deploy**:
    ```bash
    npm run build
    ```

## 5. Post-Deployment Verification
- Visit `/health` on your backend URL to verify the neural link.
- Open the `/docs` endpoint to view the full OpenAPI documentation.
- Test the dashboard to ensure the signal fingerprint bars are loading.

---
**Status: Neural Link Established. Ready for Production.**
