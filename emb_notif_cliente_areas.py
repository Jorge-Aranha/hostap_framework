import sys
import os

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, BASE_DIR)

from outros.conexao import con
from datetime import datetime
import win32com.client as win32
from pandas import DataFrame
import time


def destinatarios():
    try:
        conn = con()
        cursor = conn.cursor()
        cursor.execute("""
            WITH areas_vinculdas AS (
            SELECT
                psmn.NOTA,
                psmn.ORDEM_MEDIDA,
                UPPER(scn.PARCEIRO || ' ' || gp.TITULO || ' - ' || psmn.ORDEM_MEDIDA) AS CONCATENADO,
                --	RIGHT(UPPER(COALESCE(pc.SOLICITANTE, pp.SOLICITANTE)),10) AS SOLICITANTE,
                SUBSTRING_REGEXPR(
                    '^[^ ]+'
                    IN UPPER(COALESCE(pc.SOLICITANTE, pp.SOLICITANTE))
                )
                || ' ' ||
                SUBSTRING_REGEXPR(
                    '[^ ]+$'
                    IN UPPER(COALESCE(pc.SOLICITANTE, pp.SOLICITANTE))
                ) AS SOLICITANTE,
                scn.PARCEIRO,
                gp.TITULO,
                psmn.TIPO,
                psmn.PROCEDENTE,
                psmn.MOTIVO,
                psmn.CRIADA_EM,
                ADD_DAYS(psmn.CRIADA_EM, 60) AS VENCIMENTO_EM,
                COALESCE (cpc.TP,
                CASE
                    WHEN cpp.TP IS NOT NULL THEN 'PDP'
                    ELSE NULL
                END
                ) AS RESPONSAVEL,
                COALESCE(cpc.EMAIL, cpp.EMAIL) AS EMAIL
            FROM
                U621267.PRD_SEP_MEDIDAS_NINTERRP psmn
            LEFT JOIN CLB354074.SAP_CCS_NOTA scn ON
                psmn.NOTA = scn.NOTA
            LEFT JOIN CLB354074.SAP_CCS_ENDERECO sce ON
                scn.NUM_ENDERECO = sce.NUM_ENDERECO
            LEFT JOIN CLB354074.MUNICIPIO mun ON
                sce.MUNICIPIO = mun.MUN_CCS
            LEFT JOIN U620433.CONSULTOR_PROVISORIO_PDP cpp ON
                scn.PARCEIRO = cpp.PARCEIRO
            LEFT JOIN U620433.CONSULTOR_PROVISORIO_CGR cpc ON
                scn.PARCEIRO = cpc.PARCEIRO
                AND mun.MUN_CCS = cpc.MUNICIPIO
            LEFT JOIN U621267.PRD_CAR_STATUS_ATUAL_EMBARGADAS pcsae
                ON
                psmn.NOTA = pcsae.NOTA
                AND psmn.ORDEM_MEDIDA = pcsae.ORDEM_MEDIDA
            LEFT JOIN CLB354074.GEOEX_PROJETOS gp ON
                gp.NOTAOBRA = psmn.NOTA
            LEFT JOIN U620433.PN_CGR pc ON
                scn.PARCEIRO = pc.PARCEIRO
            LEFT JOIN U620433.PN_PDP pp ON
                scn.PARCEIRO = pp.PARCEIRO
            WHERE
                psmn.CONCLUIDA_EM IS NULL
                AND psmn.TIPO = 'CLIENTE'
                AND psmn.PROCEDENTE = TRUE
            ),
            src AS (
            SELECT
                av.NOTA,
                av.PARCEIRO,
                av.SOLICITANTE,
                av.ORDEM_MEDIDA,
                av.CONCATENADO,
                av.MOTIVO,
                av.CRIADA_EM,
                av.VENCIMENTO_EM,
                CASE
                    WHEN auu.DESABILITADO_EM IS NULL
                        THEN av.EMAIL
                    WHEN auu.DESABILITADO_EM IS NOT NULL
                        THEN auu.LIDER_EMAIL
                    ELSE NULL
                END AS EMAIL,
                COALESCE(auu.LIDER_EMAIL, '')|| ';neviton.oliveira@neoenergia.com' || ';ludimar.gomes@neoenergia.com' || ';ecardoso@neoenergia.com' || ';andre.valerio@neoenergia.com' || ';phablo.oliveira@neoenergia.com' AS LIDER_EMAIL,
                CASE
                    WHEN auu.DESABILITADO_EM IS NULL
                        THEN auu.NOME_COMPLETO
                    ELSE (
                    SELECT
                        auu2.NOME_COMPLETO
                    FROM
                        U621267.ADM_USR_USUARIOS auu2
                    WHERE
                        auu.LIDER_EMAIL = auu2.EMAIL)
                END AS NOME_COMPLETO,
                auu.UNIDADE
            FROM
                areas_vinculdas av
            LEFT JOIN U621267.ADM_USR_USUARIOS auu
                ON
                av.EMAIL = auu.EMAIL
            WHERE
                RESPONSAVEL IS NOT NULL)
            SELECT
                NOTA,
                ORDEM_MEDIDA,
                SOLICITANTE,
                CONCATENADO,
                MOTIVO,
                CRIADA_EM,
                VENCIMENTO_EM,
                EMAIL,
                LIDER_EMAIL,
                NOME_COMPLETO,
                UNIDADE
            FROM
                src
            WHERE
                CRIADA_EM >= ADD_DAYS(CURRENT_DATE, -7)
                AND CRIADA_EM < CURRENT_DATE
            ORDER BY
                PARCEIRO;
        """)
        resultado = cursor.fetchall()
        colunas = [c[0] for c in cursor.description]
        cursor.close()
        conn.close()

        Dt = DataFrame(resultado, columns=colunas)

        return Dt
    except Exception as e:
        print(f"Erro: {e}")


