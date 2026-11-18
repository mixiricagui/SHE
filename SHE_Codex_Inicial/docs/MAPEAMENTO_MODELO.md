# Mapeamento preliminar: modelo Excel e atas

> Referência de levantamento para implementação. NÃO é uma aprovação do modelo documental nem da legislação. Conferir com o secretário ou gestora autorizada.

## Inspeção local de 17/11/2026

Conversão realizada pelo Excel instalado, em cópia XLSX. Original preservado.
Mesclagens verificadas: H14:W14 (nome), X14:Z14 (região de rótulo), AA14:AC14 (região para matrícula), H15:N15, D16:P16 e D17:P17.
Na frente, as colunas T/U, V/W, X/Y, Z/AA correspondem aos campos previstos. No verso, C3:D11, E3:L11 e M3:N11 são mesclados individualmente por linha; escrever somente nas âncoras C, E e M.
Ambas as abas estão em A4/retrato e sem área de impressão explícita. Não considerar paginação validada.
O mapa `mapa_modelo_rascunho.json` permanece não aprovado: ainda é necessário conferir campos mistos de rótulo/valor, totais, cabeçalhos e rodapés antes de autorizar a limpeza do exemplar e a emissão.

## Arquivo-base recebido

- Original: `Historico F1 e F2 modelo.xls` (Excel formato legado).
- Abas: `E_Fundamental` e `E_Fund_Verso`.
- Modelo contém dados preenchidos de um **exemplo anterior**: não reutilizar esses dados em outros estudantes.

## Frente: aba `E_Fundamental`

- Linha 7: `G7` apresenta "Escola Municipal Paulo Freire" enquanto `H7` apresenta "Educandário Ulisses Guimarães". **DIVERGÊNCIA A RESOLVER:** não assumir automaticamente qual unidade oficial emitir.
- Linha 14: nome aparece na região iniciada em `H14`; campo matrícula aparece no setor da coluna `X` da linha 14. Conferir célula exata por causa das mesclagens.
- Linha 15: data de nascimento na região iniciada em `H15`. Sexo/naturalidade/nacionalidade na mesma linha: há conteúdo preexistente, verificar antes de preencher.
- Linhas 16–17: filiação, pai e mãe, a partir da região da coluna `D` (texto de rótulo e valor na mesma área; validar as mesclagens).
- Linha 23: cabeçalhos de 1º a 9º ano.
- Linha 25: C/N = conceito ou nota; CH = carga horária.

| Ano escolar | Coluna da nota/conceito | Coluna da carga horária |
|---|---|---|
| 6º ano | `T` | `U` |
| 7º ano | `V` | `W` |
| 8º ano | `X` | `Y` |
| 9º ano | `Z` | `AA` |

| Disciplina, como aparece ou equivalente no modelo | Linha da nota |
|---|---|
| Português | 29 |
| Língua Estrangeira Moderna (Inglês) | 30 |
| Geografia | 35 |
| História | 36 |
| Ciências | 40 |
| Matemática | 43 |
| Educação Artística / Arte | 44 |
| Educação Física | 46 |
| Ensino Religioso | 48 |

- Linha 54: total de carga horária. **Nunca assumir que o total preexistente é o total do aluno corrente.** Validar com a matriz curricular aplicável a cada ano.
- O modelo contém áreas preenchidas para anos anteriores e série/ano. Limpar seletivamente SOMENTE campos variáveis com mapeamento testado; preservar textos, fórmulas, mesclagens e formatação oficiais.

## Verso: aba `E_Fund_Verso`

- `A3:A11`: 1º ao 9º ano.
- `C3:C11`: anos letivos **já preenchidos** (2017–2025 no exemplar), não válidos automaticamente para todo estudante.
- `E3:E11`: unidade escolar, preenchida no exemplar.
- `M3:M11`: município.
- `O3:O11`: UF.
- Há campos de registros complementares, equivalência, educação física e transferência em curso. A existência da seção **não significa** que todo aluno possua transferência ou preenchimento nesses campos.
- Confirmar impressão frente/verso e paginação física antes do uso oficial.

## Fotografias das atas recebidas

- Primeira foto: ata de resultados finais, 8º ano, ano letivo 2024.
- Segunda foto: ata de resultados finais, 9º ano, ano letivo 2025.
- Notas e nomes manuscritos, com colunas estreitas e cabeçalhos verticais.
- Aparecem situações como aprovação e transferência; há observações e linhas que não representam uma sequência normal de notas.
- A ordenação dos componentes curriculares **não deve ser presumida constante** entre fotografias.
- Não usar os nomes verdadeiros ou suas notas como fixture de teste. Utilizar dados fictícios e imagens anonimizadas.

## Pendências que bloqueiam emissão oficial

1. Confirmar nome oficial da escola e campos de identificação do estabelecimento (há referências divergentes).
2. Confirmar matriz curricular/carga horária e critérios de avaliação conforme ano letivo.
3. Confirmar dados obrigatórios de identificação do aluno, que as atas de resultados não necessariamente trazem (nascimento, filiação, matrícula etc.).
4. Confirmar tratamento escolar de transferência, reprovação, EJA, observações e registros complementares.
5. Confirmar quando é obrigatório preencher o verso e a política de assinatura/validação.
