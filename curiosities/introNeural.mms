; Basic, super inefficient neural net example

AVAIL	  GREG	    
POOLMAX	  GREG
SEQMIN	  GREG
ZERO	  GREG
NEGONE	  GREG      -1



t 	  IS	    $255
NUM_GATES IS 	    4
NUM_UNITS IS 	    9
GATE_SIZE IS	    4*8
UNIT_SIZE IS	    4*8
c	  IS	    2*8		Nodesize(bytes), (max 256)
capacity  IS	    100		max number of c-Byte nodes 
LINK	  IS 	    0
INFO	  IS	    8
IN_UNITS  IS	    0
OUT_UNIT  IS	    8
FWD_PTR	  IS	    16
BACK_PTR  IS 	    24
VALUE	  IS	    0
GRAD	  IS	    8
IN_GATES  IS	    16
OUT_GATE  IS	    24
MAX_INPUTS IS	    5

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
	  LOC	    1B+NUM_GATES*8+100*8
	  GREG	    @
L0_pool	  OCTA      0
	  LOC	    @+c*capacity-8
	  GREG	    @
endOfPool OCTA	    0


	  LOC	    #100
Main	  LDA	    POOLMAX,L0_pool
	  LDA	    SEQMIN,endOfPool
	  PUSHJ	    $0,:Init
	  PUSHJ	    $0,:TopSort
	  PUSHJ	    $0,:ForwardProp
	  TRAP	    0,Halt,0

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
	  FLOT	    :t,:t
	  STO	    :t,retval,:VALUE
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
2H	  IS   	    2	Value
	  SET	    unitI,1B-1
	  SET	    :t,2B
	  MUL	    unitAddr,unitI,:UNIT_SIZE
	  ADD	    retval,unitAddr,UnitBase
	  FLOT	    :t,:t
	  STO	    :t,retval,:VALUE
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
2H	  IS   	    3	Value
	  SET	    unitI,1B-1
	  SUB	    :t,:ZERO,2B
	  MUL	    unitAddr,unitI,:UNIT_SIZE
	  ADD	    retval,unitAddr,UnitBase
	  FLOT	    :t,:t
	  STO	    :t,retval,:VALUE
;
	  PUT	    :rJ,retaddr
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
:ReadPairUnit LDA   :t,:Unit_arr,unitIndex
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
:Gate_Addition_2_back FADD    $2,$0,$1
	  POP	    3,0
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
:Gate_Multiplication_2_back FADD    $2,$0,$1
	  POP	    3,0
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

	  PREFIX    Dealloc:
;	  Doesn't check if trying to dealloc a node that was never alloc'd	  
X	  IS	    $0
:Dealloc  STO	    :AVAIL,X,:LINK
1H	  SET	    :AVAIL,X
	  POP	    0,0
	  PREFIX    :