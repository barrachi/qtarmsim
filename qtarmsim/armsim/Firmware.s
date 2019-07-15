	.equ	display, 0x20080000		@ Origen de la memoria del display
	.equ	fil, 6					@ Líneas del display
	.equ	col, 40					@ Caracteres por linea

/* Simbolos exportados */
	.global sqrt
	.global sdivide
	.global divide
	.global printString
	.global printUInt
	.global printInt
	.global printWord
	.global printHalf
	.global printByte
	.global printFloat
	.global printf
	.global fill
	.global cls
	.global cor2dir
	.global dir2cor

	.text
	
/********************************************************/	
/* sqrt(unsigned int val)                               */
/********************************************************/
/* Devuelve la parte entera de la raíz cuadrada de un   */
/* entero sin signo. Sigue el algoritmo binario que la  */
/* calcula bit a bit. (Wikipedia, versión en inglés).   */
/* Entrada:                                             */
/* r0: valor                                            */
/* Salida:                                              */
/* r0: raiz entera                                      */

	.balign 4	
	
sqrt:
	ldr r2, = 0x40000000			@ Base para los desplazamientos de bit
	mov r1, #0						@ Resultado, se inicia a 0
	cmp r0, r2						@ Mientras el radicando sea menor que
	bcs sqalg						@ el bit desplazado, 
buc_s:
	lsr r2, r2, #2					@ desplazamos a la derecha de 2 en 2 bits
	cmp r0, r2
	bcc   buc_s
sqalg:
    tst r2, r2						@ Si el bit desplazado llega a 0 se acaba
	beq	fin
buc_s2:
	add r3, r1, r2					@ Se compara el radicando con el resultado
	cmp r0, r3						@ parcial más el bit
	bcc else						@ Si es mayor se le resta tal suma
	sub r0, r0, r3					@ y se actualiza el resultado como
	lsr r1, r1, #1					@ como res = (res >> 1) + bit
	add r1, r1, r2
	b   finsi
else:
    lsr r1, r1, #1					@ Si no, se desplaza el resultado
finsi:
    lsr r2, r2, #2					@ Desplazamos el bit hasta que llegue a 0
	bne buc_s2
fin:
    mov r0, r1						@ Se pone el resultado en r0 y se termina
	mov pc, lr

/********************************************************/	
/* sdivide(int dividendo, int divisor) 					*/
/********************************************************/
/* Realiza una division con signo.                      */
/* Devuelve el resto en r1 y el cociente en r0.         */
/* Si el divisor es 0 devuelve 0x7FFFFFFF en ambos.     */
/* Utiliza la divión entera por lo que el resto tiene   */
/* signo del divisor.									*/
/* Entrada:                                             */
/* r0: dividendo                                        */
/* r1: divisor                                          */
/* Salida:                                              */
/* r0: cociente                                         */
/* r1: resto                                            */

	.balign 4
	
sdivide:
	push {r4-r5, lr}
	cmp	r1, #0					@ Si el divisor es 0 damos error
	bne	s_hazdiv
s_error:
	sub	r1, r1, #1				@ para ello ponemos resto y cociente
	lsr	r1, r1, #1				@ al mayor valor positivo 0x7FFFFFFF
	mov	r0, r1					@ y salimos
	bne	s_final
s_hazdiv:
	mov r4, #0					@ Ponemos a 0 las marcas de negativo
	mov r5, #0
	tst	r1, r1					@ Si el divisor es negativo 
	bpl	s_dos					@ se marca en r5 y se le cambia el signo
	mov	r5, #1
	neg	r1, r1
s_dos:							@ Si el dividendo es negativo
	tst	r0, r0					@ se marca en r4 y se le cambia el signo
	bpl	s_call
	mov	r4, #1
	neg	r0, r0
s_call:							
	bl	divide					@ Se dividen los valores positivos
	cmp	r5, r4					@ Si los signos de dividendo y divisor son distintos
	beq	s_resto
	neg	r0, r0					@ se cambia el signo al cociente
s_resto:
	cmp	r4, #1					@ Si el cociente es negativo
	bne	s_final
	neg	r1, r1					@ se cambia el signo al resto
s_final:
	pop	{r4-r5, pc}				@ Y se vuelve


