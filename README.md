# TCC: Educação científica ao ar livre

**Práticas escoteiras como estratégia de divulgação em biotecnologia.**
Romério de Oliveira Lima Filho e Bruna Pereira Lopes, IFRJ (EDC).

Este repositório guarda os textos de trabalho, os dados e os scripts das análises do TCC.
Os textos oficiais ficam no Google Drive, na pasta "TCC - EDC - Bruna e Romério".

## Estrutura

| Pasta / arquivo | Conteúdo |
|---|---|
| `textos/tcc/` | Cópias em Markdown dos Google Docs do TCC |
| `textos/revisao/` | Revisão de literatura: strings de busca, acervo da UEB, pré-lista de trabalhos |
| `dados/trabalhos_ueb/` | Tabela única com os metadados dos 46 trabalhos acadêmicos da UEB (`trabalhos_ueb.csv`, com dicionário de dados no README da pasta) |
| `dados/especialidades/` | Especialidades escoteiras da UEB com requisitos e classificação na taxonomia de Bloom |
| `scripts/` | Coleta, extração e figuras (Python) |
| `figuras/` | Figuras geradas (PNG e SVG) |
| `referencias/` | Lista dos artigos de referência (os PDFs ficam só na máquina local) |

## Análises

1. **Acervo de trabalhos acadêmicos da UEB.** Linha do tempo, distribuição por área e nuvens de palavras.
   Fonte: <https://www.escoteiros.org.br/downloads/categorias/trabalhos-academicos/>
2. **Especialidades escoteiras e taxonomia de Bloom.** Inspirado em Vick e Garvey (2008), que fizeram
   a mesma análise com as *merit badges* dos Boy Scouts of America, e no manual
   *Neurociências, cognição e as especialidades escoteiras* (UEB, 2023), que propõe o nível extra “Participar”.
   Fonte: <https://www.escoteiros.org.br/especialidades/>

## Como reproduzir

Requer Python 3.12 com `pandas`, `matplotlib`, `wordcloud` e `pypdf`. Rodar a partir da raiz do projeto:

```bash
python -I scripts/extrair_trabalhos.py dados/trabalhos_ueb
python -I scripts/tabela_trabalhos.py
python -I scripts/figuras_acervo.py
python -I scripts/figuras_mapa.py
python -I scripts/coletar_especialidades.py
python -I scripts/classificar_bloom.py
python -I scripts/figuras_especialidades.py
```

Os PDFs dos trabalhos e os textos extraídos **não ficam no repositório**, porque são obras de terceiros.
Para baixar de novo, use as URLs em `dados/trabalhos_ueb/index.tsv` (o primeiro script espera os PDFs em
`dados/trabalhos_ueb/pdf/`, com os nomes da primeira coluna).

## Observações de método

- **Ano dos trabalhos:** o ano da capa ou folha de rosto. Nos 9 trabalhos sem data, foi usado o ano da
  referência mais recente citada no texto (coluna `ano_estimado = 1`).
- **Classificação de Bloom:** automática, pelo verbo inicial de cada requisito, com um dicionário de verbos.
  É uma primeira passada: os itens devem ser revisados por duas pessoas, com medida de concordância, antes de
  irem para o texto final.
