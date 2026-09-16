import sys
import os

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..",".."))
sys.path.insert(0, BASE_DIR)

from outros.conexao import con
import csv
from datetime import datetime
import time

TEMPORARIO = r"C:\Users\u620433\OneDrive - IBERDROLA S.A\EMBARGO_HOSTAP\EMB_PROCESSOS\EMB_NOTFICACAO\EMB_NOTIFICACAO_CLIENTE_AREAS\CSV\TEMPORARIO"
END = r"C:\Users\u620433\OneDrive - IBERDROLA S.A\EMBARGO_HOSTAP\EMB_PROCESSOS\EMB_NOTFICACAO\EMB_NOTIFICACAO_CLIENTE_AREAS\CSV\END"


def executar_processo():
    try:
        print("Iniciando processo")

        arquivos_csv = [f for f in os.listdir(TEMPORARIO) if f.endswith(".csv")]

        if arquivos_csv:
            for arquivo in arquivos_csv:
                caminho = os.path.join(TEMPORARIO, arquivo)
                try:
                    os.remove(caminho)
                    print(f"Removido: {arquivo}")
                except:
                    print(f"Arquivo em uso (não removido): {arquivo}")
        else:
            print("Nenhum CSV para remover")

        print("Extraindo Select")

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

        colunas = [desc[0] for desc in cursor.description]
        linhas = cursor.fetchall()

        if not linhas:
            print("Não há dados")
            cursor.close()
            conn.close()
            return

        tabela = "PREVIEW_EMB_NOTIF_CLIENTE_AREAS"

        hoje = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
        arquivo_saida = os.path.join(TEMPORARIO, f"{tabela}_{hoje}.csv")
        arquivo_saida_fixo = os.path.join(END, f"{tabela}_{hoje}.csv")

        with open(arquivo_saida, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(colunas)
            writer.writerows(linhas)

        with open(arquivo_saida_fixo, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(colunas)
            writer.writerows(linhas)

        print(f"CSV gerado: {arquivo_saida}")
        print(f"CSV gerado FIXO: {arquivo_saida_fixo}")

        cursor.close()
        conn.close()

    except Exception as e:
        print("ERRO:", e)


if __name__ == "__main__":
    executar_processo()
