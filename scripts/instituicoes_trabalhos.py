"""Gera dados/trabalhos_ueb/instituicoes.csv: instituição, cidade, UF e coordenadas de cada trabalho.

Fonte: capa, folha de rosto ou notas de rodapé de cada PDF (lidos em 30/10/2026).
local_estimado = 1 quando o PDF não informa a instituição; nesse caso usamos a cidade
do estudo ou do vínculo do autor.
Coordenadas: centro aproximado da cidade (graus decimais).
"""
import csv
import os
import sys

base = sys.argv[1] if len(sys.argv) > 1 else "dados/trabalhos_ueb"

CIDADE = {  # cidade: (UF, região, lat, lon)
    "Goiânia": ("GO", "Centro-Oeste", -16.68, -49.25),
    "Brasília": ("DF", "Centro-Oeste", -15.79, -47.88),
    "Blumenau": ("SC", "Sul", -26.92, -49.07),
    "Caçador": ("SC", "Sul", -26.78, -51.01),
    "São José": ("SC", "Sul", -27.61, -48.63),
    "Palhoça": ("SC", "Sul", -27.64, -48.67),
    "Tubarão": ("SC", "Sul", -28.47, -49.01),
    "Belo Horizonte": ("MG", "Sudeste", -19.92, -43.94),
    "Sete Lagoas": ("MG", "Sudeste", -19.47, -44.25),
    "Três Corações": ("MG", "Sudeste", -21.69, -45.25),
    "Campinas": ("SP", "Sudeste", -22.91, -47.06),
    "São Paulo": ("SP", "Sudeste", -23.55, -46.63),
    "São Caetano do Sul": ("SP", "Sudeste", -23.62, -46.55),
    "São Bernardo do Campo": ("SP", "Sudeste", -23.69, -46.56),
    "São José dos Campos": ("SP", "Sudeste", -23.18, -45.89),
    "São Sebastião": ("SP", "Sudeste", -23.80, -45.40),
    "Rio de Janeiro": ("RJ", "Sudeste", -22.91, -43.17),
    "Vitória": ("ES", "Sudeste", -20.32, -40.34),
    "Vila Velha": ("ES", "Sudeste", -20.33, -40.29),
    "Santa Maria": ("RS", "Sul", -29.69, -53.81),
    "Porto Alegre": ("RS", "Sul", -30.03, -51.23),
    "Canoas": ("RS", "Sul", -29.92, -51.18),
    "Caxias do Sul": ("RS", "Sul", -29.17, -51.18),
    "Novo Hamburgo": ("RS", "Sul", -29.68, -51.13),
    "Lajeado": ("RS", "Sul", -29.47, -51.96),
    "Rio Grande": ("RS", "Sul", -32.03, -52.10),
    "Curitiba": ("PR", "Sul", -25.43, -49.27),
    "Campo Largo": ("PR", "Sul", -25.46, -49.53),
    "Natal": ("RN", "Nordeste", -5.79, -35.21),
    "Aracaju": ("SE", "Nordeste", -10.91, -37.07),
    "Valença": ("BA", "Nordeste", -13.37, -39.07),
    "Assunção": ("Paraguai", "Exterior", -25.26, -57.58),
}

