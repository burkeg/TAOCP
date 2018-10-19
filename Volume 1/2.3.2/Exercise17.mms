; Symbolic Differentiation
				
AVAIL		GREG	    
POOLMAX 	GREG
SEQMIN		GREG
ZERO		GREG
				
t 		IS	    	$255
octaSize 	IS	    	8
capacity 	IS	    	100		max number of nodeSize-Byte nodes
LINK		IS 	    	0
INFO		IS	    	8
_nodeSize 	IS	    	4
nodeSize 	GREG	    	_nodeSize*octaSize

		PREFIX    	node:
LLINK		IS	    	8*0
RLINK		IS	    	8*1
INFO		IS	    	8*2
TYPE		IS		8*3
		PREFIX    	TYPE:
CONSTANT	IS		0
VARIABLE	IS		1
LN		IS		2
NEG		IS		3
ADD		IS		4
SUB		IS		5
MULT		IS		6
DIV		IS		7
EXP		IS		8
		PREFIX    	:

		LOC       	Data_Segment 
		GREG	    	@
L0		OCTA      	0
		LOC	    	L0+_nodeSize*octaSize*capacity
		GREG	    	@
Linf		OCTA	    	0

T		IS		$0
last		IS		$2
		LOC		#100
Main		LDA	    	POOLMAX,L0
		LDA	    	SEQMIN,Linf
		PUSHJ	    	T,:ConstructTree2
		SET		(last+1),T
		PUSHJ		last,:ThreadTree
		SET		(last+1),T
		PUSHJ		last,:Differentiate
		TRAP	    	0,Halt,0

		PREFIX		Differentiate:
Y		IS		$0
retaddr		IS		$1
DY		IS		$2
P		IS		$3
P1		IS		$4
P2		IS		$5
Q		IS		$6
Q1		IS		$7
tmp		IS		$8
last		IS		$10
:Differentiate	GET		retaddr,:rJ
;		D1		[Initialize.]
1H		PUSHJ		last,:Alloc
		SET		DY,last		Allocate an empty tree for DY
		STO		DY,DY,:node:RLINK	 Empty tree RLINK is a link to itself
		SET		:t,DY
		ORL		:t,#0001
		STO		:t,DY,:node:LLINK	 Empty tree LLINK is a thread to itself
		SETL		:t,' '<<8+' '
		INCML		:t,' '<<8+' '
		INCMH		:t,' '<<8+' '
		INCH		:t,'d'<<8+'y'
		STO		:t,DY,:node:INFO
		SET		(last+1),Y
		PUSHJ		last,:InorderSuccessor
		SET		P,last			P <- Y$
;		D2		[Differentiate.]
2H		LDO		P1,P,:node:LLINK	P1 <- LLINK(P)
		SL		:t,P1,63
		BNZ		:t,1F
		LDO		Q1,P1,:node:RLINK	Q1 <- RLINK(P1)
1H		SET		(last+1),Q1
		SET		(last+2),Q
		SET		(last+3),P
		SET		(last+4),P1
		SET		(last+5),P2
		PUSHJ		last,:ApplyRule
		SET		Q,last
		SET		Q1,(last+1)
;		D3		[Restore Link.]
3H		LDO		tmp,P,:node:TYPE
		CMP		:t,tmp,:node:TYPE:ADD
		BZ		:t,isBinary
		CMP		:t,tmp,:node:TYPE:SUB
		BZ		:t,isBinary
		CMP		:t,tmp,:node:TYPE:MULT
		BZ		:t,isBinary
		CMP		:t,tmp,:node:TYPE:DIV
		BZ		:t,isBinary
		CMP		:t,tmp,:node:TYPE:EXP
		BZ		:t,isBinary
		JMP		4F
isBinary	STO		P2,P1,:node:RLINK	if TYPE(P) denotes a binary operator, RLINK(P1) <- P2
;		D4		[Advance to P$.]
4H		SET		P2,P			P2 <- P
		SET		(last+1),P
		PUSHJ		last,:InorderSuccessor
		SET		P,last			P <- P$
		LDO		:t,P2,:node:RLINK	load RLINK(P2)
		SL		:t,:t,63
		BNZ		:t,5F
		STO		Q,P2,:node:RLINK	if RTAG(P2)=0, RLINK(P2) <- Q
;		D4		[Advance to P$.]
5H		ANDNL		P,#0001
		CMP		:t,P,Y
		BNZ		:t,2B
		ANDNL		Q,#0001
		STO		Q,DY,:node:LLINK	LLINK(DY) <- Q
		STO		DY,Q,:node:RLINK	RLINK(Q) <- DY
		LDO		:t,Q,:node:RLINK	load RLINK(Q)
		ORL		:t,#0001
		STO		:t,Q,:node:RLINK	RTAG(Q) <- 1
		PUT		:rJ,retaddr
		SET		$0,DY
		POP		1,0
		PREFIX		:

		PREFIX		DiffConstant:
P		IS		$0
P1		IS		$1
Q		IS		$2
P2		IS		$3
Q1		IS		$4
retaddr		IS		$5
tmp		IS		$6
last		IS		$10
:DiffConstant 	GET		retaddr,:rJ
		PUSHJ		last,:Alloc
		SET		tmp,last
		SETL		:t,' '<<8+' '
		INCML		:t,' '<<8+' '
		INCMH		:t,' '<<8+' '
		INCH		:t,'0'<<8+' '
		STO		:t,last,:node:INFO
		SET		:t,:node:TYPE:CONSTANT
		STO		:t,last,:node:TYPE	create "x"
		SET		(last+1),tmp
		PUSHJ		last,:Tree0
		SET		Q,last			Q <- TREE(0)
		SET		(last+1),tmp
		PUSHJ		last,:Dealloc		delete "x"
		PUT		:rJ,retaddr
		SET		$0,Q1
		SET		$1,Q
		POP		2,0
		PREFIX		:

		PREFIX		DiffVariable:
P		IS		$0
P1		IS		$1
Q		IS		$2
P2		IS		$3
Q1		IS		$4
retaddr		IS		$5
tmp		IS		$6
tmp2		IS		$7
last		IS		$8
:DiffVariable 	GET		retaddr,:rJ
		PUSHJ		last,:Alloc
		SET		tmp,last
		LDO		tmp2,P,:node:INFO
		SETL		:t,' '<<8+' '
		INCML		:t,' '<<8+' '
		INCMH		:t,' '<<8+' '
		INCH		:t,'x'<<8+' '
		CMP		:t,:t,tmp2	Is INFO(P) = "x"?
		BZ		:t,one
		SETL		:t,' '<<8+' '
		INCML		:t,' '<<8+' '
		INCMH		:t,' '<<8+' '
		INCH		:t,'0'<<8+' '
		JMP 		1F
one		SETL		:t,' '<<8+' '
		INCML		:t,' '<<8+' '
		INCMH		:t,' '<<8+' '
		INCH		:t,'1'<<8+' '
1H		STO		:t,last,:node:INFO
		SET		:t,:node:TYPE:CONSTANT
		STO		:t,last,:node:TYPE	create "x"
		SET		(last+1),tmp
		PUSHJ		last,:Tree0
		SET		Q,last			Q <- TREE("0" or "1")
		SET		(last+1),tmp
		PUSHJ		last,:Dealloc		delete "x"
		PUT		:rJ,retaddr
		SET		$0,Q1
		SET		$1,Q
		POP		2,0
		PREFIX		:

		PREFIX		DiffLn:
P		IS		$0
P1		IS		$1
Q		IS		$2
P2		IS		$3
Q1		IS		$4
retaddr		IS		$5
tmp		IS		$6
tmp2		IS		$7
last		IS		$8
:DiffLn 	GET		retaddr,:rJ
		LDO		tmp,Q,:node:TYPE
		CMP		:t,tmp,:node:TYPE:CONSTANT
		BNZ		:t,nonZero
		LDO		tmp,Q,:node:INFO
		SETL		:t,' '<<8+' '
		INCML		:t,' '<<8+' '
		INCMH		:t,' '<<8+' '
		INCH		:t,'0'<<8+' '
		CMP		:t,:t,tmp2	Is INFO(Q) = "0"?
		BNZ		:t,nonZero
		TRAP		0,:Halt,0	d(ln(0)) d.n.e.
nonZero		PUSHJ		last,:Alloc
		SET		tmp,last
		SETL		:t,' '<<8+' '
		INCML		:t,' '<<8+' '
		INCMH		:t,' '<<8+' '
		INCH		:t,'/'<<8+' '
		STO		:t,tmp,:node:INFO
		SET		:t,:node:TYPE:DIV
		STO		:t,tmp,:node:TYPE	tmp <- node("/")
		SET		(last+1),P1
		PUSHJ		last,:CopyBinaryTree
		SET		tmp2,last		tmp2 <- COPY(P1)
		;last is copy(P1)
		SET		(last+1),tmp
		SET		(last+2),Q
		SET		(last+3),tmp2
		PUSHJ		last,:Tree2
		SET		Q,last			Q <- TREE("/",Q,COPY(P1))
		SET		(last+1),tmp
		PUSHJ		last,:Dealloc		delete "/"
		PUT		:rJ,retaddr
		SET		$0,Q1
		SET		$1,Q
		POP		2,0
		PREFIX		:

		PREFIX		DiffNeg:
P		IS		$0
P1		IS		$1
Q		IS		$2
P2		IS		$3
Q1		IS		$4
retaddr		IS		$5
tmp		IS		$6
last		IS		$7
:DiffNeg 	GET		retaddr,:rJ
		LDO		tmp,Q,:node:TYPE
		CMP		:t,tmp,:node:TYPE:CONSTANT
		BNZ		:t,nonZero
		LDO		tmp,Q,:node:INFO
		SETL		:t,' '<<8+' '
		INCML		:t,' '<<8+' '
		INCMH		:t,' '<<8+' '
		INCH		:t,'0'<<8+' '
		CMP		:t,:t,tmp	Is INFO(Q) = "0"?
		BNZ		:t,nonZero
		TRAP		0,:Halt,0	d(ln(0)) d.n.e.
nonZero		PUSHJ		last,:Alloc
		SET		tmp,last
		SETL		:t,' '<<8+' '
		INCML		:t,' '<<8+' '
		INCMH		:t,'g'<<8+' '
		INCH		:t,'n'<<8+'e'
		STO		:t,tmp,:node:INFO
		SET		:t,:node:TYPE:NEG
		STO		:t,tmp,:node:TYPE	tmp <- node("neg")
		SET		(last+1),tmp
		SET		(last+2),Q
		PUSHJ		last,:Tree1
		SET		Q,last			Q <- TREE("neg",Q)
		SET		(last+1),tmp
		PUSHJ		last,:Dealloc		delete "neg"
		PUT		:rJ,retaddr
		SET		$0,Q1
		SET		$1,Q
		POP		2,0
		PREFIX		:

		PREFIX		DiffAdd:
P		IS		$0
P1		IS		$1
Q		IS		$2
P2		IS		$3
Q1		IS		$4
retaddr		IS		$5
tmp		IS		$6
tmp2		IS		$7
last		IS		$8
:DiffAdd 	GET		retaddr,:rJ
		LDO		tmp,Q1,:node:TYPE
		CMP		:t,tmp,:node:TYPE:CONSTANT
		BNZ		:t,1F
		LDO		tmp,Q1,:node:INFO
		SETL		:t,' '<<8+' '
		INCML		:t,' '<<8+' '
		INCMH		:t,' '<<8+' '
		INCH		:t,'0'<<8+' '
		CMP		:t,:t,tmp	Is INFO(Q1) = "0"?
		BNZ		:t,1F
;		Q1 = "0"
		SET		(last+1),Q1
		PUSHJ		last,:Dealloc	AVAIL <= Q1
		SET		Q1,0
		JMP		done
1H		LDO		tmp,Q,:node:TYPE
		CMP		:t,tmp,:node:TYPE:CONSTANT
		BNZ		:t,1F
		LDO		tmp,Q,:node:INFO
		SETL		:t,' '<<8+' '
		INCML		:t,' '<<8+' '
		INCMH		:t,' '<<8+' '
		INCH		:t,'0'<<8+' '
		CMP		:t,:t,tmp	Is INFO(Q) = "0"?
		BNZ		:t,1F
