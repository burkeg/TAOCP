from stl import mesh
import math
import numpy
import os
import copy
from Life import Life, LifeTiling, LifeState
import numpy as np
from matplotlib import pyplot
from mpl_toolkits import mplot3d


class Normal:
    bottom = (0, 0, -1)
    front = (0, -1, 0)
    left = (-1, 0, 0)
    back = (0, 1, 0)
    right = (1, 0, 0)
    top = (0, 0, 1)


class Cube:
    def __init__(self, coord):
        # bottom, front, left, back, right, top
        self.faces = self.coordToFaces(coord)

    def coordToFaces(self, coord):
        assert isinstance(coord, tuple)
        assert len(coord) == 3
        x = coord[0]
        y = coord[1]
        z = coord[2]
        bflCorner = (x,   y,   z)
        bfrCorner = (x+1, y,   z)
        bblCorner = (x,   y+1, z)
        bbrCorner = (x+1, y+1, z)
        tflCorner = (x,   y,   z+1)
        tfrCorner = (x+1, y,   z+1)
        tblCorner = (x,   y+1, z+1)
        tbrCorner = (x+1, y+1, z+1)
        bottomFace = Square(bflCorner, bfrCorner, bblCorner, bbrCorner, Normal.bottom)
        frontFace = Square(bflCorner, bfrCorner, tflCorner, tfrCorner, Normal.front)
        leftFace = Square(bflCorner, bblCorner, tflCorner, tblCorner, Normal.left)
        backFace = Square(bblCorner, bbrCorner, tblCorner, tbrCorner, Normal.back)
        rightFace = Square(bfrCorner, bbrCorner, tfrCorner, tbrCorner, Normal.right)
        topFace = Square(tflCorner, tfrCorner, tblCorner, tbrCorner, Normal.top)
        return bottomFace, frontFace, leftFace, backFace, rightFace, topFace

    def toMesh(self):
        return mesh.Mesh(numpy.concatenate([x.toMesh() for x in self.faces]))


class Square:
    allSquares = set()
    def __init__(self, cornerA, cornerB, cornerC, cornerD, normal):
        self.cornerA = cornerA
        self.cornerB = cornerB
        self.cornerC = cornerC
        self.cornerD = cornerD
        self.normal = normal
        Square.allSquares.add(self.asTuple())

    def asTuple(self):
        return tuple(sorted([self.cornerA, self.cornerB, self.cornerC, self.cornerD]) + [self.normal])

    def toMesh(self):
        data = numpy.zeros(2, dtype=mesh.Mesh.dtype)
        tup = self.asTuple()
        data['vectors'][0] = numpy.array([tup[0],
                                          tup[1],
                                          tup[2]])
        data['vectors'][1] = numpy.array([tup[3],
                                          tup[1],
                                          tup[2]])
        # totally wrong probably, leaving this here so I can remember to check later
        # data['normals'][0] = numpy.array(self.normal)
        # data['normals'][1] = numpy.array(self.normal)
        return data

    @staticmethod
    def createMesh():
        def inverted(norm):
            return -norm[0], -norm[1], -norm[2]
        keptSquares = set()
        for square in Square.allSquares:
            oppositeSquare = (square[0], square[1], square[2], inverted(square[3]))
            if oppositeSquare not in Square.allSquares:
                keptSquares.add(square)
        meshLst = []
        for square in keptSquares:
            meshLst.append(square.toMesh())
        mesh.Mesh(meshLst)



