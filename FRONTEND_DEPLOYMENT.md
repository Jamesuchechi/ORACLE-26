# ◈ CONFLUX — Frontend Deployment Guide (Vercel)

Now that your backend is live at `https://conflux-o98t.onrender.com`, it's time to launch the UI.

### 1. Create a New Project on Vercel
1.  Go to [vercel.com](https://vercel.com) and click **Add New > Project**.
2.  Import your GitHub repository.

### 2. Configure Project Settings
| Field | Value |
| :--- | :--- |
| **Framework Preset** | `Vite` (should be auto-detected) |
| **Root Directory** | `frontend` |
| **Build Command** | `npm run build` |
| **Output Directory** | `dist` |

### 3. Environment Variables
Add the following key to the **Environment Variables** section:

| Key | Value | Notes |
| :--- | :--- | :--- |
| `VITE_API_URL` | `https://conflux-o98t.onrender.com` | No trailing slash |

### 4. Deploy!
Click **Deploy**. Vercel will build your React app and provide a production URL.

---

### 🧪 Post-Deployment Test
1.  Open your new Vercel URL.
2.  Open the browser console (F12).
3.  Check if there are any CORS errors or 404s.
4.  The dashboard should now load real data from your Render backend!

> [!TIP]
> If you see `Mixed Content` errors, make sure your `VITE_API_URL` starts with `https://`.
