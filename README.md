# Maya Tool Place Around Center
A Maya tool written in Python3 using maya.cmds that allows users to easily and quickly place objects in/around another object with a set radius and many other customizable parameters.

Note: Python3 is compatible with Maya 2022 and onward

  <p align="left">
   <img src="https://user-images.githubusercontent.com/44556715/138212661-d20f39b0-f849-45e0-b1cd-94a4d40f1a6a.png">
  </p>

# What can this tool do?
This tool allows the user to
- Place many selected objects in an even circle around a center object
  <p align="left">
   <img src="https://user-images.githubusercontent.com/44556715/138212284-75eeee67-fd42-4c19-9728-0436d840b27d.gif">
  </p>
- Duplicate one object around a center object
  <p align="left">
   <img src="https://user-images.githubusercontent.com/44556715/138215279-8c1dd95f-d149-4c1e-bea2-7102cefbd166.gif">
  </p>
- Randomly place selected objects in circle with a max-radius around a center object
  <p align="left">
   <img src="https://user-images.githubusercontent.com/44556715/138215003-cfd8da1d-ffbe-4d36-8a86-90b83653f195.gif">
  </p>
- Randomly duplicate object with a max-radius around radius of a center object in a 2D circle or 3D sphere
  <p align="left">
   <img src="https://user-images.githubusercontent.com/44556715/138212932-c9c8c082-56ae-4eef-a3dc-2ba54cf6a928.gif">
  </p>
- Randomly place or duplicate object(s) within a 2D circle or 3D sphere around center object
  <p align="left">
   <img src="https://user-images.githubusercontent.com/44556715/138213086-80d059ad-b39e-468b-b174-981216de290a.gif">
  </p>
  

# How to Use
1. Download folder 
2. Place files in your Maya scripts folder or update line 5 of "execute_tool.py" to be the location of the parent folder that this repository folder is located within OR ensure the parent folder is in your PYTHONPATH. This ensures that Maya can find all files in the project when run. 
3. Open the "execute_tool.py" file in the Maya script editor
4. Run the script, and the GUI for the tool will appear on screen.
5. Select the center object, surrounding outside objects, and other parameters using GUI and press "Apply" - then watch the magic happen! 


----------------
# Future goals
1. Allow for a higher radius than 99.0
2. Rotate objects inward towards center, example: chairs around a table
3. Random scale of objects
4. Prevent objects from colliding with each other
5. Patterns - such as placing houses or bricks

