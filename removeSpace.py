import os
import glob   


path       = "hardmaru_data_files"  
files_name = "*.txt"  
os.chdir(path)

files=glob.glob(files_name)

for file in files:     
    new_file_name = file.replace(" ", "").replace("~","-")
    print(new_file_name)
    # input("Press Enter to continue...")
    os.rename(file,new_file_name)