@
@ Basic loop example
@

	.text
start:	mov	r3, #0		@ Load register r3 with the value 0
	mov     r4, #5		@ Load register r4 with the value 5
loop:	add	r3, r3, #1	@ r3 <- r3 + 1
	sub	r4, r4, #1	@ r4 <- r4 - 1
	bne	loop		@ Branch if non zero
stop:	wfi			@ End of program
