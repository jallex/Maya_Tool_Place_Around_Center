import os
import PySide2.QtCore as QtCore
import PySide2.QtUiTools as QtUiTools
import PySide2.QtWidgets as QtWidgets
from functools import partial
import maya.cmds as cmds
from maya import OpenMayaUI
from pathlib import Path
import math
from shiboken2 import wrapInstance
from random import randrange

#keep track of transform settings created by user
class Transform():
    def __init__(self):
        pass
    #center object
    def set_center(self, c):
        self.center = c
    #outer object(s)
    def set_outer(self, o):
        self.outer = o 
    #radius
    def set_radius(self, r):
        self. radius = r
    def set_shape(self, s):
        self.shape = s
    def set_scatter(self, s):
        self.scatter = s
    def get_center(self):
        return self.center
    def get_outer(self):
        return self.outer
    def get_radius(self):
        return self.radius 
    def get_shape(self):
        return self.shape
    def get_scatter(self):
        return self.scatter
        
def maya_main_window():
	main_window_ptr=OpenMayaUI.MQtUtil.mainWindow()
	print(wrapInstance(main_window_ptr, QtWidgets.QWidget))
	return wrapInstance(main_window_ptr, QtWidgets.QWidget)

#show gui window
def showWindow():
    # get this files location so we can find the .ui file in the /ui/ folder alongside it
    #UI_FILE = Path(__file__).parent.resolve() / "gui.ui"
    UI_FILE = r"/Users/jackieallex/Documents/capstone/Maya_Python_Place-Rotate_Many_Objects_tool/gui.ui"
    
    # do some QT loading stuff
    ui_file = QtCore.QFile(UI_FILE)
    ui_file.open(QtCore.QFile.ReadOnly)
    loader = QtUiTools.QUiLoader()
    ui = loader.load(ui_file, parentWidget=maya_main_window())
    ui_file.close()

    t = Transform()

    #function for the clicked center object button
    def clicked_center_button():
        #get selected object(s)
        selected = cmds.ls(sl=True,long=True) or []
        if not(len(selected) == 1):
            print("Please set center to be exactly 1 selected object.")
        else: 
            t.set_center(selected[0])
        #Change location of locator to be at center object's pivot position
        x = cmds.getAttr(t.get_center() + ".translateX")
        y = cmds.getAttr(t.get_center() + ".translateY")
        z = cmds.getAttr(t.get_center() + ".translateZ")
        #change ui text
        ui.center_objs.setText(t.get_center()[1:])
        print("set center ", t.get_center())

    def clicked_outer_button():
        selected = cmds.ls(sl=True,long=True) or []
        list_outer = []
        for item in cmds.ls(selected):
            if not(item == t.get_center):
                list_outer.append(item)
        t.set_outer(list_outer)
        list_str = ""
        for item in list_outer:
            list_str += str(item)
            if(list_outer.index(item) < (len(list_outer) - 1)):
                list_str += ", "
        ui.outer_objs.setText(list_str)

    def set_radius(r):
        radius = float(r)
        t.set_radius(radius)

    def set_circle(c):
        isChecked = ui.circle_check.checkState()
        if isChecked:
            ui.sphere_checkbox.setCheckState(QtCore.Qt.Unchecked)
            t.set_shape("circle") 

    def set_sphere(s):
        isChecked = ui.sphere_checkbox.checkState()
        if isChecked:
            ui.circle_check.setCheckState(QtCore.Qt.Unchecked)
            t.set_shape("sphere")

    def set_scatter_uniform_outline(s):
        isChecked = ui.uniform_checkbox.checkState()
        if isChecked:
            ui.random_outline_checkbox.setCheckState(QtCore.Qt.Unchecked)
            ui.random_fill_checkbox.setCheckState(QtCore.Qt.Unchecked)
            t.set_scatter("uniform_outline") 

    def set_scatter_random_outline(s):
        isChecked = ui.random_outline_checkbox.checkState()
        if isChecked:
            ui.uniform_checkbox.setCheckState(QtCore.Qt.Unchecked)
            ui.random_fill_checkbox.setCheckState(QtCore.Qt.Unchecked)
            t.set_scatter("random_outline")

    def set_scatter_random_fill(s):
        isChecked = ui.random_fill_checkbox.checkState()
        if isChecked:
            ui.random_outline_checkbox.setCheckState(QtCore.Qt.Unchecked)
            ui.uniform_checkbox.setCheckState(QtCore.Qt.Unchecked)
            t.set_scatter("random_fill")

    def apply():
        if (t.get_radius() > -1) and (len(t.get_outer()) > 0) and not(t.get_center() == None):
            if(t.get_shape() == "circle"):
                #shape is circle and outline is uniform
                if(t.get_scatter() == "uniform_outline"):
                    #find degrees to rotate around 
                    degrees = 360.0 / (len(t.get_outer()))
                    deg_acc = 0
                    #find world position of center
                    center_world_pos = cmds.xform(t.get_center(),q=1,ws=1,rp=1)
                    for obj in t.get_outer():
                        #get x, y, z of center object
                        center_x = center_world_pos[0]
                        center_y = center_world_pos[1]
                        center_z = center_world_pos[2] 
                        
                        #Add the radius to the z-axis
                        obj_z = center_z + t.get_radius()
                        cmds.move( center_x, center_y, obj_z, cmds.ls(obj)[0], absolute=True )

                        radians = (deg_acc) * (math.pi / 180)

                        x_new = center_x + math.cos(radians) * (center_x - center_x) - math.sin(radians) * (obj_z - center_z) 
                        z_new = center_z + math.sin(radians) * (center_x - center_x) + math.cos(radians) * (obj_z - center_z) 

                        cmds.move( x_new, center_y, z_new, cmds.ls(obj)[0], worldSpaceDistance=True )

                        deg_acc += degrees
                elif(t.get_scatter() == "random_outline"):
                    #find world position of center
                    center_world_pos = cmds.xform(t.get_center(),q=1,ws=1,rp=1)
                    for obj in t.get_outer():
                        #find degrees to rotate around 
                        degrees = randrange(360.0)

                        #get x, y, z of center object
                        center_x = center_world_pos[0]
                        center_y = center_world_pos[1]
                        center_z = center_world_pos[2] 
                        
                        #Add the radius to the z-axis
                        obj_z = center_z + t.get_radius()
                        cmds.move( center_x, center_y, obj_z, cmds.ls(obj)[0], absolute=True )

                        radians = (degrees) * (math.pi / 180)

                        x_new = center_x + math.cos(radians) * (center_x - center_x) - math.sin(radians) * (obj_z - center_z) 
                        z_new = center_z + math.sin(radians) * (center_x - center_x) + math.cos(radians) * (obj_z - center_z) 

                        cmds.move( x_new, center_y, z_new, cmds.ls(obj)[0], worldSpaceDistance=True )
                elif(t.get_scatter() == "random_fill"):
                    #find world position of center
                    center_world_pos = cmds.xform(t.get_center(),q=1,ws=1,rp=1)
                    for obj in t.get_outer():
                        #find degrees to rotate around 
                        degrees = randrange(360.0)
                        rand_rad = randrange(float(t.get_radius))

                        #get x, y, z of center object
                        center_x = center_world_pos[0]
                        center_y = center_world_pos[1]
                        center_z = center_world_pos[2] 
                        
                        #Add the radius to the z-axis
                        obj_z = center_z + rand_rad
                        cmds.move( center_x, center_y, obj_z, cmds.ls(obj)[0], absolute=True )

                        radians = (degrees) * (math.pi / 180)

                        x_new = center_x + math.cos(radians) * (center_x - center_x) - math.sin(radians) * (obj_z - center_z) 
                        z_new = center_z + math.sin(radians) * (center_x - center_x) + math.cos(radians) * (obj_z - center_z) 

                        cmds.move( x_new, center_y, z_new, cmds.ls(obj)[0], worldSpaceDistance=True )

    #connect buttons to functions
    ui.center_button.clicked.connect(partial(clicked_center_button))
    ui.outer_button.clicked.connect(partial(clicked_outer_button))
    ui.radius_box.valueChanged.connect(partial(set_radius))
    ui.apply_button.clicked.connect(partial(apply))
    ui.circle_check.stateChanged.connect(partial(set_circle))
    ui.sphere_checkbox.stateChanged.connect(partial(set_sphere))
    ui.uniform_checkbox.stateChanged.connect(partial(set_scatter_uniform_outline))
    ui.random_outline_checkbox.stateChanged.connect(partial(set_scatter_random_outline))
    ui.random_fill_checkbox.stateChanged.connect(partial(set_scatter_random_fill))
     
    # show the QT ui
    ui.show()
    return ui

if __name__ == "__main__":
    window=showWindow()