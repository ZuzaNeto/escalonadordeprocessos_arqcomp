#include <stdio.h>
#include <stdlib.h>
#include <string.h>

typedef struct {
    char pid[10];
    int duracao;
    int chegada;
    int restante;
    int inicio;
    int fim;
    int tempo_espera;
    int tempo_turnaround;
    int tempo_resposta;
} Processo;

void ordenar_por_chegada(Processo processos[], int n) {
    for (int i = 0; i < n - 1; i++) {
        for (int j = i + 1; j < n; j++) {
            if (processos[i].chegada > processos[j].chegada) {
                Processo temp = processos[i];
                processos[i] = processos[j];
                processos[j] = temp;
            }
        }
    }
}

void executar_fifo(Processo processos[], int n) {
    ordenar_por_chegada(processos, n);
    int tempo_atual = 0;
    for (int i = 0; i < n; i++) {
        processos[i].inicio = tempo_atual;
        processos[i].fim = tempo_atual + processos[i].duracao;
        processos[i].tempo_espera = tempo_atual - processos[i].chegada;
        processos[i].tempo_turnaround = processos[i].tempo_espera + processos[i].duracao;
        processos[i].tempo_resposta = processos[i].tempo_espera;
        tempo_atual = processos[i].fim;
    }
}

void executar_sjf(Processo processos[], int n) {
    ordenar_por_chegada(processos, n);
    int tempo_atual = 0;
    int processados = 0;
    int visitado[n];
    memset(visitado, 0, sizeof(visitado));

    while (processados < n) {
        int menor_duracao = 999999;
        int indice = -1;

        for (int i = 0; i < n; i++) {
            if (!visitado[i] && processos[i].chegada <= tempo_atual && processos[i].duracao < menor_duracao) {
                menor_duracao = processos[i].duracao;
                indice = i;
            }
        }

        if (indice != -1) {
            processos[indice].inicio = tempo_atual;
            processos[indice].fim = tempo_atual + processos[indice].duracao;
            processos[indice].tempo_espera = tempo_atual - processos[indice].chegada;
            processos[indice].tempo_turnaround = processos[indice].tempo_espera + processos[indice].duracao;
            processos[indice].tempo_resposta = processos[indice].tempo_espera;
            tempo_atual = processos[indice].fim;
            visitado[indice] = 1;
            processados++;
        } else {
            tempo_atual++;
        }
    }
}

void exibir_resultados(Processo processos[], int n) {
    printf("\nResultados:\n");
    printf("PID\tDuracao\tChegada\tEspera\tTurnaround\tResposta\n");
    for (int i = 0; i < n; i++) {
        printf("%s\t%d\t%d\t%d\t%d\t\t%d\n", processos[i].pid, processos[i].duracao, processos[i].chegada,
               processos[i].tempo_espera, processos[i].tempo_turnaround, processos[i].tempo_resposta);
    }
}

int main() {
    int n;
    printf("Digite o número de processos: ");
    scanf("%d", &n);

    Processo processos[n];
    for (int i = 0; i < n; i++) {
        printf("\nDigite o PID do processo %d: ", i + 1);
        scanf("%s", processos[i].pid);
        printf("Digite a duração do processo %d: ", i + 1);
        scanf("%d", &processos[i].duracao);
        printf("Digite o tempo de chegada do processo %d: ", i + 1);
        scanf("%d", &processos[i].chegada);
        processos[i].restante = processos[i].duracao;
        processos[i].inicio = -1;
    }

    printf("\nEscolha o algoritmo de escalonamento:\n1. FIFO\n2. SJF\nOpção: ");
    int opcao;
    scanf("%d", &opcao);

    if (opcao == 1) {
        executar_fifo(processos, n);
    } else if (opcao == 2) {
        executar_sjf(processos, n);
    } else {
        printf("Opção inválida!\n");
        return 1;
    }

    exibir_resultados(processos, n);
    return 0;
}
