@
@ QtARMSim example (http://lorca.act.uji.es/projects/qtarmism/
@
	.data
a:	.word 0x20
b:	.word 0x30
res:	.space 4

	.text

main:	ldr r1, =a	@ r1 <- a
	ldr r1, [r1]	@ r1 <- [a]
	ldr r2, =b	@ r0 <- b
	ldr r2, [r2]	@ r2 <- [b]
	add r3, r1, r2	@ r3 <- r1 + r2
	ldr r0, =res	@ r0 <- res
	str r3, [r0]	@ [r0] <- r1 + r2

end:	wfi
