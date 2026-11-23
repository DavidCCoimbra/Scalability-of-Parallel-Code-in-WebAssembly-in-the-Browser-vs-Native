# 20034 samples in SpiderMonkey's code, 20032 on an instruction start of the disassembly; 20032 in this loop of 68 instructions (columns: offset, samples, instruction)
    +0     127  cmpl   $0x0,0x38(%r14)
    +5       0  jne    0xd48225f3fb8
    +b       0  movzbl (%r15,%rdi,1),%r8d
   +10       3  shl    $0x7,%r8d
   +14     123  add    %ebx,%r8d
   +17       0  test   $0x7,%r8b
   +1b       0  jne    0xd48225f3fbf
   +21       0  mov    $0x1,%r9d
   +27       0  lock add %r9,(%r15,%r8,1)
   +2c    2306  lea    0x1(%rdi),%r8d
   +30       0  movzbl (%r15,%r8,1),%r8d
   +35     121  shl    $0x7,%r8d
   +39       0  add    %ebx,%r8d
   +3c       0  test   $0x7,%r8b
   +40       0  jne    0xd48225f3fc1
   +46     116  mov    $0x1,%r9d
   +4c       0  lock add %r9,(%r15,%r8,1)
   +51    2176  lea    0x2(%rdi),%r8d
   +55       0  movzbl (%r15,%r8,1),%r8d
   +5a     124  shl    $0x7,%r8d
   +5e       0  add    %ebx,%r8d
   +61       0  test   $0x7,%r8b
   +65       0  jne    0xd48225f3fc3
   +6b     117  mov    $0x1,%r9d
   +71       0  lock add %r9,(%r15,%r8,1)
   +76    2248  lea    0x3(%rdi),%r8d
   +7a       0  movzbl (%r15,%r8,1),%r8d
   +7f     119  shl    $0x7,%r8d
   +83       0  add    %ebx,%r8d
   +86       0  test   $0x7,%r8b
   +8a       0  jne    0xd48225f3fc5
   +90     155  mov    $0x1,%r9d
   +96       0  lock add %r9,(%r15,%r8,1)
   +9b    2235  lea    0x4(%rdi),%r8d
   +9f       0  movzbl (%r15,%r8,1),%r8d
   +a4     146  shl    $0x7,%r8d
   +a8       0  add    %ebx,%r8d
   +ab       0  test   $0x7,%r8b
   +af       0  jne    0xd48225f3fc7
   +b5     144  mov    $0x1,%r9d
   +bb       0  lock add %r9,(%r15,%r8,1)
   +c0    2242  lea    0x5(%rdi),%r8d
   +c4       0  movzbl (%r15,%r8,1),%r8d
   +c9     151  shl    $0x7,%r8d
   +cd       0  add    %ebx,%r8d
   +d0       0  test   $0x7,%r8b
   +d4       0  jne    0xd48225f3fc9
   +da     139  mov    $0x1,%r9d
   +e0       0  lock add %r9,(%r15,%r8,1)
   +e5    2224  lea    0x6(%rdi),%r8d
   +e9       0  movzbl (%r15,%r8,1),%r8d
   +ee     144  shl    $0x7,%r8d
   +f2       0  add    %ebx,%r8d
   +f5       0  test   $0x7,%r8b
   +f9       0  jne    0xd48225f3fcb
   +ff     138  mov    $0x1,%r9d
  +105       0  lock add %r9,(%r15,%r8,1)
  +10a    2282  lea    0x7(%rdi),%r8d
  +10e       0  movzbl (%r15,%r8,1),%r8d
  +113     150  shl    $0x7,%r8d
  +117       0  add    %ebx,%r8d
  +11a       0  test   $0x7,%r8b
  +11e       0  jne    0xd48225f3fcd
  +124     139  mov    $0x1,%r9d
  +12a       0  lock add %r9,(%r15,%r8,1)
  +12f    2163  add    $0x8,%edi
  +132       0  cmp    %edx,%edi
  +134       0  jne    0xd48225f3c50
