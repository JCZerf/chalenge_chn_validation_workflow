# CNH Validation Workflow - Visão Geral do Fluxo no Windmill

Este workflow automatiza a validação de uma CNH (Carteira Nacional de Habilitação) utilizando as APIs da mostQI, integradas 100% via Windmill. O fluxo completo abrange captura e validação de dados da CNH, leitura do QR Code, verificação de prova de vida e comparação facial.

## 🧩 Estrutura Geral do Workflow

O processo está dividido em 10 etapas organizadas sequencialmente:

---

### 1. 🟢 Tela de Boas-vindas (`01_boas_vindas.json`)
Apresenta uma interface amigável explicando ao usuário o objetivo da validação. Inclui instruções iniciais e um botão para iniciar o processo.

---

### 2. 📸 Upload da Frente da CNH (`02_upload_frente_cnh.json`)
Formulário para o usuário enviar uma imagem legível da frente da CNH. Esta imagem será usada na extração dos dados via API IDP.

---

### 3. 🧠 Extração de Dados da CNH - IDP (`03_extrair_dados_frente.py`)
Script que consome a API **/process-image/content-extraction** da mostQI para extrair informações da frente da CNH (nome, CPF, data de nascimento, validade, etc.). O resultado é armazenado para validações posteriores.

---

### 4. 📤 Upload do Verso da CNH (QR Code) (`04_upload_verso_cnh.json`)
Formulário para envio da imagem do verso da CNH contendo o QR Code criptografado.

---

### 5. 🔍 Validação do QR Code - VIO (`05_validar_qrcode.py`)
Consome a API **/process-image/vio-extraction** da mostQI para decodificar e validar os dados do QR Code. Os dados extraídos são comparados com os obtidos na etapa 3.

---

### 6. 🎥 Upload do Vídeo de Prova de Vida (`06_upload_video.json`)
Formulário para envio do vídeo de vivacidade (liveness) necessário para análise biométrica.

---

### 7. 🧬 Verificação de Liveness (`07_liveness.py`)
Inicia o processo assíncrono via API **/liveness/streaming/async**, recebendo um `sessionUrl` para o usuário realizar o teste de vivacidade. O `processId` é armazenado para consulta posterior.

---

### 8. ✅ Confirmação de Execução do Liveness (`08_confirmacao_liveness.json`)
Tela de aprovação no Windmill que apresenta o link da sessão de vivacidade ao usuário. O processo fica suspenso até que ele complete a verificação. O botão de **Cancel** redireciona para o `sessionUrl`.

---

### 9. 🧑‍🦲 Comparação Facial (FaceMatch) (`09_facematch.py`)
Script que consome a API **/face-match/compare** da mostQI para verificar se a face da CNH e do vídeo/QR Code pertence à mesma pessoa.

---

### 10. 🧾 Resultado Final (`10_resultado_final.py`)
Consolida todos os dados das etapas anteriores, calcula o **score da validação** e exibe um relatório final com os status de:
- Comparação de dados (frente x QR Code)
- Validação de Liveness
- Resultado do FaceMatch

A saída contém uma pontuação final e uma mensagem de aprovação ou reprovação.

---

## 📌 Observações Técnicas

- Todas as chamadas às APIs utilizam autenticação JWT dinâmica, gerada em tempo real com base na `client_key` do usuário.
- O projeto segue padrão de entrada e saída compatível com o Windmill (`# wm-input`).
- Todos os scripts lidam com tratamento de erros e mensagens claras para o usuário final.

---

## 📂 Localização dos arquivos

Todos os scripts, formulários e aprovações estão na pasta `windmill_workflow/steps/`, numerados conforme a sequência do fluxo.

---

## 🏁 Resultado Esperado

Ao final do fluxo, o usuário recebe uma tela com resumo da validação da CNH, destacando:
- Validação dos dados extraídos
- Status da vivacidade
- Resultado do FaceMatch
- Pontuação geral da validação

---

Este fluxo foi construído com foco em segurança, clareza para o usuário e robustez nas integrações com a API mostQI.
