000000000002d1a0 <rayon::iter::plumbing::bridge_producer_consumer::helper::<rayon::iter::len::MaxLenProducer<rayon::slice::chunks::ChunksProducer<u8>>, rayon::iter::for_each::ForEachConsumer<<bench::workloads::histogram::atomic::AtomicHistogram as bench::workloads::workload::Workload>::run::{closure#0}>>>:
   2d1a0:	push   %r15
   2d1a2:	push   %r14
   2d1a4:	push   %r12
   2d1a6:	push   %rbx
   2d1a7:	sub    $0xb8,%rsp
   2d1ae:	mov    %rdi,0x10(%rsp)
   2d1b3:	mov    %rcx,0x38(%rsp)
   2d1b8:	shr    $1,%rdi
   2d1bb:	cmp    %rcx,%rdi
   2d1be:	jae    2d2bd <rayon::iter::plumbing::bridge_producer_consumer::helper::<rayon::iter::len::MaxLenProducer<rayon::slice::chunks::ChunksProducer<u8>>, rayon::iter::for_each::ForEachConsumer<<bench::workloads::histogram::atomic::AtomicHistogram as bench::workloads::workload::Workload>::run::{closure#0}>>+0x11d>
   2d1c4:	mov    0x10(%r8),%rax
   2d1c8:	test   %rax,%rax
   2d1cb:	je     2d3fe <rayon::iter::plumbing::bridge_producer_consumer::helper::<rayon::iter::len::MaxLenProducer<rayon::slice::chunks::ChunksProducer<u8>>, rayon::iter::for_each::ForEachConsumer<<bench::workloads::histogram::atomic::AtomicHistogram as bench::workloads::workload::Workload>::run::{closure#0}>>+0x25e>
   2d1d1:	mov    0x8(%r8),%rcx
   2d1d5:	test   %rcx,%rcx
   2d1d8:	je     2d485 <rayon::iter::plumbing::bridge_producer_consumer::helper::<rayon::iter::len::MaxLenProducer<rayon::slice::chunks::ChunksProducer<u8>>, rayon::iter::for_each::ForEachConsumer<<bench::workloads::histogram::atomic::AtomicHistogram as bench::workloads::workload::Workload>::run::{closure#0}>>+0x2e5>
   2d1de:	mov    (%r8),%rdx
   2d1e1:	mov    (%r9),%rsi
   2d1e4:	mov    (%rsi),%rsi
   2d1e7:	jmp    2d1f9 <rayon::iter::plumbing::bridge_producer_consumer::helper::<rayon::iter::len::MaxLenProducer<rayon::slice::chunks::ChunksProducer<u8>>, rayon::iter::for_each::ForEachConsumer<<bench::workloads::histogram::atomic::AtomicHistogram as bench::workloads::workload::Workload>::run::{closure#0}>>+0x59>
   2d1e9:	nopl   0x0(%rax)
   2d1f0:	sub    %rdi,%rcx
   2d1f3:	je     2d485 <rayon::iter::plumbing::bridge_producer_consumer::helper::<rayon::iter::len::MaxLenProducer<rayon::slice::chunks::ChunksProducer<u8>>, rayon::iter::for_each::ForEachConsumer<<bench::workloads::histogram::atomic::AtomicHistogram as bench::workloads::workload::Workload>::run::{closure#0}>>+0x2e5>
   2d1f9:	cmp    %rax,%rcx
   2d1fc:	mov    %rax,%rdi
   2d1ff:	cmovb  %rcx,%rdi
   2d203:	mov    %rdi,%r9
   2d206:	mov    %rdx,%r8
   2d209:	and    $0x7,%r9
   2d20d:	je     2d235 <rayon::iter::plumbing::bridge_producer_consumer::helper::<rayon::iter::len::MaxLenProducer<rayon::slice::chunks::ChunksProducer<u8>>, rayon::iter::for_each::ForEachConsumer<<bench::workloads::histogram::atomic::AtomicHistogram as bench::workloads::workload::Workload>::run::{closure#0}>>+0x95>
   2d20f:	mov    %rdx,%r8
   2d212:	data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
   2d220:	movzbl (%r8),%r10d
   2d224:	inc    %r8
   2d227:	shl    $0x7,%r10d
   2d22b:	lock incq (%rsi,%r10,1)
   2d230:	dec    %r9
   2d233:	jne    2d220 <rayon::iter::plumbing::bridge_producer_consumer::helper::<rayon::iter::len::MaxLenProducer<rayon::slice::chunks::ChunksProducer<u8>>, rayon::iter::for_each::ForEachConsumer<<bench::workloads::histogram::atomic::AtomicHistogram as bench::workloads::workload::Workload>::run::{closure#0}>>+0x80>
   2d235:	add    %rdi,%rdx
   2d238:	cmp    $0x8,%rdi
   2d23c:	jb     2d1f0 <rayon::iter::plumbing::bridge_producer_consumer::helper::<rayon::iter::len::MaxLenProducer<rayon::slice::chunks::ChunksProducer<u8>>, rayon::iter::for_each::ForEachConsumer<<bench::workloads::histogram::atomic::AtomicHistogram as bench::workloads::workload::Workload>::run::{closure#0}>>+0x50>
   2d23e:	xchg   %ax,%ax
   2d240:	movzbl (%r8),%r9d
   2d244:	shl    $0x7,%r9d
   2d248:	lock incq (%rsi,%r9,1)
   2d24d:	movzbl 0x1(%r8),%r9d
   2d252:	shl    $0x7,%r9d
   2d256:	lock incq (%rsi,%r9,1)
   2d25b:	movzbl 0x2(%r8),%r9d
   2d260:	shl    $0x7,%r9d
   2d264:	lock incq (%rsi,%r9,1)
   2d269:	movzbl 0x3(%r8),%r9d
   2d26e:	shl    $0x7,%r9d
   2d272:	lock incq (%rsi,%r9,1)
   2d277:	movzbl 0x4(%r8),%r9d
   2d27c:	shl    $0x7,%r9d
   2d280:	lock incq (%rsi,%r9,1)
   2d285:	movzbl 0x5(%r8),%r9d
   2d28a:	shl    $0x7,%r9d
   2d28e:	lock incq (%rsi,%r9,1)
   2d293:	movzbl 0x6(%r8),%r9d
   2d298:	shl    $0x7,%r9d
   2d29c:	lock incq (%rsi,%r9,1)
   2d2a1:	movzbl 0x7(%r8),%r9d
   2d2a6:	add    $0x8,%r8
   2d2aa:	shl    $0x7,%r9d
   2d2ae:	lock incq (%rsi,%r9,1)
   2d2b3:	cmp    %rdx,%r8
   2d2b6:	jne    2d240 <rayon::iter::plumbing::bridge_producer_consumer::helper::<rayon::iter::len::MaxLenProducer<rayon::slice::chunks::ChunksProducer<u8>>, rayon::iter::for_each::ForEachConsumer<<bench::workloads::histogram::atomic::AtomicHistogram as bench::workloads::workload::Workload>::run::{closure#0}>>+0xa0>
   2d2b8:	jmp    2d1f0 <rayon::iter::plumbing::bridge_producer_consumer::helper::<rayon::iter::len::MaxLenProducer<rayon::slice::chunks::ChunksProducer<u8>>, rayon::iter::for_each::ForEachConsumer<<bench::workloads::histogram::atomic::AtomicHistogram as bench::workloads::workload::Workload>::run::{closure#0}>>+0x50>
   2d2bd:	test   %sil,%sil
   2d2c0:	je     2d2eb <rayon::iter::plumbing::bridge_producer_consumer::helper::<rayon::iter::len::MaxLenProducer<rayon::slice::chunks::ChunksProducer<u8>>, rayon::iter::for_each::ForEachConsumer<<bench::workloads::histogram::atomic::AtomicHistogram as bench::workloads::workload::Workload>::run::{closure#0}>>+0x14b>
   2d2c2:	mov    %r9,%rbx
   2d2c5:	mov    %r8,%r15
   2d2c8:	mov    %rdi,%r14
   2d2cb:	mov    %rdx,%r12
   2d2ce:	call   45ad0 <rayon_core::current_num_threads>
   2d2d3:	mov    %r12,%rdx
   2d2d6:	mov    %r14,%rdi
   2d2d9:	mov    %r15,%r8
   2d2dc:	mov    %rbx,%r9
   2d2df:	shr    $1,%rdx
   2d2e2:	cmp    %rdx,%rax
   2d2e5:	cmova  %rax,%rdx
   2d2e9:	jmp    2d2f7 <rayon::iter::plumbing::bridge_producer_consumer::helper::<rayon::iter::len::MaxLenProducer<rayon::slice::chunks::ChunksProducer<u8>>, rayon::iter::for_each::ForEachConsumer<<bench::workloads::histogram::atomic::AtomicHistogram as bench::workloads::workload::Workload>::run::{closure#0}>>+0x157>
   2d2eb:	test   %rdx,%rdx
   2d2ee:	je     2d1c4 <rayon::iter::plumbing::bridge_producer_consumer::helper::<rayon::iter::len::MaxLenProducer<rayon::slice::chunks::ChunksProducer<u8>>, rayon::iter::for_each::ForEachConsumer<<bench::workloads::histogram::atomic::AtomicHistogram as bench::workloads::workload::Workload>::run::{closure#0}>>+0x24>
   2d2f4:	shr    $1,%rdx
   2d2f7:	mov    %rdx,0x30(%rsp)
   2d2fc:	mov    %rdi,0x18(%rsp)
   2d301:	mov    0x10(%r8),%rax
   2d305:	imul   %rax,%rdi
   2d309:	mov    0x8(%r8),%rcx
   2d30d:	cmp    %rcx,%rdi
   2d310:	cmovae %rcx,%rdi
   2d314:	mov    (%r8),%rdx
   2d317:	lea    (%rdx,%rdi,1),%rsi
   2d31b:	sub    %rdi,%rcx
   2d31e:	mov    0x18(%r8),%r8
   2d322:	lea    0x10(%rsp),%r10
   2d327:	mov    %r10,0x40(%rsp)
   2d32c:	lea    0x18(%rsp),%r10
   2d331:	mov    %r10,0x48(%rsp)
   2d336:	lea    0x30(%rsp),%r11
   2d33b:	mov    %r11,0x50(%rsp)
   2d340:	mov    %rsi,0x58(%rsp)
   2d345:	mov    %rcx,0x60(%rsp)
   2d34a:	mov    %rax,0x68(%rsp)
   2d34f:	mov    %r8,0x70(%rsp)
   2d354:	mov    %r9,0x78(%rsp)
   2d359:	mov    %r10,0x80(%rsp)
   2d361:	mov    %r11,0x88(%rsp)
   2d369:	mov    %rdx,0x90(%rsp)
   2d371:	mov    %rdi,0x98(%rsp)
   2d379:	mov    %rax,0xa0(%rsp)
   2d381:	mov    %r8,0xa8(%rsp)
   2d389:	mov    %r9,0xb0(%rsp)
   2d391:	mov    %fs:0xffffffffffffffb0,%rsi
   2d39a:	test   %rsi,%rsi
   2d39d:	jne    2d479 <rayon::iter::plumbing::bridge_producer_consumer::helper::<rayon::iter::len::MaxLenProducer<rayon::slice::chunks::ChunksProducer<u8>>, rayon::iter::for_each::ForEachConsumer<<bench::workloads::histogram::atomic::AtomicHistogram as bench::workloads::workload::Workload>::run::{closure#0}>>+0x2d9>
   2d3a3:	movq   $0x0,(%rsp)
   2d3ab:	mov    0x53157(%rip),%eax        # 80508 <rayon_core::registry::THE_REGISTRY_SET>
   2d3b1:	test   %eax,%eax
   2d3b3:	jne    2d416 <rayon::iter::plumbing::bridge_producer_consumer::helper::<rayon::iter::len::MaxLenProducer<rayon::slice::chunks::ChunksProducer<u8>>, rayon::iter::for_each::ForEachConsumer<<bench::workloads::histogram::atomic::AtomicHistogram as bench::workloads::workload::Workload>::run::{closure#0}>>+0x276>
   2d3b5:	mov    (%rsp),%rcx
   2d3b9:	mov    0x8(%rsp),%rax
   2d3be:	cmp    $0xffffffffffffffff,%rcx
   2d3c2:	je     2d45c <rayon::iter::plumbing::bridge_producer_consumer::helper::<rayon::iter::len::MaxLenProducer<rayon::slice::chunks::ChunksProducer<u8>>, rayon::iter::for_each::ForEachConsumer<<bench::workloads::histogram::atomic::AtomicHistogram as bench::workloads::workload::Workload>::run::{closure#0}>>+0x2bc>
   2d3c8:	cmpq   $0x0,0x53b98(%rip)        # 80f68 <rayon_core::registry::THE_REGISTRY>
   2d3d0:	je     2d4b4 <rayon::iter::plumbing::bridge_producer_consumer::helper::<rayon::iter::len::MaxLenProducer<rayon::slice::chunks::ChunksProducer<u8>>, rayon::iter::for_each::ForEachConsumer<<bench::workloads::histogram::atomic::AtomicHistogram as bench::workloads::workload::Workload>::run::{closure#0}>>+0x314>
   2d3d6:	lea    0x53b8b(%rip),%rbx        # 80f68 <rayon_core::registry::THE_REGISTRY>
   2d3dd:	cmp    $0x2,%rcx
   2d3e1:	jb     2d45f <rayon::iter::plumbing::bridge_producer_consumer::helper::<rayon::iter::len::MaxLenProducer<rayon::slice::chunks::ChunksProducer<u8>>, rayon::iter::for_each::ForEachConsumer<<bench::workloads::histogram::atomic::AtomicHistogram as bench::workloads::workload::Workload>::run::{closure#0}>>+0x2bf>
   2d3e3:	mov    %eax,%ecx
   2d3e5:	and    $0x3,%ecx
   2d3e8:	lea    -0x2(%rcx),%edx
   2d3eb:	cmp    $0x2,%edx
   2d3ee:	jb     2d45f <rayon::iter::plumbing::bridge_producer_consumer::helper::<rayon::iter::len::MaxLenProducer<rayon::slice::chunks::ChunksProducer<u8>>, rayon::iter::for_each::ForEachConsumer<<bench::workloads::histogram::atomic::AtomicHistogram as bench::workloads::workload::Workload>::run::{closure#0}>>+0x2bf>
   2d3f0:	test   %rcx,%rcx
   2d3f3:	je     2d45f <rayon::iter::plumbing::bridge_producer_consumer::helper::<rayon::iter::len::MaxLenProducer<rayon::slice::chunks::ChunksProducer<u8>>, rayon::iter::for_each::ForEachConsumer<<bench::workloads::histogram::atomic::AtomicHistogram as bench::workloads::workload::Workload>::run::{closure#0}>>+0x2bf>
   2d3f5:	lea    -0x1(%rax),%rdi
   2d3f9:	call   *0x17(%rax)
   2d3fc:	jmp    2d45f <rayon::iter::plumbing::bridge_producer_consumer::helper::<rayon::iter::len::MaxLenProducer<rayon::slice::chunks::ChunksProducer<u8>>, rayon::iter::for_each::ForEachConsumer<<bench::workloads::histogram::atomic::AtomicHistogram as bench::workloads::workload::Workload>::run::{closure#0}>>+0x2bf>
   2d3fe:	lea    -0x240f6(%rip),%rdi        # 930f <__abi_tag+0x9013>
   2d405:	lea    0x4fd04(%rip),%rdx        # 7d110 <__frame_dummy_init_array_entry+0xaa0>
   2d40c:	mov    $0x37,%esi
   2d411:	call   36eb0 <core::panicking::panic_fmt>
   2d416:	mov    %rsp,%rax
   2d419:	mov    %rax,0x20(%rsp)
   2d41e:	lea    0x20(%rsp),%rax
   2d423:	mov    %rax,0x28(%rsp)
   2d428:	lea    0x530d9(%rip),%rdi        # 80508 <rayon_core::registry::THE_REGISTRY_SET>
   2d42f:	lea    0x5050a(%rip),%rcx        # 7d940 <__frame_dummy_init_array_entry+0x12d0>
   2d436:	lea    0x50633(%rip),%r8        # 7da70 <__frame_dummy_init_array_entry+0x1400>
   2d43d:	lea    0x28(%rsp),%rdx
   2d442:	xor    %esi,%esi
   2d444:	call   727b0 <<std::sys::sync::once::futex::Once>::call>
   2d449:	mov    (%rsp),%rcx
   2d44d:	mov    0x8(%rsp),%rax
   2d452:	cmp    $0xffffffffffffffff,%rcx
   2d456:	jne    2d3c8 <rayon::iter::plumbing::bridge_producer_consumer::helper::<rayon::iter::len::MaxLenProducer<rayon::slice::chunks::ChunksProducer<u8>>, rayon::iter::for_each::ForEachConsumer<<bench::workloads::histogram::atomic::AtomicHistogram as bench::workloads::workload::Workload>::run::{closure#0}>>+0x228>
   2d45c:	mov    %rax,%rbx
   2d45f:	mov    (%rbx),%rdi
   2d462:	mov    %fs:0xffffffffffffffb0,%rsi
   2d46b:	test   %rsi,%rsi
   2d46e:	je     2d494 <rayon::iter::plumbing::bridge_producer_consumer::helper::<rayon::iter::len::MaxLenProducer<rayon::slice::chunks::ChunksProducer<u8>>, rayon::iter::for_each::ForEachConsumer<<bench::workloads::histogram::atomic::AtomicHistogram as bench::workloads::workload::Workload>::run::{closure#0}>>+0x2f4>
   2d470:	cmp    %rdi,0x110(%rsi)
   2d477:	jne    2d4a4 <rayon::iter::plumbing::bridge_producer_consumer::helper::<rayon::iter::len::MaxLenProducer<rayon::slice::chunks::ChunksProducer<u8>>, rayon::iter::for_each::ForEachConsumer<<bench::workloads::histogram::atomic::AtomicHistogram as bench::workloads::workload::Workload>::run::{closure#0}>>+0x304>
   2d479:	lea    0x40(%rsp),%rdi
   2d47e:	xor    %edx,%edx
   2d480:	call   2d4e0 <rayon_core::join::join_context::<rayon::iter::plumbing::bridge_producer_consumer::helper<rayon::iter::len::MaxLenProducer<rayon::slice::chunks::ChunksProducer<u8>>, rayon::iter::for_each::ForEachConsumer<<bench::workloads::histogram::atomic::AtomicHistogram as bench::workloads::workload::Workload>::run::{closure#0}>>::{closure#0}, rayon::iter::plumbing::bridge_producer_consumer::helper<rayon::iter::len::MaxLenProducer<rayon::slice::chunks::ChunksProducer<u8>>, rayon::iter::for_each::ForEachConsumer<<bench::workloads::histogram::atomic::AtomicHistogram as bench::workloads::workload::Workload>::run::{closure#0}>>::{closure#1}, (), ()>::{closure#0}>
   2d485:	add    $0xb8,%rsp
   2d48c:	pop    %rbx
   2d48d:	pop    %r12
   2d48f:	pop    %r14
   2d491:	pop    %r15
   2d493:	ret
   2d494:	sub    $0xffffffffffffff80,%rdi
   2d498:	lea    0x40(%rsp),%rsi
   2d49d:	call   2d7e0 <<rayon_core::registry::Registry>::in_worker_cold::<rayon_core::join::join_context<rayon::iter::plumbing::bridge_producer_consumer::helper<rayon::iter::len::MaxLenProducer<rayon::slice::chunks::ChunksProducer<u8>>, rayon::iter::for_each::ForEachConsumer<<bench::workloads::histogram::atomic::AtomicHistogram as bench::workloads::workload::Workload>::run::{closure#0}>>::{closure#0}, rayon::iter::plumbing::bridge_producer_consumer::helper<rayon::iter::len::MaxLenProducer<rayon::slice::chunks::ChunksProducer<u8>>, rayon::iter::for_each::ForEachConsumer<<bench::workloads::histogram::atomic::AtomicHistogram as bench::workloads::workload::Workload>::run::{closure#0}>>::{closure#1}, (), ()>::{closure#0}, ((), ())>>
   2d4a2:	jmp    2d485 <rayon::iter::plumbing::bridge_producer_consumer::helper::<rayon::iter::len::MaxLenProducer<rayon::slice::chunks::ChunksProducer<u8>>, rayon::iter::for_each::ForEachConsumer<<bench::workloads::histogram::atomic::AtomicHistogram as bench::workloads::workload::Workload>::run::{closure#0}>>+0x2e5>
   2d4a4:	sub    $0xffffffffffffff80,%rdi
   2d4a8:	lea    0x40(%rsp),%rdx
   2d4ad:	call   2d8b0 <<rayon_core::registry::Registry>::in_worker_cross::<rayon_core::join::join_context<rayon::iter::plumbing::bridge_producer_consumer::helper<rayon::iter::len::MaxLenProducer<rayon::slice::chunks::ChunksProducer<u8>>, rayon::iter::for_each::ForEachConsumer<<bench::workloads::histogram::atomic::AtomicHistogram as bench::workloads::workload::Workload>::run::{closure#0}>>::{closure#0}, rayon::iter::plumbing::bridge_producer_consumer::helper<rayon::iter::len::MaxLenProducer<rayon::slice::chunks::ChunksProducer<u8>>, rayon::iter::for_each::ForEachConsumer<<bench::workloads::histogram::atomic::AtomicHistogram as bench::workloads::workload::Workload>::run::{closure#0}>>::{closure#1}, (), ()>::{closure#0}, ((), ())>>
   2d4b2:	jmp    2d485 <rayon::iter::plumbing::bridge_producer_consumer::helper::<rayon::iter::len::MaxLenProducer<rayon::slice::chunks::ChunksProducer<u8>>, rayon::iter::for_each::ForEachConsumer<<bench::workloads::histogram::atomic::AtomicHistogram as bench::workloads::workload::Workload>::run::{closure#0}>>+0x2e5>
   2d4b4:	mov    %rcx,(%rsp)
   2d4b8:	mov    %rax,0x8(%rsp)
   2d4bd:	lea    -0x22725(%rip),%rdi        # ad9f <core::unicode::unicode_data::cf::SHORT_OFFSET_RUNS+0x5f7>
   2d4c4:	lea    0x50555(%rip),%rcx        # 7da20 <__frame_dummy_init_array_entry+0x13b0>
   2d4cb:	lea    0x50676(%rip),%r8        # 7db48 <__frame_dummy_init_array_entry+0x14d8>
   2d4d2:	mov    %rsp,%rdx
   2d4d5:	mov    $0x30,%esi
   2d4da:	call   39ba0 <core::result::unwrap_failed>
   2d4df:	int3
