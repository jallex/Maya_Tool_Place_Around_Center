import os
import PySide2.QtCore as QtCore
import PySide2.QtUiTools as QtUiTools
import PySide2.QtWidgets as QtWidgets
from functools import partial
import maya.cmds as cmds
from pathlib import Path
import math

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
    def set_locator(self, l):
        self.locator = l
    def get_center(self):
        return self.center
    def get_outer(self):
        return self.outer
    def get_radius(self):
        return self.radius 
    def get_locator(self):
        return self.locator

#show gui window
def showWindow():
    # get this files location so we can find the .ui file in the /ui/ folder alongside it
    UI_FILE = Path(__file__).parent.resolve() / "gui.ui"
    # do some QT loading stuff
    ui_file = QtCore.QFile(UI_FILE)
    ui_file.open(QtCore.QFile.ReadOnly)
    loader = QtUiTools.QUiLoader()
    ui = loader.load(ui_file)
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
        ui.center_objs.setText(t.get_center())
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

    def apply():
        if (t.get_radius() > -1) and (len(t.get_outer()) > 0) and not(t.get_center() == None):
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

    #connect buttons to functions
    ui.center_button.clicked.connect(partial(clicked_center_button))
    ui.outer_button.clicked.connect(partial(clicked_outer_button))
    ui.radius_box.valueChanged.connect(partial(set_radius))
    ui.apply_button.clicked.connect(partial(apply))
     
    # show the QT ui
    ui.show()
    return ui

if __name__ == "__main__":
    window=showWindow()


