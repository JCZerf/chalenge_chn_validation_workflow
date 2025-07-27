# wm-input: client_key:str

import requests


def authenticate(client_key: str) -> str:
    """Autentica e retorna o token JWT"""
    url = "https://mostqiapi.com/user/authenticate"
    headers = {"Content-Type": "application/json"}
    payload = {"token": client_key}

    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()

    return response.json().get("token")


def gerar_link_liveness(jwt_token: str) -> dict:
    """Chama a rota de liveness/streaming com personalizações"""
    url = "https://mostqiapi.com/liveness/streaming/async"
    headers = {
        "Authorization": f"Bearer {jwt_token}",
        "Content-Type": "application/json",
    }

    payload = {
        "webhook": {
            "url": "https://app.windmill.dev/api/w/desafio-mostqi-josecarlos/jobs/run/p/u/josecarlos/liveness_start"
        },
        "uiCustomization": {
            "defaultLanguage": "pt-BR",
            "theme": "dark",
            "primaryColor": "#820AD1",
            "hideTopbar": True,
            "welcomeMessage": {
                "pt-BR": "Vamos iniciar sua verificação de vivacidade.",
                "en": "Let's begin your liveness verification.",
                "es": "Vamos a comenzar tu verificación de vivacidad.",
                "fr": "Commençons votre vérification de vivacité.",
            },
            "successMessage": {
                "pt-BR": "Vivacidade confirmada com sucesso!",
                "en": "Liveness successfully confirmed!",
                "es": "¡Vivacidad confirmada con éxito!",
                "fr": "Vivacité confirmée avec succès !",
            },
            "failureMessage": {
                "pt-BR": "Não foi possível confirmar sua vivacidade. Tente novamente.",
                "en": "We couldn't confirm your liveness. Please try again.",
                "es": "No fue posible confirmar tu vivacidad. Intenta de nuevo.",
                "fr": "Impossible de confirmer votre vivacité. Veuillez réessayer.",
            },
        },
        "redirectUrl": "https://most.com.br/",
    }

    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()

    return response.json()


def main(client_key: str):
    try:
        token = authenticate(client_key)
        resultado = gerar_link_liveness(token)

        session_url = resultado.get("result", {}).get("sessionUrl")
        process_id = resultado.get("result", {}).get("processId")

        if not session_url or not process_id:
            return {
                "title": "Erro",
                "description": "Não foi possível gerar o link de prova de vida. Verifique os dados e tente novamente.",
            }

        return {
            "title": "Link para Prova de Vida",
            "description": "O link foi gerado com sucesso para realizar a verificação de vivacidade.",
            "fields": {},
            "actions": {},
            "default_args": {"process_id": process_id, "session_url": session_url},
            "enums": {},
        }

    except Exception as e:
        return {
            "title": "Erro",
            "description": f"Falha ao gerar link de prova de vida: {str(e)}",
        }
