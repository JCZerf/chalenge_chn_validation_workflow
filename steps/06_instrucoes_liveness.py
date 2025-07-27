# wm-input: session_url:str

import requests


def encurtar_link(session_url: str) -> str:
    """Encurta o link da sessão usando o TinyURL"""
    response = requests.get(f"https://tinyurl.com/api-create.php?url={session_url}")
    response.raise_for_status()
    return response.text


def main(session_url: str):
    try:
        short_link = encurtar_link(session_url)

        desc = (
            "VERIFICAÇÃO DE VIVACIDADE OBRIGATÓRIA\n\n"
            "Por favor, siga os passos abaixo para continuar:\n\n"
            "1. Copie e cole o link abaixo no navegador para iniciar a verificação:\n"
            f"{short_link}\n\n"
            "2. Siga as instruções exibidas na tela.\n"
            "3. Após concluir a verificação, volte aqui e clique no botão 'Resume' para prosseguir com o fluxo."
        )

        return {"title": "Etapa de Verificação de Vivacidade", "description": desc}

    except Exception as e:
        return {
            "title": "Erro ao encurtar link",
            "description": f"Falha ao gerar link curto: {str(e)}",
        }
