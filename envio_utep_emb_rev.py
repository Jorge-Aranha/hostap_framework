from conexao import con
import os
import csv
from datetime import datetime
import time

TEMPORARIO = r"C:\Users\u620433\OneDrive - IBERDROLA S.A\EMBARGO_EMB\ENVIO_UTEP_EMB_REV\TEMPORARIO"
END = r"C:\Users\u620433\OneDrive - IBERDROLA S.A\EMBARGO_EMB\ENVIO_UTEP_EMB_REV\END"


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

        cursor.execute("""SELECT * FROM U620433.EMB_REV_NCLB""")

        colunas = [desc[0] for desc in cursor.description]
        linhas = cursor.fetchall()

        if not linhas:
            print("Não há dados")
            cursor.close()
            conn.close()
            return

        tabela = "EMB_REV_NCLB"

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

        print("executado")

    except Exception as e:
        print("ERRO:", e)


executado = False


def agendador():
    global executado

    while True:
        agora = datetime.now()

        if (
            agora.weekday() == 0  # DIA - HORA - MINUTO - SEG
            and agora.hour == 4
            and agora.minute == 30
            and not executado
        ):
            executar_processo()

        time.sleep(20)


if __name__ == "__main__":
    print("Aguardando execucao")
    agendador()
