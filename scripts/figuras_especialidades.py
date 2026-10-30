"""Parte 2: figuras das especialidades escoteiras e da taxonomia de Bloom.

Uso: python -I scripts/figuras_especialidades.py   (a partir da raiz do projeto)
Lê dados/especialidades/requisitos_bloom.csv e especialidades.json
Grava em figuras/ e dados/especialidades/resumo_*.csv
"""
import sys as _sys
_sys.stdout.reconfigure(encoding="utf-8")
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.patches import Patch

import estilo

estilo.aplicar()
BASE = "dados/especialidades"
OUT = "figuras"
FONTE = "Fonte: escoteiros.org.br/especialidades, acesso em 30/10/2026."

esps = pd.DataFrame(json.load(open(f"{BASE}/especialidades.json", encoding="utf-8")))
esps["n_req"] = esps.requisitos.apply(len)
req = pd.read_csv(f"{BASE}/requisitos_bloom.csv", encoding="utf-8-sig")
NIV = estilo.BLOOM_NIVEIS
PROG_ORD = ["Anterior", "Atualizado (Lobinho e Escoteiro)", "Atualizado (Sênior e Pioneiro)"]
PROG_COR = {"Anterior": "#7A8B99", "Atualizado (Lobinho e Escoteiro)": "#2E86AB",
            "Atualizado (Sênior e Pioneiro)": "#1B4965"}

# ---------- 2a. Quantitativo geral ----------
cont = esps.groupby(["programa", "area"]).size().reset_index(name="n")
cont["prog_i"] = cont.programa.map(PROG_ORD.index)
cont = cont.sort_values(["prog_i", "n"], ascending=[True, False])
fig, ax = plt.subplots(figsize=(9, 6.5))
y = np.arange(len(cont))
ax.barh(y, cont.n, color=[PROG_COR[p] for p in cont.programa])
ax.set_yticks(y)
ax.set_yticklabels(cont.area)
for yi, v in zip(y, cont.n):
    ax.text(v + 1, yi, str(v), va="center", fontsize=9)
ax.invert_yaxis()
tot = esps.groupby("programa").size()
ax.legend(handles=[Patch(color=PROG_COR[p], label=f"{p}: {tot.get(p, 0)}") for p in PROG_ORD],
          frameon=False, loc="lower right", title="Programa educativo")
ax.set_xlabel("Nº de especialidades")
ax.set_title(f"Especialidades escoteiras da UEB por programa e área (total = {len(esps)})", loc="left")
ax.spines["left"].set_visible(False)
ax.tick_params(axis="y", length=0)
fig.text(0.01, -0.02, FONTE + " O programa atualizado está em implantação; muitas especialidades "
         "aparecem nos dois programas.", fontsize=8, color="#555")
estilo.salvar(fig, os.path.join(OUT, "2a_especialidades_quantitativo"))
plt.close(fig)
cont.drop(columns="prog_i").to_csv(f"{BASE}/resumo_por_area.csv", index=False)

# ---------- Biotecnologia por especialidade ----------
bio = req[req.tema_biotec.notna() & (req.tema_biotec != "")]
por_esp = bio.groupby(["slug", "programa"]).tema_biotec.agg(
    lambda s: "biotecnologia (direta)" if (s == "biotecnologia (direta)").any()
    else "microbiologia e saneamento (relacionada)").rename("biotec")
n_bio = bio.groupby(["slug", "programa"]).size().rename("n_bio")
esps = esps.merge(por_esp, on=["slug", "programa"], how="left").merge(n_bio, on=["slug", "programa"], how="left")
esps["biotec"] = esps.biotec.fillna("sem relação")
esps["n_bio"] = esps.n_bio.fillna(0).astype(int)
BIO_COR = {"biotecnologia (direta)": "#C0392B", "microbiologia e saneamento (relacionada)": "#F0A04B",
           "sem relação": "#C9CED6"}

# ---------- 2b. Ciência e Tecnologia: quais tocam biotecnologia ----------
ct = esps[(esps.programa == "Anterior") & (esps.area == "Ciência e Tecnologia")].copy()
ct = ct.sort_values(["n_bio", "nome"], ascending=[False, True])
fig, ax = plt.subplots(figsize=(9, 12))
y = np.arange(len(ct))
ax.barh(y, ct.n_req, color="#E6E9EE", label="Total de requisitos")
ax.barh(y, ct.n_bio, color=[BIO_COR[b] for b in ct.biotec])
ax.set_yticks(y)
ax.set_yticklabels(ct.nome, fontsize=9)
ax.invert_yaxis()
for yi, (nb, nr) in enumerate(zip(ct.n_bio, ct.n_req)):
    ax.text(nr + 0.2, yi, f"{nb}/{nr}" if nb else str(nr), va="center", fontsize=8, color="#333")
