#!/usr/bin/env python3
"""Gerador de hashtags em alta para YouTube, sem YouTube Data API Key.. SIM... isso foi vibecodado @-@

A busca usa o mecanismo público de pesquisa do YouTube por meio do yt-dlp.
Instalação: python -m pip install -U yt-dlp
Exemplo: python gerador_hashtags_youtube.py "receita de bolo de chocolate" -n 20 -t 15
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass
from datetime import date, datetime, timedelta
from typing import Any

try:
    import yt_dlp
except ImportError:
    print(
        "Dependência ausente. Instale com: python -m pip install -U yt-dlp",
        file=sys.stderr,
    )
    raise SystemExit(2)


STOPWORDS = {
    "a", "ao", "aos", "as", "à", "às", "com", "como", "da", "das", "de",
    "do", "dos", "e", "em", "entre", "essa", "esse", "esta", "este", "eu",
    "foi", "foram", "há", "isso", "isto", "já", "mais", "mas", "me", "mesmo",
    "na", "nas", "no", "nos", "não", "o", "os", "ou", "para", "por", "que",
    "qual", "quando", "se", "sem", "ser", "sobre", "sua", "suas", "seu", "seus",
    "tem", "tendo", "um", "uma", "umas", "uns", "você", "e", "video", "vídeo",
    "videos", "vídeos", "oficial", "official", "ft", "feat", "parte", "part",
}

@dataclass
class Video:
    title: str
    url: str
    channel: str
    views: int
    duration: int | None
    upload_date: str | None
    hashtags: list[str]
    hashtags_explicitas: list[str]
    tags_internas: list[str]


def limpar_texto(texto: str) -> str:
    texto = unicodedata.normalize("NFKD", texto)
    texto = "".join(c for c in texto if not unicodedata.combining(c))
    return texto.lower()


def tokens_relevantes(texto: str) -> list[str]:
    normalizado = limpar_texto(texto)
    palavras = re.findall(r"[a-z0-9][a-z0-9_'-]*", normalizado)
    return [
        p.strip("_'-") for p in palavras
        if len(p.strip("_'-")) >= 3
        and p not in STOPWORDS
    ]


def hashtag(token: str) -> str:
    # Mantém palavras compostas em uma única hashtag: #dicasdeestudo.
    token = re.sub(r"[^a-zA-Z0-9_]", "", limpar_texto(token))
    # Corrige a forma truncada que aparecia quando a tag interna era tratada
    # como se já tivesse o caractere #.
    token = {
        "erkdrill": "jerkdrill",
        "erkdrilltypebeat": "jerkdrilltypebeat",
    }.get(token, token)
    return f"#{token}" if token else ""


def extrair_hashtags(texto: str) -> list[str]:
    """Extrai hashtags visíveis de título/descrição e normaliza sua grafia."""
    encontradas = re.findall(r"#[\wÀ-ÿ]+", texto or "", flags=re.UNICODE)
    resultado = []
    for item in encontradas:
        normalizada = hashtag(item[1:])
        if normalizada and normalizada not in resultado:
            resultado.append(normalizada)
    return resultado


def pesquisar(titulo: str, quantidade: int, dias: int = 365) -> list[Video]:
    opcoes = {
        "quiet": True,
        "skip_download": True,
        # False permite obter descrição, tags e hashtags do vídeo, além do título.
        "extract_flat": False,
        "noplaylist": True,
        "ignoreerrors": True,
        "no_warnings": True,
    }
    # Busca mais itens quando há filtro de data, pois parte dos resultados
    # retornados pelo YouTube pode ficar fora do período escolhido.
    quantidade_busca = quantidade if dias == 0 else max(quantidade * 3, quantidade)
    consulta = f"ytsearch{quantidade_busca}:{titulo}"
    try:
        with yt_dlp.YoutubeDL(opcoes) as ydl:
            dados: dict[str, Any] = ydl.extract_info(consulta, download=False) or {}
    except Exception as erro:
        raise RuntimeError(f"Não foi possível consultar o YouTube: {erro}") from erro

    videos: list[Video] = []
    for item in dados.get("entries") or []:
        if not item:
            continue
        url = item.get("webpage_url") or item.get("url") or ""
        if not url and item.get("id"):
            url = f"https://www.youtube.com/watch?v={item['id']}"
        hashtags_explicitas = extrair_hashtags(item.get("title") or "")
        hashtags_explicitas += [
            h for h in extrair_hashtags(item.get("description") or "")
            if h not in hashtags_explicitas
        ]
        tags_internas = [
            hashtag(str(h)) for h in (item.get("tags") or [])
            if hashtag(str(h)) and hashtag(str(h)) not in hashtags_explicitas
        ]
        hashtags = hashtags_explicitas + [h for h in tags_internas if h not in hashtags_explicitas]
        videos.append(Video(
            title=item.get("title") or "",
            url=url,
            channel=item.get("channel") or item.get("uploader") or "",
            views=int(item.get("view_count") or 0),
            duration=item.get("duration"),
            upload_date=item.get("upload_date"),
            hashtags=hashtags,
            hashtags_explicitas=hashtags_explicitas,
            tags_internas=tags_internas,
        ))
    if dias > 0:
        limite = date.today() - timedelta(days=dias)
        recentes: list[Video] = []
        for video in videos:
            if not video.upload_date:
                continue
            try:
                publicada = datetime.strptime(video.upload_date, "%Y%m%d").date()
            except ValueError:
                continue
            if publicada >= limite:
                recentes.append(video)
        videos = recentes

    return sorted(videos, key=lambda v: v.views, reverse=True)[:quantidade]


def gerar_hashtags(titulo: str, videos: list[Video], limite: int) -> list[tuple[str, float, int]]:
    # O filtro usa somente o corpus coletado: consulta, títulos e hashtags dos
    # próprios resultados. Não há banco offline de termos genéricos.
    contexto = set(tokens_relevantes(titulo))
    contexto.update(
        termo for video in videos for termo in tokens_relevantes(video.title)
    )
    contexto = {termo for termo in contexto if len(termo) >= 4}

    def tem_evidencia(tag: str) -> bool:
        termo = tag[1:]
        compacto = re.sub(r"[^a-z0-9]", "", limpar_texto(titulo))
        if termo in compacto:
            return True
        # Aceita hashtags compostas quando seus componentes aparecem nos
        # títulos/consulta; rejeita tags copiadas sobre um assunto ausente.
        return any(palavra in termo for palavra in contexto)

    frequencia = Counter()
    pontuacao = defaultdict(float)
    for posicao, video in enumerate(videos):
        peso = (video.views + 1) ** 0.5 / (posicao + 1) ** 0.35
        # Prioridade máxima: hashtags publicadas pelos próprios criadores.
        for tag in set(video.hashtags_explicitas):
            termo = tag[1:]
            if len(termo) < 3 or termo in STOPWORDS or not tem_evidencia(tag):
                continue
            frequencia[termo] += 1
            pontuacao[termo] += peso * 2.20

        # Prioridade secundária: tags internas, ainda sujeitas ao contexto.
        for tag in set(video.tags_internas):
            termo = tag[1:]
            if len(termo) < 3 or termo in STOPWORDS or not tem_evidencia(tag):
                continue
            frequencia[termo] += 1
            pontuacao[termo] += peso * 1.40

    ordenados = sorted(
        pontuacao,
        key=lambda t: (pontuacao[t], frequencia[t], len(t)),
        reverse=True,
    )
    return [(hashtag(t), pontuacao[t], frequencia[t]) for t in ordenados[:limite] if hashtag(t)]


def formatar_views(valor: int) -> str:
    if valor >= 1_000_000_000:
        return f"{valor / 1_000_000_000:.1f} bi"
    if valor >= 1_000_000:
        return f"{valor / 1_000_000:.1f} mi"
    if valor >= 1_000:
        return f"{valor / 1_000:.1f} mil"
    return str(valor)


def main() -> int:
    parser = argparse.ArgumentParser(description="Gera hashtags para YouTube a partir de vídeos mais vistos.")
    parser.add_argument("titulo", help="Título ou tema do vídeo")
    parser.add_argument("-n", "--resultados", type=int, default=20, help="Quantidade de vídeos pesquisados (padrão: 20)")
    parser.add_argument("-t", "--hashtags", type=int, default=15, help="Quantidade máxima de hashtags (padrão: 15)")
    parser.add_argument(
        "--dias", type=int, default=365,
        help="Considera vídeos publicados nos últimos N dias; use 0 para todo o histórico (padrão: 365)",
    )
    parser.add_argument("--json", dest="arquivo_json", help="Salva resultados e hashtags em um arquivo JSON")
    parser.add_argument(
        "--md", dest="arquivo_md",
        help="Salva somente as hashtags, em uma única linha de arquivo Markdown",
    )
    args = parser.parse_args()

    if args.resultados < 1 or args.hashtags < 1 or args.dias < 0:
        parser.error("--resultados e --hashtags devem ser maiores que zero; --dias não pode ser negativo")

    try:
        videos = pesquisar(args.titulo, args.resultados, args.dias)
    except RuntimeError as erro:
        print(f"Erro: {erro}", file=sys.stderr)
        return 1
    if not videos:
        print("Nenhum vídeo encontrado. Tente um título mais específico.", file=sys.stderr)
        return 1

    resultado = gerar_hashtags(args.titulo, videos, args.hashtags)
    print("\nHashtags sugeridas:\n")
    print(" ".join(tag for tag, _, _ in resultado))
    quantidade_hashtags = sum(len(video.hashtags) for video in videos)
    periodo = "todo o histórico" if args.dias == 0 else f"últimos {args.dias} dias"
    print(
        f"\nBase: {len(videos)} vídeos públicos dos {periodo}, {quantidade_hashtags} "
        "hashtags encontradas em títulos, descrições e tags, ordenados por visualizações.\n"
    )
    print("Vídeos considerados:")
    for i, video in enumerate(videos, 1):
        print(f"{i:2}. {formatar_views(video.views):>9} | {video.title} — {video.channel}")

    if args.arquivo_json:
        payload = {
            "consulta": args.titulo,
            "filtro_dias": args.dias,
            "hashtags": [
                {"hashtag": tag, "pontuacao": round(score, 4), "frequencia": freq}
                for tag, score, freq in resultado
            ],
            "videos": [asdict(video) for video in videos],
        }
        with open(args.arquivo_json, "w", encoding="utf-8") as arquivo:
            json.dump(payload, arquivo, ensure_ascii=False, indent=2)
        print(f"\nJSON salvo em: {args.arquivo_json}")

    if args.arquivo_md:
        # Mantém as hashtags literais para copiar e colar diretamente.
        with open(args.arquivo_md, "w", encoding="utf-8") as arquivo:
            arquivo.write(" ".join(tag for tag, _, _ in resultado) + "\n")
        print(f"\nMarkdown salvo em: {args.arquivo_md}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
