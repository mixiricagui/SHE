# Registro de decisões — SHE

## 2026-11-18 — Continuação da instalação no computador atual

O usuário substituiu a preferência anterior por outro computador e autorizou instalar tudo neste PC. Na retomada, Ollama 0.40.16 e `qwen3.5:4b` já estavam instalados. A API local confirmou capacidade de visão. Integração ampliada para esse modelo, com `think=false` e contexto 4096. Teste real com imagem fictícia de duas linhas não retornou em 302,4 segundos. Modelo descarregado via `ollama stop`.

Escolhida a alternativa local menor `qwen3.5:0.8b` para avaliação, mantendo revisão obrigatória e sem prometer precisão em manuscritos. O modelo maior não foi removido. `iniciar.ps1` passou a iniciar o Ollama local se o serviço estiver ausente. O download de `qwen2.5vl:3b` foi evitado, pois já havia um modelo visual e pouco espaço livre.

Resultado: download de `qwen3.5:0.8b` concluído com verificação SHA-256. O teste de leitura da mesma imagem fictícia também expirou, após 301,7 segundos, sem tabela retornada. Instalação disponível, mas reconhecimento local NÃO validado como operacional neste hardware. Nenhuma foto de aluno real foi usada. Suíte do aplicativo: 40 testes passaram, zero falhas; isso não equivale a sucesso de inferência. Diagnóstico local em `dados/teste_leitor/diagnostico.json`.

## 2026-11-17 — Leitura de toda a ata com revisão em tabela

O usuário solicitou a leitura de todos os nomes, notas, situação, ano e série presentes na fotografia. Após a verificação de aproximadamente 4 GB de RAM e ausência de Ollama/Tesseract, escolheu explicitamente manter o processamento local e configurar o leitor em outro computador mais potente. Não instalar modelos pesados nesta máquina nem habilitar serviços externos.

Implementada integração local experimental com Ollama/qwen2.5vl:3b, endpoint fixo de loopback, sem proxies/redirecionamentos e sem modelos cloud. A ativação na interface é explícita. A IA sugere cabeçalho e estudantes; notas são associadas pelo rótulo. Valores ilegíveis/ausentes não viram zero; componentes desconhecidos ou duplicados ficam visíveis para resolução.

Nova aba **Ler ata inteira**: imagem ao lado de tabela editável, inclusão de linhas omitidas, persistência do rascunho, correção humana de cabeçalho com invalidação de conferências, indicação explícita de aluno existente ou novo, confirmação da versão atual da tabela antes do salvamento. Homônimos nunca são ligados automaticamente. A importação é transacional e rejeita reenvios de mesma linha ou sobrescrita de resultados existentes. Notas importadas continuam não conferidas. A situação literal e referência visual são preservadas em tabela própria.

Tabelas novas: `rascunhos_atas` e `linhas_importadas`, no SQLite local ignorado no Git. Rascunhos guardam a resposta original para rastreabilidade e precisam da mesma proteção dos demais dados pessoais. Não foram usadas fotos reais nos testes nem enviada imagem a serviço externo. Inferência real e acurácia manuscrita permanecem pendentes do computador de destino. Consulte `docs/LEITURA_LOCAL.md`.

Verificação final: `.\.venv\Scripts\python.exe -m unittest discover -s tests -v` — 39 testes passaram, zero falhas. Inclui contrato HTTP local com resposta simulada, extração por rótulo, revisão, rollback de lote, preservação de homônimos, reenvio, alteração de cabeçalho e importação pela nova interface via AppTest. Este resultado não comprova reconhecimento real de manuscritos.

## 2026-11-17 — Lote de fotografias e motor XLSX

Solicitação do usuário: enviar várias fotografias juntas, pois cada ata identifica ano e série, e avançar para a geração do histórico.

Implementado upload múltiplo com imagem, ano letivo, série, turma, turno e confirmação por foto. Não há inferência de metadados nem OCR. Falhas são informadas por item; imagens válidas são importadas, duplicatas exatas são rejeitadas e arquivos temporários rejeitados são removidos. O cadastro de alunos permanece por ID, sem vincular homônimos automaticamente.

A tela de emissão agora mostra resultados consolidados por estudante e série, com referência à ata e ano letivo. Mais de uma ata por série é exibida como conflito, sem escolher automaticamente a mais recente. O escopo de lançamento segue 6º–9º; as séries iniciais do modelo ficam sem dados enquanto não houver fonte e suporte próprio.

Criada cópia `modelos/modelo_inspecao.xlsx` pelo Excel local, com original XLS aberto somente para leitura, macros e atualização de links desativadas. Inspeção estrutural confirmou mesclagens e posições dos dados; ambas as abas não têm área de impressão definida. A cópia contém os dados do exemplar e permanece ignorada no Git. Não foi feita validação visual de impressão.

Motor puro `gerar_xlsx`: valida revisão, identificação, escola, escala, cargas, componentes e conflitos; confere hash do modelo homologado, limpa regiões mapeadas sem apagar fórmulas e escreve em células autorizadas. Testado com workbook inteiramente sintético. O mapa real está em rascunho não aprovado, inclusive pendências de campos mistos, totais e rodapé. O motor ainda não está ligado a um botão de emissão oficial. PDF continua indisponível.

