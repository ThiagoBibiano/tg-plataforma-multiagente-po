# Plataforma multiagente *low-code* para Pesquisa Operacional — texto do TG

Texto, em LaTeX, do Trabalho de Graduação *Plataforma multiagente low-code para
formulação e resolução de problemas de programação linear e linear inteira mista
a partir de descrições em língua portuguesa*.

- **Autor:** Thiago Bibiano da Silva
- **Orientação:** Profa. Carolina Corrêa de Carvalho
- **Curso:** Bacharelado em Engenharia de Gestão — Universidade Federal do ABC

O artefato descrito no texto é desenvolvido em um repositório próprio:
[`po-multiagente`](https://github.com/ThiagoBibiano/po-multiagente).

## Estrutura

```
.
├── main.tex            # documento principal: só preâmbulo e \input
├── preambulo.tex       # pacotes e configuração do abnTeX2
├── referencias.bib     # referências bibliográficas
├── pretextual/         # capa, folha de rosto e dados do trabalho
├── capitulos/          # cap1 (Introdução), cap2 (Referencial), cap3 (Metodologia)
├── figuras/            # figuras em PDF, com a fonte SVG ao lado
├── latex/bst/          # estilo bibliográfico ABNT ajustado ao guia da UFABC
└── tg2.code-workspace  # abre este repositório e o do código numa só janela do VS Code
```

## Como compilar

Requer uma distribuição TeX com abnTeX2 (por exemplo, TeX Live completo).

```bash
latexmk -pdf -interaction=nonstopmode main.tex   # gera main.pdf
latexmk -C                                        # remove os arquivos de build
```

## Relação com o código

O fluxo é de mão única, do código para o texto. Quando houver resultados, este
repositório registrará em `artefato.lock` a versão exata do `po-multiagente`
que os gerou, e as tabelas serão importadas por script para `resultados/`.

## O que não está aqui

Ficam só no computador do autor, fora do versionamento: os artigos de
referência em PDF (direitos de terceiros), rascunhos, logs de revisão e versões
anteriores do texto. Alguns comentários nos arquivos `.tex` citam esses
arquivos (`auditoria/...`) como registro de onde veio cada decisão.
