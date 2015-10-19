#coding=utf8
import os

root_path = r'./'

pyqt_path = r'C:\MyProgram\Anaconda\Lib\site-packages\PyQt4\uic\pyuic.py'

print("complie *.ui into python code")
input("continue ...")

n = 0
try:
    for f in os.listdir(root_path):
        f_parts = os.path.splitext(f)
        if f_parts and f_parts[1] == r'.ui':
            print(f)
            cmd_str = r'python %s -o ui_%s.py %s' % (pyqt_path, f_parts[0], f)
            os.system(cmd_str)
            n += 1

except Exception as e:
    print(e)

input('%d ui files finish ...' % n)