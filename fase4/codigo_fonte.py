import pandas as pd
import numpy as np
import sympy as sp
import heapq
import os
import random
import math
from collections import Counter

# --- Configuração Visual do Terminal ---
class Cores:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

# Constantes do Sistema
TAXA_PERDA_ENERGETICA = 0.02 # Simula perda de 2% por unidade de distância na rede

# --- Estruturas de Dados e Configurações ---
NOMES_BASE = [
    "Habitação", "Centro de Controle", "Armazenamento de Energia", 
    "Agricultura", "Laboratório Científico", "Comunicação", 
    "Suporte Médico", "Produção de Oxigênio"
]

# Decisão de Design: A "distância entre módulos" (pesos) é representada nas arestas (conexoes_lista) 
# em vez de atributos dos módulos. Isso permite modelar a topologia da rede como um grafo ponderado 
# independente das propriedades internas de cada unidade, facilitando algoritmos de roteamento.
#
# Justificativa da topologia: as conexões não foram escolhidas ao acaso, mas para refletir
# prioridades reais de uma colônia marciana:
#   - Armazenamento de Energia é o módulo mais conectado (Centro de Controle e Produção de
#     Oxigênio), pois é a fonte primária de energia e precisa alimentar diretamente os módulos
#     de maior consumo e maior criticidade para a sobrevivência da tripulação.
#   - Centro de Controle atua como "hub" de coordenação, ligando-se a Habitação e Comunicação,
#     já que monitora tanto o suporte à vida quanto a troca de dados com a Terra.
#   - Suporte Médico e Produção de Oxigênio ficam próximos de Habitação, pois são sistemas de
#     suporte à vida que precisam de baixa latência no atendimento à tripulação.
#   - Laboratório Científico fica na periferia da rede (ligado apenas a Agricultura, Comunicação
#     e Suporte Médico), pois é o módulo de menor prioridade operacional imediata, recebendo
#     dados em vez de demandar resposta rápida.
conexoes_lista = [
    ("Armazenamento de Energia", "Centro de Controle", 5),
    ("Centro de Controle", "Habitação", 10),
    ("Centro de Controle", "Comunicação", 8),
    ("Habitação", "Suporte Médico", 5),
    ("Habitação", "Produção de Oxigênio", 12),
    ("Produção de Oxigênio", "Agricultura", 15),
    ("Agricultura", "Laboratório Científico", 20),
    ("Armazenamento de Energia", "Produção de Oxigênio", 10),
    ("Comunicação", "Laboratório Científico", 15),
    ("Suporte Médico", "Laboratório Científico", 10)
]

def gerar_dados_aleatorios():
    """Gera dados randômicos para simulação dos módulos da colônia."""
    novos_dados = {}
    for nome in NOMES_BASE:
        consumo = random.randint(20, 100)
        prioridade = random.randint(1, 3)
        capacidade = random.randint(50, 500)
        status = random.choice(["Ativo", "Manutenção", "Alerta"])
        comunicacao = random.choice(["Alta", "Média", "Baixa"])
        novos_dados[nome] = (consumo, prioridade, capacidade, status, comunicacao)
    return novos_dados

# Inicialização global das informações
modulos_info = gerar_dados_aleatorios()
nomes_modulos = list(modulos_info.keys())

# --- Otimização de Grafos: Lista de Adjacência Global ---
def construir_lista_adjacencia():
    """Gera um dicionário global de adjacência para otimizar a busca de vizinhos em algoritmos de rede."""
    adj = {m: [] for m in nomes_modulos}
    for u, v, w in conexoes_lista:
        adj[u].append((v, w))
        adj[v].append((u, w))
    return adj

def inicializar_matriz_adjacencia():
    """
    Cria a matriz de adjacência (NumPy) para representação matemática.
    Nota: A topologia (conexoes_lista) é fixa, então esta função é chamada apenas uma vez no início.
    """
    n = len(nomes_modulos)
    matriz = np.zeros((n, n))
    for u, v, w in conexoes_lista:
        i, j = nomes_modulos.index(u), nomes_modulos.index(v)
        matriz[i][j] = w
        matriz[j][i] = w
    return matriz

# Estruturas de rede pré-calculadas
lista_adj = construir_lista_adjacencia()
matriz_adj = inicializar_matriz_adjacencia()

