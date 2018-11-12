; Comparing Dynamic storage allocation methods

POOLMAX 	GREG
ZERO		GREG

t 		IS	    	$255
octaSize	IS		8
capacity 	IS	    	8		max number of 8-byte nodes for allocation
LINK		IS 	    	0
INFO		IS	    	8

		PREFIX    	node:
LLINK		IS	    	8*0
RLINK		IS	    	8*1
INFO		IS	    	8*2
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

		LOC       	Data_Segment
		GREG	    	@
AVAIL		OCTA		0,@+8*2
L0		OCTA      	octaSize*capacity,0
		LOC	    	L0+octaSize*capacity
		GREG	    	@
Linf		OCTA	    	0

		LOC		#100
Main		PUSHJ		$0,:allocateSomeStuff
		TRAP	    	0,Halt,0

		PREFIX		testStrategy:
strategy	IS		$0
retaddr		IS		$1
:testStrategy	GET		retaddr,:rJ
		PUT		:rJ,retaddr
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
		SET		(last+1),6
		PUSHJ		last,:worstFit
		SET		a,last
		SET		(last+1),1
		PUSHJ		last,:worstFit
		SET		b,last
		SET		(last+1),a
		PUSHJ		last,:liberate
		SET		(last+1),2
		PUSHJ		last,:worstFit
		SET		c,last
		SET		(last+1),1
		PUSHJ		last,:worstFit
		SET		d,last
		SET		(last+1),c
		PUSHJ		last,:liberate
		SET		(last+1),1
		PUSHJ		last,:worstFit
		SET		e,last
;		SET		(last+1),4
;		PUSHJ		last,:worstFit		fail here
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
;		POP		1,0
		TRAP		0,:Halt,0
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
;		POP		1,0
		TRAP		0,:Halt,0
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
;		POP		1,0
		TRAP		0,:Halt,0
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
