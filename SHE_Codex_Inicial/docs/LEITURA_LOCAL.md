# Leitura da ata inteira no computador mais potente

## Atualização de 18/11/2026 — instalação neste PC

**Estado final:** Ollama e os modelos `qwen3.5:4b` e `qwen3.5:0.8b` estão instalados. Ambos excederam cinco minutos no teste com uma pequena ata fictícia, sem devolver tabela. A leitura automática ainda não ficou operacional neste PC. Cadastro, importação de fotos e revisão manual continuam disponíveis. Os 40 testes de código passaram, mas não comprovam precisão nem desempenho de OCR.

O usuário mudou a decisão e autorizou instalar tudo neste computador. Ollama 0.40.16 está instalado e o modelo `qwen3.5:4b` já estava disponível. O teste real com uma ata fictícia ultrapassou cinco minutos sem resposta; o modelo foi descarregado para liberar memória. A versão menor `qwen3.5:0.8b` foi incluída como opção experimental. O aplicativo continua aceitando `qwen2.5vl:3b` para instalações anteriores, mas ele não foi baixado neste PC.

Para abrir o sistema nesta máquina, execute `./iniciar.ps1` na pasta do projeto. O iniciador também tenta iniciar o serviço local se necessário. Na aba **Ler ata inteira**, selecione o modelo instalado. Contexto reduzido para 4096 tokens, sem raciocínio estendido nos modelos Qwen 3.5. Ata longa pode ultrapassar a capacidade de uma chamada e precisa de revisão de completude.

As instruções abaixo são mantidas para reinstalação em outro computador. Para instalar a alternativa menor, substitua o comando de download por `ollama pull qwen3.5:0.8b`. Nenhum modelo foi habilitado para uso em nuvem.

O SHE tem uma integração experimental com Ollama e `qwen2.5vl:3b`. A precisão em atas manuscritas ainda não foi validada. Os testes automatizados usam respostas simuladas e não provam acurácia de OCR. O computador atual tem cerca de 4 GB de RAM; por escolha do usuário, a instalação do modelo será realizada em outra máquina. Nenhuma foto real foi processada nesta implementação.

## Preparar o Windows de destino

1. Copie o projeto para o computador autorizado. Não copie `.venv`: recrie o ambiente Python nele. Se for transferir o banco e as fotos reais, use o procedimento de transporte protegido da escola. Os caminhos das atas antigas são absolutos; a transferência de acervo existente ainda requer migração, portanto valide primeiro com imagens fictícias importadas no computador de destino.
2. Instale Python 3.11+ e o [Ollama para Windows](https://ollama.com/download/windows).
3. Na pasta do projeto, execute:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

4. Feche o Ollama da bandeja do Windows caso esteja rodando. Em um PowerShell, dentro do projeto, inicie o servidor sem funções de nuvem:

```powershell
.\scripts\iniciar_leitor_local.ps1
```

5. Em outro PowerShell, baixe o modelo (aproximadamente 3,2 GB; precisa de internet apenas para a instalação):

```powershell
ollama pull qwen2.5vl:3b
ollama list
```

6. Inicie o SHE no mesmo computador:

```powershell
.\.venv\Scripts\python.exe -m streamlit run main.py
```

O servidor aceita apenas conexões locais. Não exponha portas na rede. O SHE usa endereço fixo `127.0.0.1:11434`, desativa proxies e redirecionamentos HTTP e só permite o modelo local indicado. Não oferece provedor cloud, campo de API key ou upload externo. A necessidade de memória e o tempo de execução deverão ser medidos no computador de destino; o arquivo do modelo não representa toda a RAM necessária.

## Usar

Importe as fotos. Abra **2. Ler ata inteira**, selecione uma ata, ative a leitura local e clique em **Ler nomes, notas e situações da foto**. A ativação vem desmarcada.

A leitura mostra sugestões de ano/série e uma tabela editável de todos os estudantes encontrados. Ela pode omitir linhas ou confundir caligrafia: compare a quantidade de alunos e cada linha com a fotografia. Campos ilegíveis ficam vazios ou conservam a transcrição inválida para correção. A tabela aceita adicionar linhas que faltaram.

Confira disciplinas não mapeadas, copie cada nota para a disciplina correta e apague o aviso somente após resolvê-lo. Para cada estudante escolha um ID existente (consulte a lista) OU marque **Criar novo aluno**. Nenhum nome é associado automaticamente. Marque **Revisado na foto** e **Importar** apenas nas linhas corrigidas. Confirme o cabeçalho e clique em **Importar alunos e resultados selecionados**.

O salvamento é atômico: um erro em qualquer linha selecionada impede todo o envio. Reenviar a mesma linha não duplica alunos nem sobrescreve resultados. Os dados importados permanecem NÃO CONFERIDOS para a etapa final. Se houver erro depois de importar, use **4. Lançar notas** para corrigir; não renumere linhas para forçar nova importação.

**Salvar rascunho da tabela** preserva o trabalho no banco local. Refazer a leitura exige marcar a substituição do rascunho; erros do leitor preservam a versão anterior. Rascunhos podem conter dados pessoais e seguem as mesmas regras de proteção e retenção do banco.

## Limites desta versão

- Uma ata por chamada; os uploads continuam em lote.
- 6º–9º ano, máximo de 200 linhas por resposta, imagem até 20 MB.
- O leitor pode falhar ou entregar uma tabela incompleta mesmo com JSON válido. Não há garantia de reconhecimento de cursiva nem detecção de todas as omissões.
- Sem precisão medida em manuscritos reais, sem instalação do modelo neste computador e sem teste de inferência real neste incremento.
- Emissão oficial e PDF continuam bloqueados pelas pendências documentais anteriores.

Referências técnicas: [API de visão](https://docs.ollama.com/capabilities/vision), [modelo](https://ollama.com/library/qwen2.5vl:3b), [modo somente local](https://docs.ollama.com/faq#how-do-i-disable-ollamas-cloud-features).
