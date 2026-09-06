"""Verifica que o entrypoint Streamlit responde sem testar APIs externas."""

import subprocess
import sys
import time
from urllib.request import urlopen


PORT = "8515"


def main() -> None:
    process = subprocess.Popen(
        [
            sys.executable,
            "-m",
            "streamlit",
            "run",
            "ui/app.py",
            "--server.headless",
            "true",
            "--server.port",
            PORT,
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    try:
        for _ in range(20):
            try:
                with urlopen(f"http://127.0.0.1:{PORT}/_stcore/health", timeout=1) as response:
                    if response.status == 200:
                        print("Streamlit smoke test: OK")
                        return
            except OSError:
                time.sleep(0.5)
        raise SystemExit("Streamlit smoke test: a aplicação não respondeu.")
    finally:
        process.terminate()
        process.wait(timeout=5)


if __name__ == "__main__":
    main()
