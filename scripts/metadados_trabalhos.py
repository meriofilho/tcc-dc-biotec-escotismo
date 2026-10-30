"""Gera dados/trabalhos_ueb/metadados.csv: ano e título curto de cada trabalho do acervo da UEB.

Ano: o da capa/folha de rosto quando existe. Sem data na capa, usa o ano mais
recente citado no texto (limite inferior) e marca ano_estimado=1.
"""
import csv
import os
import sys
import urllib.parse

base = sys.argv[1] if len(sys.argv) > 1 else "dados/trabalhos_ueb"

# arquivo: (ano, estimado, título curto)
META = {
    "01": (2014, 1, "Preservação de unidades de conservação na educação ambiental não formal escoteira (Goiânia-GO)"),
    "02": (2012, 0, "Avaliação motora em escoteiros de 7 a 11 anos (Presidente Getúlio-SC)"),
    "03": (2013, 0, "Medida social alternativa de promoção de saúde e prevenção da violência"),
    "04": (2013, 0, "Unidades de conservação para potencializar o programa e o método escoteiro"),
    "05": (2011, 0, "Preservação do gato-do-mato na região do Alto Uruguai"),
    "06": (2011, 0, "O método escoteiro a serviço do ensino de engenharia"),
    "07": (2012, 1, "Protagonismo juvenil e Movimento Escoteiro: história e panorama contemporâneo"),
    "08": (2007, 0, "Relatório de estágio supervisionado em Administração"),
    "09": (2018, 0, "Scout em ação"),
    "10": (2021, 1, "Escotismo: acessibilidade em ambientes virtuais"),
    "11": (2020, 0, "Em movimento: as mulheres no Escotismo"),
    "12": (2017, 1, "O Escotismo como elemento desenvolvedor da identidade psicossocial na terceira infância"),
    "13": (2019, 1, "A educação não formal escoteira e sua relação com as teorias de aprendizagem"),
    "14": (2025, 0, "Escotismo como ferramenta no combate à intimidação sistemática (bullying)"),
    "15": (2026, 0, "A Rede Nacional de Jovens Líderes e o seu papel pedagógico na UEB"),
    "16": (2011, 0, "Movimento Escoteiro: a vida de Baden-Powell e o nascimento do Escotismo"),
    "17": (2014, 1, "Movimento Escoteiro: liderança com base em valores"),
    "18": (2006, 0, "Movimento Escoteiro: projeto educativo extraescolar"),
    "19": (2013, 0, "Mowgli: o mito do herói vivido no Movimento Escoteiro"),
    "20": (2002, 0, "O Escotismo como opção de investimento em educação não formal"),
    "21": (2019, 0, "O Movimento Escoteiro e as relações internacionais"),
    "22": (2004, 0, "O Movimento Escoteiro no Brasil e os projetos nacionalistas de educação (1910-1945)"),
    "23": (2013, 0, "O Scouting for Boys abre para mulheres: a coeducação no escotismo brasileiro"),
    "24": (2010, 0, "Práticas pedagógicas ou militares: impasses da prática escoteira"),
    "25": (2004, 0, "Educação não formal tendo como modelo pedagógico o método escoteiro"),
    "26": (2014, 0, "Educação musical no Movimento Escoteiro"),
    "27": (2014, 0, "Educação não formal: a contribuição do Escotismo para a formação do caráter"),
    "28": (2006, 0, "Novo processo de atração e seleção de escotistas e dirigentes"),
    "29": (2017, 1, "Evasão do membro juvenil do Movimento Escoteiro"),
    "30": (2016, 0, "Grupo Escoteiro Continente: possibilidade pedagógica de educação não formal"),
    "31": (2015, 1, "Inteligência emocional: o que as organizações podem aprender com o Escotismo"),
    "32": (2014, 0, "Irmãos Escoteiros: inclusão e exclusão de membros homossexuais"),
    "33": (2017, 0, "Jogos e sua contribuição à educação"),
    "34": (2019, 0, "A performance de um escoteiro como colaborador na Caixa Econômica Federal"),
    "35": (2015, 0, "A prática do Escotismo e suas influências no contexto socioambiental e educacional"),
    "36": (2017, 1, "Princípios metodológicos do Escotismo na educação formal"),
    "37": (2017, 0, "As práticas do ensino não formal em Geografia"),
    "38": (2009, 0, "As áreas de desenvolvimento nos grupos escoteiros de Porto Alegre"),
    "39": (2016, 0, "Aspectos legais e biopsicossociais da inimputabilidade do adolescente"),
    "40": (2006, 0, "Discurso escoteiro: um olhar retórico sobre o Escotismo"),
    "41": (2010, 0, "DROPS: revista de divulgação dos valores do Movimento Escoteiro"),
    "42": (2013, 0, "Educação musical através da música escoteira"),
    "43": (2011, 0, "A contribuição do Movimento Escoteiro na educação do Brasil"),
    "44": (2012, 0, "A educação no canto do Uirapuru: subjetividades de mulheres no Escotismo"),
    "45": (2015, 0, "Sempre Alerta: de escoteiro a empreendedor social"),
    "46": (2025, 0, "WebSIG dos grupos escoteiros da América Latina e Caribe"),
}
AREA = {
    "ciencias-biologicas": "Ciências Biológicas",
    "ciencias-exatas": "Ciências Exatas",
    "ciencias-humanas": "Ciências Humanas",
    "tecnologia": "Tecnologia",
}

rows = [l.rstrip("\n").split("\t") for l in open(os.path.join(base, "index.tsv"), encoding="utf-8")]
with open(os.path.join(base, "metadados.csv"), "w", encoding="utf-8", newline="") as fh:
    w = csv.writer(fh)
    w.writerow(["arquivo", "area", "ano", "ano_estimado", "titulo", "url"])
    for f, area, url, _ in rows:
        ano, est, tit = META[f[:2]]
        w.writerow([f, AREA[area], ano, est, tit, url])
print("ok", len(rows))
