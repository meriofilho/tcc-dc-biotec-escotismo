"""Figura 1f: painel-resumo do acervo acadêmico da UEB (46 trabalhos).

a) anos de publicação  b) tipo de trabalho  c) nível  d) grande área do curso  e) local de origem

Uso: python -I scripts/figuras_painel.py   (a partir da raiz do projeto)
Lê dados/trabalhos_ueb/trabalhos_ueb.csv e dados/geo/brasil_uf.json (malha de UFs do IBGE)
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.gridspec import GridSpec
from matplotlib.patches import Patch, Polygon

import estilo

estilo.aplicar()
df = pd.read_csv("dados/trabalhos_ueb/trabalhos_ueb.csv", encoding="utf-8-sig")
geo = json.load(open("dados/geo/brasil_uf.json", encoding="utf-8"))
N = len(df)
COR = "#3B6FB6"
COR_EST = "#A9C1E3"
CINZA = "#B8BDC4"
SEM_INFO = ("Não informado", "Não informada")


def letra(ax, txt, titulo):
    ax.set_title(titulo, loc="left", fontsize=11.5, pad=8)
    ax.text(-0.02, 1.06, txt, transform=ax.transAxes, fontsize=15, fontweight="bold", ha="right", va="bottom")


def barras(ax, cont, ordem=None):
    if ordem is None:
        # maior no topo; "Não informado(a)" sempre por último
        cont = cont.sort_values(ascending=False)
        cont = pd.concat([cont[~cont.index.isin(SEM_INFO)], cont[cont.index.isin(SEM_INFO)]])[::-1]
    else:
        cont = cont.reindex([o for o in ordem if o in cont.index])[::-1]
    y = np.arange(len(cont))
    cores = [CINZA if i in SEM_INFO else COR for i in cont.index]
    ax.barh(y, cont.values, color=cores, height=0.7)
    for yi, v in zip(y, cont.values):
        ax.text(v + 0.3, yi, f"{v} ({v / N:.0%})", va="center", fontsize=9)
    ax.set_yticks(y)
    ax.set_yticklabels(cont.index, fontsize=9.5)
    ax.set_xlim(0, cont.max() * 1.35)
    ax.spines["left"].set_visible(False)
    ax.tick_params(axis="y", length=0)
    ax.set_xlabel("Nº de trabalhos", fontsize=9)
    ax.xaxis.get_major_locator().set_params(integer=True)


fig = plt.figure(figsize=(18, 10.5))
gs = GridSpec(2, 3, figure=fig, width_ratios=[1, 1, 1.75], hspace=0.38, wspace=0.5,
              left=0.065, right=0.995, top=0.87, bottom=0.07)

# a) anos
ax = fig.add_subplot(gs[0, 0])
anos = range(df.ano.min(), df.ano.max() + 1)
conf = df[df.ano_estimado == 0].ano.value_counts().reindex(anos, fill_value=0)
est = df[df.ano_estimado == 1].ano.value_counts().reindex(anos, fill_value=0)
ax.bar(list(anos), conf.values, color=COR, width=0.8, label="Ano na capa")
ax.bar(list(anos), est.values, bottom=conf.values, color=COR_EST, width=0.8, label="Ano estimado")
ax.set_xticks([a for a in anos if a % 4 == 2])
ax.yaxis.get_major_locator().set_params(integer=True)
ax.set_ylabel("Nº de trabalhos", fontsize=9)
ax.legend(frameon=False, fontsize=8.5, loc="upper left")
med = int(df.ano.median())
letra(ax, "a", f"Ano de publicação ({df.ano.min()}–{df.ano.max()}; mediana {med})")

# b) tipo de trabalho
ax = fig.add_subplot(gs[0, 1])
barras(ax, df.tipo_trabalho.value_counts())
letra(ax, "b", "Tipo de trabalho")

# c) nível
ax = fig.add_subplot(gs[1, 0])
barras(ax, df.nivel.value_counts(),
       ordem=["Técnico", "Graduação", "Especialização", "Mestrado", "Docente/pesquisador", "Não informado"])
letra(ax, "c", "Nível de formação")

# d) grande área do curso
ax = fig.add_subplot(gs[1, 1])
barras(ax, df.grande_area_curso.value_counts())
letra(ax, "d", "Grande área do curso (CNPq)")

# e) mapa
ax = fig.add_subplot(gs[:, 2])
COD_UF = {"11": "RO", "12": "AC", "13": "AM", "14": "RR", "15": "PA", "16": "AP", "17": "TO", "21": "MA",
          "22": "PI", "23": "CE", "24": "RN", "25": "PB", "26": "PE", "27": "AL", "28": "SE", "29": "BA",
          "31": "MG", "32": "ES", "33": "RJ", "35": "SP", "41": "PR", "42": "SC", "43": "RS", "50": "MS",
          "51": "MT", "52": "GO", "53": "DF"}
n_uf = df[df.pais == "Brasil"].uf.value_counts()
cmap = plt.get_cmap("Greys")
for f in geo["features"]:
    uf = COD_UF[str(f["properties"]["codarea"])]
    n = n_uf.get(uf, 0)
    cor = "#F4F4F4" if n == 0 else cmap(0.12 + 0.33 * min(n, 12) / 12)
    g = f["geometry"]
    for poly in (g["coordinates"] if g["type"] == "MultiPolygon" else [g["coordinates"]]):
        ax.add_patch(Polygon(poly[0], closed=True, facecolor=cor, edgecolor="#9A9A9A", linewidth=0.5))
cid = df.groupby(["cidade", "lat", "lon"]).size().rename("n").reset_index().sort_values("n", ascending=False)
ax.scatter(cid.lon, cid.lat, s=cid.n * 70, color=COR, alpha=0.75, edgecolor="white", linewidth=0.8, zorder=5)
for _, r in cid[cid.n >= 3].iterrows():
    ax.annotate(f"{r.cidade} ({r.n})", (r.lon, r.lat), xytext=(8, 6), textcoords="offset points", fontsize=8.5,
                bbox=dict(boxstyle="round,pad=0.15", fc="white", ec="none", alpha=0.8), zorder=6)
r = cid[cid.cidade == "Assunção"].iloc[0]
ax.annotate("Assunção (Paraguai)", (r.lon, r.lat), xytext=(-8, 0), textcoords="offset points", fontsize=8.5,
            ha="right", va="center")
ax.set_xlim(-74.5, -33.5)
ax.set_ylim(-34.5, 6)
ax.set_aspect("equal")
ax.axis("off")
reg = df.regiao.value_counts()
for k, v in zip([1, 3, 6], ["1 trabalho", "3 trabalhos", "6 trabalhos"]):
    ax.scatter([], [], s=k * 70, color=COR, alpha=0.75, edgecolor="white", label=v)
ax.legend(frameon=False, fontsize=8.5, loc="lower left", labelspacing=1.4, borderpad=1, title="Por cidade",
          title_fontsize=9)
letra(ax, "e", "Local de origem (cidade da instituição)")
ax.text(0.0, 1.0, "  ".join(f"{k}: {reg.get(k, 0)}" for k in ["Sudeste", "Sul", "Nordeste", "Centro-Oeste", "Norte", "Exterior"]),
        transform=ax.transAxes, fontsize=9, color="#333", va="top")

fig.suptitle(f"Acervo de trabalhos acadêmicos da UEB: visão geral dos {N} trabalhos", x=0.02, ha="left",
             fontsize=15, fontweight="bold")
fig.text(0.02, 0.925, "Fonte: escoteiros.org.br/downloads (Trabalhos Acadêmicos), acesso em 29/10/2026. Metadados lidos "
         "nas capas dos PDFs; grande área segundo a tabela do CNPq; malha dos estados: IBGE. "
         "Cinza: sem informação no PDF.", fontsize=8.5, color="#555")
estilo.salvar(fig, "figuras/1f_acervo_painel_resumo")
plt.close(fig)
print("ok", reg.to_dict())
