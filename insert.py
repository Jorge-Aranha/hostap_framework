import sys
import os

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, BASE_DIR)

from priv.conexao import con
from pandas import DataFrame
import time

def filtro01 ():
  conn = con()
  cursor = conn.cursor ()
  cursor.execute("""
    WITH e AS (
    SELECT 
    etmcn.NOTA,
    etmcn.ORDEM_MEDIDA
    FROM U620433.EMB_TREAT_MOTIVO_CLIENTE_NCLB etmcn
    LEFT JOIN U620433.EMB_AVRES_CLIENTE eac 
      ON etmcn.NOTA = eac.NOTA AND etmcn.ORDEM_MEDIDA = eac.ORDEM_MEDIDA
    WHERE eac.NOTA IS NULL
    AND eac.ORDEM_MEDIDA IS NULL)
    SELECT * FROM e
    """)
  resultado = cursor.fetchall ()
  colunas = [c[0] for c in cursor.description]
  cursor.close ()
  conn.close()

  Dt = DataFrame(resultado, columns=colunas)

  return Dt

def insert01():
    df = filtro01()

    if df.empty:
            return False

    conn = con()
    cursor = conn.cursor()

    dados = [(row['NOTA'], row['ORDEM_MEDIDA']) for _, row in df.iterrows()]

    try:
      cursor.executemany("""
        INSERT INTO "U620433"."EMB_AVRES_CLIENTE"
        (NOTA, ORDEM_MEDIDA, TIPO, EMAIL_RESPONSAVEL, RESULTADO)
        VALUES (?, ?, '1', NULL, NULL)
      """, dados)
      conn.commit()
      cursor.close()
      conn.close()
      return True
    
    except Exception as e:
        print("Erro ao inserir:", e)
        return False
    
time.sleep(10)

def filtro02 ():
  conn = con()
  cursor = conn.cursor ()
  cursor.execute("""
    WITH b AS (
    SELECT 
    etmcn.NOTA,
    etmcn.ORDEM_MEDIDA
    FROM U620433.EMB_TREAT_MOTIVO_CLIENTE_NCLB etmcn
    WHERE NOT EXISTS (
    SELECT 1 
    FROM U620433.EMB_AVRES_CLIENTE eac
    WHERE eac.NOTA = etmcn.NOTA
    AND eac.ORDEM_MEDIDA = etmcn.ORDEM_MEDIDA
    AND eac.TIPO IN (4,5,8)
    )
    AND etmcn.TEMP_DIAS_EMB > 30
    AND etmcn.STATUS_ENVIO IN ('NAO ENVIAREI')
    )
    SELECT * FROM b;
    """)
  resultado = cursor.fetchall ()
  colunas = [c[0] for c in cursor.description]
  cursor.close ()
  conn.close()

  Dt = DataFrame(resultado, columns=colunas)

  return Dt

def insert02():
    df = filtro02()

    if df.empty:
            return False

    conn = con()
    cursor = conn.cursor()

    dados = [(row['NOTA'], row['ORDEM_MEDIDA']) for _, row in df.iterrows()]

    try:
      cursor.executemany("""
        INSERT INTO "U620433"."EMB_AVRES_CLIENTE"
        (NOTA, ORDEM_MEDIDA, TIPO, EMAIL_RESPONSAVEL, RESULTADO)
        VALUES (?, ?, '5', NULL, NULL)
      """, dados)
      conn.commit()
      cursor.close()
      conn.close()
      return True
    
    except Exception as e:
        print("Erro ao inserir:", e)
        return False
    
time.sleep(10)

def filtro03 ():
  conn = con()
  cursor = conn.cursor ()
  cursor.execute("""
    WITH f AS (
    SELECT 
    etmcn.NOTA,
    etmcn.ORDEM_MEDIDA
    FROM U620433.EMB_TREAT_MOTIVO_CLIENTE_NCLB etmcn
    WHERE NOT EXISTS (
    SELECT 1 
    FROM U620433.EMB_AVRES_CLIENTE eac
    WHERE eac.NOTA = etmcn.NOTA
    AND eac.ORDEM_MEDIDA = etmcn.ORDEM_MEDIDA
    AND eac.TIPO IN (4,5,8)
    )
    AND etmcn.TEMP_DIAS_EMB > 30
    AND etmcn.STATUS_ENVIO IN ('PENDENTE')
    )
    SELECT * FROM f;
    """)
  resultado = cursor.fetchall ()
  colunas = [c[0] for c in cursor.description]
  cursor.close ()
  conn.close()

  Dt = DataFrame(resultado, columns=colunas)

  return Dt

