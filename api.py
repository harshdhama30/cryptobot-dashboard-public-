# api.py
from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI()

@app.get("/", response_class=HTMLResponse)
def dashboard_proxy():
    return """
    <html>
      <head>
        <title>My Crypto Bot Dashboard</title>
        <style>
          body { margin: 0; font-family: sans-serif; }
          header { background: #20232A; color: #61DAFB; padding: 1rem; text-align: center; }
        </style>
      </head>
      <body>
        <header>🔒 Proxy Dashboard (port 8000)</header>
        <!-- note the ?embed=true to hide Streamlit’s top bar & sidebar -->
        <iframe 
          src="http://localhost:8501/?embed=true" 
          width="100%" height="calc(100vh - 4rem)" 
          style="border:none;">
        </iframe>
      </body>
    </html>
    """
