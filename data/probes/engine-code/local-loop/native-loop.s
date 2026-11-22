movzbl (%rax),%ecx
incq   0x48(%rsp,%rcx,8)
movzbl 0x1(%rax),%ecx
incq   0x48(%rsp,%rcx,8)
movzbl 0x2(%rax),%ecx
incq   0x48(%rsp,%rcx,8)
movzbl 0x3(%rax),%ecx
incq   0x48(%rsp,%rcx,8)
add    $0x4,%rax
cmp    %r13,%rax
jne    2bcb0 <rayon::iter::plumbing::bridge_producer_consumer::helper::<rayon::iter::len::MaxLenProducer<rayon::slice::chunks::ChunksProducer<u8>>, rayon::iter::fold::FoldConsumer<rayon::iter::reduce::ReduceConsumer<<bench::workloads::histogram::Histogram>::merge, <bench::workloads::histogram::Histogram as core::default::Default>::default>, <bench::workloads::histogram::Histogram as core::default::Default>::default, bench::workloads::histogram::local::local_counts<rayon::iter::len::MaxLen<rayon::slice::chunks::Chunks<u8>>>::{closure#0}>>+0x120>
