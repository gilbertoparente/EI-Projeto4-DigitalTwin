class KPIService:

    def compute(self, result, total_agents):

        infected = result["infected"]
        clicked = result["clicked"]
        opened = result["opened"]

        return {
            "infection_rate": infected / total_agents if total_agents else 0,
            "click_rate": clicked / total_agents if total_agents else 0,
            "open_rate": opened / total_agents if total_agents else 0
        }