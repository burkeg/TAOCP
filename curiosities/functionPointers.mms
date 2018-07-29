t	     IS		$255
	     LOC	Data_Segment


x	     IS	        $0
y	     IS	        $1
f	     IS		$2
result	     IS		$3
	     LOC	#100
Main	     GETA	f,:SUM
	     SET	x,9
	     SET	y,6
	     SET	(result+1),f
	     SET	(result+2),x
	     SET	(result+3),y
	     PUSHJ	result,:APPLY
	     SET	result,result
	     
	     GETA	f,:DIFF
	     SET	x,13
	     SET	y,8
	     SET	(result+1),f
	     SET	(result+2),x
	     SET	(result+3),y
	     PUSHJ	result,:APPLY
	     SET	result,result
	     TRAP	0,Halt,0

	     PREFIX	APPLY:
;	     returns f(x,y)
f	     IS		$0
x	     IS		$1
y	     IS		$2
retaddr	     IS		$3
result	     IS		$4
:APPLY	     GET	retaddr,:rJ
	     SET	(result+1),x
	     SET	(result+2),y
	     PUSHGO	result,f
	     SET	$0,result
	     PUT	:rJ,retaddr
	     POP	1,0
	     PREFIX	:

	     PREFIX	SUM:
;	     returns a+b
a	     IS	        $0
b	     IS	        $1
:SUM	     ADD	$0,a,b
	     POP	1,0
	     PREFIX	:
	     
	     PREFIX	DIFF:
;	     returns a-b
a	     IS	        $0
b	     IS	        $1
:DIFF	     SUB	$0,a,b
	     POP	1,0
	     PREFIX	:


