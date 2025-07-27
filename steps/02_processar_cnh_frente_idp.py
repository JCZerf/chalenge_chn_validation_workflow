# pip: requests
# wm-input: client_key:str, cnh_image_file:file

import requests
import logging
from typing import Dict, Any, Optional, Union
from dataclasses import dataclass, asdict

# Configurações
TIMEOUT_SECONDS = 30
EXTRACTION_URL = "https://mostqiapi.com/process-image/content-extraction"
AUTH_URL = "https://mostqiapi.com/user/authenticate"
HEADERS = {
    "Content-Type": "application/json",
    "User-Agent": "CNH-Validation-Workflow/1.0",
}

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_jwt_token(client_key: str) -> Dict[str, str]:
    """
    Autentica na API mostQI usando a chave do cliente.

    Args:
        client_key (str): Chave fornecida pela mostQI para gerar o token JWT.

    Returns:
        dict: Resultado da autenticação com status, mensagem e o token (se bem-sucedido).
    """
    try:
        logger.info("Autenticando na API mostQI...")
        payload = {"token": client_key}
        response = requests.post(AUTH_URL, json=payload, headers=HEADERS, timeout=10)
        if response.status_code != 200:
            logger.error(f"Erro na resposta: {response.status_code} - {response.text}")
            return {
                "status": "erro",
                "mensagem": f"A API retornou status {response.status_code}: {response.text}",
            }
        data = response.json()
        if not isinstance(data, dict):
            return {
                "status": "erro",
                "mensagem": "Formato inválido na resposta da API.",
            }
        jwt_token = data.get("token")
        if not jwt_token:
            return {
                "status": "erro",
                "mensagem": "O token não foi encontrado na resposta da API.",
            }
        logger.info("Token JWT recebido e validado com sucesso.")
        return {
            "status": "sucesso",
            "mensagem": "Token JWT obtido com sucesso.",
            "token": jwt_token,
        }
    except Exception as e:
        logger.exception("Erro inesperado na autenticação.")
        return {
            "status": "erro",
            "mensagem": f"Erro inesperado ao obter o token: {str(e)}",
        }


@dataclass
class CNHData:
    """Estrutura para dados extraídos da CNH"""

    nome: Optional[str] = None
    cpf: Optional[str] = None
    rg: Optional[str] = None
    data_nascimento: Optional[str] = None
    local_nascimento: Optional[str] = None
    categoria: Optional[str] = None
    data_emissao: Optional[str] = None
    data_validade: Optional[str] = None
    registro: Optional[str] = None
    filiacao_1: Optional[str] = None
    filiacao_2: Optional[str] = None
    score: Optional[float] = None

    @classmethod
    def from_api_response(cls, api_data: Dict[str, Any]) -> "CNHData":
        """Cria instância a partir da resposta da API"""
        if not api_data.get("result") or not api_data["result"]:
            return cls()

        fields = api_data["result"][0].get("fields", [])
        field_dict = {
            field["name"]: field["value"] for field in fields if field["value"]
        }

        return cls(
            nome=field_dict.get("nome"),
            cpf=field_dict.get("cpf"),
            rg=field_dict.get("rg"),
            data_nascimento=field_dict.get("data_nascimento"),
            local_nascimento=field_dict.get("local_nascimento"),
            categoria=field_dict.get("cat_hab"),
            data_emissao=field_dict.get("data_emissao"),
            data_validade=field_dict.get("data_validade"),
            registro=field_dict.get("registro"),
            filiacao_1=field_dict.get("filiacao_1"),
            filiacao_2=field_dict.get("filiacao_2"),
            score=api_data["result"][0].get("score"),
        )


def format_cnh_output(cnh_data: CNHData) -> Dict[str, Any]:
    """
    Formata dados da CNH para saída estruturada

    Args:
        cnh_data: Dados da CNH extraídos

    Returns:
        Dict com dados formatados
    """
    return {
        "pessoa": {
            "nome": cnh_data.nome,
            "cpf": cnh_data.cpf,
            "rg": cnh_data.rg,
            "data_nascimento": cnh_data.data_nascimento,
            "local_nascimento": cnh_data.local_nascimento,
            "filiacao": {"mae": cnh_data.filiacao_1, "pai": cnh_data.filiacao_2},
        },
        "habilitacao": {
            "categoria": cnh_data.categoria,
            "registro": cnh_data.registro,
            "data_emissao": cnh_data.data_emissao,
            "data_validade": cnh_data.data_validade,
        },
        "qualidade": {
            "score": cnh_data.score,
            "status": (
                "aprovado" if cnh_data.score and cnh_data.score > 0.8 else "rejeitado"
            ),
        },
    }


def extract_file_content(file_input: Union[str, bytes, Any]) -> bytes:
    """
    Extrai conteúdo binário do arquivo independente do tipo

    Args:
        file_input: Arquivo de entrada (pode ser string base64, bytes, file-like object ou caminho)

    Returns:
        bytes: Conteúdo binário do arquivo
    """
    import base64
    import re

    try:
        # Se já for bytes
        if isinstance(file_input, bytes):
            return file_input

        # Se for string
        if isinstance(file_input, str):
            # Detecta e remove prefixo base64 se existir
            if file_input.strip().startswith("data:"):
                file_input = re.sub(r"^data:.*;base64,", "", file_input)
            try:
                # Tenta decodificar como base64
                return base64.b64decode(file_input, validate=True)
            except Exception:
                # Se não for base64, tenta abrir como caminho de arquivo
                try:
                    with open(file_input, "rb") as f:
                        return f.read()
                except Exception:
                    raise ValueError(
                        "String não é base64 nem caminho de arquivo válido."
                    )

        # Se tiver método read (file-like object)
        if hasattr(file_input, "read"):
            content = file_input.read()
            if isinstance(content, str):
                return content.encode("utf-8")
            return content

        # Se tiver atributo content (alguns objetos Windmill)
        if hasattr(file_input, "content"):
            content = file_input.content
            if isinstance(content, str):
                if content.strip().startswith("data:"):
                    content = re.sub(r"^data:.*;base64,", "", content)
                return base64.b64decode(content)
            return content

        # Tenta converter para bytes
        return str(file_input).encode("utf-8")

    except Exception as e:
        logger.error(f"Erro ao extrair conteúdo do arquivo: {e}")
        raise ValueError(f"Não foi possível extrair conteúdo do arquivo: {e}")


