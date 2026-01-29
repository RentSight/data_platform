# scripts/run_all.py
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
DEFAULT_COMPOSE_FILE = ROOT / "docker" / "docker-compose.yml"


def run(cmd: list[str], cwd: Path = ROOT) -> None:
    print("\n" + "=" * 80)
    print(">>>", " ".join(cmd))
    print("=" * 80)
    subprocess.check_call(cmd, cwd=str(cwd))


def main() -> int:
    parser = argparse.ArgumentParser(description="Roda a pipeline completa do RentSight Data Platform.")
    parser.add_argument("--skip-download", action="store_true")
    parser.add_argument("--skip-pipeline", action="store_true")
    parser.add_argument("--skip-docker", action="store_true")
    parser.add_argument("--skip-publish", action="store_true")
    parser.add_argument("--compose-file", default=str(DEFAULT_COMPOSE_FILE))

    args = parser.parse_args()

    download_py = SCRIPTS / "download_data.py"
    pipeline_py = SCRIPTS / "run_pipeline.py"
    publish_py = SCRIPTS / "publish_to_db.py"
    compose_file = Path(args.compose_file)

    print(f"[run_all] Raiz do projeto: {ROOT}")

    # 1) Download
    if not args.skip_download:
        run([sys.executable, str(download_py)])

    # 2) Pipeline (Bronze/Silver/Gold)
    if not args.skip_pipeline:
        run([sys.executable, str(pipeline_py)])

    # 3) Docker up (Postgres)
    if not args.skip_docker:
        run(["docker", "compose", "-f", str(compose_file), "up", "-d"])

    # 4) Publish Gold -> DB
    if not args.skip_publish:
        run([sys.executable, str(publish_py)])

    print("\n✅ Tudo pronto: dados processados e banco alimentado para o backend consumir.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
