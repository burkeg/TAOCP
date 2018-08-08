\def\date{05 Nov 2011}\def\source{V1F1, p.\ 47}\def\author{Udo Wermuth}\input mmix =-3
!!\clearline{\tenbf Farey series}\smallskip
t         IS        $255
          LOC       Data_Segment
_x        GREG      @
          LOC       Data_Segment+4*10000
_y        GREG      @
          LOC       #100
       !!\gts Computation of Farey series
       !!\gts Calling sequence: \mb{SET \$1,$n$; PUSHJ \$0,:Farey}
       !!\gts Entry conditions: $n$ in \mb{\$1} is the order of the series, $1 < n < 182$
       !!\gts \qquad \mb{\l\_x} and \mb{\l\_y} are arrays, each for at least 10000 tetras
       !!\gts Exit conditions: \mb{\$0} is number of $x/y$ pairs, i.e., entries generated in \mb{\l\_x} and \mb{\l\_y}
          PREFIX    :FAREY:             !! \startnumbering
n         IS        $1                  !! Parameter: order of the Farey series
kk        IS        $2                  !! $\mb{kk} \gets 4*k$
yk        IS        $3                  !! $y_k$
yk1       IS        $4                  !! $y_{k+1}$
xk        IS        $5                  !! $x_k$
xk1       IS        $6                  !! $x_{k+1}$
flr       IS        $7
yk2       IS        $8                  !! $y_{k+2}$
xk2       IS        $9                  !! $x_{k+2}$
:Farey    SET       n,$0                !1! Get the parameter.
          SET       xk,0                !1! Init for $k=0$.
          STTU      xk,:_x,4*0          !1!
          SET       yk,1                !1!
          STTU      yk,:_y,4*0          !1!
          SET       xk1,1               !1! Init for $k=1$.
          STTU      xk1,:_x,4*1         !1!
          SET       yk1,n               !1!
          STTU      yk1,:_y,4*1         !1!
          SET       kk,4                !1! $k\gets1$.
nextval   ADDU      flr,yk,n            !A! Calculate the next values \mb{xk2} and \mb{yk2}.
          DIVU      flr,flr,yk1         !A! $\mb{flr} \gets \lfloor(\mb{yk}+n)/\mb{yk1}\rfloor$.
          MULU      xk2,flr,xk1         !A!
          SUBU      xk2,xk2,xk          !A! $\mmm xk2 \gets \mmm flr*\mmm xk1 - \mm xk$.
          MULU      yk2,flr,yk1         !A!
          SUBU      yk2,yk2,yk          !A! $\mmm yk2 \gets \mmm flr*\mmm yk1 - \mm yk$.
          INCL      kk,4                !A! $k \gets k + 1$.
          STTU      xk2,:_x,kk          !A!
          STTU      yk2,:_y,kk          !A!
          SET       xk,xk1              !A! Shuffle the registers.
          SET       xk1,xk2             !A!
          SET       yk,yk1              !A!
          SET       yk1,yk2             !A!
          CMPU      flr,xk2,yk2         !A! The computation stops when
          PBNZ      flr,nextval         !A!\bad1\bad \quad  $1 = 1/1$ is computed.
          INCL      kk,4                !1!
          SR        kk,kk,2             !1! Remove factor for tetra.
          SET       $0,kk               !1! The number of elements
          POP       1,0                 !1! \quad  is returned.\eop
!!\endwAoA\bye
          PREFIX    :
       !!\gts Output the Farey series to StdOut
       !!\gts Calling sequence: \mb{SET \$1,$x$; PUSHJ \$0,:Output}
       !!\gts Entry condition: $x$ is the number of quotients to output, the data is in \mb{\l\_x} and \mb{\l\_y}
       !!\gts Exit condition:
          PREFIX    :Output:
          LOC       (@+7)&-8
          GREG      @
Buf       BYTE      "    /   ",#a,0     !! Template for output
NoPairs   BYTE      "000 pairs x/y have been generated",#a,0
_template GREG      #202020202F202020   !! This is ``\vs\vs\vs\vs/\vs\vs\vs''
items     IS        $1                  !! Parameter: number of array entries
asc       IS        $2                  !! An ASCII char
idx       IS        $3                  !! Index to {\tt\l\_x} and {\tt\l\_y}
acc       IS        $4                  !! The accumulator
pos       IS        $5                  !! Position in Buf
:Output   SET       items,$0            !! Get parameter.
          SL        items,items,2       !! Work with tetras.
          SET       idx,0               !! Init index for data.
          SET       acc,$0              !! Print parameter.
          LDA       :t,NoPairs
          SET       pos,2
0H        DIV       acc,acc,10
          GET       asc,:rR
          INCL      asc,'0'             !! Get an ASCII digit
          STBU      asc,:t,pos          !! \quad  and store it into \mb{NoPairs}.
          SUB       pos,pos,1
          PBNZ      acc,0B
          PBN       pos,2F              !! Fill leading zeros with blanks.
          SET       asc,' '
1H        STBU      asc,:t,pos
          SUB       pos,pos,1
          PBNN      pos,1B
2H        TRAP      0,:Fputs,:StdOut
7H        STOU      _template,Buf       !! Clear buffer.
          LDA       pos,Buf+2
          LDTU      acc,:_x,idx         !! Get value from array \mb{\l\_x}.
0H        DIV       acc,acc,10
          GET       asc,:rR
          INCL      asc,'0'             !! Convert to ASCII digit
          STBU      asc,pos,0           !! \quad and store it into \mb{Buf}.
          SUB       pos,pos,1
          PBNZ      acc,0B              !! Continue if $\mb{acc} > 0$.
          LDA       pos,Buf+7           !! Now output the \mb{\l\_y} value.
          LDTU      acc,:_y,idx
0H        DIV       acc,acc,10
          GET       asc,:rR
          INCL      asc,'0'
          STBU      asc,pos,0
          SUB       pos,pos,1
          PBNZ      acc,0B
          LDA       :t,Buf
          TRAP      0,:Fputs,:StdOut    !! Output \mb{Buf} and newline.
          INCL      idx,4               !! Next entries from the data arrays.
          CMP       :t,items,idx        !! Done?
          PBNZ      :t,7B               !! No, go back.
          POP       0,0                 !! Yes, return.
          PREFIX    :
       !!\gts
ord       IS        $1                  !! parameter to Farey: order of the series
pairs     IS        ord                 !! parameter to Output: number of pairs
          GREG      @
Banner    BYTE      "Farey series of order "
Order     BYTE      "00",#a,0
Main      SET       ord,#2037           !! First set the order to 7.
          STWU      ord,:Order
          LDA       t,Banner
          TRAP      0,Fputs,StdOut      !! Print Banner.
          SET       ord,7
          PUSHJ     $0,:Farey           !! Call Farey.
          SET       pairs,$0            !! Get number of pairs
          PUSHJ     $0,:Output          !! \quad and output the pairs.
          SET       ord,#3133           !! Next set the order to 13.
          STWU      ord,:Order
          LDA       t,Banner
          TRAP      0,Fputs,StdOut
          SET       ord,13
          PUSHJ     $0,:Farey
          SET       pairs,$0
          PUSHJ     $0,:Output
          SET       ord,#3339           !! Last test with order 39.
          STWU      ord,:Order
          LDA       t,Banner
          TRAP      0,Fputs,StdOut
          SET       ord,39
          PUSHJ     $0,:Farey
          SET       pairs,$0
          PUSHJ     $0,:Output
          TRAP      0,Halt,0            !! \eop
