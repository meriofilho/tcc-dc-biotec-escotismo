"""Figura 1e: mapa do Brasil com a instituição de origem de cada trabalho do acervo acadêmico da UEB.

Uso: python -I scripts/figuras_mapa.py   (a partir da raiz do projeto)
Lê dados/trabalhos_ueb/trabalhos_ueb.csv e dados/geo/brasil_uf.json (malha de UFs do IBGE,
https://servicodados.ibge.gov.br/api/v3/malhas/paises/BR?formato=application/vnd.geo+json&qualidade=minima&intrarregiao=UF)
"""
import json
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.lines import Line2D
from matplotlib.patches import Polygon, Rectangle

import estilo

estilo.aplicar()
OUT = "figuras"
df = pd.read_csv("dados/trabalhos_ueb/trabalhos_ueb.csv", encoding="utf-8-sig")
df["area"] = df.area_ueb
# trabalho no exterior aparece como "Paraguai" na contagem por estado
df["uf"] = df.uf.where(df.pais == "Brasil", df.pais)
geo = json.load(open("dados/geo/brasil_uf.json", encoding="utf-8"))

COD_UF = {"11": "RO", "12": "AC", "13": "AM", "14": "RR", "15": "PA", "16": "AP", "17": "TO", "21": "MA",
          "22": "PI", "23": "CE", "24": "RN", "25": "PB", "26": "PE", "27": "AL", "28": "SE", "29": "BA",
          "31": "MG", "32": "ES", "33": "RJ", "35": "SP", "41": "PR", "42": "SC", "43": "RS", "50": "MS",
          "51": "MT", "52": "GO", "53": "DF"}
n_uf = df[df.uf != "Paraguai"].uf.value_counts()
cmap = plt.get_cmap("Greys")


def cor_uf(uf):
    n = n_uf.get(uf, 0)
    return "#F4F4F4" if n == 0 else cmap(0.12 + 0.33 * min(n, 14) / 14)


def desenhar_ufs(ax, lw=0.5):
    for f in geo["features"]:
        uf = COD_UF[str(f["properties"]["codarea"])]
        g = f["geometry"]
        polys = g["coordinates"] if g["type"] == "MultiPolygon" else [g["coordinates"]]
        for poly in polys:
            ax.add_patch(Polygon(poly[0], closed=True, facecolor=cor_uf(uf), edgecolor="#9A9A9A", linewidth=lw))


def posicoes(dfc, raio):
    """Espalha os trabalhos de uma mesma cidade num pequeno círculo em volta dela."""
    pts = []
    for (cid, lat, lon), g in dfc.groupby(["cidade", "lat", "lon"]):
        k = len(g)
        for i, (_, r) in enumerate(g.sort_values("area").iterrows()):
            if k == 1:
                dx = dy = 0
            else:
                ang = 2 * math.pi * i / k
                rr = raio * (1 + 0.35 * (k > 6))
                dx, dy = rr * math.cos(ang), rr * math.sin(ang)
            pts.append((lon + dx, lat + dy, r.area, r.local_estimado))
    return pts


def pontos(ax, raio, tam):
    for x, y, area, est in posicoes(df, raio):
        cor = estilo.AREA_COR[area]
        ax.scatter(x, y, s=tam, facecolor="white" if est else cor, edgecolor=cor, linewidth=1.4, zorder=5)


fig = plt.figure(figsize=(16, 9.2))
ax = fig.add_axes([0.0, 0.04, 0.44, 0.84])
desenhar_ufs(ax)
pontos(ax, 0.55, 46)
ax.set_xlim(-74.5, -33.5)
ax.set_ylim(-34.5, 6)
ax.set_aspect("equal")
ax.axis("off")
# rótulos das cidades fora do Sul/Sudeste e do exterior
for cid, (dx, dy, ha) in {"Natal": (-1.0, 0, "right"), "Aracaju": (-1.6, 0, "right"), "Valença": (-1.0, 0, "right"),
                          "Goiânia": (-1.0, 0, "right"), "Brasília": (1.0, 0.4, "left"),
                          "Assunção": (-1.0, 0, "right")}.items():
    r = df[df.cidade == cid].iloc[0]
    n = (df.cidade == cid).sum()
    rot = f"{cid} ({r.uf})" + (f": {n}" if n > 1 else "")
    ax.annotate(rot, (r.lon, r.lat), xytext=(r.lon + dx, r.lat + dy), fontsize=8.5, ha=ha, va="center",
                color="#333")
# caixa do zoom
zx0, zx1, zy0, zy1 = -55.0, -39.5, -33.8, -18.5
ax.add_patch(Rectangle((zx0, zy0), zx1 - zx0, zy1 - zy0, fill=False, edgecolor="#555", linewidth=0.9, ls="--"))

