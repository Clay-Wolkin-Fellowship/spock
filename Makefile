# Configurations
CONFIGS  = sample l1 bucket
include $(CONFIGS:%=conf/%.config)

# Definitions
COMMA    = ,
EMPTY    =
SPACE    = $(EMPTY) $(EMPTY)

# Related to config sizes
SAMPK  := $(shell dc --expression="$(WARM) $(SAMP) $(COOL) + + p")
L1ARGS := -o $(L1OFF) -i $(L1IDX) -w $(L1WAY)
BSIZE  := $(shell dc --expression="$(SAMP) $(BUCKETS) / p")

# Trace to use
TRACES  = $(patsubst raw/%.mtrace,%,$(wildcard raw/*.mtrace))
ifeq ($(strip $(TRACES)),)
	TRACES = $(patsubst zip/%.zmtrace,%,$(wildcard zip/*.zmtrace))
endif
REPS    = rand

ZTRACES = $(TRACES:%=zip/%.zmtrace)
SAMPLES = $(TRACES:%=build/samp/%.mtrace)
L1CACHE = $(foreach rep,$(REPS),$(TRACES:%=build/l1/%.$(rep)))
L1MATRS = $(foreach rep,$(REPS),$(TRACES:%=build/matr1/%.$(rep)))
L1MATRC = $(foreach rep,$(REPS),$(TRACES:%=build/matrc1/%.$(rep)))
L1MATRB = $(foreach rep,$(REPS),$(TRACES:%=build/matrb1/%.$(rep)))
L1BPLOT = $(foreach rep,$(REPS),$(TRACES:%=build/plotmb1/%.$(rep).png))
L1CPLOT = $(foreach rep,$(REPS),$(TRACES:%=build/plotmc1/%.$(rep).png))
L1PLOTS = $(L1BPLOT) $(L1CPLOT)

TRACE   = $(basename $(basename $(@F)))
REPL	= $(patsubst .%,%,$(suffix $(@F)))
RAW     = raw/$(TRACE).mtrace
ZIP     = zip/$(TRACE).zmtrace
SAMPLE  = build/samp/$(TRACE).mtrace
L1	= build/l1/$(@F)
L1MATR  = build/matr1/$(@F)
L1CUM   = build/matrc1/$(basename $(@F))
L1BUC	= build/matrb1/$(basename $(@F))


.SECONDARY:
.SECONDEXPANSION:

all: $(L1PLOTS)

clean:
	rm -rf build

$(ZTRACES): $$(RAW) bin/zip.sh
	@mkdir -p $(@D)
	bin/zip.sh $(TRACE)

$(SAMPLES): $$(ZIP) build/bin/sample conf/sample.config
	@mkdir -p $(@D)
	build/bin/sample $< $(SAMPN) $(SAMPK) >$@

$(L1CACHE): $$(SAMPLE) rep/$$(REPL).py build/bin/uncompress conf/l1.config
	@mkdir -p $(@D)
	build/bin/uncompress <$< | python3 rep/$(REPL).py $(L1ARGS) - $@

$(L1MATRS): $$(L1) bin/matr.py conf/sample.config
	@mkdir -p $(@D)
	bin/matr.py -w $(WARM) -s $(SAMP) -c $(COOL) $< $@

$(L1MATRC): $$(L1MATR) bin/cumstats.py
	@mkdir -p $(@D)
	bin/cumstats.py <$< >$@

$(L1MATRB): $$(L1MATR) bin/bucketstats.py conf/bucket.config
	@mkdir -p $(@D)
	bin/bucketstats.py <$< >$@ $(BSIZE)

$(L1CPLOT): $$(L1CUM) bin/simple.gplot
	@mkdir -p $(@D)
	sed 's|TRACE|$@|' bin/simple.gplot | sed 's|FILES|$<|' | gnuplot -persist

$(L1BPLOT): $$(L1BUC) bin/simple.gplot
	@mkdir -p $(@D)
	sed 's|TRACE|$@|' bin/simple.gplot | sed 's|FILES|$<|' | gnuplot -persist

bin/zip.sh: build/bin/compress

PROGS   = $(patsubst src/%.c,%,$(wildcard src/*.c))

progs: $(PROGS:%=build/bin/%)

build/obj/%.o: src/%.c
	@mkdir -p $(@D)
	gcc -c -O3 -o $@ $<

build/bin/%: build/obj/%.o
	@mkdir -p $(@D)
	gcc -O3 -o $@ $<