def main(client_key: str, cnh_image_file: bytes) -> Dict[str, Any]:
    """
    Gera o token JWT e extrai dados da CNH usando a API mostQI.

    Args:
        client_key (str): Chave fornecida pela mostQI para gerar o token JWT.
        cnh_image_file: Arquivo de imagem da CNH (qualquer formato suportado pelo Windmill)

    Returns:
        dict: Resultado da extração com dados formatados
    """
    try:
        logger.info("Iniciando autenticação e extração de conteúdo da CNH...")

        # Validar entrada
        if not client_key:
            return {
                "status": "erro",
                "mensagem": "Chave do cliente não fornecida",
                "dados": None,
            }

        if not cnh_image_file:
            return {
                "status": "erro",
                "mensagem": "Arquivo de imagem não fornecido",
                "dados": None,
            }

        # Gerar token JWT
        token_result = get_jwt_token(client_key)
        if token_result.get("status") != "sucesso" or not token_result.get("token"):
            return {
                "status": "erro",
                "mensagem": f"Falha ao obter token JWT: {token_result.get('mensagem')}",
                "dados": None,
            }
        jwt_token = token_result["token"]

        # Extrair conteúdo do arquivo
        try:
            file_content = extract_file_content(cnh_image_file)
            logger.info(f"Arquivo lido com sucesso. Tamanho: {len(file_content)} bytes")
        except Exception as e:
            return {
                "status": "erro",
                "mensagem": f"Erro ao ler arquivo de imagem: {str(e)}",
                "dados": None,
            }

        # Preparar requisição
        headers = {
            "accept": "application/json",
            "Authorization": f"Bearer {jwt_token}",
        }

        files = {
            "file": ("cnh_image.jpg", file_content, "image/jpeg"),
            "returnImage": "true",
            "returnCrops": "true",
            "tags": [
                "id=bra-cnh-3",
                "language=pt-BR",
                "type=documento-pessoal",
            ],
        }

        logger.info("Enviando imagem para API mostQI...")

        # Fazer requisição
        response = requests.post(
            EXTRACTION_URL, files=files, headers=headers, timeout=TIMEOUT_SECONDS
        )

        logger.info(f"Status da resposta: {response.status_code}")

        # Processar resposta
        if response.status_code == 200:
            api_data = response.json()
            logger.info("Resposta recebida com sucesso")
            print("### DEBUG API DATA ###")
            print(api_data)

            # Verifica se veio imagem corrigida
            deskewed_image_base64 = None
            try:
                deskewed_image_base64 = api_data["result"][0].get("image")
                if deskewed_image_base64:
                    logger.info("Imagem deskewed capturada com sucesso.")
                else:
                    logger.warning("A imagem deskewed veio como null.")
            except Exception as e:
                logger.error(f"Erro ao tentar acessar imagem deskewed: {e}")
            # Extrair dados
            cnh_data = CNHData.from_api_response(api_data)

            # Verificar se dados foram extraídos
            if not cnh_data.nome and not cnh_data.cpf:
                return {
                    "status": "aviso",
                    "mensagem": "Nenhum dado foi extraído da imagem",
                    "dados": None,
                    "score": cnh_data.score,
                }

            # Formatar dados
            formatted_data = format_cnh_output(cnh_data)

            # Contar campos extraídos
            fields_extracted = sum(
                1 for field in asdict(cnh_data).values() if field is not None
            )

            logger.info(f"Extração concluída. Campos extraídos: {fields_extracted}")

            return {
                "status": "sucesso",
                "mensagem": "Dados extraídos com sucesso",
                "dados": formatted_data,
                "imagem_corrigida": deskewed_image_base64,
                "metadata": {
                    "score": cnh_data.score,
                    "campos_extraidos": fields_extracted,
                    "metodo_extracao": "mostQI_Content_API",
                    "qualidade": formatted_data["qualidade"]["status"],
                },
            }

        elif response.status_code == 401:
            logger.error("Token JWT inválido ou expirado")
            return {
                "status": "erro",
                "mensagem": "Token JWT inválido ou expirado",
                "dados": None,
            }

        elif response.status_code == 400:
            logger.error(f"Erro na requisição: {response.text}")
            return {
                "status": "erro",
                "mensagem": f"Erro na imagem ou formato: {response.text}",
                "dados": None,
            }

        else:
            logger.error(f"Erro HTTP {response.status_code}: {response.text}")
            return {
                "status": "erro",
                "mensagem": f"Erro da API: {response.status_code} - {response.text}",
                "dados": None,
            }

    except requests.exceptions.Timeout:
        logger.error("Timeout na requisição")
        return {
            "status": "erro",
            "mensagem": "Timeout na requisição para a API",
            "dados": None,
        }

    except requests.exceptions.RequestException as e:
        logger.error(f"Erro na requisição: {e}")
        return {
            "status": "erro",
            "mensagem": f"Erro na comunicação com a API: {str(e)}",
            "dados": None,
        }

    except Exception as e:
        logger.exception("Erro inesperado na extração")
        return {
            "status": "erro",
            "mensagem": f"Erro inesperado: {str(e)}",
            "dados": None,
        }
