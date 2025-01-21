import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt

# Classe para representar um processo
class Processo:
    def __init__(self, pid, duracao, chegada=0):
        self.pid = pid  # Identificador único do processo
        self.duracao = duracao  # Tempo total de execução do processo
        self.chegada = chegada  # Tempo de chegada do processo no sistema
        self.restante = duracao  # Tempo restante de execução do processo
        self.inicio = -1  # Tempo de início de execução do processo
        self.fim = 0  # Tempo de término de execução do processo
        self.tempo_espera = 0  # Tempo total de espera do processo na fila de prontos
        self.tempo_turnaround = 0  # Tempo total desde a chegada até a conclusão do processo
        self.tempo_resposta = -1  # Tempo desde a chegada até o início da primeira execução do processo

# Inicializar a lista de processos
processos = []

# Função para adicionar um processo a lista
def adicionar_processo():
    global processos
    try:
        pid = entrada_pid.get()
        duracao = int(entrada_duracao.get())
        chegada = int(entrada_chegada.get())
        processos.append(Processo(pid, duracao, chegada))
        atualizar_lista_processos()
        limpar_entradas()
    except ValueError:
        resultado_texto.set("Por favor, insira valores válidos.")

# Função para remover o processo selecionado da lista
def remover_processo():
    global processos
    try:
        indice_selecionado = lista_processos.curselection()[0]
        del processos[indice_selecionado]
        atualizar_lista_processos()
        resultado_texto.set("Processo removido com sucesso.")
    except IndexError:
        resultado_texto.set("Por favor, selecione um processo para remover.")

# Função para executar o algoritmo FIFO
def executar_fifo():
    global processos
    processos.sort(key=lambda x: x.chegada)
    tempo_atual = 0
    for processo in processos:
        processo.inicio = tempo_atual
        processo.fim = processo.inicio + processo.duracao
        processo.tempo_espera = tempo_atual
        processo.tempo_turnaround = processo.tempo_espera + processo.duracao
        processo.tempo_resposta = processo.tempo_espera
        tempo_atual = processo.fim
    atualizar_tabela(processos)
    plot_grafico_fifo(processos)

# Função para executar o algoritmo SJF
def executar_sjf():
    global processos
    processos.sort(key=lambda x: x.duracao)
    tempo_atual = 0
    for processo in processos:
        processo.inicio = tempo_atual
        processo.fim = processo.inicio + processo.duracao
        processo.tempo_espera = tempo_atual
        processo.tempo_turnaround = processo.tempo_espera + processo.duracao
        processo.tempo_resposta = processo.tempo_espera
        tempo_atual = processo.fim
    atualizar_tabela(processos)
    plot_grafico_sjf(processos)

# Função para executar o algoritmo SRTN
def executar_srtn():
    global processos
    
    # Ordenar processos por chegada
    processos.sort(key=lambda x: x.chegada)
    
    tempo_atual = 0
    processos_copia = [Processo(p.pid, p.duracao, p.chegada) for p in processos]
    sequencia_processos = []
    
    while processos_copia:
        # Filtrar processos que já chegaram e ainda têm tempo restante
        processos_disponiveis = [p for p in processos_copia if p.chegada <= tempo_atual and p.restante > 0]
        
        if processos_disponiveis:
            # Escolher o processo com menor tempo restante
            processo_atual = min(processos_disponiveis, key=lambda x: x.restante)
            
            # Se o processo não começou a ser executado, atualiza o tempo de resposta
            if processo_atual.inicio == -1:
                processo_atual.inicio = tempo_atual
                processo_atual.tempo_resposta = tempo_atual - processo_atual.chegada
            
            # Adicionar o processo à sequência de execução
            sequencia_processos.append(processo_atual.pid)
            
            # Executar o processo por 1 unidade de tempo
            processo_atual.restante -= 1
            tempo_atual += 1
            
            # Se o processo acabou, calcular tempo de turnaround e remover da lista de cópia
            if processo_atual.restante == 0:
                processo_atual.fim = tempo_atual
                processo_atual.tempo_turnaround = processo_atual.fim - processo_atual.chegada
                processo_atual.tempo_espera = processo_atual.tempo_turnaround - processo_atual.duracao
                processos_copia.remove(processo_atual)
                
                # Atualizar o processo original na lista principal
                for p in processos:
                    if p.pid == processo_atual.pid:
                        p.inicio = processo_atual.inicio
                        p.fim = processo_atual.fim
                        p.tempo_espera = processo_atual.tempo_espera
                        p.tempo_turnaround = processo_atual.tempo_turnaround
                        p.tempo_resposta = processo_atual.tempo_resposta
    
        else:
            # Avançar o tempo para o próximo processo chegar
            tempo_atual = min(p.chegada for p in processos_copia)
    
    # Atualizar tabela e plotar gráfico
    atualizar_tabela(processos)
    plot_grafico_srtn(sequencia_processos)

