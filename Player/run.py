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

directions = list(bc.Direction)
karbonite_map = []
enemy_units_map = []
my_units_map = []
unit_map = []
terrain_map = []
my_team = gc.team()
enemy_team = bc.Team.Red if my_team == bc.Team.Blue else bc.Team.Blue
#strategy = strategy.Strategy()
map_height = gc.starting_map(gc.planet()).height
map_width = gc.starting_map(gc.planet()).width
my_units = []


def update_my_units_map(units):
    """Updates the map containing information regarding friendly units."""
    for x in range(map_width):
        for y in range(map_height):
            my_units_map[x][y] = None
    strategy.Strategy.getInstance().resetCurrentUnits()
    for unit in units:
        strategy.Strategy.getInstance().addUnit(unit.unit_type)
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
                enemy_units_map[map_location.x][map_location.y] = enemy


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
            unit.id,
            gc,
            {
                "karbonite_map": karbonite_map,
                "terrain_map": terrain_map,
                "my_units_map": my_units_map,
                "enemy_units_map": enemy_units_map
            },
            my_units
        ))


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


def remove_dead_units():
    my_units[:] = [unit for unit in my_units if unit.unit()]


if gc.planet() == bc.Planet.Earth:
    init_maps()
    init_workers()
    for research in strategy.Strategy.research_strategy:
        gc.queue_research(research)
while True:
    if gc.planet() == bc.Planet.Mars:
        gc.next_turn()
    else:
        try:
            units = gc.my_units()
            remove_dead_units()
            update_enemy_units_map(units)
            update_my_units_map(units)
            for unit in my_units:
                if unit.unit():
                    unit.run()
        except Exception as e:
            print('Error:', e)
            # use this to show where the error was
            traceback.print_exc()
        gc.next_turn()
        sys.stdout.flush()
        sys.stderr.flush()
