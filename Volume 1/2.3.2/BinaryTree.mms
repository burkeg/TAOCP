; Basic Binary Tree implementation without right threads
				
AVAIL		GREG	    
POOLMAX 	GREG
SEQMIN		GREG
ZERO		GREG
				
t 		IS	    	$255
octaSize 	IS	    	8
capacity 	IS	    	7		max number of nodeSize-Byte nodes 
LINK		IS 	    	0
INFO		IS	    	8
_nodeSize 	IS	    	3
nodeSize 	GREG	    	_nodeSize*octaSize
rows		IS	    	4
cols		IS	    	4
		PREFIX    	node:
LLINK		IS	    	8*0
RLINK		IS	    	8*1
INFO		IS	    	8*2
		PREFIX    	:

		LOC       	Data_Segment
		GREG	    	@
T		OCTA		0		
		LOC	    	@+_nodeSize*octaSize*cols
L0		OCTA      	0
		LOC	    	L0+_nodeSize*octaSize*capacity
		GREG	    	@
Linf		OCTA	    	0

		LOC		#100
Main		LDA	    	POOLMAX,L0
		LDA	    	SEQMIN,Linf
		PUSHJ	    	$0,:ConstructTree
		TRAP	    	0,Halt,0

;		Stores a pointer to the root at T
;                              A
;                             / \
;                            B   C
;                           /  /   \
;                          D  E     F
;                              \   / \
;                               G H   J
		PREFIX		ConstructTree:
T		IS		$0
retaddr		IS		$1
tmpLink		IS		$2
tmp1		IS		$3
tmp2		IS		$4
tmp3		IS		$5
last		IS		$6
:ConstructTree	GET		retaddr,:rJ
;
		PUSHJ		last,:Alloc
		SET		:t,'J'
		STO		:t,last,:node:INFO
		SET		tmp1,last
;		
		PUSHJ		last,:Alloc
		SET		:t,'H'
		STO		:t,last,:node:INFO
		SET		tmp2,last
;		
		PUSHJ		last,:Alloc
		SET		:t,'F'
		STO		:t,last,:node:INFO
		STO		tmp1,last,:node:RLINK
		STO		tmp2,last,:node:LLINK
		SET		tmp3,last
;		
		PUSHJ		last,:Alloc
		SET		:t,'G'
		STO		:t,last,:node:INFO
		SET		tmp1,last
;		
		PUSHJ		last,:Alloc
		SET		:t,'E'
		STO		:t,last,:node:INFO
		STO		tmp1,last,:node:RLINK
		SET		tmp2,last
;		
		PUSHJ		last,:Alloc
		SET		:t,'C'
		STO		:t,last,:node:INFO
		STO		tmp3,last,:node:RLINK
		STO		tmp2,last,:node:LLINK
		SET		tmp1,last
;		
		PUSHJ		last,:Alloc
		SET		:t,'D'
		STO		:t,last,:node:INFO
		SET		tmp2,last
;		
		PUSHJ		last,:Alloc
		SET		:t,'B'
		STO		:t,last,:node:INFO
		STO		tmp2,last,:node:LLINK
		SET		tmp3,last
;		
		PUSHJ		last,:Alloc
		SET		:t,'A'
		STO		:t,last,:node:INFO
		STO		tmp1,last,:node:RLINK
		STO		tmp3,last,:node:LLINK
;
		STO		last,T
		PUT	    	:rJ,retaddr
		POP		0,0
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
	  
		PREFIX		Dealloc:
;	  	Doesn't check if trying to dealloc a node that was never alloc'd	  
X	  	IS	      	$0
:Dealloc  	STO	      	:AVAIL,X,:LINK
1H	  	SET	      	:AVAIL,X
	  	POP	    	0,0
	  	PREFIX   	: