# 📑 Documentação Técnica – CNH Validation Workflow

Este documento detalha o funcionamento técnico do workflow de validação de identidade via CNH, implementado em **Python** e orquestrado na plataforma **Windmill**. O projeto utiliza as APIs da **mostQI** para realizar a extração de dados, validação de QR Code, verificação de vivacidade e comparação facial.

---

## 🔍 Visão Geral

O fluxo automatiza a validação de documentos e biometria por meio de 10 etapas organizadas sequencialmente. Cada etapa corresponde a uma atividade crítica na jornada de validação, envolvendo:

- Upload e processamento da CNH (frente e verso)
- Extração de dados via OCR e QR Code
- Verificação de vivacidade via vídeo
- Comparação facial entre CNH e vídeo
- Consolidação de resultado com score final de validação

O workflow foi desenvolvido diretamente no **Windmill**, combinando scripts Python (`action`), formulários (`suspend`) e aprovações (`approval`) com controle de estado e feedback contínuo ao usuário.

---

## 🧱 Estrutura dos Steps

Os scripts estão organizados na pasta `windmill_workflow/steps/`, numerados conforme a ordem de execução. Abaixo, um detalhamento técnico de cada etapa:

---

### 1. `00_boas_vindas.py`
- **Tipo**: Formulário (suspend)
- **Função**: Apresenta o fluxo ao usuário com orientações iniciais e requisitos do processo.
- **Entrada**: Nenhuma
- **Saída**: Mensagem introdutória com instruções e botão para prosseguir.

---

### 2. `01_upload_cnh_frente.py`
- **Tipo**: Formulário (suspend)
- **Função**: Permite upload da imagem da frente da CNH.
- **Entrada**: Upload do arquivo de imagem (`cnh_image_file`)
- **Saída**: Arquivo utilizado na etapa seguinte.

---

### 3. `02_processar_cnh_frente_idp.py`
- **Tipo**: Script (action)
- **Entradas**:
  - `client_key: str`
  - `cnh_image_file: file`
- **Função**: Autentica via JWT, envia imagem à API `/process-image/content-extraction`, extrai dados como nome, CPF, data de nascimento, validade e categoria.
- **Saída**: JSON estruturado com dados extraídos da CNH e status da operação.

---

### 4. `03_upload_cnh_qrcode.py`
- **Tipo**: Formulário (suspend)
- **Função**: Permite upload da imagem do verso da CNH com o QR Code.
- **Entrada**: Upload do arquivo (`qr_image_file`)
- **Saída**: Arquivo utilizado na próxima etapa.

---

### 5. `04_processa_cnh_qrcode_vio.py`
- **Tipo**: Script (action)
- **Entradas**:
  - `client_key: str`
  - `qr_image_file: file`
- **Função**: Autentica e envia o arquivo à API `/process-image/vio-extraction` para extrair dados criptografados do QR Code.
- **Saída**: JSON com os dados extraídos do QR Code, status e comparativos iniciais.

---

### 6. `05_liveness_get_link_start.py`
- **Tipo**: Script (action)
- **Entrada**:
  - `client_key: str`
- **Função**: Gera um link de sessão assíncrona para verificação de vivacidade usando a API `/liveness/streaming/async`.
- **Saída**: `sessionUrl`, `processId`, e metadados da sessão.

---

### 7. `06_instrucoes_liveness.py`
- **Tipo**: Aprovação (approval)
- **Entrada**:
  - `session_url: str`
- **Função**: Mostra o link da sessão para o usuário iniciar a verificação. O botão "Cancel" redireciona para o link. Aguarda o usuário completar o processo.
- **Saída**: Nenhuma direta; controle de fluxo via Windmill.

---

### 8. `07_verifica_status_liveness.py`
- **Tipo**: Script (action)
- **Entradas**:
  - `client_key: str`
  - `process_id: str`
- **Função**: Consulta o status da sessão de vivacidade. Retorna status atual, tempo estimado, erros e resultado da prova de vida.
- **Saída**: Resultado booleano (`aprovado_liveness`), score, e mensagens auxiliares.

---

### 9. `08_compara_faces_facematch.py`
- **Tipo**: Script (action)
- **Entradas**:
  - `client_key: str`
  - `face_file_a: file` (ex: rosto extraído da CNH)
  - `face_base64_b: str` (frame do vídeo)
- **Função**: Realiza comparação facial entre duas imagens utilizando a API `/face-match/compare`.
- **Saída**: Score de similaridade (0–100), status de aprovação (`True/False`), logs de erro.

---

### 10. `09_validacao_final.py`
- **Tipo**: Script (action)
- **Entradas**:
  - Dados extraídos da frente da CNH
  - Dados do QR Code
  - Score e status do Liveness
  - Score e status do FaceMatch
- **Função**: Realiza validação cruzada dos dados (ex: nome, CPF, nascimento), calcula score geral, gera relatório final e exibe status de aprovação.
- **Saída**: JSON com estrutura clara de resultado, pontuação final, campos validados e explicações em Markdown.

---

## 🔐 Integrações e Segurança

- Autenticação com a API da mostQI é feita via **JWT**, com geração dinâmica baseada na `client_key`.
- Dados sensíveis (como imagens, vídeos e informações pessoais) são tratados apenas em **memória transitória**.
- Nenhuma informação pessoal é armazenada ou persistida no repositório.
- Webhooks podem ser integrados para automações externas (não habilitado por padrão).

---

## ⚙️ Considerações Técnicas

- Linguagem: **Python 3.10+**
- Bibliotecas utilizadas:
  - `requests` – para requisições HTTP
  - `python-dotenv` – para gerenciamento de chaves de ambiente
  - `dataclasses`, `typing`, `mimetypes`, `base64`, `logging`
- Todos os scripts seguem padrão modular com logging estruturado, tratamento de exceções e entradas tipadas.
- O fluxo foi testado com múltiplos inputs e lida com falhas de rede, imagens corrompidas e tokens inválidos.

---

## 📈 Extensibilidade

Este fluxo pode ser adaptado para:

- Validação de outros documentos (ex: RG, passaporte)
- Integração com sistemas internos de KYC
- Geração de relatórios automatizados via Webhook ou S3

---

Para dúvidas técnicas, consulte o [README.md](../README.md) ou entre em contato com o desenvolvedor.

---
**Desenvolvido por:** José Carlos Miranda Leite  
GitHub: [@JCZerf](https://github.com/JCZerf) • Email: josecarlosmrlt@outlook.com  
