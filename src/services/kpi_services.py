from typing import Dict

class KPIService:
    """
    Serviço responsável por calcular indicadores de desempenho (KPIs)
    da postura de segurança da organização simulada.
    """

    def compute(self, result: Dict[str, int], total_agents: int) -> Dict[str, float]:
        """
        Calcula as taxas de infecção, clique e abertura.
        """
        if total_agents <= 0:
            return {
                "infection_rate": 0.0,
                "click_rate": 0.0,
                "open_rate": 0.0,
                "conversion_click_to_infected": 0.0
            }

        infected = result.get("infected", 0)
        clicked = result.get("clicked", 0)
        opened = result.get("opened", 0)

        # Taxas relativas à população total
        infection_rate = infected / total_agents
        click_rate = clicked / total_agents
        open_rate = opened / total_agents

        # Taxa de conversão (Métrica avançada: dos que clicaram, quantos foram infectados?)
        # Útil para medir a eficácia do MFA e da Segmentação
        conversion_click_to_infected = infected / clicked if clicked > 0 else 0.0

        return {
            "infection_rate": round(infection_rate, 4),
            "click_rate": round(click_rate, 4),
            "open_rate": round(open_rate, 4),
            "conversion_rate": round(conversion_click_to_infected, 4)
        }