# Função para atualizar a lista de processos exibida na interface
def atualizar_lista_processos():
    global processos
    lista_processos.delete(0, tk.END)
    for processo in processos:
        lista_processos.insert(tk.END, f"PID: {processo.pid} | Duração: {processo.duracao} | Chegada: {processo.chegada}")

# Função para limpar as entradas de texto
def limpar_entradas():
    entrada_pid.delete(0, tk.END)
    entrada_duracao.delete(0, tk.END)
    entrada_chegada.delete(0, tk.END)

# Função para atualizar a tabela exibida na interface
def atualizar_tabela(processos_ordenados):
    for row in tree.get_children():
        tree.delete(row)
    for processo in processos_ordenados:
        tree.insert("", "end", values=(
            processo.pid, 
            processo.duracao, 
            processo.chegada,
            processo.tempo_espera, 
            processo.tempo_turnaround, 
            processo.tempo_resposta
        ))

# Função para plotar o gráfico de Gantt para o escalonamento FIFO
def plot_grafico_fifo(processos):
    gantt_pos = [(p.inicio, p.fim) for p in processos]
    fim_pos = processos[-1].fim if processos else 0
    fig, ax = plt.subplots(figsize=(10, 4))
    cores = ['purple', 'blue', 'green', 'red', 'orange', 'yellow']
    for i, tarefa in enumerate(gantt_pos):
        começo, fim = tarefa
        duracao = fim - começo
        ax.broken_barh([(começo, duracao)], (1.2, 0.6),
                       facecolors=cores[i % len(cores)], label=f"P{processos[i].pid}")
        ax.annotate(f"P{processos[i].pid}", xy=(começo, 1.5), xycoords='data',
                    xytext=(1.5, 1.5), textcoords='offset points')
        ax.annotate(começo, xy=(começo, .8), xycoords='data', xytext=(1.5, 1.5), textcoords='offset points')
    ax.annotate(fim_pos, xy=(fim_pos, .8), xycoords='data',
                xytext=(1.5, 1.5), textcoords='offset points')
    ax.set_title('Gráfico - FIFO')
    plt.ylim((0, 5))
    ax.set_yticklabels([])
    ax.set_xticklabels([])
    handles, labels = plt.gca().get_legend_handles_labels()
    by_label = dict(zip(labels, handles))
    ax.legend(by_label.values(), by_label.keys(), bbox_to_anchor=(1.05, 1), loc='upper left', title='Processos')
    ax.grid(False)
    ax.axis('on')
    plt.xlabel('Tempo')
    plt.tight_layout()
    plt.show()

