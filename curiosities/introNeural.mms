; Basic, super inefficient neural net example

#define __NL__
#define ADD_TRAINING(InputUnit1,InputValue1,InputUnit2,InputValue2,OutputUnit,OutputValue) ;__NL__\
1H	  IS   	    InputUnit1 __NL__\
2H	  IS   	    InputValue1 __NL__\
3H	  IS   	    InputUnit2 __NL__\
4H	  IS   	    InputValue2 __NL__\
5H	  IS   	    OutputUnit __NL__\
6H	  IS   	    OutputValue __NL__\
	  SET	    (last+1),2__NL__\
	  SET	    (last+2),trainingSet__NL__\
	  PUSHJ	    last,:Push_2__NL__\
	  SET	    setPtr,last__NL__\
	  SET	    (last+1),2__NL__\
	  ADD	    subPtr,setPtr,:Y_1__NL__\
	  SET	    (last+2),subPtr__NL__\
	  PUSHJ	    last,:Push_2__NL__\
	  SET	    :t,1B-1__NL__\
	  MUL	    :t,:t,:UNIT_SIZE__NL__\
	  ADD	    :t,:t,:Unit_arr__NL__\
	  STO	    :t,last,:Y_1__NL__\
	  SETL	    :t,2B%(1<<16) 0-15__NL__\
	  INCML	    :t,(2B>>16)%(1<<32) 16-31__NL__\
	  INCMH	    :t,(2B>>32)%(1<<48) 32-47__NL__\
	  INCH	    :t,(2B>>48) 48-63__NL__\
	  STO	    :t,last,:Y_2__NL__\
	  SET	    (last+1),2__NL__\
	  SET	    (last+2),subPtr__NL__\
	  PUSHJ	    last,:Push_2__NL__\
	  SET	    :t,3B-1__NL__\
	  MUL	    :t,:t,:UNIT_SIZE__NL__\
	  ADD	    :t,:t,:Unit_arr__NL__\
	  STO	    :t,last,:Y_1__NL__\
	  SETL	    :t,4B%(1<<16) 0-15__NL__\
	  INCML	    :t,(4B>>16)%(1<<32) 16-31__NL__\
	  INCMH	    :t,(4B>>32)%(1<<48) 32-47__NL__\
	  INCH	    :t,(4B>>48) 48-63__NL__\
	  STO	    :t,last,:Y_2__NL__\
	  ADD	    subPtr,setPtr,:Y_2__NL__\
	  SET	    (last+1),2__NL__\
	  SET	    (last+2),subPtr__NL__\
	  PUSHJ	    last,:Push_2__NL__\
	  SET	    :t,5B-1__NL__\
	  MUL	    :t,:t,:UNIT_SIZE__NL__\
	  ADD	    :t,:t,:Unit_arr__NL__\
	  STO	    :t,last,:Y_1__NL__\
	  SETL	    :t,6B%(1<<16) 0-15__NL__\
	  INCML	    :t,(6B>>16)%(1<<32) 16-31__NL__\
	  INCMH	    :t,(6B>>32)%(1<<48) 32-47__NL__\
	  INCH	    :t,(6B>>48) 48-63__NL__\
	  STO	    :t,last,:Y_2

AVAIL	  GREG
POOLMAX	  GREG
SEQMIN	  GREG
AVAIL_2	  GREG
POOLMAX_2 GREG
SEQMIN_2  GREG
ZERO	  GREG
NEGONE	  GREG      -1
FONE	  GREG	    #3FF0000000000000
FTWO	  GREG	    #4000000000000000
e	  GREG	    #4005BF0A8B145769
STEP_SIZE GREG	    #3F847AE147AE147B    0.01  in 64-bit floating point
;STEP_SIZE GREG	    #3FC999999999999A    0.2   in 64-bit floating point
;STEP_SIZE GREG	    #3FF0000000000000    1     in 64-bit floating point
;STEP_SIZE GREG	    #3FF0000000000000    0.001 in 64-bit floating point
a_init	  GREG	    #3FEAE3C24D02DEC2
b_init	  GREG	    #BFB3960EFF7BEBF6
c_init	  GREG	    #BFEFAE147AE147AE

t 	  IS	    $255
NUM_GATES IS 	    4
NUM_UNITS IS 	    9
GATE_SIZE IS	    4*8
UNIT_SIZE IS	    5*8
c	  IS	    2*8		Nodesize(bytes), (max 256)
capacity  IS	    100		max number of c-Byte nodes 
c_2	  IS	    3*8		Nodesize(bytes), (max 256)
capacity_2 IS	    50		max number of c-Byte nodes 
LINK	  IS 	    0		location of NEXT pointer in a node
INFO	  IS	    8		octabyte of data in a 16-byte node
IN_UNITS  IS	    0		gate byte-offset: linked list containing all units going into a gate
OUT_UNIT  IS	    8		gate byte-offset: pointer to the unit going out of a gate
FWD_PTR	  IS	    16		gate byte-offset: forward propagation function pointer
BACK_PTR  IS 	    24		gate byte-offset: back propagation function pointer
VALUE	  IS	    0		unit byte-offset: value used during forward propagation
GRAD	  IS	    8		unit byte-offset: gradient used during back propagation
IS_PARAM  IS	    16		unit byte-offset: field specifying whether a unit is a parameter
IN_GATES  IS	    24		unit byte-offset: linked list containing all gates a unit is going into
OUT_GATE  IS	    32		unit byte-offset: pointer to the gate this unit is going out of
MAX_INPUTS IS	    5		number of units that are initialized before forward propagation
NUM_INPUTS IS	    2		number of input variables in training data
NUM_OUTPUTS IS	    1		number of output variables in training data
PARAM_UNIT IS	    8		1st octabyte of data in a 24-byte node
PARAM_VALUE IS	    16		2nd octabyte of data in a 24-byte node
Y_1	  IS	    8		1st octabyte of data in a 24-byte node
Y_2	  IS	    16		2nd octabyte of data in a 24-byte node
NUM_ITER  IS        #FF		number of times to redo the training data


          LOC       Data_Segment
Gate_arr  GREG	    @
1H	  OCTA	    0
	  LOC	    1B+GATE_SIZE*NUM_GATES
Unit_arr  GREG	    @
1H	  OCTA	    0
	  LOC	    1B+UNIT_SIZE*NUM_UNITS
COUNT	  GREG	    @
1H	  OCTA	    0
TOP	  GREG	    @
QLINK	  IS	    COUNT
	  LOC	    1B+(1+NUM_GATES+MAX_INPUTS)*16
TopOutput GREG	    @
1H	  OCTA	    0
	  LOC	    1B+NUM_GATES*8
	  GREG	    @
