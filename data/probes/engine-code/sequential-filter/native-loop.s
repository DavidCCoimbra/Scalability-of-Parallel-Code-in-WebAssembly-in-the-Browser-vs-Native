lea    0x51c2f(%rip),%rcx        # 7cf48 <__frame_dummy_init_array_entry+0x8d8>
mov    %r11,%rdi
call   383a0 <core::slice::index::slice_index_fail>
lea    -0x22019(%rip),%rdi        # 930f <__abi_tag+0x9013>
lea    0x51eb9(%rip),%rdx        # 7d1e8 <__frame_dummy_init_array_entry+0xb78>
mov    $0x37,%esi
call   36eb0 <core::panicking::panic_fmt>
cmpq   $0x0,0x10(%rsp)
setne  %al
cmp    %rdx,%r11
seta   %cl
mov    %r11,%rsi
test   %cl,%al
jne    2b312 <<bench::workloads::gaussian::sequential::SequentialBlur as bench::workloads::workload::Workload>::run+0x292>
