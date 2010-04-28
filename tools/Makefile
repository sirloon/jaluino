# Title: Makefile to handle common task
# Author: Sebastien Lelong, Copyright (c) 2008, all rights reserved.
# Adapted by:
# 
# This file is part of jallib (http://jallib.googlecode.com)
# Released under the BSD license (http://www.opensource.org/licenses/bsd-license.php)
#
#


all : clean test

WEEKLYBUILDCODENAME=bee
VERSION=dev
SAMPLIR_DIR=../samples
TEST_DIR=../tests
INCLUDE_DIR=../lib
JALV2_BIN := $(shell pwd)/distrib/jallib-export/compiler/jalv2
JALV2_VERSION := `${JALV2_BIN} | sed "s\#.*jal \(.*\) (.*\#\1\#"`
JALLIB_ROOT=../3rdparty/jallib_svn


clean :
	# clean what jal produces
	find ${SAMPLIR_DIR} -name \*.cod -exec rm {} \;
	find ${SAMPLIR_DIR} -name \*.lst -exec rm {} \;
	find ${SAMPLIR_DIR} -name \*.hex -exec rm {} \;
	find ${SAMPLIR_DIR} -name \*.err -exec rm {} \;
	find ${SAMPLIR_DIR} -name \*.obj -exec rm {} \;
	find ${SAMPLIR_DIR} -name \*.asm -exec rm {} \;
	find ${TEST_DIR} -name \*.cod -exec rm {} \;
	find ${TEST_DIR} -name \*.lst -exec rm {} \;
	find ${TEST_DIR} -name \*.hex -exec rm {} \;
	find ${TEST_DIR} -name \*.err -exec rm {} \;
	find ${TEST_DIR} -name \*.obj -exec rm {} \;
	find ${TEST_DIR} -name \*.asm -exec rm {} \;
	# clean python bytecode
	find ./ -name \*.pyc -exec rm {} \;
	# clean distrib dir
	-rm -fr distrib
	# tmp build dir
	-rm -fr build/tmp
		
test :
	# run testsuite

compile:
	for f in `find ${SAMPLIR_DIR} -name \*.jal`; \
	do \
		${JALLIB_ROOT}/compiler/jalv2 -s "../lib;`find ${JALLIB_ROOT}/include -type d | grep -v \\\.svn | tr '\n' ';'`" $$f | grep '^0 errors' && true || ( echo problem with $$f && exit 255; ) \
	done 

jsg:
	for f in `find ${SAMPLIR_DIR} -name \*.jal`; \
	do \
		python2.5 ${JALLIB_ROOT}/tools/jallib.py validate $$f ;\
	done 
	for f in `find ${INCLUDE_DIR} -name \*.jal`; \
	do \
		python2.5 ${JALLIB_ROOT}/tools/jallib.py validate $$f ;\
	done 

doc:
	./jalapi_generate.sh ..


export:
	# prepare distrib dir
	mkdir distrib
	mkdir distrib/jaluino-${VERSION}
	# generate VERSION file for each
	echo ${VERSION} > distrib/jaluino-${VERSION}/VERSION
	# get clean source from repos
	# (svn export gets the sources, but without any .svn dir (no svn metadata)
	svn export http://jaluino.googlecode.com/svn/trunk distrib/jaluino-export

prepare:
	# process 2 TORELEASE files:
	#  1. jaluino TORELEASE
	cd  distrib/jaluino-export && cat TORELEASE | sed "s#\r##" | grep -v ^\# | tar cfv - -T - | tar xfv - -C ../jaluino-${VERSION}
	#  2. part of jallib TORELEASE
	for f in `cat distrib/jaluino-export/3rdparty/jallib_svn/TORELEASE | sed "s#\r##" | grep ^include | grep -v ^include\/device`; \
	do \
		cp distrib/jaluino-export/3rdparty/jallib_svn/$$f distrib/jaluino-${VERSION}/lib ;\
	done
	# manually add needed device files
	cp distrib/jaluino-export/3rdparty/jallib_svn/include/device/18f4550.jal distrib/jaluino-${VERSION}/lib
	cp distrib/jaluino-export/3rdparty/jallib_svn/include/device/chipdef_jallib.jal distrib/jaluino-${VERSION}/lib
	# same for some python libs
	-mkdir -p distrib/jaluino-${VERSION}/tools
	cp distrib/jaluino-export/3rdparty/jallib_svn/tools/jallib.py distrib/jaluino-${VERSION}/tools
	# get compiler from jallib
	cd distrib/jaluino-export/3rdparty/jallib_svn/ && tar cfv - compiler | tar xfv - -C ../../../jaluino-${VERSION}
	# TODO: wait for a jalapi DITA integration
	echo DONE: release directory distrib/jaluino-${VERSION}

archive:
	cd distrib && tar czfv jaluino-${VERSION}.tar.gz jaluino-${VERSION}
	# ZIPs don't contain a base directory
	cd distrib/jaluino-${VERSION} && zip -r jaluino-${VERSION}.zip . && mv jaluino-${VERSION}.zip ..

check:
	sh distrib/jaluino-export/3rdparty/jallib_svn/tools/check_package.sh distrib/jaluino-${VERSION}/lib distrib/jaluino-${VERSION}/samples distrib/jaluino-${VERSION}/compiler/jalv2

dita:
	-mkdir -p distrib/jaluino-${VERSION}/doc/pdf
	-mkdir -p distrib/jaluino-${VERSION}/doc/html/user_guide
	-mkdir -p distrib/jaluino-${VERSION}/doc/html/getting_started
	-mkdir -p distrib/jaluino-${VERSION}/doc/html/shields
	# PDF
	cd distrib/jaluino-export/doc/dita && make userguide-pdf && cp tmp/User_Guide_*.pdf ../../../jaluino-${VERSION}/doc/pdf/
	cd distrib/jaluino-export/doc/dita && make starter-pdf && cp tmp/Getting_Started_*.pdf ../../../jaluino-${VERSION}/doc/pdf/
	cd distrib/jaluino-export/doc/dita && make shields-pdf && cp tmp/Jaluino_Shields_*.pdf ../../../jaluino-${VERSION}/doc/pdf/
	# HTML
	cd distrib/jaluino-export/doc/dita && make userguide-html && cp -r tmp/* ../../../jaluino-${VERSION}/doc/html/user_guide
	cd distrib/jaluino-export/doc/dita && make starter-html && cp -r tmp/* ../../../jaluino-${VERSION}/doc/html/getting_started
	cd distrib/jaluino-export/doc/dita && make shields-html && cp -r tmp/* ../../../jaluino-${VERSION}/doc/html/shields

ide:
	cd ../ide/plugins/Jaluino && python setup.py bdist_egg --dist-dir ../

release: export prepare dita archive check

api_svn:
	# generate XML API file for all jallib/jaluino libraries
	for i in `../bin/jaluino_svn list`; \
	do \
		../bin/jaluino_svn api -x $$i | grep -v \?xml; \
	done > /tmp/jaluino_api_tmp.xml
	echo \<apis\> | cat - /tmp/jaluino_api_tmp.xml > ../ide/conf/jaluino_api.xml
	echo \</apis\> >> ../ide/conf/jaluino_api.xml
	rm /tmp/jaluino_api_tmp.xml
