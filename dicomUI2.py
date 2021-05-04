# -*- coding: utf-8 -*-

import sys
import cv2
import numpy as np
import imutils
import os
import pydicom
import json
import matplotlib.pyplot as plt

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QDialog
from PyQt5.uic import loadUi
from PyQt5.QtGui import QImage
from PyQt5.QtCore import QTimer

from datetime import date
##from collections import defaultdict

##dicomRoiCollection = defaultdict(dict) #tempRoicollection variable
##ROICollection = defaultdict(dict)  #collection to be saved to JSON

dicomRoiCollection = {} #tempRoicollection variable
ROICollection = {}  #collection to be saved to JSON

roiIndex = 1 # changed from -1 -> 1
datasetUser = ''

tempFFC = {}


class dicomeViewer(QDialog):
    def __init__(self):
        super(dicomeViewer,self).__init__()
        loadUi('dicomViewer.ui',self)

        self.laodBtn.clicked.connect(self.loadImage)
        self.prevBtn.clicked.connect(self.PrevImage)
        self.nextBtn.clicked.connect(self.NextImage)
        self.roiBtn.clicked.connect(self.roi_selection)
        self.zmIPBtn.clicked.connect(self.zoomIP)
        self.zmOPBtn.clicked.connect(self.zoomOP)

        self.brightSlid.valueChanged['int'].connect (self.brightness_value)
        self.contrastSlid.valueChanged['int'].connect (self.blur_value)
        
        cwdlst = []
        cwdlst = os.getcwd().split ('\\')
        self.cwd = '/'.join(cwdlst)
        print (self.cwd)
        self.dbFile = os.listdir(self.cwd + "/dataset/")
        print (self.dbFile)
        for name in self.dbFile:
            self.uName.addItem (name)

        print (self.uName.currentText())

        self.currentUser = ""
        self.currentPath = ""
        self.userFldrLst = []
        self.dcmFileLoc = None
        self.roiJsonLoc = None

        self.dcmIPFileName = None
        self.dcmOPFileName = None
        self.roiJsonFile = None

        self.loadedImgID = 1
        self.loadedImgID_temp = 1
        self.imageCount = 0

        self.scale = 1
        self.dcmFilesize = 0

        self.brightness_value_now = 256
        self.blur_value_now = 128

    def loadImage(self):
        self.currentUser = str (self.uName.currentText())
        self.currentPath = str (self.cwd + "/dataset/") + str (self.currentUser) + "/"
        self.userFldrLst = os.listdir(self.currentPath)

        self.dcmFileLoc = self.currentPath + str (self.userFldrLst [0]) + "/"
        self.roiJsonLoc = self.currentPath + str (self.userFldrLst [1]) + "/"
        self.roiJsonFile = self.roiJsonLoc + str (os.listdir (self.roiJsonLoc)[0])

        self.imageCount = len (os.listdir (self.dcmFileLoc + str (os.listdir (self.dcmFileLoc)[0]) + "/"))
        print (self.roiJsonFile, os.listdir (self.roiJsonLoc), str (self.imageCount))

        self.dcmIPFileName = self.dcmFileLoc + str (os.listdir (self.dcmFileLoc)[0]) + "/" + str (self.loadedImgID) + ".dcm"
        self.dcmOPFileName = self.dcmFileLoc + str (os.listdir (self.dcmFileLoc)[1]) + "/" + str (self.loadedImgID) + ".dcm"

        ds = pydicom.dcmread (self.dcmIPFileName)
        sos = str (ds.SOPClassUID) + "\n" + str (ds.SOPClassUID.name)

        pat_name = ds.PatientName
        pNamedat = pat_name.family_name + ", " + pat_name.given_name

        pIDdat = str (ds.PatientID)
        modality = str (ds.Modality)
        studyDate = str (ds.StudyDate)
        imgSize = str (ds.Rows) + " x " + str (ds.Columns)
        pxlSpacing = str (ds.PixelSpacing)
        sliceLoc = str (ds.get('SliceLocation', '(missing)'))
        stationNm = str (ds.get('StationName', '(missing)'))
        studyDis = str (ds.get('StudyDescription', '(missing)'))
        manufacturer = str (ds.Manufacturer)
        inistituteNam = str (ds.get('InstitutionName', '(missing)'))

        self.sosClassDat.setText(sos)
        self.pNameDat.setText(pNamedat)
        self.pIDDat.setText(pIDdat)
        self.modalityDat.setText(modality)
        self.stdyDateDat.setText(studyDate)
        self.imgSizDat.setText(imgSize)
        self.pxlSpaceDat.setText(pxlSpacing)
        self.slicingLocDat.setText(sliceLoc)
        self.stnNameDat.setText(stationNm)
        self.stdyDiscDat.setText(studyDis)
        self.mnfDat.setText(manufacturer)
        self.instNameDat.setText(inistituteNam)
        
        self.setPhoto(self.dcmIPFileName, self.dcmOPFileName)

    def PrevImage(self):
        self.loadedImgID_temp = self.loadedImgID - 1
        
        if self.loadedImgID_temp < 1:
            self.loadedImgID_temp = self.imageCount

        self.loadedImgID = self.loadedImgID_temp
        print (self.loadedImgID)

        self.dcmIPFileName = self.dcmFileLoc + str (os.listdir (self.dcmFileLoc)[0]) + "/" + str (self.loadedImgID) + ".dcm"
        self.dcmOPFileName = self.dcmFileLoc + str (os.listdir (self.dcmFileLoc)[1]) + "/" + str (self.loadedImgID) + ".dcm"

        self.setPhoto(self.dcmIPFileName, self.dcmOPFileName)

    def NextImage(self):
        self.loadedImgID_temp = self.loadedImgID + 1

        if self.loadedImgID_temp > self.imageCount:
            self.loadedImgID_temp = 1

        self.loadedImgID = self.loadedImgID_temp
        print (self.loadedImgID)

        self.dcmIPFileName = self.dcmFileLoc + str (os.listdir (self.dcmFileLoc)[0]) + "/" + str (self.loadedImgID) + ".dcm"
        self.dcmOPFileName = self.dcmFileLoc + str (os.listdir (self.dcmFileLoc)[1]) + "/" + str (self.loadedImgID) + ".dcm"

        self.setPhoto(self.dcmIPFileName, self.dcmOPFileName)

    def zoomIP(self):
        self.dcmIPFileName = self.dcmFileLoc + str (os.listdir (self.dcmFileLoc)[0]) + "/" + str (self.loadedImgID) + ".dcm"
        
        ip = pydicom.dcmread (self.dcmIPFileName).pixel_array
        plt.imshow(ip, cmap=plt.cm.bone)
        plt.show()

    def zoomOP(self):
        self.dcmOPFileName = self.dcmFileLoc + str (os.listdir (self.dcmFileLoc)[1]) + "/" + str (self.loadedImgID) + ".dcm"

        op = pydicom.dcmread (self.dcmOPFileName).pixel_array
        plt.imshow(op, cmap=plt.cm.bone)
        plt.show()

    def meanFFCGenerator(self, tempRoi, index):
        today = date.today()
        today = today.strftime("%d/%m/%Y")
        tempRoiMean = 0

        try:
            tempFFC = tempRoi[1]["roiMatrix"]       # changed from 0 -> 1
        except KeyError:
            print("error")

        for i in range(index):
            try:
                tempRoiMean += tempRoi[i+1]["roiMean"] # changed from i -> i + 1
                if(index > i+2):
                    tempFFC = np.add(tempFFC, tempRoi[i+2])
            except KeyError:
                print("error")
                
        if(index != 0):
            tempRoiMean = tempRoiMean / index

        tempFFC = tempFFC.tolist() # changed from tempFFC.tolist() -> list (tempFFC)
        print (type (tempFFC))

        ROICollection[today] = {
            "ffc": tempFFC,
            "ffcMean": tempRoiMean
        }

        url = self.roiJsonLoc + self.currentUser + '_ffc.json'
        print (url)
        
        with open(url, 'a') as jsonFile:
            json.dump(ROICollection, jsonFile)
