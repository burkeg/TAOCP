#include <stdio.h>
#include <stdlib.h>

float p_n_k(int n, int k);
float Gpn1(int n);

int main()
{
  int n = 3;
  int k = 1;
  int numel=5;
  for (n=0; n<=numel; n++) {
    printf("Gpn1(%d)=%f\n",n,Gpn1(n));
  }
  return 0;
}


//E[x]=G'n(1)
//Average/expected value of Gn(z) is G'n(1)
//G'n(1)=pn1 + 2*pn2 + 3*pn3 + ...
//=sum(k*pnk) across all k
float Gpn1(int n) {
  float sum=0.0f;
  float tmp=0.0f;
  printf("Gpn1(%d)\n",n);
  for (int k = 1; k<=n; k++) {
    tmp=(float)k*p_n_k(n,k);
    printf("%d*p_%d_%d=%d*%f=%f\n",k,n,k,k,p_n_k(n,k),tmp);
    sum+=tmp;
  }
  return sum;
}
float p_n_k(int n, int k) {
  //base cases:
  //printf("p_%d_%d\n", n,k);
  if (k<0) 
    return (float)0; //pnk=0 if k<0
  if (n==1)
    return (float)(0==k); //p1k=delta_0k
  //inductive case
  return (1.0f/(float)n)*p_n_k(n-1,k-1)+((float)(n-1)/(float)n)*p_n_k(n-1,k);
}