/********************************************************/	
/* divide(unsigned int dividendo, unsigned int divisor) */
/********************************************************/
/* Realiza una division sin signo.                      */
/* Devuelve el resto en r1 y el cociente en r0.         */
/* Si el divisor es 0 devuelve 0xFFFFFFFF en ambos.     */
/* Entrada:                                             */
/* r0: dividendo                                        */
/* r1: divisor                                          */
/* Salida:                                              */
/* r0: cociente                                         */
/* r1: resto                                            */

	.balign 4

divide:
	mov	r2, #0		@ En r2 tenemos el contador de desplazamientos
	orr	r1, r1		@ Vemos si el divisor es 0
	bne	a_hazdiv	@ y en caso afirmativo
	sub	r0, r2, #1	@ ponemos 0xFFFFFFFF (-1)
	mov	r1, r0	    	@ en cociente y resto
	b	a_final
a_hazdiv:			@ Empezamos a dividir
	mov	r3, #0		@ r3 es el cociente parcial
	and	r1, r1		@ Si el msb del cociente es 1
	bmi	a_itera		@ evitamos los desplazamientos
a_compara:
	cmp	r0, r1		@ Comparamos el dividendo con el divisor
	bcc	a_itera		@ desplazado, y seguimos desplazando hasta
	add	r2, r2, #1	@ que sea menor. Obtenemos en r2 el numero 
	lsl	r1, r1, #1	@ de bits del cociente
	bpl	a_compara	@ Evitamos el desbordamiento
a_itera:
	lsl	r3, r3, #1	@ Desplazamos el cociente
	cmp	r0, r1		@ Vemos si cabe a 1
	bcc	a_finresta	@ Si no cabe vamos a finresta
	add	r3, r3, #1	@ si cabe sumamos 1 en el cociente
	sub r0, r0, r1	@ y restamos
a_finresta:
	lsr	r1, r1, #1	@ Desplazamos el dividendo
	sub	r2, #1		@ Seguimos si quedan iteraciones
	bpl	a_itera
a_findiv:
	mov	r1, r0		@ El resto esta en r0 
	mov	r0, r3		@ y el cociente en r3
a_final:
	mov	pc, lr
	
/********************************************************/	
/* printString(int col, int fil, char *cad)             */
/********************************************************/
/* Imprime la cadena dada en el display a partir de la  */
/* coordenada dada. No realiza verificaciones.          */
/*                                                      */
/* Entrada:                                             */
/* r0: Columna (0...col - 1)                            */
/* r1: Fila (0...fil - 1)                               */
/* r2: Cadena ASCIIZ a imprimir                         */
/*                                                      */
/* Salida:                                              */
/* r0: Numero de caracteres impresos (strlen)           */

	.balign 4

printString:
      ldr	r3, =col		@ Se calcula en r0 la dirección de inicio según las
	  mul	r1, r1, r3		@ coordenadas, multiplicando el numero de fila
	  add	r1, r1, r0		@ por las colúmnas y sumando el de columna.
      ldr	r0, =display	@ Al resultado se suma la dirección base del display.
	  add	r0, r0, r1
	  mov	r3, #0			@ Se pone a 0 el contador de caracteres
buc_1:
	  ldrb	r1, [r2]		@ Se lee un caracter y si es 0 
	  cmp	r1, #0			@ se termina
	  beq	end_1			
      strb 	r1, [r0]		@ Si no, se deja en memoria y se incrementan
	  add	r3, r3, #1		@ el contador de caracteres
	  add	r0, r0, #1		@ la dirección en el display
	  add	r2, r2, #1		@ y la dirección en la cadena en memoria
	  b		buc_1			@ y se vuelve al bucle
end_1:
	  mov	r0, r3			@ El número de caracteres se pone en r0
	  mov pc, lr			@ y se termina
			
			
/********************************************************/	
/* printUInt(int col, int fil, unsigned int val)        */
/********************************************************/
/* Imprime en el display a partir de las coordenadas    */
/* dadas el entero sin signo en decimal. No realiza     */
/* verificaciones.                                      */
/*                                                      */
/* Entrada:                                             */
/* r0: Columna (0...col - 1)                            */
/* r1: Fila (0...fil - 1)                               */
/* r2: Entero a imprimir                         		*/
/*                                                      */
/* Salida:                                              */
/* r0: Numero de caracteres impresos          			*/

	.balign 4

