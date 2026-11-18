# SHE — Sistema de Históricos Escolares

Este repositório é um **ponto de partida funcional**, não um sistema pronto para emissão oficial.

## Escopo entregue neste pacote

- Interface local em Streamlit.
- Importação de fotografias JPG/PNG de atas (sem extração automática nesta versão).
- Cadastro de alunos por ID, com matrícula opcional.
- Lançamento manual de notas por disciplina e situação final, vinculados à ata.
- Visualização da imagem de origem e registro explícito de conferência.
- Banco local SQLite e testes iniciais para notas decimais.
- Módulo de emissão definido como contrato, **a implementar pelo Codex**.

## Executar no Windows (PowerShell)

Instale Python 3.11 ou 3.12, descompacte este pacote e abra o terminal na pasta `SHE_Codex_Inicial`:

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m streamlit run main.py
```

O navegador abrirá a interface local. Para rodar os testes:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

## Continuar com Codex

1. Abra a pasta deste projeto no Codex (aplicativo, extensão no VS Code ou CLI instalada).
2. Forneça as instruções de `PROMPT_CODEX.md`.
3. Copie o `.xls` original da escola para `dados/referencias/` **somente no computador autorizado**, sem versioná-lo.
4. Copie fotos de atas para `dados/referencias/` apenas com autorização institucional. Para desenvolver e testar, prefira cópias anonimizadas.
5. Siga `docs/PLANO_EXECUCAO.md` e `docs/CRITERIOS_ACEITE.md`.

**ATENÇÃO:** a interface inicial não tem autenticação ou criptografia própria. Não colocar em produção com dados reais sem validar controles de acesso, armazenamento, backup, procedimentos e autorização institucional.

## Formato do modelo

O arquivo recebido é `.xls` (legado). Para a emissão com `openpyxl`, é necessária uma cópia **convertida para `.xlsx`**, preservando o original. A conversão deve ser verificada visualmente (células mescladas, quebras de página, layout impresso, frente e verso). Não salvar a planilha com notas de aluno de exemplo como se fosse um template vazio.

## Documentos de apoio

- `PROMPT_CODEX.md`: instrução principal para o agente Codex.
- `docs/MAPEAMENTO_MODELO.md`: campos e posições identificados no arquivo enviado.
- `docs/PLANO_EXECUCAO.md`: implementação priorizada para cerca de dois dias de trabalho concentrado.
- `docs/CRITERIOS_ACEITE.md`: critérios objetivos para aprovar a entrega.

## Continuidade entre Codex e conversa

Esta conversa no ChatGPT será a base de revisão e planejamento. O Codex não recebe automaticamente os anexos da conversa: mova arquivos somente para o ambiente autorizado e mantenha `docs/DECISOES.md` atualizado para evitar perda de contexto.
# Incremento de 17/11/2026

**Atualização de 18/11/2026:** instalação local retomada por solicitação do usuário. Ollama 0.40.16 e modelos de visão Qwen 3.5 estão disponíveis. Ambos os testes reais (4b e 0.8b) expiraram em cinco minutos neste hardware. Leitura automática ainda não operacional; tabela manual disponível. Para iniciar o sistema e o serviço local, execute `./iniciar.ps1`. Consulte o estado atualizado em `docs/LEITURA_LOCAL.md`.

**Leitura da ata inteira:** abra a nova aba **2. Ler ata inteira**. A integração com IA local (Ollama + qwen2.5vl:3b) preenche um rascunho com nome, notas e situação dos estudantes. Instalação e operação estão em [docs/LEITURA_LOCAL.md](docs/LEITURA_LOCAL.md). O usuário escolheu configurar o leitor em outro computador mais potente; não há modelo instalado ou acurácia em manuscritos validada nesta máquina. Nenhum serviço externo é usado.

A tabela permite corrigir e adicionar estudantes, salvar rascunho e selecionar IDs existentes ou novos cadastros explicitamente. Após importar, os resultados seguem não conferidos. É possível usar a tabela manualmente mesmo sem modelo local.

Atualização: é possível selecionar várias fotos de uma vez. Abra cada foto, informe o ano letivo e a série conforme o cabeçalho e marque a confirmação; depois clique em **Importar fotos conferidas**. Os dados não são lidos automaticamente. O resultado aparece por foto, incluindo duplicatas e pendências.

Na aba de emissão, o histórico consolidado reúne resultados de diferentes atas pelo ID do estudante e sinaliza conflito entre atas da mesma série. O motor XLSX já possui testes sintéticos; a emissão pelo modelo real ainda depende de homologação e cadastro documental completo. A cópia convertida fica em `modelos/modelo_inspecao.xlsx` e não deve ser distribuída como modelo limpo, pois contém dados do exemplar.

Para iniciar no PowerShell, dentro desta pasta:

```powershell
.\.venv\Scripts\python.exe -m streamlit run main.py
```

Abra http://127.0.0.1:8501. Também é possível executar `./iniciar.ps1`.

Para testar o domínio e o banco com dados fictícios:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

O lançamento manual permite consultar a imagem ao lado e editar notas anteriores.
Conferência incompleta é bloqueada; alterações invalidam a conferência anterior.
Fotografia idêntica é rejeitada como duplicata. Emissão XLSX/PDF e OCR ainda não disponíveis.

