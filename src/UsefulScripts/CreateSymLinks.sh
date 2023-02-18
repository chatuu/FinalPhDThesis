#! /bin/bash

####################################################################
#                                                                  #     
#  Author       : Chatura Kuruppu                                  #     
#  Email        : ckuruppu@fnal.gov                                #     
#  Date Created : 2022-02-04                                       #     
#  Comments     : The purpose of creating this file is to quickly  #         
#                 create necessary symbolic links to the useful    #         
#                 scripts.                                         # 
#                                                                  #     
####################################################################
tput bold
tput setaf 3
thesisLoc=/Users/ckuruppu/Documents/NewThesis
loc=$PWD
echo "Creating Symbolic links..!"

declare -a fileList=("headers.py"
	"functions.py"
	"classes.py")

for i in "${fileList[@]}"; do
    ln -s $thesisLoc/src/UsefulScripts/$i $loc
    if test -f "$loc/$i"; then
        tput setaf 2
        echo "symbolic link for $i created at $loc/..!"
    else
        tput setaf 1
        echo "unable to create symbolic link for $i at $loc/..!"
    fi
done
rm -f CreateSymLinks.sh
tput setaf 5
echo "CreateSymLinks.sh file deleted successfully..!"