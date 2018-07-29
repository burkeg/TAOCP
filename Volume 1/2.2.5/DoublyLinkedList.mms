; Implementation of doubly linked lists
AVAIL	  GREG	    
POOLMAX	  GREG
SEQMIN	  GREG
ZERO	  GREG
NEGONE	  GREG      -1

t 	  IS	    $255
c	  IS	    8*3		Nodesize(bytes), (max 256)
capacity  IS	    10		max number of c-Byte nodes 
LLINK	  IS 	    0
RLINK	  IS	    8
INFO	  IS	    16

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
	  PUSHJ	    result,:NewList
	  SET	    result,result
	  TRAP	    0,Halt,0

	  PREFIX    NewList:
;	  args:     none.
;	  returns:  newly allocated header node
X	  IS	    $0
retaddr	  IS	    $1     Saved so call stack is preserved
retval	  IS	    $2	   Last register in use
:NewList  GET	    retaddr,:rJ
	  PUSHJ	    retval,:Alloc
	  STO	    retval,retval,:LLINK
	  STO	    retval,retval,:RLINK
	  STO	    :NEGONE,retval,:INFO
	  SET	    X,retval
	  PUT	    :rJ,retaddr
	  POP	    1,0
	  PREFIX    :

	  PREFIX    InsertLeft:
	  
	  PREFIX

	  PREFIX    Alloc:
X	  IS	    $0
:Alloc	  PBNZ	    :AVAIL,1F
	  SET	    X,:POOLMAX
	  ADD	    :POOLMAX,X,:c
	  CMP	    :t,:POOLMAX,:SEQMIN
	  PBNP	    :t,2F
	  TRAP	    0,:Halt,0        Overflow (no nodes left)
1H	  SET	    X,:AVAIL
	  LDO	    :AVAIL,:AVAIL,:LLINK
2H	  POP	    1,0
	  PREFIX    :
	  
	  PREFIX    Dealloc:
;	  Doesn't check if trying to dealloc a node that was never alloc'd	  
X	  IS	    $0
:Dealloc  STO	    :AVAIL,X,:LLINK
1H	  SET	    :AVAIL,X
	  POP	    0,0
	  PREFIX    :