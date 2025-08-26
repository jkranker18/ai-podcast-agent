# 🚀 Quick Start Guide - AI Podcast Agent

## ⚡ Get Running in 5 Minutes

### 1. **Install Dependencies**
```bash
pip install -r requirements.txt
```

### 2. **Test the Setup**
```bash
python test_setup.py
```

### 3. **Run the Agent**
```bash
python -m src.main
```

That's it! 🎉

---

## 📊 What You'll See

After running, check your results:

### **Check System Status**
```bash
python -m src.utils.status
```

### **View Recent Episodes**
```bash
python -m src.utils.status
```

### **Monitor Logs**
```bash
tail -f logs/podcast_agent.log
```

---

## 🎯 What's Happening

1. **RSS Feeds Checked**: 5 AI podcasts automatically scanned
2. **New Episodes Found**: Recent episodes discovered and stored
3. **Audio Downloads**: Episodes downloaded to `data/audio/`
4. **Database Updated**: Processing status tracked in SQLite

---

## 🔧 Configuration (Optional)

Copy `env.example` to `.env` for custom settings:
```bash
cp env.example .env
# Edit .env with your preferences
```

---

## 📁 Generated Files

```
data/
├── db.sqlite          # Database with episodes
├── audio/             # Downloaded podcast files
└── logs/
    └── podcast_agent.log
```

---

## 🎉 Success!

You now have:
- ✅ **5 AI Podcasts** automatically monitored
- ✅ **Episode Discovery** working
- ✅ **Audio Downloads** functional
- ✅ **Status Monitoring** available

**Next**: Add AI processing (transcription & summarization) in Phase 3! 