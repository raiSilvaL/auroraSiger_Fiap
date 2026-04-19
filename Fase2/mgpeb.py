import datetime

class ModuloPouso:
    def __init__(self, tipo, prioridade, combustivel, massa, criticidade, hec):
        self.tipo = tipo
        self.prioridade = prioridade  # 1: Alta, 2: Média, 3: Baixa
        self.combustivel = combustivel
        self.massa = massa
        self.criticidade = criticidade
        self.hec = datetime.datetime.strptime(hec, "%Y-%m-%d %H:%M:%S")
        self.pousado = False

    def __repr__(self):
        return f"[{self.tipo}] Prio: {self.prioridade}, Comb: {self.combustivel}, Massa: {self.massa}, Crit: {self.criticidade}, HEC: {self.hec}"

def cadastrar_modulos():
    modulos = [
        ModuloPouso("Habitação", 1, 80, 15, "Essencial", "2026-04-15 10:00:00"),
        ModuloPouso("Energia", 1, 70, 20, "Essencial", "2026-04-15 11:30:00"),
        ModuloPouso("Laboratório Científico", 2, 60, 10, "Importante", "2026-04-15 13:00:00"),
        ModuloPouso("Logística", 3, 90, 25, "Suporte", "2026-04-15 14:30:00"),
        ModuloPouso("Suporte Médico", 1, 75, 12, "Crítica", "2026-04-15 16:00:00")
    ]
    return modulos

def buscar_menor_combustivel(fila):
    if not fila:
        return None
    menor = fila[0]
    for modulo in fila:
        if modulo.combustivel < menor.combustivel:
            menor = modulo
    return menor

def ordenar_por_prioridade(fila):
    # Algoritmo de ordenação simples (Bubble Sort)
    n = len(fila)
    for i in range(n):
        for j in range(0, n-i-1):
            if fila[j].prioridade > fila[j+1].prioridade:
                fila[j], fila[j+1] = fila[j+1], fila[j]
    return fila

def simular_autorizacao_pouso(modulo, condicoes_atmosfericas, area_disponivel, sensores_ok):
    ncs = modulo.combustivel > 20
    caf = condicoes_atmosfericas
    dap = area_disponivel
    ids = sensores_ok
    
    # Regra Geral: NCS AND CAF AND DAP AND IDS
    ap_rga = ncs and caf and dap and ids
    
    # Regra de Emergência: (Prioridade Alta AND NCC AND NOT CAF) AND DAP AND IDS
    ncc = 5 < modulo.combustivel <= 20
    ap_re = (modulo.prioridade == 1 and ncc and not caf) and dap and ids
    
    ap_final = ap_rga or ap_re
    
    print(f"\nAnalisando pouso para o módulo: {modulo.tipo}")
    print(f"Condições: Combustível={modulo.combustivel}, Atmosfera={caf}, Área={dap}, Sensores={ids}")
    
    if ap_final:
        print(">>> POUSO AUTORIZADO!")
        return True
    else:
        print(">>> POUSO ADIADO. Aguardando melhores condições.")
        return False

def main():
    # 1. Cadastro de módulos em uma lista (estrutura linear)
    fila_pouso = cadastrar_modulos()
    modulos_pousados = []
    modulos_em_espera = []
    
    print("--- Fila Inicial de Pouso ---")
    for m in fila_pouso:
        print(m)
    
    # 2. Busca de módulo com menor combustível
    print("\n--- Busca de Módulo Crítico ---")
    critico = buscar_menor_combustivel(fila_pouso)
    print(f"Módulo com menor combustível: {critico}")
    
    # 3. Ordenação da fila por prioridade
    print("\n--- Reorganizando Fila por Prioridade ---")
    fila_pouso = ordenar_por_prioridade(fila_pouso)
    for m in fila_pouso:
        print(m)
    
    # 4. Simulação de Pouso
    print("\n--- Iniciando Simulação de Pouso ---")
    # Simulação para o primeiro módulo da fila (Habitação)
    # Condições: Atmosfera OK, Área OK, Sensores OK
    if simular_autorizacao_pouso(fila_pouso[0], True, True, True):
        modulos_pousados.append(fila_pouso.pop(0))
    
    # Simulação para o próximo módulo (Energia)
    # Condições: Atmosfera RUIM, Área OK, Sensores OK
    if simular_autorizacao_pouso(fila_pouso[0], False, True, True):
        modulos_pousados.append(fila_pouso.pop(0))
    else:
        modulos_em_espera.append(fila_pouso.pop(0))
        
    print("\n--- Status Final das Estruturas ---")
    print(f"Módulos Pousados: {[m.tipo for m in modulos_pousados]}")
    print(f"Módulos em Espera: {[m.tipo for m in modulos_em_espera]}")
    print(f"Módulos Restantes na Fila: {[m.tipo for m in fila_pouso]}")

if __name__ == "__main__":
    main()