printUInt:
	  push {r5-r7, lr}		@ Se va a crear en la pila una cadena con el número
	  mov	r5, sp			@ en decimal, por eso ponemos r5 apuntando a 
	  sub	r5, r5, #4		@ SP + 4 y reservamos espacio para 12 caracteres.
	  sub	sp, #12
	  mov	r6, r0			@ Se guardan las coordenadas en r6 y r7
	  mov	r7, r1
	  mov	r0, r2			@ y se copia el número en r0
	  mov	r1, #0			@ Ponemos el final de cadena en r5. Al ir dividiendo entre 
	  strb	r1, [r5]		@ 10 la cadena se va a crear de la cifra menos significativa
buc_2:						@ hacia la más, es decir de arriba a abajo en memoria
	  sub	r5, r5, #1		@ Se decrementa r5 para el siguiente caracter
      mov	r1, #10			@ y se divide el número entre 10
	  bl	divide
	  add	r1, #48			@ Se pasa el resto a carácter 
	  strb	r1, [r5]		@ y se escribe en la cadena
	  cmp	r0, #0			@ Si el cociente es 0 se ha terminado
	  bne	buc_2			@ en otro caso se continúa
	  mov	r0, r6			@ Recuperamos las coordenadas
	  mov	r1, r7
	  mov	r2, r5			@ y ponemos en r2 la dirección de la cadena
      bl	printString		@ Se imprime y pone en r0 su longitud
	  add sp, #12			@ Se ajusta la pila 
	  pop 	{r5-r7, pc}		@ y se termina.
	  
	  
/********************************************************/	
/* printInt(int col, int fil, int val)                  */
/********************************************************/
/* Imprime en el display a partir de las coordenadas    */
/* dadas el entero con signo en decimal. No realiza     */
/* verificaciones.                                      */
/*                                                      */
/* Entrada:                                             */
/* r0: Columna (0...col - 1)                            */
/* r1: Fila (0...fil - 1)                               */
/* r2: Entero a imprimir                         		*/
/*                                                      */
/* Salida:                                              */
/* r0: Numero de caracteres impresos                    */

	.balign 4

printInt:
	  push {r4-r7, lr}		@ Se va a crear en la pila una cadena con el número
	  mov	r5, sp			@ en decimal, por eso ponemos r5 apuntando a 
	  sub	r5, r5, #4		@ SP + 4 y reservamos espacio para 12 caracteres.
	  sub	sp, #12
	  mov	r6, r0			@ Se guardan las coordenadas en r6 y r7
	  mov	r7, r1
	  mov	r0, r2			@ y se copia el número en r0
	  mov	r4, #0			@ r4 guardará 1 si es negativo
	  and	r2, r2			@ Lo verificamos mirando su msb
	  bpl	mas_3
	  neg	r0, r2			@ si es negativo le cambiamos el signo
	  add	r4, r4, #1		@ y lo marcamos en r4
mas_3:
	  mov	r1, #0			@ Ponemos el final de cadena en r5. Al ir dividiendo entre 
	  strb	r1, [r5]		@ 10 la cadena se va a crear de la cifra menos significativa
buc_3:						@ hacia la más, es decir de arriba a abajo en memoria
	  sub	r5, r5, #1		@ Se decrementa r5 para el siguiente caracter
      mov	r1, #10			@ y se divide el número entre 10
	  bl	divide
	  add	r1, #48			@ Se pasa el resto a carácter 
	  strb	r1, [r5]		@ y se escribe en la cadena
	  cmp	r0, #0			@ Si el cociente es 0 se ha terminado
	  bne	buc_3			@ en otro caso se continúa
	  cmp	r4, #0			@ Si el número era negativo
	  beq	positivo
	  mov r4, #'-			@ Se añade el signo menos al principio
	  sub	r5, r5, #1
	  strb	r4, [r5]
positivo:
	  mov	r0, r6			@ Recuperamos las coordenadas
	  mov	r1, r7
	  mov	r2, r5			@ y ponemos en r2 la dirección de la cadena
      bl	printString		@ Se imprime y pone en r0 su longitud
	  add sp, #12			@ Se ajusta la pila 
	  pop 	{r4-r7, pc}		@ y se termina.
	  
	  
/********************************************************/	
/* printWord(int col, int fil, unsigned int val)        */
/********************************************************/
/* Imprime en el display a partir de las coordenadas    */
/* dadas el entero en hexadecimal. Siempre imprime 8    */
/* caracteres hexadecimales. No realiza verificaciones. */
/*                                                      */
/* Entrada:                                             */
/* r0: Columna (0...col - 1)                            */
/* r1: Fila (0...fil - 1)                               */
/* r2: Entero a imprimir                         		*/
/*                                                      */
/* Salida:                                              */
/* ---                                                  */
	.balign 4

printWord:	
	mov		r3, #8			@ r3 guarda los caracteres a imprimir
	b		printHex		@ se imprimen en printHex
	
	
/********************************************************/
/* printHalf(int col, int fil, unsigned int val)        */
/********************************************************/
/* Imprime en el display a partir de las coordenadas    */
/* dadas el half en hexadecimal. Siempre imprime 4      */
/* caracteres hexadecimales. No realiza verificaciones. */
/*                                                      */
/* Entrada:                                             */
/* r0: Columna (0...col - 1)                            */
/* r1: Fila (0...fil - 1)                               */
/* r2: Entero a imprimir                         		*/
/*                                                      */
/* Salida:                                              */
/* ---                                                  */

	.balign 4

printHalf:	
	mov		r3, #4			@ r3 guarda los caracteres a imprimir
	b		printHex		@ se imprimen en printHex


/********************************************************/
/* printByte(int col, int fil, unsigned int val)        */
/********************************************************/
/* Imprime en el display a partir de las coordenadas    */
/* dadas el byte en hexadecimal.Siempre imprime 2       */
/* caracteres hexadecimales. No realiza verificaciones. */
/*                                                      */
/* Entrada:                                             */
/* r0: Columna (0...col - 1)                            */
/* r1: Fila (0...fil - 1)                               */
/* r2: Entero a imprimir                         		*/
/*                                                      */
/* Salida:                                              */
/* ---                                                  */

	.balign 4
	
printByte:
	  mov		r3, #2		@ r3 guarda los caracteres a imprimir
	
printHex:					@ Comienzo del código de impresion
	  push	{r4-r5, lr}
      ldr	r4, =col		@ Se calcula la dirección del caracter
	  mul	r1, r1, r4		@ menos significativo: se multiplica la fila por
	  add	r1, r1, r0		@ el numero de columnas, se suma la columna, 
      ldr	r0, =display	@ la dirección del display
	  add	r0, r0, r1
	  add	r0, r0, r3		@ y el número de caracteres
	  mov	r5, #0x0f		@ En r5 se guarda la máscara para dejar 4 bits -una cifra hex-.
buc_4:
	  mov   r1, r2			@ Se copia en r1 el número actual
      and	r1, r1, r5		@ se deja el nibble -4 bits- bajo
	  add	r1, #'0			@ se pasa a caracter
	  cmp	r1, #'9 + 1		@ Si es menor o igual que '9 ya está
	  bcc	nosuma
	  add	r1, #'A - '9 - 1	@ si no, lo pasamos a la letra correspondiente
nosuma:
	  sub	r0, r0, #1		@ Decrementamos la posición del display
	  lsr	r2, r2, #4		@ Desplazamos 4 bits el número -dividimos entre 16-
      strb 	r1, [r0]		@ dejamos el caracter en el display
	  sub	r3, r3, #1		@ y decrementamos la cuenta de caracteres a escribir.
	  bne	buc_4			@ Si no es 0, seguimos
end_4:
	  pop	{r4-r5, pc}		@ Termina la función
	  
	  
/********************************************************/
/* printFloat(int col, int fil, float val, int format)  */
/********************************************************/
/* Imprime en el display a partir de las coordenadas    */
/* dadas el entero sin signo en decimal. No realiza     */
/* verificaciones.                                      */
/*                                                      */
/* Entrada:                                             */
/* r0: Columna (0...col - 1)                            */
/* r1: Fila (0...fil - 1)                               */
/* r2: Real a imprimir                                  */
/* r3: Formato (como qfp_float2str)                     */
/*                                                      */
/* Salida:                                              */
/* r0: Numero de caracteres impresos          	        */

	.equ	maxsize, 20

	.balign 4

