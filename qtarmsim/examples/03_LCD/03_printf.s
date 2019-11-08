@
@ This program shows in the LCD Display the strings stored in the variables 's1' and 's2'
@

	.data
@
s1:	.asciz "The value of %s is %f,\n%d in hexadecimal is 0x%w,\nand '%c' is a character.\n(PERCENT:%% TAB:[\t] UNRECOGNIZED:%j.)"
s2:	.asciz "LCD positions used: %d."
pi:	.asciz "PI"
	.balign 4
valpi:	.float 3.1415926535897932384626433832795028841971693993751058209749445923078164062
val:	.word 65538

	.text
main:	sub sp, sp, #16	
	ldr r7, =valpi
	mov r0, #'*'
	str r0, [sp, #12]
	ldr r0, [r7, #4]
	str r0, [sp, #8]
	str r0, [sp, #4]
	ldr r0, [r7]
	str r0, [sp]
	mov r0, #0
	mov r1, #0
	ldr r2, =s1
	ldr r3, =pi
	bl printf	@ Calls printf(0, 1, s1, pi, valpi, val, val, '*')

	add sp, sp, #12	@ Adjust the stack after return
	mov r3, r0	@ r3 <- LCD positions used
	mov r0, #0
	mov r1, #5
	ldr r2, =s2
	bl printf	@ Calls printf(0, 5, s2, r3)

end:	wfi		@ End of program

	.end
