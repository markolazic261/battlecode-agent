import battlecode as bc
import random
import sys
import traceback
import time
import astar
import units as u
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

random.seed(10)

def attack(units):
    for unit in units:
        if unit.unit_type != bc.UnitType.Knight:
            continue
        location = unit.location
        if location.is_on_map():
            nearby = gc.sense_nearby_units(location.map_location(), 2)
            for other in nearby:
                if other.team != unit.team and gc.is_attack_ready(unit.id) and gc.can_attack(unit.id, other.id):
                    gc.attack(unit.id, other.id)
                    continue

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
                continue
        elif gc.can_produce_robot(unit.id, bc.UnitType.Knight):
            gc.produce_robot(unit.id, bc.UnitType.Knight)
            continue


def update_my_units_map(units):
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
    for x in range(map_width):
        for y in range(map_height):
            if enemy_units_map[x][y] and enemy_units_map[x][y].unit_type != bc.UnitType.Factory:
                enemy_units_map[x][y] = None
    for unit in units:
        location = unit.location
        if location.is_on_map():
            nearby = gc.sense_nearby_units_by_team(location.map_location(), unit.vision_range, enemy_team)
            for enemy in nearby:
                map_location = enemy.location.map_location()
                enemy_units_map[map_location.x][map_location.y] = unit

def move_randomly(units):
    for unit in units:
        d = random.choice(directions)
        if gc.is_move_ready(unit.id) and gc.can_move(unit.id, d):
            if unit.unit_type == bc.UnitType.Worker:
                continue
            gc.move_robot(unit.id, d)



def init_workers():
    units = gc.my_units()
    for unit in units:
        my_units.append(u.Worker(unit,gc,{}))

def init_maps():
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
    #print(astar.astar(terrain_map,my_units_map,bc.MapLocation(gc.planet(),0,0),bc.MapLocation(gc.planet(),32,49)))
while True:
    if gc.planet() == bc.Planet.Mars:
        gc.next_turn()
    else:
        try:
            units = gc.my_units()
            update_enemy_units_map(units)
            update_my_units_map(units)
            for unit in my_units:
                unit.run()
            build_units(units)
            attack(units)
            move_randomly(units)
        except Exception as e:
            print('Error:', e)
            # use this to show where the error was
            traceback.print_exc()
        gc.next_turn()
        sys.stdout.flush()
        sys.stderr.flush()
