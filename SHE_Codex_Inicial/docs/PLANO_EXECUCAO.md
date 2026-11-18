# Plano de execução — MVP (meta: 2 dias de trabalho concentrado)

Este é um objetivo de escopo, não um prazo garantido para publicação nem autorização de uso oficial.

## Dia 1 — fluxo de dados e revisão

1. Validar ambiente Windows, executar `unittest` e iniciar Streamlit.
2. Revisar o modelo e mapear células/campos variáveis, inclusive as mescladas.
3. Confirmar banco de dados: aluno por ID, ata por ID, matrícula/ano/turma e resultados associados.
4. Acrescentar etapa de extração opcional com contrato de provedor (`extratores/`), guardando a imagem e a transcrição bruta. Se serviço externo não autorizado, deixar OCR desativado e usar entrada manual.
5. Tela de pré-visualização da imagem ao lado de tabela editável de candidatos; não imputar dados ilegíveis.
6. Impedir duplicidade de ano/serie, aluno/turma, nome semelhante e notas fora de escala.

## Dia 2 — histórico e testes

1. Converter cópia do `.xls` para `.xlsx` (Excel instalado ou conversão supervisionada), mantendo original intacto.
2. Implementar gerador de XLSX com base no mapeamento das células, protegendo formatação, mesclagens e fórmulas.
3. Não transportar dados de aluno de exemplo do arquivo-base para saída final.
4. Escrever verso por ano letivo e escola informados para cada estudante; sem preenchimento automático por progressão presumida.
5. Bloquear emissão diante de notas/disciplinas obrigatórias não conferidas, status não resolvido ou escola não confirmada.
6. Implementar exportação PDF se houver mecanismo local aprovado; caso contrário, deixar XLSX pronto e apresentar como limitação.
7. Testes com nomes e notas fictícias, emissão de pelo menos um histórico de teste e conferência visual frente/verso.

## Pós-MVP

- Processamento em lote com histórico de cada documento.
- OCR/visão aperfeiçoado para manuscritos, se tecnicamente viável e aprovado quanto à proteção de dados.
- Perfis de acesso, backups automatizados, política institucional de retenção e logs operacionais.
- Integração com cadastro escolar existente, se autorizado.
