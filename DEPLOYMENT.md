# Deployment Guide - Render

## Prerequisites
- GitHub account with the repository pushed
- Render account (free tier available at https://render.com)

## Step-by-Step Deployment

### 1. Create `.env.example` (Optional - for reference)
```
GMAIL_USER=your-email@gmail.com
GMAIL_PASSWORD=your-app-password
```

### 2. Connect GitHub to Render
1. Go to https://render.com
2. Sign up or log in with your GitHub account
3. Click "New+" → "Web Service"
4. Select "Deploy an existing repository"
5. Search for "Online-quiz-management" and click "Connect"

### 3. Configure Web Service
- **Name**: online-quiz-management
- **Environment**: Python 3
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `gunicorn app:app`
- **Plan**: Free (or paid as needed)

### 4. Add Environment Variables
In Render dashboard, go to "Environment" tab and add:
```
GMAIL_USER=your-email@gmail.com
GMAIL_PASSWORD=your-app-password
```
(These are optional - the app will work without them, but email features won't work)

### 5. Deploy
- Click "Create Web Service"
- Render will automatically deploy when you push to GitHub
- Your app will be live at: `https://your-app-name.onrender.com`

### 6. Auto-Deploy Setup
To auto-deploy on push:
- In Render dashboard → Settings → Auto-Deploy
- Select "Yes" for "Auto-Deploy on Push"

## Troubleshooting

### Error: "Build failed"
- Check requirements.txt syntax
- Verify all imports in app.py match requirements.txt

### Email not working
- Set GMAIL_USER and GMAIL_PASSWORD in Environment variables
- Use Gmail app password (not regular password): https://support.google.com/accounts/answer/185833

### App sleeping on free tier
- Free tier apps sleep after 15 minutes of inactivity
- To prevent this, upgrade to paid plan or handle gracefully in code

### File permissions error
- JSON files need proper permissions
- Render will handle this automatically

## Monitoring

After deployment:
1. Check "Logs" tab for errors
2. Monitor "Metrics" for performance
3. Check "Events" for deployment history

## Notes
- Data is stored in JSON files (admins.json, questions.json, etc.)
- On Render free tier, data persists between deployments but is lost when service is destroyed
- For production, consider migrating to a database (PostgreSQL)
