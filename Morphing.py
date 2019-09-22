#######################################################
#    Author:      Omar Abouhussein
#    email:       oabouhus@purdue.edu
#    ID:          ee364f28
#    Date:        04/02/2019
#######################################################
import os      # List of  module  import  statements
import sys     # Each  one on a line
from pprint import pprint as pp
from functools import total_ordering
import numpy as np
from scipy.spatial import Delaunay
from matplotlib.path import Path
import pylab as plt
from scipy import interpolate
from scipy import ndimage
import imageio
from PIL import ImageDraw, Image
import time
#import imageio_ffmpeg


def loadTriangles(leftPointFilePath:str, rightPointFilePath: str):
    leftArray = np.loadtxt(leftPointFilePath)
    DelaunayPts = Delaunay(leftArray)
    leftPointsArray = leftArray[DelaunayPts.simplices]
    leftTriangles = [Triangle(vertices) for vertices in leftPointsArray]

    rightArray = np.loadtxt(rightPointFilePath)
    rightPointsArray = rightArray[DelaunayPts.simplices]
    rightTriangles = [Triangle(vertices) for vertices in rightPointsArray]
    return leftTriangles, rightTriangles





class Triangle:
    def __init__(self, vertices):
        self._validateVertices(vertices)

    def _validateVertices(self, vertices):
        if not isinstance(vertices, np.ndarray):
            raise ValueError("vertices passed must be of type 'numoy array'. ")
        if vertices.dtype != np.float64:
            raise ValueError("vertices passed must be of type 'float64'. ")
        if vertices.shape != (3, 2):
            raise ValueError('Dimension mismatch.')
        self.vertices = vertices

    # https://stackoverflow.com/questions/51383969/how-to-draw-a-triangle-with-pil/51389954
    def getPoints(self):
        width, height = self.vertices.max(axis=0)
        img = Image.new('L', (int(width),int(height)))
        draw = ImageDraw.Draw(img)
        vertices = list(map(tuple, self.vertices))
        draw.polygon(vertices, fill='yellow')
        imgArray = np.array(img)
        imgArray = np.argwhere(imgArray)
        imgArray[:,[0,1]] = imgArray[:,[1, 0]]
        return imgArray