nd = int((ct.biotec == "biotecnologia (direta)").sum())
nr_ = int((ct.biotec == "microbiologia e saneamento (relacionada)").sum())
ax.legend(handles=[
    Patch(color=BIO_COR["biotecnologia (direta)"], label=f"Requisitos sobre biotecnologia (direta): {nd} especialidades"),
    Patch(color=BIO_COR["microbiologia e saneamento (relacionada)"],
          label=f"Requisitos sobre microbiologia/saneamento: {nr_} especialidades"),
    Patch(color="#E6E9EE", label="Demais requisitos")], frameon=False, loc="lower left",
    bbox_to_anchor=(0, 1.0), fontsize=9)
ax.set_xlabel("Nº de requisitos")
ax.set_ylim(len(ct) - 0.5, -0.5)
ax.set_title(f"Ciência e Tecnologia ({len(ct)} especialidades): quantos requisitos tocam em biotecnologia",
             loc="left", pad=62)
ax.spines["left"].set_visible(False)
ax.tick_params(axis="y", length=0)
fig.text(0.01, -0.01, FONTE + " Busca por palavras-chave nos requisitos (DNA, genética, vacina, fermentação, "
         "enzima, microrganismo, bactéria, compostagem, saneamento etc.).", fontsize=8, color="#555")
estilo.salvar(fig, os.path.join(OUT, "2b_ciencia_tecnologia_biotecnologia"))
plt.close(fig)
esps.drop(columns=["requisitos", "texto_bloco"], errors="ignore").to_csv(
    f"{BASE}/resumo_especialidades.csv", index=False, encoding="utf-8-sig")


# ---------- Barras empilhadas 100% no estilo do manual da UEB ----------
def barras_bloom(dados, grupo, titulo, arquivo, largura=None, ordem=None, rotulo_min=0.07):
    d = dados[dados.nivel_bloom.isin(NIV)]
    tab = pd.crosstab(d[grupo], d.nivel_bloom).reindex(columns=NIV, fill_value=0)
    pct = tab.div(tab.sum(axis=1), axis=0)
    if ordem is None:
        # ordena do mais "alto" para o mais "baixo" na taxonomia (média ponderada dos níveis)
        score = (pct * np.arange(len(NIV))).sum(axis=1)
        ordem = score.sort_values(ascending=False).index
    pct = pct.loc[ordem]
    n = len(pct)
    fig, ax = plt.subplots(figsize=(largura or max(8, 0.42 * n + 2.5), 6.8))
    base = np.zeros(n)
    x = np.arange(n)
    for nv in NIV:
        v = pct[nv].values
        ax.bar(x, v, bottom=base, color=estilo.BLOOM_COR[nv], width=0.72, label=nv, edgecolor="white", linewidth=0.3)
        for xi, (b, h) in enumerate(zip(base, v)):
            if h >= rotulo_min:
                ax.text(xi, b + h / 2, f"{h:.0%}", ha="center", va="center", fontsize=7 if n > 20 else 9,
                        color="#333" if nv in ("Participar", "Analisar", "Lembrar") else "white")
        base += v
    ax.set_xticks(x)
    ax.set_xticklabels([f"{i} ({tab.loc[i].sum()})" for i in pct.index], rotation=90, fontsize=8 if n > 20 else 10)
    ax.set_ylim(0, 1)
    ax.set_yticks([0, 1 / 3, 2 / 3, 1])
    ax.set_yticklabels(["0%", "33%", "67%", "100%"])
    ax.yaxis.grid(True, color="#ccc", linewidth=0.6)
    ax.set_axisbelow(True)
    h, l = ax.get_legend_handles_labels()
    ax.legend(h[::-1], l[::-1], frameon=False, bbox_to_anchor=(1.01, 0.5), loc="center left")
    ax.set_xlim(-0.6, n - 0.4)
    ax.set_title(titulo, loc="left", pad=22)
    ax.text(0, 1.015, FONTE + " Entre parênteses: nº de requisitos. Classificação automática pelo verbo inicial "
            "(preliminar; tende a subestimar Avaliar e Criar).", transform=ax.transAxes, fontsize=8, color="#555")
    estilo.salvar(fig, os.path.join(OUT, arquivo))
    plt.close(fig)
    return pct


