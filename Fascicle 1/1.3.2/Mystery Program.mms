* Mystery Program
a       GREG	'*'
b	GREG	' '
c	GREG 	Data_Segment
	LOC	#100
Main	NEG	$1,1,75
	SET	$2,0
2H	ADD	$3,$1,75
3H	STB	b,c,$2
	ADD	$2,$2,1
	SUB	$3,$3,1
	PBP	$3,3B
	STB	a,c,$2
	INCL	$2,1
	INCL	$1,1
	PBN	$1,2B
	SET	$255,c;
	TRAP 0,Fputs,StdOut
	TRAP 0,Halt,0