@
@ This program:
@  + initialices the registers r1 to r3,
@  + pushes the registers r1 to r3 in the stack,
@  + modifies the registers r1 to r3,
@  + pops their previous values from the stack.
@

	.text
main:	mov r1, #0x01
	mov r2, #0x02
	mov r3, #0x03
	push {r1-r3}	@ Push registers r1 to r3
	mov r1, #0x11
	mov r2, #0x22
	mov r3, #0x33
	pop {r1-r3}	@ Pop registers r1 to r3

end:	wfi
