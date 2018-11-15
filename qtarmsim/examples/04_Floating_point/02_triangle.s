@
@ This program:
@  + calculates the hypotenuse and both acute angles of a right triangle given the catheti,
@  + uses many of the floating point arithmetic functions of the firmware, and
@  + defines and uses a macro to allow the use of floating point constants, similar to ldr rx, =const.
@


@ MACRO ldrf rx, fp_const_label
@ =============================
@
@ The common pseudoinstruction ldr rx, =const does not allow the use of a
@ floating point constant, so this macro comes to solve this lack.
@ To use it just write the desired constants at a suitable place in your
@ .text region -at the end of your code, between the main program and the subroutines-
@ each preceded by a label and the .float data type, aligned in a word boundary. 
@ In this example we use -see below-
@
@ m_pi:		.float 31415926535897932384626433832795028841971.693993751E-40 
@ m_180:	.float 180.0
@
@ In your code you will access the constant using the macro and its label 
@
@ ldrf r1, m_pi
@ ldrf r4, m_180
@
@ Here is the macro definition

.macro	ldrf reg:req, label:req
	ldr 	\reg, [pc, #(\label - 2 - . ) & 0xFFFFFFFC]
.endm

@ We will use r7 and the following offsets to access the variables 
.equ cA,	0
.equ cB, 	4
.equ hypo, 	8
.equ angA,	12	@ Opossed to cathetus A
.equ angB,	16	@ Opossed to cathetus B

		.data

catheti:	.float	32.0, 17.0 	@ Place here the values of the catheti. Try 4.0, 3.0
hypotenuse:	.space 4
angles:		.space 8		@ First angle A, then B.
buffer:		.space	100		@ Buffer to print FP values
tcatheti:	.asciz "Catheti (A B): "
thypo:		.asciz "Hypotenuse:    "
tangles:	.asciz "Angles (A B):  "


		.text	
		mov	r0, #0
		ldr	r7, =catheti
		ldr	r0, [r7, #cA]	@ Square first cathetus
		mov	r1, r0
		bl	qfp_fmul
		mov	r4, r0		@  and save it in r4
		ldr	r0, [r7, #cB]	@ Square the second cathetus
		mov	r1, r0
		bl	qfp_fmul	@  and save it in r0
		mov	r1, r4		
		bl	qfp_fadd	@ Add to have in r0 the square of hypotenuse
		bl	qfp_fsqrt	@  and compute the square root
		str	r0, [r7, #hypo] @ Store the hypotenuse
@
		ldr	r0, [r7, #cA]	@ Cathetus A -sine- in r0
		ldr	r1, [r7, #cB]  @ Cathetus B -cosine- in r1
		bl	qfp_fatan2	@ Angle A in radians in r0
		ldrf	r4, m_180	@ Obtain degrees by multiplying by 180 and dividing 
		mov	r1, r4		@  by pi. We could have calculated 180/PI offline and use only
		bl	qfp_fmul	@  a constant and a multiplication, but the aim is to show the
		ldrf	r1, m_pi	@  use of the ldrf macro and the arithmetic functions.
		bl	qfp_fdiv	@  So we get the angle A in degrees and store it.
		str	r0, [r7, #angA]	@ 
		ldr	r0, [r7, #cB]	@ We repeat the procedure permuting CA and CB to obtain 
		ldr	r1, [r7, #cA]	@  angle B. This way we can verify that the procedure is correct
		bl	qfp_fatan2	@  if both sum 90.
		mov	r1, r4		
		bl	qfp_fmul	
		ldrf	r1, m_pi	
		bl	qfp_fdiv	
		str	r0, [r7, #angB]	
@		
		mov	r0, #0		@ Print catheti intro at (0,0)
		mov	r1, #0
		ldr	r2, =tcatheti
		bl	printString
		add	r4, r0, #1	@ Store next position in r4
		ldr	r0, [r7, #cA]	@ Get string for cathetus A
		ldr	r1, =buffer
		mov	r2, #0
		bl 	qfp_float2str
		mov	r0, r4		@ Print its value
		mov	r1, #0
		ldr	r2, =buffer
		bl	printString
		add     r4, r0, r4	@ Store next position in r4
		add	r4, r4, #1
                ldr	r0, [r7, #cB]	@ Get string for cathetus B
		ldr	r1, =buffer
		mov	r2, #0
		bl 	qfp_float2str
		mov	r0, r4		@ Print its value
		mov	r1, #0
		ldr	r2, =buffer
		bl	printString
		
@
		mov	r0, #0		@ Print hypotenuse intro at (0,2)
		mov	r1, #2
		ldr	r2, =thypo
		bl	printString
		add	r4, r0, #1	@ Store next position in r4
		ldr	r0, [r7, #hypo]	@ Get string for hypotenuse
		ldr	r1, =buffer
		mov	r2, #0
		bl 	qfp_float2str
		mov	r0, r4		@ Print its value
		mov	r1, #2
		ldr	r2, =buffer
		bl	printString
@
		mov	r0, #0		@ Print qngles intro at (0,4)
		mov	r1, #4
		ldr	r2, =tangles
		bl	printString
		add	r4, r0, #1	@ Store next position in r4
		ldr	r0, [r7, #angA]	@ Get string for angle A
		ldr	r1, =buffer
		mov	r2, #0
		bl 	qfp_float2str
		mov	r0, r4		@ Print its value
		mov	r1, #4
		ldr	r2, =buffer
		bl	printString
		add     r4, r0, r4	@ Store next position in r4
		add	r4, r4, #1
                ldr	r0, [r7, #angB]	@ Get string for angle B
		ldr	r1, =buffer
		mov	r2, #0
		bl 	qfp_float2str
		mov	r0, r4		@ Print its value
		mov	r1, #4
		ldr	r2, =buffer
		bl	printString
@
		wfi

@ Floating point constant values. Aligned at a 4 boundary
		.balign 4
m_pi:		.float 31415926535897932384626433832795028841971.693993751E-40 
m_180:		.float 180.0

	.end
