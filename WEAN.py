# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'WEAN_30_9_3.ui'
#
# Created by: PyQt5 UI code generator 5.15.4
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.uic import loadUi
from PyQt5.QtCore import Qt
from pandas import read_csv
import numpy as np
from pyqtgraph.graphicsItems.ScatterPlotItem import Symbols
from pyqtgraph import PlotWidget
import pyqtgraph as pg
from scipy.optimize import curve_fit
import statistics
import os
import matplotlib.pyplot as plt
from PIL import Image
from sympy import Symbol, solve
from scipy import stats as stats
import time

class SplashScreen(QtWidgets.QSplashScreen):
    def __init__(self):
        super(QtWidgets.QSplashScreen,self).__init__()
        loadUi("splash.ui",self)
        self.setWindowFlag(Qt.FramelessWindowHint)
        pixmap = QtGui.QPixmap('image.png')
        self.setPixmap(pixmap)

    def progress(self):
        time.sleep(0.05)
        for i in range(100):
            QtWidgets.QApplication.processEvents()
            time.sleep(0.02)
            self.progressBar_splash.setValue(i+1)

class Ui_MainWindow(object):

    def message_box(self, type, title, msg, btn):
        """Generates message box
        """

        box = QtWidgets.QMessageBox()

        #Define type of message box 
        if str(type) == 'Warning':
            box.setIcon(QtWidgets.QMessageBox.Warning)
        elif str(type) == 'Information':
            box.setIcon(QtWidgets.QMessageBox.Information)

        box.setWindowTitle(str(title))
        box.setText(str(msg))
        box.setStandardButtons(QtWidgets.QMessageBox.Ok)
        buttonK = box.button(QtWidgets.QMessageBox.Ok)
        buttonK.setText(str(btn))
        box.exec()

    def find_file_path(self):
        self.filePath = QtWidgets.QFileDialog.getOpenFileName(None, 'Select the .csv File containing your Data', "./", '*.csv')
        self.lineEdit.setText(str(self.filePath[0]))
        self.pushButton1.setEnabled(True)
        self.pushButton_2.setEnabled(True)


    def find_folder_path(self):
        pathName = QtWidgets.QFileDialog.getExistingDirectory(None, "Select Directory to store Results")
        self.lineEdit_6.setText(str(pathName))
        self.pushButton_9.setEnabled(True)
        self.pushButton_10.setEnabled(True)

    def check_box_erase(self):

        self.checkBox_2.setChecked(False)
        self.checkBox_3.setChecked(False)
        self.checkBox_4.setChecked(False)

    def check_box2_erase(self):

        self.checkBox.setChecked(False)
        self.checkBox_3.setChecked(False)
        self.checkBox_4.setChecked(False)

    def check_box3_erase(self):

        self.checkBox_2.setChecked(False)
        self.checkBox.setChecked(False)
        self.checkBox_4.setChecked(False)

    def check_box4_erase(self):

        self.checkBox_2.setChecked(False)
        self.checkBox_3.setChecked(False)
        self.checkBox.setChecked(False)

    def test_delimiter(self):
        """Check for dataset delimiter
        """
        self.comboBox_3.clear()
        self.comboBox_4.clear()
        self.comboBox.clear()
        try:
            if self.checkBox.isChecked():
                self.delimiter = ' '
            elif self.checkBox_2.isChecked():
                self.delimiter = ','
            elif self.checkBox_3.isChecked():
                self.delimiter = '\t'
            elif self.checkBox_4.isChecked():
                self.delimiter = ';'
            
            self.df = read_csv(str(self.lineEdit.text()), sep=str(self.delimiter), header=0)

            
            if len(self.df.columns) > 1: #Check number of columns for correct delimiter

                column_headers = list(self.df)
                self.comboBox.addItems(column_headers)
                self.comboBox_3.addItems(column_headers)
                self.comboBox_4.addItems(column_headers)

            else:
                self.message_box('Warning', 'Warning', 
                'Please check that you chose the correct delimiter', 'Got it')


        except:
            self.message_box('Warning', 'Warning', 
                'Choose a delimiter and try again', 'Got it')


    def load_csv(self):
        """Perform calculations for all samples
        """

        self.comboBox_2.clear()
        self.id_column_name = str(self.comboBox.currentText())
        self.age_column_name = str(self.comboBox_3.currentText())
        self.nitrogen_column_name = str(self.comboBox_4.currentText())

        #Get list of individual names
        try:

            self.df = read_csv(str(self.lineEdit.text()), sep=str(self.delimiter), header=0,
                             usecols=[self.id_column_name, self.age_column_name, self.nitrogen_column_name])
            
            self.individual_names = []

            for word in self.df[self.id_column_name]:
                if word not in self.individual_names:
                    self.individual_names.append(word)
        except:
            self.message_box('Warning', 'Warning', 
                'Please check that:' + '\n' + '-You entered column names correctly'
                 + '\n' + '-Data at each column have the correct format', 'Got it')
        self.rss = []
        self.obs_wa = []
        self.obs_diff = []
        self.exp_diff = []
        self.mean_diff = []
        self.std = []
        self.weaned_age = []
        self.name_analyzed = []
        self.rsquared = []
        self.derivative = []

        self.fitted_parameters = {}
        
        for name in self.individual_names:
            
            try:
                observed_wa_nitrogen = self.pyWEAN(name)[1]
                observed_wa = self.pyWEAN(name)[0]

                

                a = self.df.loc[(self.df[self.id_column_name] == str(name))] #a is a subset of self.df

                

                age_array = np.array(a[self.age_column_name].tolist())
                nitrogen_array = np.array(a[self.nitrogen_column_name].tolist())

                #Fit to quadratic formula
                popt, pcov = curve_fit(self.func, age_array, nitrogen_array)
                self.fitted_parameters[name] = popt


                #Find R squared as a measure of fit
                modelPredictions = self.func(age_array, *popt)
                absError = modelPredictions - nitrogen_array
                Rsquared = round(1.0 - (np.var(absError) / np.var(nitrogen_array)), 2)
                self.rsquared.append(Rsquared)

                '''sr = np.sum(np.square(modelPredictions - nitrogen_array))
                rss = sr / (len(nitrogen_array) - 4 - 1)
                self.rss.append(rss)'''


                


                value_zero = self.X[0]
                value_max = self.X[1]
                all_dists = []
                all_age = []

                """Iterates over ages between first and last value of the dataset,
                find nitrogen value using the regression model and calculates distance
                of the point (age, fitted_nitrogen(age)) from line that passes through
                first and last measurement point  
                """
                while value_zero <= value_max:
                    point_list = (value_zero, self.func(value_zero, *popt))
                    point = np.asarray(point_list)

                    dist = np.cross(self.max_upper_point - self.max_lower_point,
                                self.max_lower_point - point) / np.linalg.norm(
                        self.max_upper_point - self.max_lower_point)
                    all_dists.append(-1 * dist)
                    all_age.append(value_zero)
                    value_zero += 0.1

                #Find maximum distance point
                max_value = max(all_dists)
                max_index = all_dists.index(max_value)

                x = Symbol('x')
                eq = self.func(x, *popt)
                yprime = eq.diff(x)


                '''ysec = eq.diff(x, x)
                sol = solve(yprime)
                ageOfWean = []
                for i in sol:
                    try:
                        sol2 = ysec.subs(x, int(i))
                        if sol2 > 0:
                            ageOfWean.append(round(i,2))
                    except:
                        pass
                result_dev = yprime.subs(x, all_age[max_index])
                if sorted(ageOfWean)[0] < 0:
                    self.derivative.append(ageOfWean[1])
                else:
                    self.derivative.append(ageOfWean[0])'''


                self.derivative.append(yprime.subs(x, all_age[max_index]))
                #self.derivative.append('1')


                #Find age of point with maximum distance
                #weaned_age = str(self.func(all_age[max_index], *popt))
                weaned_age = all_age[max_index]

                obs_diff = nitrogen_array[0] - observed_wa_nitrogen
                exp_diff = self.func(self.X[0], *popt) - self.func(all_age[max_index], *popt)
                mean_diff = statistics.mean([obs_diff, exp_diff])
                std = statistics.stdev([obs_diff, exp_diff])

                self.obs_wa.append(observed_wa)
                self.obs_diff.append(obs_diff)
                self.exp_diff.append(exp_diff)
                self.mean_diff.append(mean_diff)
                self.std.append(std)
                self.weaned_age.append(weaned_age)
                self.name_analyzed.append(name)
            
            except Exception as e:
                print(e)
                



            

        self.individual_names.append('All Samples')

        self.comboBox_2.addItems(self.individual_names)

        self.individual_names.remove('All Samples')

        self.pushButton_7.setEnabled(True)






    def func(self, x, a, b, c, d, e):
        return (a * x**4) + (b * x**3) + (c * x**2) + (d * x) + e
    #def func(self, x, a, b, d):
        #return a + (b * np.exp(-d * x))



    def pyWEAN(self, name):
        """Initial algorithm: finds maximum distance from
        observed points
        """
        a = self.df.loc[(self.df[self.id_column_name] == str(name))]
        age_values = a[self.age_column_name].tolist()
        nitrogen_values = a[self.nitrogen_column_name].tolist()

        self.X = []
        self.Y = []

        #Extract coordinates of first and last measurement point
        self.X.append(a.iloc[0][self.age_column_name])
        self.X.append(a.iloc[-1][self.age_column_name])
        self.Y.append(a.iloc[0][self.nitrogen_column_name])
        self.Y.append(a.iloc[-1][self.nitrogen_column_name])
        self.max_upper_point = np.array([self.X[0], self.Y[0]])
        self.max_lower_point = np.array([self.X[1], self.Y[1]])


        zipped_list = list([age_values, nitrogen_values])
        all_dists = []
        
        """Find distance of each measurement point from line
        passing through first and last point"""
        for i in range(0, len(zipped_list[0])):
                point_list = (zipped_list[0][i], zipped_list[1][i])
                point = np.asarray(point_list)

                dist = np.cross(self.max_upper_point - self.max_lower_point, self.max_lower_point - point) / np.linalg.norm(
                        self.max_upper_point - self.max_lower_point)
                all_dists.append(-1 * dist)

        max_value = max(all_dists)
        max_index = all_dists.index(max_value)

        return [(zipped_list[0][max_index]), (zipped_list[1][max_index])] #Return nitrogen of observed weaning age




    def run(self):
        """On app graph function
        """
        self.graphicsView.clear()
        individual_names = []

        if str(self.comboBox_2.currentText()) == 'All Samples': #All sample option
            individual_names = self.name_analyzed
            
            
            agePlot = statistics.mean(self.weaned_age) #For all samples option calculate mean of population
            value_age = round(float(agePlot), 3)
            plotTitle = str(self.comboBox.currentText()) + ' (mean weaning age = ' + str(value_age) + ')'
            self.graphicsView.setTitle(plotTitle, color='#000000')
            

        else: #Single sample option
            individual_names.append(str(self.comboBox_2.currentText()))
            indexAge = self.name_analyzed.index(str(self.comboBox_2.currentText()))
            agePlot = self.weaned_age[indexAge]
            value_age = round(float(agePlot), 3)


        for name in individual_names:
                a = self.df.loc[(self.df[self.id_column_name] == str(name))]
                x = a[self.age_column_name].tolist()
                y = a[self.nitrogen_column_name].tolist()
                pen = pg.mkPen(color='#29B6FA', width=2)
                pen2 = pg.mkPen(color='#FA88A9', width=2)
                self.graphicsView.setTitle(str(self.comboBox_2.currentText()), color='#000000')
                self.graphicsView.setBackground('w')
                styles = {'color': '#000000', 'font-size': '20px'}
                self.graphicsView.setLabel('left', self.nitrogen_column_name, **styles)
                self.graphicsView.setLabel('bottom', self.age_column_name, **styles)
                self.graphicsView.addLegend(offset=(-30, 30))
                self.graphicsView.plot(x, y, pen=pen)


        if str(self.comboBox_2.currentText()) == 'All Samples':
            self.graphicsView.plot(x, y, pen=pen, name='Observed')
        else:
            self.graphicsView.plot(x, y, pen=pen, symbol='o', name='Observed', symbolBrush=('#29B6FA'))
            try:
                popt = self.fitted_parameters[str(self.comboBox_2.currentText())]
                pen3 = pg.mkPen(color='#000000', width=2)

                minAge = float(a[self.age_column_name].min())
                maxAge = float(a[self.age_column_name].max())

                xFit = []
                yFit = []
                while minAge <= maxAge:
                    xFit.append(minAge)
                    yFit.append(self.func(minAge, *popt))
                    minAge += 0.1

                self.graphicsView.plot(xFit, yFit, pen=pen3, name='Fitted')
                plotTitle = str(self.comboBox_2.currentText()) + ' (weaning age = ' + str(value_age) + ')'

                self.graphicsView.setTitle(plotTitle, color='#000000')
            except:
                print('Nope')

        
        maxClm = float(self.df[self.nitrogen_column_name].max())
        minClm = float(self.df[self.nitrogen_column_name].min())
        

        xWean = []
        yWean = []
        
        
        while minClm <= maxClm:
            xWean.append(value_age)
            yWean.append(minClm)
            minClm += 0.1

        self.graphicsView.plot(xWean, yWean, pen=pen2, name='Weaning Age')

        
        self.pushButton_8.setEnabled(True)





    def download_csv(self):
        """Create csv file for download
        """
        self.progressBar.setValue(5)

        weaning_age_array = np.array(self.weaned_age)
        z_score = stats.zscore(weaning_age_array)
        

        names = []
        if str(self.comboBox_2.currentText()) == 'All Samples':
            names = self.name_analyzed
            saveName = 'All_Samples'
        
        else:
            names.append(str(self.comboBox_2.currentText()))
            saveName = str(self.comboBox_2.currentText())
        
        path = str(self.lineEdit_6.text())
        save_name_results = str(path) + '/' + str(saveName) + '_results.csv'


        with open(save_name_results, 'w') as w:
            w.write('Individual,Weaning Age,Observed Weaning Age,Weaning Age Z score,Rsquared,Derivative,Mean Difference, \
                Std,Observed Nitrogen difference,Expected Nitrogen difference' + '\n')

            for name in names:
                try:
                    indexSample = self.name_analyzed.index(str(name))
                    if self.mean_diff[indexSample]  < 0:
                        w.write(str(name) + ',NA,NA,NA,NA,NA,NA,NA,NA,NA' + '\n')
                    else:
                        w.write(str(name)  + ',' + str(round(self.weaned_age[indexSample], 3)) + ',' + str(round(self.obs_wa[indexSample], 2)) + 
                        ',' +  str(z_score[indexSample])+ ',' + str(self.rsquared[indexSample]) + ',' + str(self.derivative[indexSample]) + ',' + str(self.mean_diff[indexSample]) 
                        + ',' + str(self.std[indexSample]) + ',' + str(self.obs_diff[indexSample]) + ',' + str(self.exp_diff[indexSample]) + '\n')
                except:
                    w.write(str(name) + ',NA,NA,NA,NA,NA,NA,NA,NA,NA' + '\n')

        self.progressBar.setValue(70)


        num_lines = sum(1 for line in open(save_name_results))

        if num_lines > 1:
            pass
        else:
            os.remove(save_name_results)

        self.progressBar.setValue(90)

        try:
            with open(save_name_results, 'r') as f:
                pass
            
            

            self.progressBar.setValue(100)

            self.message_box('Information', 'Done', 'File created succesfully!', 'Great!')

            
        except:
            self.message_box('Warning', 'Warning', 'Problem creating the file. \
                Make sure you have administator privilages and try again.', 'Got it')







    def plot_png(self):
        
        self.progressBar_2.setValue(5)

        names = []
        if str(self.comboBox_2.currentText()) == 'All Samples':
            names = self.name_analyzed
            saveName = 'All_Samples'
        
        else:
            names.append(str(self.comboBox_2.currentText()))
            saveName = str(self.comboBox_2.currentText())

        if len(names) == 1:
            indexSample = self.name_analyzed.index(str(names[0]))
            y= []
            y.append(self.mean_diff[indexSample])
            std = []
            std.append(self.std[indexSample])
            plt.figure(figsize=(3, 3))

        else:
            plt.figure(figsize=(10, 6))
            y = self.mean_diff
            std = self.std

        plt.clf()
        

        path = str(self.lineEdit_6.text())
        save_plot = str(path) + '/' + str(saveName) + '_results_plot.png'

        plt.errorbar(names, y, std, linestyle='None', marker='.', color='#0D7D89')
        plt.axhline(y=2, color='#021B52', linestyle='--', linewidth=1)
        plt.axhline(y=3, color='#021B52', linestyle='--', linewidth=1)
        plt.xticks(ticks=range(len(names)), rotation=90)


        max_y = max(y)
        index = y.index(max_y)
        max_std = std[index]
        max_value = max_y + max_std
        print(max_value)
        if max_value <= 5:
            plt.ylim(0, 5)
        else:
            plt.ylim(0, max_value + 1)

        plt.tight_layout()
        plt.savefig(save_plot, dpi=400, format='png')            
        

        self.progressBar_2.setValue(80)

        try:
            img = Image.open(save_plot)
            self.progressBar_2.setValue(100)

            self.message_box('Information', 'Done', 'File created succesfully!', 'Great!')

            
        except:
            self.message_box('Warning', 'Warning', 'Problem creating the file. \
                Make sure you have administator privilages and try again.', 'Got it')


    def clear(self):
        self.lineEdit.setText("")
        self.lineEdit_6.setText("")
        self.checkBox.setChecked(False)
        self.checkBox_2.setChecked(False)
        self.checkBox_3.setChecked(False)
        self.checkBox_4.setChecked(False)
        self.pushButton.setEnabled(True)
        self.pushButton1.setEnabled(False)
        self.pushButton_7.setEnabled(False)
        self.pushButton_2.setEnabled(False)
        self.comboBox.clear()
        self.comboBox_2.clear()
        self.comboBox_3.clear()
        self.comboBox_4.clear()
        self.graphicsView.clear()
        self.progressBar_2.setValue(0)
        self.progressBar.setValue(0)
        self.graphicsView.setLabel('left', '')
        self.graphicsView.setLabel('bottom', '')
        self.graphicsView.setTitle('')











    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1280, 960)
        MainWindow.setStyleSheet("background-color: rgb(200, 195, 209);")
        MainWindow.setWindowIcon(QtGui.QIcon('WEAN_logo.png'))
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout.setSizeConstraint(QtWidgets.QLayout.SetNoConstraint)
        self.verticalLayout.setSpacing(10)
        self.verticalLayout.setObjectName("verticalLayout")
        self.label = QtWidgets.QLabel(self.centralwidget)
        font = QtGui.QFont()
        font.setPointSize(40)
        self.label.setFont(font)
        self.label.setStyleSheet("")
        self.label.setAlignment(QtCore.Qt.AlignHCenter|QtCore.Qt.AlignTop)
        self.label.setObjectName("label")
        self.verticalLayout.addWidget(self.label)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout()
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.formLayout_4 = QtWidgets.QFormLayout()
        self.formLayout_4.setObjectName("formLayout_4")
        self.pushButton = QtWidgets.QPushButton(self.centralwidget)
        font = QtGui.QFont()
        font.setPointSize(13)
        self.pushButton.setFont(font)
        self.pushButton.setStyleSheet("background-color: rgb(99, 178, 220);\n"
"color: rgb(0, 0, 0);")
        self.pushButton.setObjectName("pushButton")
        self.pushButton.clicked.connect(self.find_file_path)
        self.formLayout_4.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.pushButton)
        self.lineEdit = QtWidgets.QLineEdit(self.centralwidget)
        self.lineEdit.setEnabled(False)
        font = QtGui.QFont()
        font.setPointSize(13)
        self.lineEdit.setFont(font)
        self.lineEdit.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.lineEdit.setObjectName("lineEdit")
        self.formLayout_4.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.lineEdit)
        self.verticalLayout_3.addLayout(self.formLayout_4)
        self.formLayout = QtWidgets.QFormLayout()
        self.formLayout.setObjectName("formLayout")
        self.checkBox = QtWidgets.QCheckBox(self.centralwidget)
        self.checkBox.setObjectName("checkBox")
        self.checkBox.clicked.connect(self.check_box_erase)
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.FieldRole, self.checkBox)
        self.checkBox_2 = QtWidgets.QCheckBox(self.centralwidget)
        self.checkBox_2.setObjectName("checkBox_2")
        self.checkBox_2.clicked.connect(self.check_box2_erase)
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.checkBox_2)
        self.checkBox_4 = QtWidgets.QCheckBox(self.centralwidget)
        self.checkBox_4.setObjectName("checkBox_4")
        self.checkBox_4.clicked.connect(self.check_box4_erase)
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.FieldRole, self.checkBox_4)
        self.checkBox_3 = QtWidgets.QCheckBox(self.centralwidget)
        self.checkBox_3.setObjectName("checkBox_3")
        self.checkBox_3.clicked.connect(self.check_box3_erase)
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.checkBox_3)
        self.label_5 = QtWidgets.QLabel(self.centralwidget)
        self.label_5.setObjectName("label_5")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.label_5)
        self.pushButton1 = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton1.setStyleSheet("color: rgb(0, 0, 0);background-color: rgb(99, 178, 220);\n"
"")
        self.pushButton1.setObjectName("pushButton1")
        self.pushButton1.setEnabled(False)
        self.pushButton1.clicked.connect(self.test_delimiter)
        self.formLayout.setWidget(4, QtWidgets.QFormLayout.SpanningRole, self.pushButton1)
        self.verticalLayout_3.addLayout(self.formLayout)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_3.addItem(spacerItem)
        self.horizontalLayout_5 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.verticalLayout_8 = QtWidgets.QVBoxLayout()
        self.verticalLayout_8.setObjectName("verticalLayout_8")
        self.label_6 = QtWidgets.QLabel(self.centralwidget)
        self.label_6.setObjectName("label_6")
        self.verticalLayout_8.addWidget(self.label_6)
        spacerItem1 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_8.addItem(spacerItem1)
        spacerItem2 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_8.addItem(spacerItem2)
        self.verticalLayout_8.setStretch(0, 1)
        self.verticalLayout_8.setStretch(1, 1)
        self.verticalLayout_8.setStretch(2, 3)
        self.horizontalLayout_5.addLayout(self.verticalLayout_8)
        self.verticalLayout_5 = QtWidgets.QVBoxLayout()
        self.verticalLayout_5.setObjectName("verticalLayout_5")
        self.label_7 = QtWidgets.QLabel(self.centralwidget)
        self.label_7.setObjectName("label_7")
        self.verticalLayout_5.addWidget(self.label_7)
        self.comboBox = QtWidgets.QComboBox(self.centralwidget)
        self.comboBox.setObjectName("comboBox")
        self.verticalLayout_5.addWidget(self.comboBox)
        spacerItem3 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_5.addItem(spacerItem3)
        self.verticalLayout_5.setStretch(0, 1)
        self.verticalLayout_5.setStretch(1, 1)
        self.verticalLayout_5.setStretch(2, 3)
        self.horizontalLayout_5.addLayout(self.verticalLayout_5)
        self.verticalLayout_6 = QtWidgets.QVBoxLayout()
        self.verticalLayout_6.setObjectName("verticalLayout_6")
        self.label_8 = QtWidgets.QLabel(self.centralwidget)
        self.label_8.setObjectName("label_8")
        self.verticalLayout_6.addWidget(self.label_8)
        self.comboBox_3 = QtWidgets.QComboBox(self.centralwidget)
        self.comboBox_3.setObjectName("comboBox_3")
        self.verticalLayout_6.addWidget(self.comboBox_3)
        spacerItem4 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_6.addItem(spacerItem4)
        self.verticalLayout_6.setStretch(0, 1)
        self.verticalLayout_6.setStretch(1, 1)
        self.verticalLayout_6.setStretch(2, 3)
        self.horizontalLayout_5.addLayout(self.verticalLayout_6)
        self.verticalLayout_7 = QtWidgets.QVBoxLayout()
        self.verticalLayout_7.setObjectName("verticalLayout_7")
        self.label_9 = QtWidgets.QLabel(self.centralwidget)
        self.label_9.setObjectName("label_9")
        self.verticalLayout_7.addWidget(self.label_9)
        self.comboBox_4 = QtWidgets.QComboBox(self.centralwidget)
        self.comboBox_4.setObjectName("comboBox_4")
        self.verticalLayout_7.addWidget(self.comboBox_4)
        spacerItem5 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_7.addItem(spacerItem5)
        self.verticalLayout_7.setStretch(0, 1)
        self.verticalLayout_7.setStretch(1, 1)
        self.verticalLayout_7.setStretch(2, 3)
        self.horizontalLayout_5.addLayout(self.verticalLayout_7)
        self.verticalLayout_3.addLayout(self.horizontalLayout_5)
        self.verticalLayout_4 = QtWidgets.QVBoxLayout()
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.pushButton_2 = QtWidgets.QPushButton(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.pushButton_2.sizePolicy().hasHeightForWidth())
        self.pushButton_2.setSizePolicy(sizePolicy)
        self.pushButton_2.setStyleSheet("color: rgb(0, 0, 0);background-color: rgb(99, 178, 220);\n"
"")
        self.pushButton_2.setObjectName("pushButton_2")
        self.pushButton_2.setEnabled(False)
        self.pushButton_2.clicked.connect(self.load_csv)
        self.verticalLayout_4.addWidget(self.pushButton_2)
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.label_2 = QtWidgets.QLabel(self.centralwidget)
        self.label_2.setObjectName("label_2")
        self.horizontalLayout_3.addWidget(self.label_2)
        self.comboBox_2 = QtWidgets.QComboBox(self.centralwidget)
        self.comboBox_2.setObjectName("comboBox_2")
        self.horizontalLayout_3.addWidget(self.comboBox_2)
        spacerItem6 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_3.addItem(spacerItem6)
        self.horizontalLayout_3.setStretch(0, 1)
        self.horizontalLayout_3.setStretch(1, 2)
        self.horizontalLayout_3.setStretch(2, 3)
        self.verticalLayout_4.addLayout(self.horizontalLayout_3)
        spacerItem7 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_4.addItem(spacerItem7)
        self.verticalLayout_4.setStretch(0, 2)
        self.verticalLayout_4.setStretch(1, 1)
        self.verticalLayout_3.addLayout(self.verticalLayout_4)
        spacerItem8 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_3.addItem(spacerItem8)
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.pushButton_7 = QtWidgets.QPushButton(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.pushButton_7.sizePolicy().hasHeightForWidth())
        self.pushButton_7.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setPointSize(17)
        font.setBold(False)
        font.setWeight(50)
        self.pushButton_7.setFont(font)
        self.pushButton_7.setStyleSheet("color: rgb(0, 0, 0);background-color: rgb(46, 103, 162);")
        self.pushButton_7.setObjectName("pushButton_7")
        self.pushButton_7.setEnabled(False)
        self.pushButton_7.clicked.connect(self.run)
        self.horizontalLayout_4.addWidget(self.pushButton_7)
        self.pushButton_6 = QtWidgets.QPushButton(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.pushButton_6.sizePolicy().hasHeightForWidth())
        self.pushButton_6.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setPointSize(17)
        self.pushButton_6.setFont(font)
        self.pushButton_6.setStyleSheet("color: rgb(255, 255, 255);\n"
"background-color: rgb(231, 0, 68);")
        self.pushButton_6.setObjectName("pushButton_6")
        self.pushButton_6.clicked.connect(self.clear)
        self.horizontalLayout_4.addWidget(self.pushButton_6)
        self.horizontalLayout_4.setStretch(0, 2)
        self.horizontalLayout_4.setStretch(1, 1)
        self.verticalLayout_3.addLayout(self.horizontalLayout_4)
        self.verticalLayout_3.setStretch(0, 1)
        self.verticalLayout_3.setStretch(1, 2)
        self.verticalLayout_3.setStretch(2, 1)
        self.verticalLayout_3.setStretch(3, 3)
        self.verticalLayout_3.setStretch(4, 2)
        self.verticalLayout_3.setStretch(5, 2)
        self.verticalLayout_3.setStretch(6, 1)
        self.horizontalLayout_2.addLayout(self.verticalLayout_3)
        self.verticalLayout_2 = QtWidgets.QVBoxLayout()
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.graphicsView = PlotWidget(self.centralwidget)
        self.graphicsView.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.graphicsView.setObjectName("graphicsView")
        self.graphicsView.setBackground('w')
        self.verticalLayout_2.addWidget(self.graphicsView)
        self.formLayout_2 = QtWidgets.QFormLayout()
        self.formLayout_2.setObjectName("formLayout_2")
        self.pushButton_8 = QtWidgets.QPushButton(self.centralwidget)
        font = QtGui.QFont()
        font.setPointSize(14)
        self.pushButton_8.setFont(font)
        self.pushButton_8.setStyleSheet("color: rgb(0, 0, 0);background-color: rgb(99, 178, 220);")
        self.pushButton_8.setObjectName("pushButton_8")
        self.pushButton_8.setEnabled(False)
        self.pushButton_8.clicked.connect(self.find_folder_path)
        self.formLayout_2.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.pushButton_8)
        self.lineEdit_6 = QtWidgets.QLineEdit(self.centralwidget)
        self.lineEdit_6.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.lineEdit_6.setObjectName("lineEdit_6")
        self.lineEdit_6.setEnabled(False)
        self.formLayout_2.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.lineEdit_6)
        self.pushButton_9 = QtWidgets.QPushButton(self.centralwidget)
        font = QtGui.QFont()
        font.setPointSize(14)
        self.pushButton_9.setFont(font)
        self.pushButton_9.setObjectName("pushButton_9")
        self.pushButton_9.setEnabled(False)
        self.pushButton_9.clicked.connect(self.download_csv)
        self.formLayout_2.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.pushButton_9)
        self.pushButton_10 = QtWidgets.QPushButton(self.centralwidget)
        font = QtGui.QFont()
        font.setPointSize(14)
        self.pushButton_10.setFont(font)
        self.pushButton_10.setObjectName("pushButton_10")
        self.pushButton_10.setEnabled(False)
        self.pushButton_10.clicked.connect(self.plot_png)
        self.formLayout_2.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.pushButton_10)
        self.progressBar = QtWidgets.QProgressBar(self.centralwidget)
        self.progressBar.setProperty("value", 0)
        self.progressBar.setObjectName("progressBar")
        self.formLayout_2.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.progressBar)
        self.progressBar_2 = QtWidgets.QProgressBar(self.centralwidget)
        self.progressBar_2.setProperty("value", 0)
        self.progressBar_2.setObjectName("progressBar_2")
        self.formLayout_2.setWidget(2, QtWidgets.QFormLayout.FieldRole, self.progressBar_2)
        self.verticalLayout_2.addLayout(self.formLayout_2)
        self.verticalLayout_2.setStretch(0, 8)
        self.verticalLayout_2.setStretch(1, 3)
        self.horizontalLayout_2.addLayout(self.verticalLayout_2)
        self.horizontalLayout_2.setStretch(0, 2)
        self.horizontalLayout_2.setStretch(1, 3)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "WEAN"))
        self.label.setToolTip(_translate("MainWindow", "<html><head/><body><p><span style=\" color:#ef2929;\">WE</span>aning <span style=\" color:#ef2929;\">A</span>ge fi<span style=\" color:#ef2929;\">N</span>der</p></body></html>"))
        self.label.setText(_translate("MainWindow", "<html><head/><body><p><span style=\" color:#002482;\">WE</span>aning <span style=\" color:#002482;\">A</span>ge fi<span style=\" color:#002482;\">N</span>der</p></body></html>"))
        self.pushButton.setText(_translate("MainWindow", "Choose file"))
        self.checkBox.setText(_translate("MainWindow", "space"))
        self.checkBox_2.setText(_translate("MainWindow", "comma"))
        self.checkBox_4.setText(_translate("MainWindow", "semicolon"))
        self.checkBox_3.setText(_translate("MainWindow", "tab"))
        self.label_5.setText(_translate("MainWindow", "Choose delimiter"))
        self.pushButton1.setText(_translate("MainWindow", "Confirm delimiter choice"))
        self.label_6.setText(_translate("MainWindow", "Choose header titles"))
        self.label_7.setText(_translate("MainWindow", "ID column"))
        self.label_8.setText(_translate("MainWindow", "Age column"))
        self.label_9.setText(_translate("MainWindow", "δ15N column"))
        self.pushButton_2.setText(_translate("MainWindow", "Load"))
        self.label_2.setText(_translate("MainWindow", "Choose sample"))
        self.pushButton_7.setText(_translate("MainWindow", "Run"))
        self.pushButton_6.setText(_translate("MainWindow", "Clear"))
        self.pushButton_8.setText(_translate("MainWindow", "Choose destination folder"))
        self.pushButton_9.setText(_translate("MainWindow", "Download .txt results"))
        self.pushButton_10.setText(_translate("MainWindow", "Download .png results"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)

    splash = SplashScreen()
    splash.show()
    splash.progress()
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)


    MainWindow.show()
    splash.finish(MainWindow)
    sys.exit(app.exec_())