class Morpher:
    def __init__(self, leftImage, leftTriangles, rightImage, rightTriangles):
        self._validateTriangles(leftTriangles, rightTriangles)
        self._validateImages(leftImage, rightImage)


    def _validateTriangles(self, leftTriangles, rightTriangles):
        for leftTriangle, rightTriangle in zip(leftTriangles, rightTriangles):
            if not isinstance(leftTriangle, Triangle) or not isinstance(rightTriangle, Triangle):
                raise TypeError("leftTriangles and RightTriangles must both be of type 'Triangle' class. ")
        self.leftTriangles = leftTriangles
        self.rightTriangles = rightTriangles

    def _validateImages(self, leftImage, rightImage):
        if leftImage.shape != rightImage.shape or leftImage.dtype != np.uint8 or rightImage.dtype != np.uint8:
            raise TypeError("leftImage and rightImage must both be m x n numpy arrays of type 'uint8. ")
        self.leftImage = leftImage
        self.rightImage = rightImage

    def getImageAtAlpha(self, alpha):
        interTriangles = self._intermediateTriangles(self.leftTriangles, self.rightTriangles, alpha)
        leftAffineMatrices, invLeftAffineMatrices = self._affineMatrices(self.leftTriangles, interTriangles)
        rightAffineMatrices, invRightAffineMatrices = self._affineMatrices(self.rightTriangles, interTriangles)
        finalTransformed = self._getPixels(interTriangles, invLeftAffineMatrices, invRightAffineMatrices, self.leftImage, self.rightImage, alpha)
        return finalTransformed

    def _getPixels(self, interTriangles, leftInvAffineMatrices, rightInvAffineMatrices, leftImage, rightImage, alpha):
        transformedLeftImage = np.zeros(shape=leftImage.shape)
        transformedRightImage = np.zeros(shape=rightImage.shape)
        finalTransformed = np.zeros(shape=rightImage.shape, dtype=np.uint8)
        for index, interTriangle in enumerate(interTriangles):
            interPoints = interTriangle.getPoints()
            interPoints = np.asarray(interPoints.T)
            xCoords = interPoints[0]
            yCoords = interPoints[1]
            origxCoords = np.array(xCoords, np.int)
            origyCoords = np.array(yCoords, np.int)

            matrix = np.vstack((xCoords, yCoords, np.ones(xCoords.shape[0])))
            leftFinalMatrix = np.matmul(leftInvAffineMatrices[index], matrix)
            rightFinalMatrix = np.matmul(rightInvAffineMatrices[index], matrix)
            transformedLeftImage = ndimage.map_coordinates(self.leftImage, [leftFinalMatrix[1], leftFinalMatrix[0]], order=1)
            transformedRightImage = ndimage.map_coordinates(self.rightImage, [rightFinalMatrix[1], rightFinalMatrix[0]], order=1)
            finalTransformed[origyCoords, origxCoords] = ((1 - alpha) * transformedLeftImage) + (alpha * transformedRightImage)
        return finalTransformed

    def _intermediateTriangles(self, leftTriangles, rightTriangles,
                               alpha):  # (1-a)xleft + a(xright)  --> xnew  # (1-a)yleft + a(yright)  --> ynew
        intermediate = list()
        intermedTriList = list()
        for index, (leftTriPoint, rightTriPoint) in enumerate(zip(leftTriangles, rightTriangles)):
            newX1 = ((1 - alpha) * leftTriPoint.vertices[0][0]) + (alpha * rightTriPoint.vertices[0][0])
            newY1 = ((1 - alpha) * leftTriPoint.vertices[0][1]) + (alpha * rightTriPoint.vertices[0][1])
            newX2 = ((1 - alpha) * leftTriPoint.vertices[1][0]) + (alpha * rightTriPoint.vertices[1][0])
            newY2 = ((1 - alpha) * leftTriPoint.vertices[1][1]) + (alpha * rightTriPoint.vertices[1][1])
            newX3 = ((1 - alpha) * leftTriPoint.vertices[2][0]) + (alpha * rightTriPoint.vertices[2][0])
            newY3 = ((1 - alpha) * leftTriPoint.vertices[2][1]) + (alpha * rightTriPoint.vertices[2][1])
            intermediate = [(newX1, newY1), (newX2, newY2), (newX3, newY3)]
            intermedTriList.append(np.asarray(intermediate))
        intermedTriArray = np.asarray(intermedTriList, dtype=np.float64)
        interTriangles = [Triangle(vertices) for vertices in intermedTriArray]
        return interTriangles


    def _affineMatrices(self, initalTriangles, interTriangles):
        AffineMatricesList = []
        rightConcat = np.array([1, 0, 0, 0])
        leftConcat = np.array([0, 0, 0])
        bottomConcat = np.array([0, 0, 1])
        sixBysixMat, sixByoneMat = np.array([]), np.array([])
        sixBysixList, sixByOneList = list(), list()
        for index, (initialTriPoint, interTriPoint) in enumerate(zip(initalTriangles, interTriangles)):
            sixBysixList.append(np.hstack((initialTriPoint.vertices[0], rightConcat)))
            temp = np.hstack((leftConcat, initialTriPoint.vertices[0]))
            sixBysixList.append(np.hstack((temp, np.float64(1))))
            sixByOneList.extend(interTriPoint.vertices[0])

            sixBysixList.append(np.hstack((initialTriPoint.vertices[1], rightConcat)))
            temp = np.hstack((leftConcat, initialTriPoint.vertices[1]))
            sixBysixList.append(np.hstack((temp, np.float64(1))))
            sixByOneList.extend(interTriPoint.vertices[1])

            sixBysixList.append(np.hstack((initialTriPoint.vertices[2], rightConcat)))
            temp = np.hstack((leftConcat, initialTriPoint.vertices[2]))
            sixBysixList.append(np.hstack((temp, np.float64(1))))
            sixByOneList.extend(interTriPoint.vertices[2])

            sixByoneMat = np.vstack(sixByOneList)
            sixBysixMat = np.vstack(sixBysixList)
            sixBysixList, sixByOneList = [], []

            Htransform = (np.linalg.solve(sixBysixMat, sixByoneMat))
            AffineMatricesList.append(np.vstack((np.reshape(Htransform, (2, 3)), bottomConcat)))
        InvAffineMatricesList = [np.linalg.inv(transform) for transform in AffineMatricesList]
        AffineMatrices = np.asarray(AffineMatricesList)
        InvAffineMatrices = np.asarray(InvAffineMatricesList)
        return AffineMatrices, InvAffineMatrices

    # https://www.programcreek.com/python/example/104520/imageio.get_writer
    def saveVideo(self, targetFilePath, frameCount, frameRate, includeReversed):
        videowriter = imageio.get_writer(targetFilePath, fps=frameRate, macro_block_size = None)
        for i in range(frameCount):
            alpha = float(i/frameCount)
            videowriter.append_data(self.getImageAtAlpha(alpha))
        if includeReversed:
            for i in reversed(range(frameCount)):
                alpha = float(i / frameCount)
                videowriter.append_data(self.getImageAtAlpha(alpha))
        videowriter.close()


