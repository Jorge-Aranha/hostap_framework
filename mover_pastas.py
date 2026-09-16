import os, zipfile, time, shutil
from datetime import datetime

TEMPORARIO_ZIP = r"C:\Users\u620433\OneDrive - IBERDROLA S.A\EMBARGO_EMB_CLIENTE\EMB_CLIENTE_CANC\V_ENV\TEMPORARIO_ZIP"
END_ZIP = r"C:\Users\u620433\OneDrive - IBERDROLA S.A\EMBARGO_EMB_CLIENTE\EMB_CLIENTE_CANC\G_ENV\END_ZIP"
TEMP_ZIP = r"C:\Users\u620433\OneDrive - IBERDROLA S.A\EMBARGO_EMB_CLIENTE\EMB_CLIENTE_CANC\V_ENV\TEMP_ZIP"
POSTAR_ZIP = r"C:\Users\u620433\OneDrive - IBERDROLA S.A\EMBARGO_EMB_CLIENTE\EMB_CLIENTE_CANC\V_ENV\TEMP_ZIP"

for pasta in [TEMPORARIO_ZIP, END_ZIP, TEMP_ZIP, POSTAR_ZIP]:
    os.makedirs(pasta, exist_ok=True)


def mover_zips():
    print("Movendo arquivos para END_ZIP")

    for arquivo in os.listdir(TEMPORARIO_ZIP):
        if arquivo.lower().endswith(".zip"):

            origem = os.path.join(TEMPORARIO_ZIP, arquivo)
            destino = os.path.join(END_ZIP, arquivo)

            try:
                shutil.move(origem, destino)
                print(f"Movido {arquivo}")
            except Exception as e:
                print(f"Erro ao mover {arquivo}: {e}")

    time.sleep(10)

    sincronizar_zips()


def sincronizar_zips():

    print("Sincronizando END_ZIP -> TEMP_ZIP")

    arquivos_temp = {
        f.lower() for f in os.listdir(TEMP_ZIP) if f.lower().endswith(".zip")
    }

    for arquivo in os.listdir(END_ZIP):

        if not arquivo.lower().endswith(".zip"):
            continue

        if arquivo.lower() not in arquivos_temp:

            origem = os.path.join(END_ZIP, arquivo)
            destino = os.path.join(TEMP_ZIP, arquivo)

            try:
                shutil.copy2(origem, destino)
                print(f"Copiado: {arquivo}")
            except Exception as e:
                print(f"Erro ao copiar {arquivo}: {e}")

        else:
            print(f"Já existe: {arquivo}")


executado = False
def agendador():
    global executado

    while True:
        agora = datetime.now()
        
        if (
            agora.weekday() == 6 and  #DIA - HORA - MINUTO - SEG definir
            agora.hour == 8 and
            agora.minute == 30 and # alterar e verificar
            not executado
        ):

            mover_zips()
            executado = True

        time.sleep(1)


if __name__ == "__main__":
    print("Aguardando execucao")
    agendador()
