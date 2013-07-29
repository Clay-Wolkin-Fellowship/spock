#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>

#define LINE_LENGTH (4 * sizeof(int32_t))

size_t
flength(FILE * f)
{
	size_t cpos = ftell(f), epos;
	fseek(f, 0, SEEK_END);
	epos = ftell(f);
	fseek(f, cpos, SEEK_SET);
	return epos;
}

int
main(int argc, char *argv[])
{
	FILE * input;
	size_t L, N, K, n, start;
	char * buf;
	if(argc != 4)
	{
		fprintf(stderr,"Usage: %s [FILE] N K\n",argv[0]);
		return 1;
	}
	input = fopen(argv[1], "r");
	if(!input)
	{
		fprintf(stderr,"Error: Unable to open %s\n",argv[1]);
		return 1;
	}
	N = atoll(argv[2]);
	K = atoll(argv[3]);
	L = flength(input) / LINE_LENGTH;
	if(L <= N * K)
	{
		buf = malloc(LINE_LENGTH * L);
		fread(buf, LINE_LENGTH, L, input);
		fwrite(buf, LINE_LENGTH, L, stdout);
		return 0;
	}
	buf = malloc(LINE_LENGTH * K);
	srandom(42);
	for(n = 0; n < N; ++n)
	{
		start = random() % (L - K + 1);
		fseek(input, start * LINE_LENGTH, SEEK_SET);
		fread(buf, LINE_LENGTH, K, input);
		fwrite(buf, LINE_LENGTH, L, stdout);
	}
	return 0;
}