class ColorMorpher(Morpher):
    def __init__(self, leftImage, leftTriangles, rightImage, rightTriangles):
        super().__init__(leftImage, leftTriangles, rightImage, rightTriangles)

    def getImageAtAlpha(self, alpha):
        interTriangles = self._intermediateTriangles(self.leftTriangles, self.rightTriangles, alpha)
        leftAffineMatrices, invLeftAffineMatrices = self._affineMatrices(self.leftTriangles, interTriangles)
        rightAffineMatrices, invRightAffineMatrices = self._affineMatrices(self.rightTriangles, interTriangles)
        finalTransformed = self._getColorPixels(interTriangles, invLeftAffineMatrices, invRightAffineMatrices, self.leftImage, self.rightImage, alpha)
        return finalTransformed

    def _getColorPixels(self, interTriangles, leftInvAffineMatrices, rightInvAffineMatrices, leftImage, rightImage, alpha):
        transformedLeftImage = np.zeros(shape=leftImage.shape)
        transformedRightImage = np.zeros(shape=rightImage.shape)
        finalTransformed = np.zeros(shape=rightImage.shape, dtype=np.uint8)
        for index, interTriangle in enumerate(interTriangles):
            interPoints = interTriangle.getPoints()
            interPoints = np.asarray(interPoints.T)
            xCoords = interPoints[0]
            yCoords = interPoints[1]
            origxCoords = np.array(xCoords, np.int)
            origyCoords = np.array(yCoords, np.int)

            matrix = np.vstack((xCoords, yCoords, np.ones(xCoords.shape[0])))
            leftFinalMatrix = np.matmul(leftInvAffineMatrices[index], matrix)
            rightFinalMatrix = np.matmul(rightInvAffineMatrices[index], matrix)

            transformedLeftImage = ndimage.map_coordinates(self.leftImage[:, :, 0], [leftFinalMatrix[1], leftFinalMatrix[0]], order=1)
            transformedRightImage = ndimage.map_coordinates(self.rightImage[:, :, 0], [rightFinalMatrix[1], rightFinalMatrix[0]], order=1)
            finalTransformed[origyCoords, origxCoords, 0] = ((1 - alpha) * transformedLeftImage) + (alpha * transformedRightImage)

            transformedLeftImage = ndimage.map_coordinates(self.leftImage[:, :, 1], [leftFinalMatrix[1], leftFinalMatrix[0]], order=1)
            transformedRightImage = ndimage.map_coordinates(self.rightImage[:, :, 1], [rightFinalMatrix[1], rightFinalMatrix[0]], order=1)
            finalTransformed[origyCoords, origxCoords, 1] = ((1 - alpha) * transformedLeftImage) + (alpha * transformedRightImage)

            transformedLeftImage = ndimage.map_coordinates(self.leftImage[:, :, 2], [leftFinalMatrix[1], leftFinalMatrix[0]], order=1)
            transformedRightImage = ndimage.map_coordinates(self.rightImage[:, :, 2], [rightFinalMatrix[1], rightFinalMatrix[0]], order=1)
            finalTransformed[origyCoords, origxCoords, 2] = ((1 - alpha) * transformedLeftImage) + (alpha * transformedRightImage)
        return finalTransformed



if __name__ == "__main__":
    # CHANGE THE DATA PATH !!!!!!!!!!!!!!!
    leftImagePath = '/home/ecegridfs/a/ee364f28/Documents/labs-omarhesham7/Lab12/TestData/LeftGray.png' # CHANGE THE DATA PATH !!!!!!!!!!!!!!!
    rightImagePath = '/home/ecegridfs/a/ee364f28/Documents/labs-omarhesham7/Lab12/TestData/RightGray.png' # CHANGE THE DATA PATH !!!!!!!!!!!!!!!
    leftPointFilePath = '/home/ecegridfs/a/ee364f28/Documents/labs-omarhesham7/Lab12/TestData/LeftGray.png.txt' # CHANGE THE DATA PATH !!!!!!!!!!!!!!!
    rightPointFilePath = '/home/ecegridfs/a/ee364f28/Documents/labs-omarhesham7/Lab12/TestData/RightGray.png.txt' # CHANGE THE DATA PATH !!!!!!!!!!!!!!!
    # CHANGE THE DATA PATH !!!!!!!!!!!!!!!

    t1_start = time.perf_counter()
    t2_start = time.process_time()
    tstrt = time.time()
    leftImage = np.asarray(imageio.imread(leftImagePath), dtype=np.uint8)
    rightImage = np.asarray(imageio.imread(rightImagePath), dtype=np.uint8)

    leftTriangles, rightTriangles = loadTriangles(leftPointFilePath, rightPointFilePath)

    morp = Morpher(leftImage, leftTriangles, rightImage, rightTriangles)
    morp.getImageAtAlpha(0.5)
    #morp.saveVideo('/Users/Omar/labs-omarhesham7/Lab12/TestData/test.mp4', 20 ,5 , True)

    tend = time.time()
    t1_stop = time.perf_counter()
    t2_stop = time.process_time()
    print("time: ", tend - tstrt)
    print("Elapsed time:", ((t1_stop - t1_start)))
    print("CPU process time:",  ((t2_stop - t2_start)))
