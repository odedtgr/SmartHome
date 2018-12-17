class Scenario_Manager:

    def execute_scenario(self, scenario_name):
        for scenario_number in range(len(self.settings)):
            if scenario_name == self.settings[scenario_number].get('name'):
                for task_number in range(len(self.settings[scenario_number].get('tasks'))):
                    device_name = self.settings[scenario_number].get('tasks')[task_number].get('name')
                    for device in self.device_manager.devices_list:
                        if device.name == device_name:
                            args = self.settings[scenario_number].get('tasks')[task_number].get('args')
                            device.run_scheduler_task(args)
                            break



    def __init__(self, device_manager, settings):
        self.device_manager = device_manager
        self.settings = settings