@ programa subrutina_varlocal_v0.s
@ introducción a las subrutinas
@ apilar registros y variables locales en la pila
@ mejor gestion del fichero

        .data
        .size A,24
A:      .word 6
        .word 5
        .word 4
        .word 3
        .word 2
        .word 1
dim:    .word 6
        .text

@ Programa invocador
main:	    ldr r0,.L2
            ldr r1,[r0,#24]
	    bl sumatorios

fin:        wfi 

@ subrutina sumatorios
sumatorios: @ --- 1 ---
            push {r4,r5,r6,lr}
            sub sp, sp, #48
	    add r4, sp, #0
	    str r0, [sp,#40] 
	    str r1, [sp,#44] 
            mov r5, r0
            mov r6, r1


for1:       cmp r6, #0
            beq finfor1

            @ --- 2 ---
            bl sumatorio
	    str r2, [r4,#0]

	    @ --- 3 ---
	    add r4, r4, #4    
	    add r5, r5, #4
	    sub r6, r6, #1
            mov r0, r5
            mov r1, r6
	    b    for1
  
finfor1:    @ --- 4 ---
	    ldr r0, [sp,#40] 
	    ldr r1, [sp,#44] 
            add r4, sp, #0

for2:       cmp r1, #0
            beq finfor2
            ldr r5, [r4,#0]
            str r5, [r0,#0]
	    add r4, r4, #4    
	    add r0, r0, #4
	    sub r1, r1, #1
	    b for2
          
finfor2:    @ --- 5 ---
            add sp, sp, #48
            pop {r4,r5,r6,pc}

@ subrutina sumatorio
sumatorio:  push {r5,r6,r7,lr}
            mov  r2, #0
            mov r6, r1
            mov r5, r0
for3:       cmp r6, #0
            beq finfor3
            ldr r7, [r5, #0]
            add r5, r5, #4
            add r2, r2, r6
            sub r6, r6, #1
	    b    for3
finfor3:    pop {r5,r6,r7,pc}

.L3:
       .align 2
.L2:
       .word A
       .word dim

