#!/bin/bash

export JALUINO_ROOT=`pwd`	# correct when set by buildbot
##export JALUINO_ROOT=`pwd`/../..	# run manually here
# This one is to use jallib.py over jaluino repository
export JALLIB_REPOS="$JALUINO_ROOT/3rdparty/jallib_svn/include:$JALUINO_ROOT/lib"
export JALUINO_SAMPLEDIR=$JALUINO_ROOT/samples

JALUINO_TMP=$JALUINO_ROOT/tmp
mkdir -p $JALUINO_TMP

jalsamples=`find $JALUINO_SAMPLEDIR -name \*.jal -type f`
echo `echo $jalsamples | sed "s#\.jal #.jal\n#g" | wc -l` samples to compile...

at_least_one_failed=0
counter=0

echo "" > $JALUINO_TMP/compile.out
echo "" > $JALUINO_TMP/compile.failed

for sample in $jalsamples
do
	$JALLIB_PYTHON $JALUINO_ROOT/3rdparty/jallib_svn/tools/jallib.py compile $sample > $JALUINO_TMP/tmpcomp.out 2>&1 
	if [ "$?" != "0" ]
	then
		echo sample: $sample ... Failed >> $JALUINO_TMP/compile.out
		echo -- jalv2 output -- >> $JALUINO_TMP/compile.out
		cat $JALUINO_TMP/tmpcomp.out >> $JALUINO_TMP/compile.out
		echo -- -- -- >> $JALUINO_TMP/compile.out
		echo `basename $sample` >> $JALUINO_TMP/compile.failed
		at_least_one_failed=1
		counter=`expr $counter + 1`
	fi
done

if [ "$counter" = "0" ]
then
	echo "All samples compile :)"
else
	echo "$counter samples can't be compiled..."
	echo List:
	cat $JALUINO_TMP/compile.failed
	echo
	echo
	echo Details:
	cat $JALUINO_TMP/compile.out
	echo
fi

echo JALUINO_ROOT=$JALUINO_ROOT
echo JALLIB_REPOS=$JALLIB_REPOS
echo JALUINO_SAMPLEDIR=$JALUINO_SAMPLEDIR
echo JALLIB_JALV2=$JALLIB_JALV2
echo JALLIB_PYTHON=$JALLIB_PYTHON



rm -f $JALUINO_TMP/compile.out
exit $at_least_one_failed
