000000000002b540 <bench::workloads::gaussian::blur_interior>:
   2b540:	push   %rbp
   2b541:	push   %r14
   2b543:	push   %rbx
   2b544:	mov    %rsi,%r11
   2b547:	mov    0x28(%rsp),%rsi
   2b54c:	cmp    %r11,%rsi
   2b54f:	ja     2b80e <bench::workloads::gaussian::blur_interior+0x2ce>
   2b555:	lea    0x1(%rsi),%rax
   2b559:	cmp    %r11,%rsi
   2b55c:	jae    2b81f <bench::workloads::gaussian::blur_interior+0x2df>
   2b562:	lea    0x2(%rsi),%r10
   2b566:	cmp    %r11,%r10
   2b569:	ja     2b836 <bench::workloads::gaussian::blur_interior+0x2f6>
   2b56f:	cmp    %rcx,%rsi
   2b572:	ja     2b84d <bench::workloads::gaussian::blur_interior+0x30d>
   2b578:	jae    2b861 <bench::workloads::gaussian::blur_interior+0x321>
   2b57e:	cmp    %rcx,%r10
   2b581:	ja     2b87b <bench::workloads::gaussian::blur_interior+0x33b>
   2b587:	cmp    %r9,%rsi
   2b58a:	ja     2b895 <bench::workloads::gaussian::blur_interior+0x355>
   2b590:	jae    2b8a6 <bench::workloads::gaussian::blur_interior+0x366>
   2b596:	cmp    %r9,%r10
   2b599:	ja     2b8bd <bench::workloads::gaussian::blur_interior+0x37d>
   2b59f:	test   %rsi,%rsi
   2b5a2:	je     2b934 <bench::workloads::gaussian::blur_interior+0x3f4>
   2b5a8:	mov    0x20(%rsp),%rax
   2b5ad:	cmp    $0x4,%rsi
   2b5b1:	jae    2b5ba <bench::workloads::gaussian::blur_interior+0x7a>
   2b5b3:	xor    %ecx,%ecx
   2b5b5:	jmp    2b8d4 <bench::workloads::gaussian::blur_interior+0x394>
   2b5ba:	movabs $0x7ffffffffffffff0,%r9
   2b5c4:	cmp    $0x10,%rsi
   2b5c8:	jae    2b5d1 <bench::workloads::gaussian::blur_interior+0x91>
   2b5ca:	xor    %ecx,%ecx
   2b5cc:	jmp    2b738 <bench::workloads::gaussian::blur_interior+0x1f8>
   2b5d1:	mov    %rsi,%rcx
   2b5d4:	and    %r9,%rcx
   2b5d7:	xor    %r10d,%r10d
   2b5da:	pxor   %xmm0,%xmm0
   2b5de:	movdqa -0x26b16(%rip),%xmm1        # 4ad0 <__abi_tag+0x47d4>
   2b5e6:	cs nopw 0x0(%rax,%rax,1)
   2b5f0:	movdqu (%rdi,%r10,1),%xmm2
   2b5f6:	movdqu 0x1(%rdi,%r10,1),%xmm4
   2b5fd:	movdqu 0x2(%rdi,%r10,1),%xmm3
   2b604:	movdqa %xmm4,%xmm6
   2b608:	punpcklbw %xmm0,%xmm6
   2b60c:	punpckhbw %xmm0,%xmm4
   2b610:	movdqa %xmm2,%xmm5
   2b614:	punpcklbw %xmm0,%xmm5
   2b618:	punpckhbw %xmm0,%xmm2
   2b61c:	movdqa %xmm3,%xmm9
   2b621:	punpcklbw %xmm0,%xmm9
   2b626:	paddw  %xmm5,%xmm9
   2b62b:	punpckhbw %xmm0,%xmm3
   2b62f:	paddw  %xmm2,%xmm3
   2b633:	movdqu (%rdx,%r10,1),%xmm5
   2b639:	movdqu 0x1(%rdx,%r10,1),%xmm2
   2b640:	movdqu 0x2(%rdx,%r10,1),%xmm8
   2b647:	movdqa %xmm5,%xmm7
   2b64b:	punpcklbw %xmm0,%xmm7
   2b64f:	paddw  %xmm6,%xmm7
   2b653:	punpckhbw %xmm0,%xmm5
   2b657:	paddw  %xmm4,%xmm5
   2b65b:	movdqa %xmm2,%xmm4
   2b65f:	punpcklbw %xmm0,%xmm4
   2b663:	punpckhbw %xmm0,%xmm2
   2b667:	psllw  $0x2,%xmm2
   2b66c:	paddw  %xmm3,%xmm2
   2b670:	psllw  $0x2,%xmm4
   2b675:	paddw  %xmm9,%xmm4
   2b67a:	movdqa %xmm8,%xmm9
   2b67f:	punpckhbw %xmm0,%xmm9
   2b684:	punpcklbw %xmm0,%xmm8
   2b689:	movdqu (%r8,%r10,1),%xmm10
   2b68f:	movdqu 0x1(%r8,%r10,1),%xmm3
   2b696:	movdqu 0x2(%r8,%r10,1),%xmm11
   2b69d:	movdqa %xmm10,%xmm12
   2b6a2:	punpcklbw %xmm0,%xmm12
   2b6a7:	punpckhbw %xmm0,%xmm10
   2b6ac:	movdqa %xmm3,%xmm6
   2b6b0:	punpcklbw %xmm0,%xmm6
   2b6b4:	paddw  %xmm8,%xmm6
   2b6b9:	paddw  %xmm7,%xmm6
   2b6bd:	punpckhbw %xmm0,%xmm3
   2b6c1:	paddw  %xmm9,%xmm3
   2b6c6:	paddw  %xmm5,%xmm3
   2b6ca:	movdqa %xmm11,%xmm5
   2b6cf:	punpckhbw %xmm0,%xmm5
   2b6d3:	paddw  %xmm10,%xmm5
   2b6d8:	paddw  %xmm2,%xmm5
   2b6dc:	punpcklbw %xmm0,%xmm11
   2b6e1:	paddw  %xmm12,%xmm11
   2b6e6:	paddw  %xmm4,%xmm11
   2b6eb:	paddw  %xmm6,%xmm6
   2b6ef:	paddw  %xmm11,%xmm6
   2b6f4:	paddw  %xmm3,%xmm3
   2b6f8:	paddw  %xmm5,%xmm3
   2b6fc:	paddw  %xmm1,%xmm6
   2b700:	paddw  %xmm1,%xmm3
   2b704:	psrlw  $0x4,%xmm3
   2b709:	psrlw  $0x4,%xmm6
   2b70e:	packuswb %xmm3,%xmm6
   2b712:	movdqu %xmm6,(%rax,%r10,1)
   2b718:	add    $0x10,%r10
   2b71c:	cmp    %r10,%rcx
   2b71f:	jne    2b5f0 <bench::workloads::gaussian::blur_interior+0xb0>
   2b725:	cmp    %rcx,%rsi
   2b728:	je     2b934 <bench::workloads::gaussian::blur_interior+0x3f4>
   2b72e:	test   $0xc,%sil
   2b732:	je     2b8d4 <bench::workloads::gaussian::blur_interior+0x394>
   2b738:	mov    %rcx,%r10
   2b73b:	add    $0xc,%r9
   2b73f:	mov    %r9,%rcx
   2b742:	and    %rsi,%rcx
   2b745:	pxor   %xmm0,%xmm0
   2b749:	movdqa -0x267d1(%rip),%xmm1        # 4f80 <__abi_tag+0x4c84>
   2b751:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
   2b760:	movd   0x1(%rdi,%r10,1),%xmm2
   2b767:	punpcklbw %xmm0,%xmm2
   2b76b:	movd   (%rdi,%r10,1),%xmm3
   2b771:	punpcklbw %xmm0,%xmm3
   2b775:	movd   0x2(%rdi,%r10,1),%xmm4
   2b77c:	punpcklbw %xmm0,%xmm4
   2b780:	paddw  %xmm3,%xmm4
   2b784:	movd   (%rdx,%r10,1),%xmm3
   2b78a:	punpcklbw %xmm0,%xmm3
   2b78e:	paddw  %xmm2,%xmm3
   2b792:	movd   0x1(%rdx,%r10,1),%xmm2
   2b799:	punpcklbw %xmm0,%xmm2
   2b79d:	psllw  $0x2,%xmm2
   2b7a2:	paddw  %xmm4,%xmm2
   2b7a6:	movd   0x2(%rdx,%r10,1),%xmm4
   2b7ad:	punpcklbw %xmm0,%xmm4
   2b7b1:	movd   (%r8,%r10,1),%xmm5
   2b7b7:	punpcklbw %xmm0,%xmm5
   2b7bb:	movd   0x1(%r8,%r10,1),%xmm6
   2b7c2:	punpcklbw %xmm0,%xmm6
   2b7c6:	paddw  %xmm4,%xmm6
   2b7ca:	paddw  %xmm3,%xmm6
   2b7ce:	movd   0x2(%r8,%r10,1),%xmm3
   2b7d5:	punpcklbw %xmm0,%xmm3
   2b7d9:	paddw  %xmm5,%xmm3
   2b7dd:	paddw  %xmm2,%xmm3
   2b7e1:	paddw  %xmm6,%xmm6
   2b7e5:	paddw  %xmm3,%xmm6
   2b7e9:	paddw  %xmm1,%xmm6
   2b7ed:	psrlw  $0x4,%xmm6
   2b7f2:	packuswb %xmm6,%xmm6
   2b7f6:	movd   %xmm6,(%rax,%r10,1)
   2b7fc:	add    $0x4,%r10
   2b800:	cmp    %r10,%rcx
   2b803:	jne    2b760 <bench::workloads::gaussian::blur_interior+0x220>
   2b809:	jmp    2b92f <bench::workloads::gaussian::blur_interior+0x3ef>
   2b80e:	lea    0x518b3(%rip),%rcx        # 7d0c8 <__frame_dummy_init_array_entry+0xa58>
   2b815:	xor    %edi,%edi
   2b817:	mov    %r11,%rdx
   2b81a:	call   383a0 <core::slice::index::slice_index_fail>
   2b81f:	lea    0x5188a(%rip),%rcx        # 7d0b0 <__frame_dummy_init_array_entry+0xa40>
   2b826:	mov    $0x1,%edi
   2b82b:	mov    %rax,%rsi
   2b82e:	mov    %r11,%rdx
   2b831:	call   383a0 <core::slice::index::slice_index_fail>
   2b836:	lea    0x5185b(%rip),%rcx        # 7d098 <__frame_dummy_init_array_entry+0xa28>
   2b83d:	mov    $0x2,%edi
   2b842:	mov    %r10,%rsi
   2b845:	mov    %r11,%rdx
   2b848:	call   383a0 <core::slice::index::slice_index_fail>
   2b84d:	lea    0x517b4(%rip),%rax        # 7d008 <__frame_dummy_init_array_entry+0x998>
   2b854:	xor    %edi,%edi
   2b856:	mov    %rcx,%rdx
   2b859:	mov    %rax,%rcx
   2b85c:	call   383a0 <core::slice::index::slice_index_fail>
   2b861:	lea    0x517b8(%rip),%r8        # 7d020 <__frame_dummy_init_array_entry+0x9b0>
   2b868:	mov    $0x1,%edi
   2b86d:	mov    %rax,%rsi
   2b870:	mov    %rcx,%rdx
   2b873:	mov    %r8,%rcx
   2b876:	call   383a0 <core::slice::index::slice_index_fail>
   2b87b:	lea    0x517b6(%rip),%rax        # 7d038 <__frame_dummy_init_array_entry+0x9c8>
   2b882:	mov    $0x2,%edi
   2b887:	mov    %r10,%rsi
   2b88a:	mov    %rcx,%rdx
   2b88d:	mov    %rax,%rcx
   2b890:	call   383a0 <core::slice::index::slice_index_fail>
   2b895:	lea    0x517b4(%rip),%rcx        # 7d050 <__frame_dummy_init_array_entry+0x9e0>
   2b89c:	xor    %edi,%edi
   2b89e:	mov    %r9,%rdx
   2b8a1:	call   383a0 <core::slice::index::slice_index_fail>
   2b8a6:	lea    0x517bb(%rip),%rcx        # 7d068 <__frame_dummy_init_array_entry+0x9f8>
   2b8ad:	mov    $0x1,%edi
   2b8b2:	mov    %rax,%rsi
   2b8b5:	mov    %r9,%rdx
   2b8b8:	call   383a0 <core::slice::index::slice_index_fail>
   2b8bd:	lea    0x517bc(%rip),%rcx        # 7d080 <__frame_dummy_init_array_entry+0xa10>
   2b8c4:	mov    $0x2,%edi
   2b8c9:	mov    %r10,%rsi
   2b8cc:	mov    %r9,%rdx
   2b8cf:	call   383a0 <core::slice::index::slice_index_fail>
   2b8d4:	movzbl 0x1(%rdi,%rcx,1),%r9d
   2b8da:	movzbl (%rdi,%rcx,1),%r10d
   2b8df:	movzbl 0x2(%rdi,%rcx,1),%r11d
   2b8e5:	add    %r10d,%r11d
   2b8e8:	movzbl (%rdx,%rcx,1),%r10d
   2b8ed:	add    %r9d,%r10d
   2b8f0:	movzbl 0x1(%rdx,%rcx,1),%r9d
   2b8f6:	movzbl 0x2(%rdx,%rcx,1),%ebx
   2b8fb:	movzbl (%r8,%rcx,1),%ebp
   2b900:	movzbl 0x1(%r8,%rcx,1),%r14d
   2b906:	add    %ebx,%r14d
   2b909:	add    %r10d,%r14d
   2b90c:	movzbl 0x2(%r8,%rcx,1),%r10d
   2b912:	add    %ebp,%r10d
   2b915:	lea    (%r11,%r9,4),%r9d
   2b919:	add    %r10d,%r9d
   2b91c:	lea    (%r9,%r14,2),%r9d
   2b920:	add    $0x8,%r9d
   2b924:	shr    $0x4,%r9d
   2b928:	mov    %r9b,(%rax,%rcx,1)
   2b92c:	inc    %rcx
   2b92f:	cmp    %rcx,%rsi
   2b932:	jne    2b8d4 <bench::workloads::gaussian::blur_interior+0x394>
   2b934:	pop    %rbx
   2b935:	pop    %r14
   2b937:	pop    %rbp
   2b938:	ret
   2b939:	int3
   2b93a:	int3
   2b93b:	int3
   2b93c:	int3
   2b93d:	int3
   2b93e:	int3
   2b93f:	int3
