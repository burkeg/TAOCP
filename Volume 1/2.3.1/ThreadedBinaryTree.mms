; Basic Binary Tree implementation with threads
				
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
		STO		$1,$1,:node:RLINK
		PUSHJ	    	$0,:ConstructTree
		LDA		$1,T
		PUSHJ		$0,:ThreadTree
		LDA		$1,T
		GETA		$2,:Visit
		PUSHJ		$0,:InorderThreadedFptr
		TRAP	    	0,Halt,0

		PREFIX		AttachAsRightChild:
P		IS		$0
Q		IS		$1
tmp		IS		$2
:AttachAsRightChild LDO		:t,P,:node:RLINK
		STO		:t,Q,:node:RLINK	Copy RLINK(P) to Q
		SR		:t,Q,1
		SR		:t,:t,1
		STO		:t,P,:node:RLINK	RLINK(P) <- Q, RTAG(P) <- 0
		POP		0,0
		PREFIX		:

		PREFIX		AttachAsLeftChild:
P		IS		$0
Q		IS		$1
tmp		IS		$2
:AttachAsLeftChild LDO		:t,P,:node:LLINK
		STO		:t,Q,:node:LLINK	Copy LLINK(P) to Q
		SR		:t,Q,1
		SR		:t,:t,1
		STO		:t,P,:node:RLINK	RLINK(P) <- Q, RTAG(P) <- 0
		POP		0,0
		PREFIX		:

		PREFIX		InorderThreadedFptr:
T		IS		$0
fptr		IS		$1
retaddr		IS		$2
tmp		IS		$3
P		IS		$4
Q		IS		$5
last		IS		$6
:InorderThreadedFptr GET	retaddr,:rJ
		LDO		tmp,T,:node:LLINK
		BZ   		tmp,done		If the tree is empty, exit immediately 
1H		SET		(last+1),tmp
		PUSHJ		last,:HasLeftChild
		BZ		last,firstNode
		LDO		tmp,tmp,:node:LLINK
		JMP		1B			This moves tmp to the first inorder node in the tree
firstNode	SET		P,tmp
1H		SET		:t,T
		ORL		:t,#0001
		CMP		:t,P,:t		Check if P = tree head (as thread)
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
retaddr		IS		$1
Q		IS		$2
last		IS		$3
:InorderSuccessor GET		retaddr,:rJ
		LDO		Q,P,:node:RLINK
		SET		(last+1),P
		PUSHJ		last,:HasRightChild
		BZ		last,done
1H		SET		(last+1),Q
		PUSHJ		last,:HasLeftChild
		BZ		last,done
		LDO		Q,Q,:node:LLINK
		JMP		1B
done		SET		$0,Q
		PUT		:rJ,retaddr
		POP		1,0
		PREFIX		:
		
		PREFIX		InorderPredecessor:
P		IS		$0
retaddr		IS		$1
Q		IS		$2
last		IS		$3
:InorderPredecessor GET		retaddr,:rJ
		LDO		Q,P,:node:LLINK
		SET		(last+1),P
		PUSHJ		last,:HasLeftChild
		BZ		last,done
1H		SET		(last+1),Q
		PUSHJ		last,:HasRightChild 
		BZ		last,done
		LDO		Q,Q,:node:RLINK
		JMP		1B
done		SET		$0,Q
		PUT		:rJ,retaddr
		POP		1,0
		PREFIX		:

		PREFIX		AddThreads:
P		IS		$0
retaddr		IS		$1
tmp		IS		$2
last		IS		$10
lastVisited	GREG
:AddThreads 	GET		retaddr,:rJ
		SET		(last+1),P
		PUSHJ		last,:HasLeftChild
		BNZ		last,hasLeft			If P has a left child
		ORL		lastVisited,#0001
		STO		lastVisited,P,:node:LLINK	LLINK(P) <- lastVisited (as a thread)
hasLeft		SET		(last+1),lastVisited
		PUSHJ		last,:HasRightChild
		BNZ		last,hasRight			If lastVisited has a right child
		ORL		P,#0001
		STO		P,lastVisited,:node:RLINK	RLINK(lastVisited) <- P (as a thread)
hasRight	SET		lastVisited,P
		PUT		:rJ,retaddr
		POP		0,0
		PREFIX		:
		
		PREFIX		ThreadTree:
T		IS		$0
retaddr		IS		$1
tmp		IS		$2
last		IS		$10
:ThreadTree GET		retaddr,:rJ
		SET		:AddThreads:lastVisited,T
		LDO		(last+1),T
		GETA		(last+2),:AddThreads
		PUSHJ		last,:InorderFptr
		SET		tmp,T
		ANDNL		tmp,#0001
		SET		:t,:AddThreads:lastVisited
		ANDNL		:t,#0001
		CMP		:t,:t,tmp		Compare T to lastVisited, ignoring tags
		BZ		:t,emptyTree
		ORL		tmp,#0001
		STO		tmp,:AddThreads:lastVisited,:node:RLINK		RLINK(lastVisited) <- T (as a thread)
emptyTree	PUT		:rJ,retaddr
		POP		0,0
		PREFIX		:

		PREFIX		HasLeftChild:
;		This can be used in both threaded and unthreaded trees.
;		In a threaded tree, zero means LTAG(P)=1
P		IS		$0
:HasLeftChild	LDO		:t,P,:node:LLINK
		BZ		:t,no		if LLINK(P) is null, return no
		SL		:t,:t,63	otherwise return opposite of LTAG(P)
		BNZ		:t,no
yes		SET		$0,1
		POP		1,0
no		SET		$0,0
		POP		1,0
		PREFIX		:

		PREFIX		HasRightChild:
;		This can be used in both threaded and unthreaded trees.
;		In a threaded tree, zero means RTAG(P)=1
P		IS		$0
:HasRightChild	LDO		:t,P,:node:RLINK
		BZ		:t,no		if RLINK(P) is null, return no
		SL		:t,:t,63	otherwise return opposite of RTAG(P)
		BNZ		:t,no
yes		SET		$0,1
		POP		1,0
no		SET		$0,0
		POP		1,0
		PREFIX		:

		PREFIX		Visit:
T		IS		$0
retaddr		IS		$1
PS		IS		$2
P		IS		$3
SP		IS		$4
last		IS		$10
:Visit 		GET		retaddr,:rJ
		LDO		P,T,:node:INFO
		SET		(last+1),T
		PUSHJ		last,:InorderSuccessor
		LDO		PS,last,:node:INFO
		SET		(last+1),T
		PUSHJ		last,:InorderPredecessor
		LDO		SP,last,:node:INFO
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