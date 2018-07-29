#include <stdio.h>
#include <stdlib.h>
int main()
{
  // printf() displays the string inside quotation
  int j,k,m,n;
  n=5;
  int* X = (int*)malloc(sizeof(int)*n);
  X[0]=3;
  X[1]=4;
  X[2]=7;
  X[3]=2;
  X[4]=5;
 M1://Initialize
  j=n-1;
  k=n-2;
  m=X[n-1];
 M2://All Tested?
  if (k==-1) {
    printf("max: %d.\n", m);
    return 0;
  }
 M3://Compare
  if (X[k]<=m)
    goto M5;
 M4://Change m
  j=k;
  m=X[k];
 M5://Decrease k.
  k--;
  goto M2;
  return 0;
}
