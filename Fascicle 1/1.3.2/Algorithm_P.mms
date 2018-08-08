% Example program ... Table of primes
L 	  IS	  500		The number of primes to find
t	  IS	  $255		Temporary Storage
n	  GREG	  0		Prime candidate
q	  GREG	  0		Quotient
r	  GREG	  0		Remaineder
jj	  GREG	  0		Index for PRIME[j]
kk	  GREG	  0		Index for PRIME[k]
pk	  GREG	  0		Value of PRIME[k]
mm	  IS	  kk		Index for output lines 
	  LOC 	  Data_Segment
PRIME1	  WYDE	  2		PRIME[1] = 2
	  LOC	  PRIME1+2*L
ptop	  GREG	  @		Address of PRIME[501]
j0	  GREG	  PRIME1+2-@	Initial value of jj
BUF	  OCTA	  0		Place to form a decimal string

	  LOC	  #100		
Main	  SET	  n,3		P1. Start table. n <- 3
	  SET	  jj,j0		j <- 1
2H	  STWU	  n,ptop,jj	P2. n is prime. PRIME[j+1] <- n
	  INCL	  jj,2		j <- j+1
3H	  BZ	  jj,2F		P3. 500 found?
4H	  INCL	  n,2		P4. Advance n.
5H	  SET	  kk,j0		P5. k <- 2
6H	  LDWU	  pk,ptop,kk	P6. PRIME[k]\n?
	  DIV	  q,n,pk	q <- [n/PRIME[k]]_lower.
	  GET	  r,rR		r <- n mod PRIME[k]
	  BZ	  r,4B		To P4 if r=0
7H	  CMP	  t,q,pk	P7. PRIME[k] large?
	  BNP	  t,2B		To P2 if q<= PRIME[k]
8H	  INCL	  kk,2		P8. Advance k. k <- k+1
	  JMP	  6B		To P6.
	  GREG	  @		Base Address
Title	  BYTE	  "First Five Hundred Primes"
NewLn	  BYTE	  #a,0	      	Newline and string terminator
Blanks	  BYTE	  "   ",0	String of three blanks
2H	  LDA	  t,Title	P9. Print title.
	  TRAP	  0,Fputs,StdOut
	  NEG	  mm,2		Initialize m.
3H	  ADD	  mm,mm,j0	P10. Print line.
	  LDA	  t,Blanks	Output "   ".
	  TRAP	  0,Fputs,StdOut
2H	  LDWU	  pk,ptop,mm	pk <- prime to be printed
0H	  GREG	  #2030303030000000   " 0000",0,0,0
	  STOU	  0B,BUF	Prepare buffer for decimal conversion.	
	  LDA	  t,BUF+4	t <- position of units digit.
1H	  DIV	  pk,pk,10	pk <- [pk/10]_lower.      
	  GET	  r,rR		r <- next digit
	  INCL	  r,'0'		r <- ASCII digit r.
	  STBU	  r,t,0		Store r in the buffer.
	  SUB	  t,t,1		Move one byte to the left
	  PBNZ	  pk,1B		Repeat on remaining digits
	  LDA	  t,BUF		Output " " and four digits
	  TRAP	  0,Fputs,StdOut
	  INCL	  mm,2*L/10	Advance by 50 wydes.
	  PBN	  mm,2B		
	  LDA	  t,NewLn	Output a newline.
	  TRAP	  0,Fputs,StdOut
	  CMP	  t,mm,2*(L/10-1)     P11. 500 printed?	
	  PBNZ	  t,3B	        To P10 if not done.
	  TRAP	  0,Halt,0	      