L0_pool	  OCTA      0
	  LOC	    @+c*capacity-8
	  GREG	    @
endOfPool OCTA	    0
L0_pool_2 IS	    endOfPool
	  LOC	    @+c_2*capacity_2-8
	  GREG	    @
endOfPool_2 OCTA    0
springParams OCTA   0
outputUnits OCTA    0
trainingSet OCTA    0
trainingStats OCTA  0
	  LOC 	    @+NUM_ITER*5*8-8

	  LOC	    #100
Main	  LDA	    POOLMAX,L0_pool
	  LDA	    SEQMIN,endOfPool
	  LDA	    POOLMAX_2,L0_pool_2
	  LDA	    SEQMIN_2,endOfPool_2
	  PUSHJ	    $0,:Init		Initialized the network data structure
	  PUSHJ	    $0,:TopSort		Determines a topoligical ordering of the nodes
;	  	    			in the network in order to know order to compute
;					forward prop and backprop.
	  PUSHJ	    $0,:InitTraining	Initializes the training data structure and loads
;	  	    			initial values for parameters
	  PUSHJ	    $0,:runTillAllCorrect
	  TRAP	    0,Halt,0

	  PREFIX    σ:	sigmoid
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

	  PREFIX    runTillAllCorrect:
retaddr	  IS	    $0
numCorrect IS	    $1
numTotal  IS	    $2
last	  IS	    $3
:runTillAllCorrect   GET	    retaddr,:rJ
	  SET	    :t,1    initialize to non-zero value
1H	  BZ	    :t,2F   
	  PUSHJ	    last,:Train
	  SET	    numCorrect,(last+1)
	  SET	    numTotal,last
	  CMP	    :t,numCorrect,numTotal
	  JMP	    1B
2H	  PUT	    :rJ,retaddr
	  POP	    0,0
	  PREFIX    :

	  PREFIX    Init:
retaddr	  IS	    $0
GateBase  IS	    $1
UnitBase  IS	    $2
gateI	  IS	    $4
gateN	  IS	    $5
unitI	  IS	    $6
unitN	  IS	    $7
gateAddr  IS	    $8
unitAddr  IS	    $9
fptrFw	  IS	    $11
fptrBw	  IS	    $12
retval	  IS	    $13
:Init	  GET	    retaddr,:rJ
	  LDA	    GateBase,:Gate_arr
	  LDA	    UnitBase,:Unit_arr
	  ADD	    gateN,:ZERO,4
	  ADD	    unitN,:ZERO,9
	  SET	    gateI,:ZERO
	  SET	    unitI,:ZERO
	  MUL	    gateAddr,gateI,:GATE_SIZE
	  MUL	    unitAddr,unitI,:UNIT_SIZE
	  ADD	    gateAddr,gateAddr,GateBase
	  ADD	    unitAddr,unitAddr,UnitBase
;
;
;---------
;	  Create gates
;
;	  Multiply Gate 1 init
	  GETA	    fptrFw,:Gate_Multiplication_2_fwd
	  GETA	    fptrBw,:Gate_Multiplication_2_back
	  STO	    fptrFw,gateAddr,:FWD_PTR
	  STO	    fptrBw,gateAddr,:BACK_PTR
;
	  ADD	    gateI,gateI,1
	  MUL	    gateAddr,gateI,:GATE_SIZE
	  ADD	    gateAddr,gateAddr,GateBase
;
;	  Multiply Gate 2 init
	  GETA	    fptrFw,:Gate_Multiplication_2_fwd
	  GETA	    fptrBw,:Gate_Multiplication_2_back
	  STO	    fptrFw,gateAddr,:FWD_PTR
	  STO	    fptrBw,gateAddr,:BACK_PTR
;
	  ADD	    gateI,gateI,1
	  MUL	    gateAddr,gateI,:GATE_SIZE
	  ADD	    gateAddr,gateAddr,GateBase
;
;	  Add Gate 3 init
	  GETA	    fptrFw,:Gate_Addition_2_fwd
	  GETA	    fptrBw,:Gate_Addition_2_back
	  STO	    fptrFw,gateAddr,:FWD_PTR
	  STO	    fptrBw,gateAddr,:BACK_PTR
;
	  ADD	    gateI,gateI,1
	  MUL	    gateAddr,gateI,:GATE_SIZE
	  ADD	    gateAddr,gateAddr,GateBase
;
;	  Add Gate 4 init
	  GETA	    fptrFw,:Gate_Addition_2_fwd
	  GETA	    fptrBw,:Gate_Addition_2_back
	  STO	    fptrFw,gateAddr,:FWD_PTR
	  STO	    fptrBw,gateAddr,:BACK_PTR
;
;
;---------
;	  Attach inputs
;
1H	  IS   	    1	Unit
2H	  IS   	    1	Gate
	  SET	    unitI,1B-1
	  SET	    gateI,2B-1
	  MUL	    gateAddr,gateI,:GATE_SIZE
	  MUL	    unitAddr,unitI,:UNIT_SIZE
	  ADD	    (retval+1),unitAddr,UnitBase
	  ADD	    (retval+2),gateAddr,GateBase
	  PUSHJ	    retval,:AttachAsInput
;
1H	  IS   	    2	Unit
2H	  IS   	    1	Gate
	  SET	    unitI,1B-1
	  SET	    gateI,2B-1
	  MUL	    gateAddr,gateI,:GATE_SIZE
	  MUL	    unitAddr,unitI,:UNIT_SIZE
	  ADD	    (retval+1),unitAddr,UnitBase
	  ADD	    (retval+2),gateAddr,GateBase
	  PUSHJ	    retval,:AttachAsInput
;
1H	  IS   	    3	Unit
2H	  IS   	    2	Gate
	  SET	    unitI,1B-1
	  SET	    gateI,2B-1
	  MUL	    gateAddr,gateI,:GATE_SIZE
	  MUL	    unitAddr,unitI,:UNIT_SIZE
	  ADD	    (retval+1),unitAddr,UnitBase
	  ADD	    (retval+2),gateAddr,GateBase
	  PUSHJ	    retval,:AttachAsInput
;
1H	  IS   	    4	Unit
2H	  IS   	    2	Gate
	  SET	    unitI,1B-1
	  SET	    gateI,2B-1
	  MUL	    gateAddr,gateI,:GATE_SIZE
	  MUL	    unitAddr,unitI,:UNIT_SIZE
	  ADD	    (retval+1),unitAddr,UnitBase
	  ADD	    (retval+2),gateAddr,GateBase
	  PUSHJ	    retval,:AttachAsInput
;
1H	  IS   	    5	Unit
2H	  IS   	    3	Gate
	  SET	    unitI,1B-1
	  SET	    gateI,2B-1
	  MUL	    gateAddr,gateI,:GATE_SIZE
	  MUL	    unitAddr,unitI,:UNIT_SIZE
	  ADD	    (retval+1),unitAddr,UnitBase
	  ADD	    (retval+2),gateAddr,GateBase
	  PUSHJ	    retval,:AttachAsInput
;
1H	  IS   	    6	Unit
2H	  IS   	    3	Gate
	  SET	    unitI,1B-1
	  SET	    gateI,2B-1
	  MUL	    gateAddr,gateI,:GATE_SIZE
	  MUL	    unitAddr,unitI,:UNIT_SIZE
	  ADD	    (retval+1),unitAddr,UnitBase
	  ADD	    (retval+2),gateAddr,GateBase
	  PUSHJ	    retval,:AttachAsInput
;
1H	  IS   	    7	Unit
2H	  IS   	    4	Gate
	  SET	    unitI,1B-1
	  SET	    gateI,2B-1
	  MUL	    gateAddr,gateI,:GATE_SIZE
	  MUL	    unitAddr,unitI,:UNIT_SIZE
	  ADD	    (retval+1),unitAddr,UnitBase
	  ADD	    (retval+2),gateAddr,GateBase
	  PUSHJ	    retval,:AttachAsInput
;
1H	  IS   	    8	Unit
2H	  IS   	    4	Gate
	  SET	    unitI,1B-1
	  SET	    gateI,2B-1
	  MUL	    gateAddr,gateI,:GATE_SIZE
	  MUL	    unitAddr,unitI,:UNIT_SIZE
	  ADD	    (retval+1),unitAddr,UnitBase
	  ADD	    (retval+2),gateAddr,GateBase
	  PUSHJ	    retval,:AttachAsInput
;	  
;1H	  IS   	    8	Unit	Test to see if breaks, should because it creates a cycle!
;2H	  IS   	    2	Gate
;	  SET	    unitI,1B-1
;	  SET	    gateI,2B-1
;	  MUL	    gateAddr,gateI,:GATE_SIZE
;	  MUL	    unitAddr,unitI,:UNIT_SIZE
;	  ADD	    (retval+1),unitAddr,UnitBase
;	  ADD	    (retval+2),gateAddr,GateBase
;	  PUSHJ	    retval,:AttachAsInput
;
;
;---------
;	  Attach outputs
;
1H	  IS   	    5	Unit
2H	  IS   	    1	Gate
	  SET	    unitI,1B-1
	  SET	    gateI,2B-1
	  MUL	    gateAddr,gateI,:GATE_SIZE
	  MUL	    unitAddr,unitI,:UNIT_SIZE
	  ADD	    (retval+1),unitAddr,UnitBase
	  ADD	    (retval+2),gateAddr,GateBase
	  PUSHJ	    retval,:AttachAsOutput
;
1H	  IS   	    6	Unit
2H	  IS   	    2	Gate
	  SET	    unitI,1B-1
	  SET	    gateI,2B-1
	  MUL	    gateAddr,gateI,:GATE_SIZE
	  MUL	    unitAddr,unitI,:UNIT_SIZE
	  ADD	    (retval+1),unitAddr,UnitBase
	  ADD	    (retval+2),gateAddr,GateBase
	  PUSHJ	    retval,:AttachAsOutput
;
1H	  IS   	    8	Unit
2H	  IS   	    3	Gate
	  SET	    unitI,1B-1
	  SET	    gateI,2B-1
	  MUL	    gateAddr,gateI,:GATE_SIZE
	  MUL	    unitAddr,unitI,:UNIT_SIZE
	  ADD	    (retval+1),unitAddr,UnitBase
	  ADD	    (retval+2),gateAddr,GateBase
	  PUSHJ	    retval,:AttachAsOutput
;
1H	  IS   	    9	Unit
2H	  IS   	    4	Gate
	  SET	    unitI,1B-1
	  SET	    gateI,2B-1
	  MUL	    gateAddr,gateI,:GATE_SIZE
	  MUL	    unitAddr,unitI,:UNIT_SIZE
	  ADD	    (retval+1),unitAddr,UnitBase
	  ADD	    (retval+2),gateAddr,GateBase
	  PUSHJ	    retval,:AttachAsOutput
;
;
;---------
;	  Assign inputs
;
1H	  IS   	    1	Unit
2H	  IS   	    1	Value
	  SET	    unitI,1B-1
	  SET	    :t,2B
	  MUL	    unitAddr,unitI,:UNIT_SIZE
	  ADD	    retval,unitAddr,UnitBase
;	  FLOT	    :t,:t
	  STO	    :t,retval,:VALUE
	  STO	    :a_init,retval,:VALUE
	  SET	    :t,1
	  STO	    :t,retval,:IS_PARAM
;
1H	  IS   	    2	Unit
2H	  IS   	    1	Value
	  SET	    unitI,1B-1
	  SUB	    :t,:ZERO,2B
	  MUL	    unitAddr,unitI,:UNIT_SIZE
	  ADD	    retval,unitAddr,UnitBase
	  FLOT	    :t,:t
	  STO	    :t,retval,:VALUE
;
1H	  IS   	    3	Unit
2H	  IS   	    -2	Value
	  SET	    unitI,1B-1
	  SET	    :t,2B
	  SL	    :t,:t,56
	  SR	    :t,:t,56
	  MUL	    unitAddr,unitI,:UNIT_SIZE
	  ADD	    retval,unitAddr,UnitBase
	  FLOT	    :t,:t
	  STO	    :t,retval,:VALUE
;	  STO	    :b_init,retval,:VALUE
	  SET	    :t,1
	  STO	    :t,retval,:IS_PARAM
;
1H	  IS   	    4	Unit
2H	  IS   	    3	Value
	  SET	    unitI,1B-1
	  SET	    :t,2B
	  MUL	    unitAddr,unitI,:UNIT_SIZE
	  ADD	    retval,unitAddr,UnitBase
	  FLOT	    :t,:t
	  STO	    :t,retval,:VALUE
;
1H	  IS   	    7	Unit
2H	  IS   	    -1	Value
	  SET	    unitI,1B-1
	  SET	    :t,2B
	  SL	    :t,:t,56
	  SR	    :t,:t,56
	  MUL	    unitAddr,unitI,:UNIT_SIZE
	  ADD	    retval,unitAddr,UnitBase
	  FLOT	    :t,:t
	  STO	    :t,retval,:VALUE
;	  STO	    :c_init,retval,:VALUE
	  SET	    :t,1
	  STO	    :t,retval,:IS_PARAM
