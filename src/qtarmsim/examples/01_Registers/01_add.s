@
@ This program:
@  + loads two numbers, 5 and 4, in the registers r0 and r1, respectivelly,
@  + adds the contents of these registers, and
@  + loads the result in the register r2.
@

	.text

main:	mov r0, #5	@ Load register r0 with the value 5
	mov r1, #4	@ Load register r1 with the value 4
	add r2, r1, r0	@ Add r0 and r1 and store in r2

stop:	wfi		@ End of program
