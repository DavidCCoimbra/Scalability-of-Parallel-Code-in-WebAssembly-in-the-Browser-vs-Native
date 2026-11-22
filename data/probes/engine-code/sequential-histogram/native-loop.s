movzbl (%rcx),%edx
incq   (%rsp,%rdx,8)
movzbl 0x1(%rcx),%edx
incq   (%rsp,%rdx,8)
movzbl 0x2(%rcx),%edx
incq   (%rsp,%rdx,8)
movzbl 0x3(%rcx),%edx
incq   (%rsp,%rdx,8)
add    $0x4,%rcx
cmp    %rax,%rcx
jne    2af30 <<bench::workloads::histogram::sequential::SequentialHistogram as bench::workloads::workload::Workload>::run+0x60>
