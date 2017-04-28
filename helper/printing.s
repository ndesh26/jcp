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
