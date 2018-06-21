% Solitaire
t	   IS	$255	 Temp variable

DOWN	   IS	0
UP	   IS	1
CLUBS	   IS	1
DIAMONDS   IS	2
HEARTS	   IS	3
SPADES	   IS	4

TAG	   IS 	0*8
SUIT	   IS 	1*8
RANK	   IS 	2*8
NEXT	   IS 	3*8
TITLE	   IS 	4*8

	LOC	Data_Segment
1H	OCTA	DOWN,CLUBS,3,0
	BYTE	"     3 C"
1H	OCTA	UP,DIAMONDS,6,1B
	BYTE	"     6 D"
1H	OCTA	DOWN,SPADES,10,1B
	BYTE	"    10 S"
	GREG	@
LAST	OCTA	UP,HEARTS,5,1B
	BYTE	"     5 H"
	LOC	1B+100*12
	GREG	@
NEWCARD	OCTA	DOWN,CLUBS,3,0
	BYTE	"     3 C"
BUFF	GREG	@
	OCTA  	0
NewLine	BYTE	#a,0

X	IS	$1
TOP	IS	$2
	LOC	#100
Main	LDA	TOP,LAST		
	SET	X,TOP		
2H	BZ	X,Done
	SET	$4,X
	PUSHJ	$3,:PrintTitle
	LDO	X,X,NEXT	
	JMP	2B		
Done	TRAP	0,Halt,0


	PREFIX	PrintTitle:
i	IS	$1
card	IS	$0			Card base address
j	IS	$2
updwn	IS	$3
char	IS	$6
:PrintTitle  	LDO	updwn,card,:TAG	
	SET	j,0
	SET	i,0
	SET	$4,'('
	SET	$5,')'
	ADD	card,card,:TITLE
	BNZ	updwn,1F
	STB	$4,:BUFF,j
	ADD	j,j,1
1H	LDB	char,card,i	Find the first instance of whitespace
	CMP	:t,char,' '
	BNZ	:t,3F
	ADD	i,i,1
	JMP	1B
2H	LDB	char,card,i
3H	STB	char,:BUFF,j		i is at the index of the first non-space character
	ADD	j,j,1
	ADD	i,i,1
	CMP	:t,i,8
	BN	:t,2B
	BNZ	updwn,3F
	STB	$5,:BUFF,j
	ADD	j,j,1
3H	STB	$7,:BUFF,j
	SET	:t,:BUFF
	TRAP	0,:Fputs,:StdOut
	LDA	:t,:NewLine
	TRAP	0,:Fputs,:StdOut
	POP	0,0
	PREFIX	: