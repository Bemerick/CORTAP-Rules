# Deployment Guide - Render.com

This guide walks you through deploying the FTA Comprehensive Review application to Render.com.

## Prerequisites

1. **GitHub Repository**: Push your code to GitHub
2. **Render Account**: Sign up at https://render.com
3. **Database Backup**: Have your PostgreSQL database ready

---

## Option 1: Deploy Using render.yaml (Recommended)

This method deploys all services automatically using the `render.yaml` blueprint.

### Steps:

1. **Push to GitHub**
   ```bash
   git add .
   git commit -m "Prepare for Render deployment"
   git push origin main
   ```

2. **Create New Blueprint in Render**
   - Go to https://dashboard.render.com
   - Click **"New"** → **"Blueprint"**
   - Connect your GitHub repository
   - Select the `CORTAP-Rules` repository
   - Render will detect `render.yaml` and create:
     - PostgreSQL database (`fta-review-db`)
     - FastAPI backend (`fta-review-api`)
     - React frontend (`fta-review`)

3. **Wait for Deployment**
   - Database will be created first
   - Backend will deploy next
   - Frontend will deploy last
   - Initial deploy takes ~5-10 minutes

4. **Restore Database**
   - Go to your database service in Render dashboard
   - Click **"Connect"** to get connection details
   - Use `pg_restore` or your SQL backup to restore data:
   ```bash
   # Export from local database
   pg_dump -U postgres -d fta_review > backup.sql

   # Import to Render database (get connection string from Render dashboard)
   psql <RENDER_DATABASE_URL> < backup.sql
   ```

5. **Update Frontend URL** (if names differ)
   - If your services have different names, update the environment variable:
   - Backend service → Environment → `ALLOWED_ORIGINS` → Add your frontend URL
   - Frontend service → Environment → `VITE_API_URL` → Set to your backend URL

---

## Option 2: Manual Deployment

### Step 1: Create PostgreSQL Database

1. In Render Dashboard, click **"New"** → **"PostgreSQL"**
2. Configure:
   - **Name**: `fta-review-db`
   - **Database**: `fta_review`
   - **User**: `fta_user`
   - **Plan**: Free
3. Click **"Create Database"**
4. Note the **Internal Database URL** (starts with `postgresql://`)

### Step 2: Deploy FastAPI Backend

1. Click **"New"** → **"Web Service"**
2. Connect your GitHub repository
3. Configure:
   - **Name**: `fta-review-api`
   - **Root Directory**: `backend`
   - **Environment**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - **Plan**: Free

4. **Add Environment Variables**:
   ```
   DATABASE_URL = <your-database-internal-url>
   API_HOST = 0.0.0.0
   API_PORT = $PORT
   API_RELOAD = False
   ALLOWED_ORIGINS = https://fta-review.onrender.com
   PYTHON_VERSION = 3.11.0
   ```

5. Click **"Create Web Service"**

### Step 3: Deploy React Frontend

1. Click **"New"** → **"Static Site"**
2. Connect your GitHub repository
3. Configure:
   - **Name**: `fta-review`
   - **Root Directory**: `frontend`
   - **Build Command**: `npm install && npm run build`
   - **Publish Directory**: `dist`
   - **Plan**: Free

4. **Add Environment Variable**:
   ```
   VITE_API_URL = https://fta-review-api.onrender.com
   ```

5. Click **"Create Static Site"**

---

## Post-Deployment

### 1. Verify Backend

Test the API health endpoint:
```bash
curl https://fta-review-api.onrender.com/health
# Should return: {"status":"healthy"}
```

Test the questions endpoint:
```bash
curl https://fta-review-api.onrender.com/api/questions
# Should return JSON array of questions
```

### 2. Verify Frontend

Visit: `https://fta-review.onrender.com`

You should see the FTA Review application homepage.

### 3. Test Full Workflow

1. Create a new project
2. Complete the assessment questionnaire
3. View assessment results
4. View LOE summary

---

## Environment Variables Reference

