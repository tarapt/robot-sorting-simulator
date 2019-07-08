import os
import argparse
import subprocess
import time
import numpy as np
from random import shuffle
from ..map_generation.generate_map_config import Cell
from ..utils import CoordinateSpaceManager

HOME_DIR = os.environ['HOME']
CATKIN_WORKSPACE = HOME_DIR + '/catkin_ws/'
if os.environ.get('CATKIN_WORKSPACE'):
    CATKIN_WORKSPACE = os.environ['CATKIN_WORKSPACE']
CONFIG_FILE_LOCATION = CATKIN_WORKSPACE + '/src/sorting_robot/data/{}_configuration.npy'
GENERATED_SCRIPT_FILE = CATKIN_WORKSPACE + '/src/sorting_robot/data/spawn_robots_on_{}.sh'

ADD_ROBOT_TEMPLATE = 'rosrun stdr_robot robot_handler add $HOME/catkin_ws/src/sorting_robot/stdr_data/robots/pandora_robot.yaml {} {} {}\n'
WAIT_TIME_BETWEEN_CALLS = 3


def getRandomFreePoints(count, cells, grid):
    shuffle(cells)
    result = []
    for (r, c) in cells:
        if len(result) == count:
            break
        if not grid[r][c].isObstacle:
            result.append((r, c))
    return result


def generateSpawnLocations(mapName, numberOfLocations):
    global CONFIG_FILE_LOCATION, GENERATED_SCRIPT_FILE
    CONFIG_FILE_LOCATION = CONFIG_FILE_LOCATION.format(mapName)
    GENERATED_SCRIPT_FILE = GENERATED_SCRIPT_FILE.format(mapName)
    try:
        mapConfiguration = np.load(CONFIG_FILE_LOCATION).item()
    except IOError:
        print(CONFIG_FILE_LOCATION +
              " doesn't exist. Run the following command to create it:\nrosrun sorting_robot generate_map_config")
    else:
        grid = mapConfiguration['grid']
        cells = [(r, c) for r in range(grid.shape[0])
                 for c in range(grid.shape[1])]
        freeCells = getRandomFreePoints(numberOfLocations, cells, grid)
        csm = CoordinateSpaceManager(mapName)
        points = []
        for cell in freeCells:
            points.append(csm.getWorldCoordinateWithDirection(cell))

        commandsList = []
        with open(GENERATED_SCRIPT_FILE, "w") as f:
            for point in points:
                bashCommand = ADD_ROBOT_TEMPLATE.format(*point)
                f.write(bashCommand)
                commandsList.append(bashCommand)


def executeOneByOne(mapName):
    global GENERATED_SCRIPT_FILE
    GENERATED_SCRIPT_FILE = GENERATED_SCRIPT_FILE.format(mapName)
    with open(GENERATED_SCRIPT_FILE, "r") as f:
        commandsList = f.read().splitlines()
        for bashCommand in commandsList:
            process = subprocess.Popen(bashCommand, stdout=subprocess.PIPE, shell=True)
            output, error = process.communicate()
            print("Shell Output: " + output)
            if error is not None:
                print("Shell Error: " + error)
            print('waiting {} seconds for simulator to process the current request...'.format(WAIT_TIME_BETWEEN_CALLS))
            time.sleep(WAIT_TIME_BETWEEN_CALLS)


def executeAllAtOnce(mapName):
    global GENERATED_SCRIPT_FILE
    GENERATED_SCRIPT_FILE = GENERATED_SCRIPT_FILE.format(mapName)
    launchScriptCommand = 'bash {}'.format(GENERATED_SCRIPT_FILE)
    process = subprocess.Popen(launchScriptCommand, stdout=subprocess.PIPE, shell=True)
    output, error = process.communicate()
    print("Shell Output:\n" + output)
    if error is not None:
        print("Shell Error: " + error)


if __name__ == "__main__":
    generateSpawnLocations('map', 5)