; Basic Binary Tree implementation right threads
				
AVAIL		GREG	    
POOLMAX 	GREG
SEQMIN		GREG
ZERO		GREG
				
t 		IS	    	$255
octaSize 	IS	    	8
capacity 	IS	    	9		max number of nodeSize-Byte nodes 
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
		LOC	    	@+_nodeSize*octaSize
		LOC	    	@+_nodeSize*octaSize*cols
L0		OCTA      	0
		LOC	    	L0+_nodeSize*octaSize*capacity
		GREG	    	@
Linf		OCTA	    	0


		LOC		#100
Main		LDA	    	POOLMAX,L0
		LDA	    	SEQMIN,Linf
		LDA		$1,T
		PUSHJ	    	$0,:ConstructTree
		LDA		$1,T
		PUSHJ		$0,:ThreadTree
		LDA		$1,T
		GETA		$2,:Visit
		PUSHJ		$0,:InorderThreadedFptr
		TRAP	    	0,Halt,0
 		
		PREFIX		InorderThreadedFptr:
T		IS		$0
fptr		IS		$1
retaddr		IS		$2
tmp		IS		$3
P		IS		$4
Q		IS		$5
last		IS		$6
:InorderThreadedFptr GET	retaddr,:rJ
		LDO		tmp,T
		BZ   		tmp,done		If the tree is empty, exit immediately 
1H		LDO		:t,tmp,:node:LLINK
		BZ		:t,firstNode
		SET		tmp,:t
		JMP		1B			This moves tmp to the first inorder node in the tree
firstNode	SET		P,tmp
1H		ADD		:t,T,1
		CMP		:t,P,:t		Check if P = tree head + 1 (the last P always has RLINK=1)
		BZ		:t,done
		SET		(last+1),P
		PUSHGO		last,fptr		Visit node
		SET		(last+1),P
		PUSHJ		last,:InorderSuccessor
		SET		Q,last
		SET		P,Q
		JMP		1B
done		PUT		:rJ,retaddr
		POP		0,0
		PREFIX		:

		PREFIX		InorderSuccessor:
P		IS		$0
Q		IS		$1
:InorderSuccessor LDO		Q,P,:node:RLINK
		SL		:t,Q,63
		BNZ		:t,done
1H		LDO		:t,Q,:node:LLINK
		BZ		:t,done
		LDO		Q,Q,:node:LLINK
		JMP		1B
done		SET		$0,Q
		POP		1,0
		PREFIX		:

		PREFIX		AddMostRightThreads:
T		IS		$0
retaddr		IS		$1
tmp		IS		$2
last		IS		$10
lastVisited	GREG
:AddMostRightThreads GET	retaddr,:rJ
		SET		tmp,lastVisited		If the last visited node existed, set its RLINK to T and RTAG to 1
		BZ		tmp,hasRight
		LDO		:t,tmp,:node:RLINK	Determine if RLINK is unused
		SR		:t,:t,1
		BP		:t,hasRight
		ADD		tmp,T,1
		STO		tmp,lastVisited,:node:RLINK	skip the first node	
hasRight	SET		lastVisited,T
		PUT		:rJ,retaddr
		POP		0,0
		PREFIX		:
		
		PREFIX		ThreadTree:
T		IS		$0
retaddr		IS		$1
tmp		IS		$2
last		IS		$10
:ThreadTree GET		retaddr,:rJ
		SET		:AddMostRightThreads:lastVisited,0
		LDO		(last+1),T
		GETA		(last+2),:AddMostRightThreads
		PUSHJ		last,:InorderFptr
		ADD		:t,T,1
		STO		:t,:AddMostRightThreads:lastVisited,:node:RLINK
		PUT		:rJ,retaddr
		POP		0,0
		PREFIX		:

		PREFIX		Visit:
T		IS		$0
retaddr		IS		$1
last		IS		$10
:Visit 		GET		retaddr,:rJ
		LDO		:t,T,:node:INFO
		PUT		:rJ,retaddr
		POP		0,0
		PREFIX		:

		PREFIX		Preorder:
T		IS		$0
retaddr		IS		$1
tmp		IS		$2
last		IS		$3
:Preorder 	GET		retaddr,:rJ
		SET		(last+1),T
		PUSHJ		last,:Visit
		LDO		:t,T,:node:LLINK
		SR		tmp,:t,1
		BZ		tmp,noLeft
		SET		(last+1),:t
		PUSHJ		last,:Preorder
