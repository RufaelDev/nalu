ifeq ($(OS),Windows_NT)
	CUR_DIR = $(shell cd)
	PYTHON=python
	PIP=python -m pip
	SHELL=cmd
	CMD_SEPARATOR=&
	VENV_ACTIVATE=.\env\Scripts\activate
	NALU_WHEEL=nalu --no-index --find-links=${CUR_DIR}\dist 
	RM=- rmdir /S /Q
	MAKE=make.exe

env/bin/activate:
	IF NOT EXIST env ${PYTHON} -m venv env ${CMD_SEPARATOR} \
	${VENV_ACTIVATE} ${CMD_SEPARATOR} \
	${PIP} install --upgrade pip ${CMD_SEPARATOR} \
	${PIP} install -Ur requirements.txt

# Launching html page at the end. This could give problems
# if running this on headless systems, but on Windows 
# this should never be the case, this is for developers
# not for CI.
test: install-nalu test-headless

else
	CUR_DIR = $(shell pwd)
	PYTHON=python3
	PIP=pip3
	CMD_SEPARATOR=;
	VENV_ACTIVATE=. ./env/bin/activate
	NALU_WHEEL=nalu --no-index --find-links=${CUR_DIR}/dist
	RM=rm -rf

env/bin/activate:
	test -d env || ${PYTHON} -m venv env ${CMD_SEPARATOR} \
	${VENV_ACTIVATE} ${CMD_SEPARATOR} \
	${PIP} install --upgrade pip ${CMD_SEPARATOR} \
	${PIP} install -Ur requirements.txt

test: install-nalu test-headless

endif

SRC = src/nalu/*.py

all: dist

.PHONY: env release-version

env: env/bin/activate

test-headless: env
	${VENV_ACTIVATE} ${CMD_SEPARATOR} \
	coverage run -m pytest 
    ${VENV_ACTIVATE} ${CMD_SEPARATOR} \
    coverage report --include=src/* ${CMD_SEPARATOR} \
    coverage html --include=src/*

release-version:
	git describe --tags > RELEASE-VERSION

dist: $(SRC) release-version env
	${VENV_ACTIVATE} ${CMD_SEPARATOR} \
	${PIP} install wheel ${CMD_SEPARATOR} \
	${PYTHON} setup.py bdist_wheel --universal

install-nalu: env dist
	${VENV_ACTIVATE} ${CMD_SEPARATOR} \
	${PIP} uninstall -y nalu ${CMD_SEPARATOR} \
	${PIP} install --no-cache-dir ${NALU_WHEEL}


ifneq ($(OS),Windows_NT)
# Assumes you have a correctly configured ~/.pypirc file, see
# https://gitlab.internal.unified-streaming.com/operations/base-images/validator-cli
upload: clean dist
	${PYTHON} -m venv env ;\
	. env/bin/activate ;\
	${PIP} install --upgrade pip ;\
	${PIP} install twine; \
	twine upload --repository gitlab.internal dist/*
endif

clean:
	${RM} dist
	${RM} env
