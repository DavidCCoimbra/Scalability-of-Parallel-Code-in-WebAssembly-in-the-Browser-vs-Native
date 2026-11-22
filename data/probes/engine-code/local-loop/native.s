000000000002bb90 <rayon::iter::plumbing::bridge_producer_consumer::helper::<rayon::iter::len::MaxLenProducer<rayon::slice::chunks::ChunksProducer<u8>>, rayon::iter::fold::FoldConsumer<rayon::iter::reduce::ReduceConsumer<<bench::workloads::histogram::Histogram>::merge, <bench::workloads::histogram::Histogram as core::default::Default>::default>, <bench::workloads::histogram::Histogram as core::default::Default>::default, bench::workloads::histogram::local::local_counts<rayon::iter::len::MaxLen<rayon::slice::chunks::Chunks<u8>>>::{closure#0}>>>:
   2bb90:	push   %rbp
   2bb91:	push   %r15
   2bb93:	push   %r14
   2bb95:	push   %r13
   2bb97:	push   %r12
   2bb99:	push   %rbx
   2bb9a:	sub    $0x1000,%rsp
   2bba1:	movq   $0x0,(%rsp)
   2bba9:	sub    $0x1000,%rsp
   2bbb0:	movq   $0x0,(%rsp)
   2bbb8:	sub    $0x1000,%rsp
   2bbbf:	movq   $0x0,(%rsp)
   2bbc7:	sub    $0x78,%rsp
   2bbcb:	mov    %rsi,0x18(%rsp)
   2bbd0:	mov    %r8,0x40(%rsp)
   2bbd5:	shr    $1,%rsi
   2bbd8:	cmp    %r8,%rsi
   2bbdb:	jae    2bdc5 <rayon::iter::plumbing::bridge_producer_consumer::helper::<rayon::iter::len::MaxLenProducer<rayon::slice::chunks::ChunksProducer<u8>>, rayon::iter::fold::FoldConsumer<rayon::iter::reduce::ReduceConsumer<<bench::workloads::histogram::Histogram>::merge, <bench::workloads::histogram::Histogram as core::default::Default>::default>, <bench::workloads::histogram::Histogram as core::default::Default>::default, bench::workloads::histogram::local::local_counts<rayon::iter::len::MaxLen<rayon::slice::chunks::Chunks<u8>>>::{closure#0}>>+0x235>
   2bbe1:	mov    0x10(%r9),%rax
   2bbe5:	mov    %rax,0x10(%rsp)
   2bbea:	test   %rax,%rax
   2bbed:	je     2bf5e <rayon::iter::plumbing::bridge_producer_consumer::helper::<rayon::iter::len::MaxLenProducer<rayon::slice::chunks::ChunksProducer<u8>>, rayon::iter::fold::FoldConsumer<rayon::iter::reduce::ReduceConsumer<<bench::workloads::histogram::Histogram>::merge, <bench::workloads::histogram::Histogram as core::default::Default>::default>, <bench::workloads::histogram::Histogram as core::default::Default>::default, bench::workloads::histogram::local::local_counts<rayon::iter::len::MaxLen<rayon::slice::chunks::Chunks<u8>>>::{closure#0}>>+0x3ce>
   2bbf3:	mov    %rdi,0x8(%rsp)
   2bbf8:	mov    (%r9),%r13
   2bbfb:	mov    0x8(%r9),%rbp
   2bbff:	lea    0x2878(%rsp),%rdi
   2bc07:	mov    $0x800,%edx
   2bc0c:	xor    %esi,%esi
   2bc0e:	call   *0x53734(%rip)        # 7f348 <memset@GLIBC_2.2.5>
   2bc14:	test   %rbp,%rbp
   2bc17:	je     2bce1 <rayon::iter::plumbing::bridge_producer_consumer::helper::<rayon::iter::len::MaxLenProducer<rayon::slice::chunks::ChunksProducer<u8>>, rayon::iter::fold::FoldConsumer<rayon::iter::reduce::ReduceConsumer<<bench::workloads::histogram::Histogram>::merge, <bench::workloads::histogram::Histogram as core::default::Default>::default>, <bench::workloads::histogram::Histogram as core::default::Default>::default, bench::workloads::histogram::local::local_counts<rayon::iter::len::MaxLen<rayon::slice::chunks::Chunks<u8>>>::{closure#0}>>+0x151>
   2bc1d:	lea    0x48(%rsp),%rdi
   2bc22:	lea    0x2878(%rsp),%rsi
   2bc2a:	mov    0x53667(%rip),%rax        # 7f298 <memcpy@GLIBC_2.14>
   2bc31:	jmp    2bc60 <rayon::iter::plumbing::bridge_producer_consumer::helper::<rayon::iter::len::MaxLenProducer<rayon::slice::chunks::ChunksProducer<u8>>, rayon::iter::fold::FoldConsumer<rayon::iter::reduce::ReduceConsumer<<bench::workloads::histogram::Histogram>::merge, <bench::workloads::histogram::Histogram as core::default::Default>::default>, <bench::workloads::histogram::Histogram as core::default::Default>::default, bench::workloads::histogram::local::local_counts<rayon::iter::len::MaxLen<rayon::slice::chunks::Chunks<u8>>>::{closure#0}>>+0xd0>
   2bc33:	data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
   2bc40:	mov    $0x800,%edx
   2bc45:	mov    %rbx,%rdi
   2bc48:	mov    %r15,%rsi
   2bc4b:	call   *%r14
   2bc4e:	mov    %r14,%rax
   2bc51:	mov    %rbx,%rsi
   2bc54:	mov    %r15,%rdi
   2bc57:	sub    %r12,%rbp
   2bc5a:	je     2bce1 <rayon::iter::plumbing::bridge_producer_consumer::helper::<rayon::iter::len::MaxLenProducer<rayon::slice::chunks::ChunksProducer<u8>>, rayon::iter::fold::FoldConsumer<rayon::iter::reduce::ReduceConsumer<<bench::workloads::histogram::Histogram>::merge, <bench::workloads::histogram::Histogram as core::default::Default>::default>, <bench::workloads::histogram::Histogram as core::default::Default>::default, bench::workloads::histogram::local::local_counts<rayon::iter::len::MaxLen<rayon::slice::chunks::Chunks<u8>>>::{closure#0}>>+0x151>
   2bc60:	mov    0x10(%rsp),%r12
   2bc65:	cmp    %r12,%rbp
   2bc68:	cmovb  %rbp,%r12
   2bc6c:	mov    $0x800,%edx
   2bc71:	mov    %rdi,%r15
   2bc74:	mov    %rsi,%rbx
   2bc77:	mov    %rax,%r14
   2bc7a:	call   *%rax
   2bc7c:	mov    %r12,%rcx
   2bc7f:	mov    %r13,%rax
   2bc82:	and    $0x3,%rcx
   2bc86:	je     2bca0 <rayon::iter::plumbing::bridge_producer_consumer::helper::<rayon::iter::len::MaxLenProducer<rayon::slice::chunks::ChunksProducer<u8>>, rayon::iter::fold::FoldConsumer<rayon::iter::reduce::ReduceConsumer<<bench::workloads::histogram::Histogram>::merge, <bench::workloads::histogram::Histogram as core::default::Default>::default>, <bench::workloads::histogram::Histogram as core::default::Default>::default, bench::workloads::histogram::local::local_counts<rayon::iter::len::MaxLen<rayon::slice::chunks::Chunks<u8>>>::{closure#0}>>+0x110>
   2bc88:	mov    %r13,%rax
   2bc8b:	nopl   0x0(%rax,%rax,1)
   2bc90:	movzbl (%rax),%edx
   2bc93:	inc    %rax
   2bc96:	incq   0x48(%rsp,%rdx,8)
   2bc9b:	dec    %rcx
   2bc9e:	jne    2bc90 <rayon::iter::plumbing::bridge_producer_consumer::helper::<rayon::iter::len::MaxLenProducer<rayon::slice::chunks::ChunksProducer<u8>>, rayon::iter::fold::FoldConsumer<rayon::iter::reduce::ReduceConsumer<<bench::workloads::histogram::Histogram>::merge, <bench::workloads::histogram::Histogram as core::default::Default>::default>, <bench::workloads::histogram::Histogram as core::default::Default>::default, bench::workloads::histogram::local::local_counts<rayon::iter::len::MaxLen<rayon::slice::chunks::Chunks<u8>>>::{closure#0}>>+0x100>
   2bca0:	add    %r12,%r13
   2bca3:	cmp    $0x4,%r12
   2bca7:	jb     2bc40 <rayon::iter::plumbing::bridge_producer_consumer::helper::<rayon::iter::len::MaxLenProducer<rayon::slice::chunks::ChunksProducer<u8>>, rayon::iter::fold::FoldConsumer<rayon::iter::reduce::ReduceConsumer<<bench::workloads::histogram::Histogram>::merge, <bench::workloads::histogram::Histogram as core::default::Default>::default>, <bench::workloads::histogram::Histogram as core::default::Default>::default, bench::workloads::histogram::local::local_counts<rayon::iter::len::MaxLen<rayon::slice::chunks::Chunks<u8>>>::{closure#0}>>+0xb0>
   2bca9:	nopl   0x0(%rax)
   2bcb0:	movzbl (%rax),%ecx
   2bcb3:	incq   0x48(%rsp,%rcx,8)
   2bcb8:	movzbl 0x1(%rax),%ecx
   2bcbc:	incq   0x48(%rsp,%rcx,8)
   2bcc1:	movzbl 0x2(%rax),%ecx
   2bcc5:	incq   0x48(%rsp,%rcx,8)
   2bcca:	movzbl 0x3(%rax),%ecx
   2bcce:	incq   0x48(%rsp,%rcx,8)
   2bcd3:	add    $0x4,%rax
   2bcd7:	cmp    %r13,%rax
   2bcda:	jne    2bcb0 <rayon::iter::plumbing::bridge_producer_consumer::helper::<rayon::iter::len::MaxLenProducer<rayon::slice::chunks::ChunksProducer<u8>>, rayon::iter::fold::FoldConsumer<rayon::iter::reduce::ReduceConsumer<<bench::workloads::histogram::Histogram>::merge, <bench::workloads::histogram::Histogram as core::default::Default>::default>, <bench::workloads::histogram::Histogram as core::default::Default>::default, bench::workloads::histogram::local::local_counts<rayon::iter::len::MaxLen<rayon::slice::chunks::Chunks<u8>>>::{closure#0}>>+0x120>
   2bcdc:	jmp    2bc40 <rayon::iter::plumbing::bridge_producer_consumer::helper::<rayon::iter::len::MaxLenProducer<rayon::slice::chunks::ChunksProducer<u8>>, rayon::iter::fold::FoldConsumer<rayon::iter::reduce::ReduceConsumer<<bench::workloads::histogram::Histogram>::merge, <bench::workloads::histogram::Histogram as core::default::Default>::default>, <bench::workloads::histogram::Histogram as core::default::Default>::default, bench::workloads::histogram::local::local_counts<rayon::iter::len::MaxLen<rayon::slice::chunks::Chunks<u8>>>::{closure#0}>>+0xb0>
   2bce1:	lea    0x48(%rsp),%rdi
   2bce6:	xor    %ebx,%ebx
   2bce8:	mov    $0x800,%edx
   2bced:	xor    %esi,%esi
   2bcef:	call   *0x53653(%rip)        # 7f348 <memset@GLIBC_2.2.5>
   2bcf5:	lea    0x1068(%rsp),%rdi
   2bcfd:	lea    0x2878(%rsp),%r14
   2bd05:	mov    0x5358c(%rip),%r15        # 7f298 <memcpy@GLIBC_2.14>
   2bd0c:	mov    $0x800,%edx
   2bd11:	mov    %r14,%rsi
   2bd14:	call   *%r15
   2bd17:	lea    0x848(%rsp),%rdi
   2bd1f:	mov    $0x800,%edx
   2bd24:	mov    %r14,%rsi
   2bd27:	call   *%r15
   2bd2a:	pxor   %xmm0,%xmm0
   2bd2e:	movdqu %xmm0,0x1868(%rsp)
   2bd37:	nopw   0x0(%rax,%rax,1)
   2bd40:	movdqu 0x1068(%rsp,%rbx,8),%xmm0
   2bd49:	movdqu 0x1078(%rsp,%rbx,8),%xmm1
   2bd52:	movdqu 0x1088(%rsp,%rbx,8),%xmm2
   2bd5b:	movdqu 0x1098(%rsp,%rbx,8),%xmm3
   2bd64:	movdqu 0x48(%rsp,%rbx,8),%xmm4
   2bd6a:	paddq  %xmm0,%xmm4
   2bd6e:	movdqu 0x58(%rsp,%rbx,8),%xmm0
   2bd74:	paddq  %xmm1,%xmm0
   2bd78:	movdqu 0x68(%rsp,%rbx,8),%xmm1
   2bd7e:	paddq  %xmm2,%xmm1
   2bd82:	movdqu 0x78(%rsp,%rbx,8),%xmm2
   2bd88:	paddq  %xmm3,%xmm2
   2bd8c:	movdqu %xmm4,0x48(%rsp,%rbx,8)
   2bd92:	movdqu %xmm0,0x58(%rsp,%rbx,8)
   2bd98:	movdqu %xmm1,0x68(%rsp,%rbx,8)
   2bd9e:	movdqu %xmm2,0x78(%rsp,%rbx,8)
   2bda4:	add    $0x8,%rbx
   2bda8:	cmp    $0x100,%rbx
   2bdaf:	jne    2bd40 <rayon::iter::plumbing::bridge_producer_consumer::helper::<rayon::iter::len::MaxLenProducer<rayon::slice::chunks::ChunksProducer<u8>>, rayon::iter::fold::FoldConsumer<rayon::iter::reduce::ReduceConsumer<<bench::workloads::histogram::Histogram>::merge, <bench::workloads::histogram::Histogram as core::default::Default>::default>, <bench::workloads::histogram::Histogram as core::default::Default>::default, bench::workloads::histogram::local::local_counts<rayon::iter::len::MaxLen<rayon::slice::chunks::Chunks<u8>>>::{closure#0}>>+0x1b0>
   2bdb1:	lea    0x48(%rsp),%rsi
   2bdb6:	mov    $0x800,%edx
   2bdbb:	mov    0x8(%rsp),%rdi
   2bdc0:	jmp    2c0dd <rayon::iter::plumbing::bridge_producer_consumer::helper::<rayon::iter::len::MaxLenProducer<rayon::slice::chunks::ChunksProducer<u8>>, rayon::iter::fold::FoldConsumer<rayon::iter::reduce::ReduceConsumer<<bench::workloads::histogram::Histogram>::merge, <bench::workloads::histogram::Histogram as core::default::Default>::default>, <bench::workloads::histogram::Histogram as core::default::Default>::default, bench::workloads::histogram::local::local_counts<rayon::iter::len::MaxLen<rayon::slice::chunks::Chunks<u8>>>::{closure#0}>>+0x54d>
   2bdc5:	test   %dl,%dl
   2bdc7:	je     2bdef <rayon::iter::plumbing::bridge_producer_consumer::helper::<rayon::iter::len::MaxLenProducer<rayon::slice::chunks::ChunksProducer<u8>>, rayon::iter::fold::FoldConsumer<rayon::iter::reduce::ReduceConsumer<<bench::workloads::histogram::Histogram>::merge, <bench::workloads::histogram::Histogram as core::default::Default>::default>, <bench::workloads::histogram::Histogram as core::default::Default>::default, bench::workloads::histogram::local::local_counts<rayon::iter::len::MaxLen<rayon::slice::chunks::Chunks<u8>>>::{closure#0}>>+0x25f>
   2bdc9:	mov    %rdi,%r12
   2bdcc:	mov    %rsi,%rbx
   2bdcf:	mov    %r9,%r15
   2bdd2:	mov    %rcx,%r14
   2bdd5:	call   45ad0 <rayon_core::current_num_threads>
   2bdda:	mov    %r14,%rcx
   2bddd:	mov    %r15,%r9
   2bde0:	mov    %rbx,%rsi
   2bde3:	shr    $1,%rcx
   2bde6:	cmp    %rcx,%rax
   2bde9:	cmova  %rax,%rcx
   2bded:	jmp    2bdfe <rayon::iter::plumbing::bridge_producer_consumer::helper::<rayon::iter::len::MaxLenProducer<rayon::slice::chunks::ChunksProducer<u8>>, rayon::iter::fold::FoldConsumer<rayon::iter::reduce::ReduceConsumer<<bench::workloads::histogram::Histogram>::merge, <bench::workloads::histogram::Histogram as core::default::Default>::default>, <bench::workloads::histogram::Histogram as core::default::Default>::default, bench::workloads::histogram::local::local_counts<rayon::iter::len::MaxLen<rayon::slice::chunks::Chunks<u8>>>::{closure#0}>>+0x26e>
   2bdef:	test   %rcx,%rcx
   2bdf2:	je     2bbe1 <rayon::iter::plumbing::bridge_producer_consumer::helper::<rayon::iter::len::MaxLenProducer<rayon::slice::chunks::ChunksProducer<u8>>, rayon::iter::fold::FoldConsumer<rayon::iter::reduce::ReduceConsumer<<bench::workloads::histogram::Histogram>::merge, <bench::workloads::histogram::Histogram as core::default::Default>::default>, <bench::workloads::histogram::Histogram as core::default::Default>::default, bench::workloads::histogram::local::local_counts<rayon::iter::len::MaxLen<rayon::slice::chunks::Chunks<u8>>>::{closure#0}>>+0x51>
   2bdf8:	mov    %rdi,%r12
   2bdfb:	shr    $1,%rcx
   2bdfe:	mov    0x30b0(%rsp),%rdx
   2be06:	mov    %rcx,0x38(%rsp)
   2be0b:	mov    %rsi,0x20(%rsp)
   2be10:	mov    0x10(%r9),%rax
   2be14:	imul   %rax,%rsi
   2be18:	mov    (%r9),%rcx
   2be1b:	mov    0x8(%r9),%rdi
   2be1f:	cmp    %rdi,%rsi
   2be22:	cmovae %rdi,%rsi
   2be26:	lea    (%rcx,%rsi,1),%r8
   2be2a:	sub    %rsi,%rdi
   2be2d:	mov    0x18(%r9),%r9
   2be31:	mov    (%rdx),%r10
   2be34:	mov    0x8(%rdx),%r11
   2be38:	mov    0x10(%rdx),%rbx
   2be3c:	mov    0x18(%rdx),%rdx
   2be40:	lea    0x18(%rsp),%r14
   2be45:	mov    %r14,0x48(%rsp)
   2be4a:	lea    0x20(%rsp),%r14
   2be4f:	mov    %r14,0x50(%rsp)
   2be54:	lea    0x38(%rsp),%r15
   2be59:	mov    %r15,0x58(%rsp)
   2be5e:	mov    %r8,0x60(%rsp)
   2be63:	mov    %rdi,0x68(%rsp)
   2be68:	mov    %rax,0x70(%rsp)
   2be6d:	mov    %r9,0x78(%rsp)
   2be72:	mov    %r10,0x80(%rsp)
   2be7a:	mov    %r11,0x88(%rsp)
   2be82:	mov    %rbx,0x90(%rsp)
   2be8a:	mov    %rdx,0x98(%rsp)
   2be92:	mov    %r14,0xa0(%rsp)
   2be9a:	mov    %r15,0xa8(%rsp)
   2bea2:	mov    %rcx,0xb0(%rsp)
   2beaa:	mov    %rsi,0xb8(%rsp)
   2beb2:	mov    %rax,0xc0(%rsp)
   2beba:	mov    %r9,0xc8(%rsp)
   2bec2:	mov    %r10,0xd0(%rsp)
   2beca:	mov    %r11,0xd8(%rsp)
   2bed2:	mov    %rbx,0xe0(%rsp)
   2beda:	mov    %rdx,0xe8(%rsp)
   2bee2:	mov    %fs:0xffffffffffffffb0,%rdx
   2beeb:	test   %rdx,%rdx
   2beee:	jne    2bfed <rayon::iter::plumbing::bridge_producer_consumer::helper::<rayon::iter::len::MaxLenProducer<rayon::slice::chunks::ChunksProducer<u8>>, rayon::iter::fold::FoldConsumer<rayon::iter::reduce::ReduceConsumer<<bench::workloads::histogram::Histogram>::merge, <bench::workloads::histogram::Histogram as core::default::Default>::default>, <bench::workloads::histogram::Histogram as core::default::Default>::default, bench::workloads::histogram::local::local_counts<rayon::iter::len::MaxLen<rayon::slice::chunks::Chunks<u8>>>::{closure#0}>>+0x45d>
   2bef4:	movq   $0x0,0x1048(%rsp)
   2bf00:	mov    0x54602(%rip),%eax        # 80508 <rayon_core::registry::THE_REGISTRY_SET>
   2bf06:	test   %eax,%eax
   2bf08:	jne    2bf76 <rayon::iter::plumbing::bridge_producer_consumer::helper::<rayon::iter::len::MaxLenProducer<rayon::slice::chunks::ChunksProducer<u8>>, rayon::iter::fold::FoldConsumer<rayon::iter::reduce::ReduceConsumer<<bench::workloads::histogram::Histogram>::merge, <bench::workloads::histogram::Histogram as core::default::Default>::default>, <bench::workloads::histogram::Histogram as core::default::Default>::default, bench::workloads::histogram::local::local_counts<rayon::iter::len::MaxLen<rayon::slice::chunks::Chunks<u8>>>::{closure#0}>>+0x3e6>
   2bf0a:	mov    0x1048(%rsp),%rcx
   2bf12:	mov    0x1050(%rsp),%rax
   2bf1a:	cmp    $0xffffffffffffffff,%rcx
   2bf1e:	je     2bfc8 <rayon::iter::plumbing::bridge_producer_consumer::helper::<rayon::iter::len::MaxLenProducer<rayon::slice::chunks::ChunksProducer<u8>>, rayon::iter::fold::FoldConsumer<rayon::iter::reduce::ReduceConsumer<<bench::workloads::histogram::Histogram>::merge, <bench::workloads::histogram::Histogram as core::default::Default>::default>, <bench::workloads::histogram::Histogram as core::default::Default>::default, bench::workloads::histogram::local::local_counts<rayon::iter::len::MaxLen<rayon::slice::chunks::Chunks<u8>>>::{closure#0}>>+0x438>
   2bf24:	cmpq   $0x0,0x5503c(%rip)        # 80f68 <rayon_core::registry::THE_REGISTRY>
   2bf2c:	je     2c12b <rayon::iter::plumbing::bridge_producer_consumer::helper::<rayon::iter::len::MaxLenProducer<rayon::slice::chunks::ChunksProducer<u8>>, rayon::iter::fold::FoldConsumer<rayon::iter::reduce::ReduceConsumer<<bench::workloads::histogram::Histogram>::merge, <bench::workloads::histogram::Histogram as core::default::Default>::default>, <bench::workloads::histogram::Histogram as core::default::Default>::default, bench::workloads::histogram::local::local_counts<rayon::iter::len::MaxLen<rayon::slice::chunks::Chunks<u8>>>::{closure#0}>>+0x59b>
   2bf32:	lea    0x5502f(%rip),%rbx        # 80f68 <rayon_core::registry::THE_REGISTRY>
   2bf39:	cmp    $0x2,%rcx
   2bf3d:	jb     2bfcb <rayon::iter::plumbing::bridge_producer_consumer::helper::<rayon::iter::len::MaxLenProducer<rayon::slice::chunks::ChunksProducer<u8>>, rayon::iter::fold::FoldConsumer<rayon::iter::reduce::ReduceConsumer<<bench::workloads::histogram::Histogram>::merge, <bench::workloads::histogram::Histogram as core::default::Default>::default>, <bench::workloads::histogram::Histogram as core::default::Default>::default, bench::workloads::histogram::local::local_counts<rayon::iter::len::MaxLen<rayon::slice::chunks::Chunks<u8>>>::{closure#0}>>+0x43b>
   2bf43:	mov    %eax,%ecx
   2bf45:	and    $0x3,%ecx
   2bf48:	lea    -0x2(%rcx),%edx
   2bf4b:	cmp    $0x2,%edx
   2bf4e:	jb     2bfcb <rayon::iter::plumbing::bridge_producer_consumer::helper::<rayon::iter::len::MaxLenProducer<rayon::slice::chunks::ChunksProducer<u8>>, rayon::iter::fold::FoldConsumer<rayon::iter::reduce::ReduceConsumer<<bench::workloads::histogram::Histogram>::merge, <bench::workloads::histogram::Histogram as core::default::Default>::default>, <bench::workloads::histogram::Histogram as core::default::Default>::default, bench::workloads::histogram::local::local_counts<rayon::iter::len::MaxLen<rayon::slice::chunks::Chunks<u8>>>::{closure#0}>>+0x43b>
   2bf50:	test   %rcx,%rcx
   2bf53:	je     2bfcb <rayon::iter::plumbing::bridge_producer_consumer::helper::<rayon::iter::len::MaxLenProducer<rayon::slice::chunks::ChunksProducer<u8>>, rayon::iter::fold::FoldConsumer<rayon::iter::reduce::ReduceConsumer<<bench::workloads::histogram::Histogram>::merge, <bench::workloads::histogram::Histogram as core::default::Default>::default>, <bench::workloads::histogram::Histogram as core::default::Default>::default, bench::workloads::histogram::local::local_counts<rayon::iter::len::MaxLen<rayon::slice::chunks::Chunks<u8>>>::{closure#0}>>+0x43b>
   2bf55:	lea    -0x1(%rax),%rdi
   2bf59:	call   *0x17(%rax)
   2bf5c:	jmp    2bfcb <rayon::iter::plumbing::bridge_producer_consumer::helper::<rayon::iter::len::MaxLenProducer<rayon::slice::chunks::ChunksProducer<u8>>, rayon::iter::fold::FoldConsumer<rayon::iter::reduce::ReduceConsumer<<bench::workloads::histogram::Histogram>::merge, <bench::workloads::histogram::Histogram as core::default::Default>::default>, <bench::workloads::histogram::Histogram as core::default::Default>::default, bench::workloads::histogram::local::local_counts<rayon::iter::len::MaxLen<rayon::slice::chunks::Chunks<u8>>>::{closure#0}>>+0x43b>
   2bf5e:	lea    -0x22c56(%rip),%rdi        # 930f <__abi_tag+0x9013>
   2bf65:	lea    0x511a4(%rip),%rdx        # 7d110 <__frame_dummy_init_array_entry+0xaa0>
   2bf6c:	mov    $0x37,%esi
   2bf71:	call   36eb0 <core::panicking::panic_fmt>
   2bf76:	lea    0x1048(%rsp),%rax
   2bf7e:	mov    %rax,0x28(%rsp)
   2bf83:	lea    0x28(%rsp),%rax
   2bf88:	mov    %rax,0x30(%rsp)
   2bf8d:	lea    0x54574(%rip),%rdi        # 80508 <rayon_core::registry::THE_REGISTRY_SET>
   2bf94:	lea    0x519a5(%rip),%rcx        # 7d940 <__frame_dummy_init_array_entry+0x12d0>
   2bf9b:	lea    0x51ace(%rip),%r8        # 7da70 <__frame_dummy_init_array_entry+0x1400>
   2bfa2:	lea    0x30(%rsp),%rdx
   2bfa7:	xor    %esi,%esi
   2bfa9:	call   727b0 <<std::sys::sync::once::futex::Once>::call>
   2bfae:	mov    0x1048(%rsp),%rcx
   2bfb6:	mov    0x1050(%rsp),%rax
   2bfbe:	cmp    $0xffffffffffffffff,%rcx
   2bfc2:	jne    2bf24 <rayon::iter::plumbing::bridge_producer_consumer::helper::<rayon::iter::len::MaxLenProducer<rayon::slice::chunks::ChunksProducer<u8>>, rayon::iter::fold::FoldConsumer<rayon::iter::reduce::ReduceConsumer<<bench::workloads::histogram::Histogram>::merge, <bench::workloads::histogram::Histogram as core::default::Default>::default>, <bench::workloads::histogram::Histogram as core::default::Default>::default, bench::workloads::histogram::local::local_counts<rayon::iter::len::MaxLen<rayon::slice::chunks::Chunks<u8>>>::{closure#0}>>+0x394>
   2bfc8:	mov    %rax,%rbx
   2bfcb:	mov    (%rbx),%rsi
   2bfce:	mov    %fs:0xffffffffffffffb0,%rdx
   2bfd7:	test   %rdx,%rdx
   2bfda:	je     2c0f5 <rayon::iter::plumbing::bridge_producer_consumer::helper::<rayon::iter::len::MaxLenProducer<rayon::slice::chunks::ChunksProducer<u8>>, rayon::iter::fold::FoldConsumer<rayon::iter::reduce::ReduceConsumer<<bench::workloads::histogram::Histogram>::merge, <bench::workloads::histogram::Histogram as core::default::Default>::default>, <bench::workloads::histogram::Histogram as core::default::Default>::default, bench::workloads::histogram::local::local_counts<rayon::iter::len::MaxLen<rayon::slice::chunks::Chunks<u8>>>::{closure#0}>>+0x565>
   2bfe0:	cmp    %rsi,0x110(%rdx)
   2bfe7:	jne    2c110 <rayon::iter::plumbing::bridge_producer_consumer::helper::<rayon::iter::len::MaxLenProducer<rayon::slice::chunks::ChunksProducer<u8>>, rayon::iter::fold::FoldConsumer<rayon::iter::reduce::ReduceConsumer<<bench::workloads::histogram::Histogram>::merge, <bench::workloads::histogram::Histogram as core::default::Default>::default>, <bench::workloads::histogram::Histogram as core::default::Default>::default, bench::workloads::histogram::local::local_counts<rayon::iter::len::MaxLen<rayon::slice::chunks::Chunks<u8>>>::{closure#0}>>+0x580>
   2bfed:	lea    0x1878(%rsp),%rdi
   2bff5:	lea    0x48(%rsp),%rsi
   2bffa:	xor    %ecx,%ecx
   2bffc:	call   2c170 <rayon_core::join::join_context::<rayon::iter::plumbing::bridge_producer_consumer::helper<rayon::iter::len::MaxLenProducer<rayon::slice::chunks::ChunksProducer<u8>>, rayon::iter::fold::FoldConsumer<rayon::iter::reduce::ReduceConsumer<<bench::workloads::histogram::Histogram>::merge, <bench::workloads::histogram::Histogram as core::default::Default>::default>, <bench::workloads::histogram::Histogram as core::default::Default>::default, bench::workloads::histogram::local::local_counts<rayon::iter::len::MaxLen<rayon::slice::chunks::Chunks<u8>>>::{closure#0}>>::{closure#0}, rayon::iter::plumbing::bridge_producer_consumer::helper<rayon::iter::len::MaxLenProducer<rayon::slice::chunks::ChunksProducer<u8>>, rayon::iter::fold::FoldConsumer<rayon::iter::reduce::ReduceConsumer<<bench::workloads::histogram::Histogram>::merge, <bench::workloads::histogram::Histogram as core::default::Default>::default>, <bench::workloads::histogram::Histogram as core::default::Default>::default, bench::workloads::histogram::local::local_counts<rayon::iter::len::MaxLen<rayon::slice::chunks::Chunks<u8>>>::{closure#0}>>::{closure#1}, bench::workloads::histogram::Histogram, bench::workloads::histogram::Histogram>::{closure#0}>
   2c001:	lea    0x2078(%rsp),%r14
   2c009:	lea    0x48(%rsp),%rdi
   2c00e:	lea    0x1878(%rsp),%rsi
   2c016:	mov    0x5327b(%rip),%rbx        # 7f298 <memcpy@GLIBC_2.14>
   2c01d:	mov    $0x800,%edx
   2c022:	call   *%rbx
   2c024:	lea    0x848(%rsp),%rdi
   2c02c:	mov    $0x800,%edx
   2c031:	mov    %r14,%rsi
   2c034:	call   *%rbx
   2c036:	lea    0x1068(%rsp),%rdi
   2c03e:	mov    $0x800,%edx
   2c043:	mov    %r14,%rsi
   2c046:	call   *%rbx
   2c048:	pxor   %xmm0,%xmm0
   2c04c:	movdqu %xmm0,0x1868(%rsp)
   2c055:	xor    %eax,%eax
   2c057:	nopw   0x0(%rax,%rax,1)
   2c060:	movdqu 0x1068(%rsp,%rax,8),%xmm0
   2c069:	movdqu 0x1078(%rsp,%rax,8),%xmm1
   2c072:	movdqu 0x1088(%rsp,%rax,8),%xmm2
   2c07b:	movdqu 0x1098(%rsp,%rax,8),%xmm3
   2c084:	movdqu 0x48(%rsp,%rax,8),%xmm4
   2c08a:	paddq  %xmm0,%xmm4
   2c08e:	movdqu 0x58(%rsp,%rax,8),%xmm0
   2c094:	paddq  %xmm1,%xmm0
   2c098:	movdqu 0x68(%rsp,%rax,8),%xmm1
   2c09e:	paddq  %xmm2,%xmm1
   2c0a2:	movdqu 0x78(%rsp,%rax,8),%xmm2
   2c0a8:	paddq  %xmm3,%xmm2
   2c0ac:	movdqu %xmm4,0x48(%rsp,%rax,8)
   2c0b2:	movdqu %xmm0,0x58(%rsp,%rax,8)
   2c0b8:	movdqu %xmm1,0x68(%rsp,%rax,8)
   2c0be:	movdqu %xmm2,0x78(%rsp,%rax,8)
   2c0c4:	add    $0x8,%rax
   2c0c8:	cmp    $0x100,%rax
   2c0ce:	jne    2c060 <rayon::iter::plumbing::bridge_producer_consumer::helper::<rayon::iter::len::MaxLenProducer<rayon::slice::chunks::ChunksProducer<u8>>, rayon::iter::fold::FoldConsumer<rayon::iter::reduce::ReduceConsumer<<bench::workloads::histogram::Histogram>::merge, <bench::workloads::histogram::Histogram as core::default::Default>::default>, <bench::workloads::histogram::Histogram as core::default::Default>::default, bench::workloads::histogram::local::local_counts<rayon::iter::len::MaxLen<rayon::slice::chunks::Chunks<u8>>>::{closure#0}>>+0x4d0>
   2c0d0:	lea    0x48(%rsp),%rsi
   2c0d5:	mov    $0x800,%edx
   2c0da:	mov    %r12,%rdi
   2c0dd:	call   *0x531b5(%rip)        # 7f298 <memcpy@GLIBC_2.14>
   2c0e3:	add    $0x3078,%rsp
   2c0ea:	pop    %rbx
   2c0eb:	pop    %r12
   2c0ed:	pop    %r13
   2c0ef:	pop    %r14
   2c0f1:	pop    %r15
   2c0f3:	pop    %rbp
   2c0f4:	ret
   2c0f5:	sub    $0xffffffffffffff80,%rsi
   2c0f9:	lea    0x1878(%rsp),%rdi
   2c101:	lea    0x48(%rsp),%rdx
   2c106:	call   2c650 <<rayon_core::registry::Registry>::in_worker_cold::<rayon_core::join::join_context<rayon::iter::plumbing::bridge_producer_consumer::helper<rayon::iter::len::MaxLenProducer<rayon::slice::chunks::ChunksProducer<u8>>, rayon::iter::fold::FoldConsumer<rayon::iter::reduce::ReduceConsumer<<bench::workloads::histogram::Histogram>::merge, <bench::workloads::histogram::Histogram as core::default::Default>::default>, <bench::workloads::histogram::Histogram as core::default::Default>::default, bench::workloads::histogram::local::local_counts<rayon::iter::len::MaxLen<rayon::slice::chunks::Chunks<u8>>>::{closure#0}>>::{closure#0}, rayon::iter::plumbing::bridge_producer_consumer::helper<rayon::iter::len::MaxLenProducer<rayon::slice::chunks::ChunksProducer<u8>>, rayon::iter::fold::FoldConsumer<rayon::iter::reduce::ReduceConsumer<<bench::workloads::histogram::Histogram>::merge, <bench::workloads::histogram::Histogram as core::default::Default>::default>, <bench::workloads::histogram::Histogram as core::default::Default>::default, bench::workloads::histogram::local::local_counts<rayon::iter::len::MaxLen<rayon::slice::chunks::Chunks<u8>>>::{closure#0}>>::{closure#1}, bench::workloads::histogram::Histogram, bench::workloads::histogram::Histogram>::{closure#0}, (bench::workloads::histogram::Histogram, bench::workloads::histogram::Histogram)>>
   2c10b:	jmp    2c001 <rayon::iter::plumbing::bridge_producer_consumer::helper::<rayon::iter::len::MaxLenProducer<rayon::slice::chunks::ChunksProducer<u8>>, rayon::iter::fold::FoldConsumer<rayon::iter::reduce::ReduceConsumer<<bench::workloads::histogram::Histogram>::merge, <bench::workloads::histogram::Histogram as core::default::Default>::default>, <bench::workloads::histogram::Histogram as core::default::Default>::default, bench::workloads::histogram::local::local_counts<rayon::iter::len::MaxLen<rayon::slice::chunks::Chunks<u8>>>::{closure#0}>>+0x471>
   2c110:	sub    $0xffffffffffffff80,%rsi
   2c114:	lea    0x1878(%rsp),%rdi
   2c11c:	lea    0x48(%rsp),%rcx
   2c121:	call   2c740 <<rayon_core::registry::Registry>::in_worker_cross::<rayon_core::join::join_context<rayon::iter::plumbing::bridge_producer_consumer::helper<rayon::iter::len::MaxLenProducer<rayon::slice::chunks::ChunksProducer<u8>>, rayon::iter::fold::FoldConsumer<rayon::iter::reduce::ReduceConsumer<<bench::workloads::histogram::Histogram>::merge, <bench::workloads::histogram::Histogram as core::default::Default>::default>, <bench::workloads::histogram::Histogram as core::default::Default>::default, bench::workloads::histogram::local::local_counts<rayon::iter::len::MaxLen<rayon::slice::chunks::Chunks<u8>>>::{closure#0}>>::{closure#0}, rayon::iter::plumbing::bridge_producer_consumer::helper<rayon::iter::len::MaxLenProducer<rayon::slice::chunks::ChunksProducer<u8>>, rayon::iter::fold::FoldConsumer<rayon::iter::reduce::ReduceConsumer<<bench::workloads::histogram::Histogram>::merge, <bench::workloads::histogram::Histogram as core::default::Default>::default>, <bench::workloads::histogram::Histogram as core::default::Default>::default, bench::workloads::histogram::local::local_counts<rayon::iter::len::MaxLen<rayon::slice::chunks::Chunks<u8>>>::{closure#0}>>::{closure#1}, bench::workloads::histogram::Histogram, bench::workloads::histogram::Histogram>::{closure#0}, (bench::workloads::histogram::Histogram, bench::workloads::histogram::Histogram)>>
   2c126:	jmp    2c001 <rayon::iter::plumbing::bridge_producer_consumer::helper::<rayon::iter::len::MaxLenProducer<rayon::slice::chunks::ChunksProducer<u8>>, rayon::iter::fold::FoldConsumer<rayon::iter::reduce::ReduceConsumer<<bench::workloads::histogram::Histogram>::merge, <bench::workloads::histogram::Histogram as core::default::Default>::default>, <bench::workloads::histogram::Histogram as core::default::Default>::default, bench::workloads::histogram::local::local_counts<rayon::iter::len::MaxLen<rayon::slice::chunks::Chunks<u8>>>::{closure#0}>>+0x471>
   2c12b:	mov    %rcx,0x1048(%rsp)
   2c133:	mov    %rax,0x1050(%rsp)
   2c13b:	lea    -0x213a3(%rip),%rdi        # ad9f <core::unicode::unicode_data::cf::SHORT_OFFSET_RUNS+0x5f7>
   2c142:	lea    0x518d7(%rip),%rcx        # 7da20 <__frame_dummy_init_array_entry+0x13b0>
   2c149:	lea    0x519f8(%rip),%r8        # 7db48 <__frame_dummy_init_array_entry+0x14d8>
   2c150:	lea    0x1048(%rsp),%rdx
   2c158:	mov    $0x30,%esi
   2c15d:	call   39ba0 <core::result::unwrap_failed>
   2c162:	int3
   2c163:	int3
   2c164:	int3
   2c165:	int3
   2c166:	int3
   2c167:	int3
   2c168:	int3
   2c169:	int3
   2c16a:	int3
   2c16b:	int3
   2c16c:	int3
   2c16d:	int3
   2c16e:	int3
   2c16f:	int3