# arquivo: (instituição, sigla, cidade, local_estimado)
INST = {
    "01": ("Instituto Federal de Goiás", "IFG", "Goiânia", 0),
    "02": ("Universidade Regional de Blumenau", "FURB", "Blumenau", 0),
    "03": ("Universidade Federal de Minas Gerais", "UFMG", "Belo Horizonte", 0),
    "04": ("Pontifícia Universidade Católica de Campinas", "PUC-Campinas", "Campinas", 0),
    "05": ("Universidade Federal de Santa Maria", "UFSM", "Santa Maria", 0),
    "06": ("Universidade Municipal de São Caetano do Sul", "USCS", "São Caetano do Sul", 0),
    "07": ("Não informada (Grupo Escoteiro Curuqui, São Paulo)", "—", "São Paulo", 1),
    "08": ("Centro Universitário Newton Paiva", "Newton Paiva", "Belo Horizonte", 0),
    "09": ("Universidade Anhembi Morumbi", "Anhembi Morumbi", "São Paulo", 0),
    "10": ("Centro Universitário Uniftec", "Uniftec", "Caxias do Sul", 0),
    "11": ("Universidade do Vale do Paraíba", "Univap", "São José dos Campos", 0),
    "12": ("Faculdade Ciências da Vida", "FCV", "Sete Lagoas", 0),
    "13": ("Universidade Federal do Rio Grande do Sul", "UFRGS", "Porto Alegre", 0),
    "14": ("Universidade São Francisco", "USF", "Campinas", 0),
    "15": ("Universidade Federal do Rio Grande do Norte", "UFRN", "Natal", 0),
    "16": ("Universidade Federal do Espírito Santo", "UFES", "Vitória", 0),
    "17": ("Não informada (autor de Porto Alegre)", "—", "Porto Alegre", 1),
    "18": ("Universidade do Contestado", "UnC", "Caçador", 0),
    "19": ("Universidade Metodista de São Paulo", "UMESP", "São Bernardo do Campo", 0),
    "20": ("Unicapital", "Unicapital", "São Paulo", 0),
    "21": ("Universidade Federal do Rio de Janeiro", "UFRJ", "Rio de Janeiro", 0),
    "22": ("Universidade Federal de Minas Gerais", "UFMG", "Belo Horizonte", 0),
    "23": ("Universidade Tiradentes", "UNIT", "Aracaju", 0),
    "24": ("Universidade do Estado da Bahia, Campus XV", "UNEB", "Valença", 0),
    "25": ("Centro Universitário da Cidade do Rio de Janeiro", "UniverCidade", "Rio de Janeiro", 0),
    "26": ("Faculdade Integral Cantareira", "Cantareira", "São Paulo", 0),
    "27": ("Faculdade Cenecista de Campo Largo", "FACECLA", "Campo Largo", 0),
    "28": ("Universidade do Vale do Itajaí, Centro de São José", "Univali", "São José", 0),
    "29": ("Não informada (estudo em Tubarão)", "—", "Tubarão", 1),
    "30": ("Faculdade Municipal de Palhoça", "FMP", "Palhoça", 0),
    "31": ("Centro Universitário La Salle", "Unilasalle", "Canoas", 0),
    "32": ("Sociedade Brasileira de Dinâmica dos Grupos", "SBDG", "São Paulo", 0),
    "33": ("Universidade Candido Mendes", "UCAM", "Vila Velha", 0),
    "34": ("Faculdade de Tecnologia de São Sebastião", "Fatec", "São Sebastião", 0),
    "35": ("Universidad Evangélica del Paraguay", "UEP", "Assunção", 0),
    "36": ("Centro Universitário Faculdades Integradas São Pedro", "FAESA", "Vitória", 0),
    "37": ("Universidade de Brasília (estudo em Barretos-SP)", "UnB", "Brasília", 0),
    "38": ("Escola Superior de Administração, Direito e Economia", "ESADE", "Porto Alegre", 0),
    "39": ("Centro Universitário Autônomo do Brasil", "UniBrasil", "Curitiba", 0),
    "40": ("Centro Universitário Feevale", "Feevale", "Novo Hamburgo", 0),
    "41": ("Universidade Positivo", "UP", "Curitiba", 0),
    "42": ("Universidade Vale do Rio Verde", "UninCor", "Três Corações", 0),
    "43": ("Universidade de São Paulo", "USP", "São Paulo", 0),
    "44": ("Universidade Tiradentes", "UNIT", "Aracaju", 0),
    "45": ("Centro Universitário Univates", "Univates", "Lajeado", 0),
    "46": ("Instituto Federal do Rio Grande do Sul, Campus Rio Grande", "IFRS", "Rio Grande", 0),
}

rows = list(csv.DictReader(open(os.path.join(base, "metadados.csv"), encoding="utf-8")))
with open(os.path.join(base, "instituicoes.csv"), "w", encoding="utf-8", newline="") as fh:
    w = csv.writer(fh)
    w.writerow(["arquivo", "area", "ano", "instituicao", "sigla", "cidade", "uf", "regiao",
                "local_estimado", "lat", "lon", "titulo"])
    for r in rows:
        inst, sig, cid, est = INST[r["arquivo"][:2]]
        uf, reg, lat, lon = CIDADE[cid]
        w.writerow([r["arquivo"], r["area"], r["ano"], inst, sig, cid, uf, reg, est, lat, lon, r["titulo"]])
print("ok", len(rows))