# Função para plotar o gráfico de Gantt para o escalonamento SJF
def plot_grafico_sjf(processos):
    gantt_pos = [(p.inicio, p.fim) for p in processos]
    fim_pos = processos[-1].fim if processos else 0
    fig, ax = plt.subplots(figsize=(10, 4))
    cores = ['purple', 'blue', 'green', 'red', 'orange', 'yellow']
    for i, tarefa in enumerate(gantt_pos):
        começo, fim = tarefa
        duracao = fim - começo
        ax.broken_barh([(começo, duracao)], (1.2, 0.6),
                       facecolors=cores[i % len(cores)], label=f"P{processos[i].pid}")
        ax.annotate(f"P{processos[i].pid}", xy=(começo, 1.5), xycoords='data',
                    xytext=(1.5, 1.5), textcoords='offset points')
        ax.annotate(começo, xy=(começo, .8), xycoords='data', xytext=(1.5, 1.5), textcoords='offset points')
    ax.annotate(fim_pos, xy=(fim_pos, .8), xycoords='data',
                xytext=(1.5, 1.5), textcoords='offset points')
    ax.set_title('Gráfico - SJF')
    plt.ylim((0, 5))
    ax.set_yticklabels([])
    ax.set_xticklabels([])
    handles, labels = plt.gca().get_legend_handles_labels()
    by_label = dict(zip(labels, handles))
    ax.legend(by_label.values(), by_label.keys(), bbox_to_anchor=(1.05, 1), loc='upper left', title='Processos')
    ax.grid(False)
    ax.axis('on')
    plt.xlabel('Tempo')
    plt.tight_layout()
    plt.show()

# Função para plotar o gráfico de Gantt para o escalonameno SRTN
def plot_grafico_srtn(sequencia_processos):
    tarefas = []
    inicio_tempo = 0
    for i in range(1, len(sequencia_processos)):
        if sequencia_processos[i] != sequencia_processos[i - 1]:
            tarefas.append((inicio_tempo, i - 1, sequencia_processos[i - 1]))
            inicio_tempo = i
    tarefas.append((inicio_tempo, len(sequencia_processos) - 1, sequencia_processos[-1]))

    fig, ax = plt.subplots(figsize=(10, 4))
    paleta = plt.cm.tab20.colors
    cores = {}
    cor_atual = 0
    for tarefa in tarefas:
        começo, fim, pid = tarefa
        if pid not in cores:
            cores[pid] = paleta[cor_atual % len(paleta)]
            cor_atual += 1
        ax.broken_barh([(começo, fim - começo + 1)], (1.2, 0.6),
                       facecolors=cores[pid], label=f"P{pid}")
        ax.annotate(f"P{pid}", xy=(começo, 1.5), xycoords='data',
                    xytext=(1.5, 1.5), textcoords='offset points')
        ax.annotate(começo, xy=(começo, .8), xycoords='data', xytext=(1.5, 1.5), textcoords='offset points')
    ax.annotate(len(sequencia_processos), xy=(len(sequencia_processos), .8), xycoords='data',
                xytext=(1.5, 1.5), textcoords='offset points')
    ax.set_title('Gráfico - SRTN')
    plt.ylim((0, 5))
    ax.set_yticklabels([])
    ax.set_xticklabels([])
    handles, labels = plt.gca().get_legend_handles_labels()
    by_label = dict(zip(labels, handles))
    ax.legend(by_label.values(), by_label.keys(), bbox_to_anchor=(1.05, 1), loc='upper left', title='Processos')
    ax.grid(False)
    ax.axis('on')
    plt.xlabel('Tempo')
    plt.tight_layout()
    plt.show()

# Função para executar o algoritmo escolhido
def executar_escalonador():
    algoritmo_escolhido = combo_algoritmo.get()
    if algoritmo_escolhido == "FIFO":
        executar_fifo()
    elif algoritmo_escolhido == "SJF":
        executar_sjf()
    elif algoritmo_escolhido == "SRTN":
        executar_srtn()

# Configuração da interface gráfica
janela = tk.Tk()
janela.title("Gerenciador de Processos")

# Definindo um estilo para os elementos visuais da interface
style = ttk.Style()
style.theme_use('clam')

