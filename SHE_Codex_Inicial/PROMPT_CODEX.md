# PROMPT PRINCIPAL PARA O CODEX — SHE

Você é meu engenheiro de software responsável por construir e testar o MVP do **SHE — Sistema de Históricos Escolares**, usado por uma secretaria escolar municipal brasileira. Trabalhe **diretamente no repositório aberto**, criando e modificando arquivos; não se limite a explicar o que faria. O projeto já possui um esqueleto Python + Streamlit + SQLite, documentação e testes. Respeite as estruturas existentes, refatore quando necessário e execute os testes. Comunique objetivamente o que foi implementado, o que permanece pendente e os comandos executados.

## 1. Objetivo de produto

Reduzir o trabalho manual de elaboração de históricos escolares a partir de atas de resultados finais (fotos de folhas manuscritas) e um modelo Excel já usado pela escola. A aplicação deve importar imagens, permitir identificar estudantes e resultados, revisar/corrigir os dados, preencher uma cópia limpa do modelo oficial e exportar arquivos individuais em XLSX e, quando possível de forma confiável, PDF. **Nunca emitir um documento sem revisão humana e sem campos obrigatórios confirmados.**

O alvo inicial é um MVP local, executável no Windows, preferencialmente em até dois dias de esforço focado. Priorize qualidade da transcrição e emissão confiável; não prometa OCR perfeito nem conformidade legal automática.

## 2. Materiais-base e evidência real

O usuário já possui os seguintes arquivos; estarão disponíveis localmente na pasta `dados/referencias/` quando copiados por ele:

- `Historico F1 e F2 modelo.xls`: histórico escolar legado em Excel, frente e verso.
- Fotografias de atas do 8º ano de 2024 e 9º ano de 2025, com nomes, notas e situações finais manuscritas.

O arquivo Excel inclui duas abas: `E_Fundamental` e `E_Fund_Verso`. Consulte `docs/MAPEAMENTO_MODELO.md` para os campos preliminarmente identificados. **Reabra e inspecione o modelo antes de codificar o gerador**; verifique merges, impressão e células. Não reproduza nomes verdadeiros de estudantes em código, testes, logs ou mensagens. Não suba as imagens ou históricos ao Git, nem os envie a serviços externos sem autorização expressa da escola e adequação à LGPD.

### Fatos confirmados no levantamento

- Frente `E_Fundamental`: 6º ano usa T (nota), U (carga horária); 7º V/W; 8º X/Y; 9º Z/AA.
- Linhas de disciplinas: Português 29; Inglês 30; Geografia 35; História 36; Ciências 40; Matemática 43; Arte/Educação Artística 44; Educação Física 46; Ensino Religioso 48.
- Verso `E_Fund_Verso`: `A3:A11` séries/anos escolares; `C3:C11` anos letivos; `E3:E11` unidade escolar; `M3:M11` município; `O3:O11` UF.
- O exemplar tem dados já preenchidos, **inclusive notas e anos de um estudante anterior**. Uma emissão nova não pode herdar esses valores sem confirmação.
- Há referências aparentemente divergentes à unidade escolar em `G7` e `H7` da frente. Pare e solicite/registre confirmação institucional da identificação correta; **não escolha por conta própria**.
- As fotos de atas têm cabeçalhos verticais e notas manuscritas, e podem apresentar transferência, aprovação, observações e exceções. Não pressupor que a ordem de disciplinas seja a mesma em anos distintos.

## 3. Stack e restrições

- Linguagem: Python 3.11+; interface: Streamlit; persistência local: SQLite; leitura de imagens: Pillow; geração XLSX: openpyxl, a partir de **cópia convertida** para XLSX.
- O `.xls` original deve permanecer intacto. Abrir/editar o original diretamente via openpyxl é inviável. Solicitar conversão supervisionada via Excel, preservando formatação, áreas de impressão, mesclagens, cabeçalhos e rodapés; comparar a aparência impressa com original.
- Exportação PDF apenas se houver caminho local testado (por exemplo, Excel instalado no Windows, ou conversor local avaliado). Se falhar, manter XLSX disponível e indicar o motivo; nunca gerar PDF visualmente desconfigurado de maneira silenciosa.
- Não requerer nuvem nem API paga para o fluxo básico. OCR manuscrito/visão deve ser plugável, **desabilitado por padrão**, e ativado somente mediante autorização e escolha consciente do fluxo de dados. Caso não haja leitura confiável, o operador digita ou corrige os valores manualmente.
- Evitar arquitetura excessiva. Código organizado, funções pequenas e testes unitários. Textos da interface, nomes de domínio e comentários preferencialmente em português.