def insert03():
    df = filtro03()

    if df.empty:
            return False

    conn = con()
    cursor = conn.cursor()

    dados = [(row['NOTA'], row['ORDEM_MEDIDA']) for _, row in df.iterrows()]

    try:
      cursor.executemany("""
        INSERT INTO "U620433"."EMB_AVRES_CLIENTE"
        (NOTA, ORDEM_MEDIDA, TIPO, EMAIL_RESPONSAVEL, RESULTADO)
        VALUES (?, ?, '4', NULL, NULL)
      """, dados)
      conn.commit()
      cursor.close()
      conn.close()
      return True
    
    except Exception as e:
        print("Erro ao inserir:", e)
        return False
    
time.sleep(10)

def filtro04 ():
  conn = con()
  cursor = conn.cursor ()
  cursor.execute("""
    WITH a AS (
    SELECT 
    eac.NOTA,
    eac.ORDEM_MEDIDA
    FROM U620433.EMB_AVRES_CLIENTE eac 
    LEFT JOIN U620433.EMB_TREAT_MOTIVO_CLIENTE_NCLB etmcn
    ON eac.NOTA = etmcn.NOTA 
    AND eac.ORDEM_MEDIDA = etmcn.ORDEM_MEDIDA
    WHERE eac.TIPO = 1
    AND NOT EXISTS (
    SELECT 1 
    FROM U620433.EMB_AVRES_CLIENTE e2
    WHERE e2.NOTA = eac.NOTA
    AND e2.ORDEM_MEDIDA = eac.ORDEM_MEDIDA
    AND e2.TIPO IN (4,5,8)
    )
    AND etmcn.TEMP_DIAS_EMB > 30
    AND etmcn.TEMP_DIAS_EMB_ENV > 30
    AND etmcn.STATUS_ENVIO IN ('ENVIADO')
    AND etmcn.METODO_ENVIO IN ('MAN','MKT')
    )
    SELECT * FROM a;
    """)
  resultado = cursor.fetchall ()
  colunas = [c[0] for c in cursor.description]
  cursor.close ()
  conn.close()

  Dt = DataFrame(resultado, columns=colunas)

  return Dt

def insert04():
    df = filtro04()

    if df.empty:
            return False

    conn = con()
    cursor = conn.cursor()

    dados = [(row['NOTA'], row['ORDEM_MEDIDA']) for _, row in df.iterrows()]

    try:
      cursor.executemany("""
        INSERT INTO "U620433"."EMB_AVRES_CLIENTE"
        (NOTA, ORDEM_MEDIDA, TIPO, EMAIL_RESPONSAVEL, RESULTADO)
        VALUES (?, ?, '8', NULL, NULL)
      """, dados)
      conn.commit()
      cursor.close()
      conn.close()
      return True
    
    except Exception as e:
        print("Erro ao inserir:", e)
        return False
    
time.sleep(10)

def filtro05 ():
  conn = con()
  cursor = conn.cursor ()
  cursor.execute("""
    WITH b2 AS (
    SELECT 
    eac.NOTA,
    eac.ORDEM_MEDIDA
    FROM U620433.EMB_AVRES_CLIENTE eac 
    LEFT JOIN U620433.EMB_TREAT_MOTIVO_CLIENTE_NCLB etmcn
    ON eac.NOTA = etmcn.NOTA 
    AND eac.ORDEM_MEDIDA = etmcn.ORDEM_MEDIDA
    WHERE eac.TIPO = 1
    AND NOT EXISTS (
    SELECT 1 
    FROM U620433.EMB_AVRES_CLIENTE e2
    WHERE e2.NOTA = eac.NOTA
    AND e2.ORDEM_MEDIDA = eac.ORDEM_MEDIDA
    AND e2.TIPO IN (4,5,8)
    )
    AND etmcn.MOTIVO = 'PONTO DE ENTREGA'
    )
    SELECT * FROM b2;
    """)
  resultado = cursor.fetchall ()
  colunas = [c[0] for c in cursor.description]
  cursor.close ()
  conn.close()

  Dt = DataFrame(resultado, columns=colunas)

  return Dt

def insert05():
    df = filtro05()

    if df.empty:
            return False

    conn = con()
    cursor = conn.cursor()

    dados = [(row['NOTA'], row['ORDEM_MEDIDA']) for _, row in df.iterrows()]

    try:
      cursor.executemany("""
        INSERT INTO "U620433"."EMB_AVRES_CLIENTE"
        (NOTA, ORDEM_MEDIDA, TIPO, EMAIL_RESPONSAVEL, RESULTADO)
        VALUES (?, ?, '5', NULL, NULL)
      """, dados)
      conn.commit()
      cursor.close()
      conn.close()
      return True
    
    except Exception as e:
        print("Erro ao inserir:", e)
        return False
    
time.sleep(10)