printFloat:
	  push {r5-r7, lr}		@ Se va a crear en la pila una cadena con el número
	  sub	sp, #maxsize
	  mov	r5, sp			@ en decimal, por eso ponemos r5 apuntando al espacio en la pila
	  mov	r6, r0			@ Se guardan las coordenadas en r6 y r7
	  mov	r7, r1
	  mov	r0, r2			@ y se copia el número en r0
	  mov	r1, r5			@ y la cadena en r1
	  mov   r2, r3			@ el formato en r2
	  bl	qfp_float2str	@ y se llama a la función de convertir en cadena
	  mov	r0, r6			@ Recuperamos las coordenadas
	  mov	r1, r7
	  mov	r2, r5			@ y ponemos en r2 la dirección de la cadena
      bl	printString		@ Se imprime y pone en r0 su longitud
	  add sp, #maxsize		@ Se ajusta la pila 
	  pop 	{r5-r7, pc}		@ y se termina.


/********************************************************/
/* printf(int col, int fil, char *cad, ...)             */
/********************************************************/
/* Imprime en el display a partir de las coordenadas    */
/* dadas una cadena con idicadores de formato, que se   */
/* sustituyen según se indica a continuación. Se sigue  */
/* de forma simplificada el convenio de pritnf en C     */
/* % Es el carácter indicador de formato. El tipo de    */
/* formato se indica con el carácter que le sigue.      */
/* %i o %d indican un entero con signo.                 */
/* %u un entero sin signo.                              */
/* %x o %w un entero (word) en hexadecimal.             */
/* %h un entero de 16 bits (half) en hexadecimal.       */
/* %b un byte en hexadecimal                            */
/* %c un carácter                                       */
/* %f un número en coma flotante (formato básico).      */
/* %s Una cadena de texto.                              */
/*                                                      */
/* Cada uno de los elementos de formato que aparece en  */
/* la cadena se corresponde con un valor, siempre de 32 */
/* bits aunque no sean todos significativos, que se ha  */
/* pasado como parámetro, en el mismo orden.            */
/*                                                      */
/* Además de los elementos de formato indicados, se     */
/* pueden utilizar los caracteres \n (CR) para indicar  */
/* un salto a la siguiente línea y \t (TAB) que fuerza  */
/* que el siguiente caracter esté en una columna        */
/* múltiplo de 5, escribiendo espacios.                 */
/* Para imprimir el carácter % se debe poner dos veces, */
/* es decir %%                                          */
/* En caso de encontrar en la cadena el signo % y tras  */
/* él un indicador de formato desconocido, se imprimirá */
/* un interrogante ? en lugar del signo %.              */
/*                                                      */
/* La función de vuelve el número de posiciones del     */
/* display utilizadas. Es decir, el número de           */
/* caracteres impresos teniendo en cuenta que \t suma 8 */
/* y un salto de línea suma los restantes hasta el      */
/* final de la línea en curso.                          */
/*                                                      */
/* Entrada:                                             */
/* r0: Columna (0...col - 1)                            */
/* r1: Fila (0...fil - 1)                               */
/* r2: Cadena con texto e indicadores de formato        */
/* r3 - pila: Valores según formato (en orden)          */
/*                                                      */
/* Salida:                                              */
/* r0: Numero de caracteres ocupados.                   */


	.equ	param, 20		@ Desplazamiento desde SP a r3 en la pila tras apilar
	.equ	tabesp, 5		@ Numero de espacios del tabulador
	.equ	FORMATO, '%'	@ Caracter de formato
	.equ	TAB, '\t'		@ Tabulador
	.equ	LF, '\n'		@ Salto de línea
	.equ	CHERR, '?'		@ Carácter para indicar formato erróneo

	.balign 4

printf:	
	push {r3}				@ Todos los parametros en la pila
	push {r4-r7}			@ Se apila lr más abajo en la pila, al final se
	push {lr}				@ arregla
	mov r7, sp				@ r7 recorre los parámetros en la pila
	add r7, #param
	mov r5, r2				@ r5 contiene la dirección de la cadena con formato
	bl cor2dir				@ r0 y r1 ya tienen columna y fila
	mov r4, r0				@ r4 contiene la dirección del display
	mov r6, r0				@ y r6 también para devolver el num. de caracteres usados
bucle:	
	ldrb r0, [r5]			@ Se lee el caracter de la cadena con formato
	cmp r0, #0				@ Si es final de cadena se ha terminado
	beq p_fin
