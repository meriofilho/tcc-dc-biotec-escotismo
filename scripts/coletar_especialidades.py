"""Baixa nome e requisitos de cada especialidade da UEB.

Uso: python -I scripts/coletar_especialidades.py
Lê  dados/especialidades/lista_categorias.json (categoria -> slugs, tirado do site em 29/10/2026)
Gera dados/especialidades/especialidades.json
"""
import html
import json
import os
import re
import time
import urllib.request

BASE = "dados/especialidades"
URL = "https://www.escoteiros.org.br/especialidades/{}/"

PROGRAMA = {
    "ciencia-e-tecnologia": ("Anterior", "Ciência e Tecnologia"),
    "cultura": ("Anterior", "Cultura"),
    "desportos": ("Anterior", "Desportos"),
    "habilidades-escoteiras": ("Anterior", "Habilidades Escoteiras"),
    "servicos": ("Anterior", "Serviços"),
    "habilidades-para-a-vida": ("Atualizado (Lobinho e Escoteiro)", "Habilidades para a Vida"),
    "meio-ambiente": ("Atualizado (Lobinho e Escoteiro)", "Meio Ambiente"),
    "paz-e-desenvolvimento": ("Atualizado (Lobinho e Escoteiro)", "Paz e Desenvolvimento"),
    "saude-e-bem-estar": ("Atualizado (Lobinho e Escoteiro)", "Saúde e Bem-Estar"),
}
for k in ["habilidades-para-a-vida", "meio-ambiente", "paz-e-desenvolvimento", "saude-e-bem-estar"]:
    PROGRAMA[k + "-programa-educativo-atualizado-ramos-senior-e-pioneiro"] = (
        "Atualizado (Sênior e Pioneiro)", PROGRAMA[k][1])

cats = json.load(open(os.path.join(BASE, "lista_categorias.json"), encoding="utf-8"))
# Espeleoturismo aparece na lista visível de Ciência e Tecnologia, mas não veio na coleta automática
if "espeleoturismo" not in cats["ciencia-e-tecnologia"]:
    cats["ciencia-e-tecnologia"].append("espeleoturismo")

saida_path = os.path.join(BASE, "especialidades.json")
feitos = {}
if os.path.exists(saida_path):
    feitos = {(e["categoria_slug"], e["slug"]): e for e in json.load(open(saida_path, encoding="utf-8"))}


def limpar(s):
    s = re.sub(r"<[^>]+>", " ", s)
    return re.sub(r"\s+", " ", html.unescape(s)).strip()


def baixar(slug):
    req = urllib.request.Request(URL.format(slug), headers={"User-Agent": "Mozilla/5.0 (pesquisa TCC IFRJ)"})
    return urllib.request.urlopen(req, timeout=60).read().decode("utf-8", "replace")


out = []
for cat, slugs in cats.items():
    prog, area = PROGRAMA[cat]
    for slug in slugs:
        if (cat, slug) in feitos and feitos[(cat, slug)]["requisitos"]:
            out.append(feitos[(cat, slug)])
            continue
        try:
            h = baixar(slug)
        except Exception as e:
            print("erro", slug, e)
            out.append({"categoria_slug": cat, "programa": prog, "area": area, "slug": slug,
                        "nome": slug, "requisitos": [], "erro": str(e)})
            continue
        nome = re.search(r'<h1 class="header-title[^"]*">(.*?)</h1>', h, re.S)
        bloco = re.search(r'content__text">(.*?)<div class="col-md-4', h, re.S)
        bloco = bloco.group(1) if bloco else ""
        itens = [limpar(x) for x in re.findall(r"<li[^>]*>(.*?)</li>", bloco, re.S)]
        itens = [i for i in itens if i]
        if not itens:
            # Programa atualizado: requisitos em parágrafos "1. ... 2. ..."
            corpo = re.split(r"Vers[ãa]o\s*:", limpar(bloco))[0]
            partes = re.split(r"(?:^|\s)(\d{1,2})\.\s+", corpo)
            # partes = [antes, "1", texto1, "2", texto2, ...]; só aceita numeração em sequência
            seq = []
            for k in range(1, len(partes) - 1, 2):
                if int(partes[k]) == len(seq) + 1:
                    seq.append(partes[k + 1].strip())
                elif seq:
                    seq[-1] += f" {partes[k]}. {partes[k + 1].strip()}"
            if len(seq) >= 3:
                itens = seq
        versao = re.search(r"Vers[ãa]o</strong>\s*:?\s*([^<]+)", bloco)
        out.append({
            "categoria_slug": cat, "programa": prog, "area": area, "slug": slug,
            "nome": limpar(nome.group(1)) if nome else slug,
            "requisitos": itens,
            "versao": versao.group(1).strip(" :") if versao else "",
            "texto_bloco": limpar(bloco)[:4000] if not itens else "",
        })
        time.sleep(0.3)
    print(cat, len(slugs))

json.dump(out, open(saida_path, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
sem = [e["slug"] for e in out if not e["requisitos"]]
print("total", len(out), "sem requisitos:", len(sem), sem[:30])