def filtro06 ():
  conn = con()
  cursor = conn.cursor ()
  cursor.execute("""
    WITH a2 AS (
    SELECT 
    DISTINCT             
    eac.NOTA,
    eac.ORDEM_MEDIDA
    FROM U620433.EMB_AVRES_CLIENTE eac 
    LEFT JOIN U620433.EMB_TREAT_MOTIVO_CLIENTE_NCLB etmcn
    ON eac.NOTA = etmcn.NOTA 
    AND eac.ORDEM_MEDIDA = etmcn.ORDEM_MEDIDA
    WHERE eac.TIPO IN (1,4,5)
    AND NOT EXISTS (
    SELECT 1 
    FROM U620433.EMB_AVRES_CLIENTE e2
    WHERE e2.NOTA = eac.NOTA
    AND e2.ORDEM_MEDIDA = eac.ORDEM_MEDIDA
    AND e2.TIPO IN (8)
    )
    AND etmcn.TEMP_DIAS_EMB > 30
    AND etmcn.TEMP_DIAS_EMB_ENV > 30
    AND etmcn.STATUS_ENVIO IN ('ENVIADO')
    AND etmcn.MOTIVO <> 'PONTO DE ENTREGA'
    )
    SELECT * FROM a2;
    """)
  resultado = cursor.fetchall ()
  colunas = [c[0] for c in cursor.description]
  cursor.close ()
  conn.close()

  Dt = DataFrame(resultado, columns=colunas)

  return Dt

def insert06():
    df = filtro06()

    if df.empty:
            return False

    conn = con()
    cursor = conn.cursor()

    dados = [(row['NOTA'], row['ORDEM_MEDIDA']) for _, row in df.iterrows()]

    try:
      cursor.executemany("""
        INSERT INTO "U620433"."EMB_AVRES_CLIENTE"
        (NOTA, ORDEM_MEDIDA, TIPO, EMAIL_RESPONSAVEL, RESULTADO)
        VALUES (?, ?, '8', NULL, NULL)
      """, dados)
      conn.commit()
      cursor.close()
      conn.close()
      return True
    
    except Exception as e:
        print("Erro ao inserir:", e)
        return False
    
time.sleep(10)

def filtro07():
  conn = con()
  cursor = conn.cursor ()
  cursor.execute("""
    WITH a3 AS (
    SELECT 
    eac.NOTA,
    eac.ORDEM_MEDIDA
    FROM U620433.EMB_AVRES_CLIENTE eac 
    LEFT JOIN U620433.EMB_TREAT_MOTIVO_CLIENTE_NCLB etmcn
    ON eac.NOTA = etmcn.NOTA 
    AND eac.ORDEM_MEDIDA = etmcn.ORDEM_MEDIDA
    WHERE eac.TIPO = 1
    AND NOT EXISTS (
    SELECT 1 
    FROM U620433.EMB_AVRES_CLIENTE e2
    WHERE e2.NOTA = eac.NOTA
    AND e2.ORDEM_MEDIDA = eac.ORDEM_MEDIDA
    AND e2.TIPO IN (4,5,8)
    )
    AND etmcn.TEMP_DIAS_EMB > 30
    AND etmcn.TEMP_DIAS_EMB_ENV > 45
    AND etmcn.STATUS_ENVIO IN ('ENVIADO') 
    AND etmcn.METODO_ENVIO IN ('COR')
    )
    SELECT * FROM a3;
    """)
  resultado = cursor.fetchall ()
  colunas = [c[0] for c in cursor.description]
  cursor.close ()
  conn.close()

  Dt = DataFrame(resultado, columns=colunas)

def insert07():
    df = filtro06()

    if df.empty:
            return False

    conn = con()
    cursor = conn.cursor()

    dados = [(row['NOTA'], row['ORDEM_MEDIDA']) for _, row in df.iterrows()]

    try:
      cursor.executemany("""
        INSERT INTO "U620433"."EMB_AVRES_CLIENTE"
        (NOTA, ORDEM_MEDIDA, TIPO, EMAIL_RESPONSAVEL, RESULTADO)
        VALUES (?, ?, '8', NULL, NULL)
      """, dados)
      conn.commit()
      cursor.close()
      conn.close()
      return True
    
    except Exception as e:
        print("Erro ao inserir:", e)
        return False

time.sleep(10)

if __name__ == "__main__":
  while True:
      
      print("-----Iniciando-----")

      if insert01(): print ('Executado 01')

      else: print ('Sem valor 01')

      if insert05(): print ('Executado 05')

      else: print ('Sem valor 05')

      print("-----Pausa BL1-----")

      time.sleep(60)

      if insert02(): print ('Executado 02')

      else: print ('Sem valor 02')

      if insert03(): print ('Executado 03')

      else: print ('Sem valor 03')

      if insert04(): print ('Executado 04')

      else: print ('Sem valor 04')

      if insert07(): print ('Executado 07')

      else: print ('Sem valor 07')

      print("-----Pausa BL2-----")

      time.sleep(100)

      if insert06(): print ('Executado 06')

      else: print ('Sem valor 06')

      print("-----Pausa BL03-----")

      print("------Pausa------")

time.sleep(60)