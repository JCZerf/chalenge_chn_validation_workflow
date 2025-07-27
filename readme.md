# 📘 CNH Validation Workflow – MOSTQI Challenge

Este repositório contém a implementação completa de um fluxo automatizado de **validação de identidade via CNH**, desenvolvido como solução para o desafio técnico da MOST (vaga Full Stack Developer - Python).

O workflow foi inteiramente construído e executado na plataforma **Windmill**, utilizando as APIs da **mostQI** para realizar extração de dados, validações de QR Code, verificação de vivacidade e comparação facial.

## 🚀 Funcionalidades principais

- 📤 Upload da frente e verso da CNH
- 🔎 Extração de dados da CNH via OCR (API IDP)
- 🧾 Leitura e validação do QR Code criptografado (API VIO Extraction)
- 🎥 Prova de vida com vídeo personalizado (API Liveness Streaming)
- 🧑‍💼 Comparação facial entre CNH e vídeo (API FaceMatch)
- 📊 Geração de relatório consolidado com score final de aprovação

## 🛠 Tecnologias utilizadas

- 🧠 **Python 3.10+**
- 🔁 **Windmill (EE)** – Orquestração de fluxo no-code com scripts customizados
- 🔐 **JWT** – Autenticação com chave da API
- 📡 **APIs REST** – Integrações com as APIs da mostQI
- 📄 **JSON Schema** – Validação e estruturação de formulários
- 📦 `requests`, `python-dotenv`, `dataclasses`, `typing`, `mimetypes`

## 🧩 Etapas do Workflow (10 passos)


O workflow é composto por 10 etapas integradas, cada uma automatizada por scripts Python e formulários interativos:

1. 🟢 **Boas-vindas** – Apresenta o fluxo ao usuário, explica as etapas e orienta sobre os documentos necessários (imagem frente, verso com QR Code e vídeo de vivacidade).

2. 📸 **Upload da frente da CNH** – Orienta como tirar a foto da frente da CNH: superfície plana, boa iluminação, sem reflexos, dados legíveis e boa resolução.

3. 🧠 **Processar frente da CNH (IDP)** – Envia a imagem da frente da CNH para a API `content-extraction` da mostQI, realizando autenticação JWT e extração dos dados do documento.

4. 📤 **Upload do verso da CNH (QR Code)** – Orienta como tirar a foto do QR Code: plano, iluminado, QR Code visível, sem reflexos ou cortes, boa qualidade de câmera.

5. 🔍 **Processar QR Code (VIO)** – Envia a imagem do verso para a API `vio-extraction` da mostQI, realizando autenticação JWT e extração dos dados criptografados do QR Code.

6. 🎥 **Gerar link para prova de vida (Liveness)** – Autentica e gera um link personalizado para o usuário realizar a verificação de vivacidade via vídeo, com customização de interface e integração webhook.

7. 🧬 **Instruções para prova de vida** – Exibe o link encurtado para o usuário iniciar a verificação de vivacidade, com instruções claras para seguir o processo e retornar ao fluxo após conclusão.

8. ✅ **Verificar status da prova de vida** – Consulta o status da verificação de vivacidade na API, informando se foi concluída, aprovada ou se houve erro.

9. 🧑‍🦲 **Comparação facial (FaceMatch)** – Realiza a comparação entre o rosto da CNH e o vídeo enviado, utilizando a API de biometria da mostQI, retornando score e aprovação.

10. 🧾 **Validação final** – Consolida todos os dados extraídos (IDP e VIO), scores de vivacidade e FaceMatch, e apresenta o resultado final ao usuário, incluindo status e aprovação.

📎 Para mais detalhes, consulte [`windmill_workflow/overview.md`](./windmill_workflow/overview.md).

## 📁 Estrutura do projeto


```
Chalenge_CNH_Validation/
├── readme.md
├── requirements.txt
├── assets/
│   ├── overview.md
│   ├── workflow_diagrama.png
│   ├── cnh_front_demo.jpg
│   ├── face_match1_demo.png
│   ├── face_match2_demo.jpg
├── steps/
│   ├── 00_boas_vindas.py
│   ├── 01_upload_cnh_frente.py
│   ├── 02_processar_cnh_frente_idp.py
│   ├── 03_upload_cnh_qrcode.py
│   ├── 04_processa_cnh_qrcode_vio.py
│   ├── 05_liveness_get_link_start.py
│   ├── 06_instrucoes_liveness.py
│   ├── 07_verifica_status_liveness.py
│   ├── 08_compara_faces_facematch.py
│   └── 09_validacao_final.py
```


## ✅ Como executar os scripts localmente

1. Clone o repositório:
   ```bash
   git clone https://github.com/JCZerf/cnh_validation_workflow.git
   cd cnh_validation_workflow
   ```

2. Crie e ative um ambiente virtual:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```

4. Crie um arquivo `.env` com sua chave:
   ```ini
   CLIENT_KEY=coloque_sua_chave_aqui
   ```

5. Execute qualquer script para teste (exemplo):
   ```bash
   python extract_content.py
   ```

⚠️ Para testes completos, utilize a interface do Windmill com os arquivos da pasta `windmill_workflow/steps`.

📌 Observações
- Todas as APIs utilizadas foram documentadas no portal da mostQI.
- Os tokens JWT são gerados dinamicamente antes de cada requisição, garantindo segurança e validade.
- Scripts foram testados com entradas reais e arquivos de exemplo.

---

🤝 Contato  
Desenvolvido por José Carlos Miranda Leite  
GitHub: [@JCZerf](https://github.com/JCZerf)  
LinkedIn: [josécarlos-miranda-leite](www.linkedin.com/in/josé-carlos-leite-814a15375)  
Email: josecarlosmrlt@outlook.com  

Projeto desenvolvido como parte do processo seletivo para a vaga Full Stack Developer – Python na MOST.