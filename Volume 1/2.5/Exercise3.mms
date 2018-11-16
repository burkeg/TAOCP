; Comparing Dynamic storage allocation methods

POOLMAX 	GREG
ZERO		GREG

t 		IS	    	$255
octaSize	IS		8
capacity 	IS	    	76		max number of 8-byte nodes for allocation
seed	  	IS	    	1

		PREFIX    	node:
LINK		IS	    	8*0
INFO		IS	    	8*1
		PREFIX    	:

		PREFIX		dynNode:
SIZE		IS		8*0
LINK		IS		8*1
		PREFIX		:

		PREFIX		strategy:
first		IS		0
best		IS		1
worst		IS		2
		PREFIX		:

		PREFIX		f:
one		GREG		#3FF0000000000000
negone		GREG		#BFF0000000000000 
zero		GREG		#0000000000000000
		PREFIX		:

		LOC       	Data_Segment
		GREG	    	@
AVAIL		OCTA		0,@+8*2
L0		OCTA      	octaSize*capacity,0
		LOC	    	L0+octaSize*capacity
		GREG	    	@
Linf		OCTA	    	0
schedule	OCTA		0

		LOC		#100
Main		SET		$1,:strategy:first
		PUSHJ		$0,:scheduleAllocations
		TRAP	    	0,Halt,0

		PREFIX		previewRand:
:previewRand	LDA		$0,:Data_Segment
1H		SET		$2,0
		SET		$3,255
		PUSHJ		$1,:randintAtoB
		STO		$1,$0
		ADD		$0,$0,8
		JMP		1B
		PREFIX		:

		PREFIX		testStrategy:
strategy	IS		$0
retaddr		IS		$1
last		IS		$2
minSize		IS		1
maxSize		IS		2
:testStrategy	GET		retaddr,:rJ
		SET		(last+1),minSize
		SET		(last+2),maxSize
		PUSHJ		last,:randintAtoB
		SET		(last+1),last
		CMP		:t,strategy,:strategy:first
		BNZ		:t,1F
		PUSHJ		last,:firstFit
		JMP		done
1H		CMP		:t,strategy,:strategy:best
		BNZ		:t,1F
		PUSHJ		last,:bestFit
		JMP		done
1H		CMP		:t,strategy,:strategy:worst
		BNZ		:t,1F
		PUSHJ		last,:worstFit
		JMP		done
1H		TRAP		0,:Halt,0  Unknown strategy
done		PUT		:rJ,retaddr
		SET		$0,last
		POP		1,0
		PREFIX		:

		PREFIX		scheduleAllocations:
strategy	IS		$0
retaddr		IS		$1
time		IS		$2
numEvents	IS		$3
currEvent	IS		$4
currEventPtr	IS		$5
twoK		IS		$6
tmp 		IS		$9
last 		IS		$10
:scheduleAllocations GET	retaddr,:rJ
		SET  		time,0
		SET		numEvents,0
		SETL		twoK,(2000>>(16*0))%(1<<16)
		INCML		twoK,(2000>>(16*1))%(1<<16)
		INCMH		twoK,(2000>>(16*2))%(1<<16)
		INCH		twoK,(2000>>(16*3))%(1<<16)
