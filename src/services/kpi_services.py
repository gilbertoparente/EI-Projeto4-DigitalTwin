class KPIService:

    def compute(self, result: dict, total_agents: int) -> dict:
        total = max(total_agents, 1)
        infected = result.get("infected", 0)
        clicked  = result.get("clicked", 0)
        opened   = result.get("opened", 0)

        return {
            "infection_rate":   round(infected / total, 4),
            "click_rate":       round(clicked  / total, 4),
            "open_rate":        round(opened   / total, 4),
            "conversion_rate":  round(infected / max(clicked, 1), 4),
        }
