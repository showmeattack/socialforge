"""Start all target and simulator services."""
import subprocess
import sys
from pathlib import Path

targets = [
    {"name": "Golden Mirage (Company Site)", "path": "megacorp/app.py", "port": 9001},
    {"name": "Phone Simulator", "path": "phone/app.py", "port": 9007},
    {"name": "Social Media (LinkHub)", "path": "social/app.py", "port": 9003},
    {"name": "Email Client (SF Mail)", "path": "email_client/app.py", "port": 9004},
    {"name": "Dark Hub (Data Marketplace)", "path": "darknet/app.py", "port": 9005},
    {"name": "Phishing Builder", "path": "phisher/app.py", "port": 9006},
    {"name": "Company Sites (Dynamic)", "path": "companies/app.py", "port": 9008},
]

processes = []

if __name__ == "__main__":
    base = Path(__file__).parent
    for t in targets:
        app_path = base / t["path"]
        print(f"[*] Starting {t['name']} on port {t['port']}...")
        p = subprocess.Popen(
            [sys.executable, "-m", "uvicorn", f"{app_path.stem}:app",
             "--host", "127.0.0.1", "--port", str(t["port"])],
            cwd=str(app_path.parent),
        )
        processes.append(p)

    print(f"\n[+] {len(processes)} service(s) running:")
    for t in targets:
        print(f"    http://127.0.0.1:{t['port']}  — {t['name']}")
    print("\nPress Ctrl+C to stop.\n")

    try:
        for p in processes:
            p.wait()
    except KeyboardInterrupt:
        print("\n[!] Shutting down...")
        for p in processes:
            p.terminate()