;
;
;---------
;	  Assign gradient of output
;
1H	  IS   	    9	Unit
2H	  IS   	    1	Value
	  SET	    unitI,1B-1
	  SET	    :t,2B
	  MUL	    unitAddr,unitI,:UNIT_SIZE
	  ADD	    retval,unitAddr,UnitBase
	  FLOT	    :t,:t
	  STO	    :t,retval,:GRAD
;
	  PUT	    :rJ,retaddr
	  POP	    0,0
	  PREFIX    :

	  PREFIX    InitTraining:
retaddr	  IS	    $0
springs	  IS        $1
outputs	  IS        $2
trainingSet IS	    $3
tmp1 	  IS	    $4
tmp2 	  IS	    $5
setPtr 	  IS	    $6
subPtr 	  IS	    $7
last	  IS	    $8
:InitTraining GET  retaddr,:rJ
	  LDA   springs,:springParams
	  LDA       outputs,:outputUnits
	  LDA	    trainingSet,:trainingSet
;
;
;---------
;	  Assign "spring" parameters
;
1H	  IS   	    1	Unit
	  SET	    tmp1,1B-1
	  MUL	    tmp2,tmp1,:UNIT_SIZE
	  ADD	    (last+1),tmp2,:Unit_arr
	  SET	    (last+2),springs
	  PUSHJ	    last,:Push
;
1H	  IS   	    3	Unit
	  SET	    tmp1,1B-1
	  MUL	    tmp2,tmp1,:UNIT_SIZE
	  ADD	    (last+1),tmp2,:Unit_arr
	  SET	    (last+2),springs
	  PUSHJ	    last,:Push
;
;
;---------
;	  Assign output units
;
1H	  IS   	    9	Unit
assignOutUnits	  SET	    tmp1,1B-1
	  MUL	    tmp2,tmp1,:UNIT_SIZE
	  ADD	    (last+1),tmp2,:Unit_arr
	  SET	    (last+2),outputs
	  PUSHJ	    last,:Push
;
;
;---------
;	  Assign training set
; set 6	  2.1,-3 [-1]
	  ADD_TRAINING(2,#4000CCCCCCCCCCCD,4,#C008000000000000,9,#3FF0000000000000)
; set 5	  -1.0,1.1 [-1]
	  ADD_TRAINING(2,#BFF0000000000000,4,#3FF199999999999A,9,#BFF0000000000000)
; set 4	  -0.1,-1.0 [-1]
	  ADD_TRAINING(2,#BFB999999999999A,4,#BFF0000000000000,9,#BFF0000000000000)
; set 3	  3.0,0.1 [1]
	  ADD_TRAINING(2,#4008000000000000,4,#3FB999999999999A,9,#3FF0000000000000)
; set 2	  -0.3,-0.5 [-1]
	  ADD_TRAINING(2,#BFD3333333333333,4,#BFE0000000000000,9,#BFF0000000000000)
; set 1	  1.2,0.7 [1]
	  ADD_TRAINING(2,#3FF3333333333333,4,#3FE6666666666666,9,#3FF0000000000000)
;
	  PUT	    :rJ,retaddr
	  POP	    0,0
	  PREFIX    :

	  PREFIX    Train:
retaddr	  IS	    $0
currSet	  IS	    $1
currInput IS	    $2
currExpected IS	    $3
numAttempted IS	    $4
numCorrect   IS	    $5
last	     IS	    $10
:Train	  GET  	    retaddr,:rJ
	  LDA	    currSet,:trainingSet	gets address of trainingSet ptr
	  LDO	    currSet,currSet		gets address of trainingSet
	  SET	    numCorrect,0
	  SET	    numAttempted,0
1H	  BZ	    currSet,2F		training complete!
	  LDO	    currInput,currSet,:Y_1
	  LDO	    currExpected,currSet,:Y_2
	  SET	    (last+1),currExpected
	  SET	    (last+2),currInput
	  PUSHJ	    last,:TrainSingle
	  ADD	    numCorrect,numCorrect,last
	  ADD	    numAttempted,numAttempted,1
	  LDO	    currSet,currSet,:LINK
	  JMP	    1B
2H	  PUT	    :rJ,retaddr
	  SET	    $0,numCorrect
	  SET	    $1,numAttempted
	  POP	    2,0
	  PREFIX    :

	  PREFIX    TrainSingle:
;	  Calling Sequence:
;	  SET	    $(X+1),expected
;	  SET	    $(X+2),inputs
;	  PUSHJ	    $(X),:TrainSingle
expected  IS	    $0
inputs	  IS	    $1
retaddr	  IS	    $2
outputs   IS	    $3
limit	  IS   	    $4
current	  IS	    $5
unitVal	  IS	    $6
unitGrad  IS	    $7
guessedCorrect IS   $8
outputUnit IS	    $9
outputVal IS	    $10
last 	  IS	    $11
tmp	  IS	    last
:TrainSingle  GET    retaddr,:rJ
	  SET       :t,1
	  SUB	    :t,:ZERO,1
;	  Step 1)   clear all units values and gradients (except parameters)
	  PUSHJ	    last,:ResetUnits
;	  Step 2)   initialize inputs
	  SET  	    current,inputs
2H	  BZ	    current,3F
	  LDO  	    :t,current,:PARAM_UNIT
	  LDO  	    tmp,current,:PARAM_VALUE
	  STO	    tmp,:t,:VALUE
	  LDO	    current,current,:LINK
	  JMP	    2B
;	  Step 3)   Do forward propagation
3H	  PUSHJ	    last,:ForwardProp
;	  Requires redo of logic \/
;	  Step 4)   If data aligns with training set, GRAD = 1, else GRAD = -1
	  LDA  	    outputs,:outputUnits
	  LDO	    outputs,outputs
	  LDO  	    outputUnit,outputs,:INFO
	  LDO  	    expected,expected,:PARAM_VALUE
	  LDO  	    outputVal,outputUnit,:VALUE
	  FCMP	    :t,outputVal,expected
	  FCMP	    tmp,expected,:ZERO
	  CMP	    :t,:t,tmp
	  BZ	    :t,1F	If :t and tmp are equal then move on and don't do anything
	  FLOT	    :t,tmp
	  STO	    :t,outputUnit,:GRAD	   Set gradient appropriately
;	  Step 4a)  Determine if the guess was accurate
	  FCMP 	    :t,outputVal,:ZERO
	  FCMP	    tmp,expected,:ZERO
	  CMP	    guessedCorrect,:t,tmp	0 means correct
;	  Step 5)   Do Backprop
Backprop  PUSHJ	    last,:BackProp
;	  Step 6)   Add addition "spring" pulls
6H	  LDO	    (last+1),:springParams
	  PUSHJ	    last,:SpringPull
