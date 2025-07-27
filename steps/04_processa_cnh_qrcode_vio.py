# pip: requests
# wm-input: client_key:str, qr_image_file:file

import requests
import logging
from typing import Any, Dict, Optional, List
from dataclasses import dataclass, asdict

# Configs
TIMEOUT_SECONDS = 30
VIO_URL = "https://mostqiapi.com/process-image/vio-extraction"
AUTH_URL = "https://mostqiapi.com/user/authenticate"
HEADERS = {
    "Content-Type": "application/json",
    "User-Agent": "CNH-Validation-Workflow/1.0",
}

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_jwt_token(client_key: str) -> Optional[str]:
    try:
        logger.info("Autenticando na API mostQI...")
        response = requests.post(
            AUTH_URL, json={"token": client_key}, headers=HEADERS, timeout=10
        )
        if response.status_code != 200:
            logger.error(f"Erro: {response.status_code} - {response.text}")
            return None
        return response.json().get("token")
    except Exception as e:
        logger.exception("Erro ao obter token JWT.")
        return None


@dataclass
class VIOData:
    nome: Optional[str] = None
    cpf: Optional[str] = None
    rg: Optional[str] = None
    data_nascimento: Optional[str] = None
    filiacao_1: Optional[str] = None
    filiacao_2: Optional[str] = None
    categoria: Optional[str] = None
    data_emissao: Optional[str] = None
    data_validade: Optional[str] = None
    registro: Optional[str] = None
    renach: Optional[str] = None
    local_uf: Optional[str] = None
    local_cidade: Optional[str] = None
    codigo_seguranca: Optional[str] = None
    observacoes: Optional[str] = None
    page_number: Optional[int] = None
    tags: Optional[List[str]] = None

    @classmethod
    def from_api_response(cls, api_data: Dict[str, Any]) -> "VIOData":
        if not api_data.get("result") or not api_data["result"]:
            return cls()

        result = api_data["result"][0]
        fields = {field["name"]: field["value"] for field in result.get("fields", [])}

        return cls(
            nome=fields.get("nome"),
            cpf=fields.get("cpf"),
            rg=fields.get("rg"),
            data_nascimento=fields.get("data_nascimento"),
            filiacao_1=fields.get("filiacao_1"),
            filiacao_2=fields.get("filiacao_2"),
            categoria=fields.get("cat_hab"),
            data_emissao=fields.get("data_emissao"),
            data_validade=fields.get("data_validade"),
            registro=fields.get("registro"),
            renach=fields.get("renach"),
            local_uf=fields.get("local_uf"),
            local_cidade=fields.get("local_cidade"),
            codigo_seguranca=fields.get("codigo_seguranca"),
            observacoes=fields.get("observacoes"),
            page_number=result.get("pageNumber"),
            tags=result.get("tags"),
        )


def format_vio_output(vio_data: VIOData) -> Dict[str, Any]:
    return {
        "pessoa": {
            "nome": vio_data.nome,
            "cpf": vio_data.cpf,
            "rg": vio_data.rg,
            "data_nascimento": vio_data.data_nascimento,
            "filiacao": {
                "mae": vio_data.filiacao_1,
                "pai": vio_data.filiacao_2,
            },
        },
        "habilitacao": {
            "categoria": vio_data.categoria,
            "registro": vio_data.registro,
            "renach": vio_data.renach,
            "data_emissao": vio_data.data_emissao,
            "data_validade": vio_data.data_validade,
        },
        "documento": {
            "codigo_seguranca": vio_data.codigo_seguranca,
            "observacoes": vio_data.observacoes,
            "local_uf": vio_data.local_uf,
            "local_cidade": vio_data.local_cidade,
            "tags": vio_data.tags,
            "pagina": vio_data.page_number,
        },
    }


def main(client_key: str, qr_image_file: bytes) -> Dict[str, Any]:
    if not client_key:
        return {"status": "erro", "mensagem": "Chave do cliente ausente", "dados": None}
    if not qr_image_file:
        return {
            "status": "erro",
            "mensagem": "Arquivo da imagem não foi enviado",
            "dados": None,
        }

    jwt_token = get_jwt_token(client_key)
    if not jwt_token:
        return {"status": "erro", "mensagem": "Falha ao obter token JWT", "dados": None}

    headers = {"Authorization": f"Bearer {jwt_token}"}
    files = {"file": ("qr_image.jpg", qr_image_file, "image/jpeg")}

    try:
        response = requests.post(
            VIO_URL, files=files, headers=headers, timeout=TIMEOUT_SECONDS
        )

        if response.status_code == 200:
            api_data = response.json()
            vio_data = VIOData.from_api_response(api_data)

            if not vio_data.cpf and not vio_data.nome:
                return {
                    "status": "aviso",
                    "mensagem": "Nenhum dado relevante extraído da imagem",
                    "dados": None,
                    "metadata": {
                        "tags": vio_data.tags,
                        "pagina": vio_data.page_number,
                        "metodo": "mostQI_VIO_API",
                    },
                }

            return {
                "status": "sucesso",
                "mensagem": "QR code extraído com sucesso",
                "dados": format_vio_output(vio_data),
                "metadata": {
                    "tags": vio_data.tags,
                    "pagina": vio_data.page_number,
                    "metodo": "mostQI_VIO_API",
                },
            }

        elif response.status_code == 401:
            return {
                "status": "erro",
                "mensagem": "Token JWT inválido ou expirado",
                "dados": None,
            }
        elif response.status_code == 400:
            return {
                "status": "erro",
                "mensagem": f"Erro na imagem: {response.text}",
                "dados": None,
            }
        else:
            return {
                "status": "erro",
                "mensagem": f"Erro HTTP {response.status_code}: {response.text}",
                "dados": None,
            }

    except requests.exceptions.Timeout:
        return {"status": "erro", "mensagem": "Timeout na requisição", "dados": None}
    except Exception as e:
        logger.exception("Erro inesperado durante a extração VIO.")
        return {
            "status": "erro",
            "mensagem": f"Erro inesperado: {str(e)}",
            "dados": None,
        }
