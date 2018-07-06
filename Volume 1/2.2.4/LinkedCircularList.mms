; Basic implementation of a memory pool of links
; Assumes fixed size nodes without garbage collection
; Flexible capacity
; Each node is 2 consecutive octabytes, 1 for a pointer, 1 for data
; Following Method 2 described on page 257

AVAIL	  GREG	    
POOLMAX	  GREG
SEQMIN	  GREG

t 	  IS	    $255
c	  IS	    8*2		Nodesize, (max 256)
LINK	  IS 	    0
INFO	  IS	    8

          LOC       Data_Segment
	  GREG	    @
L0	  OCTA      0
	  LOC	    @+(16-(@%16))+c*10
	  GREG	    @
PTR	  OCTA	    0,0


Ptr	  IS	    $0
result	  IS	    $2

	  LOC	    #100
Main	  LDA	    Ptr,PTR
	  LDA	    POOLMAX,L0
	  LDA	    SEQMIN,PTR

	  SET	    (result+1),Ptr
	  SET	    (result+2),1
	  PUSHJ	    result,:InsertLeft
	  
	  SET	    (result+1),Ptr
	  SET	    (result+2),4
	  PUSHJ	    result,:InsertRight
	  
	  SET	    (result+1),Ptr
	  PUSHJ	    result,:DeleteLeft
	  SET	    result,result
	  TRAP	    0,Halt,0

	  PREFIX    InsertLeft:
; 	  Calling Sequence:
;	  SET	    $(X+1),PTR    Pointer to address that contains the PTR pointer
;	  SET	    $(X+2),Y	Data
;	  PUSHJ	    $(X),:InsertLeft	
PTR	  IS	    $0	
Y	  IS	    $1
retaddr	  IS	    $2
P	  IS	    $3
tmp2	  IS	    $4
:InsertLeft   GET   retaddr,:rJ
	  PUSHJ	    P,:Alloc    P ⇐ AVAIL
;	  INFO(P) ← Y (offset of 8 is specific data format)
	  STO	    Y,P,:INFO
;	  If PTR = Λ, then PTR ← LINK(P) ← P
	  LDO	    :t,PTR,:LINK       Value of PTR
	  PBNZ	    :t,1F
	  STO	    P,P,:LINK
	  STO	    P,PTR,:LINK
	  JMP	    2F
;	  LINK(P) ← LINK(PTR)
1H	  LDO	    tmp2,:t,:LINK      LINK(PTR)
	  STO	    tmp2,P,:LINK
;	  LINK(PTR) ← P
	  STO	    P,:t,:LINK
2H	  PUT	    :rJ,retaddr
	  POP	    0,0
	  PREFIX    :

	  PREFIX    InsertRight:
; 	  Calling Sequence:
;	  SET	    $(X+1),PTR    Pointer to address that contains the PTR pointer
;	  SET	    $(X+2),Y	  Data
;	  PUSHJ	    $(X),:InsertRight
PTR	  IS	    $0
Y	  IS	    $1
retaddr	  IS	    $2
P	  IS	    $3
tmp2	  IS	    $4
:InsertRight  GET   retaddr,:rJ
	  SET 	    (tmp2+1),PTR
	  SET	    (tmp2+2),Y
	  PUSHJ	    tmp2,:InsertLeft
	  LDO	    :t,PTR,:LINK
	  LDO	    P,:t,:LINK    tmp2 ← LINK(PTR)=P
	  STO	    P,PTR,:LINK
	  PUT	    :rJ,retaddr
	  POP	    1,0
	  PREFIX    :

	  PREFIX    DeleteLeft:
; 	  Calling Sequence:
;	  SET	    $(X+1),PTR    Pointer to address that contains the PTR pointer
;	  PUSHJ	    $(X),:DeleteLeft
PTR	  IS	    $0
Y	  IS	    $1
retaddr	  IS	    $2
PTRval	  IS	    $3
P	  IS	    $4
tmp	  IS	    $5
:DeleteLeft   GET   retaddr,:rJ
;	  If PTR = Λ, then UNDERFLOW
	  LDO	    PTRval,PTR,:LINK
	  PBNZ	    PTRval,1F
	  TRAP	    0,:Halt,0	  Error: UNDERFLOW!
;	  P ← LINK(PTR)
1H	  LDO	    P,PTRval,:LINK
;	  Y ← INFO(P)
	  LDO	    Y,P,:INFO
;	  LINK(PTR) ← LINK(P)
	  LDO	    :t,P,:LINK
	  STO	    :t,PTRval,:LINK
	  SET	    (tmp+1),P
	  PUSHJ	    tmp,:Dealloc
;	  If PTR = P, then PTR ← Λ
	  CMP	    :t,PTRval,P
	  PBNZ	    :t,2F
	  STO	    :t,PTR,:LINK   since this line is only executed when t=0, PTR ← Λ
2H	  SET	    $0,Y
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