;		Q = "0"
		SET		(last+1),Q
		PUSHJ		last,:Dealloc	AVAIL <= Q
		SET		Q,Q1
		SET		Q1,0
		JMP		done
1H		PUSHJ		last,:Alloc
		SET		tmp,last
		SETL		:t,' '<<8+' '
		INCML		:t,' '<<8+' '
		INCMH		:t,' '<<8+' '
		INCH		:t,'+'<<8+' '
		STO		:t,tmp,:node:INFO
		SET		:t,:node:TYPE:ADD
		STO		:t,tmp,:node:TYPE	tmp <- node("+")
		SET		(last+1),tmp
		SET		(last+2),Q1
		SET		(last+3),Q
		PUSHJ		last,:Tree2
		SET		Q,last			Q <- TREE("+",Q)
		SET		(last+1),tmp
		PUSHJ		last,:Dealloc		delete "+"
done		PUT		:rJ,retaddr
		SET		$0,Q1
		SET		$1,Q
		POP		2,0
		PREFIX		:

		PREFIX		DiffSub:
P		IS		$0
P1		IS		$1
Q		IS		$2
P2		IS		$3
Q1		IS		$4
retaddr		IS		$5
tmp		IS		$6
tmp2		IS		$7
last		IS		$8
:DiffSub 	GET		retaddr,:rJ
		LDO		tmp,Q,:node:TYPE
		CMP		:t,tmp,:node:TYPE:CONSTANT
		BNZ		:t,1F
		LDO		tmp,Q,:node:INFO
		SETL		:t,' '<<8+' '
		INCML		:t,' '<<8+' '
		INCMH		:t,' '<<8+' '
		INCH		:t,'0'<<8+' '
		CMP		:t,:t,tmp	Is INFO(Q) = "0"?
		BNZ		:t,1F
;		Q1 = "0"
		SET		(last+1),Q
		PUSHJ		last,:Dealloc	AVAIL <= Q
		SET		Q,Q1		Q <- Q1
		JMP		done
1H		LDO		tmp,Q1,:node:TYPE
		CMP		:t,tmp,:node:TYPE:CONSTANT
		BNZ		:t,1F
		LDO		tmp,Q1,:node:INFO
		SETL		:t,' '<<8+' '
		INCML		:t,' '<<8+' '
		INCMH		:t,' '<<8+' '
		INCH		:t,'0'<<8+' '
		CMP		:t,:t,tmp	Is INFO(Q1) = "0"?
		BNZ		:t,1F
;		Q = "0"
		SET		(last+1),Q1
		PUSHJ		last,:Dealloc	AVAIL <= Q1
		PUSHJ		last,:Alloc
		SET		tmp,last
		SETL		:t,' '<<8+' '
		INCML		:t,' '<<8+' '
		INCMH		:t,'g'<<8+' '
		INCH		:t,'n'<<8+'e'
		STO		:t,tmp,:node:INFO
		SET		:t,:node:TYPE:NEG
		STO		:t,tmp,:node:TYPE	tmp <- node("neg")
		SET		(last+1),tmp
		SET		(last+2),Q
		PUSHJ		last,:Tree1
		SET		Q,last			Q <- TREE("neg",Q)
		SET		(last+1),tmp
		PUSHJ		last,:Dealloc		delete "neg"
		JMP		done
1H		PUSHJ		last,:Alloc
		SET		tmp,last
		SETL		:t,' '<<8+' '
		INCML		:t,' '<<8+' '
		INCMH		:t,' '<<8+' '
		INCH		:t,'-'<<8+' '
		STO		:t,tmp,:node:INFO
		SET		:t,:node:TYPE:SUB
		STO		:t,tmp,:node:TYPE	tmp <- node("-")
		SET		(last+1),tmp
		SET		(last+2),Q1
		SET		(last+3),Q
		PUSHJ		last,:Tree2
		SET		Q,last			Q <- TREE("-",Q)
		SET		(last+1),tmp
		PUSHJ		last,:Dealloc		delete "-"
done		PUT		:rJ,retaddr
		SET		$0,Q1
		SET		$1,Q
		POP		2,0
		PREFIX		:

		PREFIX		DiffMult:
P		IS		$0
P1		IS		$1
Q		IS		$2
P2		IS		$3
Q1		IS		$4
retaddr		IS		$5
tmp		IS		$6
tmp2		IS		$7
last		IS		$8
:DiffMult 	GET		retaddr,:rJ
		LDO		tmp,Q1,:node:TYPE
		CMP		:t,tmp,:node:TYPE:CONSTANT
		BNZ		:t,1F
		LDO		tmp,Q1,:node:INFO
		SETL		:t,' '<<8+' '
		INCML		:t,' '<<8+' '
		INCMH		:t,' '<<8+' '
		INCH		:t,'0'<<8+' '
		CMP		:t,:t,tmp	Is INFO(Q1) = "0"?
		BNZ		:t,1F
;		Q = "0"
		JMP		skipQ1
1H		SET		(last+1),P2
		PUSHJ		last,:CopyBinaryTree
		SET		(last+1),Q1
		SET		(last+2),last
		PUSHJ		last,:MULT
		SET		Q1,last		Q1 <- MULT(Q1,COPY(P2))
;		Check if Q is nonzero
skipQ1		LDO		tmp,Q,:node:TYPE
		CMP		:t,tmp,:node:TYPE:CONSTANT
		BNZ		:t,1F
		LDO		tmp,Q,:node:INFO
		SETL		:t,' '<<8+' '
		INCML		:t,' '<<8+' '
		INCMH		:t,' '<<8+' '
		INCH		:t,'0'<<8+' '
		CMP		:t,:t,tmp	Is INFO(Q) = "0"?
		BNZ		:t,1F
;		Q1 = "0"
		JMP		skipQ
1H		SET		(last+1),P1
		PUSHJ		last,:CopyBinaryTree
		SET		(last+1),last
		SET		(last+2),Q
		PUSHJ		last,:MULT
		SET		Q,last		Q <- MULT(COPY(P1),Q)
;		Go to DiffAdd
skipQ		SET		(last+1),P
		SET		(last+2),P1
		SET		(last+3),Q
		SET		(last+4),P2
		SET		(last+5),Q1
		PUSHJ		last,:DiffAdd
		SET		Q,last
		SET		Q1,(last+1)
done		PUT		:rJ,retaddr
		SET		$0,Q1
		SET		$1,Q
		POP		2,0
		PREFIX		:

		PREFIX		DiffDiv:
P		IS		$0
P1		IS		$1
Q		IS		$2
P2		IS		$3
Q1		IS		$4
retaddr		IS		$5
tmp		IS		$6
tmp2		IS		$7
tmp3		IS		$8
last		IS		$9
:DiffDiv 	GET		retaddr,:rJ
		LDO		tmp,Q1,:node:TYPE
		CMP		:t,tmp,:node:TYPE:CONSTANT
		BNZ		:t,1F
		LDO		tmp,Q1,:node:INFO
		SETL		:t,' '<<8+' '
		INCML		:t,' '<<8+' '
		INCMH		:t,' '<<8+' '
		INCH		:t,'0'<<8+' '
		CMP		:t,:t,tmp	Is INFO(Q1) = "0"?
		BNZ		:t,1F
;		Q1 = "0"
		JMP		skipQ1
1H		PUSHJ		last,:Alloc
		SET		tmp,last
		SETL		:t,' '<<8+' '
		INCML		:t,' '<<8+' '
		INCMH		:t,' '<<8+' '
		INCH		:t,'/'<<8+' '
		STO		:t,tmp,:node:INFO
		SET		:t,:node:TYPE:DIV
		STO		:t,tmp,:node:TYPE	tmp <- node("/")
		SET		(last+1),P2
		PUSHJ		last,:CopyBinaryTree
		SET		(last+1),tmp
		SET		(last+2),Q1
		SET		(last+3),last
		PUSHJ		last,:Tree2
		SET		Q1,last		Q1 <- TREE("/",Q1,COPY(P2))
		SET		(last+1),tmp
		PUSHJ		last,:Dealloc		delete "/"
;		Check if Q is nonzero
skipQ1		LDO		tmp,Q,:node:TYPE
		CMP		:t,tmp,:node:TYPE:CONSTANT
		BNZ		:t,1F
		LDO		tmp,Q,:node:INFO
		SETL		:t,' '<<8+' '
		INCML		:t,' '<<8+' '
		INCMH		:t,' '<<8+' '
		INCH		:t,'0'<<8+' '
		CMP		:t,:t,tmp	Is INFO(Q) = "0"?
		BNZ		:t,1F
;		Q = "0"
		JMP		skipQ
1H		PUSHJ		last,:Alloc
		SET		tmp,last
		SETL		:t,' '<<8+' '
		INCML		:t,' '<<8+' '
		INCMH		:t,' '<<8+' '
		INCH		:t,'^'<<8+' '
		STO		:t,tmp,:node:INFO
		SET		:t,:node:TYPE:EXP
		STO		:t,tmp,:node:TYPE	tmp <- node("^")
		PUSHJ		last,:Alloc
		SET		tmp2,last
		SETL		:t,' '<<8+' '
		INCML		:t,' '<<8+' '
		INCMH		:t,' '<<8+' '
		INCH		:t,'2'<<8+' '
		STO		:t,tmp2,:node:INFO
		SET		:t,:node:TYPE:CONSTANT
		STO		:t,tmp2,:node:TYPE	tmp2 <- node("2")
		SET		(last+1),tmp2
		PUSHJ		last,:Tree0		create TREE("2")
		SET		tmp3,last
		SET		(last+1),tmp2
		PUSHJ		last,:Dealloc		delete "2"
		SET		(last+1),P2
		PUSHJ		last,:CopyBinaryTree	create COPY(P2)
		SET		(last+1),tmp
		SET		(last+2),last
		SET		(last+3),tmp3
		PUSHJ		last,:Tree2		create TREE("^",COPY(P2),TREE(2))
		SET		tmp3,last
		SET		(last+1),tmp
		PUSHJ		last,:Dealloc		delete "^"
		SET		(last+1),P1
		PUSHJ		last,:CopyBinaryTree	create COPY(P1)
		SET		(last+1),last
		SET		(last+2),Q
		PUSHJ		last,:MULT		create MULT(COPY(P1),Q)
		SET		tmp2,last
		PUSHJ		last,:Alloc
		SET		tmp,last
		SETL		:t,' '<<8+' '
		INCML		:t,' '<<8+' '
		INCMH		:t,' '<<8+' '
		INCH		:t,'/'<<8+' '
		STO		:t,tmp,:node:INFO
		SET		:t,:node:TYPE:DIV
		STO		:t,tmp,:node:TYPE	tmp <- node("/")
		SET		(last+1),tmp
		SET		(last+2),tmp2
		SET		(last+3),tmp3
		PUSHJ		last,:Tree2		create TREE("/",MULT(COPY(P1),Q),TREE("^",COPY(P2),TREE(2)))
		SET		Q,last			Q <- TREE("/",MULT(COPY(P1),Q),TREE("^",COPY(P2),TREE(2)))
		SET		(last+1),tmp
		PUSHJ		last,:Dealloc		delete "/"
;		Go to DiffSub
skipQ		SET		(last+1),P
		SET		(last+2),P1
		SET		(last+3),Q
		SET		(last+4),P2
		SET		(last+5),Q1
		PUSHJ		last,:DiffSub
		SET		Q,last
		SET		Q1,(last+1)
done		PUT		:rJ,retaddr
		SET		$0,Q1
		SET		$1,Q
		POP		2,0
		PREFIX		:

		PREFIX		DiffExp:
