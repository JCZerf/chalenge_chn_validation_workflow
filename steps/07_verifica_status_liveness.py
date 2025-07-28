import requests


def authenticate(client_key: str) -> str:
    """Autentica e retorna o token JWT"""
    url = "https://mostqiapi.com/user/authenticate"
    headers = {"Content-Type": "application/json"}
    payload = {"token": client_key}
    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()
    return response.json().get("token")


def consultar_status(jwt_token: str, process_id: str) -> dict:
    """Consulta o status da prova de vida"""
    url = "https://mostqiapi.com/liveness/streaming/async/status"
    headers = {
        "Authorization": f"Bearer {jwt_token}",
        "Content-Type": "application/json",
    }
    payload = {"processId": process_id}
    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()
    return response.json()


def main(client_key: str, process_id: str):
    try:
        if not client_key or not process_id:
            return {
                "title": "Erro",
                "description": "Chave do cliente ou process ID não informado.",
                "default_args": {"imagem_base64": None},
            }

        token = authenticate(client_key)
        if not token:
            return {
                "title": "Erro de autenticação",
                "description": "Não foi possível obter token JWT.",
                "default_args": {"imagem_base64": None},
            }

        resultado = consultar_status(token, process_id)
        result_data = resultado.get("result", {})

        status = result_data.get("status", "Indefinido")
        liveness_score = result_data.get("livenessScore", "N/A")
        imagem_base64 = result_data.get("frontalImage")

        request_id = resultado.get("requestId")
        status_api = resultado.get("status", {})
        codigo_status = status_api.get("code", "N/A")
        mensagem_status = status_api.get("message", "Sem mensagem")

        liveness_score = (
            result_data.get("livenessScore")
            or result_data.get("metrics", {}).get("livenessScore")
            or result_data.get("results", {}).get("livenessScore")
            or None
        )

        if liveness_score is None:
            liveness_score = 0.0

        # Monta descrição detalhada
        desc = f"Status atual: **{status}**\n\n"
        desc += f"Score de vivacidade: `{liveness_score}`\n\n"
        desc += f"requestId: `{request_id}`\n"
        desc += f"Código da resposta: `{codigo_status}` - {mensagem_status}"

        if not imagem_base64:
            desc += "\n\n**Nenhuma imagem capturada disponível.**"
        else:
            desc += "\n\nImagem capturada disponível nos argumentos padrão."

        return {
            "title": f"Status: {status}",
            "description": desc,
            "fields": {},
            "actions": {},
            "default_args": {"imagem_base64": imagem_base64},
            "outputs": {"liveness_score": liveness_score},
            "enums": {},
        }

    except requests.exceptions.HTTPError as http_err:
        status_code = getattr(http_err.response, "status_code", "N/A")
        response_text = getattr(http_err.response, "text", "")
        return {
            "title": "Erro HTTP",
            "description": (
                f"Erro na requisição HTTP.\n"
                f"Código: {status_code}\n"
                f"Detalhes: {response_text}\n"
                f"Exceção: {http_err}"
            ),
            "default_args": {"imagem_base64": None},
        }
    except Exception as e:
        return {
            "title": "Erro inesperado",
            "description": f"Falha ao consultar status de prova de vida: {str(e)}",
            "default_args": {"imagem_base64": None},
        }
