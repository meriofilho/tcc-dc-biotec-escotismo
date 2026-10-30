"""Extrai texto dos PDFs do acervo da UEB e sugere o ano de publicação.

Uso: python -I scripts/extrair_trabalhos.py dados/trabalhos_ueb
Gera, dentro da pasta: texto/NN.txt e candidatos_ano.tsv
"""
import os
import re
import sys
import urllib.parse
from collections import Counter

import pypdf

base = sys.argv[1]
os.makedirs(os.path.join(base, "texto"), exist_ok=True)
rows = [l.rstrip("\n").split("\t") for l in open(os.path.join(base, "index.tsv"), encoding="utf-8")]

out = []
for f, area, url, _ in rows:
    titulo = urllib.parse.unquote(url.rsplit("/", 1)[-1])[:-4].replace("-", " ").replace("_", " ")
    try:
        r = pypdf.PdfReader(os.path.join(base, "pdf", f))
        paginas = [(p.extract_text() or "") for p in r.pages]
    except Exception as e:  # PDF quebrado ou protegido
        paginas = []
        print(f, "erro:", e, file=sys.stderr)
    texto = "\n".join(paginas)
    open(os.path.join(base, "texto", f[:-4] + ".txt"), "w", encoding="utf-8").write(texto)
    # Ano: anos que aparecem nas 3 primeiras páginas (capa e folha de rosto)
    capa = "\n".join(paginas[:3])
    anos = Counter(int(a) for a in re.findall(r"\b(19[5-9]\d|20[0-2]\d)\b", capa))
    meta = ""
    try:
        d = r.metadata or {}
        meta = str(d.get("/CreationDate", ""))[2:6]
    except Exception:
        pass
    out.append((f, area, len(paginas), len(texto), meta, " ".join(f"{a}:{n}" for a, n in anos.most_common(4)), titulo))

with open(os.path.join(base, "candidatos_ano.tsv"), "w", encoding="utf-8") as fh:
    fh.write("arquivo\tarea\tpaginas\tchars\tano_meta_pdf\tanos_capa\ttitulo\n")
    for o in out:
        fh.write("\t".join(map(str, o)) + "\n")
print("ok", len(out))
