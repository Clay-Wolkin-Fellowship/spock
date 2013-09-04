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
ZBSIZE := $(shell dc --expression="$(ZOOMED) $(BUCKETS) / p")

# Trace to use
TRACES  = sp_omp # $(patsubst raw/%.mtrace,%,$(wildcard raw/*.mtrace))
ifeq ($(strip $(TRACES)),)
	TRACES = $(patsubst zip/%.zmtrace,%,$(wildcard zip/*.zmtrace))
endif
REPS    = fifo belady rand lru nru_rand mru brrip drrip srrip

RTRACES = $(TRACES:%=raw/%.mtrace)
ZTRACES = $(TRACES:%=zip/%.zmtrace)
ZAMPLES = $(TRACES:%=build/zamp/%.zmtrace)
SAMPLES = $(TRACES:%=build/samp/%.mtrace)
L1CACHE = $(foreach rep,$(REPS),$(TRACES:%=build/l1/%.$(rep)))
L1MATRS = $(foreach rep,$(REPS),$(TRACES:%=build/matr1/%.$(rep)))
L1MATRC = $(foreach rep,$(REPS),$(TRACES:%=build/matrc1/%.$(rep)))
L1MATRB = $(foreach rep,$(REPS),$(TRACES:%=build/matrb1/%.$(rep)))
L1MATRZ = $(foreach rep,$(REPS),$(TRACES:%=build/matrz1/%.$(rep)))
L1BPLOT = $(foreach rep,$(REPS),$(TRACES:%=build/plotmb1/%.$(rep).png))
L1CPLOT = $(foreach rep,$(REPS),$(TRACES:%=build/plotmc1/%.$(rep).png))
L1ZPLOT = $(foreach rep,$(REPS),$(TRACES:%=build/plotmz1/%.$(rep).png))
L1LPLOT = $(foreach rep,$(REPS),$(TRACES:%=build/plotml1/%.$(rep).png))
L1PLOTS = $(L1BPLOT) $(L1CPLOT) $(L1ZPLOT) $(L1LPLOT)

TRACE   = $(basename $(basename $(@F)))
REPL	= $(patsubst .%,%,$(suffix $(@F)))
RAW     = raw/$(TRACE).mtrace
ZIP     = zip/$(TRACE).zmtrace
ZAMPLE  = build/zamp/$(TRACE).zmtrace
SAMPLE  = build/samp/$(TRACE).mtrace
L1	= build/l1/$(@F)
L1MATR  = build/matr1/$(@F)
L1CUM   = build/matrc1/$(basename $(@F))
L1BUC	= build/matrb1/$(basename $(@F))
L1ZBUC	= build/matrz1/$(basename $(@F))
L1CBEL  = build/matrc1/$(TRACE).belady
L1BBEL  = build/matrb1/$(TRACE).belady
L1ZBEL  = build/matrz1/$(TRACE).belady

.SECONDEXPANSION:
.SECONDARY:

all: $(L1PLOTS)

clean:
	rm -rf build

$(ZTRACES): $$(RAW) bin/zip.sh
	@mkdir -p $(@D)
	bin/zip.sh $(TRACE)

$(ZAMPLES): $$(ZIP) build/bin/sample conf/sample.config
	@mkdir -p $(@D)
	build/bin/sample $< $(SAMPN) $(SAMPK) >$@

$(SAMPLES): $$(ZAMPLE) build/bin/uncompress
	@mkdir -p $(@D)
	build/bin/uncompress <$< >$@

$(L1CACHE): $$(SAMPLE) rep/$$(REPL).py conf/l1.config
	@mkdir -p $(@D)
	python3 rep/$(REPL).py $(L1ARGS) $(SAMPLE) $@

$(L1MATRS): $$(L1) bin/matr.py conf/sample.config
	@mkdir -p $(@D)
	bin/matr.py -w $(WARM) -s $(SAMP) -c $(COOL) $< $@

$(L1MATRC): $$(L1MATR) bin/cumstats.py
	@mkdir -p $(@D)
	bin/cumstats.py <$< >$@

$(L1MATRB): $$(L1MATR) bin/bucketstats.py conf/bucket.config
	@mkdir -p $(@D)
	bin/bucketstats.py <$< >$@ $(BSIZE)

$(L1MATRZ): $$(L1MATR) bin/bucketstats.py conf/bucket.config
	@mkdir -p $(@D)
	bin/zoom.py <$< >$@ $(ZBSIZE) $(ZOOMED)

PLOT = cat bin/simple.gplot | sed 's|OUTPUT|$@|' | sed 's|INPUT|$<|' | sed 's|TRACE|$(TRACE)|'
LPLOT = cat bin/log.gplot | sed 's|OUTPUT|$@|' | sed 's|INPUT|$<|' | sed 's|TRACE|$(TRACE)|'
LLPLOT = cat bin/loglog.gplot | sed 's|OUTPUT|$@|' | sed 's|INPUT|$<|' | sed 's|TRACE|$(TRACE)|'

$(L1CPLOT): $$(L1CUM) $$(L1CBEL) bin/simple.gplot
	@mkdir -p $(@D)
	$(PLOT) | sed 's|TYPE|Cumulative sum|'| sed 's|BELADY|$(L1CBEL)|' | gnuplot -persist

$(L1BPLOT): $$(L1BUC) $$(L1BBEL) bin/simple.gplot
	@mkdir -p $(@D)
	$(PLOT) | sed 's|TYPE|Bucket plot|' | sed 's|BELADY|$(L1BBEL)|' | gnuplot -persist

$(L1LPLOT): $$(L1BUC) $$(L1BBEL) bin/loglog.gplot
	@mkdir -p $(@D)
	$(LLPLOT) | sed 's|TYPE|Bucket plot|' | sed 's|BELADY|$(L1BBEL)|' | gnuplot -persist

$(L1ZPLOT): $$(L1ZBUC) $$(L1ZBEL) bin/log.gplot
	@mkdir -p $(@D)
	$(LPLOT) | sed 's|TYPE|Zoomed in bucket plot|' | sed 's|BELADY|$(L1ZBEL)|' | gnuplot -persist

bin/zip.sh: build/bin/compress

PROGS   = $(patsubst src/%.c,%,$(wildcard src/*.c))

progs: $(PROGS:%=build/bin/%)

build/obj/%.o: src/%.c
	@mkdir -p $(@D)
	gcc -c -O3 -o $@ $<

build/bin/%: build/obj/%.o
	@mkdir -p $(@D)
	gcc -O3 -o $@ $<


