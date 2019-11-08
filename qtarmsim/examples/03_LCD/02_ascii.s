@
@ This program:
@  + Fills the first 128 bytes of the data memory with values
@    from 0 to 127.
@  + Prints the string that starts at byte 0x20 in the LCD
@
@ Hint: Run this program, open the 'Memory Dump' panel and observe
@       the ASCII chars that correspond to the numbers from 0 to
@       127 (only the printable ones are displayed)
@

	.data
ascii:	.space 128 @ Reserves 128 bytes
null:	.byte 0

	.text
main:	ldr r0, =ascii
	mov r1, #0
loop:	strb r1, [r0, r1]
	add r1, #1
	cmp r1, #127
	ble loop

	mov r0, #0
	mov r1, #1
	ldr r2, =ascii
	add r2, #0x20
	bl printString	@ printString(0, 1, ascii+0x20)
end:	wfi
