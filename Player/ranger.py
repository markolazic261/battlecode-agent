import battlecode as bc
import behaviour_tree as bt
import random
import units


class Ranger(units.Unit):
    """The container for the ranger unit."""
    def __init__(self, unit, gc):
        super().__init__(unit, gc)
        self._targeted_enemy = None

    def generate_tree(self):
        """Generates the tree for the ranger."""
        tree = bt.FallBack()

        # Attack or chase/run from enemies
        enemy_handling = bt.Sequence()
        enemy_visible = self.EnemyVisible(self)
        enemy_handling.add_child(enemy_visible)

        enemy_fallback = bt.FallBack()
        enemy_in_range = bt.Sequence()
        enemy_in_attack_range = self.EnemyInAttackRange(self)
        enemy_in_range.add_child(enemy_in_attack_range)
        attack = self.Attack(self)
        enemy_in_range.add_child(attack)

        enemy_close = bt.Sequence()
        enemy_too_close = self.EnemyTooClose(self)
        enemy_close.add_child(enemy_too_close)
        move_away = self.MoveAway(self)
        enemy_close.add_child(move_away)
        enemy_close.add_child(enemy_in_range)
        enemy_fallback.add_child(enemy_close)

        enemy_far = bt.Sequence()
        enemy_too_far = self.EnemyTooFar(self)
        enemy_far.add_child(enemy_too_far)
        move_towards = self.MoveTowards(self)
        enemy_far.add_child(move_towards)
        enemy_far.add_child(enemy_in_range)
        enemy_fallback.add_child(enemy_far)

        enemy_fallback.add_child(enemy_in_range)
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
        """Check if there is an enemy in range of the ranger."""
        def __init__(self, outer):
            super().__init__()
            self.__outer = outer

        def condition(self):
            ranger = self.__outer.unit()
            range = ranger.vision_range
            location = ranger.location.map_location()
            team = ranger.team
            enemy_team = bc.Team.Red if team == bc.Team.Blue else bc.Team.Blue

            # If already have a targeted enemy which is in range, return True
            enemy = self.__outer.get_enemy_unit(self.__outer._targeted_enemy)
            if enemy and location.distance_squared_to(enemy.location.map_location()) <= range:
                return True
            else:
                self.__outer._targeted_enemy = None

            # No saved enemy, look for new ones
            nearby_units = self.__outer._gc.sense_nearby_units_by_team(location, range, enemy_team)
            for unit in nearby_units:
                self.__outer._targeted_enemy = unit.id
                return True
            return False

    class EnemyInAttackRange(bt.Condition):
        """Check if the enemy is in attack range of the ranger."""
        def __init__(self, outer):
            super().__init__()
            self.__outer = outer

        def condition(self):
            ranger = self.__outer.unit()
            enemy = self.__outer.get_enemy_unit(self.__outer._targeted_enemy)

            enemy_distance = ranger.location.map_location().distance_squared_to(enemy.location.map_location())

            return enemy_distance > ranger.ranger_cannot_attack_range() and enemy_distance <= ranger.attack_range()

    class Attack(bt.Action):
        """Attacks the enemy targeted by the ranger."""
        def __init__(self, outer):
            super().__init__()
            self.__outer = outer

        def action(self):
            enemy = self.__outer.get_enemy_unit(self.__outer._targeted_enemy)
            ranger = self.__outer.unit()

            if not enemy:
                self._status = bt.Status.FAIL
            else:
                if self.__outer._gc.is_attack_ready(ranger.id) and self.__outer._gc.can_attack(ranger.id, enemy.id):
                    self.__outer._gc.attack(ranger.id, enemy.id)
                    self._status = bt.Status.SUCCESS

                    # Remove targeted enemy if it died
                    location = ranger.location.map_location()
                    range = ranger.vision_range
                    killed_enemy = True
                    nearby_units = self.__outer._gc.sense_nearby_units(location, range)
                    for nearby_unit in nearby_units:
                        if nearby_unit.id == enemy.id:
                            killed_enemy = False
                            break
                    if killed_enemy:
                        self.__outer._targeted_enemy = None
                else:
                    self._status = bt.Status.RUNNING

    class EnemyTooClose(bt.Condition):
        """Check if the enemy is too close to the ranger."""
        def __init__(self, outer):
            super().__init__()
            self.__outer = outer

        def condition(self):
            ranger = self.__outer.unit()
            enemy = self.__outer.get_enemy_unit(self.__outer._targeted_enemy)

            enemy_distance = ranger.location.map_location().distance_squared_to(enemy.location.map_location())

            return enemy_distance <= (ranger.attack_range() / 2)

    class MoveAway(bt.Action):
        """Moves away from the enemy."""
        def __init__(self, outer):
            super().__init__()
            self.__outer = outer

        def action(self):
            enemy = self.__outer.get_enemy_unit(self.__outer._targeted_enemy)
            ranger = self.__outer.unit()

            if not enemy:
                self._status = bt.Status.FAIL
            else:
                enemy_direction = ranger.location.map_location().direction_to(enemy.location.map_location())
                opposite_direction_position = ranger.location.map_location().subtract(enemy_direction)
                opposite_direction = ranger.location.map_location().direction_to(opposite_direction_position)
                if self.__outer._gc.is_move_ready(ranger.id) and self.__outer._gc.can_move(ranger.id, opposite_direction):
                    self.__outer._gc.move_robot(ranger.id, opposite_direction)
                    self._status = bt.Status.SUCCESS
                else:
                    self._status = bt.Status.FAIL

    class EnemyTooFar(bt.Condition):
        """Check if the enemy is too far from the ranger."""
        def __init__(self, outer):
            super().__init__()
            self.__outer = outer

        def condition(self):
            ranger = self.__outer.unit()
            enemy = self.__outer.get_enemy_unit(self.__outer._targeted_enemy)

            enemy_distance = ranger.location.map_location().distance_squared_to(enemy.location.map_location())

            return enemy_distance > ranger.attack_range()

    class MoveTowards(bt.Action):
        """Moves towards the enemy."""
        def __init__(self, outer):
            super().__init__()
            self.__outer = outer

        def action(self):
            enemy = self.__outer.get_enemy_unit(self.__outer._targeted_enemy)
            ranger = self.__outer.unit()

            if not enemy:
                self._status = bt.Status.FAIL
            else:
                enemy_direction = ranger.location.map_location().direction_to(enemy.location.map_location())
                if self.__outer._gc.is_move_ready(ranger.id) and self.__outer._gc.can_move(ranger.id, enemy_direction):
                    self.__outer._gc.move_robot(ranger.id, enemy_direction)
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
            ranger = self.__outer.unit()
            if self.__outer._gc.is_move_ready(ranger.id) and self.__outer._gc.can_move(ranger.id, random_dir):
                self.__outer._gc.move_robot(ranger.id, random_dir)
                self._status = bt.Status.SUCCESS
            else:
                self._status = bt.Status.FAIL
