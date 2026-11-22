000000000002b080 <<bench::workloads::gaussian::sequential::SequentialBlur as bench::workloads::workload::Workload>::run>:
   2b080:	push   %rbp
   2b081:	push   %r15
   2b083:	push   %r14
   2b085:	push   %r13
   2b087:	push   %r12
   2b089:	push   %rbx
   2b08a:	sub    $0x68,%rsp
   2b08e:	mov    0x28(%rdi),%r11
   2b092:	test   %r11,%r11
   2b095:	je     2b321 <<bench::workloads::gaussian::sequential::SequentialBlur as bench::workloads::workload::Workload>::run+0x2a1>
   2b09b:	mov    0x40(%rdi),%rbp
   2b09f:	test   %rbp,%rbp
   2b0a2:	je     2b2b6 <<bench::workloads::gaussian::sequential::SequentialBlur as bench::workloads::workload::Workload>::run+0x236>
   2b0a8:	mov    0x18(%rdi),%r8
   2b0ac:	mov    0x20(%rdi),%rax
   2b0b0:	dec    %rax
   2b0b3:	mov    %rax,0x10(%rsp)
   2b0b8:	mov    0x10(%rdi),%rdx
   2b0bc:	xor    %r15d,%r15d
   2b0bf:	mov    %r8,%rcx
   2b0c2:	sub    $0x1,%rcx
   2b0c6:	setne  %al
   2b0c9:	jb     2b339 <<bench::workloads::gaussian::sequential::SequentialBlur as bench::workloads::workload::Workload>::run+0x2b9>
   2b0cf:	mov    %al,%r15b
   2b0d2:	cmp    %r15,%r8
   2b0d5:	mov    %rdx,0x8(%rsp)
   2b0da:	jbe    2b360 <<bench::workloads::gaussian::sequential::SequentialBlur as bench::workloads::workload::Workload>::run+0x2e0>
   2b0e0:	mov    0x8(%rdi),%r9
   2b0e4:	lea    -0x2(%r8),%rax
   2b0e8:	mov    %rax,0x30(%rsp)
   2b0ed:	mov    0x38(%rdi),%r13
   2b0f1:	mov    %rcx,0x50(%rsp)
   2b0f6:	lea    (%r9,%rcx,1),%rax
   2b0fa:	mov    %rax,0x28(%rsp)
   2b0ff:	lea    (%r9,%r15,1),%rax
   2b103:	mov    %rax,0x48(%rsp)
   2b108:	mov    $0x1,%r14d
   2b10e:	xor    %ebx,%ebx
   2b110:	xor    %edi,%edi
   2b112:	mov    %r11,0x40(%rsp)
   2b117:	mov    %r8,0x20(%rsp)
   2b11c:	mov    %r15,0x38(%rsp)
   2b121:	mov    %r9,0x18(%rsp)
   2b126:	jmp    2b15c <<bench::workloads::gaussian::sequential::SequentialBlur as bench::workloads::workload::Workload>::run+0xdc>
   2b128:	nopl   0x0(%rax,%rax,1)
   2b130:	add    %r12,%r13
   2b133:	sub    %r12,%rbp
   2b136:	add    %r11,%rbx
   2b139:	inc    %r14
   2b13c:	mov    0x60(%rsp),%rdi
   2b141:	inc    %rdi
   2b144:	test   %rbp,%rbp
   2b147:	mov    0x8(%rsp),%rdx
   2b14c:	mov    0x20(%rsp),%r8
   2b151:	mov    0x18(%rsp),%r9
   2b156:	je     2b2b6 <<bench::workloads::gaussian::sequential::SequentialBlur as bench::workloads::workload::Workload>::run+0x236>
   2b15c:	mov    %rdi,%rcx
   2b15f:	sub    $0x1,%rcx
   2b163:	mov    $0x0,%eax
   2b168:	cmovae %rcx,%rax
   2b16c:	cmp    %r11,%rbp
   2b16f:	mov    %r11,%r12
   2b172:	cmovb  %rbp,%r12
   2b176:	cmp    %r12,%r8
   2b179:	ja     2b2c5 <<bench::workloads::gaussian::sequential::SequentialBlur as bench::workloads::workload::Workload>::run+0x245>
   2b17f:	mov    0x10(%rsp),%rcx
   2b184:	cmp    %rcx,%r14
   2b187:	cmovb  %r14,%rcx
   2b18b:	imul   %r11,%rax
   2b18f:	mov    %rax,%rsi
   2b192:	add    %r8,%rsi
   2b195:	jb     2b2d9 <<bench::workloads::gaussian::sequential::SequentialBlur as bench::workloads::workload::Workload>::run+0x259>
   2b19b:	cmp    %rdx,%rsi
   2b19e:	ja     2b2d9 <<bench::workloads::gaussian::sequential::SequentialBlur as bench::workloads::workload::Workload>::run+0x259>
   2b1a4:	mov    %r8,%rsi
   2b1a7:	add    %rbx,%rsi
   2b1aa:	jb     2b2eb <<bench::workloads::gaussian::sequential::SequentialBlur as bench::workloads::workload::Workload>::run+0x26b>
   2b1b0:	cmp    %rdx,%rsi
   2b1b3:	ja     2b2eb <<bench::workloads::gaussian::sequential::SequentialBlur as bench::workloads::workload::Workload>::run+0x26b>
   2b1b9:	imul   %r11,%rcx
   2b1bd:	mov    %rcx,%rsi
   2b1c0:	add    %r8,%rsi
   2b1c3:	jb     2b2fd <<bench::workloads::gaussian::sequential::SequentialBlur as bench::workloads::workload::Workload>::run+0x27d>
   2b1c9:	cmp    %rdx,%rsi
   2b1cc:	ja     2b30f <<bench::workloads::gaussian::sequential::SequentialBlur as bench::workloads::workload::Workload>::run+0x28f>
   2b1d2:	mov    %rdi,0x60(%rsp)
   2b1d7:	lea    (%r9,%rax,1),%rdi
   2b1db:	lea    (%r9,%rcx,1),%r8
   2b1df:	movzbl (%r9,%rbx,1),%edx
   2b1e4:	mov    0x48(%rsp),%rsi
   2b1e9:	movzbl (%rsi,%rbx,1),%esi
   2b1ed:	add    %edx,%esi
   2b1ef:	movzbl (%r9,%rcx,1),%ecx
   2b1f4:	add    %ecx,%esi
   2b1f6:	movzbl (%r9,%rax,1),%eax
   2b1fb:	lea    (%rax,%rax,2),%eax
   2b1fe:	movzbl (%r15,%rdi,1),%r9d
   2b203:	movzbl (%r15,%r8,1),%r10d
   2b208:	lea    (%rcx,%rdx,4),%ecx
   2b20b:	add    %r9d,%ecx
   2b20e:	add    %eax,%ecx
   2b210:	lea    (%rcx,%rsi,2),%eax
   2b213:	add    %r10d,%eax
   2b216:	add    $0x8,%eax
   2b219:	shr    $0x4,%eax
   2b21c:	mov    %al,0x0(%r13)
   2b220:	mov    0x50(%rsp),%rdx
   2b225:	test   %rdx,%rdx
   2b228:	je     2b130 <<bench::workloads::gaussian::sequential::SequentialBlur as bench::workloads::workload::Workload>::run+0xb0>
   2b22e:	mov    0x18(%rsp),%rax
   2b233:	add    %rbx,%rax
   2b236:	mov    %rax,0x58(%rsp)
   2b23b:	movzbl (%rdi,%rdx,1),%eax
   2b23f:	mov    0x20(%rsp),%rcx
   2b244:	movzbl -0x2(%rdi,%rcx,1),%r15d
   2b24a:	mov    0x28(%rsp),%r9
   2b24f:	movzbl (%r9,%rbx,1),%esi
   2b254:	movzbl -0x1(%r9,%rbx,1),%r9d
   2b25a:	movzbl (%r8,%rdx,1),%r10d
   2b25f:	movzbl -0x2(%r8,%rcx,1),%r11d
   2b265:	add    %esi,%r9d
   2b268:	add    %eax,%r9d
   2b26b:	add    %r10d,%r9d
   2b26e:	add    %eax,%r15d
   2b271:	lea    (%r15,%rsi,4),%eax
   2b275:	mov    0x38(%rsp),%r15
   2b27a:	add    %r10d,%r11d
   2b27d:	add    %eax,%r11d
   2b280:	lea    (%r11,%r9,2),%eax
   2b284:	add    $0x8,%eax
   2b287:	shr    $0x4,%eax
   2b28a:	mov    %al,0x0(%r13,%rdx,1)
   2b28f:	lea    0x1(%r13),%rax
   2b293:	mov    %rcx,%rsi
   2b296:	mov    0x58(%rsp),%rdx
   2b29b:	mov    %rcx,%r9
   2b29e:	push   0x30(%rsp)
   2b2a2:	push   %rax
   2b2a3:	call   2b540 <bench::workloads::gaussian::blur_interior>
   2b2a8:	mov    0x50(%rsp),%r11
   2b2ad:	add    $0x10,%rsp
   2b2b1:	jmp    2b130 <<bench::workloads::gaussian::sequential::SequentialBlur as bench::workloads::workload::Workload>::run+0xb0>
   2b2b6:	add    $0x68,%rsp
   2b2ba:	pop    %rbx
   2b2bb:	pop    %r12
   2b2bd:	pop    %r13
   2b2bf:	pop    %r14
   2b2c1:	pop    %r15
   2b2c3:	pop    %rbp
   2b2c4:	ret
   2b2c5:	lea    0x519c4(%rip),%rcx        # 7cc90 <__frame_dummy_init_array_entry+0x620>
   2b2cc:	xor    %edi,%edi
   2b2ce:	mov    %r8,%rsi
   2b2d1:	mov    %r12,%rdx
   2b2d4:	call   383a0 <core::slice::index::slice_index_fail>
   2b2d9:	mov    %rax,%r11
   2b2dc:	lea    0x51c65(%rip),%rcx        # 7cf48 <__frame_dummy_init_array_entry+0x8d8>
   2b2e3:	mov    %r11,%rdi
   2b2e6:	call   383a0 <core::slice::index::slice_index_fail>
   2b2eb:	mov    %rbx,%r11
   2b2ee:	lea    0x51c53(%rip),%rcx        # 7cf48 <__frame_dummy_init_array_entry+0x8d8>
   2b2f5:	mov    %r11,%rdi
   2b2f8:	call   383a0 <core::slice::index::slice_index_fail>
   2b2fd:	mov    %rcx,%r11
   2b300:	lea    0x51c41(%rip),%rcx        # 7cf48 <__frame_dummy_init_array_entry+0x8d8>
   2b307:	mov    %r11,%rdi
   2b30a:	call   383a0 <core::slice::index::slice_index_fail>
   2b30f:	mov    %rcx,%r11
   2b312:	lea    0x51c2f(%rip),%rcx        # 7cf48 <__frame_dummy_init_array_entry+0x8d8>
   2b319:	mov    %r11,%rdi
   2b31c:	call   383a0 <core::slice::index::slice_index_fail>
   2b321:	lea    -0x22019(%rip),%rdi        # 930f <__abi_tag+0x9013>
   2b328:	lea    0x51eb9(%rip),%rdx        # 7d1e8 <__frame_dummy_init_array_entry+0xb78>
   2b32f:	mov    $0x37,%esi
   2b334:	call   36eb0 <core::panicking::panic_fmt>
   2b339:	cmpq   $0x0,0x10(%rsp)
   2b33f:	setne  %al
   2b342:	cmp    %rdx,%r11
   2b345:	seta   %cl
   2b348:	mov    %r11,%rsi
   2b34b:	test   %cl,%al
   2b34d:	jne    2b312 <<bench::workloads::gaussian::sequential::SequentialBlur as bench::workloads::workload::Workload>::run+0x292>
   2b34f:	xor    %edi,%edi
   2b351:	lea    0x51878(%rip),%rdx        # 7cbd0 <__frame_dummy_init_array_entry+0x560>
   2b358:	mov    %rdi,%rsi
   2b35b:	call   38481 <core::panicking::panic_bounds_check>
   2b360:	test   %rdx,%rdx
   2b363:	je     2b38c <<bench::workloads::gaussian::sequential::SequentialBlur as bench::workloads::workload::Workload>::run+0x30c>
   2b365:	mov    0x10(%rsp),%rax
   2b36a:	test   %rax,%rax
   2b36d:	cmovne %r11,%rax
   2b371:	mov    $0x1,%edi
   2b376:	cmp    0x8(%rsp),%rax
   2b37b:	jae    2b3a8 <<bench::workloads::gaussian::sequential::SequentialBlur as bench::workloads::workload::Workload>::run+0x328>
   2b37d:	lea    0x5184c(%rip),%rdx        # 7cbd0 <__frame_dummy_init_array_entry+0x560>
   2b384:	mov    %rdi,%rsi
   2b387:	call   38481 <core::panicking::panic_bounds_check>
   2b38c:	mov    $0x1,%esi
   2b391:	xor    %r11d,%r11d
   2b394:	mov    0x8(%rsp),%rdx
   2b399:	lea    0x51ba8(%rip),%rcx        # 7cf48 <__frame_dummy_init_array_entry+0x8d8>
   2b3a0:	mov    %r11,%rdi
   2b3a3:	call   383a0 <core::slice::index::slice_index_fail>
   2b3a8:	mov    %rax,%rsi
   2b3ab:	inc    %rsi
   2b3ae:	mov    0x8(%rsp),%rdx
   2b3b3:	lea    0x51b8e(%rip),%rcx        # 7cf48 <__frame_dummy_init_array_entry+0x8d8>
   2b3ba:	mov    %r11,%rdi
   2b3bd:	call   383a0 <core::slice::index::slice_index_fail>
   2b3c2:	int3
   2b3c3:	int3
   2b3c4:	int3
   2b3c5:	int3
   2b3c6:	int3
   2b3c7:	int3
   2b3c8:	int3
   2b3c9:	int3
   2b3ca:	int3
   2b3cb:	int3
   2b3cc:	int3
   2b3cd:	int3
   2b3ce:	int3
   2b3cf:	int3
