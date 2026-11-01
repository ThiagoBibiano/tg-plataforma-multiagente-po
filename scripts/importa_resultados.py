#!/usr/bin/env python3
"""Importa as tabelas de um lote do experimento para o texto do TG.

Fluxo de mão única, código → texto (plano do artefato, seção 8): o lote é
gerado por ``po-multiagente experimento`` (ou ``avaliar``) no repositório do
código, e este script copia só as tabelas agregadas (``tabelas/*.tex``) para
``resultados/tabelas/``, grava ``resultados/manifesto.json`` com o hash de
cada arquivo e registra em ``artefato.lock`` a versão do código usada.

Recusa a cópia se o código não estiver numa tag limpa: um resultado do texto
precisa apontar para uma versão que qualquer um consiga reproduzir. Com
``--rascunho``, copia mesmo assim para ``resultados/rascunho/``, sem tocar o
``artefato.lock``, para testar a diagramação antes da versão final.

Nada além das tabelas é copiado. As execuções, os dossiês e ``avaliacao.md``
citam as instâncias do conjunto-teste, que é privado até a defesa.

Uso:
    python3 scripts/importa_resultados.py ../po-multiagente/saidas/experimento/<lote>
    python3 scripts/importa_resultados.py <lote> --doi 10.5281/zenodo.NNNN
    python3 scripts/importa_resultados.py <lote> --rascunho
"""

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
CODIGO = RAIZ.parent / "po-multiagente"


class Recusa(Exception):
    """Motivo pelo qual o lote não pode ser importado."""


def git(repositorio: Path, *argumentos: str) -> str:
    resultado = subprocess.run(
        ["git", "-C", str(repositorio), *argumentos],
        capture_output=True,
        text=True,
        check=False,
    )
    if resultado.returncode != 0:
        raise Recusa(f"git {' '.join(argumentos)}: {resultado.stderr.strip()}")
    return resultado.stdout.strip()


def versao_do_codigo(codigo: Path) -> dict[str, str]:
    """Tag e commit do código; recusa árvore suja ou commit sem tag."""
    if git(codigo, "status", "--porcelain"):
        raise Recusa(f"{codigo} tem alterações não commitadas")
    commit = git(codigo, "rev-parse", "HEAD")
    try:
        tag = git(codigo, "describe", "--tags", "--exact-match", "HEAD")
    except Recusa as erro:
        raise Recusa(f"o commit {commit[:7]} de {codigo} não tem tag") from erro
    return {"tag": tag, "commit": commit}


def ler_lote(lote: Path) -> tuple[dict[str, object], list[Path]]:
    manifesto = lote / "manifesto.json"
    tabelas = sorted((lote / "tabelas").glob("*.tex"))
    if not manifesto.is_file():
        raise Recusa(f"{lote} não tem manifesto.json")
    if not tabelas:
        raise Recusa(f"{lote} não tem tabelas/*.tex; rode po-multiagente avaliar antes")
    return json.loads(manifesto.read_text(encoding="utf-8")), tabelas


def sha256(caminho: Path) -> str:
    return hashlib.sha256(caminho.read_bytes()).hexdigest()


def importar(
    lote: Path, codigo: Path, destino: Path, *, doi: str | None, rascunho: bool
) -> Path:
    """Copia as tabelas e grava o manifesto; devolve a pasta de destino."""
    manifesto_lote, tabelas = ler_lote(lote)
    if rascunho:
        versao = {"tag": "", "commit": git(codigo, "rev-parse", "HEAD")}
    else:
        versao = versao_do_codigo(codigo)
        esperada = f"v{manifesto_lote.get('versao_pacote')}"
        if versao["tag"] != esperada:
            raise Recusa(
                f"o lote foi gerado com {esperada}, mas o código está em {versao['tag']}"
            )
    pasta = destino / "rascunho" if rascunho else destino
    (pasta / "tabelas").mkdir(parents=True, exist_ok=True)
    copiados = {}
    for tabela in tabelas:
        alvo = pasta / "tabelas" / tabela.name
        shutil.copyfile(tabela, alvo)
        copiados[f"tabelas/{tabela.name}"] = sha256(alvo)
    registro = {
        "importado_em": datetime.now(UTC).isoformat(),
        "lote": lote.name,
        "rascunho": rascunho,
        "codigo": versao,
        "versao_pacote": manifesto_lote.get("versao_pacote"),
        "modo_llm": manifesto_lote.get("modo_llm"),
        "perfis": sorted(dict(manifesto_lote.get("perfis") or {})),
        "instrucoes_sha256": manifesto_lote.get("instrucoes_sha256"),
        "arquivos": copiados,
    }
    (pasta / "manifesto.json").write_text(
        json.dumps(registro, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    if not rascunho:
        lock = {**versao, "doi": doi, "lote": lote.name}
        (destino.parent / "artefato.lock").write_text(
            json.dumps(lock, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
    return pasta


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("lote", type=Path, help="pasta do lote, com tabelas/ e manifesto.json")
    parser.add_argument("--codigo", type=Path, default=CODIGO, help="repositório po-multiagente")
    parser.add_argument("--destino", type=Path, default=RAIZ / "resultados")
    parser.add_argument("--doi", help="DOI da versão do código no Zenodo")
    parser.add_argument(
        "--rascunho", action="store_true", help="aceita código sem tag; copia para rascunho/"
    )
    argumentos = parser.parse_args(argv)
    try:
        pasta = importar(
            argumentos.lote,
            argumentos.codigo,
            argumentos.destino,
            doi=argumentos.doi,
            rascunho=argumentos.rascunho,
        )
    except Recusa as erro:
        print(f"Recusado: {erro}", file=sys.stderr)
        return 1
    print(f"Tabelas importadas em {pasta.relative_to(RAIZ) if pasta.is_relative_to(RAIZ) else pasta}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
