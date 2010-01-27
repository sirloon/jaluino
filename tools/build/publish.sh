#!/bin/bash

# this script automatically publish DITA files to the website. It uses 
# TOPUBLISH file registering what should go to the website. This scripts
# works incrementally: it doesn't publish *every* DITA files each time 
# TOPUBLISH has been modified, instead it uses SVN diff action to know
# which lines have changed. To do this, a revision number is stored in
# a file, this is last revision on which this script successfully run.

start_time=`date +%s`

# when run by buildbot
export JALUINO_ROOT=`pwd`
export JALUINO_DITA=$JALUINO_ROOT/doc/dita
export JALUINO_TOOLS=$JALUINO_ROOT/tools
export JALUINO_TOPUBLISH=$JALUINO_DITA/TOPUBLISH


### when run manually
##export JALUINO_ROOT=`pwd`/../..
##export JALUINO_DITA=$JALUINO_ROOT/doc/dita
##export JALUINO_TOOLS=$JALUINO_ROOT/tools
##export JALUINO_TOPUBLISH=$JALUINO_DITA/TOPUBLISH


JALUINO_TMP=$JALUINO_ROOT/tmp
mkdir -p $JALUINO_TMP

# sanity check
if ! test -s "$JALUINO_LASTREVFILE"
then
   echo "Last revision file $JALUINO_LASTREVFILE does not exist or is empty."
   echo "Please specify a revision from which DITA files should be considered"
   echo "in incremental publication"
   exit 255
fi

# extracting changed lines 
svncmd="svn info $JALUINO_TOPUBLISH"
echo "$svncmd"
LANG=C $svncmd
reposrev=`LANG=C $svncmd | grep ^Revision: | sed "s#Revision:##" | sed "s# ##g"`
lastrev=`cat $JALUINO_LASTREVFILE`
at_least_one_failed=0
counter=0
# replace spaces on the fly to read whole line by whole line...
svncmd="svn diff -x -b -r$lastrev:$reposrev $JALUINO_TOPUBLISH"
###svncmd="svn diff -x -b -r$lastrev $JALUINO_TOPUBLISH"
echo $svncmd
for file in `cat <($svncmd | grep "^+" | grep -v -e "^+#" -e "^+[[:space:]]*$" -e "^+++" | sed "s# \|\t#___#g")`
do
   pushd $JALUINO_TOOLS/japp

   cmdline=`echo $file | sed "s#^+##" | sed "s#___# #g" `
   dita=`echo $cmdline | awk '{print $1}'`
   conf=`echo $cmdline | awk '{print $2}'`
   basedita=`basename $dita`
   # let's publish...
   ismap=`echo $dita | grep -c "\.ditamap\$"`
   if [ "$ismap" = "0" ]
   then
      echo
      echo Publishing $basedita using $conf configuration
      echo 
      echo $dita | ./japp.sh $conf
      # pipe: exit code is from the right side, this is what we want
      if [ "$?" != "0" ]
      then
         echo "Failed to publish $basedita" >> $JALUINO_TMP/publish.failed
         at_least_one_failed=1
         counter=`expr $counter + 1`
      fi
   else
      echo
      echo Publishing ditamap $basedita using $conf configuration
      echo
      if ! test -s "$JAPP_DITAMAP_SCRIPT"
      then
         echo "Can't find script defined in JAPP_DITAMAP_SCRIPT"
         exit 255
      fi
	  # black magic...
      JAPPCONF=$conf $JAPP_DITAMAP_SCRIPT
      if [ "$?" != "0" ]
      then
         echo "Failed to publish ditamap $basedita" >> $JALUINO_TMP/publish.failed
         at_least_one_failed=1
         counter=`expr $counter + 1`
      fi
   fi

   popd
done

if [ "$counter" = "0" ]
then
   echo "All new DITA documents published :)"
else
   echo "$counter DITA documents can't be published"
   echo "List:"
   cat $JALUINO_TMP/publish.failed
fi

rm -fr $JALUINO_TMP
echo $reposrev > $JALUINO_LASTREVFILE

end_time=`date +%s`
seconds=`expr $end_time - $start_time`
echo "Time duration: $seconds secs"

exit $at_least_one_failed
