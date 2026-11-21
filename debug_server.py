import subprocess
import time
import urllib.request
import os

app_dir = r"."

cmd = ["python", "-m", "streamlit", "run", "app.py", "--server.port", "8599", "--server.headless", "true"]
print("Launching Streamlit...")
proc = subprocess.Popen(cmd, cwd=app_dir, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

try:
    for attempt in range(12):
        time.sleep(1)
        # Check if process died early
        ret = proc.poll()
        if ret is not None:
            out, err = proc.communicate()
            print("Process died with code:", ret)
            print("STDOUT:", out)
            print("STDERR:", err)
            break
        try:
            req = urllib.request.Request("http://localhost:8599")
            with urllib.request.urlopen(req, timeout=2) as resp:
                print("Connected! Response Code:", resp.getcode())
                break
        except Exception:
            pass
    else:
        print("Timed out waiting for connection.")
        out, err = proc.communicate(timeout=2)
        print("STDOUT:", out)
        print("STDERR:", err)
finally:
    proc.terminate()
    try:
        proc.wait(timeout=3)
    except Exception:
        proc.kill()
    print("Cleaned up.")
