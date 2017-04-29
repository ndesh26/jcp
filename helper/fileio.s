global open
global close
global create
global readChar
global writeChar

create:
    mov  eax, 8
    mov  ebx, [esp+8]
    mov  ecx, 0777        ;read, write and execute by all
    int  0x80  
    pop ebx
    pop ecx
    pop edx
    push eax
    push edx
    push ecx
    push ebx
    ret

open:
    mov eax, 5
    mov ebx, [esp+8] 
    mov ecx, 2             ;for read only access
    mov edx, 0777          ;read, write and execute by all
    int  0x80
    pop ebx
    pop ecx
    pop edx
    push eax
    push edx
    push ecx
    push ebx
    ret

writeChar:
    mov	edx, 4          ;number of bytes
    mov	ebx, [esp+8]    ;file descriptor 
    mov	eax,4            ;system call number (sys_write)
    mov	ecx, [esp+12]         ;message to write
    push ecx
    mov ecx, esp
    int	0x80             ;call kernel
    pop ecx
    ret

close:
    mov eax, 6
    mov ebx, [ebp+8]
    ret

readChar:
    mov eax, 3
    mov ebx, [esp+8]
    sub esp, 1
    mov ecx, esp
    mov edx, 1
    int 0x80
    add esp,3
    pop eax
    pop ebx
    pop ecx
    pop edx
    push eax
    push edx
    push ecx
    push ebx
    ret
