#!/bin/bash
function tryAdd () {
	git add .
	git diff --cached --exit-code
	return $?
}


# Pull all submodules
echo "Checking if there are changes"
cd ..
git submodule foreach git checkout master
git submodule foreach git pull

#Try add
tryAdd
ERROR=$?

if [ $ERROR -gt 0 ] ; then
	echo "Trying to push submodules"
	git commit -m "Update submodules"
	git push https://${GIT_USERNAME}:${GIT_PASSWORD}@github.com/elastest/elastest-toolbox.git origin master
	exit 1
else
	echo "There are not changes"
	exit 0
fi

exit 0
