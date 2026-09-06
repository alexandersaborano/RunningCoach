"""Cria uma cópia privada dos dados locais do atleta."""

from datetime import datetime
from pathlib import Path
import shutil


BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
BACKUP_DIR = BASE_DIR / "backups"


def main() -> None:
    if not DATA_DIR.is_dir():
        raise SystemExit("A pasta data/ não existe; não há dados para copiar.")

    destino = BACKUP_DIR / datetime.now().strftime("data_%Y%m%d_%H%M%S")
    shutil.copytree(DATA_DIR, destino)
    print(f"Backup criado em: {destino}")


if __name__ == "__main__":
    main()
