import battlecode as bc
from abc import ABC, abstractmethod
import behaviour_tree as bt
import random
import strategy
import astar

class Unit(ABC):
    """An abstract class container for units. Contains the tree for the unit
    and the battlecode unit reference. Subclasses must implement a tree
    generation function.
    """
    def __init__(self, unit, gc):
        self._unit = unit
        self._gc = gc
        self._tree = self.generate_tree()

    @abstractmethod
    def generate_tree(self):
        pass

    def update_unit(self, unit):
        self._unit = unit

    def get_unit(self):
        return self._unit

    def run(self):
        """Runs the unit's behaviour tree and returns the result."""
        return self._tree.run()
        
