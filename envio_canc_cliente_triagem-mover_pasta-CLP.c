#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include <windows.h>

int executar_python(char* script)
{
    STARTUPINFO si;
    PROCESS_INFORMATION pi;

    ZeroMemory(&si, sizeof(si));
    si.cb = sizeof(si);

    ZeroMemory(&pi, sizeof(pi));

    char comando[512];
    sprintf(comando, "python %s", script);

    if (!CreateProcess(
        NULL,
        comando,
        NULL,
        NULL,
        FALSE,
        0,
        NULL,
        NULL,
        &si,
        &pi))
    {
        printf("Erro CreateProcess: %lu\n", GetLastError());
        return -1;
    }

    WaitForSingleObject(pi.hProcess, INFINITE);

    DWORD exitCode;
    GetExitCodeProcess(pi.hProcess, &exitCode);

    CloseHandle(pi.hProcess);
    CloseHandle(pi.hThread);

    return (int)exitCode;
}

int main()
{
    int ultimo_mover_pastas = -1;
    int ultimo_etl_cliente = -1;

    while (1)
    {
        time_t t = time(NULL);
        struct tm* agora = localtime(&t);

        if (agora->tm_wday == 1 && // Segunda às 04:00 MOVER_PASTAS
            agora->tm_hour == 4 &&
            agora->tm_min == 0 &&
            ultimo_mover_pastas != agora->tm_yday)
        {
            printf("Executando [MOVER_PASTAS]\n");

            int status = executar_python("mover_pastas.py");

            if (status == 0)
            {
                printf("Processo executado com sucesso [MOVER_PASTAS]!\n");
            }
            else
            {
                printf("Erro ao executar [MOVER_PASTAS]!\n");
            }

            ultimo_mover_pastas = agora->tm_yday;
        }

        if (agora->tm_wday == 1 && // Segunda às 05:00 ETL_CANC_CLIENTE
            agora->tm_hour == 5 &&
            agora->tm_min == 0 &&
            ultimo_etl_cliente != agora->tm_yday)
        {
            printf("Executando [ETL_CANC_CLIENTE]\n");

            int status = executar_python("envio_canc_cliente_triagem.py");

            if (status == 0)
            {
                printf("Processo executado com sucesso [ETL_CANC_CLIENTE]!\n");
            }
            else
            {
                printf("Erro ao executar [ETL_CANC_CLIENTE]!\n");
            }

            ultimo_etl_cliente = agora->tm_yday;
        }

        Sleep(30000);
    }

    return 0;
}