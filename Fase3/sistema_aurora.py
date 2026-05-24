import math

def organizar_dados():
    """
    Organiza os dados da colônia em estruturas eficientes.
    Representa os sistemas de forma hierárquica.
    """
    colonia_dados = {
        "energia": {
            "geracao": 80,
            "consumo": 30,
            "reserva": 500,
            "fontes": ["solar", "eolica"]
        },
        "clima": {
            "temperatura": 22,
            "vento": 11,
            "umidade": 45
        },
        "sistemas": {
            "suporte_vida": {"status": "ON", "prioridade": 1},
            "habitacao": {"status": "ON", "prioridade": 2},
            "laboratorio": {"status": "ON", "prioridade": 3},
            "iluminacao_externa": {"status": "ON", "prioridade": 4}
        }
    }
    return colonia_dados

def tomar_decisoes(energia, consumo, sistemas):
    """
    Aplica regras de decisão baseadas nos níveis de energia e consumo.
    Prioriza sistemas essenciais.
    """
    acoes = []
    
    # Regra básica 1
    if energia < 50:
        acoes.append("ALERTA: Reduzir consumo imediato.")
    
    # Regra combinada 2
    if energia < 50 and consumo > 60:
        acoes.append("MODO ECONOMIA: Ativando protocolo de emergência.")
    
    # Priorização
    decisao_final = "Operação Normal"
    if energia < 30:
        decisao_final = "CRÍTICO: Desligando sistemas não essenciais. Mantendo apenas Suporte à Vida."
        for nome, info in sistemas.items():
            if info["prioridade"] > 1:
                info["status"] = "OFF"
    elif energia < 50:
        decisao_final = "ALERTA: Reduzir consumo."
    
    return decisao_final, acoes

def prever_energia_eolica(vento_historico, energia_historica, vento_atual):
    """
    Realiza uma regressão linear simples para prever a geração de energia.
    """
    n = len(vento_historico)
    if n != len(energia_historica) or n == 0:
        return 0
    
    sum_x = sum(vento_historico)
    sum_y = sum(energia_historica)
    sum_xy = sum(x * y for x, y in zip(vento_historico, energia_historica))
    sum_x2 = sum(x**2 for x in vento_historico)
    
    # Cálculo do coeficiente angular (m) e intercepto (b) da reta y = mx + b
    # m = (n*sum_xy - sum_x*sum_y) / (n*sum_x2 - (sum_x)**2)
    denominador = (n * sum_x2 - sum_x**2)
    if denominador == 0:
        m = 0
    else:
        m = (n * sum_xy - sum_x * sum_y) / denominador
        
    b = (sum_y - m * sum_x) / n
    
    previsao = m * vento_atual + b
    return round(previsao, 2)

def analisar_uso_energia(geracao, consumo):
    """
    Analisa a relação entre geração e consumo de energia.
    """
    if consumo > geracao:
        return "ALERTA: Consumo maior que geração. Risco de esgotamento de reservas."
    elif geracao > consumo:
        return "SUGESTÃO: Geração excedente detectada. Armazenar energia nas baterias."
    else:
        return "ESTÁVEL: Geração e consumo equilibrados."

def main():
    print("=== SISTEMA INTEGRADO AURORA SIGER ===")
    
    # 1. Organização de Dados
    dados = organizar_dados()
    print("\n[1] Dados da Colônia Organizados:")
    for categoria, info in dados.items():
        print(f" - {categoria.capitalize()}: {info}")
    
    # 2. Previsão de Comportamento (Regressão)
    vento_hist = [8, 10, 12]
    energia_hist = [20, 25, 30]
    vento_atual = dados["clima"]["vento"]
    previsao = prever_energia_eolica(vento_hist, energia_hist, vento_atual)
    print(f"\n[2] Previsão de Energia Eólica:")
    print(f" - Entrada (Vento): {vento_atual} km/h")
    print(f" - Saída (Previsão de Energia): ≈ {previsao} units")
    
    # 3. Análise de Energia
    analise = analisar_uso_energia(dados["energia"]["geracao"], dados["energia"]["consumo"])
    print(f"\n[3] Análise de Fluxo Energético:")
    print(f" - Geração: {dados['energia']['geracao']} | Consumo: {dados['energia']['consumo']}")
    print(f" - Resultado: {analise}")
    
    # 4. Tomada de Decisão Automática
    # Simulação de cenário crítico
    print("\n[4] Simulação de Tomada de Decisão (Cenário de Baixa Energia):")
    energia_teste = 40
    consumo_teste = 70
    decisao, alertas = tomar_decisoes(energia_teste, consumo_teste, dados["sistemas"])
    
    print(f" - Entrada: Energia = {energia_teste}, Consumo = {consumo_teste}")
    for alerta in alertas:
        print(f" - {alerta}")
    print(f" - Decisão Final: {decisao}")

if __name__ == "__main__":
    main()
