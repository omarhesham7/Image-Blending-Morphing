# Import PyQt5 classes
import sys
from PyQt5 import QtCore, QtGui
from PyQt5.QtWidgets import QMainWindow, QApplication, QFileDialog, QGraphicsScene, QGraphicsView
from PyQt5.QtGui import *
from PyQt5.QtCore import *

from Lab12.MorphingGUI import *
from Lab12.Morphing import *
from PIL.ImageQt import ImageQt
class MorphingApp(QMainWindow, Ui_MainWindow):

    def __init__(self, parent=None):
        super(MorphingApp, self).__init__(parent)
        self.setupUi(self)
        self.horizontalSlider.setDisabled(True)
        self.textEditCurrentAlphaValue.setText('0.0')
        self.textEditCurrentAlphaValue.setDisabled(True)
        self.pushButtonBlend.setDisabled(True)
        self.checkBoxShowTriangles.setDisabled(True)

        self.pushButtonStartingImage.setEnabled(True)
        self.pushButtonEndingImage.setEnabled(True)

        self.alpha = 0.0
        self.deleted = 0
        self.drewPoints = False
        self.leftImageFlag = 0
        self.rightImageFlag = 0
        self.AddedToLeftImage = 0
        self.AddedToRightImage = 1
        self.confirmed = 0
        self.persistFlag = ''
        self.leftPointColor = ''
        self.rightPointColor = ''
        self.triangleColor = ''
        self.pushButtonStartingImage.clicked.connect(self.loadStartingImage)
        self.pushButtonEndingImage.clicked.connect(self.loadEndingImage)
        self.horizontalSlider.valueChanged.connect(self.updateAlphaInBox)
        self.checkBoxShowTriangles.stateChanged.connect(self.showTriangles)
        self.pushButtonBlend.clicked.connect(self.blend)
        self.mousePressEvent = self.confirmPoints

        self.leftPointFilePath = ''
        self.rightPointFilePath = ''
        self.leftCoord = ''
        self.rightCoord = ''
        self.directoryName = ''
        self.startingImageCoords = np.array([])
        self.endingImageCoords = np.array([])
        self.startingCoords = np.array([])
        self.endingCoords = np.array([])
        self.addedPointsLeft = []
        self.addedPointsRight = []
        self.addedPointsLeftUpdated = []
        self.addedPointsRightUpdated = []
        self.addedCoordinatesLeft = []
        self.addedCoordinatesRight = []
        #self.startImageScene = QGraphicsScene()
        #self.endImageScene = QGraphicsScene()
        #self.startView = QGraphicsView(self.startImageScene)
        #self.endView = QGraphicsView(self.endImageScene)



    def loadStartingImage(self):
        filePath, _ = QFileDialog.getOpenFileNames(self, caption='Load Starting Image ...', filter="Images (*.png *.jpg)")
        if not filePath:
            return
        self.loadStartingImageFromFile(filePath)

    # https://stackoverflow.com/questions/8766584/displayin-an-image-in-a-qgraphicsscene
    def loadStartingImageFromFile(self, filePath):
        self.leftPointFilePath = ''
        self.getStartingCoordinates(filePath)
        self.startingImage = filePath[0]
        self.leftImage = np.asarray(imageio.imread(self.startingImage), dtype=np.uint8)
        pixMap = QPixmap(filePath[0])
        selfStartImageScene = QGraphicsScene()
        selfStartImageScene.addPixmap(pixMap)
        self.graphicsViewStartingImage.setScene(selfStartImageScene)
        self.graphicsViewStartingImage.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.graphicsViewStartingImage.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.graphicsViewStartingImage.fitInView(selfStartImageScene.sceneRect(), Qt.KeepAspectRatio)
        self.graphicsViewStartingImage.show()
        self.startImageScene = selfStartImageScene
        self.leftImageFlag = 1
        self.verifyImages()




    def loadEndingImage(self):
        filePath, _ = QFileDialog.getOpenFileNames(self, caption='Load Ending Image ...', filter="Images (*.png *.jpg)")
        if not filePath:
            return
        self.loadEndingImageFromFile(filePath)

    def loadEndingImageFromFile(self, filePath):
        self.rightPointFilePath = ''
        self.getEndingCoordinates(filePath)
        self.endingImage = filePath[0]
        self.rightImage = np.asarray(imageio.imread(self.endingImage), dtype=np.uint8)
        pixMap = QPixmap(filePath[0])
        selfEndImageScene = QGraphicsScene()
        selfEndImageScene.addPixmap(pixMap)
        self.graphicsViewEndingImage.setScene(selfEndImageScene)
        self.graphicsViewEndingImage.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.graphicsViewEndingImage.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.graphicsViewEndingImage.fitInView(selfEndImageScene.sceneRect(), Qt.KeepAspectRatio)
        self.graphicsViewEndingImage.show()
        self.endImageScene = selfEndImageScene
        self.rightImageFlag = 1
        self.verifyImages()


    def getStartingCoordinates(self, filePath):
        DirectoryName = os.path.dirname(filePath[0])
        self.directoryName = DirectoryName
        FilesinDirectory = os.listdir(DirectoryName)
        basename = os.path.basename(filePath[0])
        filename = os.path.splitext(basename)[0]
        extension = os.path.splitext(basename)[1]
        for file in FilesinDirectory:
            if file == filename + extension+ '.txt':
                self.leftPointFilePath = os.path.abspath(DirectoryName + '/' + file)
                self.startingCoords = np.loadtxt(self.leftPointFilePath)



    def getEndingCoordinates(self, filePath):
        DirectoryName = os.path.dirname(filePath[0])
        FilesinDirectory = os.listdir(DirectoryName)
        basename = os.path.basename(filePath[0])
        filename = os.path.splitext(basename)[0]
        extension = os.path.splitext(basename)[1]
        for file in FilesinDirectory:
            if file == filename + extension+ '.txt':
                self.rightPointFilePath = os.path.abspath(DirectoryName + '/' + file)
                self.endingCoords = np.loadtxt(self.rightPointFilePath)

    def verifyImages(self):
        if self.leftImageFlag + self.rightImageFlag == 2:
            self.horizontalSlider.setEnabled(True)
            self.textEditCurrentAlphaValue.setText('0.0')
            self.textEditCurrentAlphaValue.setEnabled(True)
            self.pushButtonBlend.setEnabled(True)
            self.checkBoxShowTriangles.setEnabled(True)
            self.startImageScene.mousePressEvent = self.AddingPointsToStartImage
            self.endImageScene.mousePressEvent = self.AddingPointsToEndImage
            if self.startingCoords.shape[0] >= 3 and self.endingCoords.shape[0] >= 3:
                self.drawStartImagePoints()
                self.drawEndImagePoints()

    def drawStartImagePoints(self):
        pointList = [QtCore.QPointF(x,y) for x,y in self.startingCoords]
        for point in pointList:
            self.startImageScene.addEllipse(point.x(), point.y(), 20, 20, QtGui.QPen(QtGui.QColor('red')), QtGui.QBrush(QtGui.QColor('red')))
        for point in self.addedPointsLeftUpdated:
            self.startImageScene.addEllipse(point[0], point[1], 20, 20, QtGui.QPen(QtGui.QColor('blue')), QtGui.QBrush(QtGui.QColor('blue')))
    def drawEndImagePoints(self):
        pointList = [QtCore.QPointF(x,y) for x,y in self.endingCoords]
        for point in pointList:
            self.endImageScene.addEllipse(point.x(), point.y(), 20, 20, QtGui.QPen(QtGui.QColor('red')), QtGui.QBrush(QtGui.QColor('red')))
        for point in self.addedPointsRightUpdated:
            self.endImageScene.addEllipse(point[0], point[1], 20, 20, QtGui.QPen(QtGui.QColor('blue')), QtGui.QBrush(QtGui.QColor('blue')))

    def showTriangles(self):
        if self.checkBoxShowTriangles.isChecked() and self.startingCoords.shape[0] >= 3 and self.endingCoords.shape[0] >= 3:
            self.leftTriangles, self.rightTriangles = loadTriangles(self.leftPointFilePath, self.rightPointFilePath)
            Triangle = QtGui.QPolygonF()
            leftTriangleList = []
            for triangle in self.leftTriangles:
                x1, y1 = triangle.vertices[0]
                x2, y2 = triangle.vertices[1]
                x3, y3 = triangle.vertices[2]
                Triangle.append(QtCore.QPointF(x1,y1))
                Triangle.append(QtCore.QPointF(x2, y2))
                Triangle.append(QtCore.QPointF(x3, y3))
                leftTriangleList.append(Triangle)
                Triangle = QtGui.QPolygonF()
            for triangle in leftTriangleList:
                if self.triangleColor == 'blue':
                    self.startImageScene.addPolygon(triangle, QtGui.QPen(QtGui.QColor('cyan')))
                else:
                    self.startImageScene.addPolygon(triangle, QtGui.QPen(QtGui.QColor('red')))

            Triangle = QtGui.QPolygonF()
            rightTriangleList = []
            for triangle in self.rightTriangles:
                x1, y1 = triangle.vertices[0]
                x2, y2 = triangle.vertices[1]
                x3, y3 = triangle.vertices[2]
                Triangle.append(QtCore.QPointF(x1,y1))
                Triangle.append(QtCore.QPointF(x2, y2))
                Triangle.append(QtCore.QPointF(x3, y3))
                rightTriangleList.append(Triangle)
                Triangle = QtGui.QPolygonF()
            for triangle in rightTriangleList:
                if self.triangleColor == 'blue':
                    self.endImageScene.addPolygon(triangle, QtGui.QPen(QtGui.QColor('cyan')))
                else:
                    self.endImageScene.addPolygon(triangle, QtGui.QPen(QtGui.QColor('red')))
        else:
            self.restoreImages()

    def restoreImages(self):
        self.startImageScene.clear()
        self.endImageScene.clear()
        pixMap = QPixmap(self.startingImage)
        self.startImageScene.addPixmap(pixMap)
        self.graphicsViewStartingImage.setScene(self.startImageScene)
        self.graphicsViewStartingImage.fitInView(self.startImageScene.sceneRect(), Qt.KeepAspectRatio)
        self.graphicsViewStartingImage.show()

        pixMap = QPixmap(self.endingImage)
        self.endImageScene.addPixmap(pixMap)
        self.graphicsViewEndingImage.setScene(self.endImageScene)
        self.graphicsViewEndingImage.fitInView(self.endImageScene.sceneRect(), Qt.KeepAspectRatio)
        self.graphicsViewEndingImage.show()
        if self.startingCoords.shape[0] >= 3 and self.endingCoords.shape[0] >= 3:  #added this check
            self.drawStartImagePoints()
            self.drawEndImagePoints()
        elif self.drewPoints:
            if len(self.addedPointsLeftUpdated) > 0:
                for point in self.addedPointsLeftUpdated:
                    self.startImageScene.addEllipse(point[0], point[1], 20, 20, QtGui.QPen(QtGui.QColor('blue')),
                                                    QtGui.QBrush(QtGui.QColor('blue')))

            if len(self.addedPointsRightUpdated) > 0:
                for point in self.addedPointsRightUpdated:
                    self.endImageScene.addEllipse(point[0], point[1], 20, 20, QtGui.QPen(QtGui.QColor('blue')),
                                                    QtGui.QBrush(QtGui.QColor('blue')))



    def updateAlphaInBox(self):
        self.alpha = self.horizontalSlider.value() / 100
        self.textEditCurrentAlphaValue.setText(str(self.alpha))


    def AddingPointsToStartImage(self, event):
        coords = event.scenePos()
        if self.persistFlag == 1 and self.drewPoints:
            if not (self.rectangleBoundsScene(coords.x(), coords.y()))  and (len(self.addedCoordinatesLeft) == len(self.addedCoordinatesRight)) and (self.AddedToRightImage == 1 or self.AddedToLeftImage == 1) and self.confirmed == 0:
                for point in self.addedPointsLeftUpdated:
                    self.startImageScene.addEllipse(point[0], point[1], 20, 20, QtGui.QPen(QtGui.QColor('blue')), QtGui.QBrush(QtGui.QColor('blue')))
                for point in self.addedPointsRightUpdated:
                    self.endImageScene.addEllipse(point[0], point[1], 20, 20, QtGui.QPen(QtGui.QColor('blue')), QtGui.QBrush(QtGui.QColor('blue')))

                self.showTriangles()

                with open(self.startingImage + '.txt', "a+") as sFile:
                    x, y = self.leftCoord
                    if self.startingCoords.size == 0:
                        newPoint = f"   {round(x,1)}   {round(y,1)}"
                    else:
                        newPoint = f"\n   {round(x,1)}   {round(y,1)}"
                    leftPoint = np.array([[round(x, 1), round(y, 1)]])
                    sFile.write(newPoint)

                if self.startingCoords.size == 0:
                    self.startingCoords = np.array(leftPoint)
                    self.leftPointFilePath = self.startingImage + '.txt'
                else:
                    tempArray = np.append(self.startingCoords, leftPoint, axis=0)
                    self.startingCoords = tempArray

                with open(self.endingImage + '.txt', "a+") as sFile:
                    x, y = self.rightCoord
                    if self.endingCoords.size == 0:
                        newPoint = f"   {round(x,1)}   {round(y,1)}"
                    else:
                        newPoint = f"\n   {round(x,1)}   {round(y,1)}"
                    rightPoint = np.array([[round(x, 1), round(y, 1)]])
                    sFile.write(newPoint)

                if self.endingCoords.size == 0:
                    self.endingCoords = np.array(rightPoint)
                    self.rightPointFilePath = self.endingImage + '.txt'
                else:
                    tempArray = np.append(self.endingCoords, rightPoint, axis=0)
                    self.endingCoords = tempArray
                self.triangleColor = 'blue'
                self.confirmed = 1
        if self.leftImageFlag + self.rightImageFlag == 2 and self.AddedToLeftImage == 0 and self.AddedToRightImage == 1:
            self.addedPointsLeft.append(self.startImageScene.addEllipse(coords.x(), coords.y(), 20, 20, QtGui.QPen(QtGui.QColor(0,255,0)), QtGui.QBrush(QtGui.QColor(0,255,0))))
            self.addedPointsLeftUpdated.append((round(coords.x(),1), round(coords.y(),1)))
            self.AddedToLeftImage = 1
            self.AddedToRightImage = 0
            self.confirmed = 0
            self.leftPointColor = 'green'
            self.deleted = 0
            newPoint = round(coords.x(), 1), round(coords.y(), 1)
            self.addedCoordinatesLeft.append(newPoint)
            self.leftCoord = newPoint
            self.drewPoints = True


    def AddingPointsToEndImage(self, event):
        coords = event.scenePos()
        if self.leftImageFlag + self.rightImageFlag == 2 and self.AddedToRightImage == 0 and self.AddedToLeftImage == 1:
            self.addedPointsRight.append(self.endImageScene.addEllipse(coords.x(), coords.y(), 20, 20, QtGui.QPen(QtGui.QColor(0, 255, 0)), QtGui.QBrush(QtGui.QColor(0, 255, 0))))
            self.addedPointsRightUpdated.append((round(coords.x(), 1), round(coords.y(), 1)))
            self.AddedToRightImage = 1
            self.AddedToLeftImage = 0
            self.rightPointColor = 'green'
            self.deleted = 0
            newPoint = round(coords.x(),1) , round(coords.y(),1)
            self.addedCoordinatesRight.append(newPoint)
            self.rightCoord = newPoint
            self.persistFlag = 1
            self.confirmed = 0
            self.drewPoints = True


    def keyPressEvent(self,event):
        if event.key() ==  QtCore.Qt.Key_Backspace and len(self.addedPointsLeftUpdated) > 0 and len(self.addedPointsLeft) != 0 and self.leftPointColor != 'blue' and len(self.addedCoordinatesLeft) > 0 and self.AddedToLeftImage == 1 and self.AddedToRightImage == 0 and self.deleted == 0:
            self.startImageScene.removeItem(self.addedPointsLeft[-1])
            self.AddedToLeftImage = 0
            self.AddedToRightImage = 1
            self.deleted = 1
            self.confirmed = 0
            self.drewPoints = False
            del self.addedCoordinatesLeft[-1]
            del self.addedPointsLeftUpdated[-1]
        elif event.key() ==  QtCore.Qt.Key_Backspace and len(self.addedPointsRightUpdated) > 0 and len(self.addedPointsRight) != 0 and self.rightPointColor != 'blue' and len(self.addedCoordinatesRight) > 0 and self.AddedToLeftImage == 0 and self.AddedToRightImage == 1 and self.deleted == 0:
            self.endImageScene.removeItem(self.addedPointsRight[-1])
            self.AddedToRightImage = 0
            self.AddedToLeftImage = 1
            self.deleted = 1
            self.confirmed = 0
            self.drewPoints = False
            del self.addedCoordinatesRight[-1]
            del self.addedPointsRightUpdated[-1]
            self.persistFlag = 0

    def confirmPoints(self, event):
        coords = event.pos()
        if self.rectangleBounds(coords.x(), coords.y()) and (len(self.addedCoordinatesLeft) == len(self.addedCoordinatesRight)) and (self.AddedToRightImage == 1 or self.AddedToLeftImage == 1) and self.confirmed == 0 and self.drewPoints:
            for point in self.addedPointsLeftUpdated:
                self.startImageScene.addEllipse(point[0], point[1], 20, 20, QtGui.QPen(QtGui.QColor('blue')),
                                                QtGui.QBrush(QtGui.QColor('blue')))
            for point in self.addedPointsRightUpdated:
                self.endImageScene.addEllipse(point[0], point[1], 20, 20, QtGui.QPen(QtGui.QColor('blue')),
                                                QtGui.QBrush(QtGui.QColor('blue')))

            self.showTriangles()

            with open(self.startingImage + '.txt', "a+") as sFile:
                x, y = self.leftCoord
                if self.startingCoords.size == 0:
                    newPoint = f"   {round(x,1)}   {round(y,1)}"
                else:
                    newPoint = f"\n   {round(x,1)}   {round(y,1)}"
                leftPoint = np.array([[round(x, 1), round(y, 1)]])
                sFile.write(newPoint)

            if self.startingCoords.size == 0:
                self.startingCoords = np.array(leftPoint)
                self.leftPointFilePath = self.startingImage + '.txt'
            else:
                tempArray = np.append(self.startingCoords, leftPoint, axis=0)
                self.startingCoords = tempArray

            with open(self.endingImage + '.txt', "a+") as sFile:
                x, y = self.rightCoord
                if self.endingCoords.size == 0:
                    newPoint = f"   {round(x,1)}   {round(y,1)}"
                else:
                    newPoint = f"\n   {round(x,1)}   {round(y,1)}"
                rightPoint = np.array([[round(x, 1), round(y, 1)]])
                sFile.write(newPoint)

            if self.endingCoords.size == 0:
                self.endingCoords = np.array(rightPoint)
                self.rightPointFilePath = self.endingImage + '.txt'
            else:
                tempArray = np.append(self.endingCoords, rightPoint, axis=0)
                self.endingCoords = tempArray

            self.confirmed = 1
            self.triangleColor = 'blue'
            self.leftPointColor = 'blue'
            self.rightPointColor = 'blue'
            self.drewPoints = True

    def blend(self):
        if os.path.exists(self.leftPointFilePath) and os.path.exists(self.rightPointFilePath) and self.startingCoords.shape[0] >= 3 and self.endingCoords.shape[0] >= 3:
            self.leftTriangles, self.rightTriangles = loadTriangles(self.leftPointFilePath, self.rightPointFilePath)
            morphedImage = Morpher(self.leftImage, self.leftTriangles, self.rightImage, self.rightTriangles)
            blendedImage = morphedImage.getImageAtAlpha(self.alpha)
            finalImage = Image.fromarray(blendedImage)
            finalImagePath = str(self.directoryName) + '/blended.png'
            finalImage.save(finalImagePath)
            pixMap = QPixmap(finalImagePath)
            selfBlendedImageScene = QGraphicsScene()
            selfBlendedImageScene.addPixmap(pixMap)
            self.graphicsViewBlendedImage.setScene(selfBlendedImageScene)
            self.graphicsViewBlendedImage.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
            self.graphicsViewBlendedImage.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
            self.graphicsViewBlendedImage.fitInView(selfBlendedImageScene.sceneRect(), Qt.KeepAspectRatio)
            self.graphicsViewBlendedImage.show()



    def rectangleBounds(self, x, y):
        firstBoxX1 = 10
        firstBoxY1 = 40
        firstBoxX2 = 351
        firstBoxY2 = 291

        secondBoxX1 = 450
        secondBoxY1 = 40
        secondBoxX2 = 791
        secondBoxY2 = 291

        if (((x < firstBoxX1 or x > firstBoxX2) or (y < firstBoxY1 or y > firstBoxY2)) and  ((x < secondBoxX1 or x > secondBoxX2) or (y < secondBoxY1 or y > secondBoxY2))):
            return True
        else:
            return False

    def rectangleBoundsScene(self, x, y):
        firstBoxX1 = 0
        firstBoxY1 = 0
        firstBoxX2 = self.leftImage.shape[1]
        firstBoxY2 = self.leftImage.shape[0]

        secondBoxX1 = 0
        secondBoxY1 = 0
        secondBoxX2 = self.rightImage.shape[1]
        secondBoxY2 = self.rightImage.shape[0]

        if (((x < firstBoxX1 or x > firstBoxX2) or (y < firstBoxY1 or y > firstBoxY2)) and  ((x < secondBoxX1 or x > secondBoxX2) or (y < secondBoxY1 or y > secondBoxY2))):
            return True
        else:
            return False

if __name__ == "__main__":
    currentApp = QApplication(sys.argv)
    currentForm = MorphingApp()

    currentForm.show()
    currentApp.exec_()