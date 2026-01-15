from pathlib import Path

Path("data/bronze").mkdir(parents=True, exist_ok=True)
Path("data/silver").mkdir(parents=True, exist_ok=True)
Path("data/gold").mkdir(parents=True, exist_ok=True)