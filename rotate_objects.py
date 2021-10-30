# Maya tool which allows users to easily and quickly place objects in/around another object 
# with a set radius and many other customizable parameters.

# Instructions: to run, navigate to execute_tool.py and run the file

from PySide2.QtCore import * 
from PySide2.QtGui import *
from PySide2.QtUiTools import *
from PySide2.QtWidgets import *
from functools import partial
import maya.cmds as cmds
from maya import OpenMayaUI
from pathlib import Path
import math
from shiboken2 import wrapInstance
from random import randrange
import random

#keep track of transform settings created by user
class Transform():
    def __init__(self):
        self.radius = 0.0
        self.outer = None
        self.center = None
        self.scatter = None
        self.shape = None
        self.duplicate = False
        self.num_duplicate = 0
        
#show gui window
def showWindow():
    # get this files location so we can find the .ui file in the /ui/ folder alongside it
    UI_FILE = str(Path(__file__).parent.resolve() / "gui_2.ui")
    loader = QUiLoader()
    file = QFile(UI_FILE)
    file.open(QFile.ReadOnly)
     
    #Get Maya main window to parent gui window to it
    mayaMainWindowPtr = OpenMayaUI.MQtUtil.mainWindow()
    mayaMainWindow = wrapInstance(int(mayaMainWindowPtr), QWidget)
    ui = loader.load(file, parentWidget=mayaMainWindow)
    file.close()
    
    ui.setParent(mayaMainWindow)
    ui.setWindowFlags(Qt.Window)
    ui.setWindowTitle('Place Around Center Tool')
    ui.setObjectName('Place_Around_Center')
    ui.setWindowFlags(Qt.Window | Qt.WindowStaysOnTopHint)

    t = Transform()

    #function for the clicked center object button
    def clicked_center_button():
        #get selected object(s)
        selected = cmds.ls(sl=True,long=True) or []
        if not(len(selected) == 1):
            print("Please set center to be exactly 1 selected object.")
        else: 
            t.center = selected[0]
        #Change location of locator to be at center object's pivot position
        x = cmds.getAttr(t.center + ".translateX")
        y = cmds.getAttr(t.center + ".translateY")
        z = cmds.getAttr(t.center + ".translateZ")
        #change ui text
        ui.center_objs.setText(t.center[1:])

    #function for the clicked outer object button
    def clicked_outer_button():
        #get selected object(s)
        selected = cmds.ls(sl=True,long=True) or []
        list_outer = []
        for item in cmds.ls(selected):
            #ensure the center object is not part of outer objects
            if not(item == t.center):
                list_outer.append(item)
        t.outer = list_outer
        list_str = ""
        for item in list_outer:
            list_str += str(item)
            if(list_outer.index(item) < (len(list_outer) - 1)):
                list_str += ", "
        #show current selected objects as a list of text on gui
        ui.outer_objs.setText(list_str)

    #circle shape changed function
    def set_circle(c):
        isChecked = ui.circle_check.checkState()
        if isChecked:
            ui.sphere_checkbox.setCheckState(Qt.Unchecked)
            t.shape = "circle"
        else:
            t.shape = None

    #sphere shape changed function
    def set_sphere(s):
        isChecked = ui.sphere_checkbox.checkState()
        if isChecked:
            ui.circle_check.setCheckState(Qt.Unchecked)
            t.shape = "sphere"
        else:
            t.shape = None

    #radius changed function
    def set_radius(r):
        t.radius = float(r)

    #uniform outline scatter changed function
    def set_scatter_uniform_outline(s):
        isChecked = ui.uniform_checkbox.checkState()
        if isChecked:
            ui.random_outline_checkbox.setCheckState(Qt.Unchecked)
            ui.random_fill_checkbox.setCheckState(Qt.Unchecked)
            t.scatter = "uniform_outline"
        else:
            t.scatter = None

    #random outline scatter changed function
    def set_scatter_random_outline(s):
        isChecked = ui.random_outline_checkbox.checkState()
        if isChecked:
            ui.uniform_checkbox.setCheckState(Qt.Unchecked)
            ui.random_fill_checkbox.setCheckState(Qt.Unchecked)
            t.scatter = "random_outline"
        else:
            t.scatter = None

    #random scatter fill changed function
    def set_scatter_random_fill(s):
        isChecked = ui.random_fill_checkbox.checkState()
        if isChecked:
            ui.random_outline_checkbox.setCheckState(Qt.Unchecked)
            ui.uniform_checkbox.setCheckState(Qt.Unchecked)
            t.scatter = "random_fill"
        else:
            t.scatter = None

    #duplicate box changed
    def set_duplicate(d):
        isChecked = ui.duplicate.checkState()
        if isChecked:
            t.duplicate = True
        else:
            t.duplicate = False

    #set number of times to duplicate
    def set_num_duplicate(n):
        t.num_duplicate = int(n)
    
    #find a random 3D point that is exactly the given distance away from (0,0,0)
    #using 3D point distance formula
    def rand_3d(dist):
        #first pick a random value for x
        x = math.sqrt(random.random() * dist ** 2) * random.choice((1, -1))
        #Then choose a value for y with the new maximum of dist^2 - x^2
        y = math.sqrt(random.random() * (dist ** 2 - x ** 2)) * random.choice((1, -1))
        #Finally, the difference is z
        z = math.sqrt(dist ** 2 - x ** 2 - y ** 2) * random.choice((1, -1))

        return (x, y, z)

    #get the distance the 3D point is away from (0,0,0)
    def dist(vector):
        x, y, z = vector
        return math.sqrt(x ** 2 + y ** 2 + z ** 2)

    #apply button clicked
    def apply():
        #User error handling
        if t.center == None:
            ui.warnings.setText("<font color='red'>Warning:Please set a center object.</font>")
            return
        elif t.outer == None:
            ui.warnings.setText("<font color='red'>Warning:Please set at least 1 outer object.</font>")
            return
        elif t.shape == None:
            ui.warnings.setText("<font color='red'>Warning:Please check 1 shape.</font>")
            return
        elif t.scatter == None:
            ui.warnings.setText("<font color='red'>Warning:Please check 1 scatter type.</font>")
            return
        elif t.radius == 0.0:
            ui.warnings.setText("<font color='red'>Warning:Radius is set to 0 cm.</font>") 
        
        else: # all proper fields have been set
            ui.warnings.setText("")

        #if not duplicating objects
        if(t.duplicate == False):
            if(t.shape == "circle"):
                #shape is circle and outline is uniform
                if(t.scatter == "uniform_outline"):
                    #find degrees to rotate around 
                    degrees = 360.0 / (len(t.outer))
                    #degrees accumulator 
                    deg_acc = 0
                    #find world position of center
                    center_world_pos = cmds.xform(t.center,q=1,ws=1,rp=1)
                    for obj in t.outer:
                        #get x, y, z of center object
                        center_x = center_world_pos[0]
                        center_y = center_world_pos[1]
                        center_z = center_world_pos[2] 
                        
                        #Add the radius to the z-axis
                        obj_z = center_z + t.radius
                        #move each outer object to center (+ radius on z axis)
                        cmds.move( center_x, center_y, obj_z, cmds.ls(obj)[0], absolute=True )
                        #convert degrees to radians
                        radians = (deg_acc) * (math.pi / 180)
                        #rotate outer objects around center object about x axis by set radians value
                        x_new = center_x + math.cos(radians) * (center_x - center_x) - math.sin(radians) * (obj_z - center_z) 
                        #rotate outer objects around center object about z axis by set radians value
                        z_new = center_z + math.sin(radians) * (center_x - center_x) + math.cos(radians) * (obj_z - center_z) 
                        #move objects to new locations
                        cmds.move( x_new, center_y, z_new, cmds.ls(obj)[0], worldSpaceDistance=True )

                        deg_acc += degrees
                elif(t.scatter == "random_outline"):
                    #find world position of center
                    center_world_pos = cmds.xform(t.center,q=1,ws=1,rp=1)
                    for obj in t.outer:
                        #find degrees to rotate around 
                        degrees = randrange(360.0)

                        #get x, y, z of center object
                        center_x = center_world_pos[0]
                        center_y = center_world_pos[1]
                        center_z = center_world_pos[2] 
                        
                        #Add the radius to the z-axis
                        obj_z = center_z + t.radius
                        cmds.move( center_x, center_y, obj_z, cmds.ls(obj)[0], absolute=True )

                        radians = (degrees) * (math.pi / 180)
                        #rotate outer objects around center object about x axis by set radians value
                        x_new = center_x + math.cos(radians) * (center_x - center_x) - math.sin(radians) * (obj_z - center_z) 
                        #rotate outer objects around center object about z axis by set radians value
                        z_new = center_z + math.sin(radians) * (center_x - center_x) + math.cos(radians) * (obj_z - center_z) 
                        #move objects to new locations
                        cmds.move( x_new, center_y, z_new, cmds.ls(obj)[0], worldSpaceDistance=True )
                elif(t.scatter == "random_fill"):
                    #find world position of center
                    center_world_pos = cmds.xform(t.center,q=1,ws=1,rp=1)
                    for obj in t.outer:
                        #find degrees to rotate around 
                        degrees = randrange(360.0)
                        rand_rad = randrange(t.radius)

                        #get x, y, z of center object
                        center_x = center_world_pos[0]
                        center_y = center_world_pos[1]
                        center_z = center_world_pos[2] 
                        
                        #Add the radius to the z-axis
                        obj_z = center_z + rand_rad
                        cmds.move( center_x, center_y, obj_z, cmds.ls(obj)[0], absolute=True )

                        radians = (degrees) * (math.pi / 180)
                        #rotate outer objects around center object about x axis by set radians value
                        x_new = center_x + math.cos(radians) * (center_x - center_x) - math.sin(radians) * (obj_z - center_z) 
                        #rotate outer objects around center object about z axis by set radians value
                        z_new = center_z + math.sin(radians) * (center_x - center_x) + math.cos(radians) * (obj_z - center_z) 

                        cmds.move( x_new, center_y, z_new, cmds.ls(obj)[0], worldSpaceDistance=True )
            if(t.shape == "sphere"):
                #shape is sphere and outline is uniform
                if(t.scatter == "uniform_outline"):
                    #find degrees to rotate around 
                    degrees = 360.0 / (len(t.outer))
                    deg_acc = 0
                    #find world position of center
                    center_world_pos = cmds.xform(t.center,q=1,ws=1,rp=1)
                    for obj in t.outer:
                        #get x, y, z of center object
                        center_x = center_world_pos[0]
                        center_y = center_world_pos[1]
                        center_z = center_world_pos[2] 
                        
                        #Add the radius to the z-axis
                        obj_z = center_z + t.radius
                        cmds.move( center_x, center_y, obj_z, cmds.ls(obj)[0], absolute=True )

                        radians = (deg_acc) * (math.pi / 180)
                        #rotate outer objects around center object about x axis by set radians value
                        x_new = center_x + math.cos(radians) * (center_x - center_x) - math.sin(radians) * (obj_z - center_z) 
                        #rotate outer objects around center object about z axis by set radians value
                        z_new = center_z + math.sin(radians) * (center_x - center_x) + math.cos(radians) * (obj_z - center_z) 

                        cmds.move( x_new, center_y, z_new, cmds.ls(obj)[0], worldSpaceDistance=True )

                        deg_acc += degrees
                elif(t.scatter == "random_outline"):
                    #find world position of center
                    center_world_pos = cmds.xform(t.center,q=1,ws=1,rp=1)
                    for obj in t.outer:
                        #find degrees to rotate around 
                        degrees = randrange(360.0)

                        #get x, y, z of center object
                        center_x = center_world_pos[0]
                        center_y = center_world_pos[1]
                        center_z = center_world_pos[2] 

                        position = rand_3d(t.radius)
                        new_x = position[0] + center_x
                        new_y = position[1] + center_y
                        new_z = position[2] + center_z
    
                        cmds.move( new_x, new_y, new_z, cmds.ls(obj)[0], absolute=True )

                        
                        # cmds.move( x_new, center_y, z_new, cmds.ls(obj)[0], worldSpaceDistance=True )
                elif(t.scatter == "random_fill"):
                    #find world position of center
                    center_world_pos = cmds.xform(t.center,q=1,ws=1,rp=1)
                    for obj in t.outer:
                        #find degrees to rotate around 
                        degrees = randrange(360.0)
                        rand_rad = randrange(t.radius)

                        x_rand = randrange(-1*t.radius, t.radius)
                        y_rand = randrange(-1*t.radius, t.radius)
                        z_rand = randrange(-1*t.radius, t.radius)

                        #get x, y, z of center object
                        center_x = center_world_pos[0] + x_rand
                        center_y = center_world_pos[1] + y_rand
                        center_z = center_world_pos[2] + z_rand

                        cmds.move( center_x, center_y, center_z, cmds.ls(obj)[0], worldSpaceDistance=True )

        else: #duplicate same object
            duplicate_list = [t.outer[0]]
            for index in range(t.num_duplicate):
                name = t.outer[0] + "copy_" + str(index)
                cmds.duplicate( t.outer[0], n= name)
                duplicate_list.append(name)
            if(t.shape == "circle"):
                #shape is circle and outline is uniform
                if(t.scatter == "uniform_outline"):
                    #find degrees to rotate around 
                    degrees = 360.0 / (len(duplicate_list))
                    deg_acc = 0
                    #find world position of center
                    center_world_pos = cmds.xform(t.center,q=1,ws=1,rp=1)
                    for obj in duplicate_list:
                        #get x, y, z of center object
                        center_x = center_world_pos[0]
                        center_y = center_world_pos[1]
                        center_z = center_world_pos[2] 
                        
                        #Add the radius to the z-axis
                        obj_z = center_z + t.radius
                        cmds.move( center_x, center_y, obj_z, cmds.ls(obj)[0], absolute=True )

                        radians = (deg_acc) * (math.pi / 180)
                        #rotate outer objects around center object about x axis by set radians value
                        x_new = center_x + math.cos(radians) * (center_x - center_x) - math.sin(radians) * (obj_z - center_z) 
                        #rotate outer objects around center object about z axis by set radians value
                        z_new = center_z + math.sin(radians) * (center_x - center_x) + math.cos(radians) * (obj_z - center_z) 

                        cmds.move( x_new, center_y, z_new, cmds.ls(obj)[0], worldSpaceDistance=True )

                        deg_acc += degrees
                elif(t.scatter == "random_outline"):
                    #find world position of center
                    center_world_pos = cmds.xform(t.center,q=1,ws=1,rp=1)
                    for obj in duplicate_list:
                        #find degrees to rotate around 
                        degrees = randrange(360.0)

                        #get x, y, z of center object
                        center_x = center_world_pos[0]
                        center_y = center_world_pos[1]
                        center_z = center_world_pos[2] 
                        
                        #Add the radius to the z-axis
                        obj_z = center_z + t.radius
                        cmds.move( center_x, center_y, obj_z, cmds.ls(obj)[0], absolute=True )

                        radians = (degrees) * (math.pi / 180)
                        #rotate outer objects around center object about x axis by set radians value
                        x_new = center_x + math.cos(radians) * (center_x - center_x) - math.sin(radians) * (obj_z - center_z) 
                        #rotate outer objects around center object about z axis by set radians value
                        z_new = center_z + math.sin(radians) * (center_x - center_x) + math.cos(radians) * (obj_z - center_z) 

                        cmds.move( x_new, center_y, z_new, cmds.ls(obj)[0], worldSpaceDistance=True )
                elif(t.scatter == "random_fill"):
                    #find world position of center
                    center_world_pos = cmds.xform(t.center,q=1,ws=1,rp=1)
                    for obj in duplicate_list:
                        #find degrees to rotate around 
                        degrees = randrange(360.0)
                        rand_rad = randrange(t.radius)

                        #get x, y, z of center object
                        center_x = center_world_pos[0]
                        center_y = center_world_pos[1]
                        center_z = center_world_pos[2] 
                        
                        #Add the radius to the z-axis
                        obj_z = center_z + rand_rad
                        cmds.move( center_x, center_y, obj_z, cmds.ls(obj)[0], absolute=True )

                        radians = (degrees) * (math.pi / 180)
                        #rotate outer objects around center object about x axis by set radians value
                        x_new = center_x + math.cos(radians) * (center_x - center_x) - math.sin(radians) * (obj_z - center_z) 
                        #rotate outer objects around center object about z axis by set radians value
                        z_new = center_z + math.sin(radians) * (center_x - center_x) + math.cos(radians) * (obj_z - center_z) 

                        cmds.move( x_new, center_y, z_new, cmds.ls(obj)[0], worldSpaceDistance=True )
            if(t.shape == "sphere"):
                #shape is circle and outline is uniform
                if(t.scatter == "uniform_outline"):
                    #find degrees to rotate around 
                    degrees = 360.0 / (len(duplicate_list))
                    deg_acc = 0
                    #find world position of center
                    center_world_pos = cmds.xform(t.center,q=1,ws=1,rp=1)
                    for obj in duplicate_list:
                        #get x, y, z of center object
                        center_x = center_world_pos[0]
                        center_y = center_world_pos[1]
                        center_z = center_world_pos[2] 
                        
                        #Add the radius to the z-axis
                        obj_z = center_z + t.radius
                        cmds.move( center_x, center_y, obj_z, cmds.ls(obj)[0], absolute=True )

                        radians = (deg_acc) * (math.pi / 180)
                        #rotate outer objects around center object about x axis by set radians value
                        x_new = center_x + math.cos(radians) * (center_x - center_x) - math.sin(radians) * (obj_z - center_z) 
                        #rotate outer objects around center object about z axis by set radians value
                        z_new = center_z + math.sin(radians) * (center_x - center_x) + math.cos(radians) * (obj_z - center_z) 

                        cmds.move( x_new, center_y, z_new, cmds.ls(obj)[0], worldSpaceDistance=True )

                        deg_acc += degrees
                elif(t.scatter == "random_outline"):
                    #find world position of center
                    center_world_pos = cmds.xform(t.center,q=1,ws=1,rp=1)
                    for obj in duplicate_list:
                        #find degrees to rotate around 
                        degrees = randrange(360.0)

                        #get x, y, z of center object
                        center_x = center_world_pos[0]
                        center_y = center_world_pos[1]
                        center_z = center_world_pos[2] 

                        position = rand_3d(t.radius)
                        new_x = position[0] + center_x
                        new_y = position[1] + center_y
                        new_z = position[2] + center_z
    
                        cmds.move( new_x, new_y, new_z, cmds.ls(obj)[0], absolute=True )
                        
                        # cmds.move( x_new, center_y, z_new, cmds.ls(obj)[0], worldSpaceDistance=True )
                elif(t.scatter == "random_fill"):
                    #find world position of center
                    center_world_pos = cmds.xform(t.center,q=1,ws=1,rp=1)
                    for obj in duplicate_list:
                        #find degrees to rotate around 
                        degrees = randrange(360.0)
                        rand_rad = randrange(t.radius)

                        x_rand = randrange(-1*t.radius, t.radius)
                        y_rand = randrange(-1*t.radius, t.radius)
                        z_rand = randrange(-1*t.radius, t.radius)

                        #get x, y, z of center object
                        center_x = center_world_pos[0] + x_rand
                        center_y = center_world_pos[1] + y_rand
                        center_z = center_world_pos[2] + z_rand

                        cmds.move( center_x, center_y, center_z, cmds.ls(obj)[0], worldSpaceDistance=True )

#Close dialog
    def close():
        ui.done(0)

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
    ui.close_button.clicked.connect(partial(close))
    ui.duplicate.stateChanged.connect(partial(set_duplicate))
    ui.num_duplicate.valueChanged.connect(partial(set_num_duplicate))

     
    # show the QT ui
    ui.show()
    return ui

if __name__ == "__main__":
    window=showWindow()
