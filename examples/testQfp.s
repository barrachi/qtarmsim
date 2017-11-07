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
	bl	qfp_str2float
	ldr	r0, =f2
	ldr	r1, =strf2
	mov	r2, #0
	bl	qfp_str2float
	ldr	r7, =f1
	ldr	r0, [r7]
	ldr	r1, [r7, #4]
	bl	qfp_fmul
	ldr	r1, =res
	mov	r2, #0
	bl 	qfp_float2str
	ldr	r2, =res
	mov	r1, #0
	mov	r0, #0
	bl	printString
	wfi
	