import sys
import os

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..",".."))
sys.path.insert(0, BASE_DIR)

from outros.conexao import con
from datetime import datetime
import time
import win32com.client as win32
from pandas import DataFrame
import os


def destinatarios():
    try:
        conn = con()
        cursor = conn.cursor()
        cursor.execute("""
            WITH MOTIVOS AS (
            SELECT
                PSMN.NOTA,
                PSMN.ORDEM_MEDIDA,
                PSMN.MOTIVO,
                PSMN.CRIADA_EM,
                CASE
                    WHEN PSMN.MOTIVO LIKE '%NAO%OBTIDO%ACESSO%' THEN 15
                    WHEN (
                            PSMN.MOTIVO LIKE '%OUTORGA%'
                    OR PSMN.MOTIVO LIKE '%CLIENTE%'
                    OR PSMN.MOTIVO LIKE '%ART%MEMORIAL%'
                    OR PSMN.MOTIVO LIKE '%ART%'
                    OR PSMN.MOTIVO LIKE '%MEMORIAL%'
                    OR PSMN.MOTIVO LIKE '%DOCUMENTACAO%CONTRATO%'
                    OR PSMN.MOTIVO LIKE '%PONTO%ENTREGA%'
                        ) THEN 60
                    ELSE NULL
                END AS DIAS_PRAZO_VENCIMENTO,
                CASE
                    WHEN PSMN.MOTIVO LIKE '%NAO%OBTIDO%ACESSO%' THEN 10
                    WHEN (
                            PSMN.MOTIVO LIKE '%OUTORGA%'
                    OR PSMN.MOTIVO LIKE '%CLIENTE%'
                    OR PSMN.MOTIVO LIKE '%ART%MEMORIAL%'
                    OR PSMN.MOTIVO LIKE '%ART%'
                    OR PSMN.MOTIVO LIKE '%MEMORIAL%'
                    OR PSMN.MOTIVO LIKE '%DOCUMENTACAO%CONTRATO%'
                    OR PSMN.MOTIVO LIKE '%PONTO%ENTREGA%'
                        ) THEN 55
                    ELSE NULL
                END AS DIAS_PRAZO_A_VENCER
            FROM
                U621267.PRD_SEP_MEDIDAS_NINTERRP PSMN
            WHERE
                PSMN.CONCLUIDA_EM IS NULL
            ),
            ULTIMA_SOLICITACAO AS (
            SELECT
                PES.NOTA,
                MAX(PES.SOLICITADO_EM) AS ULTIMA_SOLICITACAO
            FROM
                U621267.PRD_EMB_SOLICITACAO PES
            WHERE
                PES.AVALIACAO = 'PROCEDENTE'
            GROUP BY
                PES.NOTA
            ),
            GERAL AS (
            SELECT
                M.NOTA,
                M.ORDEM_MEDIDA,
                M.MOTIVO,
                M.CRIADA_EM,
                ADD_DAYS(M.CRIADA_EM, M.DIAS_PRAZO_VENCIMENTO) AS DT_VENCIMENTO,
                CASE
                    WHEN DAYS_BETWEEN(M.CRIADA_EM, CURRENT_DATE) >= M.DIAS_PRAZO_VENCIMENTO
                            THEN 'VENCIDO'
                    WHEN DAYS_BETWEEN(M.CRIADA_EM, CURRENT_DATE) BETWEEN (M.DIAS_PRAZO_VENCIMENTO - 5) AND (M.DIAS_PRAZO_VENCIMENTO - 1)
                            THEN 'A VENCER'
                    ELSE 'DENTRO DO PRAZO'
                END AS PRAZO,
                CASE
                    WHEN AUU.DESABILITADO_EM IS NULL
                        THEN AUU.NOME_COMPLETO
                    ELSE (
                    SELECT
                        AUU2.NOME_COMPLETO
                    FROM
                        U621267.ADM_USR_USUARIOS AUU2
                    WHERE
                        AUU.LIDER_EMAIL = AUU2.EMAIL)
                END AS NOME_COMPLETO,
                CASE
                    WHEN AUU.DESABILITADO_EM IS NULL
                        THEN PES.EMAIL_SOLICITANTE
                    WHEN AUU.DESABILITADO_EM IS NOT NULL
                        THEN AUU.LIDER_EMAIL
                    ELSE NULL
                END AS EMAIL_SOLICITANTE,
                CASE
                    WHEN AUU.DESABILITADO_EM IS NULL
                        THEN AUU.LIDER_EMAIL
                    WHEN AUU.DESABILITADO_EM IS NOT NULL
                        THEN NULL
                    ELSE NULL
                END AS LIDER_EMAIL,
                CAST(PES.SOLICITADO_EM AS DATE) AS DATA_SOLICITADO,
                DAYS_BETWEEN(CAST(PES.SOLICITADO_EM AS DATE), CURRENT_DATE) AS DIAS_SOL,
                DAYS_BETWEEN(M.CRIADA_EM, CURRENT_DATE) AS DIAS_EMB,
                M.DIAS_PRAZO_VENCIMENTO,
                M.DIAS_PRAZO_A_VENCER
            FROM
                MOTIVOS M
            INNER JOIN ULTIMA_SOLICITACAO US
                    ON
                M.NOTA = US.NOTA
            RIGHT JOIN U621267.PRD_EMB_SOLICITACAO PES
                    ON
                PES.NOTA = US.NOTA
                AND PES.SOLICITADO_EM = US.ULTIMA_SOLICITACAO
                AND PES.AVALIACAO = 'PROCEDENTE'
            LEFT JOIN U621267.ADM_USR_USUARIOS AUU
                    ON
                PES.EMAIL_SOLICITANTE = AUU.EMAIL
            WHERE
                M.DIAS_PRAZO_VENCIMENTO IS NOT NULL
            )
            SELECT
                GERAL.NOTA,
                GERAL.ORDEM_MEDIDA,
                GERAL.MOTIVO,
                GERAL.CRIADA_EM,
                GERAL.DT_VENCIMENTO,
                GERAL.PRAZO,
                GERAL.NOME_COMPLETO,
                GERAL.EMAIL_SOLICITANTE,
                GERAL.LIDER_EMAIL
            FROM
                GERAL
            WHERE
                GERAL.DIAS_EMB >= GERAL.DIAS_PRAZO_A_VENCER
                AND GERAL.DIAS_SOL >= GERAL.DIAS_PRAZO_A_VENCER
	            AND GERAL.MOTIVO IN ('NAO OBTIDO VIA DE ACESSO');
        """)
        resultado = cursor.fetchall()
        colunas = [c[0] for c in cursor.description]
        cursor.close()
        conn.close()

        Dt = DataFrame(resultado, columns=colunas)

        return Dt
    except Exception as e:
        print(f"Erro: {e}")


