@
@ This program:
@  + initialices the variables 'a' and 'b' with the numbers 5 and 4, respectivelly,
@  + loads the contents of the variables 'a' and 'b' on the registers r0 and r1, respectivelly,
@  + adds the contents of these registers, and
@  + stores the result in the variable 'c'.
@

	.data

a:	.word 5
b:	.word 4
res:	.space 4

	.text

main:	ldr r0, =a	@ r0 <- a
	ldr r0, [r0]	@ r0 <- [a]
	ldr r1, =b	@ r1 <- b
	ldr r1, [r1]	@ r1 <- [b]
	add r2, r0, r1	@ r2 <- r0 + r1
	ldr r0, =res	@ r0 <- res
	str r2, [r0]	@ [r0] <- a + b

end:	wfi		@ End of program