def barras_bloom_h(dados, grupo, titulo, arquivo, destaque=(), rotulo_min=0.08):
    """Mesma figura, na horizontal: uma linha por item, níveis da esquerda (Participar) para a direita (Criar)."""
    d = dados[dados.nivel_bloom.isin(NIV)]
    tab = pd.crosstab(d[grupo], d.nivel_bloom).reindex(columns=NIV, fill_value=0)
    pct = tab.div(tab.sum(axis=1), axis=0)
    score = (pct * np.arange(len(NIV))).sum(axis=1)
    pct = pct.loc[score.sort_values(ascending=False).index]
    n = len(pct)
    fig, ax = plt.subplots(figsize=(9.5, 0.3 * n + 2.2))
    y = np.arange(n)
    base = np.zeros(n)
    for nv in NIV:
        v = pct[nv].values
        ax.barh(y, v, left=base, color=estilo.BLOOM_COR[nv], height=0.78, label=nv, edgecolor="white", linewidth=0.4)
        for yi, (b, w) in enumerate(zip(base, v)):
            if w >= rotulo_min:
                ax.text(b + w / 2, yi, f"{w:.0%}", ha="center", va="center", fontsize=7,
                        color="#333" if nv in ("Participar", "Analisar", "Lembrar") else "white")
        base += v
    ax.set_yticks(y)
    ax.set_yticklabels([f"{i} ({tab.loc[i].sum()})" for i in pct.index], fontsize=8.5)
    for lab in ax.get_yticklabels():
        if lab.get_text().rsplit(" (", 1)[0] in destaque:
            lab.set_fontweight("bold")
            lab.set_color("#C0392B")
    ax.set_ylim(n - 0.5, -0.5)
    ax.set_xlim(0, 1)
    ax.set_xticks([0, 1 / 3, 2 / 3, 1])
    ax.set_xticklabels(["0%", "33%", "67%", "100%"])
    ax.xaxis.grid(True, color="#ccc", linewidth=0.6)
    ax.set_axisbelow(True)
    ax.spines["left"].set_visible(False)
    ax.tick_params(axis="y", length=0)
    ax.legend(ncol=len(NIV), frameon=False, loc="lower left", bbox_to_anchor=(0, 1.0), fontsize=8.5,
              handlelength=1.2, columnspacing=1.0)
    ax.set_title(titulo, loc="left", pad=40)
    nota = ("Ordenado do nível médio mais alto para o mais baixo. Entre parênteses: nº de requisitos."
            + (" Em vermelho: especialidades com requisitos ligados a biotecnologia." if destaque else "")
            + "\n" + FONTE + " Classificação automática pelo verbo inicial (preliminar; tende a subestimar "
            "Avaliar e Criar).")
    ax.annotate(nota, xy=(0, 0), xycoords="axes fraction", xytext=(0, -28), textcoords="offset points",
                fontsize=7.5, color="#555", va="top", ha="left")
    estilo.salvar(fig, os.path.join(OUT, arquivo))
    plt.close(fig)
    return pct


# 2c. As dez mais conquistadas, como no manual (para comparar a classificação automática com a do manual)
DEZ = ["Primeiros Socorros", "Rastreamento", "Culinária", "Acampamento", "Técnicas de Sapa", "Pioneiria",
       "Babá", "Confeitaria", "Natação", "Prevenção ao Uso de Drogas"]
ant = req[req.programa == "Anterior"]
dez = ant[ant.especialidade.isin(DEZ)]
if dez.especialidade.nunique() >= 8:
    barras_bloom(dez, "especialidade", "As dez especialidades mais conquistadas (UEB, até 2019): "
                 "classificação automática", "2c_bloom_dez_mais_conquistadas",
                 ordem=[d for d in DEZ if d in set(dez.especialidade)], largura=10)

# 2d. Ciência e Tecnologia
ctr = ant[ant.area == "Ciência e Tecnologia"]
bio_ct = set(ct.loc[ct.biotec != "sem relação", "nome"])
barras_bloom_h(ctr, "especialidade", "Níveis de Bloom nas especialidades de Ciência e Tecnologia",
               "2d_bloom_ciencia_tecnologia", destaque=bio_ct)

# 2f. Ciência e Tecnologia: distribuição dos níveis e verbos mais pedidos (como em Vick e Garvey, 2008)
cls = ctr[ctr.nivel_bloom.isin(NIV)]
niv_n = cls.nivel_bloom.value_counts().reindex(NIV, fill_value=0)
# Cada verbo conta uma vez por requisito; "construir+apresentar" conta para os dois
vb = ctr.assign(v=ctr.verbo.str.split("+")).explode("v")
vb = vb[vb.nivel_bloom.isin(NIV)]
simples = vb[~vb.verbo.str.contains(r"\+", regex=True)]
nivel_do_verbo = simples.groupby("v").nivel_bloom.agg(lambda s: s.mode().iloc[0])
nivel_do_verbo = nivel_do_verbo.reindex(vb.v.unique()).fillna(vb.groupby("v").nivel_bloom.agg(lambda s: s.mode().iloc[0]))
freq_v = vb.v.value_counts()
tab_v = pd.DataFrame({"verbo": freq_v.index, "requisitos": freq_v.values,
                      "nivel_bloom": nivel_do_verbo.reindex(freq_v.index).values})
