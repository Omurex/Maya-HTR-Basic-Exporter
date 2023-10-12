# To work correctly, have root selected before running




import os
import maya.cmds as cm


class Joint:
    
    TO_STRING_INDENT_SPACING = 2
    
    def __init__(self, _mayaObject, _name, _parent, _children):
        self.mayaObject = _mayaObject
        self.name = _name
        self.parent = _parent
        self.children = _children
        
    def __str__(self):
        return self.to_hierarchy_string(0)

    def to_hierarchy_string(self, spacing) -> str:
        
        returnStr = ""
        
        for i in range(spacing):
            returnStr += " "
        
        returnStr += self.name
        
        for i in range(len(self.children)):
            returnStr += "\n"
            returnStr += self.children[i].to_hierarchy_string(spacing + self.TO_STRING_INDENT_SPACING)
            
        return returnStr
        
        
    def get_parent_name(self) -> str:
        
        if self.parent is None:
            return "GLOBAL"
            
        else:
            return self.parent.name



def construct_joint_hierarchy(mayaObject, jointParent = None) -> Joint:
    
    if(cm.objectType(mayaObject, isType = "joint") == False): # If passed in object isn't joint, return null
        return None
        
    childJoints = []
    
    childMayaObjects = cm.listRelatives(mayaObject, c = True) # Get list of children
    
    newJoint = Joint(mayaObject, str(mayaObject), jointParent, []) # Construct new joint, fill in children later
    
    # If this joint has no children, we're done
    if childMayaObjects == None:
        return newJoint
        
    # Loop through children, and try to add them as joint children if they are joints
    for i in range(len(childMayaObjects)):
        possibleJoint = construct_joint_hierarchy(childMayaObjects[i], newJoint)
        if possibleJoint != None:
            childJoints.append(possibleJoint)
            
    newJoint.children = childJoints
            
    return newJoint

#while(

#relatives = cm.listRelatives(ad = True)
#print(relatives)


def handle_selected_joint():
    
    mayaSelectedObject = cm.ls(sl = True) # Get all selected objects

    if len(mayaSelectedObject) < 1: # If there isn't at least one object selected, don't continue
        return
        
    mayaSelectedObject = mayaSelectedObject[0] # Get first item in selection
    
    #if(cm.objectType(mayaSelectedObject, isType = "joint") == False):
     #   return
    
    rootJoint = construct_joint_hierarchy(mayaSelectedObject)
    
    print(rootJoint)
    
    return rootJoint


def main():
    
    rootJoint = handle_selected_joint()
    
    print(cm.playbackOptions(fps = True))
        
    # Write to file
    htr = open("HTR-Result.htr", "w")
    htr.close()
    
    #print(cm.currentTime(query = True))
    #print(cm.keyframe(keyframeCount = True)) # Error
    #print(cm.controller(allControllers = True)) # Returns None
    #print(cm.timeEditor(query = True)) # Error
    #print(cm.timeEditorClip("TailClip", track = True, query = True))
    #print(cm.keyframe(query = True, time = (0,)))

    # Found out how to interact with keyframe data from following video:
    # https://www.youtube.com/watch?v=A5EnANHt9Rw
    if rootJoint != None:
        keyframeChannels = cm.keyframe(rootJoint.mayaObject, q = True)
        
        if keyframeChannels == None:
            return
        
        keyframes = sorted(set(keyframeChannels))
        print(keyframes)
        
        for i in range(len(keyframes)):
            print(cm.getAttr("{}.rotateZ".format(rootJoint.mayaObject), time = keyframes[i]))
            



if __name__ == "__main__":
    main()
