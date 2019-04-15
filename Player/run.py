import battlecode as bc
import random
import sys
import traceback
import time
import astar
from worker import Worker
from knight import Knight
import strategy

gc = bc.GameController()
gc.queue_research(bc.UnitType.Worker)
gc.queue_research(bc.UnitType.Knight)
directions = list(bc.Direction)
karbonite_map = []
enemy_units_map = []
my_units_map = []
unit_map = []
terrain_map = []
my_team = gc.team()
enemy_team = bc.Team.Red if my_team == bc.Team.Blue else bc.Team.Blue
strategy = strategy.Strategy()
map_height = gc.starting_map(gc.planet()).height
map_width = gc.starting_map(gc.planet()).width
my_units = []


def build_units(units):
    for unit in units:
        if unit.unit_type != bc.UnitType.Factory:
            continue
        #print(gc.can_produce_robot(unit.id, bc.UnitType.Knight))
        #print(unit.is_factory_producing(), gc.karbonite() >= bc.cost_of(bc.UnitType.Knight, 1), gc.can_produce_robot(unit.id, bc.UnitType.Knight))
        garrison = unit.structure_garrison()
        if len(garrison) > 0:
            d = random.choice(directions)
            if gc.can_unload(unit.id, d):
                gc.unload(unit.id, d)
                knight = gc.sense_unit_at_location(unit.location.map_location().add(d))
                if knight:
                    my_units.append(Knight(knight, gc))
                continue
        elif gc.can_produce_robot(unit.id, bc.UnitType.Knight):
            gc.produce_robot(unit.id, bc.UnitType.Knight)
            continue


def update_my_units_map(units):
    """Updates the map containing information regarding friendly units."""
    for x in range(map_width):
        for y in range(map_height):
            my_units_map[x][y] = None
    strategy.getInstance().resetCurrentUnits()
    for unit in units:
        strategy.getInstance().addUnit(unit.unit_type)
        location = unit.location
        if location.is_on_map():
            map_location = location.map_location()
            my_units_map[map_location.x][map_location.y] = unit


def update_enemy_units_map(units):
    """Updates the map attempting to keep track of enemy units."""
    for x in range(map_width):
        for y in range(map_height):
            if enemy_units_map[x][y] and enemy_units_map[x][y].unit_type != bc.UnitType.Factory:
                enemy_units_map[x][y] = None
    for unit in units:
        location = unit.location
        if location.is_on_map():
            update_karbonite_map(location, unit.vision_range)
            nearby = gc.sense_nearby_units_by_team(location.map_location(), unit.vision_range, enemy_team)
            for enemy in nearby:
                map_location = enemy.location.map_location()
                enemy_units_map[map_location.x][map_location.y] = unit


def update_karbonite_map(unit_location, range):
    """Updates the map containing information regarding karbonite."""
    locations = gc.all_locations_within(unit_location.map_location(), range)
    for map_location in locations:
        karbonite_map[map_location.x][map_location.y] = gc.karbonite_at(map_location)


def init_workers():
    """Initializes the worker units with behaviour trees."""
    units = gc.my_units()
    for unit in units:
        my_units.append(Worker(
            unit,
            gc,
            {
                "karbonite_map": karbonite_map,
                "terrain_map": terrain_map,
                "my_units_map": my_units_map
            }
        ))


def update_units(units):
    """Updates all behaviour trees such that the _unit field (and more) is up to date."""
    for unit in units:
        for my_unit in my_units:
            if unit.id == my_unit.get_unit().id:
                my_unit.update_unit(unit)

                # Update targeted enemy for knights
                if my_unit.get_unit().unit_type == bc.UnitType.Knight:
                    if my_unit.get_targeted_enemy():
                        team = my_unit.get_unit().team
                        range = my_unit.get_unit().vision_range
                        location = my_unit.get_unit().location.map_location()

                        nearby_units = gc.sense_nearby_units(location, range)
                        found_enemy = False
                        for nearby_unit in nearby_units:
                            if nearby_unit.team != team and nearby_unit.id == my_unit.get_targeted_enemy().id:
                                my_unit.update_targeted_enemy(nearby_unit)
                                found_enemy = True
                                break
                        if not found_enemy:
                            my_unit.update_targeted_enemy(None)


def init_maps():
    """Initializes maps used by the AI."""
    map = gc.starting_map(gc.planet())
    for x in range(map_width):
        karbonite_map.append([])
        terrain_map.append([])
        enemy_units_map.append([])
        my_units_map.append([])
        for y in range(map_height):
            loc = bc.MapLocation(gc.planet(),x,y)
            karbonite_map[x].append(map.initial_karbonite_at(loc))
            terrain_map[x].append(map.is_passable_terrain_at(loc))
            enemy_units_map[x].append(None)
            my_units_map[x].append(None)


if gc.planet() == bc.Planet.Earth:
    init_maps()
    init_workers()
while True:
    if gc.planet() == bc.Planet.Mars:
        gc.next_turn()
    else:
        try:
            units = gc.my_units()
            update_units(units)
            update_enemy_units_map(units)
            update_my_units_map(units)
            print(strategy.getInstance().unitNeeded())
            for unit in my_units:
                unit.run()
            build_units(units) #Temporary before factory trees are up
        except Exception as e:
            print('Error:', e)
            # use this to show where the error was
            traceback.print_exc()
        gc.next_turn()
        sys.stdout.flush()
        sys.stderr.flush()
