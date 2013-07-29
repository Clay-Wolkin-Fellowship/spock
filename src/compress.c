#include <stddef.h>
#include <stdio.h>
#include <stdint.h>
#include <string.h>

#define BITS 8
#define SAVED (32 - (BITS))
#define ENTRIES (1 << (BITS))
#define MASK ((1ull << (SAVED)) - 1)
#define TAG(n) ((n) >> (SAVED))
#define INDEX(n) ((n) & MASK)
#define CMPT(x,y) (((x) << SAVED) | (INDEX(y)))


void putn(char* buf, size_t n)
{
	size_t i;
	for(i =0; i < n; ++i)
		putchar(buf[i]);
}

int main()
{
	size_t pc, loc, icount, tag, i, last = 0;
	size_t lookup[2][ENTRIES], found[2] = {0,0};
	char rw;
	uint32_t vals[4];

	while(scanf("0x%llx: %c 0x%llx %zd\n", &pc, &rw, &loc, &icount) == 4)
	{
		// compress index 0
		tag = TAG(pc);
		for(i = 0; i < found[0]; ++i)
			if(lookup[0][i] == tag)
				break;
		if(i == ENTRIES)
			return 1;
		else if(i == found[0])
			lookup[0][found[0]++] = tag;
		vals[0] = CMPT(lookup[0][i],pc);
		// compress index 1
		vals[1] = rw == 'W';
		// compress index 2
		tag = TAG(loc);
		for(i = 0; i < found[1]; ++i)
			if(lookup[1][i] == tag)
				break;
		if(i == ENTRIES)
			return 2;
		else if(i == found[1])
			lookup[1][found[1]++] = tag;
		vals[2] = CMPT(lookup[1][i],loc);
		// compress index 3
		vals[3] = last - icount;
		last = icount;
		putn((char*)vals, sizeof(vals));
	}
	return 0;
}