P		IS		$0
P1		IS		$1
Q		IS		$2
P2		IS		$3
Q1		IS		$4
retaddr		IS		$5
tmp		IS		$6
tmp2		IS		$7
tmp3		IS		$8
tmp4		IS		$9
last		IS		$10
:DiffExp 	GET		retaddr,:rJ
		LDO		tmp,Q1,:node:TYPE
		CMP		:t,tmp,:node:TYPE:CONSTANT
		BNZ		:t,1F
		LDO		tmp,Q1,:node:INFO
		SETL		:t,' '<<8+' '
		INCML		:t,' '<<8+' '
		INCMH		:t,' '<<8+' '
		INCH		:t,'0'<<8+' '
		CMP		:t,:t,tmp	Is INFO(Q1) = "0"?
		BNZ		:t,1F
;		Q1 = "0"
		JMP		skipQ1
1H		PUSHJ		last,:Alloc
		SET		tmp,last
		SETL		:t,' '<<8+' '
		INCML		:t,' '<<8+' '
		INCMH		:t,' '<<8+' '
		INCH		:t,'1'<<8+' '
		STO		:t,tmp,:node:INFO
		SET		:t,:node:TYPE:CONSTANT
		STO		:t,tmp,:node:TYPE	tmp <- node("1")
		SET		(last+1),tmp
		PUSHJ		last,:Tree0		create TREE("1")
		SET		tmp4,last
		PUSHJ		last,:Alloc
		SET		tmp2,last
		SETL		:t,' '<<8+' '
		INCML		:t,' '<<8+' '
		INCMH		:t,' '<<8+' '
		INCH		:t,'-'<<8+' '
		STO		:t,tmp2,:node:INFO
		SET		:t,:node:TYPE:SUB
		STO		:t,tmp2,:node:TYPE	tmp2 <- node("-")
		SET		(last+1),P2
		PUSHJ		last,:CopyBinaryTree	create COPY(P2)
		SET		(last+1),tmp2
		SET		(last+2),last
		SET		(last+3),tmp4
		PUSHJ		last,:Tree2		create TREE("-",COPY(P2),"1")
		SET		tmp3,last
		SET		(last+1),tmp
		PUSHJ		last,:Dealloc		delete "1"
		SET		(last+1),tmp2
		PUSHJ		last,:Dealloc		delete "-"
		PUSHJ		last,:Alloc
		SET		tmp,last
		SETL		:t,' '<<8+' '
		INCML		:t,' '<<8+' '
		INCMH		:t,' '<<8+' '
		INCH		:t,'^'<<8+' '
		STO		:t,tmp,:node:INFO
		SET		:t,:node:TYPE:EXP
		STO		:t,tmp,:node:TYPE	tmp <- node("^")
		SET		(last+1),P1
		PUSHJ		last,:CopyBinaryTree	create COPY(P2)
		SET		(last+1),tmp
		SET		(last+2),last
		SET		(last+3),tmp3
		PUSHJ		last,:Tree2		create TREE("^",COPY(P1),TREE("-",COPY(P2),"1"))
		SET		tmp3,last
		SET		(last+1),tmp
		PUSHJ		last,:Dealloc		delete "^"
		PUSHJ		last,:Alloc
		SET		tmp2,last
		SETL		:t,' '<<8+' '
		INCML		:t,' '<<8+' '
		INCMH		:t,' '<<8+' '
		INCH		:t,'*'<<8+' '
		STO		:t,tmp2,:node:INFO
		SET		:t,:node:TYPE:MULT
		STO		:t,tmp2,:node:TYPE	tmp <- node("*")
		SET		(last+1),P2
		PUSHJ		last,:CopyBinaryTree	create COPY(P2)
		SET		(last+1),tmp2
		SET		(last+2),Q1
		SET		(last+3),last
		PUSHJ		last,:Tree2		create TREE("*",Q1,COPY(P2))
		SET		tmp,last
		SET		(last+1),tmp2
		SET		(last+2),tmp3
		SET		(last+3),tmp
		PUSHJ		last,:Tree2		create TREE("*",TREE("^",COPY(P1),TREE("-",COPY(P2),"1")),TREE("*",Q1,COPY(P2)))
		SET		Q1,last
		SET		(last+1),tmp2
		PUSHJ		last,:Dealloc		delete "^"
;		Check if Q is nonzero
skipQ1		LDO		tmp,Q,:node:TYPE
		CMP		:t,tmp,:node:TYPE:CONSTANT
		BNZ		:t,1F
		LDO		tmp,Q,:node:INFO
		SETL		:t,' '<<8+' '
		INCML		:t,' '<<8+' '
		INCMH		:t,' '<<8+' '
		INCH		:t,'0'<<8+' '
		CMP		:t,:t,tmp	Is INFO(Q) = "0"?
		BNZ		:t,1F
;		Q = "0"
		JMP		skipQ
1H		PUSHJ		last,:Alloc
		SET		tmp,last
		SETL		:t,' '<<8+' '
		INCML		:t,' '<<8+' '
		INCMH		:t,' '<<8+' '
		INCH		:t,'l'<<8+'n'
		STO		:t,tmp,:node:INFO
		SET		:t,:node:TYPE:LN
		STO		:t,tmp,:node:TYPE	tmp <- node("ln")
		SET		(last+1),P1
		PUSHJ		last,:CopyBinaryTree	create COPY(P2)
		SET		(last+1),tmp
		SET		(last+2),last
		PUSHJ		last,:Tree1		create TREE("ln",COPY(P1))
		SET		tmp3,last
		SET		(last+1),tmp
		PUSHJ		last,:Dealloc		delete "ln"
		PUSHJ		last,:Alloc
		SET		tmp2,last
		SETL		:t,' '<<8+' '
		INCML		:t,' '<<8+' '
		INCMH		:t,' '<<8+' '
		INCH		:t,'*'<<8+' '
		STO		:t,tmp2,:node:INFO
		SET		:t,:node:TYPE:MULT
		STO		:t,tmp2,:node:TYPE	tmp <- node("*")
		SET		(last+1),tmp2
		SET		(last+2),tmp3
		SET		(last+3),Q
		PUSHJ		last,:Tree2		create TREE("*",TREE("ln",COPY(P1)),Q)
		SET		tmp3,last
		SET		(last+1),tmp2
		PUSHJ		last,:Dealloc		delete "*"
		SET		(last+1),P1
		PUSHJ		last,:CopyBinaryTree	create COPY(P1)
		SET		tmp,last
		PUSHJ		last,:Alloc
		SET		tmp2,last
		SETL		:t,' '<<8+' '
		INCML		:t,' '<<8+' '
		INCMH		:t,' '<<8+' '
		INCH		:t,'^'<<8+' '
		STO		:t,tmp2,:node:INFO
		SET		:t,:node:TYPE:EXP
		STO		:t,tmp2,:node:TYPE	tmp <- node("^")
		SET		(last+1),P2
		PUSHJ		last,:CopyBinaryTree	create COPY(P2)
		SET		(last+1),tmp2
		SET		(last+2),tmp
		SET		(last+3),last
		PUSHJ		last,:Tree2		create TREE("^",COPY(P1),COPY(P2))
		SET		tmp,last
		SET		(last+1),tmp2
		PUSHJ		last,:Dealloc		delete "^"
		PUSHJ		last,:Alloc
		SET		tmp2,last
		SETL		:t,' '<<8+' '
		INCML		:t,' '<<8+' '
		INCMH		:t,' '<<8+' '
		INCH		:t,'*'<<8+' '
		STO		:t,tmp2,:node:INFO
		SET		:t,:node:TYPE:MULT
		STO		:t,tmp2,:node:TYPE	tmp <- node("*")
		SET		(last+1),tmp2
		SET		(last+2),tmp3
		SET		(last+3),tmp
		PUSHJ		last,:Tree2		create TREE("*",TREE("*",TREE("ln",COPY(P1)),Q),TREE("^",COPY(P1),COPY(P2)))
		SET		Q,last
		SET		(last+1),tmp2
		PUSHJ		last,:Dealloc		delete "*"
;		Go to DiffAdd
skipQ		SET		(last+1),P
		SET		(last+2),P1
		SET		(last+3),Q
		SET		(last+4),P2
		SET		(last+5),Q1
		PUSHJ		last,:DiffAdd
		SET		Q,last
		SET		Q1,(last+1)
done		PUT		:rJ,retaddr
		SET		$0,Q1
		SET		$1,Q
		POP		2,0
		PREFIX		:

		PREFIX		MULT:
U		IS		$0
V		IS		$1
retaddr		IS		$2
tmp		IS		$3
last		IS		$4
:MULT		GET		retaddr,:rJ
		LDO		tmp,U,:node:TYPE
		CMP		:t,tmp,:node:TYPE:CONSTANT
		BNZ		:t,1F
		LDO		tmp,U,:node:INFO
		SETL		:t,' '<<8+' '
		INCML		:t,' '<<8+' '
		INCMH		:t,' '<<8+' '
		INCH		:t,'1'<<8+' '
		CMP		:t,:t,tmp	Is INFO(U) = "1"?
		BNZ		:t,1F
		SET		(last+1),U
		PUSHJ		last,:Dealloc
		SET		$0,V
		JMP		done
1H		LDO		tmp,V,:node:TYPE
		CMP		:t,tmp,:node:TYPE:CONSTANT
		BNZ		:t,1F
		LDO		tmp,V,:node:INFO
		SETL		:t,' '<<8+' '
		INCML		:t,' '<<8+' '
		INCMH		:t,' '<<8+' '
		INCH		:t,'1'<<8+' '
		CMP		:t,:t,tmp	Is INFO(V) = "1"?
		BNZ		:t,1F
		SET		(last+1),V
		PUSHJ		last,:Dealloc
		SET		$0,U
		JMP		done
1H		PUSHJ		last,:Alloc
		SET		tmp,last
		SETL		:t,' '<<8+' '
		INCML		:t,' '<<8+' '
		INCMH		:t,' '<<8+' '
		INCH		:t,'*'<<8+' '
		STO		:t,tmp,:node:INFO
		SET		:t,:node:TYPE:MULT
		STO		:t,tmp,:node:TYPE	tmp <- node("*")
		SET		(last+1),tmp
		SET		(last+2),U
		SET		(last+3),V
		PUSHJ		last,:Tree2
		SET		$0,last			MULT(U,V) <- TREE("*",U,V)
		SET		(last+1),tmp
		PUSHJ		last,:Dealloc		delete "-"
done		PUT		:rJ,retaddr
		POP		1,0
		PREFIX		:

		PREFIX		ApplyRule:
Q1		IS		$0
Q		IS		$1
P		IS		$2
P1		IS		$3
P2		IS		$4
retaddr		IS		$5
tmp		IS		$6
last		IS		$10
:ApplyRule 	GET		retaddr,:rJ
		ANDNL		Q1,#0001
		ANDNL		Q,#0001
		ANDNL		P,#0001
		ANDNL		P1,#0001
		ANDNL		P2,#0001
		LDO		tmp,P,:node:TYPE
		CMP		:t,tmp,:node:TYPE:CONSTANT
		BNZ		:t,1F
		SET		(last+1),P
		SET		(last+2),P1
		SET		(last+3),Q
		SET		(last+4),P2
		SET		(last+5),Q1
		PUSHJ		last,:DiffConstant
		JMP		done
1H		CMP		:t,tmp,:node:TYPE:VARIABLE
		BNZ		:t,1F
		SET		(last+1),P
		SET		(last+2),P1
		SET		(last+3),Q
		SET		(last+4),P2
		SET		(last+5),Q1
		PUSHJ		last,:DiffVariable
		JMP		done
1H		CMP		:t,tmp,:node:TYPE:LN
		BNZ		:t,1F
		SET		(last+1),P
		SET		(last+2),P1
		SET		(last+3),Q
		SET		(last+4),P2
		SET		(last+5),Q1
		PUSHJ		last,:DiffLn
		JMP		done
1H		CMP		:t,tmp,:node:TYPE:NEG
		BNZ		:t,1F
		SET		(last+1),P
		SET		(last+2),P1
		SET		(last+3),Q
		SET		(last+4),P2
		SET		(last+5),Q1
		PUSHJ		last,:DiffNeg
		JMP		done
