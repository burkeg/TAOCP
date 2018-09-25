; Exercise 15: Write a MIXAL program for Algorithm S. (Pivot step in a sparse matrix)

AVAIL	  GREG	    
POOLMAX	  GREG
SEQMIN	  GREG
ZERO	  GREG
FONE	  GREG	    #3FF0000000000000
FTWO	  GREG	    #4000000000000000

t 	  IS	    $255
octaSize  IS	    8
capacity  IS	    6		max number of nodeSize-Byte nodes 
LINK	  IS 	    0
INFO	  IS	    8
_nodeSize IS	    5*octaSize
nodeSize  GREG	    _nodeSize
rows	  IS	    4
cols	  IS	    4
	  PREFIX    node:
LEFT	  IS	    8*0
UP	  IS	    8*1
ROW	  IS	    8*2
COL	  IS	    8*3
VAL	  IS	    8*4
	  PREFIX    :

          LOC       Data_Segment
BASECOL	  GREG	    @
	  LOC	    @+_nodeSize*cols
BASEROW	  GREG	    @	  
	  LOC	    @+_nodeSize*rows
PTR	  GREG	    @
	  LOC	    @+_nodeSize*cols
L0	  OCTA      0
	  LOC	    L0+_nodeSize*capacity
	  GREG	    @
Linf	  OCTA	    0

	  LOC	    #100
Main	  LDA	    POOLMAX,L0
	  LDA	    SEQMIN,Linf
	  PUSHJ	    $1,:GenerateSparseMatrix
	  PUSHJ	    $0,:AlgorithmS
	  TRAP	    0,Halt,0

	  PREFIX    AlgorithmS:
PIVOT	  IS	    $0
retaddr	  IS	    $1
ALPHA	  IS	    $2
I0	  IS	    $3
J0	  IS	    $3
P0	  IS	    $3
Q0	  IS	    $3
I	  IS	    $3
J	  IS	    $3
P	  IS		$3
P1	  IS	    $3
tmp	  IS	    $3
Ji	  IS	    $3
Jptr	  IS	    $3
JupPtr	  IS	    $3
X	  IS	    $3
last	  IS	    $10
:AlgorithmS GET retaddr,:rJ
;	  S1	    [Initialize.]
1H	  LDO	    :t,PIVOT,:node:VAL
	  FDIV	    ALPHA,:FONE,:t		ALPHA<-1.0/VAL(PIVOT)
	  STO	    :FONE,PIVOT,:node:VAL	VAL(PIVOT)<-1.0
	  LDO	    I0,PIVOT,:node:ROW
	  SUB	    :t,I0,1
	  MUL	    :t,:t,:_nodeSize		
	  LDA	    P0,:BASEROW,:t		P0<-LOC(BASEROW[I0])
	  LDO	    J0,PIVOT,:node:COL
	  SUB	    :t,J0,1
	  MUL	    :t,:t,:_nodeSize
	  LDA	    Q0,:BASECOL,:t		Q0<-LOC(BASECOL[J0])
;	  S2	    [Process pivot row.]
2H	  LDO	    P0,P0,:node:LEFT		P0<-LEFT(P0)
	  LDO	    J,P0,:node:COL		J<-COL(P0)
	  BN	    J,3F			if J<0
	  SUB	    :t,J,1
	  MUL	    :t,:t,:_nodeSize		convert J to index
	  LDA	    tmp,:BASECOL,:t		use 2nd temp variable because J is still needed as an index
	  STO	    tmp,:PTR,:t			PTR[J]<-LOC(BASECOL[J])
	  LDO	    :t,P0,:node:VAL		get VAL(P0)
	  FMUL	    :t,ALPHA,:t			compute ALPHA*VAL(P0)
	  STO	    :t,P0,:node:VAL		VAL(P0)<-ALPHA*VAL(P0)
	  JMP	    2B				repeat S2
;	  S3	    [Find new row.]
3H	  LDO	    Q0,Q0,:node:UP
	  LDO	    I,Q0,:node:ROW		I<-ROW(Q0)
	  BNN	    J,rowRemain			if J<0 terminate
	  TRAP	    0,:Halt,0			terminate.
rowRemain CMP	    :t,I,I0
	  BZ	    :t,3B			IF I=I0, repeat S3
	  SUB	    :t,I,1
	  MUL	    :t,:t,:_nodeSize		convert I to index
	  LDA	    P,:BASEROW,:t		P<-LOC(BASEROW(I])
	  LDO	    P1,P,:node:LEFT		P1<-LEFT(P)
