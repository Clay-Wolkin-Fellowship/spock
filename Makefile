# Configurations
CONFIGS  = sample time
include $(CONFIGS:%=conf/%.config)

# Related to config sizes
SAMPK  := $(shell dc --expression="$(WARM) $(SAMP) $(COOL) + + p")

# Trace to use
SRC	= /proj/spock
TRACES  = # $(patsubst raw/%.mtrace,%,$(wildcard raw/*.mtrace))
ifeq ($(strip $(TRACES)),)
TRACES	= sp_omp # $(patsubst zip/%.zmtrace,%,$(wildcard zip/*.zmtrace))
RAW     = $(SRC)/raw/$(TRACE).mtrace
ZIP     = $(SRC)/zip/$(TRACE).zmtrace
RTRACES = $(TRACES:%=$(SRC)/raw/%.mtrace)
ZTRACES = $(TRACES:%=$(SRC)/zip/%.zmtrace)
else
RAW     = $(SRC)/raw/$(TRACE).mtrace
ZIP     = zip/$(TRACE).zmtrace
RTRACES = $(TRACES:%=$(SRC)/raw/%.mtrace)
ZTRACES = $(TRACES:%=zip/%.zmtrace)

$(ZTRACES): $$(RAW) bin/zip.sh
endif

REPS    = $(patsubst rep/%.py,%,$(wildcard rep/*.py))
TTRS    = $(patsubst bin/ttrs/%.py,%,$(wildcard bin/ttrs/*.py))
LXS	= l1
PLTS    = $(patsubst bin/plts/%.py,%,$(wildcard bin/plts/*.py))

include $(LXS:%=conf/lx/%.config)
include $(PLTS:%=conf/plts/%.config)

l1ARGS := -o $(L1OFF) -i $(L1IDX) -w $(L1WAY)

REPTR	= $(foreach trace,$(TRACES),$(REPS:%=$(trace).%))
LXT	= $(foreach lx,$(LXS),$(TTRS:%=$(lx)/%))
LXTPL	= $(foreach lxt,$(LXT),$(PLTS:%=$(lxt)/%))

ZAMPLES = $(TRACES:%=build/zamp/%.zmtrace)
SAMPLES = $(TRACES:%=build/samp/%.mtrace)
WTIMES  = $(REPTR:%=build/time/%.time)
LXCACHE = $(foreach lx,$(LXS),$(REPTR:%=build/$(lx)/cache/repl/%.repl))
LXTS    = $(foreach lxt,$(LXT),$(REPTR:%=build/$(lxt)/src/%.ttr))
LXPLDAT = $(foreach lxtpl,$(LXTPL),$(REPTR:%=build/$(lxtpl)/%.dat))
LXPLPNG = $(foreach lxtpl,$(LXTPL),$(TRACES:%=build/$(lxtpl)/%.%.png))

TRACE   = $(basename $(basename $(@F)))
REPL	= $(patsubst .%,%,$(suffix $(basename $(@F))))
REPLIST	= $(subst -, ,$*)
SANSPLOT= $(shell dirname $(@D))
SANSTTR = $(shell dirname $(SANSPLOT))
LX	= $(shell basename $(SANSTTR))
TTR	= $(shell basename $(SANSPLOT))
PLOT	= $(shell basename $(@D))

ZAMPLE  = build/zamp/$(TRACE).zmtrace
SAMPLE  = build/samp/$(TRACE).mtrace
CACHE	= build/$(LX)/cache/repl/$(TRACE).$(REPL).repl
CACHEX	= $(LXS:%=build/%/cache/repl/$(TRACE).$(REPL).repl)
WTIME	= build/time/$(TRACE).$(REPL).time
LXTTR   = build/$(LX)/$(TTR)/src/$(TRACE).$(REPL).ttr
LXDAT	= $(REPLIST:%=build/$(LX)/$(TTR)/$(PLOT)/$(TRACE).%.dat)

LXCONF	= conf/lx/$(LX).config
DATCONF	= conf/plts/$(PLOT).config

REPPROG	= rep/$(REPL).py
WTPROG	= bin/walltime.py
TTRPROG	= bin/ttrs/$(TTR).py
DATPROG = bin/plts/$(PLOT).py
PLOTPROG= bin/plot.py

PROGS   = $(patsubst src/%.c,%,$(wildcard src/*.c))

OUTPUT  = belady fifo srrip drrip brrip rand nru_rand belady-rand-srrip-drrip-brrip
OUTPUTS = $(foreach lxtpl,$(LXTPL),$(foreach trace,$(TRACES),$(OUTPUT:%=build/$(lxtpl)/$(trace).%.png)))

.SECONDEXPANSION:

all: $(OUTPUTS)

clean:
	rm -rf build

$(ZTRACES):
	@mkdir -p $(@D)
	bin/zip.sh $(TRACE)
	@echo "Created $@"

$(ZAMPLES): build/bin/sample conf/sample.config $$(ZIP)
	@mkdir -p $(@D)
	build/bin/sample $(ZIP) $(SAMPN) $(SAMPK) >$@
	@echo "Created $@"

$(SAMPLES): build/bin/uncompress $$(ZAMPLE)
	@mkdir -p $(@D)
	build/bin/uncompress <$(ZAMPLE) >$@
	@echo "Created $@"

$(LXCACHE): $$(REPPROG) $$(LXCONF) $$(SAMPLE)
	@mkdir -p $(@D)
	python3 $(REPPROG) $($(LX)ARGS) $(SAMPLE) $@
	@echo "Created $@"

$(WTIMES): $(WTPROG) $$(SAMPLE) $$(CACHEX)
	@mkdir -p $(@D)
	python3 $(WTPROG) $(DELAY:%=-d %) $(SAMPLE) $(CACHEX) >$@
	@echo "Created $@"

$(LXTS): $$(TTRPROG) $$(LXCONF) $$(CACHE) $$(WTIME)
	@mkdir -p $(@D)
	python3 $(TTRPROG) -w $(WARM) -s $(SAMP) -c $(COOL) $(CACHE) $@ $(WTIME)
	@echo "Created $@"

$(LXPLDAT): $$(DATPROG) $$(DATCONF) $$(LXTTR)
	@mkdir -p $(@D)
	python3 $(DATPROG) $($(PLOT)ARGS) <$(LXTTR) >$@
	@echo "Created $@"

$(LXPLPNG): $(PLOTPROG) $$(LXDAT)
	@mkdir -p $(@D)
	python3 $(PLOTPROG) "$(PLOT) $(TTR)" $@ $(LXDAT)
	@echo "Created $@"

progs: $(PROGS:%=build/bin/%)

build/obj/%.o: src/%.c
	@mkdir -p $(@D)
	gcc -c -O3 -o $@ $<
	@echo "Created $@"

build/bin/%: build/obj/%.o
	@mkdir -p $(@D)
	gcc -O3 -o $@ $<
	@echo "Created $@"