def calcular_capacidade_total():
    """Retorna a soma das capacidades de armazenamento de todos os módulos."""
    return sum(v[2] for v in modulos_info.values())

# --- Algoritmos de Redes e Navegação ---

def bfs(inicio):
    """Busca em largura (BFS) usando a lista de adjacência otimizada."""
    visitados = []
    fila = [inicio]
    while fila:
        u = fila.pop(0)
        if u not in visitados:
            visitados.append(u)
            for v, w in lista_adj[u]:
                if v not in visitados:
                    fila.append(v)
    return visitados

def bfs_caminho(inicio, fim):
    """
    Busca em Largura adaptada para reconstruir uma rota REAL entre dois módulos
    (rastreando predecessores, como o Dijkstra já faz). O BFS otimiza pelo MENOR
    NÚMERO DE SALTOS, não pelo menor peso, então o caminho encontrado normalmente
    é diferente do caminho do Dijkstra — isso é o que usamos para comparar uma
    rota "não-otimizada por peso" com a rota ótima, em vez de simular um valor fixo.
    Retorna (caminho, distancia_real) ou (None, None) se não houver rota.
    """
    visitados = {inicio}
    predecessores = {inicio: None}
    fila = [inicio]
    while fila:
        u = fila.pop(0)
        if u == fim:
            break
        for v, w in lista_adj[u]:
            if v not in visitados:
                visitados.add(v)
                predecessores[v] = u
                fila.append(v)

    if fim not in predecessores:
        return None, None

    caminho = []
    atual = fim
    while atual is not None:
        caminho.insert(0, atual)
        atual = predecessores[atual]

    # Soma os pesos reais das arestas percorridas no caminho encontrado pelo BFS
    distancia_real = 0
    for i in range(len(caminho) - 1):
        atual_nome, proximo_nome = caminho[i], caminho[i + 1]
        for v, w in lista_adj[atual_nome]:
            if v == proximo_nome:
                distancia_real += w
                break

    return caminho, distancia_real

def dfs(inicio, visitados=None):
    """Busca em profundidade (DFS) recursiva usando a lista de adjacência otimizada."""
    if visitados is None: visitados = []
    visitados.append(inicio)
    for v, w in lista_adj[inicio]:
        if v not in visitados:
            dfs(v, visitados)
    return visitados

def encontrar_pontes():
    """Detecta conexões críticas (pontes) usando DFS e tempos de descoberta."""
    tempo = 0
    descoberta = {m: -1 for m in nomes_modulos}
    low = {m: -1 for m in nomes_modulos}
    pai = {m: None for m in nomes_modulos}
    pontes = []

    def dfs_pontes(u):
        nonlocal tempo
        descoberta[u] = low[u] = tempo
        tempo += 1
        for v, w in lista_adj[u]:
            if descoberta[v] == -1:
                pai[v] = u
                dfs_pontes(v)
                low[u] = min(low[u], low[v])
                if low[v] > descoberta[u]:
                    pontes.append((u, v))
            elif v != pai[u]:
                low[u] = min(low[u], descoberta[v])

    for m in nomes_modulos:
        if descoberta[m] == -1:
            dfs_pontes(m)
    return pontes

def dijkstra(inicio, fim):
    """Encontra o caminho mínimo usando Dijkstra e a lista de adjacência otimizada."""
    distancias = {m: float('inf') for m in nomes_modulos}
    distancias[inicio] = 0
    pq = [(0, inicio)]
    predecessores = {m: None for m in nomes_modulos}
    
    while pq:
        d_atual, u = heapq.heappop(pq)
        if d_atual > distancias[u]: continue
        for v, peso in lista_adj[u]:
            distancia = d_atual + peso
            if distancia < distancias[v]:
                distancias[v] = distancia
                predecessores[v] = u
                heapq.heappush(pq, (distancia, v))
                
    caminho = []
    atual = fim
    while atual:
        caminho.insert(0, atual)
        atual = predecessores[atual]
    return caminho, distancias[fim]

# --- Modelagem Matemática Integrada ---

