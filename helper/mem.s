global mem

extern malloc

mem:
    mov edi,[esp+8]
    call malloc
    mov [esp+12], eax 
    ret
