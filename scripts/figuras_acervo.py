"""Parte 1: figuras do acervo de trabalhos acadêmicos da UEB.

Uso: python -I scripts/figuras_acervo.py   (a partir da raiz do projeto)
Lê dados/trabalhos_ueb/metadados.csv e dados/trabalhos_ueb/texto/*.txt
Grava em figuras/.
"""
import sys as _sys
_sys.stdout.reconfigure(encoding="utf-8")
import os
import re
import sys
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import matplotlib.pyplot as plt
import pandas as pd
from wordcloud import WordCloud

import estilo

estilo.aplicar()
BASE = "dados/trabalhos_ueb"
OUT = "figuras"
os.makedirs(OUT, exist_ok=True)

df = pd.read_csv(os.path.join(BASE, "metadados.csv"))
AREAS = list(estilo.AREA_COR)

# ---------- 1a. Linha do tempo ----------
anos = range(df.ano.min(), df.ano.max() + 1)
tab = df.pivot_table(index="ano", columns="area", values="arquivo", aggfunc="count").reindex(anos).fillna(0)
tab = tab.reindex(columns=[a for a in AREAS if a in tab.columns])
fig, ax = plt.subplots(figsize=(11, 4.2))
base = pd.Series(0, index=tab.index, dtype=float)
for a in tab.columns:
    ax.bar(tab.index, tab[a], bottom=base, color=estilo.AREA_COR[a], label=a, width=0.75)
    base += tab[a]
ax.set_xticks(list(anos))
ax.set_xticklabels(list(anos), rotation=90)
ax.set_ylabel("Nº de trabalhos")
ax.yaxis.get_major_locator().set_params(integer=True)
ax.set_title(f"Trabalhos acadêmicos no acervo da UEB por ano de publicação (n = {len(df)})", loc="left")
ax.set_ylim(0, tab.sum(axis=1).max() + 1.5)
ax.legend(frameon=False, ncol=4, loc="upper left")
n_est = int(df.ano_estimado.sum())
fig.text(0.01, -0.04, f"Fonte: escoteiros.org.br/downloads (Trabalhos Acadêmicos), acesso em 29/10/2026. "
         f"{n_est} trabalhos sem data na capa: ano estimado pela referência mais recente citada.",
         fontsize=8, color="#555")
estilo.salvar(fig, os.path.join(OUT, "1a_acervo_linha_do_tempo"))
plt.close(fig)

# ---------- 1b. Barras por área ----------
cont = df.area.value_counts().reindex(AREAS).fillna(0).astype(int).sort_values()
fig, ax = plt.subplots(figsize=(7, 3.2))
bars = ax.barh(cont.index, cont.values, color=[estilo.AREA_COR[a] for a in cont.index])
for b, v in zip(bars, cont.values):
    ax.text(v + 0.4, b.get_y() + b.get_height() / 2, f"{v} ({v / len(df):.0%})", va="center")
ax.set_xlabel("Nº de trabalhos")
ax.set_xlim(0, cont.max() * 1.2)
ax.set_title("Trabalhos acadêmicos da UEB por área (classificação do site)", loc="left")
ax.spines["left"].set_visible(False)
ax.tick_params(axis="y", length=0)
estilo.salvar(fig, os.path.join(OUT, "1b_acervo_por_area"))
plt.close(fig)

