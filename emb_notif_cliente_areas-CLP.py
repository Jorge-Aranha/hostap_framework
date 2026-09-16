import time
import datetime
import subprocess


def executor01():
    ultimo_etl_emb_notif_cliente_areas = -1
    ultimo_emb_notif_cliente_areas = -1

    while True:
        agora = datetime.datetime.now()

        # Domingo às 05:00 EMB_NOTIF_CLIENTE_AREAS_ETL
        if (
            agora.weekday() == 6
            and agora.hour == 5
            and agora.minute == 0
            and ultimo_etl_emb_notif_cliente_areas != agora.timetuple().tm_yday
        ):
            print("Executando [EMB_NOTIF_CLIENTE_AREAS_ETL]")

            try:
                subprocess.run(["python", "etl_emb_notif_cliente_areas.py"], check=True)

                print("Processo executado com sucesso [EMB_NOTIF_CLIENTE_AREAS]!")

            except Exception:
                print("Erro ao executar [EMB_NOTIF_CLIENTE_AREAS]!")

            ultimo_etl_emb_notif_cliente_areas = agora.timetuple().tm_yday

        # Domingo às 06:00 EMB_NOTIF_CLIENTE_AREAS
        if (
            agora.weekday() == 6
            and agora.hour == 6
            and agora.minute == 0
            and ultimo_emb_notif_cliente_areas != agora.timetuple().tm_yday
        ):
            print("Executando [EMB_NOTIF_CLIENTE_AREAS]")

            try:
                subprocess.run(["python", "emb_notif_cliente_areas.py"], check=True)

                print("Processo executado com sucesso [EMB_NOTIF_CLIENTE_AREAS]!")

            except Exception:
                print("Erro ao executar [EMB_NOTIF_CLIENTE_AREAS]!")

            ultimo_emb_notif_cliente_areas = agora.timetuple().tm_yday

        time.sleep(30)


if __name__ == "__main__":
    executor01()
