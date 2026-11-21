import subprocess
import time
import urllib.request
import os
import signal

app_dir = r"."

cmd = ["python", "-m", "streamlit", "run", "app.py", "--server.port", "8599", "--server.headless", "true"]
print("Launching Streamlit...")
proc = subprocess.Popen(cmd, cwd=app_dir, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

try:
    time.sleep(6)
    url = "http://localhost:8599"
    print(f"Pinging {url}...")
    req = urllib.request.Request(url)
    with urllib.request.urlopen(req, timeout=5) as resp:
        print("Response Code:", resp.getcode())
        content = resp.read().decode("utf-8")
        print("Page Title in HTML:", "<title>" in content)
        print("Streamlit successfully started!")
finally:
    proc.terminate()
    try:
        proc.wait(timeout=3)
    except subprocess.TimeoutExpired:
        proc.kill()
    print("Streamlit process stopped.")
