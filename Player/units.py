import battlecode as bc
from abc import ABC, abstractmethod
import behaviour_tree as bt
import random
import strategy

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
        enemies.add_child(self.EnemyVisible(self))
        enemies.add_child(self.MoveAwayFromEnemy(self))
        tree.add_child(enemies)

        # Move towards blueprints with no workers
        #find_blueprint = bt.Sequence()

        #tree.add_child(find_blueprint)

        # Add blueprints
        add_blueprint = bt.Sequence()
        add_blueprint.add_child(self.NeedAnotherFactory(self))
        add_blueprint.add_child(self.EnoughtKarboniteToBuild(self))
        add_blueprint.add_child(self.AddBlueprint(self))
        tree.add_child(add_blueprint)

        # Mine karbonite
        karbonite = bt.FallBack()
        adjacent_karbonite_sequence = bt.Sequence()
        adjacent_karbonite_sequence.add_child(self.KarboniteInAdjCell(self))
        adjacent_karbonite_sequence.add_child(self.HarvestKarbonite(self))
        karbonite.add_child(adjacent_karbonite_sequence)
        karbonite.add_child(self.MoveRandomly(self))
        tree.add_child(karbonite)

        return tree


    class MoveRandomly(bt.Action):
        """Move in some random direction"""
        def __init__(self, outer):
            super().__init__()
            self.__outer = outer

        def action(self):
            random_dir = random.choice(list(bc.Direction))
            if self.__outer._gc.is_move_ready(self.__outer._unit.id) and self.__outer._gc.can_move(self.__outer._unit.id, random_dir):
                self.__outer._gc.move_robot(self.__outer._unit.id, random_dir)
                self._status = bt.Status.SUCCESS
            else:
                self._status = bt.Status.FAIL

    class KarboniteInAdjCell(bt.Condition):
        def __init__(self, outer):
            super().__init__()
            self.__outer = outer

        def condition(self):
            for dir in list(bc.Direction):
                if self.__outer._gc.can_harvest(self.__outer._unit.id, dir):
                    return True
            return False

    class HarvestKarbonite(bt.Action):
        def __init__(self, outer):
            super().__init__()
            self.__outer = outer

        def action(self):
            karbonite_harvested = False
            for dir in list(bc.Direction):
                if self.__outer._gc.can_harvest(self.__outer._unit.id, dir):
                    self.__outer._gc.harvest(self.__outer._unit.id, dir)
                    karbonite_harvested = True
                    break
            if karbonite_harvested:
                self._status = bt.Status.SUCCESS
            else:
                self._status = bt.Status.FAIL


    class NeedAnotherFactory(bt.Condition):
        """Determines if we need another Factory."""
        def __init__(self, outer):
            super().__init__()
            self.__outer = outer

        def condition(self):
            return strategy.Strategy.getInstance().nr_factories < strategy.Strategy.getInstance().max_factories

    class EnoughtKarboniteToBuild(bt.Condition):
        """Determines if we have enought karbonite to build a factory"""
        def __init__(self, outer):
            super().__init__()
            self.__outer = outer

        def condition(self):
            return self.__outer._gc.karbonite() >= bc.UnitType.Factory.blueprint_cost()

    class AddBlueprint(bt.Action):
        """Adds a bleuprint to some of adjecant cells if possible"""
        def __init__(self, outer):
            super().__init__()
            self.__outer = outer

        def action(self):

            blueprint_added = False
            # Check if we can place a blueprint in any adjacent cell
            # TODO: Make this a bit smarter to chose a place for factory
            for dir in list(bc.Direction):
                if self.__outer._gc.can_blueprint(self.__outer._unit.id, bc.UnitType.Factory, dir):
                    self.__outer._gc.blueprint(self.__outer._unit.id, bc.UnitType.Factory, dir)
                    blueprint_added = True
                    break
            if blueprint_added:
                self._status = bt.Status.SUCCESS
            else:
                self._status = bt.Status.FAIL

    class EnemyVisible(bt.Condition):
        """Determines if there is a enemy unit in visible range."""
        def __init__(self, outer):
            super().__init__()
            self.__outer = outer

        def condition(self):
            location = self.__outer._unit.location
            if location.is_on_map():
                # Determines if we can see some enemy units beside workers and factories.
                enemy_team = bc.Team.Red if self.__outer._gc.team() == bc.Team.Blue else bc.Team.Blue
                nearby_enemy_units = self.__outer._gc.sense_nearby_units_by_team(location.map_location(),self.__outer._unit.vision_range,enemy_team)
                for enemy in nearby_enemy_units:
                    if enemy.unit_type != bc.UnitType.Factory and enemy.unit_type != bc.UnitType.Worker:
                        return True
            return False


    class MoveAwayFromEnemy(bt.Action):
        """Moves away from enemy units."""
        def __init__(self, outer):
            super().__init__()
            self.__outer = outer

        def action(self):
            ### TODO: Smart way for escaping enemies
            print("should run from enemies")
            self._status = bt.Status.FAIL


    class BlueprintAdjacent(bt.Condition):
        """Determines if there is a blueprint in an adjacent square."""
        def __init__(self, outer):
            super().__init__()
            self.__outer = outer

        def condition(self):
            # Already has a factory that it is building on
            if self.__outer._blueprint_to_build_on and self.__outer._gc.can_build(self.__outer._unit.id, self.__outer._blueprint_to_build_on.id) :
                return True
            else:
                self.__outer._blueprint_to_build_on = None


            # Look for factories that are not built yet
            location = self.__outer._unit.location
            if location.is_on_map():
                nearby_factories = self.__outer._gc.sense_nearby_units_by_type(location.map_location(), 2, bc.UnitType.Factory)
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
