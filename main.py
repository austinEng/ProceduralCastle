node = hou.pwd()
geo = node.geometry()
inputs = node.inputs()

import __builtin__
__builtin__.HOU = hou
__builtin__.GEO = geo
__builtin__.NODE = node
__builtin__.INPUTS = inputs

import random
import city
reload(city)

from city import initial
from city import stack
from city import keep
from city import spire
from city import classify
from city import decorate
from city import arch
reload(initial)
reload(stack)
reload(keep)
reload(spire)
reload(classify)
reload(decorate)
reload(arch)

SEED = inputs[1].evalParm("seed")
TYPES = [
    "initial", 
    "level0", 
    "tall", 
    "box", 
    "keep", 
    "tower_lower", 
    "tower_upper", 
    "dontkeep", 
    "destroy", 
    "wall1",
    "wall2",
    "wall3", 
    "wall_top", 
    "spire_lower", 
    "spire_upper", 
    "spire_segment", 
    "spire_segment_top",
    "spire_connection",
    "arch",
    "arch_tower",
    "terminal_keep",
    "roof"]

# Set of output houdini groups to be created
POINT_GROUPS = {}
AXES = [hou.Vector3(1,0,0), hou.Vector3(0,1,0), hou.Vector3(0,0,1)]
GENERATIONS = inputs[1].evalParm("generations")

try:
    geo.addAttrib(hou.attribType.Point, "active", 1)
except:
    pass

try:
    geo.addAttrib(hou.attribType.Point, "Cd", hou.Vector3(1,1,1))
except:
    pass

try:
    geo.addAttrib(hou.attribType.Point, "size", hou.Vector3(10,10,10))
except:
    pass

try:
    geo.addAttrib(hou.attribType.Point, "type", "box")
except:
    pass

try:
    geo.addAttrib(hou.attribType.Point, "building", "generic")
except:
    pass

try:
    geo.addAttrib(hou.attribType.Point, "hasSpire", 0)
except:
    pass

try:
    geo.addAttrib(hou.attribType.Point, "origin", hou.Vector3(0,0,0))
except:
    pass

try:
    geo.addAttrib(hou.attribType.Point, "up", hou.Vector3(0,1,0))
except:
    pass

try:
    geo.addAttrib(hou.attribType.Point, "N", hou.Vector3(0,0,1))
except:
    pass


for t in TYPES:
    POINT_GROUPS[t] = geo.createPointGroup(t)

# Store original geometry attributes
for point in geo.points():
    point.setAttribValue("origin", point.position())
    point.setAttribValue("type", "keep")
    POINT_GROUPS["keep"].add(point)


def makeSeed(*args):
    seed = 0;
    for arg in args:
        seed = seed + abs(arg) + 2 # avoid getting 1's and 0's
    return seed * SEED

def nothing(parent, size, iter):
    pass

def deactivate(parent, size, iter):
    parent.setAttribValue("active", 0)

def destroy(parent, size, iter):
    # geo.deletePoints([parent])
    parent.setAttribValue("active", 0)
    parent.setAttribValue("type", "destroy")

RULES = {
    "initial": [],
    # "initial": [(1, initial.initializeGroups)],
    "level0": [],
    "tall": [],
    "box": [],
    "keep": [
        (inputs[1].evalParm("keep_divide"), keep.divide), 
        (inputs[1].evalParm("keep_dontkeep"), keep.dontkeep), 
        (inputs[1].evalParm("keep_deactivate"), deactivate), 
        (inputs[1].evalParm("keep_destroy"), destroy)
    ],
    "tower_lower": [],
    "tower_upper": [],
    "dontkeep": [
        (inputs[1].evalParm("dontkeep_tower"), keep.tower), 
        (inputs[1].evalParm("dontkeep_deactivate"), deactivate),
        (inputs[1].evalParm("dontkeep_arch"), arch.makeArch)
    ],
    "terminal_keep": [
        # (inputs[1].evalParm("dontkeep_tower"), keep.tower),
    ],
    "arch": [],
    "arch_tower": []
}

# Apply a rule to this point based on type. Generates output points
def replacePoint(parent, size, iter):
    random.seed(makeSeed(parent.number(), iter))
    t = point.attribValue("type")
    if t in RULES and point.attribValue("active"):
        u = random.random()
        if len(RULES[t]):
            i = 0
            cumul = 0
            try:
                while (u > RULES[t][i][0] + cumul):
                    cumul += RULES[t][i][0]
                    i += 1
                RULES[t][i][1](parent, size, iter)
            except IndexError:
                pass
                # raise IndexError(RULES[t])

def decoratePoint(point):
    pass

# Replace points for GENERATIONS iterations
for iter in range(GENERATIONS):
    points = geo.points()[:]
    
    for point in points:
        replacePoint(point, hou.Vector3(point.attribValue("size")), iter)

# Make spires appear
points = geo.points()[:]
for point in points:
    spire.makeSpires(point)

# TODO classify buildings of different types
# for point in geo.points():
    # classify.classifyBuildings(point)

points = geo.points()[:]
for point in points:
    # do arch things
    pass

# Generate appropriate wall points
points = geo.points()[:]
for point in points:
    decorate.decorate(point)
geo.deletePoints(points)

for point in geo.points():
    t = point.attribValue("type")
    if len(t):
        POINT_GROUPS[t].add(point)