##            try:
##                data = json.load(jsonFile)
##                data.update(ROICollection)
##                jsonFile.seek(0)
##                json.dump(ROICollection, jsonFile)
##                print ("ok")
##            except:
##                print ("Error")
##                json.dump({}, jsonFile)
            
    def roi_selection(self):
        roiIPdcmFile = self.dcmIPFileName
        roiOPdcmFile = self.dcmOPFileName

        iproiDCM = pydicom.dcmread (roiIPdcmFile)
        oproiDCM = pydicom.dcmread (roiOPdcmFile)

        ipAryroi = iproiDCM.pixel_array
        print(ipAryroi.shape)
        scalipAry = cv2.convertScaleAbs(ipAryroi)

        opAryroi = oproiDCM.pixel_array
        scalopAry = cv2.convertScaleAbs(opAryroi)
        
        r = cv2.selectROI (scalipAry)

        dcmCropIP = ipAryroi [int(r[1]):int(r[1]+r[3]), int(r[0]):int(r[0]+r[2])]
        dcmCropOP = opAryroi [int(r[1]):int(r[1]+r[3]), int(r[0]):int(r[0]+r[2])]
        print (len (dcmCropIP), len (dcmCropOP))
        diff = np.sqrt(dcmCropIP ** 2 - dcmCropOP ** 2)
        diff=np.round(diff,2)
        
        print (len (diff))
        strROI = ""
        tempROI = ""
        for x in dcmCropIP:
            strROI = strROI + str (x) + "\n"
        tempROI = strROI
        print ("IN roi ok")
        f = open("roiIN.txt", "w")
        f.write(tempROI)
        f.close()

        strROI = ""
        tempROI = ""
        for x in dcmCropOP:
            strROI = strROI + str (x) + "\n"
        tempROI = strROI
        print ("OUT roi ok")
        f = open("roiOUT.txt", "w")
        f.write(tempROI)
        f.close()

        strROI = ""
        tempROI = ""
        for x in diff:
            strROI = strROI + str (x) + "\n"
        tempROI = strROI
        print ("dif roi ok")
        f = open("roiDIF.txt", "w")
        f.write(tempROI)
        f.close()
        
        ffc = ((diff) / (2 * dcmCropIP))*100
        ffcMean = np.mean(ffc)
        print (roiIndex)
        dicomRoiCollection[roiIndex] = {
            "roiMatrix": ffc,
            "roiMean":ffcMean 
        }

        cv2.imshow("FF",ffc)

        if(roiIndex == 1):
            self.meanFFCGenerator(dicomRoiCollection, roiIndex)
        print("fatfraction Mean: ", ffcMean)
    
        #url = "ffcData.json"
        #json.dump(ROICollection, open(url, "w"))

    def brightness_value (self,value):
        self.brightness_value_now = value * 2
        self.update ()
		
    def blur_value (self, value):
        self.blur_value_now = value * 2
        self.update ()
		
    def update (self):
        brightness = int((self.brightness_value_now - 0) * (255 - (-255)) / (510 - 0) + (-255))
        contrast = int((self.blur_value_now - 0) * (127 - (-127)) / (254 - 0) + (-127))

        pydicom.dcmread (self.dcmIPFileName).pixel_array
        pydicom.dcmread (self.dcmOPFileName).pixel_array

        ip_ = cv2.convertScaleAbs(pydicom.dcmread (self.dcmIPFileName).pixel_array)
        op_ = cv2.convertScaleAbs(pydicom.dcmread (self.dcmOPFileName).pixel_array)

        if brightness != 0:
            if brightness > 0:
                shadow = brightness
                max = 255
            else:
                shadow = 0
                max = 255 + brightness
            al_pha = (max - shadow) / 255
            ga_mma = shadow

            cal_ip = cv2.addWeighted(ip_, al_pha, ip_, 0, ga_mma)
            cal_op = cv2.addWeighted(op_, al_pha, op_, 0, ga_mma)
        else:
            cal_ip = ip_
            cal_op = op_

        if contrast != 0:
            Alpha = float(131 * (contrast + 127)) / (127 * (131 - contrast))
            Gamma = 127 * (1 - Alpha)

            cal_ip = cv2.addWeighted(cal_ip, Alpha, cal_ip, 0, Gamma)
            cal_op = cv2.addWeighted(cal_op, Alpha, cal_op, 0, Gamma)

        ip_Image = QImage(cal_ip, cal_ip.shape[1], cal_ip.shape[0], cal_ip.strides[0], QImage.Format_Indexed8).rgbSwapped()
        op_Image = QImage(cal_op, cal_op.shape[1], cal_op.shape[0], cal_op.strides[0], QImage.Format_Indexed8).rgbSwapped()
        
        self.ipView.setPixmap (QtGui.QPixmap.fromImage (ip_Image))
        self.ipView.setScaledContents (True)
        self.opView.setPixmap (QtGui.QPixmap.fromImage (op_Image))
        self.opView.setScaledContents (True)
        
    def setPhoto (self, dcmIPF, dcmOPF):
        ipDCM = pydicom.dcmread (dcmIPF)
        opDCM = pydicom.dcmread (dcmOPF)

        ipAry = ipDCM.pixel_array
        scalipAry = cv2.convertScaleAbs(ipAry)

        opAry = opDCM.pixel_array
        scalopAry = cv2.convertScaleAbs(opAry)

        ipoutImage = QImage(scalipAry, scalipAry.shape[1], scalipAry.shape[0], scalipAry.strides[0], QImage.Format_Indexed8).rgbSwapped()
        opoutImage = QImage(scalopAry, scalopAry.shape[1], scalopAry.shape[0], scalopAry.strides[0], QImage.Format_Indexed8).rgbSwapped()

        self.dcmFilesize = QtGui.QPixmap.fromImage (ipoutImage).size()
        
        self.ipView.setPixmap (QtGui.QPixmap.fromImage (ipoutImage))
        self.ipView.setScaledContents (True)
        self.opView.setPixmap (QtGui.QPixmap.fromImage (opoutImage))
        self.opView.setScaledContents (True)

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    
    window = dicomeViewer()
    window.setWindowTitle('Dicom Viewer')
    window.show()
    sys.exit(app.exec_())
