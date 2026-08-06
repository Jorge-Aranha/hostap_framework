import sys
import os

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, BASE_DIR)

from priv.conexao import con
import csv
from datetime import datetime
import time

#Dir
TEMPORARIO = r"C:\Users\u620433\OneDrive - IBERDROLA S.A\EMBARGO_EMB_CLIENTE\EMB_CLIENTE_FALHA_BLOQUEIO\TEMPORARIO"
END = r"C:\Users\u620433\OneDrive - IBERDROLA S.A\EMBARGO_EMB_CLIENTE\EMB_CLIENTE_FALHA_BLOQUEIO\END"
#Log
executado = False

#Def
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
            WITH MAIN_ENVIO_CLIENTE_FALHA_BLOQUEIO AS (
            SELECT *
            FROM U620433.EMB_AVRES_CLIENTE_NCLB eacn
            WHERE
            eacn.STATUS IN ('FALHA','BLOQUEIO')
            AND eacn.FINALIZADA_MDD NOT IN (TRUE)
            )
            SELECT *
            FROM MAIN_ENVIO_CLIENTE_FALHA_BLOQUEIO
            """)

        colunas = [desc[0] for desc in cursor.description]
        linhas = cursor.fetchall()

        if not linhas:
            print("Não há dados")
            cursor.close()
            conn.close()
            return

        tabela = "CLIENTE_FALHA_BLOQUEIO"

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
def agendador():
    global executado

    while True:
        agora = datetime.now()

        if (
            agora.weekday() == 0 and  #DIA - HORA - MINUTO - SEG
            agora.hour == 8 and
            agora.minute == 20 and
            not executado
        ):

            executar_processo()
            executado = True

        time.sleep(30)
if __name__ == "__main__":
    print("Aguardando execucao")
    agendador() 