def modelagem_energetica():
    """
    Realiza a modelagem de consumo ajustando uma função quadrática aos dados simulados.
    Usa numpy.polyfit para a regressão e sympy para o cálculo diferencial (derivada e
    resolução da equação de saturação).
    """
    # Geração de histórico simulado baseado no estado atual da colônia
    # Geração de histórico simulado com tendência para modelo quadrático
    historico_consumo = []
    consumo_atual_real = sum(v[0] for v in modulos_info.values())
    base_consumo = consumo_atual_real * 0.8 # Começa com um valor menor para simular crescimento
    for i in range(1, 6): # 5 pontos de dados para regressão quadrática
        # Simula um crescimento que acelera, adequado para um modelo quadrático
        consumo_simulado = base_consumo + (i**2) * random.uniform(2, 5) + random.uniform(-10, 10)
        historico_consumo.append(consumo_simulado)
    
    # Garante que o último ponto do histórico seja próximo ao consumo atual real
    historico_consumo[-1] = consumo_atual_real + random.uniform(-5, 5)

    X = np.array([1, 2, 3, 4, 5]).reshape(-1, 1)
    y = np.array(historico_consumo)
    
    # Usando numpy.polyfit para regressão quadrática
    # Coeficientes: [a, b, c] para ax^2 + bx + c
    coeficientes = np.polyfit(X.flatten(), y, 2)
    
    t = sp.symbols('t')
    # Modelo quadrático: a*t^2 + b*t + c
    f_t = round(coeficientes[0], 2) * t**2 + round(coeficientes[1], 2) * t + round(coeficientes[2], 2)
    df_dt = sp.diff(f_t, t)
    
    cap_total = calcular_capacidade_total()
    equacao = sp.Eq(f_t, cap_total)
    solucao = sp.solve(equacao, t)
    
    mes_saturacao = None
    for sol in solucao:
        if sol.is_real and sol > 0:
            mes_saturacao = float(sol)
            break # Pega a primeira solução positiva e real

    # Calculando a taxa de crescimento no mês atual (ex: t=5, o último ponto do histórico)
    taxa_crescimento_atual = df_dt.subs(t, 5)
    
    return f_t, df_dt, mes_saturacao, cap_total, taxa_crescimento_atual
    
