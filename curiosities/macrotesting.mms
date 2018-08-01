#define tst 1
#define __NL__
#define ADD_TRAINING(InputUnit1,InputValue1,InputUnit2,InputValue2,OutputUnit,OutputValue) \
1H	  IS   	    InputUnit1 __NL__\
2H	  IS   	    InputValue2 __NL__\
3H	  IS   	    InputUnit2 __NL__\
4H	  IS   	    InputValue2 __NL__\
5H	  IS   	    OutputUnit __NL__\
6H	  IS   	    OutputValue __NL__\
	  SET	    (last+1),2__NL__\
	  SET	    (last+2),trainingSet__NL__\
	  PUSHJ	    last,:PushArbi__NL__\
	  SET	    setPtr,last__NL__\
	  SET	    (last+1),2__NL__\
	  ADD	    subPtr,setPtr,:Y_1__NL__\
	  SET	    (last+2),subPtr__NL__\
	  PUSHJ	    last,:PushArbi__NL__\
	  SET	    :t,1B-1__NL__\
	  MUL	    :t,:t,:UNIT_SIZE__NL__\
	  ADD	    :t,:t,:Unit_arr__NL__\
	  STO	    :t,last,:Y_1__NL__\
	  SETL	    :t,2B%(1<<16) 0-15__NL__\
	  INCML	    :t,(2B>>16)%(1<<32) 16-31__NL__\
	  INCMH	    :t,(2B>>32)%(1<<48) 32-47__NL__\
	  INCH	    :t,(2B>>48) 48-63__NL__\
	  STO	    :t,last,:Y_2__NL__\
	  SET	    (last+1),2__NL__\
	  SET	    (last+2),subPtr__NL__\
	  PUSHJ	    last,:PushArbi__NL__\
	  SET	    :t,3B-1__NL__\
	  MUL	    :t,:t,:UNIT_SIZE__NL__\
	  ADD	    :t,:t,:Unit_arr__NL__\
	  STO	    :t,last,:Y_1__NL__\
	  SETL	    :t,4B%(1<<16) 0-15__NL__\
	  INCML	    :t,(4B>>16)%(1<<32) 16-31__NL__\
	  INCMH	    :t,(4B>>32)%(1<<48) 32-47__NL__\
	  INCH	    :t,(4B>>48) 48-63__NL__\
	  STO	    :t,last,:Y_2__NL__\
	  ADD	    subPtr,setPtr,:Y_2__NL__\
	  SET	    (last+1),2__NL__\
	  SET	    (last+2),subPtr__NL__\
	  PUSHJ	    last,:PushArbi__NL__\
	  SET	    :t,5B-1__NL__\
	  MUL	    :t,:t,:UNIT_SIZE__NL__\
	  ADD	    :t,:t,:Unit_arr__NL__\
	  STO	    :t,last,:Y_1__NL__\
	  SETL	    :t,6B%(1<<16) 0-15__NL__\
	  INCML	    :t,(6B>>16)%(1<<32) 16-31__NL__\
	  INCMH	    :t,(6B>>32)%(1<<48) 32-47__NL__\
	  INCH	    :t,(6B>>48) 48-63__NL__\
	  STO	    :t,last,:Y_2

ADD_TRAINING(2,#4000CCCCCCCCCCCD,4,#C008000000000000,9,#3FF0000000000000)