;	  Step 7)   Parameter update based off of STEP_SIZE
	  SET	    limit,:NUM_UNITS
	  MUL	    limit,limit,:UNIT_SIZE
	  ADD	    limit,limit,:Unit_arr
	  SET  	    current,:Unit_arr
7H	  LDO	    unitVal,current,:IS_PARAM
	  PBZ	    unitVal,8F
	  LDO	    unitGrad,current,:GRAD
	  FMUL	    unitGrad,unitGrad,:STEP_SIZE
	  LDO	    unitVal,current,:VALUE
	  FADD	    unitVal,unitVal,unitGrad	perform parameter update on a single parameter
	  STO	    unitVal,current,:VALUE	store the new calculated parameter back into VALUE
8H	  ADD	    current,current,:UNIT_SIZE
	  CMP	    :t,current,limit
	  PBN	    :t,7B
1H	  BNZ	    guessedCorrect,1F
	  SET	    $0,1	if guessedCorrect was 0, that means the guess was correct!
	  JMP	    2F
1H	  SET	    $0,0
2H	  PUT	    :rJ,retaddr
	  POP	    1,0
	  PREFIX    :

	  PREFIX    SpringPull:
;	  Calling Sequence:
;	  PUSHJ	    $(X),:SpringPull
current   IS	    $0
unitPtr	  IS	    $1
flotNegOne IS	    $2
tmp	  IS	    $3
:SpringPull  LDA    :t,:springParams
	  LDO	    current,:t
	  FLOT	    flotNegOne,:NEGONE
1H	  BZ	    current,2F
	  LDO	    unitPtr,current,:INFO
	  LDO	    tmp,unitPtr,:GRAD
	  LDO	    :t,unitPtr,:VALUE
	  FMUL	    :t,:t,flotNegOne	t <- Unit_Value*-1
	  FADD	    :t,tmp,:t
	  STO	    :t,unitPtr,:GRAD	GRAD -= VALUE
	  LDO	    current,current,:LINK
	  JMP	    1B
2H	  POP	    0,0
	  PREFIX    :

	  PREFIX    ResetUnits:
unitPtr	  IS	    $0
maxUnit	  IS	    $1
isParam	  IS	    $2
:ResetUnits SET	    unitPtr,:Unit_arr
	  SET	    :t,:UNIT_SIZE
	  MUL	    :t,:t,:NUM_UNITS
	  ADD	    maxUnit,:t,:Unit_arr
1H	  STO	    :ZERO,unitPtr,:GRAD
	  ADD	    unitPtr,unitPtr,:UNIT_SIZE
	  CMP	    :t,unitPtr,maxUnit
	  PBN	    :t,1B
	  POP	    0,0
	  PREFIX    :

	  PREFIX    ForwardProp:
;	  Calling Sequence:
;	  PUSHJ	    $(X),:ForwardProp
retaddr	  IS	    $0
gateIndex IS	    $1
gatePtr	  IS	    $3
fptr	  IS	    $4
outputPtr IS	    $5
count 	  IS	    $6
retval	  IS	    $7
:ForwardProp GET    retaddr,:rJ
	  SET	    gateIndex,0
	  SET	    count,0
	  SET	    outputPtr,:TopOutput
1H	  LDO	    :t,outputPtr	load the next gate in topological ordering
	  SUB	    :t,:t,1
	  MUL	    gateIndex,:t,:GATE_SIZE
	  LDA	    gatePtr,:Gate_arr,gateIndex    get address of gate
	  LDO	    fptr,gatePtr,:FWD_PTR
	  SET	    (retval+1),gatePtr
	  PUSHGO    retval,fptr
	  ADD	    outputPtr,outputPtr,8
	  ADD	    count,count,1
	  CMP	    :t,count,:NUM_GATES
	  PBN	    :t,1B
	  PUT	    :rJ,retaddr
	  POP	    0,0
	  PREFIX    :

	  PREFIX    BackProp:
;	  Calling Sequence:
;	  PUSHJ	    $(X),:BackProp
retaddr	  IS	    $0
gateIndex IS	    $1
gatePtr	  IS	    $3
fptr	  IS	    $4
outputPtr IS	    $5
count 	  IS	    $6
retval	  IS	    $7
:BackProp GET	    retaddr,:rJ
	  SET	    gateIndex,0
	  SET	    count,0
	  SET	    :t,:NUM_GATES-1
	  MUL	    :t,:t,8
	  ADD	    outputPtr,:t,:TopOutput	initialize outputPtr to the last gate in topological order
1H	  LDO	    :t,outputPtr	load the next gate in topological ordering
	  SUB	    :t,:t,1
	  MUL	    gateIndex,:t,:GATE_SIZE
	  LDA	    gatePtr,:Gate_arr,gateIndex    get address of gate
	  LDO	    fptr,gatePtr,:BACK_PTR
	  SET	    (retval+1),gatePtr
	  PUSHGO    retval,fptr
	  SUB	    outputPtr,outputPtr,8
	  ADD	    count,count,1
	  CMP	    :t,count,:NUM_GATES
	  PBN	    :t,1B
	  PUT	    :rJ,retaddr
	  POP	    0,0
	  PREFIX    :

	  PREFIX    TopSort:
;	  Calling Sequence:
;	  PUSHJ	    $(X),:TopSort
N	  IS	    $0
retaddr	  IS	    $1
kk	  IS	    $2
NN	  IS	    $3
P	  IS	    $4
F	  IS	    $5
R	  IS	    $6
TopOutput IS	    $7
last	  IS	    $10
:TopSort  GET	    retaddr,:rJ
	  SET	    TopOutput,:TopOutput
	  PUSHJ	    (last+1),:LoadInput
	  ADD	    N,(last+1),0	Assign N
;	  T4.	    [Scan for Zeros.]
	  SET	    :t,0
	  SL	    NN,N,4
	  SET	    R,0 		R ← 0
	  STO	    :ZERO,:QLINK,0    	QLINK[0] ← 0
	  SET	    kk,16
1H	  LDO	    :t,:COUNT,kk
	  BZ	    :t,3F
2H	  ADD	    kk,kk,16
	  CMP	    :t,kk,NN
	  BP	    :t,4F
	  JMP	    1B
3H	  SR	    last,kk,4
	  SL	    :t,R,4
	  STO	    last,:QLINK,:t
	  SET	    R,last
	  JMP	    2B
4H	  LDO	    F,:QLINK
;	  T5.	    [Output front of queue.]
9H	  CMP	    :t,F,:NUM_GATES
	  BP	    :t,Ignored	  
	  STO	    F,TopOutput
	  ADD	    TopOutput,TopOutput,8
