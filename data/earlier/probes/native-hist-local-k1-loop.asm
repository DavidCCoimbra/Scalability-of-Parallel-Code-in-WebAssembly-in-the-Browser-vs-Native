   298e0:	movzx  edx,BYTE PTR [rax]
   298e3:	inc    rax
   298e6:	inc    QWORD PTR [rsp+rdx*8+0x48]
   298eb:	dec    rcx
   298ee:	jne    298e0 
   298f0:	add    r13,r12
   298f3:	cmp    r12,0x4
   298f7:	jb     29890 
   298f9:	nop    DWORD PTR [rax+0x0]
   29900:	movzx  ecx,BYTE PTR [rax]
   29903:	inc    QWORD PTR [rsp+rcx*8+0x48]
   29908:	movzx  ecx,BYTE PTR [rax+0x1]
   2990c:	inc    QWORD PTR [rsp+rcx*8+0x48]
   29911:	movzx  ecx,BYTE PTR [rax+0x2]
   29915:	inc    QWORD PTR [rsp+rcx*8+0x48]
   2991a:	movzx  ecx,BYTE PTR [rax+0x3]
   2991e:	inc    QWORD PTR [rsp+rcx*8+0x48]
   29923:	add    rax,0x4
   29927:	cmp    rax,r13
   2992a:	jne    29900 
