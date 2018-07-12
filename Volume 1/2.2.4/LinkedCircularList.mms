; Basic implementation of a memory pool of links
; Assumes fixed size nodes without garbage collection
; Flexible capacity
; Each node is 2 consecutive octabytes, 1 for a pointer, 1 for data
; Following Method 2 described on page 257

AVAIL	  GREG	    
POOLMAX	  GREG
SEQMIN	  GREG
ZERO	  GREG

t 	  IS	    $255
c	  IS	    8*2		Nodesize, (max 256)
capacity  IS	    10		max number of c-Byte nodes 
LINK	  IS 	    0
INFO	  IS	    8

          LOC       Data_Segment
	  GREG	    @
L0	  OCTA      0
	  LOC	    @+((@%16)-16)+c*capacity
	  GREG	    @
PTR	  OCTA	    0,0


Ptr1	  IS	    $0
Ptr2	  IS	    $1
result	  IS	    $2

	  LOC	    #100
Main	  LDA	    Ptr1,PTR
	  ADD	    Ptr2,Ptr1,8
	  LDA	    POOLMAX,L0
	  LDA	    SEQMIN,PTR
	  SET	    (result+1),Ptr1
	  SET	    (result+2),1
	  PUSHJ	    result,:InsertLeft
	  SET	    (result+1),Ptr1
	  SET	    (result+2),2
	  PUSHJ	    result,:InsertRight
	  SET	    (result+1),Ptr1
	  SET	    (result+2),3
	  PUSHJ	    result,:InsertRight
	  SET	    (result+1),Ptr1
	  SET	    (result+2),4
	  PUSHJ	    result,:InsertRight
	  SET	    (result+1),Ptr1
	  SET	    (result+2),5
	  PUSHJ	    result,:InsertRight
	  TRAP	    0,Halt,0

	  PREFIX    Copy:
; 	  Calling Sequence:
;	  SET	    $(X+1),PTR    Pointer to address that contains the PTR pointer
;	  PUSHJ	    $(X),:Append	
PTR	  IS	    $0
PTRval	  IS	    $1
P	  IS	    $2
retaddr	  IS	    $3
result 	  IS	    $4
:Copy	  GET       retaddr,:rJ
	  LDO	    PTRval,PTR,:LINK
	  BZ	    PTRval,1F
	  SET	    P,PTRval
2H	  PUSHJ	    result,:Alloc
	  LDO	    :t,P,0
	  STO	    :t,result,0
	  LDO	    :t,P,8
	  STO	    :t,result,8
	  LDO	    :,P,0
1H	  PUT	    :rJ,retaddr
	  POP	    0,0
	  PREFIX    :

	  PREFIX    Append:
; 	  Calling Sequence:
;	  SET	    $(X+1),PTR1    Pointer to address that contains the PTR pointer
;	  SET	    $(X+2),PTR2    Pointer to address that contains the PTR pointer
;	  PUSHJ	    $(X),:Append	
PTR1	  IS	    $0
PTR2	  IS	    $1
PTR1val	  IS	    $2
PTR2val	  IS	    $3
P	  IS	    $4
retaddr	  IS	    $5
result 	  IS	    $6
:Append	  LDO	    PTR1val,PTR1,:LINK
	  LDO	    PTR2val,PTR2,:LINK
	  BZ	    PTR2val,1F		PTR2 ≠ Λ
	  BZ	    PTR1val,2F		PTR1 ≠ Λ
	  LDO	    P,PTR1val,:LINK	P ← PTR1
	  LDO	    :t,PTR2val,:LINK	get PTR2
	  STO	    :t,PTR1val,:LINK	PTR1 ← PTR2
	  STO	    P,PTR2val,:LINK	PTR1 ← P
2H	  STO	    PTR2val,PTR1,:LINK
	  STO	    :ZERO,PTR2,:LINK
1H	  POP	    0,0
	  PREFIX    :

	  PREFIX    Erase:
; 	  Calling Sequence:
;	  SET	    $(X+1),PTR    Pointer to address that contains the PTR pointer
;	  PUSHJ	    $(X),:Erase	
PTR	  IS	    $0
PTRval	  IS	    $1
P	  IS	    $2
retaddr	  IS	    $3
result 	  IS	    $4
:Erase    LDO	    PTRval,PTR,:LINK
	  BZ	    PTRval,1F
	  SET	    P,:AVAIL
	  LDO	    :AVAIL,PTRval,:LINK
	  STO	    P,PTRval,:LINK
	  STO	    :ZERO,PTR,:LINK	    
1H	  POP	    0,0
	  PREFIX    :
	  
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