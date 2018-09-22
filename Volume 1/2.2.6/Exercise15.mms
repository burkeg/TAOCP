; Exercise 15: Write a MIXAL program for Algorithm S. (Pivot step in a sparse matrix)

AVAIL	  GREG	    
POOLMAX	  GREG
SEQMIN	  GREG
ZERO	  GREG

t 	  IS	    $255
octaSize  IS	    8
capacity  IS	    2		max number of nodeSize-Byte nodes 
LINK	  IS 	    0
INFO	  IS	    8
_nodeSize IS	    5*octaSize
nodeSize  GREG	    _nodeSize

          LOC       Data_Segment
	  GREG	    @
L0	  OCTA      0
	  LOC	    L0+_nodeSize*capacity
	  GREG	    @
Linf	  OCTA	    0

ptr	  IS	    $1
	  LOC	    #100
Main	  LDA	    POOLMAX,L0
	  LDA	    SEQMIN,Linf
	  TRAP	    0,Halt,0

	  PREFIX    GenerateSpareMatrix:

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