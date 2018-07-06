	LOC	Data_Segment
	GREG	@
M8a	OCTA	#1
M4a	TETRA	#2,#3
M2a	WYDE	#4,#5,#6,#7
M1a	BYTE	#8,#9,#a,#b,#c,#d,#e,#f

M8	IS	$0
M4	IS	$1
M2	IS	$2
M1	IS	$3
t	IS	$255

	LOC	#100
Main	LDA	M8,M8a
	LDA	M4,M4a
	LDA	M2,M2a
	LDA	M1,M1a
	LDO	t,M8,0
	LDT	t,M4,0
	LDT	t,M4,4
	LDW	t,M2,0
	LDW	t,M2,2
	LDW	t,M2,4
	LDW	t,M2,6
	LDB	t,M1,0
	LDB	t,M1,1
	LDB	t,M1,2
	LDB	t,M1,3
	LDB	t,M1,4
	LDB	t,M1,5
	LDB	t,M1,6
	LDB	t,M1,7