	.data	
numbers:.word	34567890, -215
string:	.asciz "Prueba del display"
	

	.text
main:   ldr r7, =numbers
	ldr	r2, =string
	mov r0, #0
	mov r1, #0
	bl printString

	ldr	r2, [r7]
	mov r0, #0
	mov r1, #1
	bl printInt

	ldr	r2, [r7]
	mov r0, #20
	mov r1, #1
	bl printUInt

	ldr	r2, [r7, #4]
	mov r0, #0
	mov r1, #2
	bl printInt

	ldr	r2, [r7, #4]
	mov r0, #20
	mov r1, #2
	bl printUInt

	ldr	r2, [r7]
	mov r0, #0
	mov r1, #3
	bl printWord

	ldr	r2, [r7]
	mov r0, #20
	mov r1, #3
	bl printHalf

	ldr	r2, [r7, #4]
	mov r0, #0
	mov r1, #4
	bl printWord

	ldr	r2, [r7, #4]
	mov r0, #20
	mov r1, #4
	bl printByte

	bl cls

	mov r0, #'.
	bl fill

	mov r0, #'o
        bl fill

	mov r0, #'O
        bl fill

        mov  r0, #'o
        bl fill
	
	wfi
	
	.end