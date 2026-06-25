# Cyber Digital Twin - IPVC

Este projeto apresenta um Digital Twin para a simulação de ataques de Engenharia Social (Phishing) em ambientes corporativos, permitindo a avaliação de diferentes estratégias de defesa e o seu impacto na propagação de ameaças.

## 🚀 Arquitetura do Sistema
O sistema utiliza uma arquitetura baseada em microsserviços, separando o motor de simulação da interface de utilizador:
- **Backend:** FastAPI (Motor de Simulação & API)
- **Frontend:** Streamlit (Dashboard de Controlo e Analytics)
- **Persistência:** SQLite (Histórico de Simulações, Configurações e Topologia de Rede)



## 📅 RoadMap de Desenvolvimento (Sprints)

### Sprint 0: Investigação e Conceitos
* Definição de conceitos de Digital Twin e aplicação no sistema.
* Investigação de ferramentas de simulação: NetLogo, AnyLogic e **Mesa (Framework escolhido)**.
* Definição da arquitetura de agentes, modelos e vetores de ataque.

### Sprint 1: Motor de Simulação
* **Modelagem de Agentes:** Implementação de agentes com perfis comportamentais (propensão ao risco, nível de consciência, hierarquia).
* **Configuração de Defesas:** Desenvolvimento de módulos de mitigação (MFA, segmentação de rede, programas de treino).
* **Motor Estocástico:** Lógica probabilística de propagação baseada em *Trust Maps*.

### Sprint 2: API e Persistência Inicial
* **Desenvolvimento da API RESTful:** Exposição do motor via FastAPI.
* **Pipeline de Persistência:** Integração inicial com SQLite.
* **Telemetria:** Sistema de *logging* assíncrono para monitorização de métricas (ticks da simulação).

### Sprint 3: Dashboard e Analytics
* **Dashboard Interativo:** Interface modular com Streamlit.
* **Módulo de Analytics Comparativo:** Execução em *Batch* para comparação de cenários.
* **Visualização de Histórico:** Sistema de arquivo para consulta de métricas e topologia.

### Sprint Final: Consolidação e Gestão de Dados
* **Design do Esquema SQLite:** Estruturação avançada (runs, configs, steps, graphs).
* **Persistência Transparente:** Automação da gravação de dados em tempo real.
* **Endpoints de Histórico:** Recuperação de dados retroativos e reconstrução de grafos históricos.

## 🛠️ Instalação

1. Clonar o repositório:
   ```bash
   git clone <link-do-repositorio>

2. Instalar dependencias
   ```bash
pip install -r requirements.txt