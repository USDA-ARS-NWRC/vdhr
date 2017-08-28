"""
Compares IPW images to see the difference
"""
import subprocess as sp

#Path original data set
base_path = " /data/blizzard/Tuolumne/andrew_workspace/2017/data.1/"

orig = "ppt.4b"
modified  = "ppt.modified_mj"

cmd = 'demux -b 0 {0} | imgstat'.format("./ppt.4b_0052")
sp.Popen(cmd,shell=True)