def enviar_email():
    resultados = []
    df = destinatarios()

    for _, linha in df.iterrows():
        nota = linha["NOTA"]
        ordem = linha["ORDEM_MEDIDA"]
        email_to = linha["EMAIL_SOLICITANTE"]
        email_cc = linha["LIDER_EMAIL"]

        try:
            outlook = win32.Dispatch("Outlook.Application")
            email = outlook.CreateItem(0)

            email.To = email_to
            email.CC = email_cc

            email.Subject = "Notificação: Solicitações de Embargo"

            with open(
                r"C:\Users\u620433\OneDrive - IBERDROLA S.A\HOSTAP\OUTRO\projetos\projetos_one\static\html\index.html",
                "r",
                encoding="utf-8",
            ) as f:
                html = f.read()

            html = html.replace("{{NOTA}}", str(nota))
            html = html.replace("{{ORDEM}}", str(ordem))
            html = html.replace("{{MOTIVO}}", str(linha["MOTIVO"]))
            html = html.replace(
                "{{CRIADA_EM}}", linha["CRIADA_EM"].strftime("%d/%m/%Y")
            )
            html = html.replace(
                "{{DT_VENCIMENTO}}", linha["DT_VENCIMENTO"].strftime("%d/%m/%Y")
            )
            html = html.replace("{{PRAZO}}", str(linha["PRAZO"]))
            html = html.replace("{{NOME_COMPLETO}}", str(linha["NOME_COMPLETO"]))

            anexo = email.Attachments.Add(
                r"C:\Users\u620433\OneDrive - IBERDROLA S.A\HOSTAP\OUTRO\projetos\projetos_one\static\mage\neo.png"
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

            evidencia_envio(ultimo_email, nota, ordem)

            log_execucao(
                "SUCESSO",
                nota,
                ordem,
                linha["MOTIVO"],
                linha["NOME_COMPLETO"],
                email_to,
                "Email enviado com sucesso",
            )

            resultados.append(
                {
                    "DATA_HORA": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
                    "STATUS": "SUCESSO",
                    "NOTA": nota,
                    "ORDEM": ordem,
                    "MOTIVO": linha["MOTIVO"],
                    "NOME": linha["NOME_COMPLETO"],
                    "EMAIL": email_to,
                    "DETALHE": "Email enviado com sucesso",
                }
            )

            print("E-mail enviado com sucesso!")

        except Exception as e:

            registrar_erro(nota, ordem, linha["MOTIVO"], email_to, str(e))

            log_execucao(
                "ERRO",
                nota,
                ordem,
                linha["MOTIVO"],
                linha["NOME_COMPLETO"],
                email_to,
                str(e),
            )

            resultados.append(
                {
                    "DATA_HORA": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
                    "STATUS": "ERRO",
                    "NOTA": nota,
                    "ORDEM": ordem,
                    "MOTIVO": linha["MOTIVO"],
                    "NOME": linha["NOME_COMPLETO"],
                    "EMAIL": email_to,
                    "DETALHE": str(e),
                }
            )

            print(f"Erro ao enviar e-mail: {e}")

    gerar_csv_execucao(resultados)


def evidencia_envio(email_enviado, nota, ordem):

    pasta = (
        r"C:\Users\u620433\OneDrive - IBERDROLA S.A\EMBARGO_HOSTAP\EMB_PROCESSOS\EMB_NOTFICACAO\EMB_NOTIFICACAO_SOLICITACAO\MSG"
    )

    os.makedirs(pasta, exist_ok=True)

    data_envio = email_enviado.SentOn.strftime("%Y-%m-%d_%H%M%S")

    caminho = os.path.join(pasta, f"EMB_{nota}_{ordem}_{data_envio}.msg")

    email_enviado.SaveAs(caminho)

    print(f"Evidência salva: {caminho}")


def registrar_erro(nota, ordem, motivo, email, erro):

    pasta = r"C:\Users\u620433\OneDrive - IBERDROLA S.A\EMBARGO_HOSTAP\EMB_PROCESSOS\EMB_NOTFICACAO\EMB_NOTIFICACAO_SOLICITACAO\LOG\ERRO"

    os.makedirs(pasta, exist_ok=True)

    arquivo = os.path.join(
        pasta, f"ERRO_{nota}_{datetime.now().strftime('%Y-%m-%d_%H%M%S')}.txt"
    )

    with open(arquivo, "w", encoding="utf-8") as f:

        f.write("RELATÓRIO DE ERRO\n")
        f.write("=" * 20 + "\n")
        f.write(f"Data/Hora: {datetime.now()}\n")
        f.write(f"Nota: {nota}\n")
        f.write(f"Ordem: {ordem}\n")
        f.write(f"Motivo: {motivo}\n")
        f.write(f"Email: {email}\n")
        f.write(f"Descrição: {erro}\n")


def log_execucao(status, nota, ordem, motivo, nome, email, detalhe):

    pasta = (
        r"C:\Users\u620433\OneDrive - IBERDROLA S.A\EMBARGO_HOSTAP\EMB_PROCESSOS\EMB_NOTFICACAO\EMB_NOTIFICACAO_SOLICITACAO\LOG\END"
    )

    os.makedirs(pasta, exist_ok=True)

    arquivo = os.path.join(
        pasta, f"LOG_{nota}_{ordem}_{datetime.now().strftime('%Y-%m-%d_%H%M%S')}.txt"
    )

    with open(arquivo, "w", encoding="utf-8") as f:

        f.write("RELATÓRIO LOG\n")
        f.write("=" * 20 + "\n")
        f.write(f"Data/Hora: {datetime.now()}\n")
        f.write(f"Status: {status}\n")
        f.write(f"Nota: {nota}\n")
        f.write(f"Ordem: {ordem}\n")
        f.write(f"Motivo: {motivo}\n")
        f.write(f"Nome: {nome}\n")
        f.write(f"Email: {email}\n")
        f.write(f"Detalhe: {detalhe}\n")


def gerar_csv_execucao(resultados):

    pasta = (
        r"C:\Users\u620433\OneDrive - IBERDROLA S.A\EMBARGO_HOSTAP\EMB_PROCESSOS\EMB_NOTFICACAO\EMB_NOTIFICACAO_SOLICITACAO\LOG\CSV"
    )

    os.makedirs(pasta, exist_ok=True)

    arquivo = os.path.join(
        pasta, f"RES_{datetime.now().strftime('%Y-%m-%d_%H%M%S')}.csv"
    )

    df = DataFrame(resultados)

    df.to_csv(arquivo, sep=";", index=False, encoding="utf-8-sig")

    print(f"CSV gerado: {arquivo}")


ultima_execucao = None


def agendador():
    global ultima_execucao

    while True:

        agora = datetime.now()

        if agora.hour == 8 and agora.minute == 25 and ultima_execucao != agora.date():

            enviar_email()

            ultima_execucao = agora.date()

        time.sleep(30)


if __name__ == "__main__":
    print("Aguardando execucao")
    agendador()