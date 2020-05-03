all: fxs
.PHONY: all

# Include standard NCS examples build definitions and rules
include $(NCS_DIR)/src/ncs/build/include.ncs.mk

SRC  = $(wildcard yang/*.yang)
DIRS = ../load-dir
FXS = $(SRC:yang/%.yang=../load-dir/%.fxs)

YANGPATH += ../../ftdv-ngfw/src/yang  
YANGPATH += ../../cisco-etsi-nfvo/src/yang 
YANGPATH += ../../service-base/src/yang 

NCSCPATH   = $(YANGPATH:%=--yangpath %)
YANGERPATH = $(YANGPATH:%=--path %)
PYTHONSRC = $(wildcard ../python/itd-service/*.py)
PYTHONBUILD = $(wildcard ../python/itd-service/*.pyc)
TEMPLATESRC = $(wildcard loaddata/*.xml)

fxs: $(PYTHONSRC) $(PYTHONBUILD) $(DIRS) $(FXS) $(TEMPLATESRC)

$(PYTHONSRC): .FORCE
	python -m py_compile $@
.PHONY: .FORCE
$(PYTHONBUILD): .FORCE2
	rm -f $@
.PHONY: .FORCE2

$(DIRS):
	mkdir -p $@

../load-dir/%.fxs: yang/%.yang
	$(NCSC)  `ls $*-ann.yang  > /dev/null 2>&1 && echo "-a $*-ann.yang"` \
            $(NCSCPATH) -c -o $@ $<

$(TEMPLATESRC): .FORCE
	cp $@ ../load-dir

clean:
	rm -rf $(DIRS)
.PHONY: clean

