# Gerador de Hashtags para YouTube

Script em Python que pesquisa vídeos públicos do YouTube e sugere hashtags relacionadas ao tema informado.

A ferramenta utiliza o `yt-dlp`, não exige uma YouTube API Key e analisa:

- vídeos relacionados ao título pesquisado;
- quantidade de visualizações;
- data de publicação;
- hashtags presentes nos títulos e descrições;
- tags internas dos vídeos;
- relevância das tags em relação ao tema pesquisado.

## Requisitos

- Python 3.9 ou superior
- Internet kkj

## Instalação

Clone o projeto ou baixe os arquivos:

```bash
git clone https://github.com/SEU-USUARIO/SEU-REPOSITORIO.git
cd SEU-REPOSITORIO
```

Crie e ative um ambiente virtual:

### Linux ou macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### Windows PowerShell

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

Instale a dependência:

```bash
python -m pip install --upgrade pip
python -m pip install -U yt-dlp
```

## Uso básico

```bash
python gerador_hashtags_youtube.py "jerk drill type beat"
```

O programa pesquisa vídeos recentes, calcula as hashtags mais relevantes e mostra os vídeos considerados.

## Salvar as hashtags em Markdown

Para salvar somente as hashtags em um arquivo `.md`:

```bash
python gerador_hashtags_youtube.py \
  "jerk drill type beat" \
  --md hashtags.md
```

O arquivo conterá uma linha semelhante a:

```text
#jerkdrill #nydrill #hoodtraptypebeat
```

## Salvar os dados completos em JSON

```bash
python gerador_hashtags_youtube.py \
  "jerk drill type beat" \
  --json resultado.json
```

O JSON contém as hashtags sugeridas, pontuação, frequência e dados dos vídeos analisados.

## Opções principais

| Opção | Descrição | Padrão |
|---|---|---:|
| `--resultados` ou `-n` | Quantidade de vídeos pesquisados | `20` |
| `--hashtags` ou `-t` | Quantidade máxima de hashtags | `15` |
| `--dias` | Considera vídeos publicados nos últimos N dias | `365` |
| `--md` | Arquivo Markdown com somente as hashtags | — |
| `--json` | Arquivo JSON com os dados completos | — |

## Exemplos

Pesquisar vídeos dos últimos 30 dias e gerar 10 hashtags:

```bash
python gerador_hashtags_youtube.py "marketing digital para iniciantes" --dias 30 --resultados 60 --hashtags 42 --md hashtags.md
```

Pesquisar usando todo o histórico do YouTube:

```bash
python gerador_hashtags_youtube.py \
  "receita de bolo de chocolate" \
  --dias 0 \
  --md hashtags.md
```

Gerar Markdown e JSON ao mesmo tempo:

```bash
python gerador_hashtags_youtube.py \
  "treino para ganhar massa muscular" \
  --md hashtags.md \
  --json resultado.json
```

## Observações

- O script usa a busca pública do YouTube por meio do `yt-dlp`.
- Não é necessário informar uma API Key.
- As hashtags são sugestões baseadas nos vídeos encontrados; elas não garantem aumento de visualizações.
- O YouTube pode alterar seu sistema de busca ou limitar consultas automatizadas.
- Se a pesquisa não retornar resultados recentes, tente aumentar o valor de `--dias` ou usar `--dias 0`.