## 4. Processo operacional obrigatório

1. Importar foto/arquivo da ata e registrar metadados: estabelecimento, ano letivo, ano escolar (6º–9º inicialmente), turma e turno.
2. Mostrar imagem original e tabela editável lado a lado. Permitir digitação manual; eventual OCR gera somente **candidatos não conferidos**, com a referência visual da linha e coluna.
3. Identificar ou cadastrar aluno via ID interno; nome semelhante não autoriza vínculo automático. Matrícula e nascimento, quando fornecidos, são auxiliares; não inventar dados ausentes.
4. Para cada estudante/ano, registrar componentes curriculares, notas, situação final literal da ata e observações; manter origem de cada valor.
5. Conferência explícita por um operador: comparar nome, série, ano, cabeçalho de disciplina, nota, status e foto. Qualquer edição posterior invalida a conferência do campo/registro correspondente.
6. Validar campos necessários do histórico e configurações oficiais da escola e da matriz curricular antes da emissão.
7. Criar novo XLSX baseado na cópia do modelo, com frente e verso. Preencher apenas células mapeadas, sem modificar o original; nunca herdar valores do exemplo antigo.
8. Conferir a visualização gerada e exportar separadamente em XLSX e PDF (se disponível). Nomear arquivos por ID interno e ano de emissão, evitando nome completo no nome do arquivo por padrão.
9. Registrar no banco operação de importação, edição, conferência e emissão, com data/hora e referência ao operador local, sem logs sensíveis em claro quando evitável.

## 5. Regras de segurança dos dados

- Dados pessoais de crianças/adolescentes: adotar princípio de minimização e confidencialidade. O MVP deve ser **local e de usuário único**, não ser exposto na rede pública. Sem prometer criptografia, autenticação ou controle multiusuário que ainda não existam.
- Segregar `dados/`, `modelos/` e `exports/` fora do controle de versão; verificar `.gitignore`. Nunca incluir o banco real, fotos reais, arquivos Excel reais, chaves ou tokens no repositório.
- Testes automatizados com nomes e notas **sintéticos**. Nada de dados reais em prompts enviados ao Codex, relatórios de erro, prints ou fixtures.
- Instruir a escola a usar conta do Windows autorizada, disco e backup protegidos e política de retenção adequada. Necessária avaliação institucional de privacidade antes de produção.
- Não enviar imagens para serviços OCR externos sem autorização escrita e análise de privacidade; criar interface de provedor OCR com implementação manual padrão.

## 6. Validações de domínio que devem bloquear erros

- Diferenciar nota ausente, nota ilegível, nota zero e status de transferência. Não substituir ausente por zero nem inventar nota.
- Aceitar entrada decimal com `,` ou `.`, preservar escala como decimal; faixa 0–10 apenas se confirmada como regra da escola (o protótipo assume provisoriamente). Nunca arredondar sem regra aprovada.
- Ano letivo ≠ ano escolar; 8º ano 2024 e 9º ano 2025 são exemplos, não uma sequência obrigatória de todos os alunos.
- Agrupar notas por disciplina normalizada a partir do **cabeçalho identificado**, jamais por índice numérico fixo da coluna da imagem.
- Duplicidade de aluno homônimo: exigir identificação humana; bloquear fusão silenciosa.
- Duplicidade de ata ou reimportação: apresentar aviso de possível duplicata, solicitar confirmação.
- Situação final (APROVADO, REPROVADO, TRANSFERIDO, TRANSFERIDA, OUTRO, PENDENTE) não determina automaticamente notas, conclusão ou direito a emitir documento. Não inferir situação final por média sem normas aprovadas.
- Não preencher filiação, data de nascimento, escola anterior, frequência ou carga horária por inferência; exigir outra fonte ou entrada validada.
- Configurações divergentes da escola e matriz curricular não devem ser decididas por heurística.
- Preencher o verso com trajetória escolar real por aluno, não copiar a sequência 2017–2025 do exemplar.
- Detectar se modelo/template já contém valores de aluno antigo; limpiar só regiões variáveis mapeadas com testes, preservando fórmulas e estilos.

## 7. Entregáveis e estrutura desejada

Utilize e amplie esta estrutura:

```text
SHE_Codex_Inicial/
├── main.py                    # Interface Streamlit inicial já disponível
├── requirements.txt
├── .gitignore
├── README.md
├── PROMPT_CODEX.md            # Este documento
├── she/
│   ├── __init__.py
│   ├── config.py              # Pastas locais
│   ├── banco.py               # SQLite/auditoria
│   ├── catalogo.py            # Disciplinas e mapeamento preliminar
│   ├── validacao.py           # Notas e consistência
│   ├── emissao.py             # Implementar geração fiel XLSX/PDF
│   ├── extracao.py            # Criar interface de extração manual/OCR opcional
│   └── revisao.py             # Criar validação, pendências e bloqueio
├── docs/
│   ├── MAPEAMENTO_MODELO.md
│   ├── CRITERIOS_ACEITE.md
│   └── PLANO_EXECUCAO.md
├── tests/
│   ├── test_validacao.py
│   ├── test_emissao.py         # Criar com workbook sintético
│   └── test_revisao.py        # Criar com dados sintéticos
├── dados/                     # Somente máquina autorizada, ignorada no Git
│   ├── atas/
│   └── referencias/
├── modelos/                   # Converter modelo para xlsx, ignorar no Git
└── exports/                   # Documentos gerados, ignorar no Git
```

Se o escopo exigir ajustes de arquitetura, explique resumidamente e mantenha a aplicação executável. Não montar infraestrutura em nuvem, Docker, fila, microsserviços ou autenticação corporativa sem necessidade.

## 8. Prioridades por etapa

**Entrega 1 — primeira execução**
- Instalar dependências e iniciar aplicativo.
- Testar importação da fotografia, cadastro do aluno, lançamento manual, referência à ata e conferência.
- Corrigir eventuais problemas existentes no esqueleto.

**Entrega 2 — motor de históricos**
- Fazer inspeção de modelo com arquivo real local; criar mapa configurável de células por versão de modelo.
- Limpar campos herdados de aluno anterior, sem apagar cabeçalhos/valores institucionais válidos.
- Gerar histórico XLSX usando dados fictícios conferidos, frente e verso individualizados.
- Impedir emissão se falta dado obrigatório, se não houver conferência ou se campos críticos de escola/carga horária não forem confirmados.
- Exportar PDF apenas após verificar fidelidade visual.

**Entrega 3 — melhoria de operação**
- Tabela de revisão por aluno/ano, lista de pendências, reimportação controlada, checagem de inconsistências e interface mais rápida.
- Implementar extração automática como sugestão opcional, somente se o provedor e as restrições de privacidade estiverem aprovados.

## 9. Testes mínimos obrigatórios

Crie testes automatizados com dados sintéticos que provem:

1. `7,5` = `7.5` no armazenamento; `0` não é ausência; nota ilegível bloqueia revisão.
2. Duas atas com ordens diferentes de disciplinas geram associação igual por rótulo.
3. Dois estudantes de mesmo nome não têm notas misturadas.
4. Um aluno de 8º ano 2024 tem notas somente na coluna X; 9º ano 2025 somente Z.
5. Células de anos não pertencentes ao aluno não herdam dados do exemplar (inclusive verso).
6. Status `TRANSFERIDO`/`TRANSFERIDA` não vira valor numérico.
7. Aluno sem revisão ou com documento de identificação incompleto não pode ser emitido.
8. Gerador preserva layout, mesclagens essenciais e carga horária validada em workbook de teste.
9. Corrigir qualquer nota após conferência exige conferir novamente.
10. Reimportar uma ata semelhante não cria lançamentos duplicados sem aviso.

Execute `python -m unittest discover -s tests -v` e, se houver suíte adicional, execute-a também. Não basta afirmar que os testes passaram: informe quantos passaram e quais falharam.

## 10. Relato de conclusão esperado

Quando terminar um incremento, entregue:

- O que está implementado **de verdade** e pode ser testado agora.
- O que continua como protótipo/manual/pendência (OCR, PDF etc.).
- Arquivos alterados e comandos exatos para rodar no Windows PowerShell.
- Testes executados e seus resultados.
- Bloqueios que exigem decisão da secretaria (escola correta, matriz curricular, dados obrigatórios, autorização de privacidade).

**Aja agora:** leia os arquivos do projeto, rode os testes, identifique pendências e implemente a primeira melhoria útil. Priorize a emissão XLSX correta e verificável em vez de construir OCR complexo de caligrafia no primeiro ciclo. Não solicite confirmação desnecessária para tarefas internas de programação, mas interrompa a emissão oficial quando regras escolares ou dados pessoais não forem comprovados.

## 11. Continuidade com a conversa

Esta conversa no ChatGPT é usada pelo responsável para planejamento e revisão, mas **não assuma que você (Codex) consegue ler automaticamente a conversa ou seus anexos**. As regras resumidas encontram-se neste documento e em `docs/DECISOES.md`. Atualize `docs/DECISOES.md` ao final de cada etapa relevante e sinalize ao usuário decisões pendentes que ele poderá discutir no ChatGPT. Não substitua regras escolares oficiais por uma opinião do assistente.
