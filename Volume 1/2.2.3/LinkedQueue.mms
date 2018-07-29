; Basic implementation of a memory pool of links
; Assumes fixed size nodes without garbage collection
; Flexible capacity
; Each node is 2 consecutive octabytes, 1 for a pointer, 1 for data
; Following Method 2 described on page 257

t 	  IS	    $255
c	  IS	    16		Nodesize, (max 256)
LINK	  IS 	    0
INFO	  IS	    8
          LOC       Data_Segment
AVAIL	  GREG	    0
POOLMAX	  GREG	    @
	  LOC	    @+16*10
	  GREG	    @
F	  OCTA	    0,0
R	  OCTA	    F,0
SEQMIN	  IS	    F


Front	  IS	    $0
Rear	  IS	    $1

	  LOC	    #100
Main	  LDA	    Front,F
	  LDA	    Rear,R

	  SET	    $3,1
	  SET	    $4,Front
	  SET	    $5,Rear
	  PUSHJ	    $2,:Insert

	  SET	    $3,2
	  SET	    $4,Front
	  SET	    $5,Rear
	  PUSHJ	    $2,:Insert
	  
	  SET	    $3,Front
	  SET	    $4,Rear
	  PUSHJ	    $2,:Delete
	  SET	    $2,$2
	  
	  SET	    $3,Front
	  SET	    $4,Rear
	  PUSHJ	    $2,:Delete
	  SET	    $2,$2

	  SET	    $3,4
	  SET	    $4,Front
	  SET	    $5,Rear
	  PUSHJ	    $2,:Insert

	  SET	    $3,4
	  SET	    $4,Front
	  SET	    $5,Rear
	  PUSHJ	    $2,:Insert

	  SET	    $3,4
	  SET	    $4,Front
	  SET	    $5,Rear
	  PUSHJ	    $2,:Insert

	  SET	    $3,4
	  SET	    $4,Front
	  SET	    $5,Rear
	  PUSHJ	    $2,:Insert

	  SET	    $3,4
	  SET	    $4,Front
	  SET	    $5,Rear
	  PUSHJ	    $2,:Insert

	  SET	    $3,4
	  SET	    $4,Front
	  SET	    $5,Rear
	  PUSHJ	    $2,:Insert

	  SET	    $3,4
	  SET	    $4,Front
	  SET	    $5,Rear
	  PUSHJ	    $2,:Insert

	  SET	    $3,4
	  SET	    $4,Front
	  SET	    $5,Rear
	  PUSHJ	    $2,:Insert

	  SET	    $3,4
	  SET	    $4,Front
	  SET	    $5,Rear
	  PUSHJ	    $2,:Insert

	  SET	    $3,4
	  SET	    $4,Front
	  SET	    $5,Rear
	  PUSHJ	    $2,:Insert

	  SET	    $3,4
	  SET	    $4,Front
	  SET	    $5,Rear
	  PUSHJ	    $2,:Insert
	  
;	  SET	    $3,Front
;	  SET	    $4,Rear
;	  PUSHJ	    $2,:Delete
;	  SET	    $2,$2
	  TRAP	    0,Halt,0

	  PREFIX    Insert:
; 	  Calling Sequence:
;	  SET	    $(X+1),Y	Data
;	  SET	    $(X+2),F    Pointer to address that contains the Front pointer
;	  SET	    $(X+3),R    Pointer to address that contains the Rear pointer
;	  PUSHJ	    $(X),:Push		
Y	  IS	    $0
F	  IS	    $1
R	  IS	    $2
retaddr	  IS	    $3
P	  IS	    $4
:Insert	  GET	    retaddr,:rJ
	  PUSHJ	    P,:Alloc    P ⇐ AVAIL
	  STO	    Y,P,:INFO    INFO(P) ← Y (offset of 8 is specific data format)
	  SET	    :t,0
	  STO	    :t,P,:LINK	LINK(P) ← Λ
	  LDO	    :t,R,:LINK
	  STO	    P,:t,:LINK	LINK(R) ← P
	  STO	    P,R,:LINK
	  PUT	    :rJ,retaddr
	  POP	    0,0
	  PREFIX    :
	  
	  PREFIX    Delete:
; 	  Calling Sequence:
;	  SET	    $(X+1),F    Pointer to address that contains the Front pointer
;	  SET	    $(X+2),R    Pointer to address that contains the Rear pointer
;	  PUSHJ	    $(X),:Pop
F	  IS	    $0
R	  IS	    $1
retaddr	  IS	    $2
Y	  IS	    $3
P	  IS	    $4
:Delete	  GET	    retaddr,:rJ
	  LDO	    :t,F,:LINK
	  PBNZ	    :t,1F	If F = Λ
	  TRAP	    0,:Halt,0	Error: Underflow!
1H	  LDO	    P,F,:LINK	P ← F
	  LDO	    :t,P,:LINK
	  STO	    :t,F,:LINK	F ← LINK(P)
	  LDO	    Y,P,:INFO	Y ← INFO(P)
	  PUSHJ	    Y,:Dealloc	This works because $(Y+1)=$(P), could be cleaner.
	  LDO	    :t,F,:LINK
	  PBNZ	    :t,2F	If F = Λ
	  STO	    F,R,:LINK	R ← LOC(F)
2H	  SET	    $0,Y
	  PUT	    :rJ,retaddr
	  POP	    1,0
	  PREFIX    :

	  PREFIX    Alloc:
X	  IS	    $0
:Alloc	  PBNZ	    :AVAIL,1F
	  SET	    X,:POOLMAX
	  ADD	    :POOLMAX,X,:c
	  LDA	    :t,:SEQMIN
	  CMP	    :t,:POOLMAX,:t
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