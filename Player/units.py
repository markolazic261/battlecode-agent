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

    def run(self):
        """Runs the unit's behaviour tree and returns the result."""
        return self._tree.run()


class Worker(Unit):
    """The container for the worker unit."""
    def __init__(self, unit, gc, maps):
        super().__init__(unit, gc)
        self._maps = maps

        self._blueprint_to_build_on = None
        self._karbonite_to_mine = None
        self._path_to_follow = None
        self._neighby_karbonite_locations = []

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
        add_blueprint.add_child(self.EnoughKarboniteToBuild(self))
        add_blueprint.add_child(self.AddBlueprint(self))
        tree.add_child(add_blueprint)

        # Mine karbonite
        karbonite = bt.FallBack()
        adjacent_karbonite_sequence = bt.Sequence()
        adjacent_karbonite_sequence.add_child(self.KarboniteInAdjacentCell(self))
        adjacent_karbonite_sequence.add_child(self.HarvestKarbonite(self))
        #no_adj_karbonite_sequence = bt.Sequence()
        #no_adj_karbonite_sequence.add_child(self.KarboniteExists(self))
        #path_fallback = bt.FallBack()
        #path_following_sequence = bt.Sequence()
        #path_following_sequence.add_child(self.ExistPath(self))
        #path_following_sequence.add_child(self.MoveOnPath(self))
        #create_path_fallback = bt.FallBack()
        #create_path_sequence = bt.Sequence()
        #create_path_sequence.add_child(self.NeighbyKarboniteCells(self))
        #create_path_sequence.add_child(self.CreatePath(self))
        #create_path_fallback.add_child(create_path_sequence)
        #create_path_fallback.add_child(self.FindNeighbyKarboniteCells(self))
        #path_fallback.add_child(path_following_sequence)
        #path_fallback.add_child(create_path_fallback)
        #no_adj_karbonite_sequence.add_child(path_fallback)

        karbonite.add_child(adjacent_karbonite_sequence)
        #karbonite.add_child(no_adj_karbonite_sequence)
        karbonite.add_child(self.MoveRandomly(self))
        tree.add_child(karbonite)

        return tree

    ############
    # BUILDING #
    ############
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
                self._status = bt.Status.FAIL
            else:
                # Build the factory and check if it is finished
                self.__outer._gc.build(self.__outer._unit.id, factory.id)
                if factory.structure_is_built():
                    self.__outer._blueprint_to_build_on = None
                    self._status = bt.Status.SUCCESS
                else:
                    self._status = bt.Status.RUNNING

    ##################
    # ENEMY HANDLING #
    ##################

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
                nearby_enemy_units = self.__outer._gc.sense_nearby_units_by_team(location.map_location(), self.__outer._unit.vision_range, enemy_team)
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

    ##################
    # ADD BLUEPRINTS #
    ##################

    class NeedAnotherFactory(bt.Condition):
        """Determines if we need another Factory."""
        def __init__(self, outer):
            super().__init__()
            self.__outer = outer

        def condition(self):
            return strategy.Strategy.getInstance().nr_factories < strategy.Strategy.getInstance().max_factories

    class EnoughKarboniteToBuild(bt.Condition):
        """Determines if we have enought karbonite to build a Factory."""
        def __init__(self, outer):
            super().__init__()
            self.__outer = outer

        def condition(self):
            return self.__outer._gc.karbonite() >= bc.UnitType.Factory.blueprint_cost()

    class AddBlueprint(bt.Action):
        """Adds one blueprint to any of the adjacent cells if possible."""
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

    ##############
    # HARVESTING #
    ##############

    class KarboniteInAdjacentCell(bt.Condition):
        """Check if there is karbonite in any adjacent cells."""
        def __init__(self, outer):
            super().__init__()
            self.__outer = outer

        def condition(self):
            if self.__outer._karbonite_to_mine and self.__outer._gc.can_harvest(
                self.__outer._unit.id,
                self.__outer._karbonite_to_mine
            ):
                return True
            else:
                self.__outer.karbonite_to_mine = None

            for dir in list(bc.Direction):
                if self.__outer._gc.can_harvest(self.__outer._unit.id, dir):
                    self.__outer._karbonite_to_mine = dir
                    return True
            return False

    class HarvestKarbonite(bt.Action):
        """Harvest karbonite in any of the adjacent cells."""
        def __init__(self, outer):
            super().__init__()
            self.__outer = outer

        def action(self):
            karbonite_direction = self.__outer._karbonite_to_mine

            # Karbonite does not exist even though it should
            if not karbonite_direction:
                self._status = bt.Status.FAIL
            else:
                # Harvest the karbonite and check if deposit is empty
                self.__outer._gc.harvest(self.__outer._unit.id, karbonite_direction)
                amount = self.__outer._unit.worker_harvest_amount()
                karbonite_location = self.__outer._unit.location.map_location().add(karbonite_direction)
                self.__outer._maps['karbonite_map'][karbonite_location.x][karbonite_location.y] = max(
                    self.__outer._maps['karbonite_map'][karbonite_location.x][karbonite_location.y] - amount,
                    0
                )
                if self.__outer._maps['karbonite_map'][karbonite_location.x][karbonite_location.y] == 0:
                    self.__outer._karbonite_to_mine = None
                    self._status = bt.Status.SUCCESS
                else:
                    self._status = bt.Status.RUNNING

    class KarboniteExists(bt.Condition):
        """Check if there is any karbonite left on map"""
        def __init__(self, outer):
            super().__init__()
            self.__outer = outer

        def condition(self):
            for row in self.__outer._maps["karbonite_map"]:
                for karbonite_in_cell in row:
                    if karbonite_in_cell > 0:
                        return True
            return False

    class ExistPath(bt.Condition):
        """Check if we have a path to follow"""
        def __init__(self, outer):
            super().__init__()
            self.__outer = outer

        def condition(self):
            if self.__outer._path_to_follow:
                return True
            else:
                return False

    class MoveOnPath(bt.Action):
        """Move on current path"""
        def __init__(self, outer):
            super().__init__()
            self.__outer = outer

        def action(self):
            print('should move on path')
            return
            ## possibly a bit off logic here that can cause one extra turn to harvest. The final location is on the karbonite cell but we can harvest if adjacent.
            if len(self.__outer._path_to_follow) == 1:
                self.__outer._path_to_follow = None
                self._status = bt.Status.SUCCESS
                return
            next_point = self.__outer._path_to_follow[0]
            unit_map_location = self.__outer._unit.location.map_location()
            move_direction = unit_map_location.direction_to(next_point)
            if self.__outer._gc.can_move(self.__outer._unit.id, move_direction):
                if self.__outer._gc.is_move_ready(self.__outer._unit.id):
                    self.__outer._gc.move_robot(self.__outer._unit.id, move_direction)
                    self.__outer._path_to_follow.pop(0)
                self._status = bt.Status.RUNNING
            else:
                self.__outer._path_to_follow = None
                self._status = bt.Status.FAIL

    class NeighbyKarboniteCells(bt.Condition):
        """Check if we have some karbonite cell saved"""
        def __init__(self, outer):
            super().__init__()
            self.__outer = outer

        def condition(self):
            return len(self.__outer._neighby_karbonite_locations) > 0

    class CreatePath(bt.Action):
        """Create aStar path to first point in NeighbyKarboniteCells list"""
        def __init__(self, outer):
            super().__init__()
            self.__outer = outer

        def action(self):
            karbonite_location = self.__outer._neighby_karbonite_locations.pop(0)
            karbonite_map = self.__outer._maps["karbonite_map"]
            # someone stole karbonite meanwhile :(
            if karbonite_map[karbonite_location.x][karbonite_location.y] == 0:
                self.__outer._path_to_follow = None
                self._status = bt.Status.FAIL
                return
            terrain_map = self.__outer._maps["terrain_map"]
            my_units_map = self.__outer._maps["my_units_map"]
            unit_map_location = self.__outer._unit.location.map_location()
            path = astar.astar(terrain_map, my_units_map, unit_map_location,karbonite_location)
            if len(path) > 0:
                path.pop(0)
                self.__outer._path_to_follow = path
                self._status = bt.Status.SUCCESS
            else:
                self.__outer._path_to_follow = None
                self._status = bt.Status.FAIL

    class FindNeighbyKarboniteCells(bt.Action):
        """Find neighby cells with karbonite by expanding manhattan distance"""
        def __init__(self, outer):
            super().__init__()
            self.__outer = outer

        def action(self):
            directions = [dir for dir in bc.Direction if dir is not bc.Direction.Center]
            karbonite_map = self.__outer._maps["karbonite_map"]
            h = len(karbonite_map)
            w = len(karbonite_map[0])
            length = 2
            map_location = self.__outer._unit.location.map_location()
            while True:
                no_more_cells_left = True
                # iterate all directions
                for dir in directions:
                    # make a new location by adding a multiple of direction
                    possible_location = map_location.add_multiple(dir, length)
                    # check if outside the map
                    if possible_location.x < 0 or possible_location.y < 0 or possible_location.x >= h or possible_location.y >= w:
                        continue
                    # there is a direciton not outside the map, so we continue
                    no_more_cells_left = False
                    # check if there is karbonite there
                    if karbonite_map[possible_location.x][possible_location.y] > 0:
                        self.__outer._neighby_karbonite_locations.append(possible_location)
                # break if no unchecked cells left or we already have 3 possible cells (just a random number 3, nothing smart)
                if no_more_cells_left or len(self.__outer._neighby_karbonite_locations) > 3:
                    break
                length += 1

            if (len(self.__outer._neighby_karbonite_locations) > 0):
                self._status = bt.Status.SUCCESS
            else:
                self._status = bt.Status.FAIL

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