### Backend Environment Variables

| Variable | Value | Description |
|----------|-------|-------------|
| `DATABASE_URL` | `postgresql://...` | PostgreSQL connection string (from Render DB) |
| `API_HOST` | `0.0.0.0` | Host to bind to |
| `API_PORT` | `$PORT` | Port (automatically set by Render) |
| `API_RELOAD` | `False` | Disable auto-reload in production |
| `ALLOWED_ORIGINS` | `https://fta-review.onrender.com` | Frontend URL for CORS |
| `PYTHON_VERSION` | `3.11.0` | Python version |

### Frontend Environment Variables

| Variable | Value | Description |
|----------|-------|-------------|
| `VITE_API_URL` | `https://fta-review-api.onrender.com` | Backend API URL |

---

## Database Migration

If you need to migrate data from your local database to Render:

### Method 1: SQL Dump

```bash
# 1. Export from local
pg_dump -U postgres -d fta_review -F p -f fta_review_backup.sql

# 2. Get Render database connection string
# From Render Dashboard → Your Database → Info → External Database URL

# 3. Import to Render
psql "<EXTERNAL_DATABASE_URL>" -f fta_review_backup.sql
```

### Method 2: Using Render Shell

```bash
# 1. In Render Dashboard, go to your database
# 2. Click "Shell"
# 3. Run SQL commands directly or restore from backup
```

---

## Troubleshooting

### Backend Issues

**Issue**: Backend returns 500 errors
- **Solution**: Check logs in Render Dashboard → Backend Service → Logs
- Verify `DATABASE_URL` is correct
- Ensure all environment variables are set

**Issue**: CORS errors
- **Solution**: Verify `ALLOWED_ORIGINS` includes your frontend URL
- Make sure there are no trailing slashes

### Frontend Issues

**Issue**: Can't connect to API
- **Solution**: Check browser console for errors
- Verify `VITE_API_URL` points to correct backend URL
- Ensure backend is deployed and running

**Issue**: Build fails
- **Solution**: Check build logs
- Verify `package.json` has all dependencies
- Try building locally first: `npm run build`

### Database Issues

**Issue**: Can't connect to database
- **Solution**: Verify `DATABASE_URL` format
- Check database is running in Render Dashboard
- Ensure database allows connections from backend service

---

## Free Tier Limitations

Render Free Tier includes:

- **Web Services**: Spins down after 15 minutes of inactivity
  - **Impact**: First request after inactivity takes ~30 seconds
  - **Solution**: Use a paid plan ($7/month) for always-on service

- **PostgreSQL**: 90-day expiration on free tier
  - **Impact**: Database will be deleted after 90 days
  - **Solution**: Upgrade to paid plan ($7/month) or export data regularly

- **Static Sites**: Always on, no limitations

---

## Custom Domains (Optional)

To use a custom domain:

1. Go to your service in Render Dashboard
2. Click **"Settings"** → **"Custom Domain"**
3. Add your domain (e.g., `fta-review.yourdomain.com`)
4. Update DNS records as instructed
5. Update CORS settings in backend with new domain

---

## Monitoring & Logs

- **View Logs**: Render Dashboard → Service → Logs
- **Metrics**: Render Dashboard → Service → Metrics
- **Health Checks**: Automatically configured at `/health`

---

## Updating the Application

After making changes:

```bash
git add .
git commit -m "Update application"
git push origin main
```

Render will automatically:
1. Detect the push
2. Rebuild the services
3. Deploy new versions

---

## Support

- **Render Documentation**: https://render.com/docs
- **Render Community**: https://community.render.com
- **Application Issues**: Check service logs in Render Dashboard

---

## URLs (Update these after deployment)

- **Frontend**: https://fta-review.onrender.com
- **Backend API**: https://fta-review-api.onrender.com
- **API Docs**: https://fta-review-api.onrender.com/api/docs
- **Database**: (Internal connection only)

---

**Deployment Complete!** 🎉

Your FTA Comprehensive Review application is now live on Render.com.