tab_v["pct_requisitos"] = (tab_v.requisitos / len(cls)).round(4)
tab_v.to_csv(f"{BASE}/verbos_ciencia_tecnologia.csv", index=False, encoding="utf-8-sig")
ROTULO_V = {"demonstrar conhecimento": "demonstrar conhecimento", "ter": "ter (noções, conhecimento)"}

TOP = 20
top = tab_v.head(TOP)
fig, (a1, a2) = plt.subplots(1, 2, figsize=(13, 7.2), gridspec_kw={"width_ratios": [1, 1.35], "wspace": 0.45})
y1 = np.arange(len(NIV))
a1.barh(y1, niv_n.values, color=[estilo.BLOOM_COR[n] for n in NIV], edgecolor="#999", linewidth=0.4)
for yi, v in zip(y1, niv_n.values):
    p = v / niv_n.sum()
    a1.text(v + 3, yi, f"{v} ({p:.1%})".replace(".", ",") if p < 0.01 else f"{v} ({p:.0%})", va="center", fontsize=9)
a1.set_yticks(y1)
a1.set_yticklabels(NIV)
a1.set_ylim(len(NIV) - 0.5, -0.5)
a1.set_xlim(0, niv_n.max() * 1.3)
a1.set_xlabel("Nº de requisitos")
a1.set_title(f"Níveis de Bloom ({niv_n.sum()} requisitos)", loc="left", fontsize=11)
a1.spines["left"].set_visible(False)
a1.tick_params(axis="y", length=0)

y2 = np.arange(len(top))
a2.barh(y2, top.requisitos, color=[estilo.BLOOM_COR[n] for n in top.nivel_bloom], edgecolor="#999", linewidth=0.4)
for yi, v in zip(y2, top.requisitos):
    a2.text(v + 1, yi, str(v), va="center", fontsize=9)
a2.set_yticks(y2)
a2.set_yticklabels([ROTULO_V.get(v, v) for v in top.verbo])
a2.set_ylim(len(top) - 0.5, -0.5)
a2.set_xlim(0, top.requisitos.max() * 1.15)
a2.set_xlabel("Nº de requisitos que pedem o verbo")
a2.set_title(f"Os {TOP} verbos mais pedidos (de {len(tab_v)} verbos diferentes)", loc="left", fontsize=11)
a2.spines["left"].set_visible(False)
a2.tick_params(axis="y", length=0)
a2.legend(handles=[Patch(color=estilo.BLOOM_COR[n], label=n) for n in NIV], frameon=False, title="Nível do verbo",
          loc="lower right", fontsize=9)
fig.suptitle("Ciência e Tecnologia: o que as especialidades pedem que os jovens façam", x=0.02, ha="left",
             fontweight="bold", fontsize=13)
fig.text(0.02, -0.02, FONTE + f" {len(ctr) - len(cls)} requisitos sem verbo reconhecido ficaram de fora. "
         "Cada verbo conta uma vez por requisito (\"construir e apresentar\" conta para os dois). "
         "Classificação automática, preliminar.", fontsize=8, color="#555")
estilo.salvar(fig, os.path.join(OUT, "2f_ciencia_tecnologia_niveis_e_verbos"))
plt.close(fig)
print(tab_v.head(10).to_string())

# 2e. Visão geral: todas as áreas dos três programas
req["grupo"] = req.area + " · " + req.programa.str.replace("Atualizado ", "Atual. ").str.replace(
    "(Lobinho e Escoteiro)", "(L/E)").str.replace("(Sênior e Pioneiro)", "(S/P)")
barras_bloom(req, "grupo", "Níveis de Bloom nos requisitos, por área e programa (todas as especialidades)",
             "2e_bloom_por_area", rotulo_min=0.05)

# Tabela de resumo
d = req[req.nivel_bloom.isin(NIV)]
pd.crosstab([d.programa, d.area], d.nivel_bloom).reindex(columns=NIV, fill_value=0).to_csv(
    f"{BASE}/resumo_bloom_por_area.csv", encoding="utf-8-sig")
print("ok")
print(ct[["nome", "n_req", "n_bio", "biotec"]].head(12).to_string())