# zoom no Sul e Sudeste
az = fig.add_axes([0.455, 0.06, 0.33, 0.64])
desenhar_ufs(az, lw=0.7)
pontos(az, 0.32, 40)
az.set_xlim(zx0, zx1)
az.set_ylim(zy0, zy1)
az.set_aspect("equal")
az.set_xticks([])
az.set_yticks([])
for s in az.spines.values():
    s.set_edgecolor("#555")
    s.set_linestyle("--")
az.set_title("Sul e Sudeste (ampliado)", fontsize=10, loc="left")
ROT_Z = {"São Paulo": (0.9, -0.9), "Porto Alegre": (0.9, -0.6), "Belo Horizonte": (0.8, 0.5),
         "Campinas": (-0.8, 0.6), "Curitiba": (0.8, 0.35), "Rio de Janeiro": (0.7, -0.6), "Vitória": (0.7, 0.2),
         "Caxias do Sul": (0.7, 0.55), "Santa Maria": (-0.6, 0.6), "Blumenau": (0.7, 0.2),
         "Rio Grande": (0.6, -0.2)}
for cid, (dx, dy) in ROT_Z.items():
    r = df[df.cidade == cid].iloc[0]
    n = (df.cidade == cid).sum()
    az.annotate(f"{cid}" + (f": {n}" if n > 1 else ""), (r.lon, r.lat), xytext=(r.lon + dx, r.lat + dy),
                fontsize=8, ha="left" if dx > 0 else "right", va="center", color="#222",
                bbox=dict(boxstyle="round,pad=0.15", fc="white", ec="none", alpha=0.75), zorder=6)

# barras por UF, empilhadas por área
ab = fig.add_axes([0.845, 0.12, 0.14, 0.70])
uf_area = pd.crosstab(df.uf, df.area).reindex(columns=list(estilo.AREA_COR), fill_value=0)
uf_area = uf_area.loc[uf_area.sum(axis=1).sort_values().index]
left = np.zeros(len(uf_area))
y = np.arange(len(uf_area))
for a in uf_area.columns:
    ab.barh(y, uf_area[a], left=left, color=estilo.AREA_COR[a], height=0.7)
    left += uf_area[a].values
for yi, v in zip(y, uf_area.sum(axis=1)):
    ab.text(v + 0.2, yi, str(v), va="center", fontsize=8.5)
ab.set_yticks(y)
ab.set_yticklabels(["Paraguai (exterior)" if u == "Paraguai" else u for u in uf_area.index], fontsize=9)
ab.set_xlim(0, uf_area.sum(axis=1).max() + 2)
ab.set_xlabel("Nº de trabalhos", fontsize=9)
ab.spines["left"].set_visible(False)
ab.tick_params(axis="y", length=0)
reg = df.regiao.value_counts()
ab.set_title("Por estado", fontsize=10, loc="left")
txt_reg = "  ".join(f"{k}: {reg.get(k, 0)}" for k in ["Sul", "Sudeste", "Nordeste", "Centro-Oeste", "Norte", "Exterior"])

h = [Line2D([], [], marker="o", ls="", markersize=8, markerfacecolor=c, markeredgecolor=c, label=a)
     for a, c in estilo.AREA_COR.items()]
h.append(Line2D([], [], marker="o", ls="", markersize=8, markerfacecolor="white", markeredgecolor="#555",
                label="Instituição não informada (cidade do estudo ou do autor)"))
fig.legend(handles=h, loc="upper left", bbox_to_anchor=(0.02, 0.905), frameon=False, fontsize=9, ncol=1)
fig.text(0.02, 0.965, f"Onde foram produzidos os {len(df)} trabalhos acadêmicos do acervo da UEB",
         fontsize=14, fontweight="bold")
fig.text(0.02, 0.935, "Um ponto por trabalho, na cidade da instituição. Estados mais escuros têm mais trabalhos. "
         f"Por região: {txt_reg}.", fontsize=9.5, color="#333")
fig.text(0.02, 0.01, "Fonte: capas dos trabalhos em escoteiros.org.br/downloads (Trabalhos Acadêmicos), acesso em "
         "29/10/2026; malha dos estados: IBGE. Cor = área atribuída pelo site da UEB.", fontsize=8, color="#555")
estilo.salvar(fig, os.path.join(OUT, "1e_acervo_mapa_instituicoes"))
plt.close(fig)

# tabela de instituições para o texto
inst = df.groupby(["sigla", "instituicao", "cidade", "uf"]).size().rename("trabalhos").reset_index()
inst.sort_values(["trabalhos", "uf"], ascending=[False, True]).to_csv(
    "dados/trabalhos_ueb/resumo_instituicoes.csv", index=False, encoding="utf-8-sig")
print("ok")
print(reg.to_dict())
print(n_uf.to_dict())
