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
    
    def __init__(self, _translation, _rotation, _scaleFactor):
        self.translation = _translation
        self.rotation = _rotation
        self.scaleFactor = _scaleFactor
        
    
    def __str__(self):
        
        returnStr = "TRANSLATION: " + str(self.translation) + " | ROTATION: " + str(self.rotation) + \
            " | SCALE FACTOR: " + str(self.scaleFactor)
        return returnStr
        
        
    def __sub__(self, other):
        
        newTranslation = [self.translation[0] - other.translation[0], self.translation[1] - other.translation[1], self.translation[2] - other.translation[2]]
        newRotation = [self.rotation[0] - other.rotation[0], self.rotation[1] - other.rotation[1], self.rotation[2] - other.rotation[2]]
        newInfo = TransformationInfo(newTranslation, newRotation, self.scaleFactor - other.scaleFactor)
        
        return newInfo
        
        
    def get_htr_format(self):
        return str(self.translation[0]) + "\t" + str(self.translation[1]) + "\t" + str(self.translation[2]) + "\t" \
            + str(self.rotation[0]) + "\t" + str(self.rotation[1]) + "\t" + str(self.rotation[2]) + "\t" + str(self.scaleFactor)


class Joint:
    
    TO_STRING_INDENT_SPACING = 2
    
    def __init__(self, _mayaObject, _name, _parent, _children, _frameTransformationInfoTimeline):
        self.mayaObject = _mayaObject
        self.name = _name
        self.parent = _parent
        self.children = _children
        self.frameTransformationInfoTimeline = _frameTransformationInfoTimeline
        
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
    
    # All the below are floats
    translation = [0] * 3
    translation[0] = cm.getAttr("{}.translateX".format(mayaObject), time = time)
    translation[1] = cm.getAttr("{}.translateY".format(mayaObject), time = time)
    translation[2] = cm.getAttr("{}.translateZ".format(mayaObject), time = time)
    
    rotation = [0] * 3
    rotation[0] = cm.getAttr("{}.rotateX".format(mayaObject), time = time)
    rotation[1] = cm.getAttr("{}.rotateY".format(mayaObject), time = time)
    rotation[2] = cm.getAttr("{}.rotateZ".format(mayaObject), time = time)
    
    scaleFactor = cm.getAttr("{}.scaleX".format(mayaObject), time = time)
    
    return TransformationInfo(translation, rotation, scaleFactor)



def get_transformation_info_for_timeline(mayaObject, numFrames):
    
    tInfo = [None] * numFrames
    
    for i in range(numFrames):
        tInfo[i] = get_transformation_info_at_time(mayaObject, i)
    
    return TransformationInfoTimeline(tInfo)



def get_num_frames():
    
    # Found out how to interact with keyframe data from following video:
    # https://www.youtube.com/watch?v=A5EnANHt9Rw
    
    # Old method, didn't work with root joint
    #keyframeChannels = cm.keyframe(mayaObject, q = True)
    #keyframes = sorted(set(keyframeChannels))
        
    #numFrames = int(round(keyframes[len(keyframes) - 1]))
    
    return int(round(cm.playbackOptions(q = True, max = True)) - round(cm.playbackOptions(q = True, min = True))) + 1



def construct_joint_hierarchy(mayaObject, numFrames, jointParent = None) -> (Joint, int):
    
    if(cm.objectType(mayaObject, isType = "joint") == False): # If passed in object isn't joint, return null
        return None
        
    childJoints = []
    
    childMayaObjects = cm.listRelatives(mayaObject, c = True) # Get list of children
    
    numJoints = 1 # Starts at 1 because we count ourselves
    
    # Get keyframe data for this joint for whole timeline
    timeline = get_transformation_info_for_timeline(mayaObject, numFrames)
    
    # Construct new joint, fill in children later
    newJoint = Joint(mayaObject, str(mayaObject), jointParent, [], timeline)
    
    # If this joint has no children, we're done
    if childMayaObjects == None:
        return newJoint, numJoints
        
    # Loop through children, and try to add them as joint children if they are joints
    for i in range(len(childMayaObjects)):
        
        possibleJoint = construct_joint_hierarchy(childMayaObjects[i], numFrames, newJoint)
        
        if possibleJoint != None:
            childJoints.append(possibleJoint[0])
            numJoints += possibleJoint[1]
            
    newJoint.children = childJoints
            
    return newJoint, numJoints



def handle_selected_joint():
    
    mayaSelectedObject = cm.ls(sl = True) # Get all selected objects

    if len(mayaSelectedObject) < 1: # If there isn't at least one object selected, don't continue
        return
        
    mayaSelectedObject = mayaSelectedObject[0] # Get first item in selection
    
    if(cm.objectType(mayaSelectedObject, isType = "joint") == False):
        return
    
    numFrames = get_num_frames()
    
    rootJoint, numJoints = construct_joint_hierarchy(mayaSelectedObject, numFrames)
    
    return rootJoint, numJoints


