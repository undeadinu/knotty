from numpy import *
from algebra import *

class BoundingBox(object):
    def __init__(self):
        self.valid = False
        self.bounding_min = array([0.0,0.0,0.0])
        self.bounding_max = array([0.0,0.0,0.0])

    def intersect(self, ray):
        #special case the z intersect used in voxelization
        #for faster intersection calcs
        if (ray.direction[0] == 0 and 
            ray.direction[1] == 0 and 
            ray.direction[2] == 1):
            return self.z_intersect(ray)
        elif (ray.direction[0] == 0 and
              ray.direction[1] == 1 and
              ray.direction[2] == 0):
            return self.y_intersect(ray)
        elif (ray.direction[0] == 1 and
              ray.direction[1] == 0 and
              ray.direction[2] == 0):
            return self.x_intersect(ray)
        else:
            return self.normal_intersect(ray)

    def z_intersect(self,ray):
        #ignore ray direction, just consider if ray is shooting in z
        for i in xrange(0,2):
            if (ray.start[i] > self.bounding_max[i] or 
                    ray.start[i] < self.bounding_min[i]):
                return False
        #print "intersect"
        return True

    def y_intersect(self,ray):
        #ignore ray direction, just consider if ray is shooting in y
        for i in xrange(0,3,2):
            if (ray.start[i] > self.bounding_max[i] or 
                    ray.start[i] < self.bounding_min[i]):
                return False
        #print "intersect"
        return True

    def x_intersect(self,ray):
        #ignore ray direction, just consider if ray is shooting in x
        for i in xrange(1,3):
            if (ray.start[i] > self.bounding_max[i] or 
                    ray.start[i] < self.bounding_min[i]):
                return False
        #print "intersect"
        return True



    def normal_intersect(self, ray):
        t_min = array([0.0,0.0,0.0])
        t_max = array([0.0,0.0,0.0])
        a = array([0.0,0.0,0.0])
        e = ray.start
        for i in xrange(0,3):
            a[i] = 1.0/ray.direction[i]
            if(a[i] >= 0):
                t_min[i] = a[i] * (self.bounding_min[i] - e[i])
                t_max[i] = a[i] * (self.bounding_max[i] - e[i])
            else:
                t_min[i] = a[i] * (self.bounding_max[i] - e[i])
                t_max[i] = a[i] * (self.bounding_min[i] - e[i])
        if (t_min[0] > t_max[1] or t_min[0] > t_max[2] or
            t_min[1] > t_max[0] or t_min[1] > t_max[2] or
            t_min[2] > t_max[0] or t_min[2] > t_max[1]):
            return False
        return True

    def addPoint(self,new_point):
        if self.valid:
            for i in xrange(0,3):
                self.bounding_max[i] = max(self.bounding_max[i], new_point[i])
                self.bounding_min[i] = min(self.bounding_min[i], new_point[i])
        else:
            self.bounding_min = array(new_point)
            self.bounding_max = array(new_point)
            self.valid = True

    def addPoints(self,new_points):
        for point in new_points:
            self.addPoints(point)

    def extend(self,new_bb):
        new_max = array(new_bb.bounding_max)
        new_min = array(new_bb.bounding_min)
        if not self.valid:
            self.bouning_max = new_max
            self.bounding_min = new_min
            self.valid = True
        for i in xrange(0,3):
            self.bounding_max[i] = max(self.bounding_max[i], new_max[i])
            self.bounding_min[i] = min(self.bounding_min[i], new_min[i])

class AABBNode(object):
    def __init__(self):
        self.bb = BoundingBox()
        self.primitives = []
        self.children = []
    def addChild(self, new_child):
        self.children.append(new_child)
    def addPrimitive(self, new_primitive):
        self.primitives.append(new_primitive)
    def isLeaf(self):
        return len(self.children) == 0
    def calculateBoundingSides(self):
        if self.isLeaf():
            for primitive in self.primitives:
                new_bb = primitive.worldBoundingBox()
                self.bb.extend(new_bb)
        else:
            for child in self.children:
                self.bb.extend(child.calculateBoundingSides())
        return self.bb
    def relevantPrimitives(self, ray):
        if self.bb.intersect(ray):
            if self.isLeaf():
                return self.primitives
            else:
                relevant = []
                for child in self.children:
                    relevant.extend(child.relevantPrimitives(ray))
                return relevant
        return []

def createAABBTree(prims, depth=0):
    new_node = AABBNode()
    #hardcoded depth for now... just trying to keep it reasonable
    if depth > 1024 or len(prims) <= 1:
        for prim in prims:
            new_node.addPrimitive(prim)
    else:
        div_axis = depth%3
        median_axis = 0 
        #i would use quickselect, but python only has sort implemented
        sorted_axis = sorted(prims, key=lambda p: p.center()[div_axis])

        bucket_a = sorted_axis[:len(sorted_axis)/2]
        bucket_b = sorted_axis[len(sorted_axis)/2:]

        new_node.addChild(createAABBTree(bucket_a,depth+1))
        new_node.addChild(createAABBTree(bucket_b,depth+1))
    return new_node




                

