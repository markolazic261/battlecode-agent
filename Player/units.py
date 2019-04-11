import battlecode as bc
from abc import ABC, abstractmethod
import behaviour_tree as bt

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

    def run(self):
        """Runs the unit's behaviour tree and returns the result."""
        return self._tree.run()


class Worker(Unit):
    """The container for the worker unit."""
    def __init__(self, unit, gc, maps):
        super().__init__(unit, gc)
        self.__maps = maps

        self._blueprint_to_build_on = None

    def generate_tree(self):
        """Generates the tree for the worker."""
        tree = bt.FallBack()

        # Build on adjacent blueprints
        build = bt.Sequence()
        build.add_child(self.BlueprintAdjacent(self))
        build.add_child(self.BuildBlueprint(self))
        tree.add_child(build)

        # Avoid enemies
        enemies = bt.Sequence()

        tree.add_child(enemies)

        # Move towards blueprints with no workers
        find_blueprint = bt.Sequence()

        tree.add_child(find_blueprint)

        # Add blueprints
        add_blueprint = bt.Sequence()

        tree.add_child(add_blueprint)

        # Mine karbonite
        karbonite = bt.FallBack()

        tree.add_child(karbonite)

        return tree

    class BlueprintAdjacent(bt.Condition):
        """Determines if there is a blueprint in an adjacent square."""
        def __init__(self, outer):
            super().__init__()
            self.__outer = outer

        def condition(self):
            # Already has a factory that it is building on
            if self.__outer._blueprint_to_build_on:
                return True

            # Look for factories that are not built yet
            location = self.__outer._unit.location
            if location.is_on_map():
                nearby_factories = self.__outer._gc.sense_nearby_units_by_type(location, 2, bc.UnityType.Factory)
                for factory in nearby_factories:
                    if self.__outer._gc.can_build(self.__outer._unit.id, factory.id):
                        # Found factory
                        self.__outer._blueprint_to_build_on = factory
                        return True
            return False

    class BuildBlueprint(bt.Action):
        """Builds on a blueprint that has been found adjacent to the worker."""
        def __init__(self, outer):
            super().__init__()
            self.__outer = outer

        def action(self):
            factory = self.__outer._blueprint_to_build_on

            # Factory does not exist even though it should
            if not factory:
                return bt.Status.FAIL

            # Build the factory and check if it is finished
            self.__outer._gc.build(self.__outer._unit.id, factory.id)
            if factory.structure_is_built():
                self.__outer._blueprint_to_build_on = None
                self._status = bt.Status.SUCCESS
            else:
                self._status = bt.Status.RUNNING
