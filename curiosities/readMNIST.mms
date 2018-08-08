;	Reads contents of MNIST

t	  IS	    $255
imageHandle IS	    5
labelHandle IS	    6
	  LOC       Data_Segment
	  GREG	    @
fopenArgs OCTA	    0,BinaryRead
freadArgs OCTA	    readData,0
train_labels BYTE   "train-labels.idx1-ubyte",0
train_images BYTE   "train-images.idx3-ubyte",0
test_labels BYTE    "t10k-labels.idx1-ubyte",0
test_images BYTE    "t10k-images.idx3-ubyte",0
	  LOC (@+7)&-8
labels_magic TETRA #00000801
images_magic TETRA #00000803
	  LOC (@+7)&-8
readData  OCTA	    0
	  LOC	    readData+28*28

	  LOC       #100
Main	  SET	    $1,1
	  PUSHJ	    $0,:OpenImages
	  SET	    $1,0
	  PUSHJ	    $0,:OpenLabels
	  LDA	    $1,:readData
	  PUSHJ	    $0,:LoadNextImage
	  TRAP	    0,Halt,0


	  PREFIX    OpenImages:
isTrain	  IS	    $0		0 means test set, 1 means training set
charPtr	  IS	    $1
numBytes  IS	    $2
freadAddr IS	    $3
readData  IS	    $4
tmp	  IS	    $5
:OpenImages BZ	    isTrain,test
train	  LDA	    charPtr,:train_images
	  JMP	    1F
test	  LDA	    charPtr,:test_images
1H	  LDA	    :t,:fopenArgs
	  STO	    charPtr,:t
	  LDA	    $255,:fopenArgs;	TRAP  0,:Fopen,:imageHandle
	  BN	    $255,failed
;	  Read the magic number to verify it is the correct file.
2H	  SET  	    numBytes,4
	  LDA	    freadAddr,:freadArgs
	  STO	    numBytes,freadAddr,8
	  LDA	    $255,:freadArgs;	TRAP  0,:Fread,:imageHandle
	  BN	    $255,failed
	  LDA	    readData,:readData
	  LDT	    :t,readData		Reads file's magic number
	  LDA	    tmp,:images_magic
	  LDT	    tmp,tmp		Reads correct magic number
	  CMP	    :t,:t,tmp
	  BNZ	    :t,failedMagic
	  LDA	    $255,:freadArgs;	TRAP  0,:Fread,:imageHandle
	  BN	    $255,failed
	  LDT	    $0,readData		Reads the number of images in file
	  LDA	    $255,:freadArgs;	TRAP  0,:Fread,:imageHandle
	  BN	    $255,failed		skips over number of rows
	  LDA	    $255,:freadArgs;	TRAP  0,:Fread,:imageHandle
	  BN	    $255,failed		skips over number of columns
	  POP	    1,0
failedMagic TRAP    0,:Halt,0	Wrong magic number!
failed	  TRAP	    0,:Halt,0	Unable to open file!
	  PREFIX    :

	  PREFIX    OpenLabels:
isTrain	  IS	    $0		0 means test set, 1 means training set
charPtr	  IS	    $1
numBytes  IS	    $2
freadAddr IS	    $3
readData  IS	    $4
tmp	  IS	    $5
:OpenLabels BZ	    isTrain,test
train	  LDA	    charPtr,:train_labels
	  JMP	    1F
test	  LDA	    charPtr,:test_labels
1H	  LDA	    :t,:fopenArgs
	  STO	    charPtr,:t
	  LDA	    $255,:fopenArgs;	TRAP  0,:Fopen,:labelHandle
	  BN	    $255,failed
;	  Read the magic number to verify it is the correct file.
2H	  SET  	    numBytes,4
	  LDA	    freadAddr,:freadArgs
	  STO	    numBytes,freadAddr,8
	  LDA	    $255,:freadArgs;	TRAP  0,:Fread,:labelHandle
	  BN	    $255,failed
	  LDA	    readData,:readData
	  LDT	    :t,readData		Reads file's magic number
	  LDA	    tmp,:labels_magic
	  LDT	    tmp,tmp		Reads correct magic number
	  CMP	    :t,:t,tmp
	  BNZ	    :t,failedMagic
	  LDA	    $255,:freadArgs;	TRAP  0,:Fread,:labelHandle
	  BN	    $255,failed
	  LDT	    $0,readData		Reads the number of labels in file
	  POP	    1,0
failedMagic TRAP    0,:Halt,0	Wrong magic number!
failed	  TRAP	    0,:Halt,0	Unable to open file!
	  PREFIX    :

	  PREFIX    LoadNextImage:
buffer	  IS	    $0
freadAddr IS	    $1
:LoadNextImage LDA  freadAddr,:freadArgs
	  TRAP 	    0,:Ftell,:imageHandle
	  SETL 	    :t,28*28
	  STO	    :t,freadAddr,8
	  LDA	    $255,:freadArgs;	TRAP  0,:Fread,:imageHandle
	  BN	    $255,failed		skips over number of rows
Done	  POP	    0,0
failed	  TRAP	    0,:Halt,0	Unable to read file!
	  PREFIX    :

	  PREFIX    LoadNextLabel:
buffer	  IS	    $0
freadAddr IS	    $1
:LoadNextLabel LDA  freadAddr,:freadArgs
	  TRAP 	    0,:Ftell,:labelHandle
	  SETL 	    :t,1
	  STO	    :t,freadAddr,8
	  LDA	    $255,:freadArgs;	TRAP  0,:Fread,:imageHandle
	  BN	    $255,failed		skips over number of rows
Done	  POP	    0,0
failed	  TRAP	    0,:Halt,0	Unable to read file!
	  PREFIX    :
