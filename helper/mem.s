global mem

extern malloc

mem:
    mov edi,[esp+4]
    call malloc
    mov [esp+8], eax
    ret