def simular_falha_rede():
    global nomes_modulos, modulos_info, conexoes_lista, lista_adj, matriz_adj

    print(f"\n{Cores.GREEN}--- SIMULAÇÃO DE FALHA NA REDE ---{Cores.ENDC}")
    print(f"{Cores.CYAN}1. Simular falha de Módulo | 2. Simular falha de Conexão{Cores.ENDC}")
    tipo_falha = input("Escolha o tipo de falha a simular: ")

    # Salvar estado original da rede
    original_nomes_modulos = list(nomes_modulos)
    original_modulos_info = modulos_info.copy()
    original_conexoes_lista = list(conexoes_lista)
    original_lista_adj = construir_lista_adjacencia() # Reconstruir para garantir cópia profunda
    original_matriz_adj = inicializar_matriz_adjacencia() # Reconstruir para garantir cópia profunda

    if tipo_falha == '1':
        modulo_falho = selecionar_modulo("Selecione o módulo que irá falhar:")
        if not modulo_falho:
            return
        
        # Remover módulo
        nomes_modulos.remove(modulo_falho)
        del modulos_info[modulo_falho]
        conexoes_lista_temp = []
        for u, v, w in conexoes_lista:
            if u != modulo_falho and v != modulo_falho:
                conexoes_lista_temp.append((u, v, w))
        conexoes_lista = conexoes_lista_temp

        print(f"{Cores.WARNING}Módulo \'{modulo_falho}\' simulado como falho.{Cores.ENDC}")

    elif tipo_falha == '2':
        print(f"\n{Cores.BLUE}Conexões Disponíveis:{Cores.ENDC}")
        for i, (u, v, w) in enumerate(conexoes_lista):
            print(f"  {i+1}. {u} --({w})--> {v}")
        
        try:
            idx_conexao = int(input("Digite o número da conexão que irá falhar: ")) - 1
            if not (0 <= idx_conexao < len(conexoes_lista)):
                raise ValueError
            
            conexao_falha = conexoes_lista.pop(idx_conexao)
            print(f"{Cores.WARNING}Conexão {conexao_falha[0]} --({conexao_falha[2]})--> {conexao_falha[1]} simulada como falha.{Cores.ENDC}")

        except ValueError:
            print(f"{Cores.FAIL}Entrada inválida. Por favor, digite um número de conexão válido.{Cores.ENDC}")
            return

    else:
        print(f"{Cores.FAIL}Opção de falha inválida.{Cores.ENDC}")
        return

    # Reconstruir estruturas de rede após a falha
    lista_adj = construir_lista_adjacencia()
    matriz_adj = inicializar_matriz_adjacencia()

    print(f"\n{Cores.GREEN}--- ANÁLISE DE IMPACTO DA FALHA ---{Cores.ENDC}")

    # 1. Verificar módulos isolados
    if nomes_modulos:
        componentes_conectados = []
        visitados_bfs = set()
        for modulo in nomes_modulos:
            if modulo not in visitados_bfs:
                componente = bfs(modulo)
                componentes_conectados.append(componente)
                visitados_bfs.update(componente)
        
        if len(componentes_conectados) > 1:
            print(f"{Cores.FAIL}Atenção: A rede foi particionada! Existem {len(componentes_conectados)} componentes conectados.{Cores.ENDC}")
            for i, comp in enumerate(componentes_conectados):
                print(f"  Componente {i+1}: {', '.join(comp)}")
        else:
            print(f"{Cores.GREEN}A rede permanece conectada. Nenhum módulo isolado detectado.{Cores.ENDC}")
    else:
        print(f"{Cores.FAIL}Todos os módulos foram removidos ou a rede está vazia.{Cores.ENDC}")

    # 2. Verificar se a conexão removida era uma ponte crítica (apenas para falha de conexão)
    if tipo_falha == '2' and 'conexao_falha' in locals():
        pontes_apos_falha = encontrar_pontes()
        if (conexao_falha[0], conexao_falha[1]) in pontes_apos_falha or \
           (conexao_falha[1], conexao_falha[0]) in pontes_apos_falha:
            print(f"{Cores.FAIL}A conexão removida ({conexao_falha[0]} <---> {conexao_falha[1]}) ERA uma ponte crítica!{Cores.ENDC}")
        else:
            print(f"{Cores.GREEN}A conexão removida não era uma ponte crítica na rede original.{Cores.ENDC}")

    # 3. Recalcular rotas Dijkstra para um exemplo
    if len(nomes_modulos) >= 2:
        origem_exemplo = nomes_modulos[0]
        destino_exemplo = nomes_modulos[1]
        if origem_exemplo != destino_exemplo:
            caminho_novo, dist_nova = dijkstra(origem_exemplo, destino_exemplo)
            if dist_nova == float('inf'):
                print(f"{Cores.WARNING}Não há rota entre {origem_exemplo} e {destino_exemplo} após a falha.{Cores.ENDC}")
            else:
                print(f"\n{Cores.CYAN}Exemplo de Rota (Dijkstra) após falha:{Cores.ENDC}")
                print(f"  De {origem_exemplo} para {destino_exemplo}: {" -> ".join(caminho_novo)} (Distância: {dist_nova})")
        else:
            print(f"{Cores.WARNING}Não há módulos suficientes para demonstrar uma rota Dijkstra após a falha.{Cores.ENDC}")

    # Restaurar estado original da rede
    nomes_modulos = original_nomes_modulos
    modulos_info = original_modulos_info
    conexoes_lista = original_conexoes_lista
    lista_adj = original_lista_adj
    matriz_adj = original_matriz_adj
    print(f"\n{Cores.GREEN}Simulação concluída. Rede restaurada ao estado original.{Cores.ENDC}")

def visualizar_conexoes_legiveis():
    print(f"\n{Cores.GREEN}--- CONEXÕES DA REDE ---{Cores.ENDC}")
    if not conexoes_lista:
        print("Nenhuma conexão configurada na rede.")
        return
    for u, v, w in conexoes_lista:
        print(f"  {u} --({w})--> {v}")

