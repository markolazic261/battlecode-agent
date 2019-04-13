import battlecode as bc

class Strategy:
   __instance = None
   max_factories = 5
   nr_workers = 0
   nr_factories = 0
   nr_healers = 0
   nr_knights = 0
   nr_mages = 0
   nr_rangers = 0


   def resetCurrentUnits(self):
       self.nr_workers = 0
       self.nr_factories = 0
       self.nr_healers = 0
       self.nr_knights = 0
       self.nr_mages = 0
       self.nr_rangers = 0


   def addUnit(self, unitType):
       if unitType == bc.UnitType.Worker:
           self.nr_workers += 1
       elif unitType == bc.UnitType.Factory:
           self.nr_factories += 1
       elif unitType == bc.UnitType.Healer:
           self.nr_healers += 1
       elif unitType == bc.UnitType.Knight:
           self.nr_knights += 1
       elif unitType == bc.UnitType.Mage:
           self.nr_mages += 1
       elif unitType == bc.UnitType.Ranger:
           self.nr_rangers += 1

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
