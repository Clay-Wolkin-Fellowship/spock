#include <assert.h>
#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>

#define BUFFER_SIZE 16384

size_t
min(size_t a, size_t b)
{
	return a < b ? a : b;
}

void *
memswap(void * dst, void * src, size_t num)
{
	size_t i;
	char *cd = dst, *cs = src;
	for(i = 0; i < num; ++i)
	{
		cd[i] ^= cs[i];
		cs[i] ^= cd[i];
		cd[i] ^= cs[i];
	}
}

size_t
frread(void * ptr, size_t size, size_t count, FILE * stream)
{
	char *cptr;
	size_t fi, bi;
	// only grab full size lines
	count = min(ftell(stream), size * count) / size;
	
	// read the file into the ptr
	fseek(stream, -(size * count), SEEK_CUR);
	fread(ptr, size, count, stream);
	fseek(stream, -(size * count), SEEK_CUR);
	
	// reverse all of the lines
	for(fi = 0, bi = count - 1; fi < bi; ++fi, --bi)
		memswap(&cptr[fi * size], &cptr[bi * size], size);
	return count;
}

int
main(int argc, char *argv[])
{
	FILE * input;
	size_t N, K, k;
	char buf[BUFFER_SIZE];

	if(argc != 3)
	{
		fprintf(stderr,"Usage: %s [FILE] N\n",argv[0]);
		return 1;
	}
	input = fopen(argv[1], "r");
	if(!input)
	{
		fprintf(stderr,"Error: Unable to open %s\n",argv[1]);
		return 1;
	}
	N = atoi(argv[2]);
	K = BUFFER_SIZE / N;

	fseek(input, 0, SEEK_END);
	while((k = frread(buf, N, K, input)) > 0)
		fwrite(buf, N, k, input);

	return 0;
}

