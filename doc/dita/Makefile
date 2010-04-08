

USERGUIDE_VERSION=0.2
STARTER_VERSION=0.1

JAPPCONF_STARTER=japp_starter_config.py
JAPPCONF_USERGUIDE=japp_userguide_config.py


prepare:
	-rm -fr tmp
	-mkdir tmp

# User Guide

userguide-pdf: prepare
	ant -f $$DITA_HOME/build_demo.xml -Dprompt.ditamap.filename=`pwd`/jaluino_medium_userguide.ditamap -Dprompt.output.type=pdf -Dprompt.output.directory=`pwd`/tmp -Dprompt.output.confirm=y
	mv `pwd`/tmp/jaluino_medium_userguide.pdf `pwd`/tmp/User_Guide_${USERGUIDE_VERSION}.pdf

userguide-html: prepare
	ant -f $$DITA_HOME/build_demo.xml -Dprompt.ditamap.filename=`pwd`/jaluino_medium_userguide.ditamap -Dprompt.output.type=web -Dprompt.output.directory=`pwd`/tmp -Dprompt.output.confirm=y

userguide-front: userguide-html
	# this page is only dedicated to website, it needs to integrate TOC
	# prepare generated TOC for web publishing
	cd ../../tools/japp && python2.5 htmlizer.py ${JAPPCONF_USERGUIDE} ../../doc/dita/tmp/toc.html
	ant -Dargs.transtype=xhtml -Doutput.dir=`pwd`/tmp -Dargs.input=`pwd`/mainboard/front.xml  -Dargs.target=init -f $$DITA_HOME/build.xml dita2xhtml
	# the beauty and magic of sed :)
	cat tmp/front.html | sed -e '/Table of Content/rtmp/topublish/content' -e "s#@VERSION@#${USERGUIDE_VERSION}#g" > tmp/front.html.toc
	mv tmp/front.html.toc tmp/front.html
	mv tmp/topublish tmp/topublish.toc
	cd ../../tools/japp && python2.5 htmlizer.py ${JAPPCONF_USERGUIDE} ../../doc/dita/tmp/front.html

publish-userguide-front: userguide-front
	cd ../../tools/japp && python2.5 publish.py ${JAPPCONF_USERGUIDE} ../../doc/dita/tmp/topublish 

# Getting Started

starter-pdf: prepare
	ant -f $$DITA_HOME/build_demo.xml -Dprompt.ditamap.filename=`pwd`/jaluino_medium_getting_started.ditamap -Dprompt.output.type=pdf -Dprompt.output.directory=`pwd`/tmp -Dprompt.output.confirm=y
	mv `pwd`/tmp/jaluino_medium_getting_started.pdf `pwd`/tmp/Getting_Started_${STARTER_VERSION}.pdf

starter-html: prepare
	ant -f $$DITA_HOME/build_demo.xml -Dprompt.ditamap.filename=`pwd`/jaluino_medium_getting_started.ditamap -Dprompt.output.type=web -Dprompt.output.directory=`pwd`/tmp -Dprompt.output.confirm=y

starter-front: starter-html
	# this page is only dedicated to website, it needs to integrate TOC
	# prepare generated TOC for web publishing
	cd ../../tools/japp && python2.5 htmlizer.py ${JAPPCONF_STARTER} ../../doc/dita/tmp/toc.html
	ant -Dargs.transtype=xhtml -Doutput.dir=`pwd`/tmp -Dargs.input=`pwd`/starter/front.xml  -Dargs.target=init -f $$DITA_HOME/build.xml dita2xhtml
	# the beauty and magic of sed :)
	cat tmp/front.html | sed -e '/Table of Content/rtmp/topublish/content' -e "s#@VERSION@#${STARTER_VERSION}#g" > tmp/front.html.toc
	mv tmp/front.html.toc tmp/front.html
	mv tmp/topublish tmp/topublish.toc
	cd ../../tools/japp && python2.5 htmlizer.py ${JAPPCONF_STARTER} ../../doc/dita/tmp/front.html

publish-starter-front: starter-front
	cd ../../tools/japp && python2.5 publish.py ${JAPPCONF_STARTER} ../../doc/dita/tmp/topublish 

