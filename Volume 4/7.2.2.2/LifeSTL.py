from stl import mesh
import math
import numpy
import os
from Life import Life, LifeTiling, LifeState
import numpy as np
from matplotlib import pyplot
from mpl_toolkits import mplot3d

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
        self.meshes = []
        for i, tiling in enumerate(self.lifeGame.game.tilings):
            if i != 4:
                # continue
                pass
            meshLayer = self.convertTilingToStl(tiling)
            meshLayer.translate(np.array([0, 0, i]))
            self.meshes.append(meshLayer)




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


    @staticmethod
    def example():
        # Create 3 faces of a cube
        data = numpy.zeros(6, dtype=mesh.Mesh.dtype)

        # Top of the cube
        data['vectors'][0] = numpy.array([[0, 1, 1],
                                          [1, 0, 1],
                                          [0, 0, 1]])
        data['vectors'][1] = numpy.array([[1, 0, 1],
                                          [0, 1, 1],
                                          [1, 1, 1]])
        # Front face
        data['vectors'][2] = numpy.array([[1, 0, 0],
                                          [1, 0, 1],
                                          [1, 1, 0]])
        data['vectors'][3] = numpy.array([[1, 1, 1],
                                          [1, 0, 1],
                                          [1, 1, 0]])
        # Left face
        data['vectors'][4] = numpy.array([[0, 0, 0],
                                          [1, 0, 0],
                                          [1, 0, 1]])
        data['vectors'][5] = numpy.array([[0, 0, 0],
                                          [0, 0, 1],
                                          [1, 0, 1]])

        # Since the cube faces are from 0 to 1 we can move it to the middle by
        # substracting .5
        data['vectors'] -= .5

        # Generate 4 different meshes so we can rotate them later
        meshes = [mesh.Mesh(data.copy()) for _ in range(4)]

        # Rotate 90 degrees over the Y axis
        meshes[0].rotate([0.0, 0.5, 0.0], math.radians(90))

        # Translate 2 points over the X axis
        meshes[1].x += 2

        # Rotate 90 degrees over the X axis
        meshes[2].rotate([0.5, 0.0, 0.0], math.radians(90))
        # Translate 2 points over the X and Y points
        meshes[2].x += 2
        meshes[2].y += 2

        # Rotate 90 degrees over the X and Y axis
        meshes[3].rotate([0.5, 0.0, 0.0], math.radians(90))
        meshes[3].rotate([0.0, 0.5, 0.0], math.radians(90))
        # Translate 2 points over the Y axis
        meshes[3].y += 2



        # Create a new plot
        figure = pyplot.figure()
        axes = mplot3d.Axes3D(figure)

        # Render the cube faces
        for m in meshes:
            axes.add_collection3d(mplot3d.art3d.Poly3DCollection(m.vectors))

        # Auto scale to the mesh size
        scale = numpy.concatenate([m.points for m in meshes]).flatten(-1)
        axes.auto_scale_xyz(scale, scale, scale)

        # Show the plot to the screen
        pyplot.show()

if __name__ == '__main__':
    lg = Life()
    lg.readSolution('GabeIn6/solution4.bin')
    LifeSTL(lg, saveDir='GabeMeshes', render=False)
