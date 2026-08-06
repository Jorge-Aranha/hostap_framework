import sys
import os

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, BASE_DIR)

from flask import Blueprint, render_template, request, jsonify, abort
from AUT.priv.conexao import con
from datetime import datetime
import json, csv, io
from AUT.auto_model.pasta_c1 import criar_zip

cliente_bp = Blueprint("cliente", __name__, url_prefix="/cliente")

# @cliente_bp.before_request
# def validar_ip():

#     if request.remote_addr not in ["127.0.0.1", "::1"]:
#         abort(403)

# @cliente_bp.before_request
# def validar_ip():

#     print(
#         f"IP: {request.remote_addr} | URL: {request.path}"
#     )

#     if request.remote_addr not in ["127.0.0.1", "::1"]:
#         abort(403)

# @cliente_bp.before_request
# def validar_ip():

#     print("IP recebido:", request.remote_addr)
#     print("URL:", request.path)

#     if request.remote_addr not in ["127.0.0.1", "::1"]:
#         abort(403)

@cliente_bp.route("/", methods=["GET"])
def clientes():
    try:
        conn = con()
        cursor = conn.cursor()

        cursor.execute("""
            WITH a_isnull AS (
                SELECT
                    eac.NOTA,
                    eac.ORDEM_MEDIDA,
                    etmcn.ID_MEDIDA,
                    etmcn.MOTIVO,
                    TO_VARCHAR(etmcn.CRIADA_EM, 'DD/MM/YYYY') AS DT_CRIA
                FROM U620433.EMB_AVRES_CLIENTE eac
                INNER JOIN U620433.EMB_TREAT_MOTIVO_CLIENTE_NCLB etmcn
                    ON eac.NOTA = etmcn.NOTA
                    AND eac.ORDEM_MEDIDA = etmcn.ORDEM_MEDIDA
                WHERE eac.TIPO = 8
                    AND eac.RESULTADO IS NULL
                    AND etmcn.CONCLUIDA_EM IS NULL
            )
            SELECT * FROM a_isnull
        """)

        resultado = cursor.fetchall()

        cursor.close()
        conn.close()

        return render_template("clientes.html", clientes=resultado)

    except Exception as e:
        return f"Erro: {e}"


@cliente_bp.route("/tratamento", methods=["POST"])
def tratamento():

    try:
        data = request.get_json()

        nota = data["nota"]
        ordem = data["ordem"]
        resultado = data["resultado"]
        email = ["jorge.aranha@neoenergia.com"]

        conn = con()
        cursor = conn.cursor()

        cursor.execute(
            """
            UPDATE U620433.EMB_AVRES_CLIENTE
            SET
                RESULTADO = ?,
                EMAIL_RESPONSAVEL = ?
            WHERE
                NOTA = ?
                AND ORDEM_MEDIDA = ?
                AND TIPO = 8
        """,
            (json.dumps(resultado, ensure_ascii=False), email[0], nota, ordem),
        )

        conn.commit()

        if resultado.get("ACAO") == "CANCELAR":
            criar_zip(nota, ordem)

        cursor.close()
        conn.close()

        return jsonify(
            {"status": "ok", "mensagem": "Tratativa atualizada com sucesso."}
        )

    except Exception as e:
        return jsonify({"status": "erro", "mensagem": str(e)})
