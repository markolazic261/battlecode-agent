import battlecode as bc
import behaviour_tree as bt
import random
import units
import math


class Mage(units.Unit):
    """The container for the mage unit."""
    def __init__(self, unit, gc, maps):
        super().__init__(unit, gc)
        self._targeted_enemy = None
        self._maps = maps

    def generate_tree(self):
        """Generates the tree for the mage."""
        tree = bt.FallBack()

        enemy_visible_sequence = bt.Sequence()
        enemy_visible_sequence.add_child(self.EnemyVisible(self))
        attack_sequence = bt.Sequence()
        attack_sequence.add_child(self.FindBestTarget(self))
        attack_sequence.add_child(self.Attack(self))
        enemy_visible_sequence.add_child(attack_sequence)
        move_randomly_sequence = bt.Sequence()
        move_randomly_sequence.add_child(self.MoveRandomly(self))
        move_randomly_sequence.add_child(enemy_visible_sequence)

        tree.add_child(enemy_visible_sequence)
        tree.add_child(move_randomly_sequence)

        return tree

    ##################
    # ENEMY HANDLING #
    ##################

    class EnemyVisible(bt.Condition):
        """Check if there is an enemy in range of the mage."""
        def __init__(self, outer):
            super().__init__()
            self.__outer = outer

        def condition(self):
            mage = self.__outer.unit()
            range = mage.vision_range
            location = mage.location.map_location()
            my_team = mage.team
            enemy_team = bc.Team.Red if my_team == bc.Team.Blue else bc.Team.Blue

            nearby_enemy_units = self.__outer._gc.sense_nearby_units_by_team(location, range, enemy_team)

            return len(nearby_enemy_units) > 0

    class FindBestTarget(bt.Action):
        """Find the best targed in the mages range"""
        def __init__(self, outer):
            super().__init__()
            self.__outer = outer

        def action(self):
            mage = self.__outer.unit()
            range = mage.vision_range
            location = mage.location.map_location()
            my_team = mage.team
            enemy_team = bc.Team.Red if my_team == bc.Team.Blue else bc.Team.Blue
            my_units_map = self.__outer._maps['my_units_map']

            best_target_id = None
            best_taget_hp = math.inf
            best_target_nr_enemies = 0
            nearby_enemy_units = self.__outer._gc.sense_nearby_units_by_team(location, range, enemy_team)
            for enemy in nearby_enemy_units:
                current_target_nr_enemies = 0
                current_target_hp = 0
                enemy_location = enemy.location.map_location()
                # get number of adjacent enemies
                for dir in list(bc.Direction):
                    adj_location = enemy_location.add(dir)
                    if self.__outer._gc.has_unit_at_location(adj_location) and not my_units_map[adj_location.x][adj_location.y]:
                        current_target_nr_enemies += 1
                        current_target_hp += self.__outer._gc.sense_unit_at_location(adj_location).health
                # update target with more enemies found
                if current_target_nr_enemies > best_target_nr_enemies:
                    best_target_nr_enemies = current_target_nr_enemies
                    best_taget_hp = current_target_hp
                    best_target_id = enemy.id
                # if same number of enemies at target take the one with lowest combined hp
                elif current_target_nr_enemies == best_target_nr_enemies and current_target_hp < best_taget_hp:
                    best_target_nr_enemies = current_target_nr_enemies
                    best_taget_hp = current_target_hp
                    best_target_id = enemy.id

            if best_target_id:
                self.__outer._targeted_enemy = best_target_id
                self._status = bt.Status.SUCCESS
            else:
                self._status = bt.Status.FAIL



    class Attack(bt.Action):
        """Attacks the enemy targeted by the mage."""
        def __init__(self, outer):
            super().__init__()
            self.__outer = outer

        def action(self):
            enemy = self.__outer.get_enemy_unit(self.__outer._targeted_enemy)
            unit = self.__outer.unit()

            if not enemy:
                self._status = bt.Status.FAIL
            else:
                if self.__outer._gc.is_attack_ready(unit.id) and self.__outer._gc.can_attack(unit.id, enemy.id):
                    self.__outer._gc.attack(unit.id, enemy.id)
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
            ranger = self.__outer.unit()
            if self.__outer._gc.is_move_ready(ranger.id) and self.__outer._gc.can_move(ranger.id, random_dir):
                self.__outer._gc.move_robot(ranger.id, random_dir)
                self._status = bt.Status.SUCCESS
            else:
                self._status = bt.Status.FAIL
