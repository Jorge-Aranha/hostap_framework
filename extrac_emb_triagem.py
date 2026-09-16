import pandas as pd
from conexao import con
import time
from datetime import datetime
import os

def select():

    conn = con()

    sql = """
    SELECT "NOTA", "ORDEM_MEDIDA", "ID_MEDIDA",
           "USUARIO_CRIA", "DT_CRIA",
           "USUARIO_CONC", "DT_CONC",
           "NINTERRP" , "NINTERRP_AMB" , "REVIORCM" ,"AV_EMB_CLIENTE"
    FROM (
        SELECT
            M.NOTA,
            M.ORDEM_MEDIDA,
            M.ID_MEDIDA,
            M.USUARIO_CRIA,
            M.DT_CRIA,
            M.USUARIO_CONC,
            M.DT_CONC,
            CASE
                WHEN EXISTS (
                    SELECT 1
                    FROM U621267.PRD_SEP_MEDIDAS_NINTERRP psmn
                    WHERE M.NOTA = psmn.NOTA
                    AND psmn.CONCLUIDA_EM IS NULL
                ) THEN TRUE
                ELSE FALSE
            END AS NINTERRP,
            CASE
                WHEN EXISTS (
                    SELECT 1
                    FROM CLB354074.PRD_INS_SEP_REVISAO_ABERTA pisra
                    WHERE M.NOTA = pisra.NOTA
                ) THEN TRUE
                ELSE FALSE
            END AS REVIORCM,
    		CASE
				WHEN EXISTS (SELECT 1 FROM U621267.PRD_SEP_MEDIDAS_NINTERRP psmn WHERE M.NOTA = psmn.NOTA AND psmn.CONCLUIDA_EM IS NULL AND psmn.ID_MEDIDA IN (0027,0127)) 
				THEN TRUE
				ELSE FALSE
			END AS "NINTERRP_AMB",
			CASE
				WHEN EXISTS (SELECT 1 FROM U620433.EMB_AVRES_CLIENTE_NCLB eacn WHERE M.NOTA = eacn.NOTA AND eacn.CONCLUIDA_EM IS NULL AND eacn.ACAO IN ('CANCELAR')) 
				THEN TRUE
				ELSE FALSE
			END AS "AV_EMB_CLIENTE",
            ROW_NUMBER() OVER (
                PARTITION BY M.NOTA
                ORDER BY M.ORDEM_MEDIDA DESC
            ) AS RN
        FROM CLB354074.SAP_CCS_MEDIDA M
        WHERE M.GRUPO_MEDIDA = 'OBRACANC'
          AND M.ELIMINADO IS NULL
          AND M.DT_CONC IS NULL
          AND M.ID_MEDIDA IN ('0032','0033')
    )
    WHERE RN = 1
    """

    df = pd.read_sql(sql, conn)

    conn.close()

    return df


def excel():
    try:
        arquivo = (
            r"C:\Users\u620433\OneDrive - IBERDROLA S.A" r"\OBRACANC\obracanc_view.xlsx"
        )

        df = select()

        with pd.ExcelWriter(arquivo, engine="openpyxl", mode="w") as writer:

            df.to_excel(writer, index=False, sheet_name="Dados")
            print(f"Registros: {len(df)}")

        if df.empty:
            return "Nehum registro"

    except Exception as erro:
        print(f"Erro: {erro}")


ultima_execucao = None


def agendador():
    global ultima_execucao

    while True:

        agora = datetime.now()

        if agora.hour == 4 and agora.minute == 30 and ultima_execucao != agora.date():

            excel()

            ultima_execucao = agora.date()

        time.sleep(30)


if __name__ == "__main__":
    agendador()