1H		CMP		:t,tmp,:node:TYPE:ADD
		BNZ		:t,1F
		SET		(last+1),P
		SET		(last+2),P1
		SET		(last+3),Q
		SET		(last+4),P2
		SET		(last+5),Q1
		PUSHJ		last,:DiffAdd
		JMP		done
1H		CMP		:t,tmp,:node:TYPE:SUB
		BNZ		:t,1F
		SET		(last+1),P
		SET		(last+2),P1
		SET		(last+3),Q
		SET		(last+4),P2
		SET		(last+5),Q1
		PUSHJ		last,:DiffSub
		JMP		done
1H		CMP		:t,tmp,:node:TYPE:MULT
		BNZ		:t,1F
		SET		(last+1),P
		SET		(last+2),P1
		SET		(last+3),Q
		SET		(last+4),P2
		SET		(last+5),Q1
		PUSHJ		last,:DiffMult
		JMP		done
1H		CMP		:t,tmp,:node:TYPE:DIV
		BNZ		:t,1F
		SET		(last+1),P
		SET		(last+2),P1
		SET		(last+3),Q
		SET		(last+4),P2
		SET		(last+5),Q1
		PUSHJ		last,:DiffDiv
		JMP		done
1H		CMP		:t,tmp,:node:TYPE:EXP
		BNZ		:t,done
		SET		(last+1),P
		SET		(last+2),P1
		SET		(last+3),Q
		SET		(last+4),P2
		SET		(last+5),Q1
		PUSHJ		last,:DiffExp
done		PUT		:rJ,retaddr
		SET		$0,(last+1)
		SET		$1,last
		POP		2,0
		PREFIX		:

		PREFIX		Tree2:
x		IS		$0
U		IS		$1
V		IS		$2
retaddr		IS		$3
W		IS		$4
last		IS		$5
:Tree2		GET		retaddr,:rJ
		ANDNL		U,#0001
		ANDNL		V,#0001
		PUSHJ		last,:Alloc		W <= AVAIL
		SET		W,last
		LDO		:t,x,:node:TYPE
		STO		:t,W,:node:TYPE
		LDO		:t,x,:node:INFO
		STO		:t,W,:node:INFO		INFO(W) <- x
		STO		U,W,:node:LLINK		LLINK(W) <- U
		STO		V,U,:node:RLINK		RLINK(U) <- V
		LDO		:t,U,:node:RLINK
		ANDNL		:t,#0001	
		LDO		:t,U,:node:RLINK	RTAG(U) <- 0
		STO		W,V,:node:RLINK		RLINK(V) <- W
		LDO		:t,V,:node:RLINK
		ORL		:t,#0001
		STO		:t,V,:node:RLINK	RTAG(V) <- 1
		PUT		:rJ,retaddr
		SET		$0,W
		POP		1,0
		PREFIX		:

		PREFIX		Tree1:
x		IS		$0
U		IS		$1
retaddr		IS		$2
W		IS		$3
last		IS		$4
:Tree1		GET		retaddr,:rJ
		ANDNL		U,#0001
		PUSHJ		last,:Alloc		W <= AVAIL
		SET		W,last
		LDO		:t,x,:node:TYPE
		STO		:t,W,:node:TYPE
		LDO		:t,x,:node:INFO
		STO		:t,W,:node:INFO		INFO(W) <- x
		STO		U,W,:node:LLINK		LLINK(W) <- U
		STO		W,U,:node:RLINK		RLINK(U) <- W
		LDO		:t,U,:node:RLINK
		ORL		:t,#0001	
		STO		:t,U,:node:RLINK	RTAG(U) <- 1
		PUT		:rJ,retaddr
		SET		$0,W
		POP		1,0
		PREFIX		:

		PREFIX		Tree0:
x		IS		$0
retaddr		IS		$1
W		IS		$2
last		IS		$3
:Tree0		GET		retaddr,:rJ
		PUSHJ		last,:Alloc		W <= AVAIL
		SET		W,last
		LDO		:t,x,:node:TYPE
		STO		:t,W,:node:TYPE
		LDO		:t,x,:node:INFO
		STO		:t,W,:node:INFO		INFO(W) <- x
		ORL		W,#0001
		STO		W,W,:node:LLINK		LLINK(W) <- thread to W
		PUT		:rJ,retaddr
		SET		$0,W
		POP		1,0
		PREFIX		:

		PREFIX		CopyBinaryTree:
HEAD		IS		$0
retaddr		IS		$1
T		IS		$2
P		IS		$3
Q		IS		$4
U		IS		$5
R		IS		$6
tmp		IS		$7
fakeHEAD	IS		$8
tmp2		IS		$9
last		IS		$10
;	  	C1	    	[Initialize.]
:CopyBinaryTree GET		retaddr,:rJ
		SET		tmp,HEAD
1H		SET		(last+1),tmp
		PUSHJ		last,:HasRightChild
		BZ		last,2F
		LDO		tmp,tmp,:node:RLINK
		JMP		1B
2H		SET		(last+1),tmp
		PUSHJ		last,:HasLeftChild
		BZ		last,3F
		LDO		tmp,tmp,:node:LLINK
		JMP		1B
3H		LDO		fakeHEAD,tmp,:node:RLINK	Set fakeHEAD to P$ (as a thread) where P is the last node in the subtree in preorder
		PUSHJ		last,:Alloc
		SET		tmp2,last
		STO		HEAD,tmp2,:node:LLINK
		STO		tmp2,tmp2,:node:RLINK
		PUSHJ		last,:Alloc
		SET		U,last		Allocate NODE(U)
		STO		U,U,:node:RLINK
		SET		:t,U
		ORL		:t,#0001
		STO		:t,U,:node:LLINK
		SET		P,tmp2		P <- HEAD
		SET		Q,U		Q <- U
		JMP		4F
;	  	C2	    	[Anything to right?]
2H		SET		(last+1),P
		PUSHJ		last,:HasRightChild
		BZ		last,3F			If P doesn't have a right subtree, skip to C3
		PUSHJ		last,:Alloc
		SET		R,last		R <= AVAIL
		SET		(last+1),Q
		SET		(last+2),R
		PUSHJ		last,:AttachAsRightChild
;	  	C3	    	[Copy INFO]
3H		LDO		:t,P,:node:INFO
		STO		:t,Q,:node:INFO
		LDO		:t,P,:node:TYPE
		STO		:t,Q,:node:TYPE 	INFO(Q) <- INFO(P)
;	  	C4	    	[Anything to left?]
4H		SET		(last+1),P
		PUSHJ		last,:HasLeftChild
		BZ		last,6F			If P doesn't have a left subtree, skip to C6
		PUSHJ		last,:Alloc
		SET		R,last		R <= AVAIL
		SET		(last+1),Q
		SET		(last+2),R
		PUSHJ		last,:AttachAsLeftChild
;	  	C6	    	[Test if complete.]
6H		LDO		:t,P,:node:RLINK
		CMP		:t,:t,fakeHEAD
		BNZ		:t,5F		if true, terminate otherwise go to C2
		SET		(last+1),tmp2
		PUSHJ		last,:Dealloc
		LDO		$0,U,:node:LLINK
		SET		(last+1),U
		PUSHJ		last,:Dealloc
		PUT		:rJ,retaddr
		POP		1,0
;	  	C5	    	[Advance.]
5H		SET		(last+1),P
		PUSHJ		last,:PreorderSuccessor
		SET		P,last		P <- P*
		SET		(last+1),Q
		PUSHJ		last,:PreorderSuccessor
		SET		Q,last		Q <- Q*
		JMP		2B
		PREFIX		:

		PREFIX		AttachAsRightChild:
P		IS		$0
Q		IS		$1
retaddr		IS		$2
last		IS		$3
:AttachAsRightChild GET		retaddr,:rJ
		LDO		:t,P,:node:RLINK
		STO		:t,Q,:node:RLINK	Copy RLINK(P) to Q
		ANDNL		Q,#0001
		STO		Q,P,:node:RLINK	RLINK(P) <- Q, RTAG(P) <- 0
		ORL		P,#0001
		STO		P,Q,:node:LLINK LLINK(Q) <- P, LTAG(Q) <- 1
2H		SET		(last+1),Q
		PUSHJ		last,:HasRightChild
		BZ		last,done		if RTAG(Q)=1, terminate
		SET		(last+1),Q
;		PUSHJ		last,:InorderSuccessor		last <- Q$
		ORL		Q,#0001
		STO		Q,last,:node:LLINK	LLINK(Q$) <- Q, LTAG(Q$) is always a thread
done		PUT		:rJ,retaddr
		POP		0,0
		PREFIX		:

		PREFIX		AttachAsLeftChild:
P		IS		$0
Q		IS		$1
retaddr		IS		$2
last		IS		$3
:AttachAsLeftChild GET		retaddr,:rJ
		LDO		:t,P,:node:LLINK
		STO		:t,Q,:node:LLINK	Copy LLINK(P) to Q
		ANDNL		Q,#0001
		STO		Q,P,:node:LLINK	LLINK(P) <- Q, LTAG(P) <- 0
		ORL		P,#0001
		STO		P,Q,:node:RLINK RLINK(Q) <- P, RTAG(Q) <- 1
2H		SET		(last+1),Q
		PUSHJ		last,:HasLeftChild
		BZ		last,done		if LTAG(Q)=1, terminate
		SET		(last+1),Q
;		PUSHJ		last,:InorderPredecessor	last <- $Q
		ORL		Q,#0001
		STO		Q,last,:node:RLINK	RLINK($Q) <- Q, RTAG($Q) is always a thread
done		PUT		:rJ,retaddr
		POP		0,0
		PREFIX		:

		PREFIX		InorderThreadedFptr:
T		IS		$0
fptr		IS		$1
retaddr		IS		$2
tmp		IS		$3
P		IS		$4
Q		IS		$5
last		IS		$6
:InorderThreadedFptr GET	retaddr,:rJ
		LDO		tmp,T,:node:LLINK
		BZ   		tmp,done		If the tree is empty, exit immediately 
1H		SET		(last+1),tmp
		PUSHJ		last,:HasLeftChild
		BZ		last,firstNode
		LDO		tmp,tmp,:node:LLINK
		JMP		1B			This moves tmp to the first inorder node in the tree
firstNode	SET		P,tmp
1H		SET		:t,T
		ORL		:t,#0001
		CMP		:t,P,:t		Check if P = tree head (as thread)
		BZ		:t,done
		SET		(last+1),P
		PUSHGO		last,fptr		Visit node
		SET		(last+1),P
		PUSHJ		last,:InorderSuccessor
		SET		Q,last
		SET		P,Q
		JMP		1B
done		PUT		:rJ,retaddr
		POP		0,0
		PREFIX		:

		PREFIX		PreorderSuccessor:
P		IS		$0
retaddr		IS		$1
Q		IS		$2
last		IS		$3
:PreorderSuccessor GET		retaddr,:rJ
		SET		Q,P
		SET		(last+1),P
		PUSHJ		last,:HasLeftChild
		BZ		last,noLeft
		LDO		Q,P,:node:LLINK
		JMP		done
noLeft		SET		(last+1),P
		PUSHJ		last,:HasRightChild
		BZ		last,noRight
		LDO		Q,P,:node:RLINK
		JMP		done
noRight		LDO		Q,Q,:node:RLINK
		SET		(last+1),Q
		PUSHJ		last,:HasRightChild
		BNZ		last,found
		JMP		noRight
found		LDO		Q,Q,:node:RLINK
done		SET		$0,Q
		PUT		:rJ,retaddr
		POP		1,0
		PREFIX		:

		PREFIX		InorderSuccessor:
P		IS		$0
retaddr		IS		$1
Q		IS		$2
last		IS		$3
:InorderSuccessor GET		retaddr,:rJ
		LDO		Q,P,:node:RLINK
		SET		(last+1),P
		PUSHJ		last,:HasRightChild
		BZ		last,done
1H		SET		(last+1),Q
		PUSHJ		last,:HasLeftChild
		BZ		last,done
		LDO		Q,Q,:node:LLINK
		JMP		1B
done		SET		$0,Q
		PUT		:rJ,retaddr
		POP		1,0
		PREFIX		:
		
		PREFIX		InorderPredecessor:
P		IS		$0
retaddr		IS		$1
Q		IS		$2
last		IS		$3
:InorderPredecessor GET		retaddr,:rJ
		LDO		Q,P,:node:LLINK
		SET		(last+1),P
		PUSHJ		last,:HasLeftChild
		BZ		last,done
1H		SET		(last+1),Q
		PUSHJ		last,:HasRightChild 
		BZ		last,done
		LDO		Q,Q,:node:RLINK
		JMP		1B
done		SET		$0,Q
		PUT		:rJ,retaddr
		POP		1,0
		PREFIX		:

		PREFIX		AddThreads:
P		IS		$0
retaddr		IS		$1
tmp		IS		$2
last		IS		$10
lastVisited	GREG
:AddThreads 	GET		retaddr,:rJ
		SET		(last+1),P
		PUSHJ		last,:HasLeftChild
		BNZ		last,hasLeft			If P has a left child
		ORL		lastVisited,#0001
		STO		lastVisited,P,:node:LLINK	LLINK(P) <- lastVisited (as a thread)
hasLeft		SET		(last+1),lastVisited
		PUSHJ		last,:HasRightChild
		BNZ		last,hasRight			If lastVisited has a right child
		ORL		P,#0001
		STO		P,lastVisited,:node:RLINK	RLINK(lastVisited) <- P (as a thread)
hasRight	SET		lastVisited,P
		PUT		:rJ,retaddr
		POP		0,0
		PREFIX		:
		
		PREFIX		ThreadTree:
T		IS		$0
retaddr		IS		$1
tmp		IS		$2
last		IS		$10
:ThreadTree GET		retaddr,:rJ
		SET		:AddThreads:lastVisited,T
		LDO		(last+1),T
		GETA		(last+2),:AddThreads
		PUSHJ		last,:InorderFptr
		SET		tmp,T
		ANDNL		tmp,#0001
		SET		:t,:AddThreads:lastVisited
		ANDNL		:t,#0001
		CMP		:t,:t,tmp		Compare T to lastVisited, ignoring tags
		BZ		:t,emptyTree
		ORL		tmp,#0001
		STO		tmp,:AddThreads:lastVisited,:node:RLINK		RLINK(lastVisited) <- T (as a thread)
emptyTree	PUT		:rJ,retaddr
		POP		0,0
		PREFIX		:

		PREFIX		HasLeftChild:
;		This can be used in both threaded and unthreaded trees.
;		In a threaded tree, zero means LTAG(P)=1
P		IS		$0
:HasLeftChild	LDO		:t,P,:node:LLINK
		BZ		:t,no		if LLINK(P) is null, return no
		SL		:t,:t,63	otherwise return opposite of LTAG(P)
		BNZ		:t,no
yes		SET		$0,1
		POP		1,0
no		SET		$0,0
		POP		1,0
		PREFIX		:

		PREFIX		HasRightChild:
;		This can be used in both threaded and unthreaded trees.
;		In a threaded tree, zero means RTAG(P)=1
P		IS		$0
:HasRightChild	LDO		:t,P,:node:RLINK
		BZ		:t,no		if RLINK(P) is null, return no
		SL		:t,:t,63	otherwise return opposite of RTAG(P)
		BNZ		:t,no
yes		SET		$0,1
		POP		1,0
no		SET		$0,0
		POP		1,0
		PREFIX		:

		PREFIX		Visit:
T		IS		$0
retaddr		IS		$1
PS		IS		$2
P		IS		$3
SP		IS		$4
last		IS		$10
:Visit 		GET		retaddr,:rJ
		LDO		P,T,:node:INFO
		SET		(last+1),T
		PUSHJ		last,:InorderSuccessor
		LDO		PS,last,:node:INFO
		SET		(last+1),T
		PUSHJ		last,:InorderPredecessor
		LDO		SP,last,:node:INFO
		PUT		:rJ,retaddr
		POP		0,0
		PREFIX		:

		PREFIX		Preorder:
T		IS		$0
retaddr		IS		$1
tmp		IS		$2
last		IS		$3
:Preorder 	GET		retaddr,:rJ
		SET		(last+1),T
		PUSHJ		last,:Visit
		LDO		:t,T,:node:LLINK
		SR		tmp,:t,1
		BZ		tmp,noLeft
		SET		(last+1),:t
		PUSHJ		last,:Preorder
noLeft          LDO		:t,T,:node:RLINK
		SR		tmp,:t,1
		BZ		tmp,noRight
		SET		(last+1),:t
		PUSHJ		last,:Preorder
noRight		PUT		:rJ,retaddr
		POP		0,0
		PREFIX		:

		PREFIX		Inorder:
T		IS		$0
retaddr		IS		$1
tmp		IS		$2
last		IS		$3
:Inorder 	GET		retaddr,:rJ
		LDO		:t,T,:node:LLINK
		SR		tmp,:t,1
		BZ		tmp,noLeft
		SET		(last+1),:t
		PUSHJ		last,:Inorder
noLeft		SET		(last+1),T
		PUSHJ		last,:Visit
		LDO		:t,T,:node:RLINK
		SR		tmp,:t,1
		BZ		tmp,noRight
		SET		(last+1),:t
		PUSHJ		last,:Inorder
noRight		PUT		:rJ,retaddr
		POP		0,0
		PREFIX		:

		PREFIX		Postorder:
T		IS		$0
retaddr		IS		$1
tmp		IS		$2
last		IS		$3
:Postorder 	GET		retaddr,:rJ
		LDO		:t,T,:node:LLINK
		SR		tmp,:t,1
		BZ		tmp,noLeft
		SET		(last+1),:t
		PUSHJ		last,:Postorder
noLeft          LDO		:t,T,:node:RLINK
		SR		tmp,:t,1
		BZ		tmp,noRight
		SET		(last+1),:t
		PUSHJ		last,:Postorder
noRight		SET		(last+1),T
		PUSHJ		last,:Visit
		PUT		:rJ,retaddr
		POP		0,0
		PREFIX		:
		
		PREFIX		PreorderFptr:
T		IS		$0
fptr		IS		$1
retaddr		IS		$2
tmp		IS		$3
last		IS		$4
:PreorderFptr 	GET		retaddr,:rJ
		SET		(last+1),T
		PUSHGO		last,fptr
		LDO		:t,T,:node:LLINK
		SR		tmp,:t,1
		BZ		tmp,noLeft
		SET		(last+1),:t
		SET		(last+2),fptr
		PUSHJ		last,:PreorderFptr
noLeft          LDO		:t,T,:node:RLINK
		SR		tmp,:t,1
		BZ		tmp,noRight
		SET		(last+1),:t
		SET		(last+2),fptr
		PUSHJ		last,:PreorderFptr
noRight		PUT		:rJ,retaddr
		POP		0,0
		PREFIX		:

		PREFIX		InorderFptr:
T		IS		$0
fptr		IS		$1
retaddr		IS		$2
tmp		IS		$3
last		IS		$4
:InorderFptr 	GET		retaddr,:rJ
		LDO		:t,T,:node:LLINK
		SR		tmp,:t,1
		BZ		tmp,noLeft
		SET		(last+1),:t
		SET		(last+2),fptr
		PUSHJ		last,:InorderFptr
noLeft		SET		(last+1),T
		PUSHGO		last,fptr
		LDO		:t,T,:node:RLINK
		SR		tmp,:t,1
		BZ		tmp,noRight
		SET		(last+1),:t
		SET		(last+2),fptr
		PUSHJ		last,:InorderFptr
noRight		PUT		:rJ,retaddr
		POP		0,0
		PREFIX		:

		PREFIX		PostorderFptr:
T		IS		$0
fptr		IS		$1
retaddr		IS		$2
tmp		IS		$3
last		IS		$4
:PostorderFptr 	GET		retaddr,:rJ
		LDO		:t,T,:node:LLINK
		SR		tmp,:t,1
		BZ		tmp,noLeft
		SET		(last+1),:t
		SET		(last+2),fptr
		PUSHJ		last,:PostorderFptr
noLeft          LDO		:t,T,:node:RLINK
		SR		tmp,:t,1
		BZ		tmp,noRight
		SET		(last+1),:t
		SET		(last+2),fptr
		PUSHJ		last,:PostorderFptr
noRight		SET		(last+1),T
		PUSHGO		last,fptr
		PUT		:rJ,retaddr
		POP		0,0
		PREFIX		:

;		Stores a pointer to the root at T
;		       	 	    	     	y>
;                  				|
;		     ^				^
;		    / \				|
;		   x   x			x --> x
		PREFIX		ConstructTree18:
retaddr		IS		$0
tmp1		IS		$1
last		IS		$2
:ConstructTree18 GET		retaddr,:rJ
;
		PUSHJ		last,:Alloc
		SETL		:t,' '<<8+' '
		INCML		:t,' '<<8+' '
		INCMH		:t,' '<<8+' '
		INCH		:t,'x'<<8+' '
		STO		:t,last,:node:INFO
		SET		:t,:node:TYPE:VARIABLE
		STO		:t,last,:node:TYPE
		SET		tmp1,last
;
		PUSHJ		last,:Alloc
		SETL		:t,' '<<8+' '
		INCML		:t,' '<<8+' '
		INCMH		:t,' '<<8+' '
		INCH		:t,'x'<<8+' '
		STO		:t,last,:node:INFO
		SET		:t,:node:TYPE:VARIABLE
		STO		:t,last,:node:TYPE
		STO		tmp1,last,:node:RLINK
		SET		tmp1,last
;
		PUSHJ		last,:Alloc
		SETL		:t,' '<<8+' '
		INCML		:t,' '<<8+' '
		INCMH		:t,' '<<8+' '
		INCH		:t,'^'<<8+' '
		STO		:t,last,:node:INFO
		SET		:t,:node:TYPE:EXP
		STO		:t,last,:node:TYPE
		STO		tmp1,last,:node:LLINK
		SET		tmp1,last
;		
		PUSHJ		last,:Alloc
		SETL		:t,' '<<8+' '
		INCML		:t,' '<<8+' '
		INCMH		:t,' '<<8+' '
		INCH		:t,'y'<<8+' '
		STO		:t,last,:node:INFO
		SET		:t,:node:TYPE:VARIABLE
		STO		:t,last,:node:TYPE
		STO		tmp1,last,:node:LLINK
		STO		last,last,:node:RLINK
;
		PUT	    	:rJ,retaddr
		SET		$0,last
		POP		1,0
		PREFIX		:

;		Stores a pointer to the root at T
;		       	 	    	     	y>
;                  				|
;		     /				/
;		    / \				|
;		   a   x			a --> x
		PREFIX		ConstructTree17:
retaddr		IS		$0
tmp1		IS		$1
last		IS		$2
:ConstructTree17 GET		retaddr,:rJ
;
		PUSHJ		last,:Alloc
		SETL		:t,' '<<8+' '
		INCML		:t,' '<<8+' '
		INCMH		:t,' '<<8+' '
		INCH		:t,'x'<<8+' '
		STO		:t,last,:node:INFO
		SET		:t,:node:TYPE:VARIABLE
		STO		:t,last,:node:TYPE
		SET		tmp1,last
;
		PUSHJ		last,:Alloc
		SETL		:t,' '<<8+' '
		INCML		:t,' '<<8+' '
		INCMH		:t,' '<<8+' '
		INCH		:t,'a'<<8+' '
		STO		:t,last,:node:INFO
		SET		:t,:node:TYPE:VARIABLE
		STO		:t,last,:node:TYPE
		STO		tmp1,last,:node:RLINK
		SET		tmp1,last
;
		PUSHJ		last,:Alloc
		SETL		:t,' '<<8+' '
		INCML		:t,' '<<8+' '
		INCMH		:t,' '<<8+' '
		INCH		:t,'/'<<8+' '
		STO		:t,last,:node:INFO
		SET		:t,:node:TYPE:DIV
		STO		:t,last,:node:TYPE
		STO		tmp1,last,:node:LLINK
		SET		tmp1,last
;		
		PUSHJ		last,:Alloc
		SETL		:t,' '<<8+' '
		INCML		:t,' '<<8+' '
		INCMH		:t,' '<<8+' '
		INCH		:t,'y'<<8+' '
		STO		:t,last,:node:INFO
		SET		:t,:node:TYPE:VARIABLE
		STO		:t,last,:node:TYPE
		STO		tmp1,last,:node:LLINK
		STO		last,last,:node:RLINK
;
		PUT	    	:rJ,retaddr
		SET		$0,last
		POP		1,0
		PREFIX		:

;		Stores a pointer to the root at T
;		       	 	    	     	y>
;                  				|
;		     /				/
;		    / \				|
;		   x   a			x --> a
		PREFIX		ConstructTree16:
retaddr		IS		$0
tmp1		IS		$1
last		IS		$2
:ConstructTree16 GET		retaddr,:rJ
;
		PUSHJ		last,:Alloc
		SETL		:t,' '<<8+' '
		INCML		:t,' '<<8+' '
		INCMH		:t,' '<<8+' '
		INCH		:t,'a'<<8+' '
		STO		:t,last,:node:INFO
		SET		:t,:node:TYPE:VARIABLE
		STO		:t,last,:node:TYPE
		SET		tmp1,last
;
		PUSHJ		last,:Alloc
		SETL		:t,' '<<8+' '
		INCML		:t,' '<<8+' '
		INCMH		:t,' '<<8+' '
		INCH		:t,'x'<<8+' '
		STO		:t,last,:node:INFO
		SET		:t,:node:TYPE:VARIABLE
		STO		:t,last,:node:TYPE
		STO		tmp1,last,:node:RLINK
		SET		tmp1,last
;
		PUSHJ		last,:Alloc
		SETL		:t,' '<<8+' '
		INCML		:t,' '<<8+' '
		INCMH		:t,' '<<8+' '
		INCH		:t,'/'<<8+' '
		STO		:t,last,:node:INFO
		SET		:t,:node:TYPE:DIV
		STO		:t,last,:node:TYPE
		STO		tmp1,last,:node:LLINK
		SET		tmp1,last
;		
		PUSHJ		last,:Alloc
		SETL		:t,' '<<8+' '
		INCML		:t,' '<<8+' '
		INCMH		:t,' '<<8+' '
		INCH		:t,'y'<<8+' '
		STO		:t,last,:node:INFO
		SET		:t,:node:TYPE:VARIABLE
		STO		:t,last,:node:TYPE
		STO		tmp1,last,:node:LLINK
		STO		last,last,:node:RLINK
;
		PUT	    	:rJ,retaddr
		SET		$0,last
		POP		1,0
		PREFIX		:

;		Stores a pointer to the root at T
;		       	 	    	     	y>
;                  				|
;		     /				/
;		    / \				|
;		   1   x			1 --> x
		PREFIX		ConstructTree15:
retaddr		IS		$0
tmp1		IS		$1
last		IS		$2
:ConstructTree15 GET		retaddr,:rJ
;
		PUSHJ		last,:Alloc
		SETL		:t,' '<<8+' '
		INCML		:t,' '<<8+' '
		INCMH		:t,' '<<8+' '
		INCH		:t,'x'<<8+' '
		STO		:t,last,:node:INFO
		SET		:t,:node:TYPE:VARIABLE
		STO		:t,last,:node:TYPE
		SET		tmp1,last
;
		PUSHJ		last,:Alloc
		SETL		:t,' '<<8+' '
		INCML		:t,' '<<8+' '
		INCMH		:t,' '<<8+' '
		INCH		:t,'1'<<8+' '
		STO		:t,last,:node:INFO
		SET		:t,:node:TYPE:CONSTANT
		STO		:t,last,:node:TYPE
		STO		tmp1,last,:node:RLINK
		SET		tmp1,last
;
		PUSHJ		last,:Alloc
		SETL		:t,' '<<8+' '
		INCML		:t,' '<<8+' '
		INCMH		:t,' '<<8+' '
		INCH		:t,'/'<<8+' '
		STO		:t,last,:node:INFO
		SET		:t,:node:TYPE:DIV
		STO		:t,last,:node:TYPE
		STO		tmp1,last,:node:LLINK
		SET		tmp1,last
;		
		PUSHJ		last,:Alloc
		SETL		:t,' '<<8+' '
		INCML		:t,' '<<8+' '
		INCMH		:t,' '<<8+' '
		INCH		:t,'y'<<8+' '
		STO		:t,last,:node:INFO
		SET		:t,:node:TYPE:VARIABLE
		STO		:t,last,:node:TYPE
		STO		tmp1,last,:node:LLINK
		STO		last,last,:node:RLINK
;
		PUT	    	:rJ,retaddr
		SET		$0,last
		POP		1,0
		PREFIX		:

;		Stores a pointer to the root at T
;		       	 	    	     	y>
;                  				|
;		     ln				ln
;		    /				|
;		   x				x
		PREFIX		ConstructTree14:
retaddr		IS		$0
tmp1		IS		$1
last		IS		$2
:ConstructTree14 GET		retaddr,:rJ
;
		PUSHJ		last,:Alloc
		SETL		:t,' '<<8+' '
		INCML		:t,' '<<8+' '
		INCMH		:t,' '<<8+' '
		INCH		:t,'x'<<8+' '
		STO		:t,last,:node:INFO
		SET		:t,:node:TYPE:VARIABLE
		STO		:t,last,:node:TYPE
		SET		tmp1,last
;		
		PUSHJ		last,:Alloc
		SETL		:t,' '<<8+' '
		INCML		:t,' '<<8+' '
		INCMH		:t,' '<<8+' '
		INCH		:t,'l'<<8+'n'
		STO		:t,last,:node:INFO
		SET		:t,:node:TYPE:LN
		STO		:t,last,:node:TYPE
		STO		tmp1,last,:node:LLINK
		SET		tmp1,last
;		
		PUSHJ		last,:Alloc
		SETL		:t,' '<<8+' '
		INCML		:t,' '<<8+' '
		INCMH		:t,' '<<8+' '
		INCH		:t,'y'<<8+' '
		STO		:t,last,:node:INFO
		SET		:t,:node:TYPE:VARIABLE
		STO		:t,last,:node:TYPE
		STO		tmp1,last,:node:LLINK
		STO		last,last,:node:RLINK
;
		PUT	    	:rJ,retaddr
		SET		$0,last
		POP		1,0
		PREFIX		:

;		Stores a pointer to the root at T
;		       	 	    	     	y>
;                  				|
;		     *				*
;		    / \				|
;		   x   x			x --> x
		PREFIX		ConstructTree13:
retaddr		IS		$0
tmp1		IS		$1
last		IS		$2
:ConstructTree13 GET		retaddr,:rJ
;
		PUSHJ		last,:Alloc
		SETL		:t,' '<<8+' '
		INCML		:t,' '<<8+' '
		INCMH		:t,' '<<8+' '
		INCH		:t,'x'<<8+' '
		STO		:t,last,:node:INFO
		SET		:t,:node:TYPE:VARIABLE
		STO		:t,last,:node:TYPE
		SET		tmp1,last
;
		PUSHJ		last,:Alloc
		SETL		:t,' '<<8+' '
		INCML		:t,' '<<8+' '
		INCMH		:t,' '<<8+' '
		INCH		:t,'x'<<8+' '
		STO		:t,last,:node:INFO
		SET		:t,:node:TYPE:VARIABLE
		STO		:t,last,:node:TYPE
		STO		tmp1,last,:node:RLINK
		SET		tmp1,last
;
		PUSHJ		last,:Alloc
		SETL		:t,' '<<8+' '
		INCML		:t,' '<<8+' '
		INCMH		:t,' '<<8+' '
		INCH		:t,'*'<<8+' '
		STO		:t,last,:node:INFO
		SET		:t,:node:TYPE:MULT
		STO		:t,last,:node:TYPE
		STO		tmp1,last,:node:LLINK
		SET		tmp1,last
;		
		PUSHJ		last,:Alloc
		SETL		:t,' '<<8+' '
		INCML		:t,' '<<8+' '
		INCMH		:t,' '<<8+' '
		INCH		:t,'y'<<8+' '
		STO		:t,last,:node:INFO
		SET		:t,:node:TYPE:VARIABLE
		STO		:t,last,:node:TYPE
		STO		tmp1,last,:node:LLINK
		STO		last,last,:node:RLINK
;
		PUT	    	:rJ,retaddr
		SET		$0,last
		POP		1,0
		PREFIX		:

;		Stores a pointer to the root at T
;		       	 	    	     	y>
;                  				|
;		     *				*
;		    / \				|
;		   y   0			y --> 0
		PREFIX		ConstructTree12:
retaddr		IS		$0
tmp1		IS		$1
last		IS		$2
:ConstructTree12 GET		retaddr,:rJ
;
		PUSHJ		last,:Alloc
		SETL		:t,' '<<8+' '
		INCML		:t,' '<<8+' '
		INCMH		:t,' '<<8+' '
		INCH		:t,'0'<<8+' '
		STO		:t,last,:node:INFO
		SET		:t,:node:TYPE:CONSTANT
		STO		:t,last,:node:TYPE
		SET		tmp1,last
;
		PUSHJ		last,:Alloc
		SETL		:t,' '<<8+' '
		INCML		:t,' '<<8+' '
		INCMH		:t,' '<<8+' '
		INCH		:t,'y'<<8+' '
		STO		:t,last,:node:INFO
		SET		:t,:node:TYPE:VARIABLE
		STO		:t,last,:node:TYPE
		STO		tmp1,last,:node:RLINK
		SET		tmp1,last
;
		PUSHJ		last,:Alloc
		SETL		:t,' '<<8+' '
		INCML		:t,' '<<8+' '
		INCMH		:t,' '<<8+' '
		INCH		:t,'*'<<8+' '
		STO		:t,last,:node:INFO
		SET		:t,:node:TYPE:MULT
		STO		:t,last,:node:TYPE
		STO		tmp1,last,:node:LLINK
		SET		tmp1,last
;		
		PUSHJ		last,:Alloc
		SETL		:t,' '<<8+' '
		INCML		:t,' '<<8+' '
		INCMH		:t,' '<<8+' '
		INCH		:t,'y'<<8+' '
		STO		:t,last,:node:INFO
		SET		:t,:node:TYPE:VARIABLE
		STO		:t,last,:node:TYPE
		STO		tmp1,last,:node:LLINK
		STO		last,last,:node:RLINK
;
		PUT	    	:rJ,retaddr
		SET		$0,last
		POP		1,0
		PREFIX		:

;		Stores a pointer to the root at T
;		       	 	    	     	y>
;                  				|
;		     *				*
;		    / \				|
;		   1   x			1 --> x
		PREFIX		ConstructTree11:
retaddr		IS		$0
tmp1		IS		$1
last		IS		$2
:ConstructTree11 GET		retaddr,:rJ
;
		PUSHJ		last,:Alloc
		SETL		:t,' '<<8+' '
		INCML		:t,' '<<8+' '
		INCMH		:t,' '<<8+' '
		INCH		:t,'x'<<8+' '
		STO		:t,last,:node:INFO
		SET		:t,:node:TYPE:VARIABLE
		STO		:t,last,:node:TYPE
		SET		tmp1,last
;
		PUSHJ		last,:Alloc
		SETL		:t,' '<<8+' '
		INCML		:t,' '<<8+' '
		INCMH		:t,' '<<8+' '
		INCH		:t,'1'<<8+' '
		STO		:t,last,:node:INFO
		SET		:t,:node:TYPE:CONSTANT
		STO		:t,last,:node:TYPE
		STO		tmp1,last,:node:RLINK
		SET		tmp1,last
