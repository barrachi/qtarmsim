	.equ	mascara, 0x55555555	@ En binario 010101...0101
	.equ	cero, '0			@ ASCII del 0, por probar

	.data
cosas:	.word	0x12345600		@ Numero a manipular
cadin:	.space	33				@ Cadenas en binario
	.align
cadout:	.space	33

.section	.text

main:
	ldr 	r2, =cosas			@ Ponemos el dato desde cosas
	ldr		r0, [r2]			@ en r0
	ldr		r1, = cadin			@ Lo convertimos a ASCII en binario
	bl		itobin				@ a partir de cadin
	ldr		r0, [r2]			@ Recuperamos el dato
	bl		prmbits				@ y permutamos los bits pares e impares
	ldr		r1, = cadout		@ Convertimos a ASCII el resultado
	bl		itobin				@ a partir de cadout
stop:  wfi						@ Hecho

# Funcion itobin
# Devuelve una cadena ASCIIZ con el valor de una palabra en binario
# Parametros: r0 - Palabra
#             r1 - Dir. inicio de la cadena
# Devuelve: -
itobin:
	push	{r3-r4, lr}			@ Usamos r3 y r4		
	mov		r4, #1				@ r4 recorre los bits empezando por el
	lsl		r4, r4, #31			@ msb
lazo:
	mov		r3, #cero			@ r3 guarda el caracter 0
	tst		r0, r4				@ Si el bit está a 0
	beq		noinc				@ no incrementamos r3
	add		r3, r3, #1
noinc:
	strb	r3, [r1]			@ Guardamos el caracter e
	add		r1, r1, #1			@ incrementamos la posicion en la cadena
	lsr		r4, r4, #1			@ Desplazamos la máscara
	bne		lazo				@ hasta que sea 0 -32 veces
	strb	r4,	[r1]			@ Ponemos el \0 final de cadena
	pop		{r3-r4, pc}			@ Hecho. Volvemos
	
# Funcion prmbits
# Permuta los bits pares e impares de una palabra
# Parametros: r0 - Palabra a invertir
# Devuelve: r0 - Palabra invertida
prmbits:
	push	{r1-r2, lr}			@ r1 y r2 para trabajar
	ldr		r1, =mascara		@ Ponemos en r1 la máscara con 01 alternos
	lsr		r2, r0, #1			@ Ponemos en r2 los bits de r0 desplazados par -> impar
	and		r0, r1				@ Dejamos en r0 los impares
	lsl		r0, r0, #1			@ y los deplazamos impar -> par
	and		r2, r1				@ Quitamos los pares de r2
	orr		r0, r2				@ y los juntamos permutados con el or
	pop		{r1-r2, pc}			@ Hecho. Volvemos
	.end
