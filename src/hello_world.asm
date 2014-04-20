@ Hello World example in ARM assembly language
@ ============================================
@ Using GCC to compile it, the @ sign seems
@  to work best for line comments
@ compile using something like:
@  (arm-linux-)gcc -o helloarm helloarm.S -nostdlib
@  with -DEABI for the newer EABI
@    or -DTHUMB for 16-bit thumb code
@  (if the kernel supports these modes)

#ifdef THUMB
.code 16
#endif

.text                 @ section declaration
    .align  2         @ word boundary (2^2)
    .global _start    @ export the entry point to
                      @ the ELF linker or loader
                      @ (like in crt1.o)
#ifdef THUMB
    .thumb_func
#endif
_start:

@       write string to stdout
@
        mov    r0,#1      @ r0 file handle (stdout)
        adr    r1,msg     @ r1 ptr to string
        mov    r2,#12     @ r2 string length
#if defined(EABI) || defined(THUMB)
        mov    r7,#4
        swi    0x00       @ call kernel
#else
        swi    0x0900004  @ call kernel
#endif

@       exit back to system
@
        mov    r0,#0      @ r0 exit code
#if defined(EABI) || defined(THUMB)
        mov    r7,#1
        swi    0x00       @ call kernel
#else
        swi    0x0900001  @ call kernel
#endif

msg:
    .ascii     "Hello World\n"
