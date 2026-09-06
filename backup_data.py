"""Cria uma cópia privada dos dados locais do atleta."""

from datetime import datetime
import json
from pathlib import Path
import shutil
from typing import Iterable


BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
BACKUP_DIR = BASE_DIR / "backups"
BACKUP_CONFIG = BASE_DIR / ".backup_config.json"


def _backup_root(destino: str | Path | None = None) -> Path:
    raiz = Path(destino).expanduser() if destino else BACKUP_DIR
    return raiz if raiz.is_absolute() else BASE_DIR / raiz


def criar_backup(destino: str | Path | None = None, retencao: int | None = None) -> Path:
    if not DATA_DIR.is_dir():
        raise FileNotFoundError("A pasta data/ não existe; não há dados para copiar.")

    raiz = _backup_root(destino)
    raiz.mkdir(parents=True, exist_ok=True)
    caminho = raiz / datetime.now().strftime("data_%Y%m%d_%H%M%S_%f")
    shutil.copytree(DATA_DIR, caminho)
    if retencao:
        aplicar_retencao(raiz, retencao)
    return caminho


def listar_backups(destino: str | Path | None = None) -> list[Path]:
    raiz = _backup_root(destino)
    return sorted(
        (caminho for caminho in raiz.glob("data_*") if caminho.is_dir()),
        key=lambda caminho: caminho.name,
        reverse=True,
    )


def carregar_configuracao() -> dict:
    if not BACKUP_CONFIG.exists():
        return {"automatico": False, "intervalo_horas": 24, "retencao": 10, "destino": str(BACKUP_DIR)}
    try:
        with BACKUP_CONFIG.open("r", encoding="utf-8") as ficheiro:
            dados = json.load(ficheiro)
        return dados if isinstance(dados, dict) else {}
    except (OSError, json.JSONDecodeError) as error:
        raise ValueError(f"Configuração de backup inválida: {error}") from error


def guardar_configuracao(configuracao: dict) -> None:
    BACKUP_CONFIG.write_text(
        json.dumps(configuracao, indent=4, ensure_ascii=False),
        encoding="utf-8",
    )


def backup_automatico_devido(configuracao: dict) -> bool:
    if not configuracao.get("automatico"):
        return False
    backups = listar_backups(configuracao.get("destino"))
    if not backups:
        return True
    intervalo = max(1, int(configuracao.get("intervalo_horas", 24)))
    idade_horas = (datetime.now().timestamp() - backups[0].stat().st_mtime) / 3600
    return idade_horas >= intervalo


def aplicar_retencao(destino: str | Path, quantidade: int) -> None:
    if quantidade < 1:
        raise ValueError("A retenção deve manter pelo menos um backup.")
    for antigo in listar_backups(destino)[quantidade:]:
        shutil.rmtree(antigo)


def _iter_json(caminho: Path) -> Iterable[Path]:
    return caminho.rglob("*.json") if caminho.is_dir() else ()


def verificar_integridade(caminho: str | Path = DATA_DIR) -> list[str]:
    """Devolve problemas encontrados sem alterar quaisquer ficheiros."""
    raiz = Path(caminho)
    problemas = []
    if not raiz.is_dir():
        return [f"Pasta inexistente: {raiz}"]
    for ficheiro in _iter_json(raiz):
        try:
            with ficheiro.open("r", encoding="utf-8") as stream:
                json.load(stream)
        except (OSError, json.JSONDecodeError) as error:
            problemas.append(f"{ficheiro.relative_to(raiz)}: {error}")
    return problemas


def restaurar_backup(caminho: str | Path, destino: str | Path = DATA_DIR) -> None:
    origem = Path(caminho)
    problemas = verificar_integridade(origem)
    if problemas:
        raise ValueError("Backup inválido: " + "; ".join(problemas))
    if not origem.is_dir():
        raise FileNotFoundError(f"Backup inexistente: {origem}")

    destino_path = Path(destino)
    temporario = destino_path.with_name(f"{destino_path.name}.restore_tmp")
    if temporario.exists():
        shutil.rmtree(temporario)
    shutil.copytree(origem, temporario)
    if destino_path.exists():
        shutil.rmtree(destino_path)
    temporario.replace(destino_path)


def main() -> None:
    destino = criar_backup()
    print(f"Backup criado em: {destino}")


if __name__ == "__main__":
    main()
