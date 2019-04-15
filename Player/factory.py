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

        unload = self.Unload(self)
        tree.add_child(unload)

        build_fallback = bt.FallBack()
        non_workers = bt.Sequence()
        have_max_workers = self.HaveMaxWorkers(self)
        non_workers.add_child(have_max_workers)
        can_build = self.CanBuild(self)
        non_workers.add_child(can_build)
        non_workers_fallback = bt.FallBack()
        local_damage = bt.Sequence()
        damaged_units = self.DamagedUnits(self)
        local_damage.add_child(damaged_units)
        no_healer_nearby = self.NoHealerNearby(self)
        local_damage.add_child(no_healer_nearby)
        build_healer = self.BuildHealer(self)
        local_damage.add_child(build_healer)
        non_workers_fallback.add_child(local_damage)
        local_enemies = bt.Sequence()
        enemies_nearby = self.EnemiesNearby(self)
        local_enemies.add_child(enemies_nearby)
        build_knight = self.BuildKnight(self)
        local_enemies.add_child(build_knight)
        non_workers_fallback.add_child(local_enemies)
        build_global = self.BuildGlobal(self)
        non_workers_fallback.add_child(build_global)
        non_workers.add_child(non_workers_fallback)
        build_fallback.add_child(non_workers)

        workers = bt.Sequence()
        can_build_worker = self.CanBuildWorker(self)
        workers.add_child(can_build_worker)
        build_worker = self.BuildWorker(self)
        workers.add_child(build_worker)
        build_fallback.add_child(workers)
        tree.add_child(build_fallback)

        return tree

    ##########
    # UNLOAD #
    ##########

    class Unload(bt.Action):
        """Unloads a unit from the factory if it exists."""
        def __init__(self, outer):
            super().__init__()
            self.__outer = outer

        def action(self):
            self._status = bt.Status.FAIL #TODO: Add logic

    ###############
    # NON WORKERS #
    ###############

    class HaveMaxWorkers(bt.Condition):
        """Check if enough workers exist."""
        def __init__(self, outer):
            super().__init__()
            self.__outer = outer

        def condition(self):
            return False

    class CanBuild(bt.Condition):
        """Check if resources to build exist."""
        def __init__(self, outer):
            super().__init__()
            self.__outer = outer

        def condition(self):
            return False

    class DamagedUnits(bt.Condition):
        """Check if damaged units are nearby."""
        def __init__(self, outer):
            super().__init__()
            self.__outer = outer

        def condition(self):
            return False

    class NoHealerNearby(bt.Condition):
        """Check if a healer is already in the area."""
        def __init__(self, outer):
            super().__init__()
            self.__outer = outer

        def condition(self):
            return False

    class BuildHealer(bt.Action):
        """Builds a healer."""
        def __init__(self, outer):
            super().__init__()
            self.__outer = outer

        def action(self):
            self._status = bt.Status.FAIL #TODO: Add logic

    class EnemiesNearby(bt.Condition):
        """Check if an enemy is in the area."""
        def __init__(self, outer):
            super().__init__()
            self.__outer = outer

        def condition(self):
            return False

    class BuildKnight(bt.Action):
        """Builds a knight."""
        def __init__(self, outer):
            super().__init__()
            self.__outer = outer

        def action(self):
            self._status = bt.Status.FAIL #TODO: Add logic

    class BuildGlobal(bt.Action):
        """Builds a unit depending on what is needed globally."""
        def __init__(self, outer):
            super().__init__()
            self.__outer = outer

        def action(self):
            self._status = bt.Status.FAIL #TODO: Add logic

    ###########
    # WORKERS #
    ###########

    class CanBuildWorker(bt.Condition):
        """Check if resources exist to build a worker."""
        def __init__(self, outer):
            super().__init__()
            self.__outer = outer

        def condition(self):
            return False

    class BuildWorker(bt.Action):
        """Builds a worker."""
        def __init__(self, outer):
            super().__init__()
            self.__outer = outer

        def action(self):
            self._status = bt.Status.FAIL #TODO: Add logic
