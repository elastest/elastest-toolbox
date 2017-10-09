#!/bin/bash
function tryAdd () {
	git add .
	git diff --cached --exit-code
	return $?
}

# HARDCODED EXIT
echo 'Ignoring update submodules'
exit 0

# Pull all submodules
echo "Checking if there are changes"
cd ..
git submodule foreach git checkout master
git submodule foreach git pull

#Try add
tryAdd
ERROR=$?

if [ $ERROR -gt 0 ] ; then
	echo "Trying to commit submodules..."
	git commit -m "Update submodules"
	echo "Commited, trying to push..."
	git push https://${GIT_USERNAME}:${GIT_PASSWORD}@github.com/elastest/elastest-toolbox.git
	exit 1
else
	echo "There are not changes"
	exit 0
fi

exit 0
