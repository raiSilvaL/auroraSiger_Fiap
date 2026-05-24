# Sistema Aurora Siger

Este projeto foi desenvolvido como parte de uma atividade com o objetivo de simular um sistema de análise e tomada de decisão para uma colônia espacial, focando na gestão de recursos e na otimização do uso de energia.

## Funcionalidades

O sistema integra as seguintes funcionalidades:

1.  **Organização de Dados da Colônia**: Armazena e organiza dados essenciais como níveis de energia (geração, consumo, reserva), condições climáticas (temperatura, vento, umidade) e o status de sistemas críticos da colônia de forma hierárquica.
2.  **Tomada de Decisões Automática**: Implementa regras de decisão baseadas nos dados coletados para gerenciar o consumo de energia e priorizar sistemas em cenários de escassez. Por exemplo, se a energia cair abaixo de um limite, o sistema pode recomendar a redução do consumo ou até mesmo desligar sistemas não essenciais.
3.  **Previsão de Comportamentos Simples (Regressão)**: Utiliza um modelo de regressão linear simples para prever a geração de energia eólica com base em dados históricos de vento, auxiliando no planejamento energético.
4.  **Análise de Uso de Energia**: Compara a geração e o consumo de energia para identificar situações de risco (consumo > geração) ou oportunidades de armazenamento (geração > consumo).

## Estrutura do Código

O código-fonte principal está localizado em `sistema_aurora.py` e é organizado em funções modulares para cada funcionalidade:

-   `organizar_dados()`: Inicializa e estrutura os dados da colônia.
-   `tomar_decisoes(energia, consumo, sistemas)`: Aplica as regras de decisão e retorna as ações recomendadas.
-   `prever_energia_eolica(vento_historico, energia_historica, vento_atual)`: Realiza a previsão de energia eólica.
-   `analisar_uso_energia(geracao, consumo)`: Analisa o balanço energético.
-   `main()`: Orquestra a execução das funcionalidades e simula um cenário completo.

## Exemplo de Uso

Para executar o sistema, basta rodar o arquivo `sistema_aurora.py`:

```bash
python3 sistema_aurora.py
```

### Exemplo de Entrada e Saída

Considerando os dados iniciais e um cenário simulado de baixa energia, o sistema produzirá uma saída similar a esta:

```
=== SISTEMA INTEGRADO AURORA SIGER ===

[1] Dados da Colônia Organizados:
 - Energia: {'geracao': 80, 'consumo': 30, 'reserva': 500, 'fontes': ['solar', 'eolica']}
 - Clima: {'temperatura': 22, 'vento': 11, 'umidade': 45}
 - Sistemas: {'suporte_vida': {'status': 'ON', 'prioridade': 1}, 'habitacao': {'status': 'ON', 'prioridade': 2}, 'laboratorio': {'status': 'ON', 'prioridade': 3}, 'iluminacao_externa': {'status': 'ON', 'prioridade': 4}}

[2] Previsão de Energia Eólica:
 - Entrada (Vento): 11 km/h
 - Saída (Previsão de Energia): ≈ 27.5 units

[3] Análise de Fluxo Energético:
 - Geração: 80 | Consumo: 30
 - Resultado: SUGESTÃO: Geração excedente detectada. Armazenar energia nas baterias.

[4] Simulação de Tomada de Decisão (Cenário de Baixa Energia):
 - Entrada: Energia = 40, Consumo = 70
 - ALERTA: Reduzir consumo imediato.
 - MODO ECONOMIA: Ativando protocolo de emergência.
 - Decisão Final: ALERTA: Reduzir consumo.
```

Este exemplo demonstra como o sistema organiza os dados, prevê a geração de energia eólica, analise energética e toma decisões em um cenário de baixa energia, priorizando a manutenção dos sistemas essenciais.