;
		PUSHJ		last,:Alloc
		SETL		:t,' '<<8+' '
		INCML		:t,' '<<8+' '
		INCMH		:t,' '<<8+' '
		INCH		:t,'*'<<8+' '
		STO		:t,last,:node:INFO
		SET		:t,:node:TYPE:MULT
		STO		:t,last,:node:TYPE
		STO		tmp1,last,:node:LLINK
		SET		tmp1,last
;		
		PUSHJ		last,:Alloc
		SETL		:t,' '<<8+' '
		INCML		:t,' '<<8+' '
		INCMH		:t,' '<<8+' '
		INCH		:t,'y'<<8+' '
		STO		:t,last,:node:INFO
		SET		:t,:node:TYPE:VARIABLE
		STO		:t,last,:node:TYPE
		STO		tmp1,last,:node:LLINK
		STO		last,last,:node:RLINK
;
		PUT	    	:rJ,retaddr
		SET		$0,last
		POP		1,0
		PREFIX		:

;		Stores a pointer to the root at T
;		       	 	    	     	y>
;                  				|
;		     -				-
;		    / \				|
;		   6   x			6 --> x
		PREFIX		ConstructTree10:
retaddr		IS		$0
tmp1		IS		$1
last		IS		$2
:ConstructTree10 GET		retaddr,:rJ
;
		PUSHJ		last,:Alloc
		SETL		:t,' '<<8+' '
		INCML		:t,' '<<8+' '
		INCMH		:t,' '<<8+' '
		INCH		:t,'x'<<8+' '
		STO		:t,last,:node:INFO
		SET		:t,:node:TYPE:VARIABLE
		STO		:t,last,:node:TYPE
		SET		tmp1,last
;
		PUSHJ		last,:Alloc
		SETL		:t,' '<<8+' '
		INCML		:t,' '<<8+' '
		INCMH		:t,' '<<8+' '
		INCH		:t,'6'<<8+' '
		STO		:t,last,:node:INFO
		SET		:t,:node:TYPE:CONSTANT
		STO		:t,last,:node:TYPE
		STO		tmp1,last,:node:RLINK
		SET		tmp1,last
;
		PUSHJ		last,:Alloc
		SETL		:t,' '<<8+' '
		INCML		:t,' '<<8+' '
		INCMH		:t,' '<<8+' '
		INCH		:t,'-'<<8+' '
		STO		:t,last,:node:INFO
		SET		:t,:node:TYPE:SUB
		STO		:t,last,:node:TYPE
		STO		tmp1,last,:node:LLINK
		SET		tmp1,last
;		
		PUSHJ		last,:Alloc
		SETL		:t,' '<<8+' '
		INCML		:t,' '<<8+' '
		INCMH		:t,' '<<8+' '
		INCH		:t,'y'<<8+' '
		STO		:t,last,:node:INFO
		SET		:t,:node:TYPE:VARIABLE
		STO		:t,last,:node:TYPE
		STO		tmp1,last,:node:LLINK
		STO		last,last,:node:RLINK
;
		PUT	    	:rJ,retaddr
		SET		$0,last
		POP		1,0
		PREFIX		:

;		Stores a pointer to the root at T
;		       	 	    	     	y>
;                  				|
;		     -				-
;		    / \				|
;		   x   a			x --> a
		PREFIX		ConstructTree9:
retaddr		IS		$0
tmp1		IS		$1
last		IS		$2
:ConstructTree9	GET		retaddr,:rJ
;
		PUSHJ		last,:Alloc
		SETL		:t,' '<<8+' '
		INCML		:t,' '<<8+' '
		INCMH		:t,' '<<8+' '
		INCH		:t,'a'<<8+' '
		STO		:t,last,:node:INFO
		SET		:t,:node:TYPE:VARIABLE
		STO		:t,last,:node:TYPE
		SET		tmp1,last
;
		PUSHJ		last,:Alloc
		SETL		:t,' '<<8+' '
		INCML		:t,' '<<8+' '
		INCMH		:t,' '<<8+' '
		INCH		:t,'x'<<8+' '
		STO		:t,last,:node:INFO
		SET		:t,:node:TYPE:VARIABLE
		STO		:t,last,:node:TYPE
		STO		tmp1,last,:node:RLINK
		SET		tmp1,last
;
		PUSHJ		last,:Alloc
		SETL		:t,' '<<8+' '
		INCML		:t,' '<<8+' '
		INCMH		:t,' '<<8+' '
		INCH		:t,'-'<<8+' '
		STO		:t,last,:node:INFO
		SET		:t,:node:TYPE:SUB
		STO		:t,last,:node:TYPE
		STO		tmp1,last,:node:LLINK
		SET		tmp1,last
;		
		PUSHJ		last,:Alloc
		SETL		:t,' '<<8+' '
		INCML		:t,' '<<8+' '
		INCMH		:t,' '<<8+' '
		INCH		:t,'y'<<8+' '
		STO		:t,last,:node:INFO
		SET		:t,:node:TYPE:VARIABLE
		STO		:t,last,:node:TYPE
		STO		tmp1,last,:node:LLINK
		STO		last,last,:node:RLINK
;
		PUT	    	:rJ,retaddr
		SET		$0,last
		POP		1,0
		PREFIX		:

;		Stores a pointer to the root at T
;		       	 	    	     	y>
;                  				|
;		     -				-
;		    / \				|
;		   x   x			x --> x
		PREFIX		ConstructTree8:
retaddr		IS		$0
tmp1		IS		$1
last		IS		$2
:ConstructTree8	GET		retaddr,:rJ
;
		PUSHJ		last,:Alloc
		SETL		:t,' '<<8+' '
		INCML		:t,' '<<8+' '
		INCMH		:t,' '<<8+' '
		INCH		:t,'x'<<8+' '
		STO		:t,last,:node:INFO
		SET		:t,:node:TYPE:VARIABLE
		STO		:t,last,:node:TYPE
		SET		tmp1,last
;
		PUSHJ		last,:Alloc
		SETL		:t,' '<<8+' '
		INCML		:t,' '<<8+' '
		INCMH		:t,' '<<8+' '
		INCH		:t,'x'<<8+' '
		STO		:t,last,:node:INFO
		SET		:t,:node:TYPE:VARIABLE
		STO		:t,last,:node:TYPE
		STO		tmp1,last,:node:RLINK
		SET		tmp1,last
;
		PUSHJ		last,:Alloc
		SETL		:t,' '<<8+' '
		INCML		:t,' '<<8+' '
		INCMH		:t,' '<<8+' '
		INCH		:t,'-'<<8+' '
		STO		:t,last,:node:INFO
		SET		:t,:node:TYPE:SUB
		STO		:t,last,:node:TYPE
		STO		tmp1,last,:node:LLINK
		SET		tmp1,last
;		
		PUSHJ		last,:Alloc
		SETL		:t,' '<<8+' '
		INCML		:t,' '<<8+' '
		INCMH		:t,' '<<8+' '
		INCH		:t,'y'<<8+' '
		STO		:t,last,:node:INFO
		SET		:t,:node:TYPE:VARIABLE
		STO		:t,last,:node:TYPE
		STO		tmp1,last,:node:LLINK
		STO		last,last,:node:RLINK
;
		PUT	    	:rJ,retaddr
		SET		$0,last
		POP		1,0
		PREFIX		:

;		Stores a pointer to the root at T
;		       	 	    	     	y>
;                  				|
;		     +				+
;		    / \				|
;		   3   x			3 --> x
		PREFIX		ConstructTree7:
retaddr		IS		$0
tmp1		IS		$1
last		IS		$2
:ConstructTree7	GET		retaddr,:rJ
;
		PUSHJ		last,:Alloc
		SETL		:t,' '<<8+' '
		INCML		:t,' '<<8+' '
		INCMH		:t,' '<<8+' '
		INCH		:t,'x'<<8+' '
		STO		:t,last,:node:INFO
		SET		:t,:node:TYPE:VARIABLE
		STO		:t,last,:node:TYPE
		SET		tmp1,last
;
		PUSHJ		last,:Alloc
		SETL		:t,' '<<8+' '
		INCML		:t,' '<<8+' '
		INCMH		:t,' '<<8+' '
		INCH		:t,'3'<<8+' '
		STO		:t,last,:node:INFO
		SET		:t,:node:TYPE:CONSTANT
		STO		:t,last,:node:TYPE
		STO		tmp1,last,:node:RLINK
		SET		tmp1,last
;
		PUSHJ		last,:Alloc
		SETL		:t,' '<<8+' '
		INCML		:t,' '<<8+' '
		INCMH		:t,' '<<8+' '
		INCH		:t,'+'<<8+' '
		STO		:t,last,:node:INFO
		SET		:t,:node:TYPE:ADD
		STO		:t,last,:node:TYPE
		STO		tmp1,last,:node:LLINK
		SET		tmp1,last
;		
		PUSHJ		last,:Alloc
		SETL		:t,' '<<8+' '
		INCML		:t,' '<<8+' '
		INCMH		:t,' '<<8+' '
		INCH		:t,'y'<<8+' '
		STO		:t,last,:node:INFO
		SET		:t,:node:TYPE:VARIABLE
		STO		:t,last,:node:TYPE
		STO		tmp1,last,:node:LLINK
		STO		last,last,:node:RLINK
;
		PUT	    	:rJ,retaddr
		SET		$0,last
		POP		1,0
		PREFIX		:

;		Stores a pointer to the root at T
;		       	 	    	     	y>
;                  				|
;		     +				+
;		    / \				|
;		   x   a			x --> a
		PREFIX		ConstructTree6:
retaddr		IS		$0
tmp1		IS		$1
last		IS		$2
:ConstructTree6	GET		retaddr,:rJ
;
		PUSHJ		last,:Alloc
		SETL		:t,' '<<8+' '
		INCML		:t,' '<<8+' '
		INCMH		:t,' '<<8+' '
		INCH		:t,'a'<<8+' '
		STO		:t,last,:node:INFO
		SET		:t,:node:TYPE:VARIABLE
		STO		:t,last,:node:TYPE
		SET		tmp1,last
;
		PUSHJ		last,:Alloc
		SETL		:t,' '<<8+' '
		INCML		:t,' '<<8+' '
		INCMH		:t,' '<<8+' '
		INCH		:t,'x'<<8+' '
		STO		:t,last,:node:INFO
		SET		:t,:node:TYPE:VARIABLE
		STO		:t,last,:node:TYPE
		STO		tmp1,last,:node:RLINK
		SET		tmp1,last
;
		PUSHJ		last,:Alloc
		SETL		:t,' '<<8+' '
		INCML		:t,' '<<8+' '
		INCMH		:t,' '<<8+' '
		INCH		:t,'+'<<8+' '
		STO		:t,last,:node:INFO
		SET		:t,:node:TYPE:ADD
		STO		:t,last,:node:TYPE
		STO		tmp1,last,:node:LLINK
		SET		tmp1,last
;		
		PUSHJ		last,:Alloc
		SETL		:t,' '<<8+' '
		INCML		:t,' '<<8+' '
		INCMH		:t,' '<<8+' '
		INCH		:t,'y'<<8+' '
		STO		:t,last,:node:INFO
		SET		:t,:node:TYPE:VARIABLE
		STO		:t,last,:node:TYPE
		STO		tmp1,last,:node:LLINK
		STO		last,last,:node:RLINK
;
		PUT	    	:rJ,retaddr
		SET		$0,last
		POP		1,0
		PREFIX		:

;		Stores a pointer to the root at T
;		       	 	    	     	y>
;                  				|
;		     x				x
		PREFIX		ConstructTree5:
retaddr		IS		$0
tmp1		IS		$1
last		IS		$2
:ConstructTree5	GET		retaddr,:rJ
;
		PUSHJ		last,:Alloc
		SETL		:t,' '<<8+' '
		INCML		:t,' '<<8+' '
		INCMH		:t,' '<<8+' '
		INCH		:t,'x'<<8+' '
		STO		:t,last,:node:INFO
		SET		:t,:node:TYPE:VARIABLE
		STO		:t,last,:node:TYPE
		SET		tmp1,last
