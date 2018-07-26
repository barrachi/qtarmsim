@
@ This program:
@ + stores the floating point numbers given by the strings in
@     'strf1' and 'strf2' into the variables 'f1' and 'f2',
@ + multiplies the floating point numbers in 'f1' and 'f2',
@ + converts the result to a string,
@ + and shows it on the LCD Display.

	.data
f1:	.space	4
f2:	.space	4
res:	.space	100
strf1:	.asciz	"6.234e5"
strf2:	.asciz	"10"

	.text
main:	ldr	r0, =f1
	ldr	r1, =strf1
	mov	r2, #0
	bl	qfp_str2float	@ Calls qfp_str2float(f1, strf1, 0)
	ldr	r0, =f2
	ldr	r1, =strf2
	mov	r2, #0
	bl	qfp_str2float	@ Calls qfp_str2float(f2, strf2, 0)
	ldr	r7, =f1
	ldr	r0, [r7]
	ldr	r1, [r7, #4]
	bl	qfp_fmul		@ Calls qfp_fmul(f1, f2)
	ldr	r1, =res
	mov	r2, #0
	bl 	qfp_float2str	@ Calls qfp_float2str(f1*f2, res, 0)
	mov	r0, #0
	mov	r1, #0
	ldr	r2, =res
	bl	printString	@ Calls printString(0, 0, res)
end:	wfi
