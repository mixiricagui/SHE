# Critérios de aceite

## Operação

- [ ] Programa inicia localmente com instruções reproduzíveis no Windows.
- [ ] Foto é importada e pode ser visualizada para conferência lado a lado.
- [ ] Aluno é identificado por ID interno, sem associação silenciosa por nome semelhante.
- [ ] Ano letivo, ano escolar, turma, turno e situação final são preservados independentemente.
- [ ] Nomes de disciplinas são mapeados por rótulo, nunca apenas por índice de coluna.
- [ ] Nota vazia, ilegível e `0` são distinguíveis.
- [ ] Formato `7,5` permanece nota 7,5, sem arredondamento implícito.
- [ ] `TRANSFERIDO`, `TRANSFERIDA` e observações não são tratados como nota.
- [ ] Importação não aprova dados automaticamente; qualquer edição posterior invalida conferência anterior.

## Emissão

- [ ] Apenas aluno/ano/série corretos são exportados.
- [ ] Notas de exemplo do modelo foram removidas dos campos variáveis, e não vazaram para documento final.
- [ ] Frente e verso estão vinculados ao mesmo estudante.
- [ ] Células de disciplinas preservam a posição correta para 6º, 7º, 8º e 9º anos.
- [ ] Ano letivo e estabelecimento no verso refletem registros próprios do aluno, não valores herdados.
- [ ] Escola e carga horária foram confirmadas por pessoa autorizada.
- [ ] Exportação falha de modo seguro se faltarem informações obrigatórias ou houver conflito.
- [ ] PDF preserva layout e quebras de página, se emissão PDF estiver habilitada.

## Segurança e rastreabilidade

- [ ] Todos os testes usam dados fictícios.
- [ ] Arquivos pessoais e banco SQLite não são adicionados ao Git.
- [ ] Não existem chamadas para serviços externos sem autorização explícita.
- [ ] Eventos de importação, edição, conferência e emissão são auditáveis.
- [ ] Operador pode rever a foto e corrigir a nota antes da emissão.

## Teste de regressão

- [ ] 8º ano de 2024 e 9º ano de 2025 usando nomes fictícios e notas inventadas.
- [ ] Dois estudantes homônimos não têm seus resultados misturados.
- [ ] Disciplina trocando de coluna entre duas atas não altera a atribuição.
- [ ] Nota 0 é preservada; nota vazia não vira zero.
- [ ] Reimportação de imagem não duplica silenciosamente registros.