sigue:	
	add r5, r5, #1			@ Se incrementa ya el puntero a la cadena
	cmp r0, #FORMATO		@ Más probable: se evalua primero y se salta al
	beq formato				@ código para dar formato
	cmp r0, #LF				@ Si no es LF se mira el siguiente caso
	bne s_tab
	mov r0, r4				@ Esto funciona porque la direccion base es multiplo de col
	mov r1, #col
	bl divide				@ Al dividir se queda en una direccion de inicio de fila
	add r4, r0, #1			@ Se suma 1 y se multiplica por col
	mov r1, #col			@ con lo que se pasa al pincipio de la siguiente fila
	mul r4, r1				@ Se restaura el valor en el puntero al display r4
	b bucle					@ y se sigue con la cadena
s_tab:	
	cmp r0, #TAB			@ Si no es TAB es un caracter normal
	bne s_normal
	mov r0, r4				@ Dividimos la dirección entre el valor del tab
	mov r1, #tabesp			@ que ha de ser divisor entero del tamaño de linea
	bl divide
	mov r0, #tabesp			@ Preparamos el contador,que es el tamaño del tab
	sub r1, r0, r1      	@ menos el resto
	mov r0, #' '			@ r0 es el caracter espacio
esc_tab:
	strb r0, [r4]			@ Se imprimen tantos espacios
	add r4, r4, #1			@ como indique el contador
	sub r1, r1, #1
	bne esc_tab
	b bucle					@ Se sigue con la cadena
s_normal:
	strb r0, [r4]			@ Si es un caracter normal se imprime
	add r4, r4, #1			@ y se incrementa la posicion del display
	b bucle
formato:
	mov r0, r4				@ Optimista: se supone que se va a imprimir algo que requiere
	bl dir2cor				@ convertir la dirección de display en coordenadas.
	ldr r2, [r7]			@ Se consume el parametro en r2 y las coordenadas
	add r7, r7, #4			@ van a r0 y r1. Reduce el tamaño del código
	ldrb r3, [r5]			@ Se lee el caracter que indica el formato
	add r5, r5, #1			@ y se incrementa el puntero a la cadena
	cmp r3, #'i'			@ %i %d - Imprime entero con signo
	beq s_int
	cmp r3, #'d'
	bne s_noint
s_int:	
	bl printInt				@ r2 ya tiene el parámetro y r0 y r1 las coordenadas
	add r4, r4, r0			@ Añade los caracteres impresos a la cuenta en r4
	b bucle					@ y vuelve al bucle
s_noint:
	cmp r3, #'u'			@ %u - Imprime entero sin signo
	bne s_nouint			
	bl printUInt
	add r4, r4, r0
	b bucle
s_nouint:
	cmp r3, #'s'			@ %s - Imprime cadena
	bne s_nostring
	bl printString
	add r4, r4, r0
	b bucle
s_nostring:
	cmp r3, #'w'			@ %w %x - Imprime word en hexadecimal
	beq s_word
	cmp r3, #'x'
	bne s_noword
s_word:	
	bl printWord
	add r4, #8
	b bucle
s_noword:
	cmp r3, #'h'			@ %h - Imprime half hexadecimal
	bne s_nohalf
	bl printHalf
	add r4, #4
	b bucle
s_nohalf:
	cmp r3, #'b'			@ %b - Imprime byte hexadecimal
	bne s_nobyte
	bl printByte
	add r4, #4
	b bucle
s_nobyte:
	cmp r3, #'f'			@ %f - Imprime float en modo básico
	bne s_nofloat
	mov r3, #0				@ Formato básico en r3
	bl printFloat
	add r4, r4, r0
	b bucle
s_nofloat:
	cmp r3, #'c'			@ %c - Imprime caracter
	bne s_nochar
	strb r2, [r4]			@ Se escribe el caracter en el display y se
	add r4, r4, #1			@ incrementa el puntero
	b bucle
s_nochar:
	sub r7, r7, #4			@ No se consume el parámetro => se restaura r7
	cmp r3, #FORMATO		@ Si es % todo va bien
	bne s_p_error
	strb r3, [r4]			@ Si es % se imprime
	add r4, r4, #1
	b bucle
