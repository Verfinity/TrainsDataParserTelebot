import json


class ProjectDataLoader:
    @staticmethod
    def get_project_data() -> dict:
        settings_path = 'settings.json'

        with open(settings_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
            return data