;	  S4	    [Find new column.]
4H	  LDO	    P0,P0,:node:LEFT		P0<-LEFT(P0)
	  LDO	    J,P0,:node:COL		J<-COL(P0)
	  BNN	    J,JnonNeg			if J<0
	  LDO	    :t,Q0,:node:VAL		get VAL(Q0)
	  FMUL	    :t,ALPHA,:t			compute ALPHA*VAL(Q0)
	  FSUB	    :t,:ZERO,:t			compute -ALPHA*VAL(Q0)
	  STO	    :t,Q0,:node:VAL		VAL(Q0) <- -ALPHA*VAL(Q0)
	  JMP	    3B				return to S3
JnonNeg	  CMP	    :t,J,J0
	  BN	    :t,5F
	  JMP	    4B				If J=J0, repeat S4
;	  S5	    [Find I, J element.]
5H	  LDO	    :t,P1,:node:COL		get COL(P1)
	  CMP	    :t,:t,J
	  BN	    :t,9F			If COL(P1)>J
	  SET	    P,P1			P<-P1
	  LDO	    P1,P,:node:LEFT		P1<-LEFT(P)
	  JMP	    5B				Repeat S5
9H	  BZ	    :t,7F			If COL(P1)=J
	  JMP	    6F				go to S6
;	  S6	    [Insert I, J element.]
6H	  SUB	    :t,J,1
	  MUL	    Ji,:t,:_nodeSize		convert J to index	(Ji)
	  LDO	    Jptr,:PTR,Ji		get PTR[J]   		(Jptr)
	  LDO	    JupPtr,Jptr,:node:UP	get UP(PTR[J])		(JupPtr)
	  LDO	    :t,JupPtr,:node:ROW		get ROW(UP(PTR[J]))
	  CMP	    :t,:t,I
	  BN	    :t,insertNode
	  STO	    JupPtr,:PTR,Ji		PTR[J]<-UP(PTR[J])
	  JMP	    6B
insertNode PUSHJ    last,:Alloc
	  SET	    X,last			X<=AVAIL
	  STO	    :ZERO,X,:node:VAL		VAL(X)<-0
	  STO	    I,X,:node:ROW		ROW(X)<-I
	  STO	    J,X,:node:COL		COL(X)<-J
	  STO	    P1,X,:node:LEFT		LEFT(X)<-P1
	  STO	    JupPtr,X,:node:UP		UP(X)<-UP(PTR[J])
	  STO	    X,P,:node:LEFT		LEFT(P)<-X
	  STO	    X,Jptr,:node:UP		UP(PTR[J])<-X
	  SET	    P1,X			P1<-X
;	  S7	    [Pivot.]
7H	  LDO	    :t,Q0,:node:VAL		get VAL(Q0)
	  LDO	    tmp,P0,:node:VAL		get VAL(P0)
	  FMUL	    :t,:t,tmp			compute VAL(Q0)*VAL(P0)
	  LDO	    tmp,P1,:node:VAL		get VAL(P1)
	  FSUB	    :t,:t,tmp			compute VAL(P1)-VAL(Q0)*VAL(P0)
	  STO	    :t,P1,:node:VAL		VAL(P1)<-VAL(P1)-VAL(Q0)*VAL(P0)
	  FEQLE	    :t,:t,:ZERO			Check if VAL(P1) is equal to zero w.r.t. epsilon
	  BZ	    :t,8F			if VAL(P1)=0, go to S8
	  STO	    P1,:PTR,Ji			PTR[J]<-P1
	  SET	    P,P1			P<-P1
	  LDO	    P1,P,:node:LEFT		P1<-LEFT(P)
	  JMP	    4B
;	  S8	    [Delete I, J element.]
8H	  CMP	    :t,P1,JupPtr
	  BZ	    :t,finalDelete		if UP(PTR[J])!=P1
	  STO	    JupPtr,:PTR,Ji		PTR[J]<-UP(PTR[J])
	  JMP	    8B
finalDelete LDO	    :t,P1,:node:UP		get UP(P1)
	  STO	    :t,Jptr,:node:UP		UP(PTR[J])<-UP(P1)
	  LDO	    :t,P1,:node:LEFT		get LEFT(P1)
	  STO	    :t,P,:node:LEFT		LEFT(P)<-LEFT(P1)
	  SET	    (last+1),P1
	  PUSHJ	    last,:Dealloc		AVAIL<=P1
	  LDO	    P1,P,:node:LEFT		P1<-LEFT(P)
	  JMP	    4B
	  PUT	    :rJ,retaddr
	  PREFIX    :

	  PREFIX    GenerateSparseMatrix:
retaddr	  IS	    $0
node11	  IS	    $1
node21	  IS	    $2
node23	  IS	    $3
node41	  IS	    $4
node43	  IS	    $5
node44	  IS	    $6
val	  IS	    $7
last	  IS	    $10
:GenerateSparseMatrix GET retaddr,:rJ
          PUSHJ	    node11,:Alloc
