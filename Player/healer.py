import battlecode as bc
import behaviour_tree as bt
import random
import units
import math
import astar

class Healer(units.Unit):
    """The container for the healer unit."""
    def __init__(self, unit, gc, maps):
        super().__init__(unit, gc)
        self._maps = maps
        self._healing_friend = None
        self._targeted_location = None
        self._path_to_follow = None

    def generate_tree(self):
        """Generates the tree for the knight."""
        tree = bt.FallBack()
        exist_injured_friend_sequence = bt.Sequence()
        friend_fallback = bt.FallBack()
        exist_injured_friend_sequence.add_child(self.ExistsInjuredFriend(self))
        injured_friend_in_range_sequence = bt.Sequence()
        friend_fallback.add_child(injured_friend_in_range_sequence)
        exist_injured_friend_sequence.add_child(friend_fallback)
        injured_friend_in_range_sequence.add_child(self.InjuredFriendInRange(self))
        injured_friend_in_range_sequence.add_child(self.FindHighestPriorityFriend(self))
        injured_friend_in_range_sequence.add_child(self.Heal(self))

        find_injured_friend_sequence = bt.Sequence()
        find_injured_friend_sequence.add_child(self.FindClosestInjuredFriend(self))
        find_injured_friend_sequence.add_child(self.CreatePath(self))
        find_injured_friend_sequence.add_child(self.MoveOnPath(self))
        find_injured_friend_sequence.add_child(injured_friend_in_range_sequence)

        friend_fallback.add_child(find_injured_friend_sequence)

        # Random movement
        move_randomly = self.MoveRandomly(self)
        tree.add_child(exist_injured_friend_sequence)
        tree.add_child(move_randomly)

        return tree



    class ExistsInjuredFriend(bt.Condition):
        """Check if there is an injured frind"""
        def __init__(self, outer):
            super().__init__()
            self.__outer = outer

        def condition(self):
            units = self.__outer._gc.my_units()
            healer = self.__outer.unit()
            for unit in units:
                if unit.unit_type != bc.UnitType.Factory and unit.id != healer.id and unit.health < unit.max_health:
                    return True

            return False

    class InjuredFriendInRange(bt.Condition):
        """Check if there is an injured frind"""
        def __init__(self, outer):
            super().__init__()
            self.__outer = outer

        def condition(self):
            healer = self.__outer.unit()
            location = healer.location.map_location()
            nearby = self.__outer._gc.sense_nearby_units_by_team(location, healer.attack_range(), self.__outer._gc.team())
            for unit in nearby:
                if unit.unit_type != bc.UnitType.Factory and unit.id != healer.id and unit.health < unit.max_health:
                    return True

            return False

    class FindHighestPriorityFriend(bt.Action):
        """Find the injured friend with highest heal priority (just now only health is cheched)"""
        def __init__(self, outer):
            super().__init__()
            self.__outer = outer

        def action(self):
            healer = self.__outer.unit()
            location = healer.location.map_location()
            nearby = self.__outer._gc.sense_nearby_units_by_team(location, healer.attack_range(), self.__outer._gc.team())
            lowestHealthProcentage = 1
            highestPrioUnit = None
            for unit in nearby:
                if unit.unit_type != bc.UnitType.Factory and unit.id != healer.id and unit.health < unit.max_health:
                    currentHealthProcentage = unit.health / unit.max_health
                    if currentHealthProcentage < lowestHealthProcentage:
                        lowestHealthProcentage = currentHealthProcentage
                        highestPrioUnit = unit.id

            if highestPrioUnit:
                self.__outer._healing_friend = highestPrioUnit
                self._status = bt.Status.SUCCESS
            else:
                self._status = bt.Status.FAIL

    class Heal(bt.Action):
        """Heal targeted friendly unit"""
        def __init__(self, outer):
            super().__init__()
            self.__outer = outer

        def action(self):
            friend = self.__outer.get_friendly_unit(self.__outer._healing_friend)
            unit = self.__outer.unit()

            self.__outer._path_to_follow = None
            self.__outer._targeted_location = None

            if not friend:
                self._status = bt.Status.FAIL
            else:
                if self.__outer._gc.is_heal_ready(unit.id) and self.__outer._gc.can_heal(unit.id, friend.id):
                    self.__outer._gc.heal(unit.id, friend.id)
                    print('friend healed')
                    if friend.health == friend.max_health:
                        self.__outer._healing_friend = None
                    self._status = bt.Status.SUCCESS
                else:
                    self._status = bt.Status.RUNNING

    class FindClosestInjuredFriend(bt.Action):
        """Find the closest injured friend"""
        def __init__(self, outer):
            super().__init__()
            self.__outer = outer

        def action(self):
            units = self.__outer._gc.my_units()
            healer = self.__outer.unit()
            healer_location = healer.location.map_location()
            my_units_map = self.__outer._maps['my_units_map']
            width = len(my_units_map)
            height = len(my_units_map[0])

            min_distance = math.inf
            min_unit_id = None
            for unit in units:
                if not unit.location.is_on_map():
                    continue
                if unit.unit_type != bc.UnitType.Factory and unit.id != healer.id and unit.health < unit.max_health:
                    current_distance = healer_location.distance_squared_to(unit.location.map_location())
                    if current_distance < min_distance:
                        min_distance = current_distance
                        min_unit_id = unit.id

            if min_unit_id:

                unit_range = healer.attack_range()
                position_found = False
                while not position_found:
                    for x in range(-unit_range , unit_range  + 1):
                        for y in range(-unit_range , unit_range + 1):
                            possible_location = healer_location.translate(x,y)

                            # Check if location is outside of the map
                            if possible_location.x < 0 or possible_location.y < 0 or possible_location.x >= width or possible_location.y >= height:
                                continue
                            if not my_units_map[possible_location.x][possible_location.y]:
                                position_found = True
                                self.__outer._targeted_location = possible_location
                                self._status = bt.Status.SUCCESS
                                return
            else:
                self._status = bt.Status.FAIL

    class CreatePath(bt.Action):
        """Create path to closest injured friend"""
        def __init__(self, outer):
            super().__init__()
            self.__outer = outer

        def action(self):
            location = self.__outer._targeted_location
            healer = self.__outer.unit()
            terrain_map = self.__outer._maps['terrain_map']
            my_units_map = self.__outer._maps['my_units_map']
            path = astar.astar(terrain_map, my_units_map, healer.location.map_location(), location, max_path_length=10)
            if len(path) > 0:
                path.pop(0) # Remove the point the unit is already on
                self.__outer._path_to_follow = path
                self._status = bt.Status.SUCCESS
            else:
                self.__outer._path_to_follow = None
                self._status = bt.Status.FAIL


    class MoveOnPath(bt.Action):
        """Create path to closest injured friend"""
        def __init__(self, outer):
            super().__init__()
            self.__outer = outer

        def action(self):
            next_point = self.__outer._path_to_follow[0]
            healer = self.__outer.unit()
            unit_map_location = healer.location.map_location()
            move_direction = unit_map_location.direction_to(next_point)
            if self.__outer._gc.can_move(healer.id, move_direction):
                self._status = bt.Status.RUNNING
                if self.__outer._gc.is_move_ready(healer.id):
                    print('moved on path')
                    self.__outer._gc.move_robot(healer.id, move_direction)
                    self.__outer._path_to_follow.pop(0)
                    if len(self.__outer._path_to_follow) == 1:
                        self.__outer._path_to_follow = None
                        self._status = bt.Status.SUCCESS
            else:
                self.__outer._path_to_follow = None
                self._status = bt.Status.FAIL




    #################
    # MOVE RANDOMLY #
    #################

    class MoveRandomly(bt.Action):
        """Move in some random direction."""
        def __init__(self, outer):
            super().__init__()
            self.__outer = outer

        def action(self):
            random_dir = random.choice(list(bc.Direction))
            healer = self.__outer.unit()
            if self.__outer._gc.is_move_ready(healer.id) and self.__outer._gc.can_move(healer.id, random_dir):
                self.__outer._gc.move_robot(healer.id, random_dir)
                self._status = bt.Status.SUCCESS
            else:
                self._status = bt.Status.FAIL
