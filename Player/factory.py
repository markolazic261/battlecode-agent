import battlecode as bc
import behaviour_tree as bt
import random
import units


class Factory(units.Unit):
    """The container for the factory unit."""
    def __init__(self, unit, gc):
        super().__init__(unit, gc)

    def generate_tree(self):
        tree = bt.Sequence()

        return tree