timeLoop	CMPU		:t,time,twoK				for (time=0; time<2000;time++) {
		BP		:t,timeLoopExit
		LDA		currEventPtr,:schedule
		SET		currEvent,0
eventLoop	CMPU		:t,currEvent,numEvents				for (event=0; event<numEvents; numEvents++) {
		BNN		:t,eventLoopExit
		LDO		:t,currEventPtr,:node:INFO
		CMP		:t,:t,time					
		BNZ		:t,notNow						if (events[currEvent].expireTime == time) {
		LDO		(last+1),currEventPtr,:node:LINK
		PUSHJ		last,:liberate							free(events[currEvent].nodePtr);
		SET		:t,0
		SUB		:t,:t,1
		STO		:t,currEventPtr,:node:INFO
notNow		ADD		currEventPtr,currEventPtr,16
		ADD		currEvent,currEvent,1
		JMP		eventLoop					}
eventLoopExit	SET		(last+1),strategy
		PUSHJ		last,:testStrategy
		SET		tmp,last
		BNZ		last,allocSuccess				if (alloc failed) {return time;}
		SET		$0,time
		JMP		done
allocSuccess	STO		tmp,currEventPtr,:node:LINK
		PUSHJ		last,:randExp
		ADD		:t,time,last
		STO		:t,currEventPtr,:node:INFO
		ADD		numEvents,numEvents,1
		ADD		time,time,1
		JMP		timeLoop				}
timeLoopExit	SET		$0,twoK							
done		PUT  		:rJ,retaddr
		POP		1,0
		PREFIX		:

;		Exponential distrobution Quantile: −ln(1 − F) / λ
		PREFIX	        randExp:
retaddr		IS		$0
idx		IS		$1
tmp 		IS		$9
last 		IS		$10
table		BYTE		1,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2
		BYTE		2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2
		BYTE		2,2,2,2,2,2,3,3,3,3,3,3,3,3,3,3,3
		BYTE		3,3,3,3,3,3,3,3,3,3,3,3,3,4,4,4,4
		BYTE		4,4,4,4,4,4,4,4,4,4,5,5,5,5,5,5,5
		BYTE		5,5,6,6,6,6,6,7,7,7,7,8,9,9,11
;		Generated using "testDist.m"
tableEnd	BYTE		11
numItems	IS		(tableEnd+1-table)
:randExp 	GET		retaddr,:rJ
		SET		tmp,numItems
		SETL		tmp,(numItems>>(8*0))%(1<<8)
		INCML		tmp,(numItems>>(8*1))%(1<<8)
		INCMH		tmp,(numItems>>(8*2))%(1<<8)
		INCH		tmp,(numItems>>(8*3))%(1<<8)
		SET		(last+1),0
		SET		(last+2),tmp
		PUSHJ		last,:randintAtoB
		SET		idx,last
		GETA		:t,table
		PUT  		:rJ,retaddr
		LDB		$0,:t,idx
		POP		1,0
		PREFIX		:

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
		PUSHJ		last,:firstFit
		SET		a,last
		SET		(last+1),1
		PUSHJ		last,:firstFit
		SET		b,last
		SET		(last+1),a
		PUSHJ		last,:liberate
		SET		(last+1),2
		PUSHJ		last,:firstFit
		SET		c,last
		SET		(last+1),1
		PUSHJ		last,:firstFit
		SET		d,last
		SET		(last+1),c
		PUSHJ		last,:liberate
		SET		(last+1),1
		PUSHJ		last,:firstFit
		SET		e,last
;		SET		(last+1),4
;		PUSHJ		last,:firstFit		fail here
;		SET		f,last
		PUT		:rJ,retaddr
		POP		0,0
		PREFIX		:

		PREFIX		worstFit:
N		IS		$0
P		IS		$1
Q		IS		$2
K		IS		$3
tmp		IS		$4
L		IS		$5
worstLocP	IS		$6
worstLocQ	IS		$7
worstSize	IS		$8
last		IS		$9
c		IS		2<<3
;	  	A1	    	[Initialize.]
:worstFit	SL		N,N,3
		SET		worstSize,0
		LDA		Q,:AVAIL	Q <- LOC(AVAIL)
;	  	A2	    	[End of list?]
2H		LDO		P,Q,:dynNode:LINK	P <- LINK(Q)
		BNZ		P,3F			If P = Λ, terminate
		BZ		worstSize,failed	Fail if worstSize is zero. (worstSize never changed from default)
		SET		P,worstLocP
		SET		Q,worstLocQ		
		JMP		4F
failed		SET		$0,0			Unsuccessfully allocated space
		POP		1,0
;		TRAP		0,:Halt,0
;	  	A3	    	[Is SIZE enough?]
3H		LDO		tmp,P,:dynNode:SIZE	get SIZE(P)
		CMPU		:t,tmp,N
		BN		:t,notBetter		If SIZE(P)≥N, go to A4
		CMPU		:t,worstSize,tmp	worstSize compare SIZE(P)
		BNN		:t,notBetter
		SET		worstSize,tmp		If SIZE(P) is the largest so far
		SET		worstLocP,P		then update worst.
		SET		worstLocQ,Q
notBetter	SET		Q,P			Q <- P
		JMP		2B			return to A2
;	  	A4	    	[Reserve ≥ N.]
4H		LDO		tmp,P,:dynNode:SIZE	get SIZE(P)
		SUB		K,tmp,N			K <- SIZE(P)-N
		CMP		:t,K,c			if K < c
		BN		:t,closeEnough
		STO		K,P,:dynNode:SIZE	SIZE(P) <- K
		ADD		L,P,K			L <- P + K
		STO		N,L,:dynNode:SIZE	SIZE(L) <- N
		JMP		done
closeEnough	LDO		:t,P,:dynNode:LINK	get  LINK(P)
		STO		:t,Q,:dynNode:LINK	LINK(Q) <- LINK(P)
		SET		L,P
done		SET		$0,L			Successfully allocated space
		POP		1,0
		PREFIX		:

		PREFIX		bestFit:
N		IS		$0
P		IS		$1
Q		IS		$2
K		IS		$3
tmp		IS		$4
L		IS		$5
bestLocP	IS		$6
bestLocQ	IS		$7
bestSize	IS		$8
last		IS		$9
c		IS		2<<3
bestSizeDefault	OCTA		#7FFFFFFFFFFFFFFF
;	  	A1	    	[Initialize.]
:bestFit	SL		N,N,3
		GETA		bestSize,bestSizeDefault
		LDO		bestSize,bestSize
		LDA		Q,:AVAIL	Q <- LOC(AVAIL)
;	  	A2	    	[End of list?]
2H		LDO		P,Q,:dynNode:LINK	P <- LINK(Q)
		BNZ		P,3F			If P = Λ, terminate
		ADD		:t,bestSize,1
		BN		:t,failed		Fail if bestSize+1 is negative. (bestSize never changed from default)
		SET		P,bestLocP
		SET		Q,bestLocQ		
		JMP		4F
failed		SET		$0,0			Unsuccessfully allocated space
		POP		1,0
;		TRAP		0,:Halt,0
;	  	A3	    	[Is SIZE enough?]
3H		LDO		tmp,P,:dynNode:SIZE	get SIZE(P)
		CMPU		:t,tmp,N
		BN		:t,notBetter		If SIZE(P)≥N, go to A4
		CMPU		:t,tmp,bestSize		SIZE(P) compare bestSize
		BNN		:t,notBetter
		SET		bestSize,tmp		If SIZE(P) is the smallest so far that is still ≥ N
		SET		bestLocP,P		then update best.
		SET		bestLocQ,Q
notBetter	SET		Q,P			Q <- P
		JMP		2B			return to A2
;	  	A4	    	[Reserve ≥ N.]
4H		LDO		tmp,P,:dynNode:SIZE	get SIZE(P)
		SUB		K,tmp,N			K <- SIZE(P)-N
		CMP		:t,K,c			if K < c
		BN		:t,closeEnough
		STO		K,P,:dynNode:SIZE	SIZE(P) <- K
		ADD		L,P,K			L <- P + K
		STO		N,L,:dynNode:SIZE	SIZE(L) <- N
		JMP		done
closeEnough	LDO		:t,P,:dynNode:LINK	get  LINK(P)
		STO		:t,Q,:dynNode:LINK	LINK(Q) <- LINK(P)
		SET		L,P
done		SET		$0,L			Successfully allocated space
		POP		1,0
		PREFIX		:

		PREFIX		firstFit:
N		IS		$0
P		IS		$1
Q		IS		$2
K		IS		$3
tmp		IS		$4
L		IS		$5
last		IS		$6
c		IS		2<<3
;	  	A1	    	[Initialize.]
:firstFit	SL		N,N,3
		LDA		Q,:AVAIL	Q <- LOC(AVAIL)
;	  	A2	    	[End of list?]
2H		LDO		P,Q,:dynNode:LINK	P <- LINK(Q)
		BNZ		P,3F			If P = Λ, terminate
		SET		$0,0			Unsuccessfully allocated space
		POP		1,0
;		TRAP		0,:Halt,0
;	  	A3	    	[Is SIZE enough?]
3H		LDO		tmp,P,:dynNode:SIZE	get SIZE(P)
		CMPU		:t,tmp,N
		BNN		:t,4F			If SIZE(P)≥N, go to A4
		SET		Q,P			Q <- P
		JMP		2B			return to A2
;	  	A4	    	[Reserve ≥ N.]
4H		SUB		K,tmp,N			K <- SIZE(P)-N
		CMP		:t,K,c			if K < c
		BN		:t,closeEnough
		STO		K,P,:dynNode:SIZE	SIZE(P) <- K
		ADD		L,P,K			L <- P + K
		STO		N,L,:dynNode:SIZE	SIZE(L) <- N
		JMP		done
closeEnough	LDO		:t,P,:dynNode:LINK	get  LINK(P)
		STO		:t,Q,:dynNode:LINK	LINK(Q) <- LINK(P)
		SET		L,P
done		SET		$0,L			Successfully allocated space
		POP		1,0
		PREFIX		:

		PREFIX		liberate:
P0	  	IS	      	$0
N		IS		$1
P		IS		$2
Q		IS		$3
tmp		IS		$4
;	  	B1	    	[Initialize.]
:liberate  	LDO		N,P0,:dynNode:SIZE
		LDA		Q,:AVAIL		Q <- LOC(AVAIL)
;	  	B2	    	[Advance P.]
2H		LDO		P,Q,:dynNode:LINK	P <- LINK(Q)
		BZ		P,3F			If P = Λ, go to B3
		CMP		:t,P,P0			If P > P0, go to B3
		BP		:t,3F
		SET		Q,P
		JMP		2B			Else, Q ← P and repeat step B2		Q <- LOC(AVAIL)
;	  	B3	    	[Check upper bound.]
3H		ADD		:t,P0,N			get P0+N
		CMP		:t,:t,P
		BNZ		:t,noMergeUp		if P0 + N = P
		BZ		P,noMergeUp		and P ≠ Λ
		LDO		:t,P,:dynNode:SIZE	
		ADD		N,N,:t			N ← N + SIZE(P)
		LDO		:t,P,:dynNode:LINK
		STO		:t,P0,:dynNode:LINK	LINK(P0) ← LINK(P)
		JMP		4F
noMergeUp	STO		P,P0,:dynNode:LINK	otherwise LINK(P0) ← P
;	  	B4	    	[Check lower bound.]
4H		LDO		tmp,Q,:dynNode:SIZE	get SIZE(Q)
		ADD		:t,Q,tmp		get Q + SIZE(Q)
		CMP		:t,:t,P0		If Q + SIZE(Q) = P0
		BNZ		:t,noMergeDown
		ADD		:t,tmp,N		get SIZE(Q)+N
		STO		:t,Q,:dynNode:SIZE	SIZE(Q) ← SIZE(Q)+N
		LDO		:t,P0,:dynNode:LINK	get LINK(P0)
		STO		:t,Q,:dynNode:LINK	LINK(Q) ← LINK(P0)
		POP		0,0
noMergeDown	STO		P0,Q,:dynNode:LINK	LINK(Q) ← P0
		STO		N,P0,:dynNode:SIZE	SIZE(P0) ← N
	  	POP	    	0,0
	  	PREFIX   	:

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