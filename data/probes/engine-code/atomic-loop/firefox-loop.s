# 20040 samples in SpiderMonkey's code, 20034 on the start of an instruction of this listing
    +0     128  cmpl   $0x0,0x38(%r14)
    +5       0  jne    0xe646da21fb8
    +b       0  movzbl (%r15,%rdi,1),%r8d
   +10       8  shl    $0x7,%r8d
   +14     133  add    %ebx,%r8d
   +17       0  test   $0x7,%r8b
   +1b       0  jne    0xe646da21fbf
   +21       0  mov    $0x1,%r9d
   +27       0  lock add %r9,(%r15,%r8,1)
   +2c    2232  lea    0x1(%rdi),%r8d
   +30       0  movzbl (%r15,%r8,1),%r8d
   +35     129  shl    $0x7,%r8d
   +39       0  add    %ebx,%r8d
   +3c       0  test   $0x7,%r8b
   +40       0  jne    0xe646da21fc1
   +46     130  mov    $0x1,%r9d
   +4c       0  lock add %r9,(%r15,%r8,1)
   +51    2188  lea    0x2(%rdi),%r8d
   +55       0  movzbl (%r15,%r8,1),%r8d
   +5a     144  shl    $0x7,%r8d
   +5e       0  add    %ebx,%r8d
   +61       0  test   $0x7,%r8b
   +65       0  jne    0xe646da21fc3
   +6b     124  mov    $0x1,%r9d
   +71       0  lock add %r9,(%r15,%r8,1)
   +76    2304  lea    0x3(%rdi),%r8d
   +7a       0  movzbl (%r15,%r8,1),%r8d
   +7f     123  shl    $0x7,%r8d
   +83       0  add    %ebx,%r8d
   +86       0  test   $0x7,%r8b
   +8a       0  jne    0xe646da21fc5
   +90     131  mov    $0x1,%r9d
   +96       0  lock add %r9,(%r15,%r8,1)
   +9b    2201  lea    0x4(%rdi),%r8d
   +9f       0  movzbl (%r15,%r8,1),%r8d
   +a4     126  shl    $0x7,%r8d
   +a8       0  add    %ebx,%r8d
   +ab       0  test   $0x7,%r8b
   +af       0  jne    0xe646da21fc7
   +b5     128  mov    $0x1,%r9d
   +bb       0  lock add %r9,(%r15,%r8,1)
   +c0    2233  lea    0x5(%rdi),%r8d
   +c4       0  movzbl (%r15,%r8,1),%r8d
   +c9     122  shl    $0x7,%r8d
   +cd       0  add    %ebx,%r8d
   +d0       0  test   $0x7,%r8b
   +d4       0  jne    0xe646da21fc9
   +da     138  mov    $0x1,%r9d
   +e0       0  lock add %r9,(%r15,%r8,1)
   +e5    2308  lea    0x6(%rdi),%r8d
   +e9       0  movzbl (%r15,%r8,1),%r8d
   +ee     120  shl    $0x7,%r8d
   +f2       0  add    %ebx,%r8d
   +f5       1  test   $0x7,%r8b
   +f9       0  jne    0xe646da21fcb
   +ff     137  mov    $0x1,%r9d
  +105       0  lock add %r9,(%r15,%r8,1)
  +10a    2225  lea    0x7(%rdi),%r8d
  +10e       0  movzbl (%r15,%r8,1),%r8d
  +113     144  shl    $0x7,%r8d
  +117       0  add    %ebx,%r8d
  +11a       0  test   $0x7,%r8b
  +11e       0  jne    0xe646da21fcd
  +124     139  mov    $0x1,%r9d
  +12a       0  lock add %r9,(%r15,%r8,1)
  +12f    2238  add    $0x8,%edi
  +132       0  cmp    %edx,%edi
  +134       0  jne    0xe646da21c50