noLeft          LDO		:t,T,:node:RLINK
		SR		tmp,:t,1
		BZ		tmp,noRight
		SET		(last+1),:t
		PUSHJ		last,:Preorder
noRight		PUT		:rJ,retaddr
		POP		0,0
		PREFIX		:

		PREFIX		Inorder:
T		IS		$0
retaddr		IS		$1
tmp		IS		$2
last		IS		$3
:Inorder 	GET		retaddr,:rJ
		LDO		:t,T,:node:LLINK
		SR		tmp,:t,1
		BZ		tmp,noLeft
		SET		(last+1),:t
		PUSHJ		last,:Inorder
noLeft		SET		(last+1),T
		PUSHJ		last,:Visit
		LDO		:t,T,:node:RLINK
		SR		tmp,:t,1
		BZ		tmp,noRight
		SET		(last+1),:t
		PUSHJ		last,:Inorder
noRight		PUT		:rJ,retaddr
		POP		0,0
		PREFIX		:

		PREFIX		Postorder:
T		IS		$0
retaddr		IS		$1
tmp		IS		$2
last		IS		$3
:Postorder 	GET		retaddr,:rJ
		LDO		:t,T,:node:LLINK
		SR		tmp,:t,1
		BZ		tmp,noLeft
		SET		(last+1),:t
		PUSHJ		last,:Postorder
noLeft          LDO		:t,T,:node:RLINK
		SR		tmp,:t,1
		BZ		tmp,noRight
		SET		(last+1),:t
		PUSHJ		last,:Postorder
noRight		SET		(last+1),T
		PUSHJ		last,:Visit
		PUT		:rJ,retaddr
		POP		0,0
		PREFIX		:
		
		PREFIX		PreorderFptr:
T		IS		$0
fptr		IS		$1
retaddr		IS		$2
tmp		IS		$3
last		IS		$4
:PreorderFptr 	GET		retaddr,:rJ
		SET		(last+1),T
		PUSHGO		last,fptr
		LDO		:t,T,:node:LLINK
		SR		tmp,:t,1
		BZ		tmp,noLeft
		SET		(last+1),:t
		SET		(last+2),fptr
		PUSHJ		last,:PreorderFptr
noLeft          LDO		:t,T,:node:RLINK
		SR		tmp,:t,1
		BZ		tmp,noRight
		SET		(last+1),:t
		SET		(last+2),fptr
		PUSHJ		last,:PreorderFptr
noRight		PUT		:rJ,retaddr
		POP		0,0
		PREFIX		:

		PREFIX		InorderFptr:
T		IS		$0
fptr		IS		$1
retaddr		IS		$2
tmp		IS		$3
last		IS		$4
:InorderFptr 	GET		retaddr,:rJ
		LDO		:t,T,:node:LLINK
		SR		tmp,:t,1
		BZ		tmp,noLeft
		SET		(last+1),:t
		SET		(last+2),fptr
		PUSHJ		last,:InorderFptr
noLeft		SET		(last+1),T
		PUSHGO		last,fptr
		LDO		:t,T,:node:RLINK
		SR		tmp,:t,1
		BZ		tmp,noRight
		SET		(last+1),:t
		SET		(last+2),fptr
		PUSHJ		last,:InorderFptr
noRight		PUT		:rJ,retaddr
		POP		0,0
		PREFIX		:

		PREFIX		PostorderFptr:
T		IS		$0
fptr		IS		$1
retaddr		IS		$2
tmp		IS		$3
last		IS		$4
:PostorderFptr 	GET		retaddr,:rJ
		LDO		:t,T,:node:LLINK
		SR		tmp,:t,1
		BZ		tmp,noLeft
		SET		(last+1),:t
		SET		(last+2),fptr
		PUSHJ		last,:PostorderFptr
noLeft          LDO		:t,T,:node:RLINK
		SR		tmp,:t,1
		BZ		tmp,noRight
		SET		(last+1),:t
		SET		(last+2),fptr
		PUSHJ		last,:PostorderFptr
noRight		SET		(last+1),T
		PUSHGO		last,fptr
		PUT		:rJ,retaddr
		POP		0,0
		PREFIX		:

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