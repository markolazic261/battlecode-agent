import battlecode as bc
import random
import sys
import traceback
import time

gc = bc.GameController()
gc.queue_research(bc.UnitType.Worker)
gc.queue_research(bc.UnitType.Rocket)
gc.queue_research(bc.UnitType.Knight)
directions = list(bc.Direction)

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
                    a = gc.can_harvest(unit.id, dir)





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



while True:
    try:
        units = gc.my_units()

        build_factories(units)
        harvest_carbonite(units)
        build_units(units)
        move_randomly(units)
    except Exception as e:
        print('Error:', e)
        # use this to show where the error was
        traceback.print_exc()
    gc.next_turn()
    sys.stdout.flush()
    sys.stderr.flush()
