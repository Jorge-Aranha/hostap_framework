from flask import Flask, send_file, request, redirect
from io import BytesIO
import os
import sys

BASE_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..")
)

sys.path.insert(0, BASE_DIR)

from outros.conexao import con

app = Flask(__name__)


@app.route("/tracking/<hash_envio>")
def tracking(hash_envio):

    ip_abert = request.remote_addr

    navegador_abert = request.headers.get(
        "User-Agent",
        "DESCONHECIDO"
    )

    if "Windows" in navegador_abert:
        dispositivo_abert = "DESKTOP"
    elif "Android" in navegador_abert:
        dispositivo_abert = "ANDROID"
    elif "iPhone" in navegador_abert:
        dispositivo_abert = "IPHONE"
    else:
        dispositivo_abert = "DESCONHECIDO"

    conn = con()
    cursor = conn.cursor()

    cursor.execute(
        """
        UPDATE "U620433"."EMB_NOTIFICACAO_CLIENTE_AREAS"
        SET
            DT_ABERT_DESTINATARIO = CURRENT_UTCTIMESTAMP,
            IP_ABERT = ?,
            NAVEGADOR_ABERT = ?,
            DISPOSITIVO_ABERT = ?
        WHERE HASH = ?
          AND DT_ABERT_DESTINATARIO IS NULL
        """,
        (
            ip_abert,
            navegador_abert[:100],
            dispositivo_abert,
            hash_envio
        )
    )

    conn.commit()

    cursor.close()
    conn.close()

    return redirect(
        "http://hor5gsn034.amer.iberdrola.local:1241/projetos/embargos"
    )


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=False
    )