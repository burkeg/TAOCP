; Basic implementation of a memory pool of links
; Assumes fixed size nodes without garbage collection
; Fixed capacity
; Each node is 2 consecutive octabytes, 1 for a pointer, 1 for data
; Following Method 1 described on page 256

t 	  IS	    $255
c	  IS	    16		Nodesize, (max 256)
          LOC       Data_Segment
AVAIL	  GREG	    0
POOLMAX	  GREG	    @
	  LOC	    @+16*5
SEQMIN	  GREG	    @
	  BYTE	    "abcdefg: Please don't delete me!"

	  LOC	    #100
locA	  IS	    $0
locB	  IS	    $1
locC	  IS	    $2
locD	  IS	    $3
locE	  IS	    $4
locF	  IS	    $5
locG	  IS	    $6
locH	  IS	    $7
ret	  IS	    $8
arg	  IS	    $9
Main	  PUSHJ	    ret,:Alloc
	  SET	    locA,ret
	  SET	    :t,1
	  STO	    :t,locA,8
	  
	  PUSHJ	    ret,:Alloc
	  SET	    locB,ret
	  SET	    :t,2
	  STO	    :t,locB,8
	  
	  PUSHJ	    ret,:Alloc
	  SET	    locC,ret
	  SET	    :t,3
	  STO	    :t,locC,8

	  PUSHJ	    ret,:Alloc
	  SET	    locD,ret
	  SET	    :t,4
	  STO	    :t,locD,8


	  SET	    arg,locB
	  PUSHJ	    ret,:Dealloc

	  PUSHJ	    ret,:Alloc
	  SET	    locE,ret
	  SET	    :t,5
	  STO	    :t,locE,8

	  PUSHJ	    ret,:Alloc
	  SET	    locF,ret
	  SET	    :t,6
	  STO	    :t,locF,8

	  PUSHJ	    ret,:Alloc
	  SET	    locG,ret
	  SET	    :t,7
	  STO	    :t,locG,8

	  PUSHJ	    ret,:Alloc
	  SET	    locH,ret
	  SET	    :t,8
	  STO	    :t,locH,8

	  
	  TRAP	    0,Halt,0

	  PREFIX    Alloc:
X	  IS	    $0
:Alloc	  PBNZ	    :AVAIL,1F
	  SET	    X,:POOLMAX
	  ADD	    :POOLMAX,X,:c
	  CMP	    :t,:POOLMAX,:SEQMIN
	  PBNP	    :t,2F
	  TRAP	    0,:Halt,0        Overflow (no nodes left)
1H	  SET	    X,:AVAIL
	  LDO	    :AVAIL,:AVAIL
2H	  POP	    1,0
	  PREFIX    :
	  
	  PREFIX    Dealloc:
;	  Doesn't check if trying to dealloc a node that was never alloc'd	  
X	  IS	    $0
:Dealloc  STO	    :AVAIL,X
1H	  SET	    :AVAIL,X
	  POP	    0,0
	  PREFIX    :