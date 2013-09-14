# Configurations
CONFIGS  = sample l1 bucket time
include $(CONFIGS:%=conf/%.config)

# Related to config sizes
SAMPK  := $(shell dc --expression="$(WARM) $(SAMP) $(COOL) + + p")
l1ARGS := -o $(L1OFF) -i $(L1IDX) -w $(L1WAY)
BSIZE  := $(shell dc --expression="$(SAMP) $(BUCKETS) / p")
ZBSIZE := $(shell dc --expression="$(ZOOMED) $(BUCKETS) / p")

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

REPS    = fifo belady # rand lru nru_rand mru brrip drrip srrip # $(patsubst rep/%.py,%,$(wildcard rep/*.py))
TTRS    = matr mmtr wttr
LXS	= l1
PLTS    = cum

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
WTIME	= build/time/$(TRACE).$(REPL).time
LXTTR   = build/$(LX)/$(TTR)/src/$(TRACE).$(REPL).ttr
LXDAT	= $(REPLIST:%=build/$(LX)/$(TTR)/$(PLOT)/$(TRACE).%.dat)

LXCONF	= conf/$(LX).config

REPPROG	= rep/$(REPL).py
WTPROG	= rep/walltime.py
TTRPROG	= bin/$(TTR).py
DATPROG = bin/$(PLOT).py
PLOTPROG= bin/plot.py

PROGS   = $(patsubst src/%.c,%,$(wildcard src/*.c))

OUTPUT  = belady-fifo
OUTPUTS = $(foreach lxtpl,$(LXTPL),$(foreach trace,$(TRACES),$(OUTPUT:%=build/$(lxtpl)/$(trace).%.png)))

.SECONDEXPANSION:
.SECONDARY:

all: $(OUTPUTS)

clean:
	rm -rf build

$(ZTRACES):
	@mkdir -p $(@D)
	bin/zip.sh $(TRACE)

$(ZAMPLES): $$(ZIP) build/bin/sample conf/sample.config
	@mkdir -p $(@D)
	build/bin/sample $(ZIP) $(SAMPN) $(SAMPK) >$@

$(SAMPLES): $$(ZAMPLE) build/bin/uncompress
	@mkdir -p $(@D)
	build/bin/uncompress <$(ZAMPLE) >$@

$(LXCACHE): $$(SAMPLE) $$(REPPROG) $$(LXCONF)
	@mkdir -p $(@D)
	python3 $(REPPROG) $($(LX)ARGS) $(SAMPLE) $@

$(WTIMES): $(WTPROG) $$(SAMPLE) $(LXS:%=build/%/cache/repl/$$(TRACE).$$(REPL).repl) 
	@mkdir -p $(@D)
	python3 $(WTPROG) $(DELAY:%=-d %) $(SAMPLE) $(LXS:%=build/%/cache/repl/$(TRACE).$(REPL).repl) >$@

$(LXTS): $$(CACHE) $$(TTRPROG) $$(LXCONF)
	@mkdir -p $(@D)
	$(TTRPROG) -w $(WARM) -s $(SAMP) -c $(COOL) $< $@ $(WTIME)

$(LXPLDAT): $$(DATPROG) $$(LXTTR)
	@mkdir -p $(@D)
	$(DATPROG) <$(LXTTR) >$@

$(LXPLPNG): $(PLOTPROG) $$(LXDAT)
	@mkdir -p $(@D)
	python3 $(PLOTPROG) "$(PLOT) $(TTR)" $@ $(LXDAT)

progs: $(PROGS:%=build/bin/%)

build/obj/%.o: src/%.c
	@mkdir -p $(@D)
	gcc -c -O3 -o $@ $<

build/bin/%: build/obj/%.o
	@mkdir -p $(@D)
	gcc -O3 -o $@ $<

