import battlecode as bc

class Strategy:
    __instance = None

    unit_information = {
        'current_amount': {
            'worker': 0,
            'factory': 0,
            'healer': 0,
            'knight': 0,
            'mage': 0,
            'ranger': 0
        },
        'max_amount': {
            'worker': 3,
            'factory': 5,
            'healer': 5,
            'knight': 25,
            'mage': 10,
            'ranger': 15
        }
    }

    def resetCurrentUnits(self):
        """Resets the information regarding what units currently exist."""
        self.unit_information['current_amount'] = {
            'worker': 0,
            'factory': 0,
            'healer': 0,
            'knight': 0,
            'mage': 0,
            'ranger': 0
        }


    def addUnit(self, unitType):
        """Adds information regarding one type of unit existing."""
        if unitType == bc.UnitType.Worker:
            self.unit_information['current_amount']['worker'] += 1
        elif unitType == bc.UnitType.Factory:
            self.unit_information['current_amount']['factory'] += 1
        elif unitType == bc.UnitType.Healer:
            self.unit_information['current_amount']['healer'] += 1
        elif unitType == bc.UnitType.Knight:
            self.unit_information['current_amount']['knight'] += 1
        elif unitType == bc.UnitType.Mage:
            self.unit_information['current_amount']['mage'] += 1
        elif unitType == bc.UnitType.Ranger:
            self.unit_information['current_amount']['ranger'] += 1


    def getCurrentUnit(self, unitType):
        """Gets information regarding one type of unit existing."""
        if unitType == bc.UnitType.Worker:
            return self.unit_information['current_amount']['worker']
        elif unitType == bc.UnitType.Factory:
            return self.unit_information['current_amount']['factory']
        elif unitType == bc.UnitType.Healer:
            return self.unit_information['current_amount']['healer']
        elif unitType == bc.UnitType.Knight:
            return self.unit_information['current_amount']['knight']
        elif unitType == bc.UnitType.Mage:
            return self.unit_information['current_amount']['mage']
        elif unitType == bc.UnitType.Ranger:
            return self.unit_information['current_amount']['ranger']


    def getMaxUnit(self, unitType):
        """Gets information regarding one type of unit existing."""
        if unitType == bc.UnitType.Worker:
            return self.unit_information['max_amount']['worker']
        elif unitType == bc.UnitType.Factory:
            return self.unit_information['max_amount']['factory']
        elif unitType == bc.UnitType.Healer:
            return self.unit_information['max_amount']['healer']
        elif unitType == bc.UnitType.Knight:
            return self.unit_information['max_amount']['knight']
        elif unitType == bc.UnitType.Mage:
            return self.unit_information['max_amount']['mage']
        elif unitType == bc.UnitType.Ranger:
            return self.unit_information['max_amount']['ranger']


    def unitNeeded(self):
        """Determines the unit which a factory should build depending on
        the percentage of units of all types currently active.
        """
        # Determine the percent of all units created
        percentages = [(key, self.unit_information['current_amount'][key] / self.unit_information['max_amount'][key]) for key in self.unit_information['max_amount']]
        min_key = ''
        min_value = 1

        # Find the lowest percentage
        for percentage in percentages:
            if percentage[0] != 'factory' and percentage[1] < min_value:
                min_key = percentage[0]
                min_value = percentage[1]

        if min_key == 'worker':
            return bc.UnitType.Worker
        elif min_key == 'healer':
            return bc.UnitType.Healer
        elif min_key == 'knight':
            return bc.UnitType.Knight
        elif min_key == 'mage':
            return bc.UnitType.Mage
        elif min_key == 'ranger':
            return bc.UnitType.Ranger


    @staticmethod
    def getInstance():
        """ Static access method. """
        if Strategy.__instance == None:
            Strategy()
        return Strategy.__instance
    def __init__(self):
        """ Virtually private constructor. """
        if Strategy.__instance != None:
            raise Exception("This class is a Singleton!")
        else:
            Strategy.__instance = self
