%Fibonacci using recursive and non-recursive method. (mod 2^62)
	   PREFIX	Main:     
fn	   IS		$0
n	   IS		20
	   LOC		:Data_Segment
sp	   GREG		@

	   LOC		#100
:Main	   SET		$1,n
	   PUSHJ	fn,:FibStack
	   ADD		fn,fn,0
	   TRAP		0,:Halt,0
	   PREFIX	:

	   PREFIX	FibStack:
n  IS  $0;fn_1  IS  $1;t  IS  $3;oldJ  IS  $2;
:FibStack  CMPU   	t,n,1
	   BNP		t,9F
	   GET		oldJ,:rJ
	   SUB		$4,n,1
	   PUSHJ	t,:FibRec
	   SET		fn_1,t
	   SUB		$4,n,2
	   PUSHJ	t,:FibRec
	   ADD		n,fn_1,t
	   PUT		:rJ,oldJ
9H	   POP		1,0
	   PREFIX	:
	   
	   PREFIX	FibRec:
n  IS  $0;fn_1  IS  $1;t  IS  $3;oldJ  IS  $2;
:FibRec	   CMPU	     	t,n,1
	   BNP		t,9F
	   GET		oldJ,:rJ
	   SUB		$4,n,1
	   PUSHJ	t,:FibRec
	   SET		fn_1,t
	   SUB		$4,n,2
	   PUSHJ	t,:FibRec
	   ADD		n,fn_1,t
	   PUT		:rJ,oldJ
9H	   POP		1,0
	   PREFIX	:


	   PREFIX	FibIter:
:FibIter   CMP		$1,$0,1
	   BNP		$1,2F
	   SET		$2,1
1H	   ADD		$1,$3,$2
	   SET		$3,$2
	   SET		$2,$1
	   SUB		$0,$0,1
	   CMP		$4,$0,1
	   PBP		$4,1B
	   SET		$0,$1
2H	   POP		1,0
	   PREFIX	:

%Their best Solution to FibIter
%compared n=20, mine=132 oops, golden=58 oops... ouch
	   PREFIX	FibGolden: %Fib2 in solutions
:FibGolden CMP		$1,$0,1
	   BNP		$1,1F
	   SUB		$2,$0,1
	   SET		$0,0
2H	   ADDU		$0,$0,$1
	   ADDU		$1,$0,$1
	   SUB		$2,$2,2
	   PBP		$2,2B
	   CSZ		$0,$2,$1
1H	   POP		1,0

