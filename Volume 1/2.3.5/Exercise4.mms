; Algorithm E for garbage collection
				
AVAIL		GREG	    
POOLMAX 	GREG
SEQMIN		GREG
ZERO		GREG
				
t 		IS	    	$255
octaSize 	IS	    	8
capacity 	IS	    	100		max number of nodeSize-Byte nodes 
LINK		IS 	    	0
INFO		IS	    	8
_nodeSize 	IS	    	4 bytes
nodeSize 	GREG	    	_nodeSize*octaSize

		PREFIX    	nodeGarbage:
ALINK		IS	    	8*0
BLINK		IS	    	8*1
MARK		IS	    	8*2+0
ATOM		IS	    	8*2+1
INFO		IS	    	8*3
		PREFIX    	:

		PREFIX    	node:
LLINK		IS	    	:nodeGarbage:ALINK
RLINK		IS	    	:nodeGarbage:BLINK
INFO		IS	    	:nodeGarbage:INFO
		PREFIX    	:

		LOC       	Data_Segment
		GREG	    	@
T		OCTA		0
		LOC	    	@+(_nodeSize-1)*octaSize
L0		OCTA      	0
		LOC	    	L0+_nodeSize*octaSize*capacity
		GREG	    	@
Linf		OCTA	    	0


		LOC		#100
Main		LDA	    	POOLMAX,L0
		LDA	    	SEQMIN,Linf
		PUSHJ		$1,:makeSomeUselessGarbage
		PUSHJ		$0,:garbageCollect
		TRAP	    	0,Halt,0

		PREFIX		makeSomeUselessGarbage:
retaddr		IS		$0
a		IS		$1
b		IS		$2
c		IS		$3
d		IS		$4
e		IS		$5
tmp		IS		$6
last		IS		$7
:makeSomeUselessGarbage GET	retaddr,:rJ
		PUSHJ		last,:Alloc
		SET		a,last
		PUSHJ		last,:Alloc
		SET		b,last
		PUSHJ		last,:Alloc
		SET		c,last
		PUSHJ		last,:Alloc
		SET		d,last
		PUSHJ		last,:Alloc
		SET		e,last
		SET		:t,1
		STB		:t,b,:nodeGarbage:ATOM
		SET		:t,0
;		a
		SET		:t,'a'
		STO		:t,a,:node:INFO
		STO		b,a,:node:LLINK
		STO		c,a,:node:RLINK
;		b
		SET		:t,'b'
		STO		:t,b,:node:INFO
		SET		:t,0
		STO		:t,b,:node:LLINK
		STO		:t,b,:node:RLINK
;		c
		SET		:t,'c'
		STO		:t,c,:node:INFO
		STO		b,c,:node:LLINK
		STO		d,c,:node:RLINK
;		d
		SET		:t,'d'
		STO		:t,d,:node:INFO
		STO		e,d,:node:LLINK
		STO		d,d,:node:RLINK
;		e
		SET		:t,'e'
		STO		:t,e,:node:INFO
		SET		:t,0
		STO		:t,e,:node:LLINK
		STO		c,e,:node:RLINK
		PUT		:rJ,retaddr
		SET		$0,a
		POP		1,0
		PREFIX		:

		PREFIX		garbageCollect:
;		throws that shit out		
P0		IS		$0
retaddr		IS		$1
T		IS		$2
Q		IS		$3
P		IS		$4
tmp		IS		$5
last 		IS		$6
;	  	E1	    	[Initialize.]
:garbageCollect SET		T,0	T <- Λ
		SET		P,P0	P <- P0
;	  	E2	    	[Mark.]
2H		SET		:t,1
		STB		:t,P,:nodeGarbage:MARK	MARK(P) <- 1
;	  	E3	    	[Atom?]
3H		LDB		:t,P,:nodeGarbage:ATOM
		BNZ		:t,6F	if ATOM(P) = 1, go to E6
;	  	E4	    	[Down ALINK.]
4H		LDO		Q,P,:nodeGarbage:ALINK
		BZ		Q,5F	if Q = Λ skip to E5
		LDB		:t,Q,:nodeGarbage:MARK
		BNZ		:t,5F	if MARK(Q) = 0 skip to E5
		SET		:t,1
		STB		:t,P,:nodeGarbage:ATOM	ATOM(P) <- 1
		STO		T,P,:nodeGarbage:ALINK	ALINK(P) <- T
		SET		T,P			T <- P
		SET		P,Q			P <- Q
		JMP		2B			go to E2
;	  	E5	    	[Down BLINK.]
5H		LDO		Q,P,:nodeGarbage:BLINK
		BZ		Q,6F	if Q = Λ skip to E6
		LDB		:t,Q,:nodeGarbage:MARK
		BNZ		:t,6F	if MARK(Q) != 0 skip to E6
		STO		T,P,:nodeGarbage:BLINK	BLINK(P) <- T
		SET		T,P			T <- P
		SET		P,Q			P <- Q
		JMP		2B			go to E2
;	  	E6	    	[Up.]
6H		BZ		T,done	if T = Λ, terminate
		SET		Q,T	Q <- T
3H		LDB		:t,Q,:nodeGarbage:ATOM
		BZ		:t,doB	if ATOM(Q) = 0, do B again
		SET		:t,0
		STB		:t,Q,:nodeGarbage:ATOM	ATOM(Q) <- 0
		LDO		T,Q,:nodeGarbage:ALINK T <- ALINK(Q)
		STO		P,Q,:nodeGarbage:ALINK ALINK(Q) <- P
		SET		P,Q	P <- Q
		JMP		5B	return to E5
doB		LDO		T,Q,:nodeGarbage:BLINK T <- BLINK(Q)
		STO		P,Q,:nodeGarbage:BLINK BLINK(Q) <- P
		SET		P,Q	P <- Q
		JMP		6B	return to E6
done		POP		0,0
		PREFIX		:

		PREFIX		Alloc:
X	  	IS	    	$0
:Alloc	  	PBNZ		:AVAIL,1F
	 	SET		X,:POOLMAX
		ADD		:POOLMAX,X,:nodeSize
		CMP		:t,:POOLMAX,:SEQMIN
		PBNP		:t,2F
		TRAP		0,:Halt,0        Overflow (no nodes left)
1H		SET	    	X,:AVAIL
		LDO		:AVAIL,:AVAIL,:LINK
2H	  	POP	    	1,0
	  	PREFIX    	:

;		Don't need you anymore!
;		PREFIX		Dealloc:
;	  	Doesn't check if trying to dealloc a node that was never alloc'd	  
;X	  	IS	      	$0
;:Dealloc  	STO	      	:AVAIL,X,:LINK
;1H	  	SET	      	:AVAIL,X
;	  	POP	    	0,0
;	  	PREFIX   	: