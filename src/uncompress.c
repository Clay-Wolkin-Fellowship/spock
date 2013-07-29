#include <stddef.h>
#include <stdio.h>
#include <stdint.h>

size_t getn(char* buf, size_t n)
{
	size_t i;
	int temp;
	for(i =0; i < n; ++i)
	{
		temp = getchar();
		if(temp == EOF)
			break;
		buf[i] = (char)temp;
	}
	return i;
}

int main()
{
	size_t last = 0;
	uint32_t vals[4];
	char temp;
	while(getn((char*)vals, sizeof(vals)))
	{
		temp = vals[1] ? 'W' : 'R';
		last += vals[3];
		printf("0x%x: %c 0x%x %zd\n", vals[0], temp, vals[2], last);
	}
	return 0;
}

