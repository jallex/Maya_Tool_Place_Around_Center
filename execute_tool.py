import sys

#SET THIS FOLDER to the parent folder that you've downloaded the repository to
#or ensure that the parent folder is added to your PYTHONPATH
folder = ''

#check if folder is part of PYTHONPATH and if not, add it
if folder not in sys.path:
    sys.path.append(folder)

if 'Maya_Tool_Place_Around_Center' in sys.modules:
    del sys.modules['Maya_Tool_Place_Around_Center']
if 'Maya_Tool_Place_Around_Center.rotate_objects' in sys.modules:
    del sys.modules['Maya_Tool_Place_Around_Center.rotate_objects']
import Maya_Tool_Place_Around_Center.rotate_objects

window = Maya_Tool_Place_Around_Center.rotate_objects.showWindow()