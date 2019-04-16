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

    def get_unit(self, unit_id):
        try:
            return self._gc.unit(unit_id)
        except:
            # Unit not in visible range.
            return None

    def unit(self):
        return self.get_unit_from_id(self._unit)

    def run(self):
        """Runs the unit's behaviour tree and returns the result."""
        return self._tree.run()