Ignored	  BZ	    F,8F
	  SUB	    N,N,1
	  SL	    :t,F,4		Convert F to a byte offset
	  LDO	    P,:TOP,:t		P ← TOP[F]
;	  T6.	    [Erase relations.]
6H	  BZ	    P,7F
	  LDO	    :t,P,:INFO		:t ← SUC(P)
	  SL	    :t,:t,4		:t ← SUC(P) (as byte offset)
	  LDO	    last,:COUNT,:t
	  SUB	    last,last,1
	  STO	    last,:COUNT,:t	Decrement COUNT[SUC(P)]
	  BNZ	    last,5F
	  SL	    :t,R,4		:t ← R (as byte offset)
	  LDO	    last,P,:INFO 	last ← SUB(P)
	  STO	    last,:QLINK,:t	QLINK[R] ← SUC(P)
	  SET	    R,last		R ← SUC(P)
5H	  LDO	    P,P,:LINK		P ← NEXT(P)
	  JMP	    6B
;	  T7.	    [Remove from queue.]
7H	  SL	    last,F,4
	  LDO	    F,:QLINK,last
	  JMP	    9B
;	  T8.	    [End of process.]
8H	  BZ	    N,1F
	  TRAP	    0,:Halt,0	Error Topological Ordering not achieved. 
1H	  PUT	    :rJ,retaddr
	  POP	    0,0
	  PREFIX    :

	  PREFIX    LoadInput:
;	  Calling Sequence:
;	  PUSHJ	    $(X),:LoadInput
;	  Returns N
N	  IS	    $0
NumGates  IS	    $0
NumUnits  IS	    $1
retaddr	  IS	    $2
flag	  IS	    $3
arg1	  IS	    $4
arg2	  IS	    $5
arg3	  IS	    $6
arg4	  IS	    $7
j	  IS	    $8
k	  IS	    $9
jj	  IS	    $10
kk	  IS	    $12
last	  IS	    $13
:LoadInput GET	    retaddr,:rJ
	  SET	    NumGates,:NUM_GATES
	  SET	    NumUnits,:NUM_UNITS
	  SET	    flag,0
	  SET	    arg1,NumGates
	  SET	    arg2,0
	  LDO	    :t,:Gate_arr,:OUT_UNIT
	  LDO	    arg3,:t,:IN_GATES	Loads the pointer to the in_gates first element
3H	  CMP	    :t,flag,0
	  SET	    (last+1),arg1
	  SET	    (last+2),arg2
	  SET	    (last+3),arg3
	  SET	    (last+4),arg4
	  PBZ	    :t,4F
	  PUSHJ	    last,:ReadPairUnit
	  JMP	    5F
4H	  PUSHJ	    last,:ReadPairGate          Passes in: *,arg1,arg2,arg3,arg4,*
5H	  SET	    j,(last+5)			returns  : k,arg1,arg2,arg3,arg4,j
	  SET	    k,last
	  SET	    arg1,(last+1)
	  SET	    arg2,(last+2)
	  SET	    arg3,(last+3)
	  SET	    arg4,(last+4)
	  CMP	    :t,j,k
	  PBNZ	    :t,1F
	  PBZ	    j,2F	change back to 2F after debugging!
	  TRAP	    0,:Halt,0	Cycle detected. j≺j
1H	  SL	    jj,j,4
	  SL	    kk,k,4
	  LDO	    :t,:COUNT,kk
	  ADD	    :t,:t,1
	  STO	    :t,:COUNT,kk	COUNT[k] ← COUNT[k]+1
	  SET	    (last+1),k
	  LDA	    (last+2),:TOP,jj
	  PUSHJ	    (last+0),:Push
	  JMP	    3B
2H	  BNZ	    flag,6F
	  SET	    flag,1
	  SET	    arg1,NumUnits
	  SET	    arg2,0	index of unit array
	  LDO	    arg3,:Unit_arr,:IN_GATES	Loads the first gate that Unit[0] precedes
	  ADD	    arg4,NumGates,1		Make sure the inputs continue where gates left off
	  JMP 	    3B
6H	  SUB	    $0,arg4,1
	  PUT	    :rJ,retaddr
	  POP	    1,0
	  PREFIX    :

	  PREFIX    ReadPairGate:
numGates  IS	    $0
gateIndex IS	    $1
in_gates  IS	    $2
j	  IS	    $4
k	  IS	    $5
out_gate  IS	    $6
:ReadPairGate PBNZ  in_gates,1F		check if in_gates is null
	  ADD	    gateIndex,gateIndex,:GATE_SIZE	move gateIndex forward 1 gate
	  DIV	    :t,gateIndex,:GATE_SIZE
	  CMP	    :t,:t,numGates
	  PBN	    :t,2F		check if gateIndex is still in range
	  SET	    j,0			if it isn't, return 0,0
	  SET	    k,0
	  POP	    6,0
2H	  LDA	    :t,:Gate_arr,gateIndex
	  LDO	    :t,:t,:OUT_UNIT	get the unit who is the output to the current gate
	  LDO	    in_gates,:t,:IN_GATES   load the ptr to the first of in_gates
	  JMP	    :ReadPairGate
1H	  DIV	    :t,gateIndex,:GATE_SIZE
	  ADD	    j,:t,1		get the value of j
	  LDO	    :t,in_gates,:INFO	get the address of gate k
	  SUB	    :t,:t,:Gate_arr
	  DIV	    :t,:t,:GATE_SIZE
	  ADD	    k,:t,1
	  LDO	    in_gates,in_gates,:LINK
	  POP	    6,0
	  PREFIX    :

	  PREFIX    ReadPairUnit:
numUnits  IS	    $0
unitIndex IS	    $1
in_gates  IS	    $2
unitNum	  IS	    $3
j	  IS	    $4
k	  IS	    $5
:ReadPairUnit SET   j,0
	  SET	    k,0
	  POP	    6,0		No more input units
	  LDA   :t,:Unit_arr,unitIndex
	  LDO 	    :t,:t,:OUT_GATE
	  BNZ  	    :t,FIX		check if out_gate is null
	  BZ	    in_gates,FIX	check if in_gates is null
	  SET	    j,unitNum		get the value of j
	  LDO	    :t,in_gates,:INFO	get the address of gate k
	  SUB	    :t,:t,:Gate_arr
	  DIV	    :t,:t,:GATE_SIZE
	  ADD	    k,:t,1		get the value of k
	  LDO	    in_gates,in_gates,:LINK 	move in_gates to the next gate
	  	    ;check if in_gates is now null, if it is increment unitNum
	  BNZ	    in_gates,1F
	  ADD	    unitNum,unitNum,1
