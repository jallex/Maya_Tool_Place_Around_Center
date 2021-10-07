import os
import PySide2.QtCore as QtCore
import PySide2.QtUiTools as QtUiTools
import PySide2.QtWidgets as QtWidgets
from functools import partial
import maya.cmds as cmds
from pathlib import Path
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
        #cmds.move( x, y, z, cmds.ls(t.get_center()), absolute=True )
        #change ui text
        ui.center_objs.setText(t.get_center())
        print("set center ", t.get_center())

    def clicked_outer_button():
        selected = cmds.ls(sl=True,long=True) or []
        list_outer = []
        for item in cmds.ls(selected):
            print(item, "==", t.get_center)
            if not(item == t.get_center):
                list_outer.append(item)
        t.set_outer(list_outer)
        list_str = ""
        for item in list_outer:
            list_str += str(item)
            if(list_outer.index(item) < (len(list_outer) - 1)):
                list_str += ", "
        ui.outer_objs.setText(list_str)
        print("set outer ", t.get_outer())

    def set_radius(r):
        radius = float(r)
        t.set_radius(radius)
        print("set radius", t.get_radius())

    def apply():
        print(t.get_radius())
        print(len(t.get_outer()))
        print(t.get_center())
        if (t.get_radius() > -1) and (len(t.get_outer()) > 0) and not(t.get_center() == None):
            #find degrees to rotate around 
            degrees = 360.0 / (len(t.get_outer()))
            deg_acc = 0
            for obj in t.get_outer():
                #offset by radius
                x = cmds.getAttr(t.get_center() + ".translateX")
                y = cmds.getAttr(t.get_center() + ".translateY")
                z = cmds.getAttr(t.get_center() + ".translateZ")
                # cmds.move( x, y, z + t.get_radius(), cmds.ls(obj)[0], absolute=True )
                # cmds.rotate(0, str(degrees) + 'deg', 0, cmds.ls(t.get_locator()))
                cmds.move( x, y, z + t.get_radius(), cmds.ls(obj)[0], absolute=True )
                cmds.rotate( 0, str(deg_acc) + 'deg', 0, cmds.ls(obj)[0], pivot=(x, y, z) )
                deg_acc += degrees
                print("moved " + obj + " " + str(degrees) + 'deg')
                #rotate Null object
                #cmds.setAttr(t.get_locator().ry,degrees)

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