def consultar_modulo_individual():
    nome_modulo = selecionar_modulo("Selecione o módulo para consultar:")
    if nome_modulo and nome_modulo in modulos_info:
        dados = modulos_info[nome_modulo]
        print(f"\n{Cores.GREEN}--- DADOS DO MÓDULO: {nome_modulo.upper()} ---{Cores.ENDC}")
        print(f"  Consumo: {dados[0]} kW")
        print(f"  Prioridade: {dados[1]}")
        print(f"  Capacidade: {dados[2]} kW")
        print(f"  Status: {dados[3]}")
        print(f"  Comunicação: {dados[4]}")
        
        print(f"\n{Cores.CYAN}Conexões Diretas:{Cores.ENDC}")
        encontrado = False
        for u, v, w in conexoes_lista:
            if u == nome_modulo:
                print(f"  - {u} --({w})--> {v}")
                encontrado = True
            elif v == nome_modulo:
                print(f"  - {v} --({w})--> {u}")
                encontrado = True
        if not encontrado:
            print("  Nenhuma conexão direta encontrada.")
    elif nome_modulo:
        print(f"{Cores.FAIL}Módulo '{nome_modulo}' não encontrado.{Cores.ENDC}")
    # Se nome_modulo for None, selecionar_modulo() já exibiu a mensagem de erro.

def realizar_analise_esg():
    """Análise ESG robusta com contagem segura de status e ranking de custo/prioridade."""
    consumo_total = sum(v[0] for v in modulos_info.values())
    cap_total = calcular_capacidade_total()
    
    # Uso de Counter para robustez na contagem de status (evita KeyError)
    status_counts = Counter(v[3] for v in modulos_info.values())
    
    ranking_custo = []
    criticos = []
    for nome, dados in modulos_info.items():
        razao = dados[0] / dados[1] # Consumo / Prioridade
        ranking_custo.append((nome, razao))
        
        # Lógica de criticidade: suporte à vida (P1) + alta demanda (>70) + baixa margem (<150)
        if dados[1] == 1 and dados[0] > 70 and dados[2] < 150:
            criticos.append(nome)
            
    ranking_custo.sort(key=lambda x: x[1], reverse=True)
    top_3_custo = ranking_custo[:3]
    
    per_alerta = (status_counts["Alerta"] / len(nomes_modulos)) * 100
    per_manutencao = (status_counts["Manutenção"] / len(nomes_modulos)) * 100
    
    recomendacao = "Sistema operando dentro dos parâmetros normais."
    if per_alerta > 20:
        recomendacao = "ALERTA: Alta incidência de módulos críticos. Priorizar manutenção preventiva."
    elif consumo_total > cap_total * 0.8:
        recomendacao = "AVISO: Consumo próximo ao limite. Ativar protocolos de eficiência energética."
        
    return consumo_total, cap_total, per_alerta, per_manutencao, criticos, top_3_custo, recomendacao

# --- Interface do Usuário ---

def limpar_tela():
    os.system('cls' if os.name == 'nt' else 'clear')

def cabecalho():
    print(f"{Cores.HEADER}{Cores.BOLD}" + "="*65)
    print("           SISTEMA AURORA SIGER - COLÔNIA MARCIANA (SIGIC)           ")
    print("="*65 + f"{Cores.ENDC}")

def selecionar_modulo(mensagem="Selecione um módulo:"):
    """
    Exibe a lista de módulos numerada e retorna o nome do módulo escolhido.
    Substitui a digitação manual do nome por uma escolha numérica, evitando
    erros de digitação/acentuação e tornando a navegação mais rápida.
    Retorna None se a escolha for inválida.
    """
    print(f"\n{Cores.BLUE}{mensagem}{Cores.ENDC}")
    for i, nome in enumerate(nomes_modulos, start=1):
        print(f"  {i}. {nome}")
    escolha = input("Número do módulo: ")
    if not escolha.isdigit():
        print(f"{Cores.FAIL}Entrada inválida. Digite apenas o número do módulo.{Cores.ENDC}")
        return None
    indice = int(escolha) - 1
    if 0 <= indice < len(nomes_modulos):
        return nomes_modulos[indice]
    print(f"{Cores.FAIL}Número fora da faixa de módulos disponíveis.{Cores.ENDC}")
    return None

