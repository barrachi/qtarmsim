@
@ This program shows in the LCD Display the strings stored in the variables 's1' and 's2'
@

	.data
@	        0123456789012345678901234567890123456789
s1:	.asciz "HELLO WORLD!"
s2:	.asciz "This is QtARMSim LCD Display!"

	.text

main:	mov r0, #0
	mov r1, #1
	ldr r2, =s1
	bl printString	@ Calls printstring(0, 1, s1)

	mov r0, #0
	mov r1, #3
	ldr r2, =s2
	bl printString	@ Calls printstring(0, 3, s2)

end:	wfi		@ End of program