def validar_emails(email_to, email_cc=None):

    import re

    padrao = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"

    if not email_to:
        return False, "EMAIL_DESTINO_VAZIO"

    if not re.match(padrao, email_to):
        return False, f"EMAIL_DESTINO_INVALIDO: {email_to}"

    if email_cc:

        emails_cc = [email.strip() for email in email_cc.split(";") if email.strip()]

        for email in emails_cc:

            if not re.match(padrao, email):

                return False, f"EMAIL_CC_INVALIDO: {email}"

    return True, None


def obter_tentativa(nota, ordem_medida):

    conn = con()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT COALESCE(MAX(TENTATIVAS_ENVIO), 0)
        FROM "U620433"."EMB_NOTIFICACAO_CLIENTE_AREAS"
        WHERE NOTA = ?
          AND ORDEM_MEDIDA = ?
        """,
        (nota, ordem_medida),
    )

    tentativa = cursor.fetchone()[0] + 1

    cursor.close()
    conn.close()

    return tentativa


import hashlib


def gerar_hash(email):

    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")

    dados = f"{email}_{timestamp}"

    hash_valor = hashlib.sha256(dados.encode()).hexdigest()

    return hash_valor


def salvamento_msg(email_enviado, hash_envio):

    pasta_base = r"C:\Users\u620433\OneDrive - IBERDROLA S.A\EMBARGO_HOSTAP\EMB_PROCESSOS\EMB_NOTFICACAO\EMB_NOTIFICACAO_CLIENTE_AREAS\MSG"

    os.makedirs(pasta_base, exist_ok=True)

    data_envio = email_enviado.SentOn.strftime("%Y%m%d_%H%M%S")

    nome_arquivo = f"{data_envio}_{hash_envio[:10]}.msg"

    caminho = os.path.join(pasta_base, nome_arquivo)

    email_enviado.SaveAs(caminho, 3)

    print(f"MSG salvo: {caminho}")

    return caminho


def enviar_email():

    df = destinatarios()

    for (email_to, email_cc, nome), grupo in df.groupby(
        ["EMAIL", "LIDER_EMAIL", "NOME_COMPLETO"]
    ):

        valido, erro = validar_emails(email_to, email_cc)

        if not valido:

            conn = con()
            cursor = conn.cursor()

            for _, linha in grupo.iterrows():

                tentativa = obter_tentativa(linha["NOTA"], linha["ORDEM_MEDIDA"])

                cursor.execute(
                    """
                    INSERT INTO "U620433"."EMB_NOTIFICACAO_CLIENTE_AREAS"
                    (
                        NOTA,
                        ORDEM_MEDIDA,
                        DESTINATARIO,
                        UNIDADE,
                        TIPO_LAYOUT,
                        LOG_ENVIO,
                        TIPO_ERRO,
                        TENTATIVAS_ENVIO
                    )
                    VALUES
                    (
                        ?,
                        ?,
                        ?,
                        ?,
                        ?,
                        ?,
                        ?,
                        ?
                    )
                    """,
                    (
                        linha["NOTA"],
                        linha["ORDEM_MEDIDA"],
                        email_to,
                        linha["UNIDADE"],
                        1,
                        2,
                        erro,
                        tentativa,
                    ),
                )

            conn.commit()

            cursor.close()
            conn.close()

            print(f"[VALIDAR_EMAIL] {erro}")

            continue

        hash_envio = gerar_hash(email_to)

        try:

            outlook = win32.Dispatch("Outlook.Application")

            email = outlook.CreateItem(0)

            email.To = email_to
            email.CC = email_cc

            email.Subject = "Notificação: Embargo Cliente"

            # Prioridade Alta
            # email.Importance = 2
            # Solicitar confirmação de leitura
            email.ReadReceiptRequested = True
            # Solicitar confirmação de entrega
            email.OriginatorDeliveryReportRequested = True

            # email.Importance = 2

            with open(
                r"C:\Users\u620433\OneDrive - IBERDROLA S.A\HOSTAP\OUTRO\projetos\projetos_three\static\html\index.html",
                "r",
                encoding="utf-8",
            ) as f:
                html = f.read()

            linhas_tabela = ""

            for _, linha in grupo.iterrows():

                linhas_tabela += f"""
                <tr>
                    <td align="center" style="white-space: nowrap;font-size: 11px;">{linha['NOTA']}</td>
                    <td align="center" style="white-space: nowrap;font-size: 11px;">{linha['SOLICITANTE']}</td>
                    <td align="center" style="white-space: nowrap;font-size: 11px;">{linha['CONCATENADO']}</td>
                    <td align="center" style="white-space: nowrap;font-size: 11px;">{linha['MOTIVO']}</td>
                    <td align="center" style="white-space: nowrap;font-size: 11px;">{linha['CRIADA_EM'].strftime('%d/%m/%Y')}</td>
                    <td align="center" style="white-space: nowrap;font-size: 11px;">{linha['VENCIMENTO_EM'].strftime('%d/%m/%Y')}</td>
                </tr>
                """

            html = html.replace("{{NOME_COMPLETO}}", str(nome))

            html = html.replace("{{LINHAS_TABELA}}", linhas_tabela)

            html = html.replace("{{HASH}}", hash_envio)

            anexo = email.Attachments.Add(
                r"C:\Users\u620433\OneDrive - IBERDROLA S.A\HOSTAP\OUTRO\projetos\projetos_three\static\mage\neo.png"
            )

            anexo.PropertyAccessor.SetProperty(
                "http://schemas.microsoft.com/mapi/proptag/0x3712001F", "neo_logo"
            )

            email.HTMLBody = html

            # email.Display()
            email.Send()

            time.sleep(5)

            namespace = outlook.GetNamespace("MAPI")

            itens_enviados = namespace.GetDefaultFolder(5)

            itens = itens_enviados.Items
            itens.Sort("[SentOn]", True)

            ultimo_email = itens.GetFirst()

            salvamento_msg(ultimo_email, hash_envio)

            conn = con()
            cursor = conn.cursor()

            for _, linha in grupo.iterrows():

                tentativa = obter_tentativa(linha["NOTA"], linha["ORDEM_MEDIDA"])

                cursor.execute(
                    """
                    INSERT INTO "U620433"."EMB_NOTIFICACAO_CLIENTE_AREAS"
                    (
                        NOTA,
                        ORDEM_MEDIDA,
                        HASH,
                        DESTINATARIO,
                        UNIDADE,
                        TIPO_LAYOUT,
                        LOG_ENVIO,
                        TENTATIVAS_ENVIO,
                        DT_PROCESSAMENTO,
                        DT_ENVIO,
                        DT_ENTREGA
                    )
                    VALUES
                    (
                        ?,
                        ?,
                        ?,
                        ?,
                        ?,
                        ?,
                        ?,
                        ?,
                        CURRENT_UTCTIMESTAMP,
                        CURRENT_UTCTIMESTAMP,
                        CURRENT_UTCTIMESTAMP
                    )
                    """,
                    (
                        linha["NOTA"],
                        linha["ORDEM_MEDIDA"],
                        hash_envio,
                        email_to,
                        linha["UNIDADE"],
                        1,
                        1,
                        tentativa,
                    ),
                )

            conn.commit()

            cursor.close()
            conn.close()

            print(f"Colaborador:{nome} - {len(grupo)} registros\n", "Enviado")

        except Exception as e:

            conn = con()
            cursor = conn.cursor()

            for _, linha in grupo.iterrows():

                tentativa = obter_tentativa(linha["NOTA"], linha["ORDEM_MEDIDA"])

                cursor.execute(
                    """
                    INSERT INTO "U620433"."EMB_NOTIFICACAO_CLIENTE_AREAS"
                    (
                        NOTA,
                        ORDEM_MEDIDA,
                        HASH,
                        DESTINATARIO,
                        UNIDADE,
                        TIPO_LAYOUT,
                        LOG_ENVIO,
                        TIPO_ERRO,
                        TENTATIVAS_ENVIO,
                        DT_PROCESSAMENTO
                    )
                    VALUES
                    (
                        ?,
                        ?,
                        ?,
                        ?,
                        ?,
                        ?,
                        ?,
                        ?,
                        ?,
                        CURRENT_UTCTIMESTAMP
                    )
                    """,
                    (
                        linha["NOTA"],
                        linha["ORDEM_MEDIDA"],
                        hash_envio,
                        email_to,
                        linha["UNIDADE"],
                        1,
                        2,
                        str(e),
                        tentativa,
                    ),
                )

            conn.commit()

            cursor.close()
            conn.close()

            print(f"Erro ao enviar para {email_to}: {e}")


if __name__ == "__main__":
    enviar_email()
