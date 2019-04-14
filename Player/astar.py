import battlecode as bc
import sys


directions = [dir for dir in bc.Direction if dir is not bc.Direction.Center]


class Node():
    """A node class for A* Pathfinding"""

    def __init__(self, parent=None, position=None):
        self.parent = parent
        self.position = position

        self.g = 0
        self.h = 0
        self.f = 0

    def __eq__(self, other):
        return ((self.position.x == other.position.x) and (self.position.y == other.position.y))


def astar(maze,friendly_units, start, end):
    """Returns a list of tuples as a path from the given start to the given end in the given maze"""
    # Create start and end node
    start_node = Node(None, start)
    start_node.g = start_node.h = start_node.f = 0
    end_node = Node(None, end)
    end_node.g = end_node.h = end_node.f = 0

    # Initialize both open and closed list
    open_list = []
    closed_list = []

    # Add the start node
    open_list.append(start_node)

    # Loop until you find the end

    while len(open_list) > 0:

        # Get the current node
        current_node = open_list[0]
        current_index = 0
        for index, item in enumerate(open_list):
            if item.f < current_node.f:
                current_node = item
                current_index = index

        # Pop current off open list, add to closed list
        open_list.pop(current_index)
        closed_list.append(current_node)

        #print('Current node: ', current_node.position)
        #print('Open list: ',[p.position for p in open_list])
        #print('Closed list: ', [p.position for p in closed_list])

        # Found the goal
        if current_node == end_node:
            path = []
            current = current_node
            while current is not None:
                path.append(current.position)
                current = current.parent
            return path[::-1] # Return reversed path

        # Generate children
        for dir in directions: # Adjacent squares

            # Get node position
            node_position = current_node.position.add(dir)

            # Make sure within range
            if node_position.x > (len(maze) - 1) or node_position.x < 0 or node_position.y > (len(maze[len(maze)-1]) -1) or node_position.y < 0:
                continue

            # Make sure walkable terrain
            if not maze[node_position.x][node_position.y] or friendly_units[node_position.x][node_position.y]:
                continue

            # Create new node
            new_node = Node(current_node, node_position)

            if new_node in closed_list:
                continue

            new_node.g = current_node.g + 1
            new_node.h = ((new_node.position.x - end_node.position.x) ** 2) + ((new_node.position.y - end_node.position.y) ** 2)
            new_node.f = new_node.g + new_node.h

            min_cost = 0
            min_index = -1

            for (index, node) in enumerate(open_list):
                if node == new_node and node.g < min_cost:
                    min_cost = node.g
                    min_index = index

            if min_index == -1:
                open_list.append(new_node)
            elif new_node.cost < min_cost:
                open_list.append(new_node)
    return []
