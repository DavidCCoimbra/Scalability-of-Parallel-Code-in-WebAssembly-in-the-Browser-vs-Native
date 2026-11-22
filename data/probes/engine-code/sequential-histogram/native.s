000000000002aed0 <<bench::workloads::histogram::sequential::SequentialHistogram as bench::workloads::workload::Workload>::run>:
   2aed0:	push   %rbx
   2aed1:	sub    $0x800,%rsp
   2aed8:	mov    %rdi,%rbx
   2aedb:	mov    %rsp,%rdi
   2aede:	mov    $0x800,%edx
   2aee3:	xor    %esi,%esi
   2aee5:	call   *0x5445d(%rip)        # 7f348 <memset@GLIBC_2.2.5>
   2aeeb:	mov    0x10(%rbx),%rdx
   2aeef:	test   %rdx,%rdx
   2aef2:	je     2af58 <<bench::workloads::histogram::sequential::SequentialHistogram as bench::workloads::workload::Workload>::run+0x88>
   2aef4:	mov    0x8(%rbx),%rax
   2aef8:	mov    %rdx,%rsi
   2aefb:	mov    %rax,%rcx
   2aefe:	and    $0x3,%rsi
   2af02:	je     2af20 <<bench::workloads::histogram::sequential::SequentialHistogram as bench::workloads::workload::Workload>::run+0x50>
   2af04:	mov    %rax,%rcx
   2af07:	nopw   0x0(%rax,%rax,1)
   2af10:	movzbl (%rcx),%r8d
   2af14:	inc    %rcx
   2af17:	incq   (%rsp,%r8,8)
   2af1b:	dec    %rsi
   2af1e:	jne    2af10 <<bench::workloads::histogram::sequential::SequentialHistogram as bench::workloads::workload::Workload>::run+0x40>
   2af20:	cmp    $0x4,%rdx
   2af24:	jb     2af58 <<bench::workloads::histogram::sequential::SequentialHistogram as bench::workloads::workload::Workload>::run+0x88>
   2af26:	add    %rdx,%rax
   2af29:	nopl   0x0(%rax)
   2af30:	movzbl (%rcx),%edx
   2af33:	incq   (%rsp,%rdx,8)
   2af37:	movzbl 0x1(%rcx),%edx
   2af3b:	incq   (%rsp,%rdx,8)
   2af3f:	movzbl 0x2(%rcx),%edx
   2af43:	incq   (%rsp,%rdx,8)
   2af47:	movzbl 0x3(%rcx),%edx
   2af4b:	incq   (%rsp,%rdx,8)
   2af4f:	add    $0x4,%rcx
   2af53:	cmp    %rax,%rcx
   2af56:	jne    2af30 <<bench::workloads::histogram::sequential::SequentialHistogram as bench::workloads::workload::Workload>::run+0x60>
   2af58:	add    $0x30,%rbx
   2af5c:	mov    %rsp,%rsi
   2af5f:	mov    $0x800,%edx
   2af64:	mov    %rbx,%rdi
   2af67:	call   *0x5432b(%rip)        # 7f298 <memcpy@GLIBC_2.14>
   2af6d:	add    $0x800,%rsp
   2af74:	pop    %rbx
   2af75:	ret
   2af76:	int3
   2af77:	int3
   2af78:	int3
   2af79:	int3
   2af7a:	int3
   2af7b:	int3
   2af7c:	int3
   2af7d:	int3
   2af7e:	int3
   2af7f:	int3
