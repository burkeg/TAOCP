#include <stdio.h>

#define AMOUNT 13*2
void writeByte(__uint64_t num, FILE * fptr);
  
int main()
{
  // printf() displays the string inside quotation
  FILE *fp;
  __uint64_t num[AMOUNT] = {
    0,9,
    9,2,
    3,7,
    7,5,
    5,8,
    8,6,
    4,6,
    1,3,
    7,4,
    9,5,
    2,8,
    0,0
  };
  int i = 0;

  fp = fopen("input.dat","w");
  for (i = 0; i < AMOUNT; i++) {
    printf("%d,%lX\n",i,num[i]);
    writeByte(num[i],fp);
  }
  fclose(fp);
  return 0;
}

void writeByte(__uint64_t num, FILE * fptr) {
  __uint64_t b0,b1,b2,b3,b4,b5,b6,b7;
  __uint64_t res;
  b0 = (num & 0x00000000000000ff) << 56;
  b1 = (num & 0x000000000000ff00) << 40;
  b2 = (num & 0x0000000000ff0000) << 24;
  b3 = (num & 0x00000000ff000000) << 8;
  b4 = (num & 0x000000ff00000000) >> 8;
  b5 = (num & 0x0000ff0000000000) >> 24;
  b6 = (num & 0x00ff000000000000) >> 40;
  b7 = (num & 0xff00000000000000) >> 56;
  res = b0 | b1 | b2 | b3 | b4 | b5 | b6 | b7;
  fwrite(&res , sizeof(__uint64_t), 1, fptr);
}