1H	  POP	    6,0
FIX	  ADD	    unitIndex,unitIndex,:UNIT_SIZE
	  DIV	    :t,unitIndex,:UNIT_SIZE
	  CMP	    :t,:t,numUnits
	  PBN	    :t,IN_RANGE
	  SET	    j,0
	  SET	    k,0
	  POP	    6,0		No more input units
IN_RANGE  LDA	    :t,:Unit_arr,unitIndex
	  LDO	    in_gates,:t,:IN_GATES   load the ptr to the first of in_gates
	  JMP	    :ReadPairUnit
	  PREFIX    :

	  PREFIX    Gate_arbi_1_fwd:
;	  Input format: ax+by+cz+...+offset in reverse order. Always assumes an odd number of inputs
;	  Reads offset, adds to accumulator
;	  Reads both c and z, multiplies and adds to accumulator
;	  Repeates on all remaining elements 2 at a time until none left
;	  Computes sigmoid on the accumulator
Gate	  IS	    $0
retaddr	  IS	    $1
acc	  IS	    $2	accumulates the expression
currUnit  IS	    $3
param	  IS	    $4
var	  IS	    $5
last	  IS	    $10
:Gate_arbi_fwd	GET retaddr,:rJ
	  LDO	    currUnit,Gate,:IN_UNITS  loads head of in_units
	  LDO	    :t,currUnit,:INFO
	  LDO	    acc,:t,:VALUE
	  LDO	    currUnit,currUnit,:LINK
nextPair  BZ	    currUnit,sumDone
	  LDO	    :t,currUnit,:INFO
	  LDO	    var,:t,:VALUE
	  LDO	    currUnit,currUnit,:LINK
	  LDO	    :t,currUnit,:INFO
	  LDO	    param,:t,:VALUE
	  LDO	    currUnit,currUnit,:LINK
	  FMUL	    :t,param,var
	  FADD	    acc,acc,:t		acc+=a*x where a is a parameter and x is a variable
	  JMP	    nextPair
sumDone	  SET	    (last+1),acc
	  PUSHJ	    last,:σ
	  LDO	    :t,Gate,:OUT_UNIT
	  STO	    last,:t,:VALUE
	  PUT  	    :rJ,retaddr
	  PREFIX    :

	  PREFIX    Gate_arbi_1_back:
;	  Input format: ax+by+cz+...+offset in reverse order. Always assumes an odd number of inputs
;	  Reads offset, adds σ(...)*(1-σ(...)) to gradient
;	  Reads both c and z, adds σ(...)*(1-σ(...))*z to gradient of c and σ(...)*(1-σ(...))*c to gradient of z
;	  Repeates on all remaining elements 2 at a time until none left
Gate	  IS	    $0
retaddr	  IS	    $1
currUnit  IS	    $2
currUnitPtr IS	    $3
s	  IS	    $4  output of sigmoid function
ds	  IS	    $5
param	  IS	    $6	parameter such as a,b,c
var	  IS	    $7  variable such as x,y,z
dparam	  IS	    $8	parameter such as a,b,c
dvar	  IS	    $9  variable such as x,y,z
paramPtr  IS	    $10
varPtr	  IS	    $11
last	  IS	    $12
:Gate_arbi_back	GET retaddr,:rJ
	  LDO	    :t,Gate,:OUT_UNIT
	  LDO	    s,:t,:VALUE		computes σ(ax+by+cz+...+offset)
	  FSUB	    :t,:FONE,s
	  FMUL	    ds,:t,s	        computes σ(...)*(1-σ(...))
	  LDO	    currUnit,Gate,:IN_UNITS  loads head of in_units
	  LDO	    currUnitPtr,currUnit,:INFO
	  LDO	    :t,currUnitPtr,:GRAD	load current gradient
	  FADD	    :t,:t,ds
	  STO	    :t,currUnitPtr,:GRAD	offset.grad+=ds
	  LDO	    currUnit,currUnit,:LINK
nextPair  BZ	    currUnit,sumDone
	  LDO	    varPtr,currUnit,:INFO
	  LDO	    var,varPtr,:VALUE
	  LDO	    currUnit,currUnit,:LINK
	  LDO	    paramPtr,currUnit,:INFO
	  LDO	    param,paramPtr,:VALUE
	  LDO	    currUnit,currUnit,:LINK
	  LDO	    :t,varPtr,:GRAD
	  FMUL	    dvar,param,ds
	  FADD	    :t,dvar,:t		var.grad+=param.value*ds
	  STO	    :t,varPtr,:GRAD
	  LDO	    :t,paramPtr,:GRAD
	  FMUL	    dparam,var,ds
	  FADD	    :t,dparam,:t		param.grad+=var.value*ds
	  STO	    :t,varPtr,:GRAD
	  JMP	    nextPair
sumDone	  PUT  	    :rJ,retaddr
	  PREFIX    :

	  PREFIX    Gate_Addition_2_fwd:
Gate	  IS	    $0
a	  IS	    $1
b	  IS	    $2
tmp	  IS	    $3
:Gate_Addition_2_fwd	LDO   tmp,Gate,:IN_UNITS  loads head of in_units
	  LDO	    :t,tmp,:INFO     loads ptr to in unit
	  LDO	    a,:t,:VALUE	     loads value of in unit
	  LDO	    tmp,tmp,:LINK    loads next of in_units
	  LDO	    :t,tmp,:INFO     loads ptr to in unit
	  LDO	    b,:t,:VALUE	     loads value of in unit
	  FADD	    tmp,a,b	     calculates out unit value
	  LDO	    :t,Gate,:OUT_UNIT   loads ptr to out unit
	  STO	    tmp,:t,:VALUE    stores a+b to out unit value 
	  POP	    0,0
	  PREFIX    :

	  PREFIX    Gate_Addition_2_back:
	  ; f(x)=a+b
	  ; da=1*dx
	  ; db=1*dx
Gate	  IS	    $0
unit_a	  IS	    $1
unit_b	  IS	    $2
dx	  IS	    $3
floatOne  IS	    $4
da	  IS	    $5
db	  IS	    $6
tmp	  IS	    $7
:Gate_Addition_2_back SET floatOne,1
	  FLOT	    floatOne,floatOne
	  LDO	    tmp,Gate,:OUT_UNIT
	  LDO	    dx,tmp,:GRAD		load dx
	  LDO       tmp,Gate,:IN_UNITS  	loads head of in_units
          LDO	    unit_a,tmp,:INFO
	  LDO	    tmp,tmp,:LINK
          LDO	    unit_b,tmp,:INFO
	  LDO	    tmp,unit_a,:GRAD
	  FMUL	    da,floatOne,dx
	  FADD	    tmp,tmp,da
	  STO	    tmp,unit_a,:GRAD
	  LDO	    tmp,unit_b,:GRAD
	  FMUL	    db,floatOne,dx
	  FADD	    tmp,tmp,db
	  STO	    tmp,unit_b,:GRAD
	  POP	    0,0
	  PREFIX    :

	  PREFIX    Gate_Multiplication_2_fwd:
