# ◈ CONFLUX — Backend Deployment Guide (Render)

Since Render's free tier doesn't offer an interactive shell, we use a custom build script to install dependencies and bootstrap the intelligence data automatically.

### 1. Build Script
I have created `render_build.sh` in your project root. This script will:
1.  Install all Python dependencies.
2.  Run `wc2026_pipeline.py --all` to generate the processed data files.

### 2. Render Configuration
When creating your **Web Service** on Render, use these settings:

| Field | Value |
| :--- | :--- |
| **Name** | `oracle-26-backend` |
| **Runtime** | `Python 3` |
| **Build Command** | `bash render_build.sh` |
| **Start Command** | `uvicorn api:app --host 0.0.0.0 --port 8000` |

### 3. Environment Variables (MANDATORY)
Ensure these are set in the **Environment** tab before your first deploy, or the pipeline will fail:

| Key | Value | Notes |
| :--- | :--- | :--- |
| `FRED_API_KEY` | *Your Key* | Required for Economic signals |
| `ALPHA_VANTAGE_KEY` | *Your Key* | Required for Financial signals |
| `GROQ_API_KEY` | *Your Key* | Required for AI Analyst |
| `REDDIT_CLIENT_ID` | *Your ID* | Required for Social signals |
| `REDDIT_CLIENT_SECRET` | *Your Secret* | Required for Social signals |
| `CONFLUX_API_KEY` | `conflux_dev_2026` | Security header |

### 4. Verification
Once Render shows "Live", test the `/health` endpoint:
`https://your-service-name.onrender.com/health`

---

### ⚠️ Important Notes
*   **Initial Build Time**: The first deployment will take **5-10 minutes** because it is collecting data from multiple APIs and running simulations. 
*   **Build Timeout**: If the build fails due to a timeout, try running it again; the free tier can be slow, but subsequent runs may be faster if some tasks were cached.
*   **VITE_API_URL**: Once the backend is live, copy its URL (e.g., `https://oracle-26-backend.onrender.com`) and add it as an environment variable in your Vercel frontend project.
