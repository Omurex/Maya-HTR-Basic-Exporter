import os
import TestImport

htr = open("TestFile.htr", "w")
htr.write("Hello World!\n")
htr.write("New Line?")
#print(os.path.dirname(os.path.realpath(__file__)))
print(os.path.abspath(''))

TestImport.another_fn()

htr.close()