def menu():
    global modulos_info
    while True:
        cabecalho()
        print(f"{Cores.CYAN}1.{Cores.ENDC} Visualizar Infraestrutura (Módulos)")
        print(f"{Cores.CYAN}2.{Cores.ENDC} Matriz de Adjacência (Conexões)")
        print(f"{Cores.CYAN}3.{Cores.ENDC} Otimizar Rota - Dijkstra (Caminho Mínimo)")
        print(f"{Cores.CYAN}4.{Cores.ENDC} Exploração de Rede (BFS/DFS)")
        print(f"{Cores.CYAN}5.{Cores.ENDC} Simular Operações (Dados Randômicos)")
        print(f"{Cores.CYAN}6.{Cores.ENDC} Modelagem Matemática e Previsão de Saturação")
        print(f"{Cores.CYAN}7.{Cores.ENDC} Análise de Eficiência Operacional e ESG")
        print(f"{Cores.CYAN}8.{Cores.ENDC} Detectar Conexões Críticas (Pontes)")
        print(f"{Cores.CYAN}9.{Cores.ENDC} Consultar Módulo Individual")
        print(f"{Cores.CYAN}10.{Cores.ENDC} Simular Falha na Rede")
        print(f"{Cores.CYAN}11.{Cores.ENDC} Visualizar Conexões Legíveis")
        print(f"{Cores.FAIL}0. Sair{Cores.ENDC}")
        
        opcao = input(f"\n{Cores.BOLD}Escolha uma opção: {Cores.ENDC}")
        
        # --- Opção 1: Exibição tabular da infraestrutura usando Pandas ---
        if opcao == '1':
            df = pd.DataFrame.from_dict(modulos_info, orient='index', 
                                       columns=['Consumo', 'Prioridade', 'Capacidade', 'Status', 'Comunicação'])
            print(f"\n{Cores.GREEN}--- STATUS OPERACIONAL DA COLÔNIA ---{Cores.ENDC}")
            print(df)
            input("\nPressione Enter para continuar...")
            
        # --- Opção 2: Representação matemática da topologia via Matriz de Adjacência ---
        elif opcao == '2':
            print(f"\n{Cores.GREEN}--- REPRESENTAÇÃO MATRICIAL DA REDE ---{Cores.ENDC}")
            df_matriz = pd.DataFrame(matriz_adj, index=nomes_modulos, columns=nomes_modulos)
            print(df_matriz)
            input("\nPressione Enter para continuar...")
            
        # --- Opção 3: Roteamento ótimo via Dijkstra + cálculo de perda energética ---
        elif opcao == '3':
            origem = selecionar_modulo("Selecione o módulo de ORIGEM:")
            destino = selecionar_modulo("Selecione o módulo de DESTINO:") if origem else None
            if origem and destino:
                caminho, dist = dijkstra(origem, destino)
                perda_estimada = dist * TAXA_PERDA_ENERGETICA

                print(f"\n{Cores.BOLD}{Cores.GREEN}Rota Otimizada (Dijkstra):{Cores.ENDC} {' -> '.join(caminho)}")
                print(f"{Cores.BOLD}Distância Total:{Cores.ENDC} {dist} unidades")
                print(f"{Cores.BOLD}Perda Energética:{Cores.ENDC} {perda_estimada:.2f} kW (Baseado em {TAXA_PERDA_ENERGETICA*100:.0f}% de perda por unidade de distância)")

                # Comparação com rota alternativa REAL (BFS rastreando predecessores),
                # em vez de simular um valor fixo (ex.: dist * 1.4).
                if origem == destino or dist == 0:
                    print(f"{Cores.WARNING}Origem e destino são o mesmo módulo. Não há economia a ser calculada.{Cores.ENDC}")
                else:
                    caminho_bfs, dist_bfs = bfs_caminho(origem, destino)
                    if caminho_bfs is None:
                        print(f"{Cores.WARNING}Não foi possível encontrar uma rota alternativa para comparação.{Cores.ENDC}")
                    else:
                        print(f"\n{Cores.CYAN}Rota Alternativa (BFS, menor número de saltos):{Cores.ENDC} {' -> '.join(caminho_bfs)}")
                        print(f"{Cores.CYAN}Distância Real da Rota Alternativa:{Cores.ENDC} {dist_bfs} unidades")
                        if dist_bfs == dist:
                            print(f"{Cores.GREEN}Neste caso, a rota com menos saltos coincide com a de menor custo.{Cores.ENDC}")
                        else:
                            economia = ((dist_bfs - dist) / dist_bfs) * 100
                            print(f"{Cores.CYAN}Economia Real:{Cores.ENDC} A rota do Dijkstra é {economia:.1f}% mais eficiente em distância/energia do que a rota alternativa encontrada pelo BFS.")
            else:
                print(f"{Cores.FAIL}Módulo inválido.{Cores.ENDC}")
            input("\nPressione Enter para continuar...")
                
        # --- Opção 4: Algoritmos de busca e exploração (BFS/DFS) ---
        elif opcao == '4':
            inicio = selecionar_modulo("Selecione o módulo de PARTIDA:")
            if inicio:
                print(f"\n{Cores.CYAN}1. BFS (Largura) | 2. DFS (Profundidade){Cores.ENDC}")
                sub = input("Escolha: ")
                if sub == '1':
                    print(f"{Cores.GREEN}Sequência BFS:{Cores.ENDC}", " -> ".join(bfs(inicio)))
                elif sub == '2':
                    print(f"{Cores.GREEN}Sequência DFS:{Cores.ENDC}", " -> ".join(dfs(inicio)))
                else:
                    print(f"{Cores.FAIL}Erro: Opção inválida.{Cores.ENDC}")
            else:
                print(f"{Cores.FAIL}Erro: Módulo não encontrado.{Cores.ENDC}")
            input("\nPressione Enter para continuar...")

        # --- Opção 5: Simulação de novos cenários operacionais (Dados Randômicos) ---
        elif opcao == '5':
            modulos_info = gerar_dados_aleatorios()
            print(f"\n{Cores.WARNING}Dados simulados com sucesso! A topologia da rede permanece fixa.{Cores.ENDC}")
            input("\nPressione Enter para continuar...")
            
        # --- Opção 6: Modelagem preditiva com Regressão Linear e Cálculo Diferencial ---
        elif opcao == '6':
            f_t, df_dt, mes_sat, cap_total, taxa_crescimento_atual = modelagem_energetica()
            print(f"\n{Cores.GREEN}--- MODELAGEM MATEMÁTICA (DADOS REAIS SIMULADOS) ---{Cores.ENDC}")
            print(f"Função de Consumo Projetada: f(t) = {f_t}")
            print(f"  Onde 't' representa o tempo em meses a partir do início da projeção.")
            print(f"  A função modela o consumo energético total da colônia ao longo do tempo.")
            print(f"Taxa de Crescimento (Derivada): f'(t) = {df_dt}")
            print(f"  A derivada representa a taxa de variação do consumo energético em relação ao tempo.")
            print(f"  No mês atual (t=5), a taxa de crescimento é de {taxa_crescimento_atual:.2f} kW/mês.")
            print(f"  Isso significa que o consumo energético está aumentando em aproximadamente {taxa_crescimento_atual:.2f} kW a cada mês neste ponto.")

            # Análise qualitativa: interpreta a concavidade da função e contextualiza
            # o que ela significa para o comportamento da colônia, junto com uma
            # limitação explícita do modelo.
            coef_a = float(f_t.coeff(sp.symbols('t'), 2))
            print(f"\n{Cores.CYAN}Análise Qualitativa:{Cores.ENDC}")
            if coef_a > 0:
                print("  O coeficiente do termo quadrático é positivo (concavidade para cima): o consumo")
                print("  energético não apenas cresce, mas cresce de forma cada vez mais rápida com o tempo.")
            elif coef_a < 0:
                print("  O coeficiente do termo quadrático é negativo (concavidade para baixo): segundo este")
                print("  modelo, o crescimento do consumo tende a desacelerar e eventualmente recuar.")
            else:
                print("  O termo quadrático é praticamente nulo: o consumo se comporta de forma quase linear")
                print("  neste horizonte de tempo.")
            print("  Limitação do modelo: por ser ajustado a apenas 5 pontos simulados, ele representa uma")
            print("  tendência de curto prazo, não uma lei física — variações reais (novas missões, falhas,")
            print("  expansões) podem alterar significativamente o comportamento real do consumo.")

            # Melhoria: Salvaguarda para previsão de saturação
            if mes_sat is not None and mes_sat > 0:
                print(f"\n{Cores.WARNING}{Cores.BOLD}PREVISÃO DE SATURAÇÃO DA REDE:{Cores.ENDC}")
                print(f"O consumo atingirá a capacidade total ({cap_total} kW) no mês: {Cores.BOLD}{mes_sat:.2f}{Cores.ENDC}")
            else:
                print(f"\n{Cores.WARNING}Sem previsão de saturação no horizonte projetado ou dados insuficientes para projeção.{Cores.ENDC}")
            input("\nPressione Enter para continuar...")
            
        # --- Opção 7: Governança, Sustentabilidade e Eficiência Operacional (ESG) ---
        elif opcao == '7':
            cons, cap, alert, manut, crit, ranking, rec = realizar_analise_esg()
            print(f"\n{Cores.GREEN}--- ANÁLISE DE EFICIÊNCIA OPERACIONAL E ESG ---{Cores.ENDC}")
            print(f"Consumo Total: {cons} kW | Capacidade Total: {cap} kW")
            print(f"Módulos em Alerta: {alert:.1f}% | Em Manutenção: {manut:.1f}%")
            
            print(f"\n{Cores.CYAN}Ranking de Custo Energético por Prioridade (Top 3):{Cores.ENDC}")
            for nome, valor in ranking:
                print(f" - {nome}: {valor:.2f}")
            
            # Melhoria: Recomendação de governança dinâmica
            print(f"\n{Cores.BOLD}Governança e Sustentabilidade:{Cores.ENDC}")
            recomendacao_governanca = ""
            if manut > 15:
                recomendacao_governanca = "Reforçar as equipes de manutenção e revisar os planos de manutenção preventiva para garantir a estabilidade da infraestrutura."
            elif alert > 10:
                recomendacao_governanca = "Revisar os protocolos de alerta e implementar medidas proativas para mitigar riscos em módulos críticos."
            else:
                recomendacao_governanca = "Focar na expansão controlada da infraestrutura, buscando otimização de recursos e redundância de rede."
            print(recomendacao_governanca)
            
            if crit:
                print(f"\n{Cores.FAIL}Módulos Críticos Detectados:{Cores.ENDC} {', '.join(crit)}")
                print(f"{Cores.WARNING}Governança: esta é uma sinalização automática de apoio à decisão.{Cores.ENDC}")
                print(f"{Cores.WARNING}Nenhuma ação é executada automaticamente sobre esses módulos — qualquer{Cores.ENDC}")
                print(f"{Cores.WARNING}realocação de energia ou prioridade de manutenção deve ser revisada e{Cores.ENDC}")
                print(f"{Cores.WARNING}aprovada por um responsável humano antes de ser aplicada.{Cores.ENDC}")
            print(f"\n{Cores.BOLD}RECOMENDAÇÃO:{Cores.ENDC} {rec}")
            input("\nPressione Enter para continuar...")

        # --- Opção 8: Detecção de Pontos Únicos de Falha (Pontes no Grafo) ---
        elif opcao == '8':
            pontes = encontrar_pontes()
            print(f"\n{Cores.WARNING}--- DETECÇÃO DE CONEXÕES CRÍTICAS (PONTES) ---{Cores.ENDC}")
            if pontes:
                print("Conexões vitais identificadas (Risco de desconexão):")
                for u, v in pontes:
                    print(f" - {u} <---> {v}")
            else:
                print("Nenhuma conexão crítica (ponte) detectada. A rede possui redundância projetada.")
            input("\nPressione Enter para continuar...")
            
        # --- Opção 9: Consulta Individual de Módulo ---
        elif opcao == '9':
            consultar_modulo_individual()
            input("\nPressione Enter para continuar...")

        # --- Opção 10: Simulação Operacional Dinâmica ---
        elif opcao == '10':
            simular_falha_rede()
            input("\nPressione Enter para continuar...")

        # --- Opção 11: Visualização de Conexões Legíveis ---
        elif opcao == '11':
            visualizar_conexoes_legiveis()
            input("\nPressione Enter para continuar...")
            
        elif opcao == '0':
            print(f"{Cores.WARNING}Encerrando sistema Aurora Siger...{Cores.ENDC}")
            break
        
        limpar_tela()

if __name__ == "__main__":
    limpar_tela()
    menu()
