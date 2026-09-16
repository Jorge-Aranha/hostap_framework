#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include <windows.h>

int main()
{
    int ultimo_etl = -1;

    while (1)
    {
        time_t t = time(NULL);
        struct tm* agora = localtime(&t);

        if (agora->tm_wday >= 1 && agora->tm_wday <=5 &&// Seg a Sext às 17:00 
            agora->tm_hour == 17 &&
            agora->tm_min == 0 &&
            ultimo_etl != agora->tm_yday)

            {
                printf("Executando [ELT_AREAS_CONC]\n");

                int status = system("python etl_areas_conc.py");

                if (status == 0)
                {
                    printf("Processo executado com sucesso [ELT_AREAS_CONC]!\n");
                }
                else
                {
                    printf("Erro ao executar [ELT_AREAS_CONC]!\n");
                }

                ultimo_etl = agora->tm_yday;
            }

        Sleep(30000);
    }

    return 0;
}