# Convert units found with "currentUnit" to an fps
# Have to do it like this because for some reason fps isn't readily available to scripts
def time_unit_to_fps(unit):
    
    # Used this form post to figure out how to get fps
    # https://forums.autodesk.com/t5/maya-programming/getting-the-frames-per-second-of-a-scene/td-p/6543383
    
    match unit:
        
        case "game":
            return 15
        case "film":
            return 24
        case "pal":
            return 25
        case "ntsc":
            return 30
        case "show":
            return 48
        case "palf":
            return 50
        case "ntscf":
            return 60  
            
        case _:
            # https://www.geeksforgeeks.org/python-string-till-substring/
            return float(unit.partition("fps")[0])
        

def get_fps():
    return time_unit_to_fps(cm.currentUnit(q = True, time = True))
    
    
def get_measurement_units():
    # Gets us our cm
    return cm.currentUnit(q = True) 


def write_line(htr, line):
    htr.write(line + "\n")


def get_segment_names_and_hierarchy_htr(currentJoint) -> str:
    
    returnStr = ""
    
    if currentJoint.parent == None:
         returnStr = currentJoint.name + "\tGLOBAL\n"
    else:
        returnStr = currentJoint.name + "\t" + currentJoint.parent.name + "\n"
    
    for i in range(len(currentJoint.children)):
        returnStr += get_segment_names_and_hierarchy_htr(currentJoint.children[i])
        
    return returnStr
    
    
def get_base_position(currentJoint) -> TransformationInfo:
    
    return currentJoint.frameTransformationInfoTimeline.data[0]
    
    
def get_base_position_htr(currentJoint) -> str:
    
    returnStr = currentJoint.name + "\t" + get_base_position(currentJoint).get_htr_format() + "\n"
    
    for i in range(len(currentJoint.children)):
        returnStr += get_base_position_htr(currentJoint.children[i])
    
    return returnStr
    
    
def get_joint_timeline_data(currentJoint) -> str:
    
    returnStr = "[" + currentJoint.name + "]\n"
    returnStr += "# Tx<tab>Ty<tab>Tz<tab>Rx<tab>Ry<tab>Rz<tab>BoneScaleFactor<CR>\n"
    
    basePose = get_base_position(currentJoint)
    
    for i in range(len(currentJoint.frameTransformationInfoTimeline.data)):
        returnStr += str(i) + "\t" + (currentJoint.frameTransformationInfoTimeline.data[i] - basePose).get_htr_format() + "\n"
        
    for i in range(len(currentJoint.children)):
        returnStr += get_joint_timeline_data(currentJoint.children[i])
        
    return returnStr


def write_htr_file(rootJoint, numJoints):
    # Write to file
    htr = open("maya_export.htr", "w")
    
    write_line(htr, "# Maya Export HTR")
    
    write_line(htr, "[Header]")
    write_line(htr, "# KeyWord<space>Value<CR>")
    write_line(htr, "FileType htr")
    write_line(htr, "DataType HTRS")
    write_line(htr, "FileVersion 1")
    write_line(htr, "NumSegments " + str(numJoints))
    write_line(htr, "NumFrames " + str(get_num_frames()))
    write_line(htr, "DataFrameRate " + str(get_fps()))
    write_line(htr, "EulerRotationOrder ZYX")
    write_line(htr, "CalibrationUnits " + str(get_measurement_units()))
    write_line(htr, "RotationUnits Degrees")
    write_line(htr, "GlobalAxisofGravity Y")
    write_line(htr, "BoneLengthAxis X")
    write_line(htr, "ScaleFactor 1.00")
    
    write_line(htr, "[SegmentNames&Hierarchy]")
    write_line(htr, "# ObjectName<tab>ParentObjectName<CR>")
    
    # Found rsplit example on this form:
    # https://stackoverflow.com/questions/18731028/remove-last-instance-of-a-character-and-rest-of-a-string
    write_line(htr, get_segment_names_and_hierarchy_htr(rootJoint).rsplit("\n", 1)[0])
    
    write_line(htr, "[BasePosition]")
    write_line(htr, "# ObjectName<tab>Tx<tab>Ty<tab>Tz<tab>Rx<tab>Ry<tab>Rz<tab>BoneLength<CR>")
    write_line(htr, get_base_position_htr(rootJoint).rsplit("\n", 1)[0])
    
    write_line(htr, get_joint_timeline_data(rootJoint).rsplit("\n", 1)[0])
    
    htr.write("[EndOfFile]")
    
    htr.close()
    return



def main():
    
    rootJoint, numJoints = handle_selected_joint()
    print(rootJoint)
    
    write_htr_file(rootJoint, numJoints)


if __name__ == "__main__":
    main()