s_p_error:
	mov r1, #CHERR			@ Si no se imprime CHERR indicando el error
	strb r1, [r4]
	add r4, r4, #1
	cmp r3, #0				@ y si no es el final de la cadena
	beq p_fin
	strb r3, [r4]           @ se imprime el caracter erróneo original
	add r4, r4, #1
	b bucle
p_fin:	
	sub r0, r4, r6			@ Se calcula el valor a devolver, se arregla la pila
	pop {r3}				@ y se lleva lr a su sitio
	str r3, [sp, #(param - 4)]
	pop {r4-r7, pc}

	
/********************************************************/	
/* fill(char val)                                       */
/********************************************************/
/* Rellena el display con el valor val.                 */
/*                                                      */
/* Entrada:                                             */
/* r0: Valor a rellenar (8 lsb)                         */
/*                                                      */
/* Salida:                                              */
/* ---                                                  */

	.balign	4
	
fill:
	mov r1, #0xFF			@ Dejamos en r2 el carácter de r0
	and	r0, r1				@ dejando el resto del registro a 0
	mov	r2, r0				@ con el and anterior
	lsl r0, r0, #8			@ Dejamos espacio para otro caracter igual
	orr	r2, r0				@ que añadimos con or
	lsl r0, r0, #8			@ Repetimos tres veces para dejar el 
	orr r2, r0				@ caracter original en los 4 bytes
	lsl r0, r0, #8			@ de r2
	orr r2, r0
	b	limpia				@ saltamos a escribir los caracteres

	
/********************************************************/	
/* cls()                                                */
/********************************************************/
/* Limpia el display                                    */
/*                                                      */
/* Entrada:                                             */
/* ---                                           	    */
/*                                                      */
/* Salida:                                              */
/* ---                                                  */

	.balign	4
	
cls:
	ldr	r2, =0x20202020		@ Un entero con 4 caracteres espacio -blancos-
limpia:
    ldr	r0, =display		@ r0 apunta a la dirección del display
	ldr	r1, =(fil*col)/4	@ en r1 el número de caracteres entre 4
buc_5:
	str	r2, [r0]			@ Se escribe entero a entero
	add	r0, r0, #4			@ incrementando en 4 la dirección
	sub	r1, r1, #1			@ decrementando en 1 el número de enteros que faltan
	bne	buc_5				@ Terminamos al llegar a 0
	mov pc, lr				@ y volvemos
	
	
/********************************************************/
/* cor2dir(int col, int fil)                            */
/********************************************************/
/* Devuelve la dirección de memoria del display que     */
/* corresponde a las coordenadas dadas. No realiza      */
/* verificaciones.                                      */
/*                                                      */
/* Entrada:                                             */
/* r0: Columna (0...col - 1)                            */
/* r1: Fila (0...fil - 1)                               */
/*                                                      */
/* Salida:                                              */
/* r0: Dirección de memoria correspondiente             */

	.balign 4

cor2dir:
	mov r2, #col
	mul r1, r2				@ Multiplica el índice de fila por el número de columnas
	add r1, r1, r0			@ le suma el índice de columna para obtener el desplazamiento
	ldr r0, =display
	add r0, r0, r1			@ que se suma a la dirección base del display
	mov pc, lr				@ Termina


/********************************************************/
/* dir2cor(char *dir)                                   */
/********************************************************/
/* Devuelve las coordenadas asociadas a una dirección   */
/* de memoria del display. No realiza verificaciones.   */
/*                                                      */
/* Entrada:                                             */
/* r0: Dirección de memoria                             */
/*                                                      */
/* Salida:                                              */
/* r0: Columna (0...col - 1)                            */
/* r1: Fila (0...fil - 1)                               */

	.balign 4

dir2cor:
	push {lr}
	ldr r1, =display
	sub r0, r0, r1			@ Se resta la dirección base del display
	mov r1, #col			@ y se divide entre el número de columnas.
	bl divide				@ El resto es la columna y el cociente la fila
	mov r2, r1				@ Se permutan usando r2 como auxiliar
	mov r1, r0
	mov r0, r2
	pop {pc}				@ Y termina
	
	
/********************************************************/
/*                FINAL DE LAS FUNCIONES                */
/********************************************************/

	.ltorg		@ Forzamos constantes

			
	.include "qfplib-20161124/qfplib.s"
	.include "qfplib-20161124/qfpio.s"

	.end