class LifeSTL:
    def __init__(self, lifeGame, render=True, saveDir=None):
        assert isinstance(lifeGame, Life)
        self.lifeGame = lifeGame
        self.meshes = []
        self.convertLifeToStlSquare()
        if saveDir is not None:
            self.saveMeshes(saveDir)
        if render:
            self.renderMeshes()


    def saveMeshes(self, dir):
        try:
            os.mkdir(dir)
        except OSError:
            # print("Creation of the directory %s failed" % dir)
            pass

        for i, layer in enumerate(self.meshes):
            assert isinstance(layer, mesh.Mesh)
            layer.save(dir + '/layer' + str(i) + '.stl')
        combined = LifeSTL.combineMeshes(self.meshes)
        combined.save(dir + '/combined.stl')


    def convertLifeToStlSquare(self):
        for i, tiling in enumerate(self.lifeGame.game.tilings):
            assert isinstance(tiling, LifeTiling)
            cubesInLayer = []
            for row in range(tiling.height):
                for col in range(tiling.width):
                    if tiling[row][col].state == LifeState.ALIVE:
                        cubesInLayer.append(Cube((row, col, i)))

            layerMesh = LifeSTL.combineMeshes([x.toMesh() for x in cubesInLayer])
            self.meshes.append(layerMesh)


    def convertTilingToStl(self, tiling, includeBottom=True, includeTop=True):
        assert isinstance(tiling, LifeTiling)
        meshes = []
        for row in range(tiling.height):
            for col in range(tiling.width):
                if tiling[row][col].state == LifeState.ALIVE:
                    singleMesh = LifeSTL.cube(includeBottom, includeTop)
                    singleMesh.translate(np.array([row, col, 0]))
                    meshes.append(singleMesh)

        return LifeSTL.combineMeshes(meshes)

    @staticmethod
    def combineMeshes(meshes):
        return mesh.Mesh(numpy.concatenate([x.data.copy() for x in meshes]))

    @staticmethod
    def cube(includeBottom=True, includeTop=True):
        return mesh.Mesh(np.concatenate((LifeSTL.topFace() if includeTop else numpy.zeros(0, dtype=mesh.Mesh.dtype),
                                  LifeSTL.frontFace(),
                                  LifeSTL.rightFace(),
                                  LifeSTL.backFace(),
                                  LifeSTL.bottomFace() if includeBottom else numpy.zeros(0, dtype=mesh.Mesh.dtype),
                                  LifeSTL.leftFace())))

    @staticmethod
    def topFace():
        data = numpy.zeros(2, dtype=mesh.Mesh.dtype)

        # Top of the cube
        data['vectors'][0] = numpy.array([[0, 1, 1],
                                          [1, 0, 1],
                                          [0, 0, 1]])
        data['vectors'][1] = numpy.array([[1, 0, 1],
                                          [0, 1, 1],
                                          [1, 1, 1]])
        return data

    @staticmethod
    def frontFace():
        data = numpy.zeros(2, dtype=mesh.Mesh.dtype)

        # Front face
        data['vectors'][0] = numpy.array([[1, 0, 0],
                                          [1, 0, 1],
                                          [1, 1, 0]])
        data['vectors'][1] = numpy.array([[1, 1, 1],
                                          [1, 0, 1],
                                          [1, 1, 0]])
        return data

    @staticmethod
    def leftFace():
        data = numpy.zeros(2, dtype=mesh.Mesh.dtype)

        # Left face
        data['vectors'][0] = numpy.array([[0, 0, 0],
                                          [1, 0, 0],
                                          [1, 0, 1]])
        data['vectors'][1] = numpy.array([[0, 0, 0],
                                          [0, 0, 1],
                                          [1, 0, 1]])
        return data

    @staticmethod
    def rightFace():
        data = numpy.zeros(2, dtype=mesh.Mesh.dtype)

        # Right face
        data['vectors'][0] = numpy.array([[0, 1, 0],
                                          [1, 1, 0],
                                          [1, 1, 1]])
        data['vectors'][1] = numpy.array([[0, 1, 0],
                                          [0, 1, 1],
                                          [1, 1, 1]])
        return data

    @staticmethod
    def backFace():
        data = numpy.zeros(2, dtype=mesh.Mesh.dtype)

        # Front face
        data['vectors'][0] = numpy.array([[0, 0, 0],
                                          [0, 0, 1],
                                          [0, 1, 0]])
        data['vectors'][1] = numpy.array([[0, 1, 1],
                                          [0, 0, 1],
                                          [0, 1, 0]])
        return data

    @staticmethod
    def bottomFace():
        data = numpy.zeros(2, dtype=mesh.Mesh.dtype)

        # Top of the cube
        data['vectors'][0] = numpy.array([[0, 1, 0],
                                          [1, 0, 0],
                                          [0, 0, 0]])
        data['vectors'][1] = numpy.array([[1, 0, 0],
                                          [0, 1, 0],
                                          [1, 1, 0]])
        return data

    def renderMeshes(self):

        # Create a new plot
        figure = pyplot.figure()
        axes = mplot3d.Axes3D(figure)

        # Render the cube faces
        for m in self.meshes:
            axes.add_collection3d(mplot3d.art3d.Poly3DCollection(m.vectors))

        # Auto scale to the mesh size
        scale = numpy.concatenate([m.points for m in self.meshes]).flatten(-1)
        axes.auto_scale_xyz(scale, scale, scale)

        # Show the plot to the screen
        pyplot.show()

if __name__ == '__main__':
    lg = Life()
    lg.readSolution('GabeIn6/solution4.bin')
    LifeSTL(lg, saveDir='GabeMeshes', render=False)
