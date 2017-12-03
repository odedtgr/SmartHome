class Scenario_Manager:

    def execute_scenario(self, scenario_name):
        for scenario_number in range(len(self.settings)):
            if scenario_name == self.settings[scenario_number].get('name'):
                for task_number in range(len(self.settings[scenario_number].get('tasks'))):
                    device_name = self.settings[scenario_number].get('tasks')[task_number].get('name')
                    for device_number in range(len(self.device_manager.devices)):
                        if self.device_manager.devices[device_number].get('name') == device_name:
                            device_id = self.device_manager.devices[device_number].get('id')
                            break
                    args = self.settings[scenario_number].get('tasks')[task_number].get('args')
                    self.device_manager.update_device(device_id, args, False)
                return

    def __init__(self, device_manager, settings):
        self.device_manager = device_manager
        self.settings = settings