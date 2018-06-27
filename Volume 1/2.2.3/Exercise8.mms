;	  Reverse a linked linear list

t 	  IS	    $255
c	  IS	    16		Nodesize, (max 256)
LINK	  IS 	    0
INFO	  IS	    8
          LOC       Data_Segment
AVAIL	  GREG	    0
POOLMAX	  GREG	    @
	  LOC	    @+16*10
	  GREG	    @
T	  OCTA	    0,0
SEQMIN	  IS	    T


Top	  IS	    $0

	  LOC	    #100
Main	  LDA	    Top,T

;	  PUSH
	  SET	    $3,3
	  SET	    $4,Top
	  PUSHJ	    $2,:Push

;	  PUSH
	  SET	    $3,2
	  SET	    $4,Top
	  PUSHJ	    $2,:Push

;	  PUSH
	  SET	    $3,1
	  SET	    $4,Top
	  PUSHJ	    $2,:Push

;	  REVERSE
;	  SET	    $3,Top
;	  PUSHJ	    $2,:Reverse

;	  SET	    $3,Top
;	  PUSHJ	    $2,:Pop
;	  SET	    $2,$2

	  TRAP	    0,Halt,0

	  PREFIX    Reverse:
;	  Reverses a linked linear list
; 	  Calling Sequence:
;	  SET	    $(X+1),T
;	  PUSHJ	    $(X),:Reverse	
T	  IS	    $0
retaddr	  IS	    $1
Y	  IS	    $2
	  LOC	    @+(16-@%16)
tmp	  GREG	    @
	  OCTA	    0,0
:Reverse  GET	    retaddr,:rJ
2H	  LDO	    :t,T,:LINK
	  BZ	    :t,1F
	  SET	    $3,T
	  PUSHJ	    Y,:Pop
	  SET	    $3,Y
	  SET	    $4,tmp
	  PUSHJ	    $2,:Push
	  JMP	    2B
1H	  LDO	    :t,tmp,:LINK
	  STO	    :t,T,:LINK
	  PUT	    :rJ,retaddr
	  POP	    0,0
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