; alloc nodes
	  SET	    :t,50
	  FLOT	    :t,:t
	  STO	    :t,node11,:node:VAL
	  SET	    :t,1
	  STO	    :t,node11,:node:ROW
	  SET	    :t,1
	  STO	    :t,node11,:node:COL
	  PUSHJ	    node21,:Alloc
	  SET	    :t,10
	  FLOT	    :t,:t
	  STO	    :t,node21,:node:VAL
	  SET	    :t,2
	  STO	    :t,node21,:node:ROW
	  SET	    :t,1
	  STO	    :t,node21,:node:COL
	  PUSHJ	    node23,:Alloc
	  SET	    :t,20
	  FLOT	    :t,:t
	  STO	    :t,node23,:node:VAL
	  SET	    :t,2
	  STO	    :t,node23,:node:ROW
	  SET	    :t,3
	  STO	    :t,node23,:node:COL
	  PUSHJ	    node41,:Alloc
	  SUB	    :t,:ZERO,30
	  FLOT	    :t,:t
	  STO	    :t,node41,:node:VAL
	  SET	    :t,4
	  STO	    :t,node41,:node:ROW
	  SET	    :t,1
	  STO	    :t,node41,:node:COL
	  PUSHJ	    node43,:Alloc
	  SUB	    :t,:ZERO,60
	  FLOT	    :t,:t
	  STO	    :t,node43,:node:VAL
	  SET	    :t,4
	  STO	    :t,node43,:node:ROW
	  SET	    :t,3
	  STO	    :t,node43,:node:COL
	  PUSHJ	    node44,:Alloc
	  SET	    :t,5
	  FLOT	    :t,:t
	  STO	    :t,node44,:node:VAL
	  SET	    :t,4
	  STO	    :t,node44,:node:ROW
	  SET	    :t,4
	  STO	    :t,node44,:node:COL
; BASECOL
	  SUB	    :t,:ZERO,1
	  SET	    last,:BASECOL
	  STO	    :t,last,:node:ROW
	  ADD	    last,last,:_nodeSize
	  STO	    :t,last,:node:ROW
	  ADD	    last,last,:_nodeSize
	  STO	    :t,last,:node:ROW
	  ADD	    last,last,:_nodeSize
	  STO	    :t,last,:node:ROW
; BASEROW
	  SUB	    :t,:ZERO,1
	  SET	    last,:BASEROW
	  STO	    :t,last,:node:COL
	  ADD	    last,last,:_nodeSize
	  STO	    :t,last,:node:COL
	  ADD	    last,last,:_nodeSize
	  STO	    :t,last,:node:COL
	  ADD	    last,last,:_nodeSize
	  STO	    :t,last,:node:COL
; row links
	  SET	    last,:BASEROW
	  STO	    node11,last,:node:LEFT
	  STO	    last,node11,:node:LEFT
	  ADD	    last,last,:_nodeSize
	  STO	    node23,last,:node:LEFT
	  STO	    last,node21,:node:LEFT
	  ADD	    last,last,:_nodeSize
	  STO	    last,last,:node:LEFT
	  ADD	    last,last,:_nodeSize
	  STO	    node44,last,:node:LEFT
	  STO	    last,node41,:node:LEFT
	  STO	    node21,node23,:node:LEFT
	  STO	    node43,node44,:node:LEFT
	  STO	    node41,node43,:node:LEFT
; col links
	  SET	    last,:BASECOL
	  STO	    node41,last,:node:UP
	  STO	    last,node11,:node:UP
	  ADD	    last,last,:_nodeSize
	  STO	    last,last,:node:UP
	  ADD	    last,last,:_nodeSize
	  STO	    node43,last,:node:UP
	  STO	    last,node23,:node:UP
	  ADD	    last,last,:_nodeSize
	  STO	    node44,last,:node:UP
	  STO	    last,node44,:node:UP
	  STO	    node21,node41,:node:UP
	  STO	    node11,node21,:node:UP
	  STO	    node23,node43,:node:UP
	  PUT	    :rJ,retaddr
	  SET	    $0,node21
	  POP	    1,0
	  PREFIX    :

	  PREFIX    Alloc:
X	  IS	    $0
:Alloc	  PBNZ	    :AVAIL,1F
	  SET	    X,:POOLMAX
	  ADD	    :POOLMAX,X,:nodeSize
	  CMP	    :t,:POOLMAX,:SEQMIN
	  PBNP	    :t,2F
	  TRAP	    0,:Halt,0        Overflow (no nodes left)
1H	  SET	    X,:AVAIL
	  LDO	    :AVAIL,:AVAIL,:LINK
2H	  POP	    1,0
	  PREFIX    :
	  
	  PREFIX    Dealloc:
;	  Doesn't check if trying to dealloc a node that was never alloc'd	  
X	  IS	    $0
:Dealloc  STO	    :AVAIL,X,:LINK
1H	  SET	    :AVAIL,X
	  POP	    0,0
	  PREFIX    :