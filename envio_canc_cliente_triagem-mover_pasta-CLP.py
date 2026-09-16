import time
import datetime
import subprocess


def executor01():
    ultimo_mover_pastas = -1
    ultimo_etl_cliente = -1

    while True:
        agora = datetime.datetime.now()

        # Segunda às 04:00 MOVER_PASTAS
        if (
            agora.weekday() == 0
            and agora.hour == 4
            and agora.minute == 0
            and ultimo_mover_pastas != agora.timetuple().tm_yday
        ):
            print("Executando [MOVER_PASTAS]")

            try:
                subprocess.run(["python", "mover_pastas.py"], check=True)

                print("Processo executado com sucesso [MOVER_PASTAS]!")

            except Exception:
                print("Erro ao executar [MOVER_PASTAS]!")

            ultimo_mover_pastas = agora.timetuple().tm_yday

        # Segunda às 05:00 ETL_CANC_CLIENTE
        if (
            agora.weekday() == 0
            and agora.hour == 5
            and agora.minute == 0
            and ultimo_etl_cliente != agora.timetuple().tm_yday
        ):
            print("Executando [ETL_CANC_CLIENTE]")

            try:
                subprocess.run(["python", "envio_canc_cliente_triagem.py"], check=True)

                print("Processo executado com sucesso [ETL_CANC_CLIENTE]!")

            except Exception:
                print("Erro ao executar [ETL_CANC_CLIENTE]!")

            ultimo_etl_cliente = agora.timetuple().tm_yday

        time.sleep(30)


if __name__ == "__main__":
    executor01()
