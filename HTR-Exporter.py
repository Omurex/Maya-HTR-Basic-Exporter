# To work correctly, have root selected before running




import os
import maya.cmds as cm


class TransformationInfoTimeline:
    
    # _data == list of TransformationInfo objects
    def __init__(self, _data):
        self.data = _data
        
        
    def __str__(self):
        
        returnStr = ""
        
        for i in range(len(self.data)):
            returnStr += str(i) + " : " + str(self.data[i])
            returnStr += "\n"
            
        return returnStr


class TransformationInfo:
    
    def __init__(self, _translation, _rotation):
        self.translation = _translation
        self.rotation = _rotation
        
    
    def __str__(self):
        
        returnStr = "TRANSLATION: " + str(self.translation) + " | ROTATION: " + str(self.rotation)
        return returnStr


class Joint:
    
    TO_STRING_INDENT_SPACING = 2
    
    def __init__(self, _mayaObject, _name, _parent, _children, _frameTransformationInfo):
        self.mayaObject = _mayaObject
        self.name = _name
        self.parent = _parent
        self.children = _children
        self.frameTransformationInfo = _frameTransformationInfo
        
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


def get_transformation_info_at_time(mayaObject, time):
    
    translation = [0] * 3
    rotation = [0] * 3
    
    translation[0] = cm.getAttr("{}.translateX".format(mayaObject), time = time)
    translation[1] = cm.getAttr("{}.translateY".format(mayaObject), time = time)
    translation[2] = cm.getAttr("{}.translateZ".format(mayaObject), time = time)
    
    rotation[0] = cm.getAttr("{}.rotateX".format(mayaObject), time = time)
    rotation[1] = cm.getAttr("{}.rotateY".format(mayaObject), time = time)
    rotation[2] = cm.getAttr("{}.rotateZ".format(mayaObject), time = time)
    
    return TransformationInfo(translation, rotation)


def get_transformation_info_for_timeline(mayaObject, numFrames):
    
    tInfo = [None] * numFrames
    
    for i in range(numFrames):
        tInfo[i] = get_transformation_info_at_time(mayaObject, i)
    
    return TransformationInfoTimeline(tInfo)



def get_num_frames(mayaObject):
    
    # Found out how to interact with keyframe data from following video:
    # https://www.youtube.com/watch?v=A5EnANHt9Rw
    
    keyframeChannels = cm.keyframe(mayaObject, q = True)
    keyframes = sorted(set(keyframeChannels))
        
    numFrames = int(round(keyframes[len(keyframes) - 1]))
    
    return numFrames



def construct_joint_hierarchy(mayaObject, numFrames, jointParent = None) -> Joint:
    
    if(cm.objectType(mayaObject, isType = "joint") == False): # If passed in object isn't joint, return null
        return None
        
    childJoints = []
    
    childMayaObjects = cm.listRelatives(mayaObject, c = True) # Get list of children
    
    
    
    # Get keyframe data for this joint for whole timeline
    
    
    
    newJoint = Joint(mayaObject, str(mayaObject), jointParent, [], None) # Construct new joint, fill in children later
    
    # If this joint has no children, we're done
    if childMayaObjects == None:
        return newJoint
        
    # Loop through children, and try to add them as joint children if they are joints
    for i in range(len(childMayaObjects)):
        possibleJoint = construct_joint_hierarchy(childMayaObjects[i], numFrames, newJoint)
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
    
    if(cm.objectType(mayaSelectedObject, isType = "joint") == False):
        return
    
    numFrames = get_num_frames(mayaSelectedObject)
    
    rootJoint = construct_joint_hierarchy(mayaSelectedObject, numFrames)
    
    print(get_transformation_info_for_timeline(rootJoint.mayaObject, numFrames))
    
    print(rootJoint)
    
    return rootJoint


def main():
    
    rootJoint = handle_selected_joint()
    
    print(cm.playbackOptions(fps = True))
        
    # Write to file
    htr = open("HTR-Result.htr", "w")
    htr.close()

    # Found out how to interact with keyframe data from following video:
    # https://www.youtube.com/watch?v=A5EnANHt9Rw
    #if rootJoint != None:
     #   keyframeChannels = cm.keyframe(rootJoint.mayaObject, q = True)
     #   
     #   if keyframeChannels == None:
    #        return
    ##    
    #    keyframes = sorted(set(keyframeChannels))
    #    print(keyframes)
    #    
    #    numFrames = int(round(keyframes[len(keyframes) - 1]))
    #    
    #    for i in range(numFrames):
    #        print(cm.getAttr("{}.rotateZ".format(rootJoint.mayaObject), time = i))
            



if __name__ == "__main__":
    main()
