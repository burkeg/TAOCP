	LOC	Data_Segment
data	GREG	@
	OCTA 	0

	LOC #100
Main	SET $3,3
	LDA	$1,data
	STO	$3,$1,0
	TRAP	0,Halt,0