# ---------- 1c. Nuvens de palavras ----------
STOP = set("""
a à ao aos as às até com como da das de dei do dos e é ela elas ele eles em entre era essa essas esse esses esta
está estas este estes eu foi for foram há isso isto já lhe lhes mais mas me mesmo meu minha muito na não nas nem
no nos nós num numa o os ou para pela pelas pelo pelos por qual quando que quem se sem ser seu seus si sua suas
também te tem têm ter teu um uma umas uns você vocês sobre após assim ainda onde pois porque cada todo toda todos
todas outro outra outros outras sendo seja sejam será serão pode podem deve devem forma além bem apenas desde
sua tal tais vez vezes então muitas muitos mesma mesmas mesmos sido estar estão foram tinha tinham fazer feito
seus suas nesse nessa neste nesta nesses nessas desse dessa deste desta desses dessas aquele aquela aqueles
dentro durante segundo grande grandes maior menor parte partir através meio tanto outro qualquer quanto
sempre nunca algum alguma alguns algumas nenhum nenhuma ponto modo maneira caso tipo pouco geral diversos
diversas algo cerca acordo conforme apud idem ibid disponível acesso http https www com br org pdf html
página páginas figura tabela quadro gráfico fonte autor autora autores capítulo editora universidade
faculdade curso trabalho conclusão monografia dissertação tese orientador orientadora artigo pesquisa
estudo análise resultados objetivo objetivos introdução considerações finais referências bibliográficas
metodologia revista edição vol ed anos ano dia dias janeiro fevereiro março abril maio junho julho agosto setembro
outubro novembro dezembro rio paulo janeiro sao são porto alegre santa catarina curitiba brasília
escotismo escoteiro escoteiros escoteira escoteiras movimento scout scouts scouting
brasil brasileiro brasileira baden powell dois três quatro gente aqui coisa coisas
""".split())


def tokens(txt):
    # Corta a lista de referências bibliográficas (última ocorrência do título da seção)
    m = list(re.finditer(r"\n\s*REFER[ÊE]NCIAS", txt))
    if m and m[-1].start() > len(txt) * 0.5:
        txt = txt[: m[-1].start()]
    txt = re.sub(r"-\s*\n\s*", "", txt).lower()
    return [t for t in re.findall(r"[a-záéíóúâêôãõçà]{4,}", txt) if t not in STOP]


freq = {a: Counter() for a in AREAS}
for _, r in df.iterrows():
    p = os.path.join(BASE, "texto", r.arquivo.replace(".pdf", ".txt"))
    freq[r.area].update(tokens(open(p, encoding="utf-8").read()))
geral = sum(freq.values(), Counter())

pd.DataFrame(geral.most_common(200), columns=["palavra", "freq"]).to_csv(
    os.path.join(BASE, "frequencia_palavras_geral.csv"), index=False)


def nuvem(cont, cor, w=1600, h=900):
    def cf(*a, **k):
        return cor
    return WordCloud(width=w, height=h, background_color="white", max_words=120, color_func=cf,
                     prefer_horizontal=0.9, random_state=7, collocations=False).generate_from_frequencies(cont)


fig, ax = plt.subplots(figsize=(12, 6.8))
ax.imshow(nuvem(geral, "#1F3A5F"), interpolation="bilinear")
ax.axis("off")
fig.suptitle(f"Palavras mais frequentes nos {len(df)} trabalhos acadêmicos do acervo da UEB",
             x=0.01, ha="left", fontweight="bold")
fig.text(0.01, 0.01, "Texto completo sem referências bibliográficas; removidas palavras vazias e os termos "
         "escotismo/escoteiro(s)/movimento/Brasil/Baden-Powell, presentes em todos os trabalhos.", fontsize=8, color="#555")
estilo.salvar(fig, os.path.join(OUT, "1c_nuvem_geral"))
plt.close(fig)

fig, axs = plt.subplots(2, 2, figsize=(14, 8.4))
for ax, a in zip(axs.flat, AREAS):
    n = int((df.area == a).sum())
    ax.imshow(nuvem(freq[a], estilo.AREA_COR[a], 1200, 700), interpolation="bilinear")
    ax.axis("off")
    ax.set_title(f"{a} (n = {n})", color=estilo.AREA_COR[a])
fig.suptitle("Palavras mais frequentes por área do acervo da UEB", x=0.01, ha="left", fontweight="bold")
fig.tight_layout()
estilo.salvar(fig, os.path.join(OUT, "1d_nuvem_por_area"))
plt.close(fig)

print("ok")
for a in AREAS:
    print(a, [w for w, _ in freq[a].most_common(12)])
