; Comparing Dynamic storage allocation methods

POOLMAX 	GREG
ZERO		GREG

t 		IS	    	$255
wordSize	IS		#10
m		IS		3
capacity 	IS	    	1<<(m+4)	max number of 8-byte nodes for allocation
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

		PREFIX		f:
one		GREG		#3FF0000000000000
negone		GREG		#BFF0000000000000 
zero		GREG		#0000000000000000
		PREFIX		:

		LOC       	Data_Segment
		GREG	    	@
AVAIL		OCTA		0,@+8*2
L0		OCTA      	0
		LOC	    	L0+capacity
		GREG	    	@
Linf		OCTA	    	0
schedule	OCTA		0

		LOC		#100
Main		PUSHJ		$0,:allocateSomeStuff
		TRAP	    	0,Halt,0

	  	PREFIX    	reserve:
k	  	IS	    	$0
retaddr		IS		$1
last		IS		$10
:reserve  	GET		retaddr,:rJ
		PUT		:rJ,retaddr
	  	POP	    	1,0
	  	PREFIX      	:

	  	PREFIX    	liberate:
k	  	IS	    	$0
retaddr		IS		$1
last		IS		$10
:liberate  	GET		retaddr,:rJ
		PUT		:rJ,retaddr
	  	POP	    	1,0
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