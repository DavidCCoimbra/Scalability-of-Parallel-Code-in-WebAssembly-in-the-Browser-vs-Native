     8c0:	movzx  ebx,BYTE PTR [r15+r12*1]
     8c5:	lea    ebx,[rax+rbx*8+0x2830]
     8cc:	mov    rdx,QWORD PTR [r15+rbx*1]
     8d0:	add    rdx,0x1
     8d4:	mov    QWORD PTR [r15+rbx*1],rdx
     8d8:	add    r12d,0x1
     8dc:	add    r11d,0xffffffff
     8e0:	je     0x963
     8e6:	movzx  ebx,BYTE PTR [r15+r12*1]
     8eb:	lea    ebx,[rax+rbx*8+0x2830]
     8f2:	mov    rdx,QWORD PTR [r15+rbx*1]
     8f6:	add    rdx,0x1
     8fa:	mov    QWORD PTR [r15+rbx*1],rdx
     8fe:	add    r12d,0x1
     902:	add    r11d,0xffffffff
     906:	je     0x963
     90c:	movzx  ebx,BYTE PTR [r15+r12*1]
     911:	lea    ebx,[rax+rbx*8+0x2830]
     918:	mov    rdx,QWORD PTR [r15+rbx*1]
     91c:	add    rdx,0x1
     920:	mov    QWORD PTR [r15+rbx*1],rdx
     924:	add    r12d,0x1
     928:	add    r11d,0xffffffff
     92c:	je     0x963
     932:	cmp    BYTE PTR [r13-0x4f],0x0
     937:	jne    0xfa1
     93d:	movzx  ebx,BYTE PTR [r15+r12*1]
     942:	lea    ebx,[rax+rbx*8+0x2830]
     949:	mov    rdx,QWORD PTR [r15+rbx*1]
     94d:	add    rdx,0x1
     951:	mov    QWORD PTR [r15+rbx*1],rdx
     955:	add    r12d,0x1
     959:	add    r11d,0xffffffff
     95d:	jne    0x8c0
     963:	mov    ebx,DWORD PTR [rbp-0x60]
     966:	add    ebx,r8d
     969:	cmp    r8d,0x4
     96d:	jb     0xa0b
     973:	nop    WORD PTR [rax+rax*1+0x0]
     97c:	nop    DWORD PTR [rax+0x0]
     980:	cmp    BYTE PTR [r13-0x4f],0x0
     985:	jne    0xfce
     98b:	movzx  r11d,BYTE PTR [r15+r12*1]
     990:	lea    r11d,[rax+r11*8+0x2830]
     998:	mov    rdx,QWORD PTR [r15+r11*1]
     99c:	add    rdx,0x1
     9a0:	mov    QWORD PTR [r15+r11*1],rdx
     9a4:	lea    r11d,[r12+0x1]
     9a9:	movzx  r11d,BYTE PTR [r15+r11*1]
     9ae:	lea    r11d,[rax+r11*8+0x2830]
     9b6:	mov    rdx,QWORD PTR [r15+r11*1]
     9ba:	add    rdx,0x1
     9be:	mov    QWORD PTR [r15+r11*1],rdx
     9c2:	lea    r11d,[r12+0x2]
     9c7:	movzx  r11d,BYTE PTR [r15+r11*1]
     9cc:	lea    r11d,[rax+r11*8+0x2830]
     9d4:	mov    rdx,QWORD PTR [r15+r11*1]
     9d8:	add    rdx,0x1
     9dc:	mov    QWORD PTR [r15+r11*1],rdx
     9e0:	lea    r11d,[r12+0x3]
     9e5:	movzx  r11d,BYTE PTR [r15+r11*1]
     9ea:	lea    r11d,[rax+r11*8+0x2830]
     9f2:	mov    rdx,QWORD PTR [r15+r11*1]
     9f6:	add    rdx,0x1
     9fa:	mov    QWORD PTR [r15+r11*1],rdx
     9fe:	add    r12d,0x4
     a02:	cmp    r12d,ebx
     a05:	jne    0x980
