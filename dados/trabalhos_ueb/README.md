# Acervo de trabalhos acadêmicos da UEB

Fonte: <https://www.escoteiros.org.br/downloads/categorias/trabalhos-academicos/> (46 trabalhos, coleta em 29/10/2026).

## Arquivos

| Arquivo | Conteúdo |
|---|---|
| `trabalhos_ueb.csv` | **Tabela principal**: um trabalho por linha, com todos os metadados (dicionário abaixo). Gerada por `scripts/tabela_trabalhos.py` |
| `index.tsv` | Arquivo local, área no site, URL do PDF e tamanho (saída do download) |
| `lista.tsv` | Lista bruta de URLs por área, como coletada no site |
| `candidatos_ano.tsv` | Saída da extração de texto: páginas, anos que aparecem na capa, ano nos metadados do PDF |
| `frequencia_palavras_geral.csv` | 200 palavras mais frequentes (base das nuvens de palavras) |
| `resumo_instituicoes.csv` | Nº de trabalhos por instituição |
| `pdf/`, `texto/` | PDFs e texto extraído (**só locais**, fora do git: obras de terceiros) |

## Dicionário de dados de `trabalhos_ueb.csv`

Codificação UTF-8 com BOM (abre direto no Excel). Campos lidos na capa, folha de rosto, resumo e notas de rodapé de cada PDF.

| Coluna | Descrição |
|---|---|
| `id` | Identificador: UEB01 a UEB46, na ordem do site (área e página) |
| `arquivo_local` | Nome do PDF em `pdf/` |
| `titulo` | Título completo |
| `autores` | Autores, separados por `;` |
| `n_autores` | Número de autores |
| `orientacao` | Orientador(a) e coorientador(a), quando informados |
| `ano` | Ano de publicação ou defesa |
| `ano_estimado` | 1 = sem data na capa; ano estimado pela referência mais recente citada no texto |
| `tipo_trabalho` | TCC, Monografia, Dissertação, Artigo, Trabalho em evento, Relatório de estágio, Projeto experimental |
| `nivel` | Técnico, Graduação, Especialização (inclui MBA), Mestrado, Docente/pesquisador ou Não informado |
| `curso` | Curso ou programa de origem |
| `grande_area_curso` | Grande área do curso, pela tabela de áreas do CNPq/CAPES (Ensino e Ciências Ambientais = Multidisciplinar) |
| `area_ueb` | Área atribuída pelo site da UEB (Ciências Biológicas, Exatas, Humanas, Tecnologia) |
| `tema` | Tema principal, codificado a partir do título e do resumo (10 categorias; classificação preliminar, a revisar) |
| `instituicao`, `sigla` | Instituição de origem |
| `natureza_instituicao` | Pública federal, estadual ou municipal; Privada (inclui comunitárias e confessionais); Não informada |
| `cidade`, `uf`, `regiao`, `pais` | Local da instituição |
| `lat`, `lon` | Coordenadas aproximadas do centro da cidade (graus decimais) |
| `local_estimado` | 1 = o PDF não informa a instituição; local = cidade do estudo ou do autor |
| `observacao_vinculo` | Detalhes sobre o vínculo institucional ou o contexto do trabalho |
| `veiculo` | Revista ou evento, quando o trabalho foi publicado como artigo |
| `paginas` | Nº de páginas do PDF |
| `palavras_chave` | Palavras-chave do resumo, separadas por `;` (vazio se o trabalho não traz) |
| `relevancia_tcc` | Alta, Secundária ou Baixa para o nosso TCC (mesma triagem da revisão de literatura) |
| `url` | Link do PDF no site da UEB |

## Observações

- A coluna `area_ueb` é a classificação do site e nem sempre corresponde ao curso. Exemplo: 5 trabalhos estão em
  "Ciências Biológicas", mas só um vem de um curso de Biologia; os outros vêm de Educação Física, Medicina
  Preventiva, Saneamento Ambiental e Educação Ambiental. Para análises por área do conhecimento, use
  `grande_area_curso`.
- UEB23 é um artigo derivado da dissertação UEB44 (mesma autora).
- UEB35 é um mestrado de uma instituição paraguaia, feito por autora brasileira.
