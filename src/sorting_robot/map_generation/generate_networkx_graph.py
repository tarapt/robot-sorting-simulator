import os
import numpy as np
import networkx as nx
if os.environ.get('CIRCLECI'):
    import matplotlib
    matplotlib.use('agg')
import matplotlib.pyplot as plt
from matplotlib.patches import ArrowStyle
from generate_map_config import Cell, Direction, Turn, CellType
from ..utils.map_information_provider import CONFIG_FILE_LOCATION, GRAPH_PICKLED_FILE_LOCATION, GRAPH_IMAGE_FILE_LOCATION

# Note that these weights are just placeholders, the actual weights change with heatmap
TURN_COST = 50
MOVE_COST = 20

CELL_LENGTH = 2


def addEdges(grid, graph):
    for row in range(0, grid.shape[0]):
        for col in range(0, grid.shape[1]):
            cell = grid[row][col]
            if cell.isObstacle:
                if cell.cellType == CellType.PARCEL_BIN:
                    neighbours = [(row - 1, col), (row + 1, col), (row, col - 1), (row, col + 1)]
                    for neighbour in neighbours:
                        neighbourCell = grid[neighbour[0]][neighbour[1]]
                        direction = list(neighbourCell.directions)[0]
                        if(direction == Direction.RIGHT):
                            neighbourNode = neighbour + (0, )
                        elif(direction == Direction.UP):
                            neighbourNode = neighbour + (90, )
                        elif(direction == Direction.LEFT):
                            neighbourNode = neighbour + (180, )
                        elif(direction == Direction.DOWN):
                            neighbourNode = neighbour + (270, )
                        graph.add_edge((row, col), neighbourNode)
            else:
                for direction in cell.directions:
                    if(direction == Direction.RIGHT):
                        graph.add_edge(
                            (row, col, 0), (row, col + 1, 0), weight=MOVE_COST)
                    if(direction == Direction.UP):
                        graph.add_edge(
                            (row, col, 90), (row - 1, col, 90), weight=MOVE_COST)
                    if(direction == Direction.LEFT):
                        graph.add_edge((row, col, 180),
                                       (row, col - 1, 180), weight=MOVE_COST)
                    if(direction == Direction.DOWN):
                        graph.add_edge((row, col, 270),
                                       (row + 1, col, 270), weight=MOVE_COST)

                for turn in cell.allowedTurns:
                    if(turn == Turn.UP_LEFT):
                        graph.add_edge(
                            (row, col, 90), (row, col, 180), weight=TURN_COST)
                    elif(turn == Turn.DOWN_RIGHT):
                        graph.add_edge((row, col, 270),
                                       (row, col, 0), weight=TURN_COST)
                    elif(turn == Turn.RIGHT_UP):
                        graph.add_edge(
                            (row, col, 0), (row, col, 90), weight=TURN_COST)
                    elif(turn == Turn.LEFT_DOWN):
                        graph.add_edge((row, col, 180),
                                       (row, col, 270), weight=TURN_COST)
                    elif(turn == Turn.LEFT_UP):
                        graph.add_edge((row, col, 180),
                                       (row, col, 90), weight=TURN_COST)
                    elif(turn == Turn.RIGHT_DOWN):
                        graph.add_edge(
                            (row, col, 0), (row, col, 270), weight=TURN_COST)
                    elif(turn == Turn.UP_RIGHT):
                        graph.add_edge(
                            (row, col, 90), (row, col, 0), weight=TURN_COST)
                    elif(turn == Turn.DOWN_LEFT):
                        graph.add_edge((row, col, 270),
                                       (row, col, 180), weight=TURN_COST)


def getNodePositions(G, grid):
    pos = {}
    for node in G.nodes():
        center = (node[1] * 3 * CELL_LENGTH, -node[0] * 3 * CELL_LENGTH)
        cell = grid[node[0]][node[1]]
        if cell.cellType != CellType.PARCEL_BIN and len(cell.directions) > 1:
            offset = 0.5
            if node[2] == 0:
                pos[node] = (center[0] + offset * CELL_LENGTH, center[1])
            elif node[2] == 90:
                pos[node] = (center[0], center[1] + offset * 5 * CELL_LENGTH)
            elif node[2] == 180:
                pos[node] = (center[0] - offset * CELL_LENGTH, center[1])
            elif node[2] == 270:
                pos[node] = (center[0], center[1] - offset * CELL_LENGTH)
        else:
            pos[node] = center
    return pos


def generateNetworkxGraph(saveFig=False):
    try:
        mapConfiguration = np.load(CONFIG_FILE_LOCATION).item()
    except IOError:
        print(CONFIG_FILE_LOCATION +
              " doesn't exist. Run the following command to create it:\nrosrun sorting_robot generate_map_config")
    else:
        grid = mapConfiguration['grid']
        G = nx.DiGraph()
        addEdges(grid, G)

        pos = getNodePositions(G, grid)

        nx.write_gpickle(G, GRAPH_PICKLED_FILE_SAVE_LOCATION)
        if saveFig:
            plt.axes().set_aspect('auto')
            nx.draw(G, pos=pos, node_size=0.005, width=0.25, arrowstyle=ArrowStyle.CurveB(head_length=.05, head_width=.05))
            plt.savefig(GRAPH_IMAGE_FILE_LOCATION, dpi=1200)


if __name__ == "__main__":
    generateNetworkxGraph(saveFig=True)
