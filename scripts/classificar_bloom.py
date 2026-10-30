"""Classifica cada requisito de especialidade num nível da taxonomia de Bloom revisada
(Krathwohl, 2002), mais o nível extra "Participar" proposto no manual da UEB (2023).

Regra: o nível é dado pelo verbo que abre o requisito. Expressões como "Saber", "Ser capaz de"
e "Conhecer e ..." são puladas para chegar ao verbo de ação. Requisitos com dois verbos
coordenados ("Construir e apresentar") recebem o nível MAIS ALTO entre eles.
Verbos fora do dicionário ficam como "Não classificado" e vão para revisão manual.

Também marca se o requisito toca em temas de biotecnologia (palavras-chave abaixo).

Uso: python -I scripts/classificar_bloom.py
Lê  dados/especialidades/especialidades.json
Gera dados/especialidades/requisitos_bloom.csv e verbos_nao_classificados.csv
"""
import sys as _sys
_sys.stdout.reconfigure(encoding="utf-8")
import csv
import json
import re
import unicodedata
from collections import Counter

BASE = "dados/especialidades"
NIVEIS = ["Participar", "Lembrar", "Compreender", "Aplicar", "Analisar", "Avaliar", "Criar"]

VERBOS = {
    "Participar": """participar assistir frequentar comparecer visitar acompanhar colaborar ajudar auxiliar
        integrar contribuir envolver tomar estar vivenciar conviver ouvir""",
    "Lembrar": """conhecer citar enumerar listar nomear identificar reconhecer mencionar relacionar indicar
        memorizar recitar repetir definir localizar apontar recordar saber""",
    "Compreender": """explicar descrever apresentar relatar expor resumir interpretar exemplificar classificar
        comparar ilustrar conceituar entender compreender comentar discutir conversar dizer contar
        pesquisar estudar ler informar narrar caracterizar diferenciar_conceitos expressar traduzir
        conceitar esclarecer falar demonstrar_conhecimento mostrar_conhecimento""",
    "Aplicar": """realizar executar fazer demonstrar utilizar usar montar preparar praticar aplicar implementar
        construir confeccionar cozinhar acender amarrar navegar nadar percorrer operar manusear medir
        calcular desenhar tirar fotografar filmar cultivar plantar coletar manter cuidar tocar cantar
        jogar prestar ensinar mostrar observar testar instalar reparar consertar limpar costurar pintar
        transmitir enviar receber conduzir dirigir_veiculo pilotar remar velejar escalar correr pedalar
        socorrer tratar resolver registrar anotar fixar afiar transportar improvisar recolher separar
        reciclar cozer assar servir dobrar armar desmontar guardar acondicionar empregar seguir efetuar
        decorar treinar exercitar mergulhar lancar atirar arremessar saltar orientar_se manobrar ler_mapa
        produzir_alimento confeccionar fabricar soldar ligar programar_dispositivo digitar navegar_internet
        criar_conta acessar cadastrar""",
    "Analisar": """analisar diferenciar distinguir organizar investigar examinar escolher selecionar verificar
        diagnosticar mapear levantar inventariar categorizar comparar_criticamente estruturar
        identificar_e_corrigir avaliar_riscos calcular_custos orcar""",
    "Avaliar": """avaliar julgar criticar debater argumentar justificar defender opinar recomendar coordenar
        liderar chefiar monitorar supervisionar decidir propor_solucoes refletir ponderar""",
    "Criar": """criar elaborar projetar planejar inventar compor produzir desenvolver idealizar propor redigir
        escrever conceber programar organizar_evento roteirizar construir_projeto desenhar_projeto
        gravar_producao editar montar_espetaculo""",
}
EXTRA = {  # verbos encontrados nos requisitos da UEB que não estavam no dicionário inicial
    "Participar": "trazer",
    "Lembrar": "possuir enunciar",
    "Compreender": "aprender discorrer buscar explorar descobrir associar dissertar especificar",
    "Aplicar": """entrevistar trabalhar gravar atuar simular dominar trocar reproduzir orientar representar dar
        atravessar colocar dramatizar configurar encontrar passar marcar colher empinar abrir posicionar
        dirigir modificar encadernar acertar dissecar afinar estabelecer conectar digitalizar extrair obter
        decolar pousar lidar embutir trimar""",
    "Analisar": "catalogar",
    "Avaliar": "promover validar",
    "Criar": "formular customizar recriar",
}
# Requisitos escritos no imperativo ou com erro de digitação
IMPERATIVO = {"cite": "citar", "explique": "explicar", "escolha": "escolher", "descreva": "descrever",
              "faca": "fazer", "identifique": "identificar", "entende": "entender", "scolher": "escolher",
              "demonstre": "demonstrar", "apresente": "apresentar", "liste": "listar"}
for nivel, txt in EXTRA.items():
    VERBOS[nivel] += " " + txt

VERBO_NIVEL = {}
for nivel, txt in VERBOS.items():
    for v in txt.split():
        VERBO_NIVEL.setdefault(v, nivel)

PULAR = {"saber", "ser", "capaz", "de", "o", "a", "os", "as", "e", "ou", "conhecer", "poder", "sobre"}

