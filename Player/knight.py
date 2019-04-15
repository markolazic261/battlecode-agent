import battlecode as bc
import behaviour_tree as bt
import random
import units


class Knight(units.Unit):
    """The container for the knight unit."""
    def __init__(self, unit, gc):
        super().__init__(unit, gc)
        self._targeted_enemy = None

    def update_targeted_enemy(self, enemy):
        self._targeted_enemy = enemy

    def get_targeted_enemy(self):
        return self._targeted_enemy

    def generate_tree(self):
        """Generates the tree for the knight."""
        tree = bt.FallBack()

        # Attack or chase enemies
        enemy_handling = bt.Sequence()
        enemy_visible = self.EnemyVisible(self)
        enemy_fallback = bt.FallBack()
        enemy_attack = bt.Sequence()
        enemy_adjacent = self.EnemyAdjacent(self)
        attack = self.Attack(self)
        enemy_attack.add_child(enemy_adjacent)
        enemy_attack.add_child(attack)
        enemy_chase = bt.Sequence()
        move_towards_enemy = self.MoveTowardsEnemy(self)
        enemy_chase.add_child(move_towards_enemy)
        enemy_chase.add_child(enemy_attack)
        enemy_fallback.add_child(enemy_attack)
        enemy_fallback.add_child(enemy_chase)
        enemy_handling.add_child(enemy_visible)
        enemy_handling.add_child(enemy_fallback)
        tree.add_child(enemy_handling)

        # Random movement
        move_randomly = self.MoveRandomly(self)
        tree.add_child(move_randomly)

        return tree

    ##################
    # ENEMY HANDLING #
    ##################

    class EnemyVisible(bt.Condition):
        """Check if there is an enemy close to the knight."""
        def __init__(self, outer):
            super().__init__()
            self.__outer = outer

        def condition(self):
            range = self.__outer._unit.vision_range
            location = self.__outer._unit.location.map_location()
            team = self.__outer._unit.team

            # If already have a targeted enemy which is in range, return True
            if self.__outer._targeted_enemy and location.distance_squared_to(self.__outer._targeted_enemy.location.map_location()) <= range:
                return True
            else:
                self.__outer._targeted_enemy = None

            # No saved enemy, look for new ones
            nearby_units = self.__outer._gc.sense_nearby_units(location, range)
            for unit in nearby_units:
                if unit.team != team:
                    self.__outer._targeted_enemy = unit
                    return True
            return False

    class EnemyAdjacent(bt.Condition):
        """Check if there is an enemy adjacent to the knight."""
        def __init__(self, outer):
            super().__init__()
            self.__outer = outer

        def condition(self):
            location = self.__outer._unit.location
            enemy_location = self.__outer._targeted_enemy.location
            return location.is_adjacent_to(enemy_location)

    class Attack(bt.Action):
        """Attacks the adjacent enemy."""
        def __init__(self, outer):
            super().__init__()
            self.__outer = outer

        def action(self):
            enemy = self.__outer._targeted_enemy
            unit = self.__outer._unit

            if not enemy:
                self._status = bt.Status.FAIL
            else:
                if self.__outer._gc.is_attack_ready(unit.id) and self.__outer._gc.can_attack(unit.id, enemy.id):
                    self.__outer._gc.attack(unit.id, enemy.id)
                    self._status = bt.Status.SUCCESS

                    # Remove targeted enemy if it died
                    location = unit.location.map_location()
                    killed_enemy = True
                    nearby_units = self.__outer._gc.sense_nearby_units(location, 2)
                    for nearby_unit in nearby_units:
                        if nearby_unit.id == enemy.id:
                            killed_enemy = False
                            break
                    if killed_enemy:
                        self.__outer._targeted_enemy = None
                else:
                    self._status = bt.Status.RUNNING

    class MoveTowardsEnemy(bt.Action):
        """Moves in the direction of the visible enemy."""
        def __init__(self, outer):
            super().__init__()
            self.__outer = outer

        def action(self):
            enemy = self.__outer._targeted_enemy
            unit = self.__outer._unit

            if not enemy:
                self._status = bt.Status.FAIL
            else:
                enemy_direction = unit.location.map_location().direction_to(enemy.location.map_location())
                if self.__outer._gc.is_move_ready(unit.id) and self.__outer._gc.can_move(unit.id, enemy_direction):
                    self.__outer._gc.move_robot(unit.id, enemy_direction)
                    self._status = bt.Status.SUCCESS
                else:
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
            if self.__outer._gc.is_move_ready(self.__outer._unit.id) and self.__outer._gc.can_move(self.__outer._unit.id, random_dir):
                self.__outer._gc.move_robot(self.__outer._unit.id, random_dir)
                self._status = bt.Status.SUCCESS
            else:
                self._status = bt.Status.FAIL