# Personalizar o estilo dos elementos visuais da interface
style.configure('TLabel', background='#34495E', foreground='white', font=('Helvetica', 12), padx=10, pady=5)
style.configure('TEntry', fieldbackground='#D5DBDB', font=('Helvetica', 12))
style.configure('TButton', background='#1E90FF', foreground='white', font=('Helvetica', 12), padx=10, pady=5)

# Frame principal para conter todos os elementos visuais da interface
frame_principal = ttk.Frame(janela, padding=20)
frame_principal.grid(row=0, column=0, sticky="nsew")

# Labels e Entradas para o PID
ttk.Label(frame_principal, text="PID do Processo:").grid(row=0, column=0, sticky="w")
entrada_pid = ttk.Entry(frame_principal, width=20)
entrada_pid.grid(row=0, column=1, padx=5, pady=5)

# Labels e Entradas para o Tempo de Duração
ttk.Label(frame_principal, text="Tempo de Duração do Processo:").grid(row=1, column=0, sticky="w")
entrada_duracao = ttk.Entry(frame_principal, width=20)
entrada_duracao.grid(row=1, column=1, padx=5, pady=5)

# Labels e Entradas para o Tempo de Chegada
ttk.Label(frame_principal, text="Tempo de Chegada do Processo:").grid(row=2, column=0, sticky="w")
entrada_chegada = ttk.Entry(frame_principal, width=20)
entrada_chegada.grid(row=2, column=1, padx=5, pady=5)

# Botão para adicionar processo
botao_adicionar = ttk.Button(frame_principal, text="Adicionar Processo", command=adicionar_processo)
botao_adicionar.grid(row=3, column=0, columnspan=2, pady=10)

# Botão para remover processo
botao_remover = ttk.Button(frame_principal, text="Remover Processo", command=remover_processo)
botao_remover.grid(row=4, column=0, columnspan=2, pady=10)

# Lista de processos adicionados
lista_processos = tk.Listbox(frame_principal, width=60, height=10, bg='#D5DBDB', font=('Helvetica', 12))
lista_processos.grid(row=5, column=0, columnspan=2, pady=10)

# Combobox para seleção do algoritmo
ttk.Label(frame_principal, text="Algoritmo de Escalonamento:").grid(row=6, column=0, sticky="w")
combo_algoritmo = ttk.Combobox(frame_principal, values=["FIFO", "SJF", "SRTN"], font=('Helvetica', 12))
combo_algoritmo.grid(row=6, column=1, padx=5, pady=5)
combo_algoritmo.current(0)

# Botão para executar o escalonamento
botao_executar = ttk.Button(frame_principal, text="Executar Escalonamento", command=executar_escalonador)
botao_executar.grid(row=7, column=0, columnspan=2, pady=10)

# Mensagem de resultado
resultado_texto = tk.StringVar()
resultado_label = ttk.Label(frame_principal, textvariable=resultado_texto, foreground='white')
resultado_label.grid(row=8, column=0, columnspan=2)

# Tabela para exibir os dados dos processos
tree = ttk.Treeview(frame_principal, columns=("PID", "Duracao", "Chegada", "Espera", "Turnaround", "Resposta"), show='headings', height=10)
tree.heading("PID", text="PID")
tree.heading("Duracao", text="Duração")
tree.heading("Chegada", text="Chegada")
tree.heading("Espera", text="Espera")
tree.heading("Turnaround", text="Turnaround")
tree.heading("Resposta", text="Resposta")
tree.column("PID", width=100)
tree.column("Duracao", width=100)
tree.column("Chegada", width=100)
tree.column("Espera", width=100)
tree.column("Turnaround", width=120)
tree.column("Resposta", width=120)
tree.grid(row=9, column=0, columnspan=2, pady=10)

# Ajustar o tamanho das colunas e linhas do frame principal
frame_principal.columnconfigure(0, weight=1)
frame_principal.columnconfigure(1, weight=1)
frame_principal.rowconfigure(8, weight=1)

# Configurações finais da janela principal
janela.configure(bg='#34495E')
janela.geometry("680x800")

# Iniciar loop de eventos da interface gráfica 
janela.mainloop()