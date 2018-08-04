;	Floating point exponentiation using an algorithm from stack overflow:
;	https://stackoverflow.com/questions/3518973/floating-point-exponentiation-without-power-function
;	(With modifications to allow for calculating negative exponents)

;t 	  IS	    $255
;ZERO	  GREG	    0
FONE	  GREG	    #3FF0000000000000
FTWO	  GREG	    #4000000000000000
e	  GREG	    #4005BF0A8B145769
;base	  GREG	    #400B333333333333 3.4
;exp	  GREG	    #4004000000000000 2.5
;negFive	  GREG	    #C014000000000000 -5
;	  LOC	    #100
;Main	  SET	    $1,negFive
;	  PUSHJ	    $0,:σ
;	  SET	    $1,negFive
;	  SET	    $2,:ZERO
;	  PUSHJ	    $0,:pow
;	  TRAP	    0,Halt,0
	  
	  PREFIX    σ:
X	  IS	    $0
retaddr	  IS	    $1
last	  IS	    $2
:σ	  GET	    retaddr,:rJ
	  SET	    (last+1),:e
	  FSUB	    (last+2),:ZERO,X
	  PUSHJ	    last,:pow
	  FADD	    :t,:FONE,last
	  FDIV	    $0,:FONE,:t
	  PUT	    :rJ,retaddr
	  POP	    1,0
	  PREFIX    :

	  PREFIX    pow:
base	  IS	    $0
exp	  IS	    $1
retaddr	  IS	    $2
sqr	  IS	    $3
acc	  IS	    $4
low	  IS	    $5
mid	  IS	    $6
high	  IS	    $7
last	  IS	    $8
:pow	  GET	    retaddr,:rJ
	  BNZ	    exp,1F
	  SET	    $0,:FONE
	  POP	    1,0		PUT instruction not necessary since no subroutine is called.
1H	  FCMP	    :t,exp,:ZERO
	  BNN	    :t,1F		If exp is negative, return 1/(base^-exp) instead
	  SET	    (last+1),base
	  FSUB	    (last+2),:ZERO,exp
	  PUSHJ	    last,:pow
	  FDIV	    $0,:FONE,last
	  PUT	    :rJ,retaddr
	  POP	    1,0
1H	  FCMP	    :t,exp,:FONE
	  BN	    :t,1F
	  SET	    (last+1),base
	  FDIV	    (last+2),exp,:FTWO
	  PUSHJ	    last,:pow
	  FMUL	    $0,last,last
	  PUT	    :rJ,retaddr
	  POP	    1,0
1H	  SET	    low,0
	  SET	    high,:FONE
	  FSQRT	    sqr,base
	  SET	    acc,sqr
	  FDIV	    mid,high,:FTWO
3H	  FEQLE	    :t,mid,exp
	  BNZ	    :t,Done
	  FSQRT	    sqr,sqr
	  FCMP	    :t,mid,exp
	  BNN	    :t,lower
higher	  SET	    low,mid
	  FMUL	    acc,acc,sqr
	  JMP	    2F
lower	  SET	    high,mid
	  FDIV	    :t,:FONE,sqr
	  FMUL	    acc,acc,:t
2H	  FADD	    :t,low,high
	  FDIV	    mid,:t,:FTWO
	  JMP	    3B
Done	  SET	    $0,acc
	  PUT	    :rJ,retaddr
	  POP	    1,0
	  PREFIX    :