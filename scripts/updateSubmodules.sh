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
ERROR=$(tryAdd)

if [ $ERROR -gt 0 ] ; then
	echo "There are not changes"
	exit 0
else
	echo "Trying to push submodules"
	git commit -m "Update submodules"
	git push origin master
	git push https://${GIT_USERNAME}:${GIT_PASSWORD}@github.com/elastest/elastest-toolbox.git
	exit 1
fi

exit 0