Gate	  IS	    $0
a	  IS	    $1
b	  IS	    $2
tmp	  IS	    $3
:Gate_Multiplication_2_fwd	LDO   tmp,Gate,:IN_UNITS  loads head of in_units
	  LDO	    :t,tmp,:INFO     loads ptr to in unit
	  LDO	    a,:t,:VALUE	     loads value of in unit
	  LDO	    tmp,tmp,:LINK    loads next of in_units
	  LDO	    :t,tmp,:INFO     loads ptr to in unit
	  LDO	    b,:t,:VALUE	     loads value of in unit
	  FMUL	    tmp,a,b	     calculates out unit value
	  LDO	    :t,Gate,:OUT_UNIT   loads ptr to out unit
	  STO	    tmp,:t,:VALUE    stores a+b to out unit value 
	  POP	    0,0
	  PREFIX    :

	  PREFIX    Gate_Multiplication_2_back:
	  ; f(x)=a*b
	  ; da=b*dx
	  ; db=a*dx
Gate	  IS	    $0
unit_a	  IS	    $1
unit_b	  IS	    $2
a	  IS	    $3
b	  IS	    $4
dx	  IS	    $5
floatOne  IS	    $6
da	  IS	    $7
db	  IS	    $8
tmp	  IS	    $9
:Gate_Multiplication_2_back LDO	    tmp,Gate,:OUT_UNIT
          LDO	    dx,tmp,:GRAD		load dx
          LDO       tmp,Gate,:IN_UNITS  	loads head of in_units
          LDO	    unit_a,tmp,:INFO
          LDO	    a,unit_a,:VALUE
          LDO	    tmp,tmp,:LINK
          LDO	    unit_b,tmp,:INFO
          LDO	    b,unit_b,:VALUE
          LDO	    tmp,unit_a,:GRAD
          FMUL	    da,b,dx
          FADD	    tmp,tmp,da
          STO	    tmp,unit_a,:GRAD
          LDO	    tmp,unit_b,:GRAD
          FMUL	    db,a,dx
          FADD	    tmp,tmp,db
          STO	    tmp,unit_b,:GRAD
          POP	    0,0
          PREFIX    :

	  PREFIX    AttachAsInput:
Unit	  IS	    $0
Gate	  IS	    $1
retaddr	  IS	    $2
retval	  IS	    $3
:AttachAsInput GET  retaddr,:rJ
          SET  	    (retval+1),Gate
          ADD	    (retval+2),Unit,:IN_GATES
          PUSHJ	    retval,:Push
          SET  	    (retval+1),Unit
          ADD	    (retval+2),Gate,:IN_UNITS
          PUSHJ	    retval,:Push
          PUT	    :rJ,retaddr
          POP	    0,0
          PREFIX    :

	  PREFIX    AttachAsOutput:
Unit	  IS	    $0
Gate	  IS	    $1
retaddr	  IS	    $2
retval	  IS	    $3
:AttachAsOutput     STO	    Unit,Gate,:OUT_UNIT
          STO	    Gate,Unit,:OUT_GATE
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

	  PREFIX    PushArbi:
; 	  Calling Sequence:
;	  SET	    $(X+1),NumBytes	number of octabytes being pushed
;	  SET	    $(X+2),T    Pointer to address that contains the TOP pointer
;	  PUSHJ	    $(X),:PushArbi		
NumBytes  IS	    $0
T	  IS	    $1
retaddr	  IS	    $2
P	  IS	    $3
:PushArbi GET	    retaddr,:rJ
	  SET	    (P+1),NumBytes
          PUSHJ	    P,:AllocArbi    P ⇐ AVAIL
          LDO	    :t,T,:LINK	
          STO	    :t,P,:LINK	LINK(P) ← T
          STO	    P,T,:LINK	T ← P
	  SET	    $0,P
          PUT	    :rJ,retaddr
          POP	    1,0
          PREFIX    :

	  PREFIX    Push_2:
; 	  Calling Sequence:
;	  SET	    $(X+1),nothing
;	  SET	    $(X+2),T    Pointer to address that contains the TOP pointer
;	  PUSHJ	    $(X),:PushArbi		
NumBytes  IS	    $0
T	  IS	    $1
retaddr	  IS	    $2
P	  IS	    $3
:Push_2 GET	    retaddr,:rJ
          PUSHJ	    P,:Alloc_2    P ⇐ AVAIL
          LDO	    :t,T,:LINK	
          STO	    :t,P,:LINK	LINK(P) ← T
          STO	    P,T,:LINK	T ← P
	  SET	    $0,P
          PUT	    :rJ,retaddr
          POP	    1,0
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
          CMP	    :t,:POOLMAX,:SEQMIN
          PBNP	    :t,2F
          TRAP	    0,:Halt,0        Overflow (no nodes left)
1H	  SET	    X,:AVAIL
          LDO	    :AVAIL,:AVAIL,:LINK
2H	  POP	    1,0
          PREFIX    :

          PREFIX    Alloc_2:
X	  IS	    $0
:Alloc_2  PBNZ	    :AVAIL_2,1F
          SET	    X,:POOLMAX_2
          ADD	    :POOLMAX_2,X,:c_2
          CMP	    :t,:POOLMAX_2,:SEQMIN_2
          PBNP	    :t,2F
          TRAP	    0,:Halt,0        Overflow (no nodes left)_2
1H	  SET	    X,:AVAIL_2
          LDO	    :AVAIL_2,:AVAIL_2,:LINK
2H	  POP	    1,0
          PREFIX    :

          PREFIX    AllocArbi:
size	  IS	    $0	size of data in octabytes
X	  IS	    $1
:AllocArbi PBNZ	    :AVAIL,1F
          SET	    X,:POOLMAX
	  ADD	    size,size,1
	  SL	    :t,size,3
          ADD	    :POOLMAX,X,:t
          CMP	    :t,:POOLMAX,:SEQMIN
          PBNP	    :t,2F
          TRAP	    0,:Halt,0        Overflow (no nodes left)
1H	  SET	    X,:AVAIL
          LDO	    :AVAIL,:AVAIL,:LINK
2H	  SET	    $0,X
	  POP	    1,0
          PREFIX    :

	  PREFIX    Dealloc:
;	  Doesn't check if trying to dealloc a node that was never alloc'd	  
X	  IS	    $0
:Dealloc  STO	    :AVAIL,X,:LINK
1H	  SET	    :AVAIL,X
          POP	    0,0
          PREFIX    :