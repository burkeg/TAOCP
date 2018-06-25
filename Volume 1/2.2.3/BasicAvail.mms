; Basic implementation of a memory pool of links
; Assumes fixed size nodes without garbage collection
; Fixed capacity
; Each node is 2 consecutive octabytes, 1 for a pointer, 1 for data
; Following Method 1 described on page 256

t 	  IS	    $255
          LOC       Data_Segment
AVAIL	  GREG	    @
Pool	  OCTA	    @+16,0,@+32,0,@+48,0,@+64,0
	  OCTA	    @+16,0,@+32,0,@+48,0,@+64,0
	  OCTA	    @+16,0,@+32,0,@+48,0,@+64,0
	  OCTA	    @+16,0,@+32,0,@+48,0,@+64,0
	  OCTA	    @+16,0,@+32,0,@+48,0,@+64,0
	  OCTA	    @+16,0,@+32,0,@+48,0,@+64,0
	  OCTA	    @+16,0,@+32,0,@+48,0,@+64,0
	  OCTA	    @+16,0,@+32,0,@+48,0,@+64,0

	  LOC	    #100
Main	  PUSHJ	    $5,:Alloc
	  SET	    $0,$5
	  SET	    :t,1
	  STO	    :t,$0,8
	  
	  PUSHJ	    $5,:Alloc
	  SET	    $1,$5
	  SET	    :t,3
	  STO	    :t,$1,8
	  
	  PUSHJ	    $5,:Alloc
	  SET	    $2,$5
	  SET	    :t,7
	  STO	    :t,$2,8

	  SET	    $6,$1
	  PUSHJ	    $5,:Dealloc


	  PUSHJ	    $5,:Alloc
	  SET	    $4,$5
	  SET	    :t,18
	  STO	    :t,$4,8
	  
	  TRAP	    0,Halt,0

	  PREFIX    Alloc:
X	  IS	    $0
:Alloc	  LDO	    :t,:AVAIL
	  PBNZ	    :t,1F
	  TRAP	    0,:Halt,0        Overflow (no nodes left)
1H	  SET	    X,:AVAIL
	  LDO	    :AVAIL,:AVAIL
	  POP	    1,0
	  PREFIX    :
	  
	  PREFIX    Dealloc:
;	  Doesn't check if trying to dealloc a node that was never alloc'd	  
X	  IS	    $0
:Dealloc  STO	    :AVAIL,X
1H	  SET	    :AVAIL,X
	  POP	    0,0
	  PREFIX    :