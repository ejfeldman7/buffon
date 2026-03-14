# Buffon's Needle — Streamlit App

An interactive Monte Carlo simulation of Buffon's Needle problem, demonstrating how dropping needles randomly onto a lined floor can estimate the value of π.

## Features

- 🎯 Live π estimate with color-coded accuracy (green → yellow → red)
- 📊 Plotly visualization of needle drops (up to 2,000 displayed)
- 📈 Convergence chart tracking π estimate over time
- 🔢 Adjustable needle count (1–10,000 per drop)
- 📏 Needle/board width ratio slider (0.1× – 2.0×, supports long-needle formula)
- 📐 Formula and explanation tabs

## Local Development

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run the app
streamlit run app.py
```

The app will open at `http://localhost:8501`.

## Deploy to Streamlit Community Cloud (free)

1. Push this folder to a **GitHub repository**
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Click **New app**
4. Select your repo, branch (`main`), and set the **Main file path** to `app.py`
5. Click **Deploy** — it will be live in ~60 seconds

## Deploy to Other Platforms

### Railway / Render / Fly.io
Add a `Procfile` (already included below) and deploy as a normal Python web service:
```
web: streamlit run app.py --server.port=$PORT --server.address=0.0.0.0
```

### Docker
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8501
CMD ["streamlit", "run", "app.py", "--server.address=0.0.0.0"]
```

## File Structure

```
buffons_needle/
├── app.py                  # Main Streamlit application
├── requirements.txt        # Python dependencies
├── README.md               # This file
└── .streamlit/
    └── config.toml         # Theme configuration
```