BIOTEC = {
    "biotecnologia (direta)": r"biotecnolog|\bdna\b|\brna\b|genétic|\bgenes?\b|genoma|transgên|clonag|"
                              r"vacina|enzima|ferment|levedura|biorremedia|biocombust|biogás|biodiesel",
    "microbiologia e saneamento (relacionada)": r"microrganism|micro-organism|microbio|bactéri|fungo|vírus|"
                                                r"microscóp|cultura de (bactéri|fung|microrganism|célul)|"
                                                r"compostag|decomposi|esgoto|"
                                                r"tratamento d[ae] água|purifica|saneamento|chorume|biodegrad",
}


def norm(s):
    return unicodedata.normalize("NFC", s.lower())


def sem_acento(s):
    return "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn")


def infinitivo(palavra):
    """Leva formas comuns ao infinitivo: 'cite' -> 'citar' não é preciso; os requisitos já vêm no
    infinitivo. Só trata o reflexivo (orientar-se) e tira pontuação."""
    p = palavra.strip(" ,.;:()\"'“”")
    p = re.sub(r"-(se|lo|la|los|las)$", "", p)
    p = sem_acento(p)
    return IMPERATIVO.get(p, p)


def classificar(req):
    txt = norm(req)
    txt = re.sub(r"^\s*[\d\.\)\-–a-z]\s*[\)\.]\s*", "", txt)  # tira "a) " ou "1. "
    if re.match(r"^(demonstrar|mostrar|ter|possuir)\s+(que\s+conhece|conhecimento)", txt):
        return "Compreender", "demonstrar conhecimento"
    if re.match(r"^ter\s+(participado|assistido|frequentado|visitado|acompanhado|colaborado|ajudado)", txt):
        return "Participar", "ter participado"
    if re.match(r"^(ter|possuir)\s", txt):
        return "Lembrar", "ter"
    palavras = txt.split()
    # Requisito que não abre com verbo ("Em um acampamento, identificar..."): procura o 1º verbo conhecido
    if palavras and infinitivo(palavras[0]) not in VERBO_NIVEL and infinitivo(palavras[0]) not in PULAR:
        for j, p in enumerate(palavras[1:9], 1):
            w = infinitivo(p)
            if w in VERBO_NIVEL and w.endswith(("ar", "er", "ir", "or")):
                palavras = palavras[j:]
                break
    verbos = []
    i = 0
    # Verbo principal e verbos coordenados logo depois ("construir e apresentar", "montar, desmontar e dobrar")
    while i < len(palavras) and len(verbos) < 4:
        w = infinitivo(palavras[i])
        if w in PULAR and not verbos:
            # "Saber" e "Conhecer" sozinhos contam como Lembrar se nenhum outro verbo vier
            if w in ("saber", "conhecer") and (i + 1 >= len(palavras) or infinitivo(palavras[i + 1]) not in VERBO_NIVEL):
                return "Lembrar", w
            i += 1
            continue
        if w.endswith(("ar", "er", "ir", "or")) and w in VERBO_NIVEL:
            verbos.append(w)
            # segue se o próximo for "e"/"," + verbo
            if i + 2 < len(palavras) and palavras[i + 1] in ("e", "ou") and infinitivo(palavras[i + 2]) in VERBO_NIVEL:
                i += 2
                continue
            if palavras[i].endswith(",") and i + 1 < len(palavras) and infinitivo(palavras[i + 1]) in VERBO_NIVEL:
                i += 1
                continue
            break
        if not verbos:
            return "Não classificado", w
        break
    if not verbos:
        return "Não classificado", infinitivo(palavras[0]) if palavras else ""
    nivel = max((VERBO_NIVEL[v] for v in verbos), key=NIVEIS.index)
    return nivel, "+".join(verbos)


def tema_biotec(req):
    t = norm(req)
    for tema, rx in BIOTEC.items():
        if re.search(rx, t):
            return tema
    return ""


esps = json.load(open(f"{BASE}/especialidades.json", encoding="utf-8"))
linhas = []
nao = Counter()
for e in esps:
    # Sênior e Pioneiro (programa atualizado) não têm lista fixa de itens: ficam fora da classificação
    if e["programa"].startswith("Atualizado (Sênior"):
        continue
    for n, req in enumerate(e["requisitos"], 1):
        nivel, verbo = classificar(req)
        if nivel == "Não classificado":
            nao[verbo] += 1
        linhas.append({
            "programa": e["programa"], "area": e["area"], "especialidade": e["nome"], "slug": e["slug"],
            "item": n, "requisito": req, "verbo": verbo, "nivel_bloom": nivel,
            "tema_biotec": tema_biotec(req),
            "revisao_manual": "",
        })

with open(f"{BASE}/requisitos_bloom.csv", "w", encoding="utf-8-sig", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=list(linhas[0]))
    w.writeheader()
    w.writerows(linhas)
with open(f"{BASE}/verbos_nao_classificados.csv", "w", encoding="utf-8-sig", newline="") as fh:
    w = csv.writer(fh)
    w.writerow(["verbo", "ocorrencias"])
    w.writerows(nao.most_common())

tot = len(linhas)
nc = sum(1 for l in linhas if l["nivel_bloom"] == "Não classificado")
print(f"requisitos: {tot} | classificados: {tot - nc} ({(tot - nc) / tot:.1%})")
print(Counter(l["nivel_bloom"] for l in linhas).most_common())
print("não classificados mais comuns:", nao.most_common(40))
