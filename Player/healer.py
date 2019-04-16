import battlecode as bc
import behaviour_tree as bt
import random
import units

class Healer(units.Unit):
    """The container for the healer unit."""
    def __init__(self, unit, gc):
        super().__init__(unit, gc)
        self._targeted_friend = None

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
            units = self.__outer._gc.units()
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
                self.__outer._targeted_friend = highestPrioUnit
                self._status = bt.Status.SUCCESS
            else:
                self._status = bt.Status.FAIL

    class Heal(bt.Action):
        """Heal targeted friendly unit"""
        def __init__(self, outer):
            super().__init__()
            self.__outer = outer

        def action(self):
            friend = self.__outer.get_friendly_unit(self.__outer._targeted_friend)
            unit = self.__outer.unit()

            if not friend:
                self._status = bt.Status.FAIL
            else:
                if self.__outer._gc.is_heal_ready(unit.id) and self.__outer._gc.can_heal(unit.id, friend.id):
                    self.__outer._gc.heal(unit.id, friend.id)
                    print('friend healed')
                    if friend.health == friend.max_health:
                        self.__outer._targeted_friend = None
                    self._status = bt.Status.SUCCESS
                else:
                    self._status = bt.Status.RUNNING




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
