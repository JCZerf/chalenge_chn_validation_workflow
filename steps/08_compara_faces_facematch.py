# wm-input: client_key:str, face_file_a:file, face_base64_b:str

import requests
import logging
import base64

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def authenticate(client_key: str) -> str:
    url = "https://mostqiapi.com/user/authenticate"
    headers = {"Content-Type": "application/json"}
    payload = {"token": client_key}
    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        return response.json().get("token")
    except requests.exceptions.HTTPError as e:
        raise Exception("Erro na autenticação: token inválido ou serviço indisponível.")
    except Exception as e:
        raise Exception(f"Falha ao autenticar: {str(e)}")


def comparar_faces(jwt_token: str, file_a: bytes, base64_str_b: str) -> dict:
    url = "https://mostqiapi.com/process-image/biometrics/face-compare"
    headers = {"Authorization": f"Bearer {jwt_token}"}

    try:
        file_b = base64.b64decode(base64_str_b)
    except Exception as e:
        raise Exception(
            "Erro ao decodificar imagem base64 da selfie: verifique o conteúdo enviado."
        )

    files = {
        "faceFileA": ("face_a.jpg", file_a, "application/octet-stream"),
        "faceFileB": ("face_b.jpg", file_b, "application/octet-stream"),
    }

    try:
        response = requests.post(url, headers=headers, files=files)
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        status_code = getattr(e.response, "status_code", "N/A")
        response_text = getattr(e.response, "text", "")
        raise Exception(
            f"Erro ao comparar imagens: verifique os arquivos enviados.\n"
            f"Código HTTP: {status_code}\n"
            f"Detalhes: {response_text}"
        )
    except Exception as e:
        raise Exception(f"Erro inesperado na requisição FaceMatch: {str(e)}")

    data = response.json()
    similarity = data.get("result", {}).get("similarity", 0.0)
    status = data.get("status", {}).get("message", "Desconhecido")
    code = data.get("status", {}).get("code", "N/A")
    request_id = data.get("requestId")
    aprovado = similarity >= 0.70

    descricao = (
        f"Similaridade facial: {round(similarity * 100, 2)}%\n\n"
        f"Aprovação: {'Sim' if aprovado else 'Não'}\n\n"
        f"Status da API: {code} - {status}\n"
        f"Request ID: {request_id}"
    )

    return {
        "title": "Resultado da Comparação Facial",
        "description": descricao,
        "fields": {
            "similaridade_percentual": round(similarity * 100, 2),
            "aprovado": aprovado,
        },
        "actions": {},
        "default_args": {},
        "enums": {},
    }


def main(client_key: str, face_file_a: bytes, face_base64_b: str):
    try:
        if not client_key or not face_file_a or not face_base64_b:
            raise Exception("Todos os campos são obrigatórios. Verifique as entradas.")

        jwt_token = authenticate(client_key)
        return comparar_faces(jwt_token, face_file_a, face_base64_b)

    except Exception as e:
        logger.error(f"Erro: {e}")
        return {
            "title": "Erro na Comparação Facial",
            "description": str(e),
            "fields": {},
            "actions": {},
            "default_args": {},
            "enums": {},
        }
