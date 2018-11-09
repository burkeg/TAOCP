; Comparing Dynamic storage allocation methods
				
AVAIL		GREG	    
POOLMAX 	GREG
ZERO		GREG
				
t 		IS	    	$255
octaSize 	IS	    	8
capacity 	IS	    	100		max number of nodeSize-Byte nodes 
LINK		IS 	    	0
INFO		IS	    	8

		PREFIX    	node:
LLINK		IS	    	8*0
RLINK		IS	    	8*1
INFO		IS	    	8*2
		PREFIX    	:

		PREFIX		dynNode:
LINK		IS		8*0
SIZE		IS		8*1
		PREFIX		:

		LOC       	Data_Segment
		GREG	    	@
L0		OCTA      	0
		LOC	    	L0+_nodeSize*octaSize*capacity
		GREG	    	@
Linf		OCTA	    	0


		LOC		#100
Main		TRAP	    	0,Halt,0

		PREFIX		Alloc:
N		IS		$0
:CopyBinaryTree GET		retaddr,:rJ
		PUT		:rJ,retaddr
		POP		0,0

		PREFIX		Alloc:
N		IS		$0
P		IS		$1
Q		IS		$2
last		IS		$3
;	  	A1	    	[Initialize.]
:Alloc 		SET		Q,:AVAIL	Q <- LOC(AVAIL)
;	  	A2	    	[End of list?]
2H		LDO		P,Q,:dynNode:LINK	P <- LINK(Q)
		BNZ		P,3F			If P = Λ, terminate
		TRAP		0,:Halt,0		No room for N consecutive nodes!
;	  	A3	    	[Is SIZE enough?]
		
		POP		1,0
		
		PREFIX		Dealloc:
;	  	Doesn't check if trying to dealloc a node that was never alloc'd	  
P0	  	IS	      	$0
:Dealloc  	STO	      	:AVAIL,X,:LINK
1H	  	SET	      	:AVAIL,X
	  	POP	    	0,0
	  	PREFIX   	: