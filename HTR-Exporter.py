




import os
import maya.cmds as cm


class Joint:
    
    def __init__(self, _children):
        self.children = _children


def construct_joint_hierarchy(mayaObject) -> Joint:
    
    if(cm.objectType(mayaObject, isType = "joint") == False): # If passed in object isn't joint, return null
        return None
        
    childJoints = []
    
    childMayaObjects = cm.listRelatives(mayaObject, c = True) # Get list of children
    
    print("PARENT: " + str(mayaObject) + " | CHILDREN: " + str(childMayaObjects))
    
    for i in range(len(childMayaObjects)):
        possibleJoint = construct_joint_hierarchy(childMayaObjects[i])
        if possibleJoint != None:
            childJoints.append(possibleJoint)
            
    return Joint(childJoints)
    
    #joints.append(Joint(NULL, NULL))


# To work correctly, have root selected before running

#while(

#relatives = cm.listRelatives(ad = True)
#print(relatives)

def main():
    
    mayaSelectedObject = cm.ls(sl = True) # Get all selected objects

    if len(mayaSelectedObject) < 1: # If there isn't at least one object selected, don't continue
        return
        
    mayaSelectedObject = mayaSelectedObject[0] # Get first item in selection
    
    
        
    # Write to file
    htr = open("HTR-Result.htr", "w")
    htr.close()

    construct_joint_hierarchy(mayaSelectedObject)

#print(construct_joint_hierarchy(cm.ls(sl = True)[0]))

#numSegments = 0

if __name__ == "__main__":
    main()
