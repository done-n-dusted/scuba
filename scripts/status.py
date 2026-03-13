import time
import urllib.request
import urllib.error
import json
import sys
import datetime

def get_status():
    try:
        req = urllib.request.Request("http://127.0.0.1:8000/rpc/health", method="GET")
        with urllib.request.urlopen(req, timeout=1.0) as response:
            if response.status == 200:
                data = json.loads(response.read().decode())
                return data
            return {"status": "error", "message": f"HTTP {response.status}"}
    except urllib.error.URLError as e:
        return {"status": "offline", "message": str(e.reason)}
    except Exception as e:
        return {"status": "offline", "message": str(e)}

def main():
    base_interval = 2.0
    max_interval = 30.0
    current_interval = base_interval
    last_check_time = 0
    
    while True:
        now_ts = time.time()
        
        # Check if it's time to poll
        if now_ts - last_check_time >= current_interval:
            status_data = get_status()
            last_check_time = now_ts
            
            if status_data.get("status") == "ok":
                current_interval = base_interval
            else:
                current_interval = min(current_interval * 2, max_interval)
        
        # UI Update (more frequent than polling for the countdown)
        sys.stdout.write("\033[2J\033[H")
        
        if status_data.get("status") == "ok":
            color = "\033[92m" # Green
            status_text = f"ONLINE / OK (Uptime: {status_data.get('uptime_seconds', '?')}s)"
        else:
            color = "\033[91m" # Red
            status_text = f"OFFLINE ({status_data.get('message', 'Unknown Error')})"
            
        reset = "\033[0m"
        bold = "\033[1m"
        
        now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        time_until_next = max(0, current_interval - (time.time() - last_check_time))
        
        output = (
            f"{bold}=== SCUBA SYSTEM STATUS ==={reset}\n"
            f"Time:        {now_str}\n"
            f"PollRate:    {current_interval:.1f}s\n"
            f"Next poll:   {time_until_next:.1f}s\n"
            f"---------------------------\n"
            f"Backend API: {color}{bold}{status_text}{reset}\n"
        )
        sys.stdout.write(output)
        sys.stdout.flush()
        
        time.sleep(0.1) # UI refresh rate

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.stdout.write("\nExited status monitor.\n")
