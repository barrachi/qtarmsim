.text
adr r0,maxneg
add r1,#3
ldrb r3,[r0,r1]
ldrsb r3,[r0,r1]
sub r1,#1
ldrh r3,[r0,r1]
ldrsh r3,[r0,r1]
ldm r0!,{r0,r1,r3}
adr r0,maxpos
ldm r0,{r0,r1,r3}
adr r0,maxpos
ldm r0!,{r1,r3}
adr r0,maxpos
ldm r0,{r1,r3}
adr r0,maxpos
ldr r5,perm
ldr r0,=almacen
mov r1,#0
strb r5,[r0,r1]
strh r5,[r0,r1]
str r5,[r0,r1]
stm r0,{r0-r7}
adr r0, maxpos
stm r0,{r0-r7}
stm r0,{r0-r1}
stm r0,{r0-r2}
stm r0,{r0-r3}
stm r0,{r0-r4}
stm r0,{r0-r7}
ldr r0,maxpos
ldr r1,maxneg
sub r0,r0,r0
ldr r0,maxpos
sbc r0,r0
add r4,r4@para poner el carry a cero.
ldr r0,maxpos
sbc r0,r0
ldr r2,alt
lsr r0,#7
lsr r2,#1
lsr r2,#1
lsr r2,#1
lsr r2,#1
lsr r2,#1
lsr r2,#1

ldr r0,maxpos
lsl r0,#7
asr r1,#2
asr r1,#2

ldr r3,perm
rev r3,r3
rev16 r3,r3
revsh r3,r3
sxtb r3,r3
sxth r3,r3
sxtb r0,r0
sxth r0,r0
uxth r0,r0
uxtb r0,r0

ldr r1,alt
mov r4,#4
ror r1,r4
sub r4,#3
ror r1,r4
ror r0,r4
ror r2,r4
orr r2,r4
ror r2,r4
asr r2,r4
mov r4,#7
asr r2,r4
mov r4,#1
lsl r2,r4
lsr r2,r4

add sp,#40
add sp,#-40
sub sp,#40

neg r7,r7
ldr r0,maxpos
ldr r1,maxneg
mov r7,#0
cmp r7,r1
cmn r0,r0
cmn r0,r1
cmp r0,r0

neg r2,r0
sub r2,r7,r0
add r2,r7,r2
neg r3,r1
sub r7,r0,r1
add r7,r0,r7
sub r7,r7,r7
cmp r0,r0
add r7,#2

sub r7,r0,r0
sub r7,r7,r7
cmp r0,r0
add r7,#4

mul r7,r0

mvn r7,r7
mvn r7,r7
mvn r7,r7
sub  r6,r0,r7
add r6,r0,r7

adc r0,r1
adc r1,r7
add r0,r0,r0
adc r0,r1

add r0,#2
add r2,r0,r0
sbc r1,r0
ldr r1,maxneg
add r2,r0,r0
sub r1,#1
add r2,r0,r0

add r1,r1,#2
sub r1,r1,#2
add r0,r0,#2
add r0,r1,r0
sub r2,r2,r2
sub r2,r1,r2
add r3,r2,r2
mvn r2,r2
add r3,r2,r2
@bvs here
add r2,r2,#-1
add r2,r2,#-1
here: ldr r3, maxpos
.align 2
maxpos: .word 0x7FFFFFFF
maxneg: .word 0x80000000
alt: .word 0xAAAAAAAA
perm: .word 0x01FF20AA

.data
almacen: .word 0