Validação final: `.\.venv\Scripts\python.exe -m unittest discover -s tests -v` — 26 testes passaram, zero falhas, incluindo importação parcial, reenvio, consolidação, homônimos, limpeza e posicionamento XLSX, preservação de estilos/mesclagens/fórmulas e inicialização da interface com aluno fictício. Teste de interface via AppTest; upload interativo e impressão visual ainda não verificados. Streamlit apresentou avisos de depreciação de `use_container_width`, sem exceções.

## 2026-11-17 — Primeiro incremento executável

Recuperado o contexto da conversa “Automatizar históricos escolares”. Projeto extraído do ZIP para esta pasta. A emissão XLSX continua pendente de inspeção do modelo real convertido e confirmação institucional; nenhum documento oficial foi gerado.

Implementados: validação também no banco, identificação de disciplinas por rótulo, bloqueio de conferência incompleta, invalidação integral da conferência após edição, fechamento explícito das conexões SQLite, detecção por SHA-256 de fotografia idêntica, fotografia ao lado do formulário e recuperação de notas anteriores. Situações especiais podem ser armazenadas, mas a conferência final permanece bloqueada até definição das regras.

A detecção de duplicatas é exata, não identifica recortes ou fotografias diferentes da mesma ata. O índice atende importações novas; registros legados sem hash não são comparados. OCR, operador identificado na auditoria, confirmação de matriz/escala, revisão de identificação e motor XLSX/PDF permanecem pendentes. O servidor está limitado a 127.0.0.1 e a telemetria do Streamlit foi desativada.

Os anexos da conversa anterior foram localizados em arquivos temporários. Ainda não foram copiados nem alterados. Próximo incremento: inspecionar o XLS, produzir cópia XLSX preservando impressão e validar o mapeamento antes de implementar o gerador.

Validação do incremento: `python -m unittest discover -s tests -v`: 15 testes passaram, zero falhas. A primeira tentativa no sandbox falhou por falta de acesso à pasta temporária; a execução autorizada fora do sandbox passou. `python -m py_compile main.py she/banco.py she/revisao.py` também passou.

Dependências instaladas em `.venv`. A inicialização da interface foi validada com `streamlit.testing.v1.AppTest` fora do sandbox, sem exceções. Não foi realizada validação visual no navegador nem teste completo de upload pela interface.

Este arquivo mantém no repositório as decisões aprovadas nesta conversa. O Codex deve atualizá-lo ao fazer mudanças arquiteturais relevantes, incluindo data, decisão, motivação e impacto. Não colocar dados identificáveis de alunos aqui.

## Decisões estabelecidas

| Área | Decisão | Justificativa |
|---|---|---|
| Produto | Criar programa local próprio | Uso recorrente pela secretaria, conferência e padronização |
| Trabalho | Utilizar Codex para implementar; ChatGPT para planejamento, revisão e critérios | Processo contínuo com histórico de decisões |
| Prazo | Meta de protótipo MVP em aproximadamente dois dias de trabalho concentrado, sem garantia de uso oficial | Leitura manuscrita e validação exigem revisão |
| Stack inicial | Python + Streamlit + SQLite | Iteração rápida em Windows e sem infraestrutura em nuvem |
| Entrada | Foto de ata com transcrição manual como caminho garantido | Cursiva manuscrita pode ser interpretada incorretamente |
| OCR | Opcional, implementado como módulo separado, desativado inicialmente | Proteção de dados e incerteza da leitura |
| Revisão | Conferência humana obrigatória, edição posterior invalida conferência | Evitar erros no documento oficial |
| Saída | XLSX fiel ao modelo; PDF apenas após teste de fidelidade | Preservação de frente/verso e impressão |
| Integração Excel | Preservar original `.xls`; trabalhar com cópia `.xlsx` verificada | Compatibilidade e integridade do modelo |
| Identificação | IDs internos para alunos e atas, não apenas comparação por nome | Evitar confundir homônimos |
| Dados | Dados pessoais apenas em máquina autorizada; sem Git ou nuvem automática | Sigilo e princípios da LGPD |

## Decisões pendentes da secretaria

- [ ] Confirmar nome oficial do estabelecimento diante das referências diferentes encontradas no modelo.
- [ ] Confirmar grade curricular/carga horária por ano, regras de avaliação e critérios de emissão.
- [ ] Definir quais fontes contêm data de nascimento, filiação, matrícula e demais informações não presentes nas atas.
- [ ] Definir tratamento de transferências, reclassificação, EJA, estudos anteriores e observações.
- [ ] Validar procedimento de assinatura, emissão e arquivamento de históricos.
- [ ] Autorizar uso dos dados reais no computador e decidir se algum OCR externo pode ser usado.

## Modelo de nova decisão

### AAAA-MM-DD — Assunto

**Decisão:** ...

**Motivação:** ...

**Impacto no código e na operação:** ...