;		
		PUSHJ		last,:Alloc
		SETL		:t,' '<<8+' '
		INCML		:t,' '<<8+' '
		INCMH		:t,' '<<8+' '
		INCH		:t,'y'<<8+' '
		STO		:t,last,:node:INFO
		SET		:t,:node:TYPE:VARIABLE
		STO		:t,last,:node:TYPE
		STO		tmp1,last,:node:LLINK
		STO		last,last,:node:RLINK
;
		PUT	    	:rJ,retaddr
		SET		$0,last
		POP		1,0
		PREFIX		:

;		Stores a pointer to the root at T
;		       	 	    	     	y>
;                  				|
;		     a				a
		PREFIX		ConstructTree4:
retaddr		IS		$0
tmp1		IS		$1
last		IS		$2
:ConstructTree4	GET		retaddr,:rJ
;
		PUSHJ		last,:Alloc
		SETL		:t,' '<<8+' '
		INCML		:t,' '<<8+' '
		INCMH		:t,' '<<8+' '
		INCH		:t,'a'<<8+' '
		STO		:t,last,:node:INFO
		SET		:t,:node:TYPE:VARIABLE
		STO		:t,last,:node:TYPE
		SET		tmp1,last
;		
		PUSHJ		last,:Alloc
		SETL		:t,' '<<8+' '
		INCML		:t,' '<<8+' '
		INCMH		:t,' '<<8+' '
		INCH		:t,'y'<<8+' '
		STO		:t,last,:node:INFO
		SET		:t,:node:TYPE:VARIABLE
		STO		:t,last,:node:TYPE
		STO		tmp1,last,:node:LLINK
		STO		last,last,:node:RLINK
;
		PUT	    	:rJ,retaddr
		SET		$0,last
		POP		1,0
		PREFIX		:

;		Stores a pointer to the root at T
;		       	 	    	     	y>
;                  				|
;		     4				4
		PREFIX		ConstructTree3:
retaddr		IS		$0
tmp1		IS		$1
last		IS		$2
:ConstructTree3	GET		retaddr,:rJ
;
		PUSHJ		last,:Alloc
		SETL		:t,' '<<8+' '
		INCML		:t,' '<<8+' '
		INCMH		:t,' '<<8+' '
		INCH		:t,'4'<<8+' '
		STO		:t,last,:node:INFO
		SET		:t,:node:TYPE:CONSTANT
		STO		:t,last,:node:TYPE
		SET		tmp1,last
;		
		PUSHJ		last,:Alloc
		SETL		:t,' '<<8+' '
		INCML		:t,' '<<8+' '
		INCMH		:t,' '<<8+' '
		INCH		:t,'y'<<8+' '
		STO		:t,last,:node:INFO
		SET		:t,:node:TYPE:VARIABLE
		STO		:t,last,:node:TYPE
		STO		tmp1,last,:node:LLINK
		STO		last,last,:node:RLINK
;
		PUT	    	:rJ,retaddr
		SET		$0,last
		POP		1,0
		PREFIX		:

;		Stores a pointer to the root at T
;		       	 	    	     	y>
;                  				|
;		     -				-
;		   /   \			|
;		 *       /			*  ------->  /
;	        / \     / \			|            |
;	       3  ln   a   ↑			3  --> ln    a --> ↑
;	       	   |   	  / \			       |     	   |
;		   +	 x   2			       +	   x --> 2
;		  / \	     			       |
;		 x   1				       x --> 1
		PREFIX		ConstructTree2:
retaddr		IS		$0
tmp1		IS		$1
tmp2		IS		$2
last		IS		$3
:ConstructTree2	GET		retaddr,:rJ
;		
		PUSHJ		last,:Alloc
		SETL		:t,' '<<8+' '
		INCML		:t,' '<<8+' '
		INCMH		:t,' '<<8+' '
		INCH		:t,'1'<<8+' '
		STO		:t,last,:node:INFO
		SET		:t,:node:TYPE:CONSTANT
		STO		:t,last,:node:TYPE
		SET		tmp1,last
;		
		PUSHJ		last,:Alloc
		SETL		:t,' '<<8+' '
		INCML		:t,' '<<8+' '
		INCMH		:t,' '<<8+' '
		INCH		:t,'x'<<8+' '
		STO		:t,last,:node:INFO
		SET		:t,:node:TYPE:VARIABLE
		STO		:t,last,:node:TYPE
		STO		tmp1,last,:node:RLINK
		SET		tmp1,last
;		
		PUSHJ		last,:Alloc
		SETL		:t,' '<<8+' '
		INCML		:t,' '<<8+' '
		INCMH		:t,' '<<8+' '
		INCH		:t,'+'<<8+' '
		STO		:t,last,:node:INFO
		SET		:t,:node:TYPE:ADD
		STO		:t,last,:node:TYPE
		STO		tmp1,last,:node:LLINK
		SET		tmp1,last
;		
		PUSHJ		last,:Alloc
		SETL		:t,' '<<8+' '
		INCML		:t,' '<<8+' '
		INCMH		:t,' '<<8+' '
		INCH		:t,'l'<<8+'n'
		STO		:t,last,:node:INFO
		SET		:t,:node:TYPE:LN
		STO		:t,last,:node:TYPE
		STO		tmp1,last,:node:LLINK
		SET		tmp1,last
;		
		PUSHJ		last,:Alloc
		SETL		:t,' '<<8+' '
		INCML		:t,' '<<8+' '
		INCMH		:t,' '<<8+' '
		INCH		:t,'3'<<8+' '
		STO		:t,last,:node:INFO
		SET		:t,:node:TYPE:CONSTANT
		STO		:t,last,:node:TYPE
		STO		tmp1,last,:node:RLINK
		SET		tmp1,last
;		
		PUSHJ		last,:Alloc
		SETL		:t,' '<<8+' '
		INCML		:t,' '<<8+' '
		INCMH		:t,' '<<8+' '
		INCH		:t,'2'<<8+' '
		STO		:t,last,:node:INFO
		SET		:t,:node:TYPE:CONSTANT
		STO		:t,last,:node:TYPE
		SET		tmp2,last
;		
		PUSHJ		last,:Alloc
		SETL		:t,' '<<8+' '
		INCML		:t,' '<<8+' '
		INCMH		:t,' '<<8+' '
		INCH		:t,'x'<<8+' '
		STO		:t,last,:node:INFO
		SET		:t,:node:TYPE:VARIABLE
		STO		:t,last,:node:TYPE
		STO		tmp2,last,:node:RLINK
		SET		tmp2,last
;		
		PUSHJ		last,:Alloc
		SETL		:t,' '<<8+' '
		INCML		:t,' '<<8+' '
		INCMH		:t,' '<<8+' '
		INCH		:t,'^'<<8+' '
		STO		:t,last,:node:INFO
		SET		:t,:node:TYPE:EXP
		STO		:t,last,:node:TYPE
		STO		tmp2,last,:node:LLINK
		SET		tmp2,last
;		
		PUSHJ		last,:Alloc
		SETL		:t,' '<<8+' '
		INCML		:t,' '<<8+' '
		INCMH		:t,' '<<8+' '
		INCH		:t,'a'<<8+' '
		STO		:t,last,:node:INFO
		SET		:t,:node:TYPE:VARIABLE
		STO		:t,last,:node:TYPE
		STO		tmp2,last,:node:RLINK
		SET		tmp2,last
;		
		PUSHJ		last,:Alloc
		SETL		:t,' '<<8+' '
		INCML		:t,' '<<8+' '
		INCMH		:t,' '<<8+' '
		INCH		:t,'/'<<8+' '
		STO		:t,last,:node:INFO
		SET		:t,:node:TYPE:DIV
		STO		:t,last,:node:TYPE
		STO		tmp2,last,:node:LLINK
		SET		tmp2,last
;		
		PUSHJ		last,:Alloc
		SETL		:t,' '<<8+' '
		INCML		:t,' '<<8+' '
		INCMH		:t,' '<<8+' '
		INCH		:t,'*'<<8+' '
		STO		:t,last,:node:INFO
		SET		:t,:node:TYPE:MULT
		STO		:t,last,:node:TYPE
		STO		tmp1,last,:node:LLINK
		STO		tmp2,last,:node:RLINK
		SET		tmp1,last
;		
		PUSHJ		last,:Alloc
		SETL		:t,' '<<8+' '
		INCML		:t,' '<<8+' '
		INCMH		:t,' '<<8+' '
		INCH		:t,'-'<<8+' '
		STO		:t,last,:node:INFO
		SET		:t,:node:TYPE:SUB
		STO		:t,last,:node:TYPE
		STO		tmp1,last,:node:LLINK
		SET		tmp1,last
;		
		PUSHJ		last,:Alloc
		SETL		:t,' '<<8+' '
		INCML		:t,' '<<8+' '
		INCMH		:t,' '<<8+' '
		INCH		:t,'y'<<8+' '
		STO		:t,last,:node:INFO
		SET		:t,:node:TYPE:VARIABLE
		STO		:t,last,:node:TYPE
		STO		tmp1,last,:node:LLINK
		STO		last,last,:node:RLINK
;
		PUT	    	:rJ,retaddr
		SET		$0,last
		POP		1,0
		PREFIX		:

;		Stores a pointer to the root at T
;                              A
;                             / \
;                            B   C
;                           /  /   \
;                          D  E     F
;                              \   / \
;                               G H   J
		PREFIX		ConstructTree:
T		IS		$0
retaddr		IS		$1
tmpLink		IS		$2
tmp1		IS		$3
tmp2		IS		$4
tmp3		IS		$5
last		IS		$6
:ConstructTree	GET		retaddr,:rJ
;
		PUSHJ		last,:Alloc
		SET		:t,'J'
		STO		:t,last,:node:INFO
		SET		tmp1,last
;		
		PUSHJ		last,:Alloc
		SET		:t,'H'
		STO		:t,last,:node:INFO
		SET		tmp2,last
;		
		PUSHJ		last,:Alloc
		SET		:t,'F'
		STO		:t,last,:node:INFO
		STO		tmp1,last,:node:RLINK
		STO		tmp2,last,:node:LLINK
		SET		tmp3,last
;		
		PUSHJ		last,:Alloc
		SET		:t,'G'
		STO		:t,last,:node:INFO
		SET		tmp1,last
;		
		PUSHJ		last,:Alloc
		SET		:t,'E'
		STO		:t,last,:node:INFO
		STO		tmp1,last,:node:RLINK
		SET		tmp2,last
;		
		PUSHJ		last,:Alloc
		SET		:t,'C'
		STO		:t,last,:node:INFO
		STO		tmp3,last,:node:RLINK
		STO		tmp2,last,:node:LLINK
		SET		tmp1,last
;		
		PUSHJ		last,:Alloc
		SET		:t,'D'
		STO		:t,last,:node:INFO
		SET		tmp2,last
;		
		PUSHJ		last,:Alloc
		SET		:t,'B'
		STO		:t,last,:node:INFO
		STO		tmp2,last,:node:LLINK
		SET		tmp3,last
;		
		PUSHJ		last,:Alloc
		SET		:t,'A'
		STO		:t,last,:node:INFO
		STO		tmp1,last,:node:RLINK
		STO		tmp3,last,:node:LLINK
;
		STO		last,T
		PUT	    	:rJ,retaddr
		POP		0,0
		PREFIX		:

		PREFIX		Alloc:
X	  	IS	    	$0
:Alloc	  	PBNZ		:AVAIL,1F
	 	SET		X,:POOLMAX
		ADD		:POOLMAX,X,:nodeSize
		CMP		:t,:POOLMAX,:SEQMIN
		PBNP		:t,2F
		TRAP		0,:Halt,0        Overflow (no nodes left)
1H		SET	    	X,:AVAIL
		LDO		:AVAIL,:AVAIL,:LINK
2H	  	POP	    	1,0
	  	PREFIX    	:
	  
		PREFIX		Dealloc:
;	  	Doesn't check if trying to dealloc a node that was never alloc'd	  
X	  	IS	      	$0
:Dealloc  	STO	      	:AVAIL,X,:LINK
1H	  	SET	      	:AVAIL,X
	  	POP	    	0,0
	  	PREFIX   	: