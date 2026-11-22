movzbl (%r8),%r9d
shl    $0x7,%r9d
lock incq (%rsi,%r9,1)
movzbl 0x1(%r8),%r9d
shl    $0x7,%r9d
lock incq (%rsi,%r9,1)
movzbl 0x2(%r8),%r9d
shl    $0x7,%r9d
lock incq (%rsi,%r9,1)
movzbl 0x3(%r8),%r9d
shl    $0x7,%r9d
lock incq (%rsi,%r9,1)
movzbl 0x4(%r8),%r9d
shl    $0x7,%r9d
lock incq (%rsi,%r9,1)
movzbl 0x5(%r8),%r9d
shl    $0x7,%r9d
lock incq (%rsi,%r9,1)
movzbl 0x6(%r8),%r9d
shl    $0x7,%r9d
lock incq (%rsi,%r9,1)
movzbl 0x7(%r8),%r9d
add    $0x8,%r8
shl    $0x7,%r9d
lock incq (%rsi,%r9,1)
cmp    %rdx,%r8
jne    2d240 <rayon::iter::plumbing::bridge_producer_consumer::helper::<rayon::iter::len::MaxLenProducer<rayon::slice::chunks::ChunksProducer<u8>>, rayon::iter::for_each::ForEachConsumer<<bench::workloads::histogram::atomic::AtomicHistogram as bench::workloads::workload::Workload>::run::{closure#0}>>+0xa0>
