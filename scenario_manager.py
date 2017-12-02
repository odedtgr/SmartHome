class Scenario_Manager:

    def execute_scenario(self, scenario_name):
        for scenario_number in range(len(self.settings)):
            if scenario_name == self.settings[scenario_number].get('name'):
                for task_number in range(len(self.settings[scenario_number].get('tasks'))):
                    device_id = self.settings[scenario_number].get('tasks')[task_number].get('device_id')
                    args = self.settings[scenario_number].get('tasks')[task_number].get('args')
                    self.device_manager.update_device(device_id, args, True)
                return

    def __init__(self, device_manager, settings):
        self.device_manager = device_manager
        self.settings = settings