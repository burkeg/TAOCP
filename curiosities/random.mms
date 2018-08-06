;	simple pseudo-random number generator
;	Disclaimer: I am still on volume 1 as of right now,
;	but I'm impatient and need a simple random number
;	now and I don't want to wait until I reach chapter 3.
t 	  IS	    $255
NEGONE	  GREG	    -1
	  LOC	    Data_Segment
seed	  IS	    1
	  LOC	    #100
Main	  PUSHJ	    $1,:rand
	  PUSHJ	    $2,:rand
	  PUSHJ	    $3,:rand
	  PUSHJ	    $4,:rand
	  PUSHJ	    $5,:rand
	  PUSHJ	    $6,:rand
	  PUSHJ	    $7,:rand
	  PUSHJ	    $8,:rand
	  PUSHJ	    $9,:rand
	  PUSHJ	    $10,:rand
	  FCMP	    :t,$1,$2
	  FCMP	    :t,$3,$4
	  FCMP	    :t,$5,$6
	  FCMP	    :t,$7,$8
	  FCMP	    :t,$9,$10
	  TRAP	    0,Halt,0
	  
	  PREFIX    rand:
X	  IS	    $0
a	  IS	    $1
c	  IS	    $2
last	  IS	    $3
:rand	  GETA	    last,X_
	  LDO	    X,last
	  GETA	    :t,a_
	  LDO	    a,:t
	  GETA	    :t,c_
	  LDO	    c,:t
	  MUL	    :t,a,X
	  ADD	    X,:t,c
	  STO	    X,last
	  FLOT	    X,X
	  SET	    :t,:NEGONE
	  ANDNH	    :t,#8000
	  FLOT	    :t,:t
	  FDIV	    X,X,:t
	  POP	    1,0
a_	  OCTA	    #5851F42D4C957F2D
c_	  OCTA	    #14057B7EF767814F
X_	  OCTA	    :seed
	  PREFIX    :