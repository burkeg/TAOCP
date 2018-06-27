; Topological Sort

AVAIL	  GREG	    
POOLMAX	  GREG
SEQMIN	  GREG
COUNT	  GREG
TOP	  GREG

t 	  IS	    $255
c	  IS	    16		Nodesize, (max 256)
LINK	  IS 	    0
INFO	  IS	    8
MaxNodes  IS	    10

          LOC       Data_Segment
	  GREG	    @
L0	  OCTA      0
	  LOC	    @+(16-@%16)+16*MaxNodes*MaxNodes
	  GREG	    @
COUNTLoc  OCTA	    0
TOPLoc	  OCTA	    0
QLINK	  IS	    COUNT

; 	  I'm lazy and putting the data directly into memory
;	  I could insted load a binary file with the same data
;	  and read it with fread using "Input" as a buffer
; 	  but again, I'm lazy...
	  LOC	    @+(16-@%16)+16*(MaxNodes+1)
	  GREG	    @
Input	  OCTA	    0,9          9 objects
	  OCTA	    9,2		 9≺2
	  OCTA	    3,7		 3≺7
	  OCTA	    7,5		 7≺5
	  OCTA	    5,8		 5≺8
	  OCTA	    8,6		 8≺6
	  OCTA	    4,6		 4≺6
	  OCTA	    1,3		 1≺3
	  OCTA	    7,4		 7≺4
	  OCTA	    9,5		 9≺5
	  OCTA	    2,8		 2≺8
	  OCTA	    0,0		 Terminating sequence

Top	  IS	    $0

	  LOC	    #100
Main	  LDA	    POOLMAX,L0
	  LDA	    SEQMIN,COUNTLoc
	  LDA	    TOP,TOPLoc
	  SET	    COUNT,SEQMIN
	  PUSHJ	    $0,:LoadInput
	  SET	    $0,$0
	  TRAP	    0,Halt,0

	  PREFIX    LoadInput:
;	  Calling Sequence:
;	  PUSHJ	    $(X),:LoadInput
;	  Returns N
N	  IS	    $0
retaddr	  IS	    $1
InPtr	  IS	    $2
j	  IS	    $3
k	  IS	    $4
jj	  IS	    $5
kk	  IS	    $6
:LoadInput GET	    retaddr,:rJ
	  LDA	    InPtr,:Input
	  LDO	    N,InPtr,:INFO
3H	  ADD	    InPtr,InPtr,16
	  LDO	    j,InPtr,:LINK
	  LDO	    k,InPtr,:INFO
	  CMP	    :t,j,k
	  PBNZ	    :t,1F
	  PBZ	    j,2F
	  TRAP	    0,:Halt,0	Cycle detected. j≺j
1H	  SL	    jj,j,4
	  SL	    kk,k,4
	  LDO	    :t,:COUNT,kk
	  ADD	    :t,:t,1
	  STO	    :t,:COUNT,kk	COUNT[k] ← COUNT[k]+1
	  SET	    (kk+2),k
	  LDA	    (kk+3),:TOP,jj
	  PUSHJ	    (kk+1),:Push
	  JMP	    3B
2H	  PUT	    :rJ,retaddr
	  POP	    1,0
	  PREFIX    :

	  PREFIX    Push:
; 	  Calling Sequence:
;	  SET	    $(X+1),Y	Data
;	  SET	    $(X+2),T    Pointer to address that contains the TOP pointer
;	  PUSHJ	    $(X),:Push		
Y	  IS	    $0
T	  IS	    $1
retaddr	  IS	    $2
P	  IS	    $3
:Push	  GET	    retaddr,:rJ
	  PUSHJ	    P,:Alloc    P ⇐ AVAIL
	  STO	    Y,P,:INFO    INFO(P) ← Y (offset of 8 is specific data format)
	  LDO	    :t,T,:LINK	
	  STO	    :t,P,:LINK	LINK(P) ← T
	  STO	    P,T,:LINK	T ← P
	  PUT	    :rJ,retaddr
	  POP	    0,0
	  PREFIX    :
	  
	  PREFIX    Pop:
; 	  Calling Sequence:
;	  SET	    $(X+1),T    Pointer to address that contains the TOP pointer
;	  PUSHJ	    $(X),:Pop
T	  IS	    $0
retaddr	  IS	    $1
Y	  IS	    $2
P	  IS	    $3
:Pop	  GET	    retaddr,:rJ
	  LDO	    :t,T,:LINK
	  PBNZ	    :t,1F	If T = Λ
	  TRAP	    0,:Halt,0	Error: Underflow!
1H	  LDO	    P,T,:LINK	P ← T
	  LDO	    :t,P,:LINK
	  STO	    :t,T,:LINK	T ← LINK(P)
	  LDO	    Y,P,:INFO	Y ← INFO(P)
	  SET	    $5,P
	  PUSHJ	    $4,:Dealloc
	  SET	    $0,Y
	  PUT	    :rJ,retaddr
	  POP	    1,0
	  PREFIX    :

	  PREFIX    Alloc:
X	  IS	    $0
:Alloc	  PBNZ	    :AVAIL,1F
	  SET	    X,:POOLMAX
	  ADD	    :POOLMAX,X,:c
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