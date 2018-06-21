% Farey series
tmp1 	IS	$255	Temp variable
tmp2	GREG	0
n 	GREG	#7
kk	GREG	0	4*k
xk	GREG	0	index of x[k]
yk	GREG	0	index of y[k]
xm1	GREG	0	value of x[k-1]
ym1	GREG	0	value of y[k-1]
xm2	GREG	0	value of x[k-2]
ym2	GREG	0	value of y[k-2]


	LOC	Data_Segment
	GREG	@
ArgOp	OCTA	1F,BinaryWrite
botX	GREG	@
ArgWrX	OCTA	2F,32
botY	GREG	@
ArgWrY	OCTA	3F,32
botBord	GREG	@
ArgWrB	OCTA	Border,8
1H	BYTE	"Farey_output",0
	GREG	@
NewLine	BYTE	#A,0
Border	BYTE	#FF,#FF,#FF,#FF,#FF,#FF,#FF,#FF

X0	GREG	@
2H	TETRA	0,1
	LOC	2B+4*(1<<32)
	TETRA	#FFFF
Y0	GREG	@
3H	TETRA	1

	LOC	#100
Main	STT	n,Y0,4			Place n into postion Y1
	LDT	xm2,X0,4
	LDT	ym2,Y0,0
	LDT	xm1,X0,8
	LDT	ym1,Y0,4
	SET	kk,4*2			k <- 2

%	LDA	tmp1,ArgOp;		TRAP   0,Fopen,5       Fopen(5,"foo",BinaryWrite)
%	LDA	tmp1,ArgWrY;
%	TRAP   	0,Fwrite,5		Writes x's to binary file "Farey_output"
%	TRAP	0,Fclose,5
%	TRAP	0,Halt,0

3H	ADD	tmp1,ym2,n		(y_{k-2}+n)
	DIV	tmp1,tmp1,ym1		lower[(y_{k-2}+n) / y_{k-1}]
	
	MUL	tmp2,tmp1,ym1		Calculate y_k
	SUB	tmp2,tmp2,ym2	
	SET	ym2,ym1			Update y_{k-1} and y_{k-2}
	SET	ym1,tmp2	
	STT	tmp2,Y0,kk
	
	ADD	kk,kk,4
	
	MUL	tmp2,tmp1,xm1		Calculate x_k
	SUB	tmp2,tmp2,xm2
	SET	xm2,xm1			Update x_{k-1} and x_{k-2}
	SET	xm1,tmp2
	STT	tmp2,X0,kk		Store x_k
	

	XOR	tmp1,xm1,ym1
	PBNZ	tmp1,3B			if numerator matches denominator then we're done!
	
	STO	kk,botX,8
	STO	kk,botY,8


	LDA	tmp1,ArgOp;		TRAP   0,Fopen,5       Fopen(5,"foo",BinaryWrite)
	LDA	tmp1,ArgWrX;
	TRAP   	0,Fwrite,5		Writes x's to binary file "Farey_output"
	LDA	tmp1,ArgWrB;
	TRAP   	0,Fwrite,5	Writes  #FF's as a border between X and Y
	LDA	tmp1,ArgWrY;
	TRAP   	0,Fwrite,5		Writes x's to binary file "Farey_output"
	TRAP	0,Fclose,5
	
	