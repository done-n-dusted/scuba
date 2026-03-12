import time
import urllib.request
import urllib.error
import json
import sys
import datetime

def get_status():
    try:
        req = urllib.request.Request("http://127.0.0.1:8000/rpc/health", method="GET")
        with urllib.request.urlopen(req, timeout=0.5) as response:
            if response.status == 200:
                data = json.loads(response.read().decode())
                return data
            return {"status": "error", "message": f"HTTP {response.status}"}
    except urllib.error.URLError as e:
        return {"status": "offline", "message": str(e.reason)}
    except Exception as e:
        return {"status": "offline", "message": str(e)}

def main():
    while True:
        status_data = get_status()
        
        # Clear screen and move cursor to top-left
        sys.stdout.write("\033[2J\033[H")
        
        # Determine colors
        if status_data.get("status") == "ok":
            color = "\033[92m" # Green
            status_text = "ONLINE / OK"
        else:
            color = "\033[91m" # Red
            status_text = f"OFFLINE ({status_data.get('message', 'Unknown Error')})"
            
        reset = "\033[0m"
        bold = "\033[1m"
        
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        
        output = (
            f"{bold}=== SCUBA SYSTEM STATUS ==={reset}\n"
            f"Time:        {now}\n"
            f"RefreshRate: 100ms\n"
            f"---------------------------\n"
            f"Backend API: {color}{bold}{status_text}{reset}\n"
        )
        sys.stdout.write(output)
        sys.stdout.flush()
        
        time.sleep(0.1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.stdout.write("\033[2J\033[HExited status monitor.\n")
