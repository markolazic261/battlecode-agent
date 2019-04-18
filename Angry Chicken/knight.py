import battlecode as bc
import behaviour_tree as bt
import random
import units


class Knight(units.Unit):
    """The container for the knight unit."""
    def __init__(self, unit, gc):
        super().__init__(unit, gc)
        self._targeted_enemy = None

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
        enemy_javelin = bt.Sequence()
        can_javelin = self.CanJavelin(self)
        javelin = self.Javelin(self)
        move_towards_enemy = self.MoveTowardsEnemy(self)
        enemy_javelin.add_child(can_javelin)
        enemy_javelin.add_child(javelin)
        enemy_javelin.add_child(move_towards_enemy)
        enemy_chase = bt.Sequence()
        enemy_chase.add_child(move_towards_enemy)
        enemy_chase.add_child(enemy_attack)
        enemy_fallback.add_child(enemy_attack)
        enemy_fallback.add_child(enemy_javelin)
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
            knight = self.__outer.unit()
            range = knight.vision_range
            location = knight.location.map_location()
            team = knight.team
            enemy_team = bc.Team.Red if team == bc.Team.Blue else bc.Team.Blue

            nearby_units = self.__outer._gc.sense_nearby_units_by_team(location, range, enemy_team)

            # No enemy visible
            if not nearby_units:
                return False

            # Look for the enemy closest to the knight with lowest health
            best_enemy = nearby_units[0]
            best_enemy_distance = location.distance_squared_to(best_enemy.location.map_location())
            for unit in nearby_units:
                enemy_distance = location.distance_squared_to(unit.location.map_location())
                if enemy_distance < best_enemy_distance:
                    best_enemy = unit
                    best_enemy_distance = enemy_distance
                elif enemy_distance == best_enemy_distance:
                    if unit.health < best_enemy.health:
                        best_enemy = unit
                        best_enemy_distance = enemy_distance

            self.__outer._targeted_enemy = best_enemy.id
            return True

    class EnemyAdjacent(bt.Condition):
        """Check if there is an enemy adjacent to the knight."""
        def __init__(self, outer):
            super().__init__()
            self.__outer = outer

        def condition(self):
            location = self.__outer.unit().location
            enemy_location = self.__outer.get_enemy_unit(self.__outer._targeted_enemy).location
            return location.is_adjacent_to(enemy_location)

    class Attack(bt.Action):
        """Attacks the adjacent enemy."""
        def __init__(self, outer):
            super().__init__()
            self.__outer = outer

        def action(self):
            enemy = self.__outer.get_enemy_unit(self.__outer._targeted_enemy)
            knight = self.__outer.unit()

            if not enemy:
                self._status = bt.Status.FAIL
            else:
                if self.__outer._gc.is_attack_ready(knight.id) and self.__outer._gc.can_attack(knight.id, enemy.id):
                    self.__outer._gc.attack(knight.id, enemy.id)
                    self._status = bt.Status.SUCCESS
                else:
                    self._status = bt.Status.RUNNING

    class CanJavelin(bt.Condition):
        """Check if the knight can perform a javelin attack."""
        def __init__(self, outer):
            super().__init__()
            self.__outer = outer

        def condition(self):
            knight = self.__outer.unit()
            enemy = self.__outer.get_enemy_unit(self.__outer._targeted_enemy)

            if knight.research_level < 3:
                return False

            if not enemy:
                return False

            distance = knight.location.map_location().distance_squared_to(enemy.location.map_location())
            return distance <= knight.ability_range()


    class Javelin(bt.Action):
        """Perform the javelin attack."""
        def __init__(self, outer):
            super().__init__()
            self.__outer = outer

        def action(self):
            enemy = self.__outer.get_enemy_unit(self.__outer._targeted_enemy)
            knight = self.__outer.unit()

            if not enemy:
                self._status = bt.Status.FAIL
            else:
                if self.__outer._gc.is_javelin_ready(knight.id) and self.__outer._gc.can_javelin(knight.id, enemy.id):
                    self.__outer._gc.javelin(knight.id, enemy.id)
                    self._status = bt.Status.SUCCESS
                else:
                    self._status = bt.Status.RUNNING


    class MoveTowardsEnemy(bt.Action):
        """Moves in the direction of the visible enemy."""
        def __init__(self, outer):
            super().__init__()
            self.__outer = outer

        def action(self):
            enemy = self.__outer.get_enemy_unit(self.__outer._targeted_enemy)
            knight = self.__outer.unit()

            if not enemy:
                self._status = bt.Status.FAIL
            else:
                enemy_direction = knight.location.map_location().direction_to(enemy.location.map_location())
                if self.__outer._gc.is_move_ready(knight.id) and self.__outer._gc.can_move(knight.id, enemy_direction):
                    self.__outer._gc.move_robot(knight.id, enemy_direction)
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
            knight = self.__outer.unit()
            if self.__outer._gc.is_move_ready(knight.id) and self.__outer._gc.can_move(knight.id, random_dir):
                self.__outer._gc.move_robot(knight.id, random_dir)
                self._status = bt.Status.SUCCESS
            else:
                self._status = bt.Status.FAIL
