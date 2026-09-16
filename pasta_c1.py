import os
import zipfile
from datetime import datetime

PASTA_INPUT = r"C:\Users\u620433\Pictures\Screenshots"
PASTA_OUTPUT = r"C:\Users\u620433\OneDrive - IBERDROLA S.A\EMBARGO_HOSTAP\EMB_PROCESSOS\EMB_CLIENTE\EMB_CLIENTE_CANC\TEMPORARIO_FIXO\TEMPORARIO_ZIP"

def criar_zip(nota, ordem):
    os.makedirs(PASTA_OUTPUT, exist_ok=True)

    agora = datetime.now()
    data = agora.strftime("%Y-%m-%d-%H-%M-%S")

    nome_zip = f"{nota}_{ordem}_{data}.zip"
    caminho_zip = os.path.join(PASTA_OUTPUT, nome_zip)

    arquivos = [
        f for f in os.listdir(PASTA_INPUT)
        if f.lower().endswith((".png",".jpg",".jpeg",".txt",".pdf",".docx",".msg",".html",".eml"))
    ]

    if not arquivos:
        print(f"Não feito: {nota} - {ordem}")
        return "Sem arquivos"

    with zipfile.ZipFile(caminho_zip, 'w') as zipf:
        for arquivo in arquivos:
            caminho_arquivo = os.path.join(PASTA_INPUT, arquivo)
            zipf.write(caminho_arquivo, arcname=arquivo)

    for arquivo in arquivos:
        try:
            os.remove(os.path.join(PASTA_INPUT, arquivo))
        except:
            pass

    print(f"ZIP gerado: {nota} - {ordem}")
    return caminho_zip