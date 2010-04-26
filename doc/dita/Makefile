

USERGUIDE_VERSION_MAJOR=0.3
USERGUIDE_VERSION_MINOR=0.30

STARTER_VERSION_MAJOR=0.1
STARTER_VERSION_MINOR=0.12

JAPPCONF_STARTER=japp_starter_config.py
JAPPCONF_USERGUIDE=japp_userguide_config.py


prepare:
	-rm -fr tmp
	-mkdir tmp

# User Guide

userguide-pdf: prepare
	ant -f $$DITA_HOME/build_demo.xml -Dprompt.ditamap.filename=`pwd`/jaluino_medium_userguide.ditamap -Dprompt.output.type=pdf -Dprompt.output.directory=`pwd`/tmp -Dprompt.output.confirm=y
	mv `pwd`/tmp/jaluino_medium_userguide.pdf `pwd`/tmp/User_Guide_${USERGUIDE_VERSION_MAJOR}.pdf

userguide-html: prepare
	ant -f $$DITA_HOME/build_demo.xml -Dprompt.ditamap.filename=`pwd`/jaluino_medium_userguide.ditamap -Dprompt.output.type=web -Dprompt.output.directory=`pwd`/tmp -Dprompt.output.confirm=y

userguide-front: userguide-html
	# this page is only dedicated to website, it needs to integrate TOC
	# prepare generated TOC for web publishing
	cd ../../tools/japp && python2.5 htmlizer.py ${JAPPCONF_USERGUIDE} ../../doc/dita/tmp/toc.html
	ant -Dargs.transtype=xhtml -Doutput.dir=`pwd`/tmp -Dargs.input=`pwd`/userguide/front.xml  -Dargs.target=init -f $$DITA_HOME/build.xml dita2xhtml
	# the beauty and magic of sed :)
	cat tmp/front.html | sed -e '/Table of Content/rtmp/topublish/content' -e "s#@VERSION@#${USERGUIDE_VERSION_MINOR}#g" > tmp/front.html.toc
	mv tmp/front.html.toc tmp/front.html
	mv tmp/topublish tmp/topublish.toc
	cd ../../tools/japp && python2.5 htmlizer.py ${JAPPCONF_USERGUIDE} ../../doc/dita/tmp/front.html

publish-userguide-front: userguide-front
	cd ../../tools/japp && python2.5 publish.py ${JAPPCONF_USERGUIDE} ../../doc/dita/tmp/topublish 

upload-userguide-pdf:
	python2.5 ~/bin/googlecode_upload.py -s "Jaluino Medium user guide, version ${USERGUIDE_VERSION_MINOR}" -p jaluino -l Type-Docs -l Featured -u $$UPLOAD_USER -w $$UPLOAD_PASSWD `pwd`/tmp/User_Guide_${USERGUIDE_VERSION_MAJOR}.pdf


# Getting Started

starter-pdf: prepare
	ant -f $$DITA_HOME/build_demo.xml -Dprompt.ditamap.filename=`pwd`/jaluino_medium_getting_started.ditamap -Dprompt.output.type=pdf -Dprompt.output.directory=`pwd`/tmp -Dprompt.output.confirm=y
	mv `pwd`/tmp/jaluino_medium_getting_started.pdf `pwd`/tmp/Getting_Started_${STARTER_VERSION_MAJOR}.pdf

starter-html: prepare
	ant -f $$DITA_HOME/build_demo.xml -Dprompt.ditamap.filename=`pwd`/jaluino_medium_getting_started.ditamap -Dprompt.output.type=web -Dprompt.output.directory=`pwd`/tmp -Dprompt.output.confirm=y

starter-front: starter-html
	# this page is only dedicated to website, it needs to integrate TOC
	# prepare generated TOC for web publishing
	cd ../../tools/japp && python2.5 htmlizer.py ${JAPPCONF_STARTER} ../../doc/dita/tmp/toc.html
	ant -Dargs.transtype=xhtml -Doutput.dir=`pwd`/tmp -Dargs.input=`pwd`/starter/front.xml  -Dargs.target=init -f $$DITA_HOME/build.xml dita2xhtml
	# the beauty and magic of sed :)
	cat tmp/front.html | sed -e '/Table of Content/rtmp/topublish/content' -e "s#@VERSION@#${STARTER_VERSION_MINOR}#g" > tmp/front.html.toc
	mv tmp/front.html.toc tmp/front.html
	mv tmp/topublish tmp/topublish.toc
	cd ../../tools/japp && python2.5 htmlizer.py ${JAPPCONF_STARTER} ../../doc/dita/tmp/front.html

publish-starter-front: starter-front
	cd ../../tools/japp && python2.5 publish.py ${JAPPCONF_STARTER} ../../doc/dita/tmp/topublish 

upload-starter-pdf:
	python2.5 ~/bin/googlecode_upload.py -s "Getting Started with Jaluino, version ${STARTER_VERSION_MINOR}" -p jaluino -l Type-Docs -l Featured -u $$UPLOAD_USER -w $$UPLOAD_PASSWD `pwd`/tmp/Getting_Started_${STARTER_VERSION_MAJOR}.pdf

