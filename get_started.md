📄 instrucoes_uso.md

# 🧭 Instruções de Uso – CNH Validation Workflow

Este documento descreve como executar o fluxo de validação de identidade via CNH utilizando a plataforma **Windmill**, com suporte a testes locais dos scripts em Python.

---

## ⚙️ Requisitos

Antes de iniciar, verifique se você tem:

- Conta com acesso à plataforma **Windmill EE** (Self-hosted ou Cloud)
- Chave de acesso (`client_key`) válida para as APIs da **mostQI**
- Python 3.10+ instalado (opcional, para testes locais)
- Permissões para criar workflows e scripts na instância Windmill

---

## 🧩 Executando o Workflow no Windmill


1. **Clone este repositório:**
   ```bash
   git clone https://github.com/JCZerf/cnh_validation_workflow.git
   cd cnh_validation_workflow
   ```

2. Acesse o painel do Windmill e vá até a aba Workflows.

3. Crie um novo Workflow e adicione os passos manualmente:
   - Cada passo deve seguir a numeração da pasta `steps/`
   - Use os arquivos `.py` como scripts do tipo action
   - Use os arquivos `.json` como formulários suspensos ou approvals
   - 💡 Recomendado: usar o modo avançado para criar etapas suspend com Form habilitado.

4. Configure as conexões entre etapas:
   - Conecte a saída de um script à entrada do próximo.
   - Exemplo: a imagem da frente enviada em `01_upload_cnh_frente.py` deve ser usada em `02_processar_cnh_frente_idp.py`.

5. No início da execução, o workflow solicitará o `client_key` (ou configure um campo global).

6. Execute o workflow inteiro clicando em "Run". Siga os passos interativos conforme solicitado:
   - Upload de imagens
   - Aguardar retorno das APIs
   - Confirmar liveness
   - Visualizar resultado final


---

## 🧪 Testando scripts localmente (modo desenvolvedor)
Caso deseje testar os scripts Python localmente:

1. Crie e ative um ambiente virtual:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

2. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```

3. Crie um arquivo `.env`:
   ```ini
   CLIENT_KEY=sua_chave_aqui
   ```

4. Execute qualquer script diretamente:
   ```bash
   python extract_content.py
   ```

⚠️ Os scripts locais exigem arquivos de imagem válidos (frente e verso da CNH) e, em alguns casos, um vídeo de liveness para simulação.


---

### 🖼 Exemplos de arquivos de entrada (na pasta `assets/`):
- `exemplo_frente.jpg` – imagem da frente da CNH
- `exemplo_verso.jpg` – imagem do QR Code (verso)
- `exemplo_video.mp4` – vídeo de prova de vida
- `print_resultado.png` – captura do relatório final gerado

---

## ✅ Fluxo de Validação – Resumo Visual

```text
01 – Boas-vindas
      ↓
02 – Upload frente da CNH
      ↓
03 – Extração de dados (IDP)
      ↓
04 – Upload verso da CNH (QR Code)
      ↓
05 – Validação QR Code (VIO)
      ↓
06 – Upload vídeo de vivacidade
      ↓
07 – Geração do link de liveness
      ↓
08 – Confirmação após prova de vida
      ↓
09 – Comparação facial (FaceMatch)
      ↓
10 – Resultado final
```

---

### 📎 Dicas
- Se estiver usando uma instância self-hosted do Windmill, garanta que o serviço tenha acesso à internet para chamar as APIs da mostQI.
- Os arquivos `.py` devem ser salvos como scripts do tipo action dentro do Windmill.
- Os arquivos `.json` podem ser usados para gerar formulários customizados no modo suspend > Form.
- Utilize os prints da pasta `assets/` como referência visual para reproduzir a experiência do usuário.

---

### 🤝 Suporte
Dúvidas ou dificuldades? Entre em contato:

- Desenvolvedor: José Carlos Miranda Leite
- GitHub: [@JCZerf](https://github.com/JCZerf)
- Email: josecarlosmrlt@outlook.com