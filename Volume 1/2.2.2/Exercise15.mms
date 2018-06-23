% Monte Carlo Algo G vs moving 1 at a time

t 	    IS	   $255	       Temp var
nConst	    IS	   6
LinfConst   IS	   20
L0Const	    IS	   0
n	    GREG   nConst
elemSize    IS	   8
L0	    IS	   L0Const
Linf	    GREG   LinfConst

	    LOC	   Data_Segment	    
BASE	    GREG   @
1H	    OCTA   0
	    LOC	   1B+(nConst+1)*8
TOP	    GREG   @
1H	    OCTA   0
	    LOC	   1B+(nConst)*8
DATA	    GREG   @
2H	    OCTA   0
	    LOC	   2B+(LinfConst)*8
SEQ	    GREG   @
	    BYTE   "SSSS"
	    LOC	   @+(8-@%8)
OUT	    GREG   @
	    BYTE

BASEj	    IS	   $0
TOPj	    IS	   $1
LDiff	    IS	   $2
L0R	    IS	   $6
LinfR	    IS	   $8
j	    IS	   $3
Fj	    IS	   $4
Fn	    IS	   $5
newBase	    IS	   $7
	    LOC	   #100
Main	    SET	   t,Linf
	    SUB	   LDiff,t,L0
	    SET	   j,0
	    SET	   Fn,n
	    FLOT   LDiff,LDiff
	    FLOT   Fn,Fn
	    SET	   L0R,L0
	    SET	   LinfR,Linf
	    
1H	    FLOT   Fj,j
	    FMUL   t,Fj,LDiff
	    FDIV   t,t,Fn
	    FIX	   t,t
	    ADD	   newBase,L0R,t
	    SUB	   newBase,newBase,1
	    SL	   t,j,3
	    STO	   newBase,BASE,t
	    STO	   newBase,TOP,t
	    ADD	   j,j,1
	    CMP	   t,j,n
	    BNZ	   t,1B
	    SL	   t,j,3
	    SUB	   LinfR,LinfR,1
	    STO	   LinfR,BASE,t


;---------------------------------------;
i	    IS	   $1
Y	    IS	   $2
j	    IS	   $3
tmp2	    IS	   $4
j2	    IS	   $5
;---------------------------------------;
;	Hardcoded stack operations

	    SET	   Y,1
	    SET	   i,(nConst-1)*8
	    
;	    Push	    
	    SET	   $7,i
	    SET	   $8,Y
	    PUSHJ  $6,:Push
	    ADD	   Y,Y,1
	    	    
;	    Push	    
	    SET	   $7,i
	    SET	   $8,Y
	    PUSHJ  $6,:Push
	    ADD	   Y,Y,1
	    	    
;	    Push	    
	    SET	   $7,i
	    SET	   $8,Y
	    PUSHJ  $6,:Push
	    ADD	   Y,Y,1
	    	    
;	    Push	    
	    SET	   $7,i
	    SET	   $8,Y
	    PUSHJ  $6,:Push
	    ADD	   Y,Y,1
	    	    
;	    Push	    
	    SET	   $7,i
	    SET	   $8,Y
	    PUSHJ  $6,:Push
	    ADD	   Y,Y,1
	    	    
;	    Push	    
	    SET	   $7,i
	    SET	   $8,Y
	    PUSHJ  $6,:Push
	    ADD	   Y,Y,1
	    


	    TRAP   0,Halt,0
	    
;---------------------------------------;
;	Read a string of inputs and apply them from start to finish
;	to stacks 1 <= i < n
	    SET	   i,0
	    SET	   j2,0
5H	    SET	   Y,1
	    SET	   j,0
1H	    LDB	   :t,SEQ,j
	    CMP	   tmp2,:t,#53      S
	    BZ	   tmp2,2F
	    CMP	   tmp2,:t,#58      X
	    BZ	   tmp2,3F
	    SUB	   :t,n,2
	    SL	   :t,:t,3
	    CMP	   :t,i,:t
	    BZ	   :t,5F
	    ADD	   i,i,8
	    ADD	   j2,j2,8
	    JMP	   5B
5H	    TRAP   0,Halt,0
	    
2H	    SET	   $7,i
	    SET	   $8,Y
	    PUSHJ  $6,:Push
	    ADD	   i,i,0
	    ADD	   Y,Y,1
	    JMP	   4F
	    
	    
3H	    SET	   $7,i
	    PUSHJ  $6,:Pop
	    STO	   $6,OUT,j2
	    ADD	   j2,j2,8

4H	    ADD	   j,j,1
	    JMP	   1B
;---------------------------------------;


	    PREFIX Dump:
j	    IS	   $0
lim	    IS	   $1
:Dump	    SET	   j,0
	    ADD	   :t,:n,1
	    SL	   lim,:t,3
1H	    LDO	   :t,:BASE,j
	    ADD	   j,j,8
	    CMP	   :t,j,lim
	    BNZ	   :t,1B
	    SET	   j,0
	    SL	   lim,:n,3
1H	    LDO	   :t,:TOP,j
	    ADD	   j,j,8
	    CMP	   :t,j,lim
	    BNZ	   :t,1B
	    SET	   j,0
	    SUB	   :t,:Linf,:L0
	    SL	   lim,:t,3
1H	    LDO	   :t,:DATA,j
	    ADD	   j,j,8
	    CMP	   :t,j,lim
	    BNZ	   :t,1B
	    TRAP   0,:Halt,0
	    PREFIX :


	    PREFIX Push:
i	    IS	   $0
Y	    IS	   $1
BASEi1	    IS	   $2
TOPi	    IS	   $3
retaddr	    IS	   $4
:Push	    GET	   retaddr,:rJ
	    LDO	   TOPi,:TOP,i	    Load TOP[i]
	    ADD	   TOPi,TOPi,1	    
	    STO	   TOPi,:TOP,i	    Top[i] <- TOP[i]+1
	    ADD	   :t,i,8
	    LDO	   BASEi1,:BASE,:t  Load BASE[i+1]
	    CMP	   :t,TOPi,BASEi1
	    PBNP   :t,1F	    Branch if no overflow
	    SET	   $6,i
	    PUSHJ  $5,:Overflow
	    LDO	   TOPi,:TOP,i	    Reload TOP[i] in the case of overflow
1H	    SL	   :t,TOPi,3   Convert TOP[i] from an index to a byte offset
	    STO	   Y,:DATA,:t	    
	    PUT	   :rJ,retaddr
	    POP	   0,0
	    PREFIX :




	    PREFIX Pop:
i	    IS	   $0
BASEi	    IS	   $1
TOPi	    IS	   $2
Y	    IS	   $3
:Pop	    LDO	   BASEi,:BASE,i
	    LDO	   TOPi,:TOP,i
	    CMP	   :t,TOPi,BASEi
	    PBNZ   :t,1F
	    TRAP   0,:Halt,0	    Underflow occurred.
1H	    SL	   :t,TOPi,3   Convert TOP[i] from an index to a byte offset
	    LDO	   Y,:DATA,:t	    
	    SUB	   :t,TOPi,1
	    STO	   :t,:TOP,i
	    SET	   $0,Y
	    POP	   1,0
	    PREFIX :


	    PREFIX Overflow:
i	    IS	   $0
k	    IS	   $1
TOPk	    IS	   $2
BASEk1	    IS	   $3
L	    IS	   $4
lim	    IS	   $5
j	    IS	   $6
:Overflow   ADD	   k,i,8
4H	    SL	   :t,:n,3
	    CMP	   :t,k,:t
	    BZ	   :t,6F
;---------------------------------------;
;	Move things up a notch
	    LDO	   TOPk,:TOP,k
	    ADD	   :t,k,8
	    LDO	   BASEk1,:BASE,:t
	    CMP	   :t,TOPk,BASEk1
	    BN	   :t,5F
	    ADD	   k,k,8
	    JMP	   4B
5H	    SL	   lim,BASEk1,3
	    LDA	   lim,:DATA,lim
	    SL	   :t,TOPk,3
	    LDA	   L,:DATA,:t	  Load L with pointer to data TOPk references
	    ADD	   :t,i,8
	    LDO	   :t,:BASE,:t
	    CMP	   :t,:t,TOPk
	    BZ	   :t,1F
3H	    LDO	   :t,L,0
	    STO	   :t,L,8
	    SUB	   L,L,8
	    CMP	   :t,L,lim
	    PBNZ   :t,3B	  Shifts data right 1 index
	    
1H	    ADD	   j,i,8
2H	    LDO	   :t,:BASE,j
	    ADD	   :t,:t,1	
	    STO	   :t,:BASE,j	  BASE[j] <- BASE[j]+1
	    LDO	   :t,:TOP,j
	    ADD	   :t,:t,1	
	    STO	   :t,:TOP,j	  TOP[j] <- TOP[j]+1
	    ADD	   j,j,8
	    CMP	   :t,j,k
	    PBNP   :t,2B
	    JMP	   8F
	    
;---------------------------------------;
;	Move things down a notch
6H	    SUB	   k,i,8

4H	    BN	   k,7F
	    LDO    TOPk,:TOP,k
	    ADD	   :t,k,8
	    LDO	   BASEk1,:BASE,:t
	    CMP	   :t,TOPk,BASEk1
	    BN	   :t,5F
	    SUB	   k,k,8
	    JMP	   4B
5H	    LDO	   :t,:TOP,i
	    SL	   :t,:t,3
	    LDA	   lim,:DATA,:t
	    SUB	   lim,lim,8
	    SL	   :t,BASEk1,3
	    LDA	   L,:DATA,:t	  Load L with Loc(BASE[k+1])
3H	    LDO	   :t,L,8
	    STO	   :t,L,0
	    ADD	   L,L,8
	    CMP	   :t,L,lim
	    PBN   :t,3B	  Shifts data left 1 index
	    
1H	    SET	   j,i
2H	    LDO	   :t,:BASE,j
	    SUB	   :t,:t,1	
	    STO	   :t,:BASE,j	  BASE[j] <- BASE[j]+1
	    LDO	   :t,:TOP,j
	    SUB	   :t,:t,1	
	    STO	   :t,:TOP,j	  TOP[j] <- TOP[j]+1
	    SUB	   j,j,8
	    CMP	   :t,j,k
	    PBP    :t,2B
	    JMP	   8F
;---------------------------------------;



7H	    TRAP   0,:Halt,0	(GIVEUP)
8H	    POP	   0,0		(SUCCESS)
	    PREFIX :

