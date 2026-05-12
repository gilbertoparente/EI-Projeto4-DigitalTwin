📋 Requisitos do Projeto: Digital Twin de Cibersegurança
Este documento detalha os requisitos funcionais, técnicos e não-funcionais para o desenvolvimento do Digital Twin focado em simulação de ataques de Engenharia Social.

1. Requisitos Funcionais (RF)
RF01 - Modelação de Agentes: O sistema deve representar colaboradores individuais com atributos de cargo, departamento e nível de sensibilidade à segurança (probabilidade de clique).

RF02 - Grafo Sociotécnico: O sistema deve gerar uma rede de comunicações (baseada em NetworkX) que represente a hierarquia e os fluxos de confiança da organização.

RF03 - Vetores de Ataque: * Simulação de Phishing Genérico (broadcast).

Simulação de Spear Phishing (ataque direcionado que usa os contactos de um agente já comprometido).

RF04 - Medidas de Defesa: O utilizador deve poder ativar/configurar:

MFA (Multi-Factor Authentication): Redução da probabilidade de sucesso após roubo de credenciais.

Formação em Cibersegurança: Redução da probabilidade de clique inicial.

Segmentação de Rede: Limitação da propagação lateral entre departamentos.

RF05 - Visualização Real-time: Dashboard interativo que mostre a evolução do estado da rede (Saudável vs. Infetado) durante a simulação.

2. Requisitos Técnicos (RT)
RT01 - Framework Core: Utilização obrigatória da biblioteca Mesa (Python) para modelação baseada em agentes (ABM).

RT02 - Arquitetura de 3 Camadas:

Input: Interface de parametrização via UserSettableParameters.

Processamento: Lógica estocástica e motor de simulação em Python.

Output: Recolha de dados via DataCollector e visualização via ModularServer.

RT03 - Gestão de Dependências: Projeto configurado com ambiente virtual (venv) e ficheiro requirements.txt.

RT04 - Versionamento: Código hospedado e gerido via Git/GitHub.

3. Requisitos de Dados e Métricas (RD)
O sistema deve ser capaz de extrair e exibir as seguintes métricas (KPIs):

Taxa de Compromisso: Percentagem total da organização infetada.

MTTD (Mean Time To Detection): Tempo médio (em ticks) até que a simulação detete a ameaça.

Impacto por Departamento: Identificação das áreas mais vulneráveis da organização.

4. Requisitos Não-Funcionais (RNF)
RNF01 - Escalabilidade: O modelo deve suportar a simulação fluida de, pelo menos, 150 a 200 agentes.

RNF02 - Usabilidade: A interface deve ser intuitiva para que um gestor de TI (não programador) consiga ajustar os parâmetros de defesa.

