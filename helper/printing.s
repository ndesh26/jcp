global printInt
global printChar
global printlnInt
global scanInt 
extern scanf

SECTION .data
formatin: db "%d", 0
integer1: times 4 db 0 ; 32-bits integer = 4 bytes

printInt:
        mov eax, [esp+8]
        xor esi, esi
        cmp eax, 0
        jge loop
        neg eax
        push eax
        mov eax, 45
        push eax
        mov eax, 4 ; Print "-" 
        mov edx, 1 
        mov ecx, esp
        mov ebx, 1
        int 0x80
        pop eax
        pop eax
        
loop:
        mov edx, 0
        mov ebx, 10
        div ebx
        add edx, 48
        push edx
        inc esi
        cmp eax, 0
        jz  next
        jmp loop
        
next:
        cmp  esi, 0
        jz   exit
        dec  esi
        mov  eax, 4
        mov  ecx, esp
        mov  ebx, 1
        mov  edx, 1
        int  0x80
        add  esp, 4
        jmp  next
        
exit:
        ret

printChar:
        mov eax, [esp+8]
        push eax
        mov  eax, 4
        mov  ecx, esp
        mov  ebx, 1
        mov  edx, 1
        int  0x80
        add  esp, 4
        ret

printlnInt:
        mov eax, [esp+8]
        xor esi, esi
        cmp eax, 0
        jge loop1
        neg eax
        push eax
        mov eax, 45
        push eax
        mov eax, 4 ; Print "-" 
        mov edx, 1 
        mov ecx, esp
        mov ebx, 1
        int 0x80
        pop eax
        pop eax
        
loop1:
        mov edx, 0
        mov ebx, 10
        div ebx
        add edx, 48
        push edx
        inc esi
        cmp eax, 0
        jz  next1
        jmp loop1
        
next1:
        cmp  esi, 0
        jz   exit1
        dec  esi
        mov  eax, 4
        mov  ecx, esp
        mov  ebx, 1
        mov  edx, 1
        int  0x80
        add  esp, 4
        jmp  next1
        
exit1:
        push 10
        mov  eax, 4
        mov  ecx, esp
        mov  ebx, 1
        mov  edx, 1
        int  0x80
        pop eax
        ret

scanInt:
        push integer1
        push formatin ; arguments are right to left (first parameter)
        call scanf
        add esp, 8
        mov eax, [integer1]
        pop ebx
        push eax
        push ebx
        push ebx
        ret

        
