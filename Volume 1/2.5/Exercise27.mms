; Comparing Dynamic storage allocation methods

POOLMAX 	GREG
ZERO		GREG

t 		IS	    	$255
wordSize	IS		#10
m		IS		3
mOffset		IS		5		Each node is of size 2^mOffset bytes
capacity 	IS	    	1<<(m+mOffset)	max number of bytes for allocation
seed	  	IS	    	1

		PREFIX    	node:
LINK		IS	    	8*1
INFO		IS	    	8*2
		PREFIX    	:

		PREFIX		dynNode:
TAG		IS		0
KVAL		IS		1
LINKF		IS		8*1
LINKB		IS		8*2 
		PREFIX		:

		PREFIX		availNode:
AVAILF		IS		8*0
AVAILB		IS		8*1 
		PREFIX		:

		PREFIX		f:
one		GREG		#3FF0000000000000
negone		GREG		#BFF0000000000000 
zero		GREG		#0000000000000000
		PREFIX		:

		LOC       	Data_Segment
		GREG	    	@
L0		OCTA      	0
		LOC	    	L0+capacity
		GREG	    	@
;Linf		OCTA	    	0
AVAIL		OCTA		0
		LOC		AVAIL+m*8

		LOC		#100
Main		SET		$1,:m
		PUSHJ		$0,:initMemory
		PUSHJ		$0,:allocateSomeStuff
		TRAP	    	0,Halt,0

		
	  	PREFIX    	initMemory:
m	  	IS	    	$0
retaddr		IS		$1
AVAILhead	IS		$2
AVAIL		IS		$3
i		IS		$4
last		IS		$10
:initMemory  	GET		retaddr,:rJ
		LDA		AVAILhead,:AVAIL
		SET		AVAIL,AVAILhead
		SET		i,m
1H		BZ		i,2F				AVAILF[k]=LINKF(LOC(AVAIL[k]))=link to rear of AVAIL[k] list
		STO		AVAIL,AVAIL			AVAILB[k]=LINKB(LOC(AVAIL[k]))=link to front of AVAIL[k] list
		STO		AVAIL,AVAIL,8
		SUB		i,i,1
		ADD		AVAIL,AVAIL,16
		JMP		1B
2H		SUB		AVAIL,AVAIL,16			Bring back AVAIL to point to LOC(AVAIL[m])
		LDA		:t,:L0				Loop ends before k=m so AVAILF[m]=AVAILF[m]=0
		STO		AVAIL,:t,:dynNode:LINKF	     	
		STO		AVAIL,:t,:dynNode:LINKB	     	LINKF(0)=LINKB(0)=LOC(AVAIL[m])
		SET		last,1
		STB		last,:t,:dynNode:TAG		TAG(0)=1
		STB		m,:t,:dynNode:KVAL		KVAL(0)=m
		PUT		:rJ,retaddr
	  	POP	    	1,0
	  	PREFIX      	:

	  	PREFIX    	reserve:
k	  	IS	    	$0
j		IS		$1
P		IS		$2
L		IS		$3
delta		IS		$4
AVAILj		IS		$5
AVAILk		IS		$6
AVAILm		IS		$7
last		IS		$10
:reserve  	SET		j,k
		SET		delta,1<<:mOffset
		LDA		AVAILk,:AVAIL
		MUL		:t,k,16
		ADD		AVAILk,:t,AVAILk	AVAILk = LOC(AVAIL[k])
		LDA		AVAILm,:AVAIL
		SET		:t,:m
		MUL		:t,:t,16
		ADD		AVAILm,:t,AVAILm	AVAILm = LOC(AVAIL[m])
		SET		AVAILj,AVAILk
;	  	R1	    	[Find block.]
1H		CMPU		:t,AVAILj,AVAILm
		BP		:t,5F			for k ≤ j ≤ m
		LDO		:t,AVAILj,:availNode:AVAILF
		CMPU		:t,:t,AVAILj		if AVAILF[j] ≠ LOC(AVAIL[j])
		BNZ		:t,2F
		ADD		j,j,1
		ADD		AVAILj,AVAILj,16
		JMP		1B
5H		TRAP		0,:Halt,0	Insufficient memory
;	  	R2	    	[Remove from list.]
2H		POP	    	1,0
	  	PREFIX      	:

	  	PREFIX    	buddyk:
k	  	IS	    	$0
x		IS		$1
:buddyk  	SET		:t,1
		SL		:t,:t,k
		XOR		$0,x,:t
	  	POP	    	1,0
	  	PREFIX      	:

	  	PREFIX    	liberate:
k	  	IS	    	$0
last		IS		$10
:liberate  	POP	    	1,0
	  	PREFIX      	:

		PREFIX		allocateSomeStuff:
retaddr		IS		$0
a		IS		$1
b		IS		$2
c		IS		$3
d		IS		$4
e		IS		$5
f		IS		$6
g		IS		$7
tmp 		IS		$8
last 		IS		$9		
:allocateSomeStuff GET		retaddr,:rJ
		SET		(last+1),1
		PUSHJ		last,:reserve
		SET		a,last
		SET		(last+1),1
		PUSHJ		last,:reserve
		SET		b,last
		SET		(last+1),a
		PUSHJ		last,:liberate
		SET		(last+1),2
		PUSHJ		last,:reserve
		SET		c,last
		SET		(last+1),1
		PUSHJ		last,:reserve
		SET		d,last
		SET		(last+1),c
		PUSHJ		last,:liberate
		SET		(last+1),1
		PUSHJ		last,:reserve
		SET		e,last
;		SET		(last+1),4
;		PUSHJ		last,:reserve		fail here
;		SET		f,last
		PUT		:rJ,retaddr
		POP		0,0
		PREFIX		:

	  	PREFIX    	rand:
X	  	IS	    	$0
a	  	IS	    	$1
c	  	IS	    	$2
last	  	IS	    	$3
:rand	  	GETA	    	last,X_
	  	LDO	    	X,last
	  	GETA	    	:t,a_
	  	LDO	    	a,:t
	  	GETA	    	:t,c_
	  	LDO	    	c,:t
	 	MUL	    	:t,a,X
	  	ADD	    	X,:t,c
	  	STO	    	X,last
	  	FLOTU	    	X,X
	  	SET	    	:t,0
		SUB		:t,:t,1
	  	FLOTU	    	:t,:t
	  	FDIV	    	X,X,:t
	  	POP	    	1,0
a_	  	OCTA	    	#5851F42D4C957F2D
c_	  	OCTA	    	#14057B7EF767814F
X_	  	OCTA	    	:seed
	  	PREFIX      	:

	  	PREFIX    	randintAtoB:
A	  	IS	    	$0
B	  	IS	    	$1
retaddr		IS		$2
last	  	IS	    	$3
:randintAtoB  	GET		retaddr,:rJ
		PUSHJ		last,:rand
		SUB		:t,B,A
		FLOTU		:t,:t
		FMUL		:t,:t,last
		FIXU		:t,:t
		ADD		$0,:t,A
	  	PUT		:rJ,retaddr
		POP		1,0
	  	PREFIX      	: