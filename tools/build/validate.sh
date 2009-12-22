#!/bin/bash

start_time=`date +%s`

export JALUINO_ROOT=`pwd`	# correct when set by buildbot
##export JALUINO_ROOT=`pwd`/../..	# run manually here
export JALUINO_LIB=$JALUINO_ROOT/lib
export JALUINO_SAMPLEDIR=$JALUINO_ROOT/samples

JALUINO_TMP=$JALUINO_ROOT/tmp
mkdir -p $JALUINO_TMP

jalsamples=`find $JALUINO_SAMPLEDIR -name \*.jal -type f`
jallibs=`find $JALUINO_LIB -name \*.jal -type f`

echo `echo $jalsamples | sed "s#\.jal #.jal\n#g" | wc -l` samples to validate...
echo `echo $jallibs | sed "s#\.jal #.jal\n#g" | wc -l` libraries to validate...

at_least_one_failed=0
counter=0

echo "" > $JALUINO_TMP/validate.out
echo "" > $JALUINO_TMP/validate.failed

for jalfile in `echo $jalsamples $jallibs`
do
	##echo -n file: $jalfile... 
	$JALLIB_PYTHON $JALUINO_ROOT/3rdparty/jallib_svn/tools/jallib.py validate $jalfile > $JALUINO_TMP/tmpval.out 2>&1 
	if [ "$?" != "0" ]
	then
		echo -- jsg output -- >> $JALUINO_TMP/validate.out
		cat $JALUINO_TMP/tmpval.out >> $JALUINO_TMP/validate.out
		echo -- -- -- >> $JALUINO_TMP/validate.out
		echo >> $JALUINO_TMP/validate.out
		echo `basename $jalfile` >> $JALUINO_TMP/validate.failed
		at_least_one_failed=1
		counter=`expr $counter + 1`		
	fi
done

if [ "$counter" = "0" ]
then
	echo "All files validated :)"
else
	echo "$counter files can't be validated..."
	echo List:
	cat $JALUINO_TMP/validate.failed
	echo
	echo
	echo Details:
	cat $JALUINO_TMP/validate.out
	echo
fi

echo "Environment config"
echo JALUINO_ROOT=$JALUINO_ROOT
echo JALUINO_LIB=$JALUINO_LIB
echo JALUINO_SAMPLEDIR=$JALUINO_SAMPLEDIR
echo JALLIB_JALV2=$JALLIB_JALV2
echo JALLIB_PYTHON=$JALLIB_PYTHON
echo
end_time=`date +%s`
seconds=`expr $end_time - $start_time`
echo "Time duration: $seconds secs"



rm -f $JALUINO_TMP/validate.out
exit $at_least_one_failed
