class Organization:
    def __init__(self, departments: list, hierarchy: dict):
        self.departments = departments
        self.hierarchy = hierarchy  # manager → employees mapping

    def get_department_agents(self, department):
        pass