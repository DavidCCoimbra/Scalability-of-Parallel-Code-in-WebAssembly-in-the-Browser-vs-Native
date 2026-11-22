023098 func[185] <<bench[c9b452c63323ae17]::workloads::histogram::sequential::SequentialHistogram as bench[c9b452c63323ae17]::workloads::workload::Workload>::run>:
 023099: 06 7f                      | local[1..6] type=i32
 02309b: 23 00                      | global.get 0 <__stack_pointer>
 02309d: 41 80 10                   | i32.const 2048
 0230a0: 6b                         | i32.sub
 0230a1: 22 01                      | local.tee 1
 0230a3: 24 00                      | global.set 0 <__stack_pointer>
 0230a5: 20 01                      | local.get 1
 0230a7: 41 00                      | i32.const 0
 0230a9: 41 80 10                   | i32.const 2048
 0230ac: fc 0b 00                   | memory.fill 0
 0230af: 02 40                      | block
 0230b1: 20 00                      |   local.get 0
 0230b3: 28 02 08                   |   i32.load 2 8
 0230b6: 22 02                      |   local.tee 2
 0230b8: 45                         |   i32.eqz
 0230b9: 0d 00                      |   br_if 0
 0230bb: 20 00                      |   local.get 0
 0230bd: 28 02 04                   |   i32.load 2 4
 0230c0: 22 03                      |   local.tee 3
 0230c2: 21 04                      |   local.set 4
 0230c4: 02 40                      |   block
 0230c6: 20 02                      |     local.get 2
 0230c8: 41 03                      |     i32.const 3
 0230ca: 71                         |     i32.and
 0230cb: 22 05                      |     local.tee 5
 0230cd: 45                         |     i32.eqz
 0230ce: 0d 00                      |     br_if 0
 0230d0: 20 03                      |     local.get 3
 0230d2: 21 04                      |     local.set 4
 0230d4: 03 40                      |     loop
 0230d6: 20 01                      |       local.get 1
 0230d8: 20 04                      |       local.get 4
 0230da: 2d 00 00                   |       i32.load8_u 0 0
 0230dd: 41 03                      |       i32.const 3
 0230df: 74                         |       i32.shl
 0230e0: 6a                         |       i32.add
 0230e1: 22 06                      |       local.tee 6
 0230e3: 20 06                      |       local.get 6
 0230e5: 29 03 00                   |       i64.load 3 0
 0230e8: 42 01                      |       i64.const 1
 0230ea: 7c                         |       i64.add
 0230eb: 37 03 00                   |       i64.store 3 0
 0230ee: 20 04                      |       local.get 4
 0230f0: 41 01                      |       i32.const 1
 0230f2: 6a                         |       i32.add
 0230f3: 21 04                      |       local.set 4
 0230f5: 20 05                      |       local.get 5
 0230f7: 41 7f                      |       i32.const 4294967295
 0230f9: 6a                         |       i32.add
 0230fa: 22 05                      |       local.tee 5
 0230fc: 0d 00                      |       br_if 0
 0230fe: 0b                         |     end
 0230ff: 0b                         |   end
 023100: 20 02                      |   local.get 2
 023102: 41 04                      |   i32.const 4
 023104: 49                         |   i32.lt_u
 023105: 0d 00                      |   br_if 0
 023107: 20 03                      |   local.get 3
 023109: 20 02                      |   local.get 2
 02310b: 6a                         |   i32.add
 02310c: 21 06                      |   local.set 6
 02310e: 03 40                      |   loop
 023110: 20 01                      |     local.get 1
 023112: 20 04                      |     local.get 4
 023114: 2d 00 00                   |     i32.load8_u 0 0
 023117: 41 03                      |     i32.const 3
 023119: 74                         |     i32.shl
 02311a: 6a                         |     i32.add
 02311b: 22 05                      |     local.tee 5
 02311d: 20 05                      |     local.get 5
 02311f: 29 03 00                   |     i64.load 3 0
 023122: 42 01                      |     i64.const 1
 023124: 7c                         |     i64.add
 023125: 37 03 00                   |     i64.store 3 0
 023128: 20 01                      |     local.get 1
 02312a: 20 04                      |     local.get 4
 02312c: 41 01                      |     i32.const 1
 02312e: 6a                         |     i32.add
 02312f: 2d 00 00                   |     i32.load8_u 0 0
 023132: 41 03                      |     i32.const 3
 023134: 74                         |     i32.shl
 023135: 6a                         |     i32.add
 023136: 22 05                      |     local.tee 5
 023138: 20 05                      |     local.get 5
 02313a: 29 03 00                   |     i64.load 3 0
 02313d: 42 01                      |     i64.const 1
 02313f: 7c                         |     i64.add
 023140: 37 03 00                   |     i64.store 3 0
 023143: 20 01                      |     local.get 1
 023145: 20 04                      |     local.get 4
 023147: 41 02                      |     i32.const 2
 023149: 6a                         |     i32.add
 02314a: 2d 00 00                   |     i32.load8_u 0 0
 02314d: 41 03                      |     i32.const 3
 02314f: 74                         |     i32.shl
 023150: 6a                         |     i32.add
 023151: 22 05                      |     local.tee 5
 023153: 20 05                      |     local.get 5
 023155: 29 03 00                   |     i64.load 3 0
 023158: 42 01                      |     i64.const 1
 02315a: 7c                         |     i64.add
 02315b: 37 03 00                   |     i64.store 3 0
 02315e: 20 01                      |     local.get 1
 023160: 20 04                      |     local.get 4
 023162: 41 03                      |     i32.const 3
 023164: 6a                         |     i32.add
 023165: 2d 00 00                   |     i32.load8_u 0 0
 023168: 41 03                      |     i32.const 3
 02316a: 74                         |     i32.shl
 02316b: 6a                         |     i32.add
 02316c: 22 05                      |     local.tee 5
 02316e: 20 05                      |     local.get 5
 023170: 29 03 00                   |     i64.load 3 0
 023173: 42 01                      |     i64.const 1
 023175: 7c                         |     i64.add
 023176: 37 03 00                   |     i64.store 3 0
 023179: 20 04                      |     local.get 4
 02317b: 41 04                      |     i32.const 4
 02317d: 6a                         |     i32.add
 02317e: 22 04                      |     local.tee 4
 023180: 20 06                      |     local.get 6
 023182: 47                         |     i32.ne
 023183: 0d 00                      |     br_if 0
 023185: 0b                         |   end
 023186: 0b                         | end
 023187: 20 00                      | local.get 0
 023189: 41 18                      | i32.const 24
 02318b: 6a                         | i32.add
 02318c: 20 01                      | local.get 1
 02318e: 41 80 10                   | i32.const 2048
 023191: fc 0a 00 00                | memory.copy 0 0
 023195: 20 01                      | local.get 1
 023197: 41 80 10                   | i32.const 2048
 02319a: 6a                         | i32.add
 02319b: 24 00                      | global.set 0 <__stack_pointer>
 02319d: 0b                         | end
