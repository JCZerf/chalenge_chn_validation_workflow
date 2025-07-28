# wm-input: nome_idp:str, nome_vio:str
# wm-input: cpf_idp:str, cpf_vio:str
# wm-input: nascimento_idp:str, nascimento_vio:str
# wm-input: filiacao1_idp:str, filiacao1_vio:str
# wm-input: filiacao2_idp:str, filiacao2_vio:str
# wm-input: rg_idp:str, rg_vio:str
# wm-input: registro_idp:str, registro_vio:str
# wm-input: emissao_idp:str, emissao_vio:str
# wm-input: validade_idp:str, validade_vio:str
# wm-input: categoria_idp:str, categoria_vio:str

# wm-input: liveness_score:float
# wm-input: facematch_score:float
# wm-input: facematch_aprovado:bool


def main(
    nome_idp,
    nome_vio,
    cpf_idp,
    cpf_vio,
    nascimento_idp,
    nascimento_vio,
    filiacao1_idp,
    filiacao1_vio,
    filiacao2_idp,
    filiacao2_vio,
    rg_idp,
    rg_vio,
    registro_idp,
    registro_vio,
    emissao_idp,
    emissao_vio,
    validade_idp,
    validade_vio,
    categoria_idp,
    categoria_vio,
    liveness_score,
    facematch_score,
    facematch_aprovado,
):
    try:

        def normalizar(valor: str) -> str:
            if not isinstance(valor, str):
                return ""
            return (
                valor.strip()
                .lower()
                .replace(" ", "")
                .replace(".", "")
                .replace("-", "")
                .replace("/", "")
            )

        def comparar(valor1: str, valor2: str) -> bool:
            return normalizar(valor1) == normalizar(valor2)

        def format_linha(nome, val_frente, val_qr, status):
            return f"- {nome}: {'✅' if status else '❌'}\n  - Frente da CNH: `{val_frente}`\n  - QR Code: `{val_qr}`"

        comparacoes = {
            "Nome": (nome_idp, nome_vio, comparar(nome_idp, nome_vio)),
            "CPF": (cpf_idp, cpf_vio, comparar(cpf_idp, cpf_vio)),
            "Data de nascimento": (
                nascimento_idp,
                nascimento_vio,
                comparar(nascimento_idp, nascimento_vio),
            ),
            "Filiação mãe": (
                filiacao1_idp,
                filiacao1_vio,
                comparar(filiacao1_idp, filiacao1_vio),
            ),
            "Filiação pai": (
                filiacao2_idp,
                filiacao2_vio,
                comparar(filiacao2_idp, filiacao2_vio),
            ),
            "RG": (
                rg_idp,
                rg_vio,
                (
                    comparar(rg_idp, rg_vio)
                    if isinstance(rg_idp, str) and isinstance(rg_vio, str)
                    else (
                        False or rg_idp in rg_vio
                        if isinstance(rg_idp, str) and isinstance(rg_vio, str)
                        else (
                            False or rg_vio in rg_idp
                            if isinstance(rg_idp, str) and isinstance(rg_vio, str)
                            else False
                        )
                    )
                ),
            ),
            "Registro CNH": (
                registro_idp,
                registro_vio,
                comparar(registro_idp, registro_vio),
            ),
            "Data de emissão": (
                emissao_idp,
                emissao_vio,
                comparar(emissao_idp, emissao_vio),
            ),
            "Data de validade": (
                validade_idp,
                validade_vio,
                comparar(validade_idp, validade_vio),
            ),
            "Categoria de habilitação": (
                categoria_idp,
                categoria_vio,
                comparar(categoria_idp, categoria_vio),
            ),
        }

        # Validação dos campos essenciais
        campos_faltando = [
            campo for campo, (idp, vio, _) in comparacoes.items() if not idp or not vio
        ]
        if campos_faltando:
            resultado_parcial = (
                "### 🔎 Comparativo entre Dados da Frente da CNH e Dados do QR Code\n"
            )
            for campo, (idp, vio, status) in comparacoes.items():
                if campo not in campos_faltando:
                    resultado_parcial += format_linha(campo, idp, vio, status) + "\n"
            mensagem = (
                "Atenção: Os seguintes campos não foram preenchidos corretamente e podem indicar falha nos passos anteriores:\n"
                + "\n".join(f"- {campo}" for campo in campos_faltando)
                + "\nSugestão: Refaça os passos correspondentes e envie os dados novamente.\n\n"
                + resultado_parcial
            )
            return {
                "score_dados": 0,
                "aprovado_dados": False,
                "aprovado_liveness": liveness_score >= 80,
                "aprovado_facematch": facematch_aprovado,
                "mensagem_resultado_final": mensagem,
            }

        total = len(comparacoes)
        acertos = sum(1 for _, _, ok in comparacoes.values() if ok)
        score = round((acertos / total) * 100, 2) if total > 0 else 0

        resultado_validacao = (
            "### 🔎 Comparativo entre Dados da Frente da CNH e Dados do QR Code\n"
        )
        for campo, (idp, vio, status) in comparacoes.items():
            resultado_validacao += format_linha(campo, idp, vio, status) + "\n"

        resultado_facematch = f"""
### 🧑‍🦲 Similaridade Facial (FaceMatch)
- Similaridade: {round(facematch_score, 2)}%
- Aprovado: {"✅ Sim" if facematch_aprovado else "❌ Não"}
""".strip()

        resultado_liveness = f"""
### 👁️ Verificação de Prova de Vida (Liveness)
- Score de vivacidade: {round(liveness_score * 100, 2)}%
- Resultado: {"🟢 Prova de vida aprovada" if liveness_score >= 0.80 else "🔴 Prova de vida reprovada"}
""".strip()

        output = f"""
📋 **Resumo da Validação da CNH**

{resultado_validacao}

{resultado_facematch}

{resultado_liveness}
""".strip()

        return {
            "score_dados": score,
            "aprovado_dados": score >= 75,
            "aprovado_liveness": liveness_score >= 80,
            "aprovado_facematch": facematch_aprovado,
            "mensagem_resultado_final": output,
        }
    except Exception as e:
        return {
            "score_dados": 0,
            "aprovado_dados": False,
            "aprovado_liveness": False,
            "aprovado_facematch": False,
            "mensagem_resultado_final": f"Erro inesperado na validação final: {str(e)}",
        }
