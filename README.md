# YouTube Downloader

A simple Flask-based YouTube downloader built using yt-dlp.

## 🚀 Features

- Fetch and list all available formats (Video/Audio)
- Download in high or low quality
- Convert to MP3
- Ready for deployment (Render, Replit, Railway)

## 📁 Project Structure

```
youtube_downloader/
├── app.py
├── index.html
├── requirements.txt
├── Procfile
├── downloads/
```

## 🛠 How to Run Locally

```bash
pip install -r requirements.txt
python app.py
```

Visit: `http://localhost:5000`

## 🌐 Deploy to Render

1. Push repo to GitHub
2. Go to https://render.com > New > Web Service
3. Connect repo → Build command: `pip install -r requirements.txt`
4. Start command: `python app.py`
