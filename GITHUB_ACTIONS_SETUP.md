# GitHub Actions Setup Guide

This guide will help you set up GitHub Actions to run your AI Podcast Agent automatically every day.

## 🚀 **Step 1: Create GitHub Repository**

1. **Create a new repository** on GitHub:
   - Go to https://github.com/new
   - Name it something like `ai-podcast-agent`
   - Make it **Private** (recommended for security)
   - Don't initialize with README (we'll push our existing code)

2. **Push your code** to GitHub:
   ```bash
   git init
   git add .
   git commit -m "Initial commit: AI Podcast Agent"
   git branch -M main
   git remote add origin https://github.com/YOUR_USERNAME/ai-podcast-agent.git
   git push -u origin main
   ```

## 🔐 **Step 2: Configure GitHub Secrets**

1. **Go to your repository** on GitHub
2. **Click Settings** → **Secrets and variables** → **Actions**
3. **Add the following secrets**:

### **Email Configuration Secrets:**
- `SMTP_SERVER`: `smtp.gmail.com`
- `SMTP_PORT`: `587`
- `EMAIL_USER`: `your-email@gmail.com`
- `EMAIL_PASSWORD`: `your-app-password`
- `SUBSCRIBER_EMAILS`: `email1@gmail.com,email2@gmail.com`

### **How to Add Secrets:**
1. Click **"New repository secret"**
2. **Name**: Enter the secret name (e.g., `SMTP_SERVER`)
3. **Value**: Enter the secret value
4. Click **"Add secret"**

## ⚙️ **Step 3: Test the Workflow**

1. **Go to Actions tab** in your repository
2. **Click on "Daily AI Podcast Digest"** workflow
3. **Click "Run workflow"** → **"Run workflow"**
4. **Monitor the run** to ensure everything works

## 📅 **Step 4: Verify Schedule**

The workflow is configured to run:
- **Daily at 6:00 AM Eastern** (11:00 AM UTC)
- **Automatically** every day
- **Manually** via "Run workflow" button

## 🔍 **Step 5: Monitor and Debug**

### **Check Workflow Runs:**
- Go to **Actions** tab
- Click on **"Daily AI Podcast Digest"**
- View recent runs and their status

### **View Logs:**
- Click on any workflow run
- Click on **"process-podcasts"** job
- Expand steps to see detailed logs

### **Download Artifacts:**
- After a run completes, you can download logs
- Click **"processing-logs"** to download log files

## 🛠️ **Troubleshooting**

### **Common Issues:**

1. **Email not sending:**
   - Check SMTP credentials in secrets
   - Verify app password is correct
   - Check logs for SMTP errors

2. **Models not loading:**
   - First run will be slow (downloading models)
   - Subsequent runs use cached models
   - Check Ollama installation logs

3. **Database errors:**
   - Database is recreated each run (stateless)
   - Episodes are fetched fresh each time
   - No persistent storage between runs

### **Performance Notes:**
- **First run**: ~30-45 minutes (model downloads)
- **Subsequent runs**: ~15-25 minutes
- **GitHub Actions**: Free for 2,000 minutes/month
- **Daily usage**: ~25 minutes = 750 minutes/month ✅

## 🎯 **Success Indicators**

✅ **Workflow runs successfully**
✅ **Email digest received**
✅ **Logs show no errors**
✅ **Models cached properly**

## 📧 **Email Digest**

You should receive an email digest containing:
- **New episodes** from RSS feeds
- **Transcriptions** of audio content
- **AI-generated summaries** with key points
- **Links** to original episodes

---

**Your AI Podcast Agent is now fully automated! 🚀** 