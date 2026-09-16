import sys
import os

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, BASE_DIR)

from priv.conexao import con
import csv
from datetime import datetime
import time

TEMPORARIO = r"C:\Users\u620433\OneDrive - IBERDROLA S.A\EMBARGO_EMB_CLIENTE\EMB_CLIENTE_CANC\V_ENV\TEMPORARIO_CSV_AMB"
END = r"C:\Users\u620433\OneDrive - IBERDROLA S.A\EMBARGO_EMB_CLIENTE\EMB_CLIENTE_CANC\G_ENV\END_CSV_AMB"

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

        print('Extraindo Select')

        conn = con()
        cursor = conn.cursor()

        cursor.execute ("""
            WITH MAIN_ENVIO_CANC_CLIENTE_AMBIENTAL AS (
            SELECT
            eacn.*,
            municipio.GER
            FROM U620433.EMB_AVRES_CLIENTE_NCLB eacn
            LEFT JOIN CLB354074.SAP_CCS_NOTA nota ON
				eacn.NOTA = nota.NOTA
			LEFT JOIN CLB354074.SAP_CCS_ENDERECO endereco ON
				nota.NUM_ENDERECO = endereco.NUM_ENDERECO
			LEFT JOIN CLB354074.MUNICIPIO municipio ON
				endereco.MUNICIPIO = municipio.MUN_CCS
            WHERE
            eacn.ACAO IN ('CANCELAR')
            AND eacn.FINALIZADA_NT NOT IN (TRUE)
            AND EXISTS (SELECT 1 FROM U621267.PRD_SEP_MEDIDAS_NINTERRP psmn WHERE eacn.NOTA = psmn.NOTA AND psmn.CONCLUIDA_EM IS NULL AND psmn.ID_MEDIDA IN (0027,0127)))
            SELECT *
            FROM MAIN_ENVIO_CANC_CLIENTE_AMBIENTAL
        """)

        colunas = [desc[0] for desc in cursor.description]
        linhas = cursor.fetchall()

        if not linhas:
            print("Não há dados")
            cursor.close()
            conn.close()
            return

        tabela = "MAIN_ENVIO_CANC_CLIENTE_AMBIENTAL"

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
    # Domingo às 04:30hrs
    executar_processo()