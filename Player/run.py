import battlecode as bc
import random
import sys
import traceback
import time
import astar

gc = bc.GameController()
gc.queue_research(bc.UnitType.Worker)
gc.queue_research(bc.UnitType.Knight)
directions = list(bc.Direction)
karbonite_map = []
enemy_unit_map = []
terrain_map = []


random.seed(10)


def build_factories(units):
    for unit in units:
        if unit.unit_type != bc.UnitType.Worker:
            continue
        location = unit.location
        if location.is_on_map():
            nearby = gc.sense_nearby_units(location.map_location(), 2)
            for other in nearby:
                if gc.can_build(unit.id, other.id):
                    gc.build(unit.id, other.id)
                    print('built a factory!')
                    continue
        for d in directions:
            if gc.karbonite() > bc.UnitType.Factory.blueprint_cost() and gc.can_blueprint(unit.id, bc.UnitType.Factory, d):
                gc.blueprint(unit.id, bc.UnitType.Factory, d)

def harvest_carbonite(units):
    for unit in units:
        if unit.unit_type != bc.UnitType.Worker:
            continue
        location = unit.location
        if location.is_on_map():
            '''
            nearby_locations = gc.all_locations_within(location.map_location(), 2)
            best_location = location
            most_karbonite = 0
            for loc in nearby_locations:
                karbonite_at_loc =  gc.karbonite_at(loc.map_location())
                if karbonite_at_loc > most_karbonite:
                    most_karbonite = karbonite_at_loc
                    best_location = loc.map_location()
            '''
            for dir in directions:
                if gc.can_harvest(unit.id, dir):
                    gc.harvest(unit.id, dir)

def attack(units):
    for unit in units:
        if unit.unit_type != bc.UnitType.Knight:
            continue
        location = unit.location
        if location.is_on_map():
            nearby = gc.sense_nearby_units(location.map_location(), 2)
            for other in nearby:
                if other.team != unit.team and gc.is_attack_ready(unit.id) and gc.can_attack(unit.id, other.id):
                    print('attacked a thing!')
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
                print('unloaded a unit!')
                gc.unload(unit.id, d)
                continue
        elif gc.can_produce_robot(unit.id, bc.UnitType.Knight):
            gc.produce_robot(unit.id, bc.UnitType.Knight)
            print('produced a unit!')
            continue


def move_randomly(units):

    for unit in units:
        d = random.choice(directions)
        if gc.is_move_ready(unit.id) and gc.can_move(unit.id, d):
            gc.move_robot(unit.id, d)

def init_maps():
    map = gc.starting_map(gc.planet())
    print(map.height, map.width)
    for x in range(map.width):
        karbonite_map.append([])
        terrain_map.append([])
        for y in range(map.height):
            loc = bc.MapLocation(gc.planet(),x,y)
            karbonite_map[x].append(map.initial_karbonite_at(loc))
            terrain_map[x].append(map.is_passable_terrain_at(loc))


if gc.planet() == bc.Planet.Earth:
    init_maps()
    #print(Astar.astar(terrain_map, bc.MapLocation(gc.planet(),0,0),bc.MapLocation(gc.planet(),32,49)))
while True:
    if gc.planet() == bc.Planet.Mars:
        gc.next_turn()
    else:
        try:
            units = gc.my_units()
            build_factories(units)
            harvest_carbonite(units)
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
