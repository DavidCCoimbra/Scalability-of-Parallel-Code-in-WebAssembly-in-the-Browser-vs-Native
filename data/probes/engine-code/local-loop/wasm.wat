00e986 func[33] <rayon[599452d85584ec74]::iter::plumbing::bridge_producer_consumer::helper::<rayon[599452d85584ec74]::iter::len::MaxLenProducer<rayon[599452d85584ec74]::slice::chunks::ChunksProducer<u8>>, rayon[599452d85584ec74]::iter::fold::FoldConsumer<rayon[599452d85584ec74]::iter::reduce::ReduceConsumer<<bench[c9b452c63323ae17]::workloads::histogram::Histogram>::merge, <bench[c9b452c63323ae17]::workloads::histogram::Histogram as core[44f98dc1fdbe93f7]::default::Default>::default>, <bench[c9b452c63323ae17]::workloads::histogram::Histogram as core[44f98dc1fdbe93f7]::default::Default>::default, bench[c9b452c63323ae17]::workloads::histogram::local::local_counts<rayon[599452d85584ec74]::iter::len::MaxLen<rayon[599452d85584ec74]::slice::chunks::Chunks<u8>>>::{closure#0}>>>:
 00e987: 05 7f                      | local[7..11] type=i32
 00e989: 23 00                      | global.get 0 <__stack_pointer>
 00e98b: 41 b0 f0 00                | i32.const 14384
 00e98f: 6b                         | i32.sub
 00e990: 22 07                      | local.tee 7
 00e992: 24 00                      | global.set 0 <__stack_pointer>
 00e994: 20 07                      | local.get 7
 00e996: 20 01                      | local.get 1
 00e998: 36 02 0c                   | i32.store 2 12
 00e99b: 20 07                      | local.get 7
 00e99d: 20 04                      | local.get 4
 00e99f: 36 02 14                   | i32.store 2 20
 00e9a2: 02 40                      | block
 00e9a4: 02 40                      |   block
 00e9a6: 02 40                      |     block
 00e9a8: 02 40                      |       block
 00e9aa: 02 40                      |         block
 00e9ac: 02 40                      |           block
 00e9ae: 02 40                      |             block
 00e9b0: 20 01                      |               local.get 1
 00e9b2: 41 01                      |               i32.const 1
 00e9b4: 76                         |               i32.shr_u
 00e9b5: 22 01                      |               local.tee 1
 00e9b7: 20 04                      |               local.get 4
 00e9b9: 49                         |               i32.lt_u
 00e9ba: 0d 00                      |               br_if 0
 00e9bc: 20 02                      |               local.get 2
 00e9be: 0d 01                      |               br_if 1
 00e9c0: 20 03                      |               local.get 3
 00e9c2: 45                         |               i32.eqz
 00e9c3: 0d 00                      |               br_if 0
 00e9c5: 20 03                      |               local.get 3
 00e9c7: 41 01                      |               i32.const 1
 00e9c9: 76                         |               i32.shr_u
 00e9ca: 21 04                      |               local.set 4
 00e9cc: 0c 02                      |               br 2
 00e9ce: 0b                         |             end
 00e9cf: 20 05                      |             local.get 5
 00e9d1: 28 02 08                   |             i32.load 2 8
 00e9d4: 22 08                      |             local.tee 8
 00e9d6: 45                         |             i32.eqz
 00e9d7: 0d 02                      |             br_if 2
 00e9d9: 20 05                      |             local.get 5
 00e9db: 28 02 00                   |             i32.load 2 0
 00e9de: 21 06                      |             local.set 6
 00e9e0: 20 05                      |             local.get 5
 00e9e2: 28 02 04                   |             i32.load 2 4
 00e9e5: 21 02                      |             local.set 2
 00e9e7: 41 00                      |             i32.const 0
 00e9e9: 21 03                      |             local.set 3
 00e9eb: 20 07                      |             local.get 7
 00e9ed: 41 98 c0 00                |             i32.const 8216
 00e9f1: 6a                         |             i32.add
 00e9f2: 41 00                      |             i32.const 0
 00e9f4: 41 80 10                   |             i32.const 2048
 00e9f7: fc 0b 00                   |             memory.fill 0
 00e9fa: 02 40                      |             block
 00e9fc: 20 02                      |               local.get 2
 00e9fe: 45                         |               i32.eqz
 00e9ff: 0d 00                      |               br_if 0
 00ea01: 03 40                      |               loop
 00ea03: 20 07                      |                 local.get 7
 00ea05: 41 b0 d0 00                |                 i32.const 10288
 00ea09: 6a                         |                 i32.add
 00ea0a: 20 07                      |                 local.get 7
 00ea0c: 41 98 c0 00                |                 i32.const 8216
 00ea10: 6a                         |                 i32.add
 00ea11: 41 80 10                   |                 i32.const 2048
 00ea14: fc 0a 00 00                |                 memory.copy 0 0
 00ea18: 20 06                      |                 local.get 6
 00ea1a: 21 05                      |                 local.set 5
 00ea1c: 02 40                      |                 block
 00ea1e: 20 02                      |                   local.get 2
 00ea20: 20 08                      |                   local.get 8
 00ea22: 20 02                      |                   local.get 2
 00ea24: 20 08                      |                   local.get 8
 00ea26: 49                         |                   i32.lt_u
 00ea27: 1b                         |                   select
 00ea28: 22 09                      |                   local.tee 9
 00ea2a: 41 03                      |                   i32.const 3
 00ea2c: 71                         |                   i32.and
 00ea2d: 22 01                      |                   local.tee 1
 00ea2f: 45                         |                   i32.eqz
 00ea30: 0d 00                      |                   br_if 0
 00ea32: 20 06                      |                   local.get 6
 00ea34: 21 05                      |                   local.set 5
 00ea36: 03 40                      |                   loop
 00ea38: 20 07                      |                     local.get 7
 00ea3a: 41 b0 d0 00                |                     i32.const 10288
 00ea3e: 6a                         |                     i32.add
 00ea3f: 20 05                      |                     local.get 5
 00ea41: 2d 00 00                   |                     i32.load8_u 0 0
 00ea44: 41 03                      |                     i32.const 3
 00ea46: 74                         |                     i32.shl
 00ea47: 6a                         |                     i32.add
 00ea48: 22 04                      |                     local.tee 4
 00ea4a: 20 04                      |                     local.get 4
 00ea4c: 29 03 00                   |                     i64.load 3 0
 00ea4f: 42 01                      |                     i64.const 1
 00ea51: 7c                         |                     i64.add
 00ea52: 37 03 00                   |                     i64.store 3 0
 00ea55: 20 05                      |                     local.get 5
 00ea57: 41 01                      |                     i32.const 1
 00ea59: 6a                         |                     i32.add
 00ea5a: 21 05                      |                     local.set 5
 00ea5c: 20 01                      |                     local.get 1
 00ea5e: 41 7f                      |                     i32.const 4294967295
 00ea60: 6a                         |                     i32.add
 00ea61: 22 01                      |                     local.tee 1
 00ea63: 0d 00                      |                     br_if 0
 00ea65: 0b                         |                   end
 00ea66: 0b                         |                 end
 00ea67: 20 06                      |                 local.get 6
 00ea69: 20 09                      |                 local.get 9
 00ea6b: 6a                         |                 i32.add
 00ea6c: 21 06                      |                 local.set 6
 00ea6e: 02 40                      |                 block
 00ea70: 20 09                      |                   local.get 9
 00ea72: 41 04                      |                   i32.const 4
 00ea74: 49                         |                   i32.lt_u
 00ea75: 0d 00                      |                   br_if 0
 00ea77: 03 40                      |                   loop
 00ea79: 20 07                      |                     local.get 7
 00ea7b: 41 b0 d0 00                |                     i32.const 10288
 00ea7f: 6a                         |                     i32.add
 00ea80: 20 05                      |                     local.get 5
 00ea82: 2d 00 00                   |                     i32.load8_u 0 0
 00ea85: 41 03                      |                     i32.const 3
 00ea87: 74                         |                     i32.shl
 00ea88: 6a                         |                     i32.add
 00ea89: 22 01                      |                     local.tee 1
 00ea8b: 20 01                      |                     local.get 1
 00ea8d: 29 03 00                   |                     i64.load 3 0
 00ea90: 42 01                      |                     i64.const 1
 00ea92: 7c                         |                     i64.add
 00ea93: 37 03 00                   |                     i64.store 3 0
 00ea96: 20 07                      |                     local.get 7
 00ea98: 41 b0 d0 00                |                     i32.const 10288
 00ea9c: 6a                         |                     i32.add
 00ea9d: 20 05                      |                     local.get 5
 00ea9f: 41 01                      |                     i32.const 1
 00eaa1: 6a                         |                     i32.add
 00eaa2: 2d 00 00                   |                     i32.load8_u 0 0
 00eaa5: 41 03                      |                     i32.const 3
 00eaa7: 74                         |                     i32.shl
 00eaa8: 6a                         |                     i32.add
 00eaa9: 22 01                      |                     local.tee 1
 00eaab: 20 01                      |                     local.get 1
 00eaad: 29 03 00                   |                     i64.load 3 0
 00eab0: 42 01                      |                     i64.const 1
 00eab2: 7c                         |                     i64.add
 00eab3: 37 03 00                   |                     i64.store 3 0
 00eab6: 20 07                      |                     local.get 7
 00eab8: 41 b0 d0 00                |                     i32.const 10288
 00eabc: 6a                         |                     i32.add
 00eabd: 20 05                      |                     local.get 5
 00eabf: 41 02                      |                     i32.const 2
 00eac1: 6a                         |                     i32.add
 00eac2: 2d 00 00                   |                     i32.load8_u 0 0
 00eac5: 41 03                      |                     i32.const 3
 00eac7: 74                         |                     i32.shl
 00eac8: 6a                         |                     i32.add
 00eac9: 22 01                      |                     local.tee 1
 00eacb: 20 01                      |                     local.get 1
 00eacd: 29 03 00                   |                     i64.load 3 0
 00ead0: 42 01                      |                     i64.const 1
 00ead2: 7c                         |                     i64.add
 00ead3: 37 03 00                   |                     i64.store 3 0
 00ead6: 20 07                      |                     local.get 7
 00ead8: 41 b0 d0 00                |                     i32.const 10288
 00eadc: 6a                         |                     i32.add
 00eadd: 20 05                      |                     local.get 5
 00eadf: 41 03                      |                     i32.const 3
 00eae1: 6a                         |                     i32.add
 00eae2: 2d 00 00                   |                     i32.load8_u 0 0
 00eae5: 41 03                      |                     i32.const 3
 00eae7: 74                         |                     i32.shl
 00eae8: 6a                         |                     i32.add
 00eae9: 22 01                      |                     local.tee 1
 00eaeb: 20 01                      |                     local.get 1
 00eaed: 29 03 00                   |                     i64.load 3 0
 00eaf0: 42 01                      |                     i64.const 1
 00eaf2: 7c                         |                     i64.add
 00eaf3: 37 03 00                   |                     i64.store 3 0
 00eaf6: 20 05                      |                     local.get 5
 00eaf8: 41 04                      |                     i32.const 4
 00eafa: 6a                         |                     i32.add
 00eafb: 22 05                      |                     local.tee 5
 00eafd: 20 06                      |                     local.get 6
 00eaff: 47                         |                     i32.ne
 00eb00: 0d 00                      |                     br_if 0
 00eb02: 0b                         |                   end
 00eb03: 0b                         |                 end
 00eb04: 20 07                      |                 local.get 7
 00eb06: 41 98 c0 00                |                 i32.const 8216
 00eb0a: 6a                         |                 i32.add
 00eb0b: 20 07                      |                 local.get 7
 00eb0d: 41 b0 d0 00                |                 i32.const 10288
 00eb11: 6a                         |                 i32.add
 00eb12: 41 80 10                   |                 i32.const 2048
 00eb15: fc 0a 00 00                |                 memory.copy 0 0
 00eb19: 20 02                      |                 local.get 2
 00eb1b: 20 09                      |                 local.get 9
 00eb1d: 6b                         |                 i32.sub
 00eb1e: 22 02                      |                 local.tee 2
 00eb20: 0d 00                      |                 br_if 0
 00eb22: 0b                         |               end
 00eb23: 0b                         |             end
 00eb24: 20 07                      |             local.get 7
 00eb26: 41 98 20                   |             i32.const 4120
 00eb29: 6a                         |             i32.add
 00eb2a: 20 07                      |             local.get 7
 00eb2c: 41 98 c0 00                |             i32.const 8216
 00eb30: 6a                         |             i32.add
 00eb31: 41 80 10                   |             i32.const 2048
 00eb34: fc 0a 00 00                |             memory.copy 0 0
 00eb38: 20 07                      |             local.get 7
 00eb3a: 41 b0 d0 00                |             i32.const 10288
 00eb3e: 6a                         |             i32.add
 00eb3f: 41 00                      |             i32.const 0
 00eb41: 41 80 10                   |             i32.const 2048
 00eb44: fc 0b 00                   |             memory.fill 0
 00eb47: 20 07                      |             local.get 7
 00eb49: 41 b0 d0 00                |             i32.const 10288
 00eb4d: 6a                         |             i32.add
 00eb4e: 41 80 10                   |             i32.const 2048
 00eb51: 6a                         |             i32.add
 00eb52: 20 07                      |             local.get 7
 00eb54: 41 98 20                   |             i32.const 4120
 00eb57: 6a                         |             i32.add
 00eb58: 41 80 10                   |             i32.const 2048
 00eb5b: fc 0a 00 00                |             memory.copy 0 0
 00eb5f: 20 07                      |             local.get 7
 00eb61: 41 98 c0 00                |             i32.const 8216
 00eb65: 6a                         |             i32.add
 00eb66: 41 10                      |             i32.const 16
 00eb68: 6a                         |             i32.add
 00eb69: 20 07                      |             local.get 7
 00eb6b: 41 98 20                   |             i32.const 4120
 00eb6e: 6a                         |             i32.add
 00eb6f: 41 80 10                   |             i32.const 2048
 00eb72: fc 0a 00 00                |             memory.copy 0 0
 00eb76: 20 07                      |             local.get 7
 00eb78: 42 00                      |             i64.const 0
 00eb7a: 37 03 a8 50                |             i64.store 3 10280
 00eb7e: 03 40                      |             loop
 00eb80: 20 07                      |               local.get 7
 00eb82: 41 b0 d0 00                |               i32.const 10288
 00eb86: 6a                         |               i32.add
 00eb87: 20 03                      |               local.get 3
 00eb89: 6a                         |               i32.add
 00eb8a: 22 05                      |               local.tee 5
 00eb8c: 20 05                      |               local.get 5
 00eb8e: fd 00 03 00                |               v128.load 3 0
 00eb92: 20 07                      |               local.get 7
 00eb94: 41 98 c0 00                |               i32.const 8216
 00eb98: 6a                         |               i32.add
 00eb99: 20 03                      |               local.get 3
 00eb9b: 6a                         |               i32.add
 00eb9c: 22 01                      |               local.tee 1
 00eb9e: 41 10                      |               i32.const 16
 00eba0: 6a                         |               i32.add
 00eba1: fd 00 03 00                |               v128.load 3 0
 00eba5: fd ce 01                   |               i64x2.add
 00eba8: fd 0b 03 00                |               v128.store 3 0
 00ebac: 20 05                      |               local.get 5
 00ebae: 41 10                      |               i32.const 16
 00ebb0: 6a                         |               i32.add
 00ebb1: 22 05                      |               local.tee 5
 00ebb3: 20 05                      |               local.get 5
 00ebb5: fd 00 03 00                |               v128.load 3 0
 00ebb9: 20 01                      |               local.get 1
 00ebbb: 41 20                      |               i32.const 32
 00ebbd: 6a                         |               i32.add
 00ebbe: fd 00 03 00                |               v128.load 3 0
 00ebc2: fd ce 01                   |               i64x2.add
 00ebc5: fd 0b 03 00                |               v128.store 3 0
 00ebc9: 20 03                      |               local.get 3
 00ebcb: 41 20                      |               i32.const 32
 00ebcd: 6a                         |               i32.add
 00ebce: 22 03                      |               local.tee 3
 00ebd0: 41 80 10                   |               i32.const 2048
 00ebd3: 47                         |               i32.ne
 00ebd4: 0d 00                      |               br_if 0
 00ebd6: 0b                         |             end
 00ebd7: 20 00                      |             local.get 0
 00ebd9: 20 07                      |             local.get 7
 00ebdb: 41 b0 d0 00                |             i32.const 10288
 00ebdf: 6a                         |             i32.add
 00ebe0: 41 80 10                   |             i32.const 2048
 00ebe3: fc 0a 00 00                |             memory.copy 0 0
 00ebe7: 0c 05                      |             br 5
 00ebe9: 0b                         |           end
 00ebea: 10 a0 03                   |           call 416 <rayon_core[7650722b9b765dc1]::current_num_threads>
 00ebed: 22 04                      |           local.tee 4
 00ebef: 20 03                      |           local.get 3
 00ebf1: 41 01                      |           i32.const 1
 00ebf3: 76                         |           i32.shr_u
 00ebf4: 22 03                      |           local.tee 3
 00ebf6: 20 04                      |           local.get 4
 00ebf8: 20 03                      |           local.get 3
 00ebfa: 4b                         |           i32.gt_u
 00ebfb: 1b                         |           select
 00ebfc: 21 04                      |           local.set 4
 00ebfe: 0b                         |         end
 00ebff: 20 07                      |         local.get 7
 00ec01: 41 98 10                   |         i32.const 2072
 00ec04: 6a                         |         i32.add
 00ec05: 21 02                      |         local.set 2
 00ec07: 20 07                      |         local.get 7
 00ec09: 20 04                      |         local.get 4
 00ec0b: 36 02 10                   |         i32.store 2 16
 00ec0e: 20 05                      |         local.get 5
 00ec10: 28 02 04                   |         i32.load 2 4
 00ec13: 21 04                      |         local.set 4
 00ec15: 20 07                      |         local.get 7
 00ec17: 20 01                      |         local.get 1
 00ec19: 36 02 98 40                |         i32.store 2 8216
 00ec1d: 20 05                      |         local.get 5
 00ec1f: 28 02 00                   |         i32.load 2 0
 00ec22: 21 09                      |         local.set 9
 00ec24: 20 05                      |         local.get 5
 00ec26: 28 02 08                   |         i32.load 2 8
 00ec29: 21 03                      |         local.set 3
 00ec2b: 20 05                      |         local.get 5
 00ec2d: 28 02 0c                   |         i32.load 2 12
 00ec30: 21 05                      |         local.set 5
 00ec32: 20 06                      |         local.get 6
 00ec34: 28 02 00                   |         i32.load 2 0
 00ec37: 21 08                      |         local.set 8
 00ec39: 20 06                      |         local.get 6
 00ec3b: 28 02 04                   |         i32.load 2 4
 00ec3e: 21 0a                      |         local.set 10
 00ec40: 20 06                      |         local.get 6
 00ec42: 28 02 08                   |         i32.load 2 8
 00ec45: 21 0b                      |         local.set 11
 00ec47: 20 07                      |         local.get 7
 00ec49: 20 06                      |         local.get 6
 00ec4b: 28 02 0c                   |         i32.load 2 12
 00ec4e: 22 06                      |         local.tee 6
 00ec50: 36 02 80 51                |         i32.store 2 10368
 00ec54: 20 07                      |         local.get 7
 00ec56: 20 0b                      |         local.get 11
 00ec58: 36 02 fc 50                |         i32.store 2 10364
 00ec5c: 20 07                      |         local.get 7
 00ec5e: 20 0a                      |         local.get 10
 00ec60: 36 02 f8 50                |         i32.store 2 10360
 00ec64: 20 07                      |         local.get 7
 00ec66: 20 08                      |         local.get 8
 00ec68: 36 02 f4 50                |         i32.store 2 10356
 00ec6c: 20 07                      |         local.get 7
 00ec6e: 20 05                      |         local.get 5
 00ec70: 36 02 f0 50                |         i32.store 2 10352
 00ec74: 20 07                      |         local.get 7
 00ec76: 20 03                      |         local.get 3
 00ec78: 36 02 ec 50                |         i32.store 2 10348
 00ec7c: 20 07                      |         local.get 7
 00ec7e: 20 09                      |         local.get 9
 00ec80: 36 02 e4 50                |         i32.store 2 10340
 00ec84: 20 07                      |         local.get 7
 00ec86: 20 06                      |         local.get 6
 00ec88: 36 02 d8 50                |         i32.store 2 10328
 00ec8c: 20 07                      |         local.get 7
 00ec8e: 20 0b                      |         local.get 11
 00ec90: 36 02 d4 50                |         i32.store 2 10324
 00ec94: 20 07                      |         local.get 7
 00ec96: 20 0a                      |         local.get 10
 00ec98: 36 02 d0 50                |         i32.store 2 10320
 00ec9c: 20 07                      |         local.get 7
 00ec9e: 20 08                      |         local.get 8
 00eca0: 36 02 cc 50                |         i32.store 2 10316
 00eca4: 20 07                      |         local.get 7
 00eca6: 20 05                      |         local.get 5
 00eca8: 36 02 c8 50                |         i32.store 2 10312
 00ecac: 20 07                      |         local.get 7
 00ecae: 20 03                      |         local.get 3
 00ecb0: 36 02 c4 50                |         i32.store 2 10308
 00ecb4: 20 07                      |         local.get 7
 00ecb6: 20 03                      |         local.get 3
 00ecb8: 20 01                      |         local.get 1
 00ecba: 6c                         |         i32.mul
 00ecbb: 22 05                      |         local.tee 5
 00ecbd: 20 04                      |         local.get 4
 00ecbf: 20 05                      |         local.get 5
 00ecc1: 20 04                      |         local.get 4
 00ecc3: 49                         |         i32.lt_u
 00ecc4: 1b                         |         select
 00ecc5: 22 05                      |         local.tee 5
 00ecc7: 36 02 e8 50                |         i32.store 2 10344
 00eccb: 20 07                      |         local.get 7
 00eccd: 20 04                      |         local.get 4
 00eccf: 20 05                      |         local.get 5
 00ecd1: 6b                         |         i32.sub
 00ecd2: 36 02 c0 50                |         i32.store 2 10304
 00ecd6: 20 07                      |         local.get 7
 00ecd8: 20 09                      |         local.get 9
 00ecda: 20 05                      |         local.get 5
 00ecdc: 6a                         |         i32.add
 00ecdd: 36 02 bc 50                |         i32.store 2 10300
 00ece1: 23 01                      |         global.get 1 <__tls_base>
 00ece3: 21 05                      |         local.set 5
 00ece5: 20 07                      |         local.get 7
 00ece7: 20 07                      |         local.get 7
 00ece9: 41 10                      |         i32.const 16
 00eceb: 6a                         |         i32.add
 00ecec: 36 02 e0 50                |         i32.store 2 10336
 00ecf0: 20 07                      |         local.get 7
 00ecf2: 20 07                      |         local.get 7
 00ecf4: 41 98 c0 00                |         i32.const 8216
 00ecf8: 6a                         |         i32.add
 00ecf9: 36 02 dc 50                |         i32.store 2 10332
 00ecfd: 20 07                      |         local.get 7
 00ecff: 20 07                      |         local.get 7
 00ed01: 41 10                      |         i32.const 16
 00ed03: 6a                         |         i32.add
 00ed04: 36 02 b8 50                |         i32.store 2 10296
 00ed08: 20 07                      |         local.get 7
 00ed0a: 20 07                      |         local.get 7
 00ed0c: 41 98 c0 00                |         i32.const 8216
 00ed10: 6a                         |         i32.add
 00ed11: 36 02 b4 50                |         i32.store 2 10292
 00ed15: 20 07                      |         local.get 7
 00ed17: 20 07                      |         local.get 7
 00ed19: 41 0c                      |         i32.const 12
 00ed1b: 6a                         |         i32.add
 00ed1c: 36 02 b0 50                |         i32.store 2 10288
 00ed20: 02 40                      |         block
 00ed22: 20 05                      |           local.get 5
 00ed24: 41 28                      |           i32.const 40
 00ed26: 6a                         |           i32.add
 00ed27: 22 01                      |           local.tee 1
 00ed29: 28 02 00                   |           i32.load 2 0
 00ed2c: 22 05                      |           local.tee 5
 00ed2e: 45                         |           i32.eqz
 00ed2f: 0d 00                      |           br_if 0
 00ed31: 20 07                      |           local.get 7
 00ed33: 41 18                      |           i32.const 24
 00ed35: 6a                         |           i32.add
 00ed36: 20 07                      |           local.get 7
 00ed38: 41 b0 d0 00                |           i32.const 10288
 00ed3c: 6a                         |           i32.add
 00ed3d: 20 05                      |           local.get 5
 00ed3f: 41 00                      |           i32.const 0
 00ed41: 10 2e                      |           call 46 <rayon_core[7650722b9b765dc1]::join::join_context::<rayon[599452d85584ec74]::iter::plumbing::bridge_producer_consumer::helper<rayon[599452d85584ec74]::iter::len::MaxLenProducer<rayon[599452d85584ec74]::slice::chunks::ChunksProducer<u8>>, rayon[599452d85584ec74]::iter::fold::FoldConsumer<rayon[599452d85584ec74]::iter::reduce::ReduceConsumer<<bench[c9b452c63323ae17]::workloads::histogram::Histogram>::merge, <bench[c9b452c63323ae17]::workloads::histogram::Histogram as core[44f98dc1fdbe93f7]::default::Default>::default>, <bench[c9b452c63323ae17]::workloads::histogram::Histogram as core[44f98dc1fdbe93f7]::default::Default>::default, bench[c9b452c63323ae17]::workloads::histogram::local::local_counts<rayon[599452d85584ec74]::iter::len::MaxLen<rayon[599452d85584ec74]::slice::chunks::Chunks<u8>>>::{closure#0}>>::{closure#0}, rayon[599452d85584ec74]::iter::plumbing::bridge_producer_consumer::helper<rayon[599452d85584ec74]::iter::len::MaxLenProducer<rayon[599452d85584ec74]::slice::chunks::ChunksProducer<u8>>, rayon[599452d85584ec74]::iter::fold::FoldConsumer<rayon[599452d85584ec74]::iter::reduce::ReduceConsumer<<bench[c9b452c63323ae17]::workloads::histogram::Histogram>::merge, <bench[c9b452c63323ae17]::workloads::histogram::Histogram as core[44f98dc1fdbe93f7]::default::Default>::default>, <bench[c9b452c63323ae17]::workloads::histogram::Histogram as core[44f98dc1fdbe93f7]::default::Default>::default, bench[c9b452c63323ae17]::workloads::histogram::local::local_counts<rayon[599452d85584ec74]::iter::len::MaxLen<rayon[599452d85584ec74]::slice::chunks::Chunks<u8>>>::{closure#0}>>::{closure#1}, bench[c9b452c63323ae17]::workloads::histogram::Histogram, bench[c9b452c63323ae17]::workloads::histogram::Histogram>::{closure#0}>
 00ed43: 0c 03                      |           br 3
 00ed45: 0b                         |         end
 00ed46: 10 d1 01                   |         call 209 <rayon_core[7650722b9b765dc1]::registry::global_registry>
 00ed49: 28 02 00                   |         i32.load 2 0
 00ed4c: 21 04                      |         local.set 4
 00ed4e: 20 01                      |         local.get 1
 00ed50: 28 02 00                   |         i32.load 2 0
 00ed53: 22 05                      |         local.tee 5
 00ed55: 45                         |         i32.eqz
 00ed56: 0d 01                      |         br_if 1
 00ed58: 02 40                      |         block
 00ed5a: 20 05                      |           local.get 5
 00ed5c: 28 02 8c 01                |           i32.load 2 140
 00ed60: 20 04                      |           local.get 4
 00ed62: 47                         |           i32.ne
 00ed63: 0d 00                      |           br_if 0
 00ed65: 20 07                      |           local.get 7
 00ed67: 41 18                      |           i32.const 24
 00ed69: 6a                         |           i32.add
 00ed6a: 20 07                      |           local.get 7
 00ed6c: 41 b0 d0 00                |           i32.const 10288
 00ed70: 6a                         |           i32.add
 00ed71: 20 05                      |           local.get 5
 00ed73: 41 00                      |           i32.const 0
 00ed75: 10 2e                      |           call 46 <rayon_core[7650722b9b765dc1]::join::join_context::<rayon[599452d85584ec74]::iter::plumbing::bridge_producer_consumer::helper<rayon[599452d85584ec74]::iter::len::MaxLenProducer<rayon[599452d85584ec74]::slice::chunks::ChunksProducer<u8>>, rayon[599452d85584ec74]::iter::fold::FoldConsumer<rayon[599452d85584ec74]::iter::reduce::ReduceConsumer<<bench[c9b452c63323ae17]::workloads::histogram::Histogram>::merge, <bench[c9b452c63323ae17]::workloads::histogram::Histogram as core[44f98dc1fdbe93f7]::default::Default>::default>, <bench[c9b452c63323ae17]::workloads::histogram::Histogram as core[44f98dc1fdbe93f7]::default::Default>::default, bench[c9b452c63323ae17]::workloads::histogram::local::local_counts<rayon[599452d85584ec74]::iter::len::MaxLen<rayon[599452d85584ec74]::slice::chunks::Chunks<u8>>>::{closure#0}>>::{closure#0}, rayon[599452d85584ec74]::iter::plumbing::bridge_producer_consumer::helper<rayon[599452d85584ec74]::iter::len::MaxLenProducer<rayon[599452d85584ec74]::slice::chunks::ChunksProducer<u8>>, rayon[599452d85584ec74]::iter::fold::FoldConsumer<rayon[599452d85584ec74]::iter::reduce::ReduceConsumer<<bench[c9b452c63323ae17]::workloads::histogram::Histogram>::merge, <bench[c9b452c63323ae17]::workloads::histogram::Histogram as core[44f98dc1fdbe93f7]::default::Default>::default>, <bench[c9b452c63323ae17]::workloads::histogram::Histogram as core[44f98dc1fdbe93f7]::default::Default>::default, bench[c9b452c63323ae17]::workloads::histogram::local::local_counts<rayon[599452d85584ec74]::iter::len::MaxLen<rayon[599452d85584ec74]::slice::chunks::Chunks<u8>>>::{closure#0}>>::{closure#1}, bench[c9b452c63323ae17]::workloads::histogram::Histogram, bench[c9b452c63323ae17]::workloads::histogram::Histogram>::{closure#0}>
 00ed77: 0c 03                      |           br 3
 00ed79: 0b                         |         end
 00ed7a: 20 07                      |         local.get 7
 00ed7c: 41 18                      |         i32.const 24
 00ed7e: 6a                         |         i32.add
 00ed7f: 20 04                      |         local.get 4
 00ed81: 41 c0 00                   |         i32.const 64
 00ed84: 6a                         |         i32.add
 00ed85: 20 05                      |         local.get 5
 00ed87: 20 07                      |         local.get 7
 00ed89: 41 b0 d0 00                |         i32.const 10288
 00ed8d: 6a                         |         i32.add
 00ed8e: 10 f4 01                   |         call 244 <<rayon_core[7650722b9b765dc1]::registry::Registry>::in_worker_cross::<rayon_core[7650722b9b765dc1]::join::join_context<rayon[599452d85584ec74]::iter::plumbing::bridge_producer_consumer::helper<rayon[599452d85584ec74]::iter::len::MaxLenProducer<rayon[599452d85584ec74]::slice::chunks::ChunksProducer<u8>>, rayon[599452d85584ec74]::iter::fold::FoldConsumer<rayon[599452d85584ec74]::iter::reduce::ReduceConsumer<<bench[c9b452c63323ae17]::workloads::histogram::Histogram>::merge, <bench[c9b452c63323ae17]::workloads::histogram::Histogram as core[44f98dc1fdbe93f7]::default::Default>::default>, <bench[c9b452c63323ae17]::workloads::histogram::Histogram as core[44f98dc1fdbe93f7]::default::Default>::default, bench[c9b452c63323ae17]::workloads::histogram::local::local_counts<rayon[599452d85584ec74]::iter::len::MaxLen<rayon[599452d85584ec74]::slice::chunks::Chunks<u8>>>::{closure#0}>>::{closure#0}, rayon[599452d85584ec74]::iter::plumbing::bridge_producer_consumer::helper<rayon[599452d85584ec74]::iter::len::MaxLenProducer<rayon[599452d85584ec74]::slice::chunks::ChunksProducer<u8>>, rayon[599452d85584ec74]::iter::fold::FoldConsumer<rayon[599452d85584ec74]::iter::reduce::ReduceConsumer<<bench[c9b452c63323ae17]::workloads::histogram::Histogram>::merge, <bench[c9b452c63323ae17]::workloads::histogram::Histogram as core[44f98dc1fdbe93f7]::default::Default>::default>, <bench[c9b452c63323ae17]::workloads::histogram::Histogram as core[44f98dc1fdbe93f7]::default::Default>::default, bench[c9b452c63323ae17]::workloads::histogram::local::local_counts<rayon[599452d85584ec74]::iter::len::MaxLen<rayon[599452d85584ec74]::slice::chunks::Chunks<u8>>>::{closure#0}>>::{closure#1}, bench[c9b452c63323ae17]::workloads::histogram::Histogram, bench[c9b452c63323ae17]::workloads::histogram::Histogram>::{closure#0}, (bench[c9b452c63323ae17]::workloads::histogram::Histogram, bench[c9b452c63323ae17]::workloads::histogram::Histogram)>>
 00ed91: 0c 02                      |         br 2
 00ed93: 0b                         |       end
 00ed94: 41 80 80 c0 00             |       i32.const 1048576
 00ed99: 41 37                      |       i32.const 55
 00ed9b: 41 bc cc c0 00             |       i32.const 1058364
 00eda0: 10 84 03                   |       call 388 <core[44f98dc1fdbe93f7]::panicking::panic_fmt>
 00eda3: 00                         |       unreachable
 00eda4: 0b                         |     end
 00eda5: 20 07                      |     local.get 7
 00eda7: 41 18                      |     i32.const 24
 00eda9: 6a                         |     i32.add
 00edaa: 20 04                      |     local.get 4
 00edac: 41 c0 00                   |     i32.const 64
 00edaf: 6a                         |     i32.add
 00edb0: 20 07                      |     local.get 7
 00edb2: 41 b0 d0 00                |     i32.const 10288
 00edb6: 6a                         |     i32.add
 00edb7: 10 a2 02                   |     call 290 <<rayon_core[7650722b9b765dc1]::registry::Registry>::in_worker_cold::<rayon_core[7650722b9b765dc1]::join::join_context<rayon[599452d85584ec74]::iter::plumbing::bridge_producer_consumer::helper<rayon[599452d85584ec74]::iter::len::MaxLenProducer<rayon[599452d85584ec74]::slice::chunks::ChunksProducer<u8>>, rayon[599452d85584ec74]::iter::fold::FoldConsumer<rayon[599452d85584ec74]::iter::reduce::ReduceConsumer<<bench[c9b452c63323ae17]::workloads::histogram::Histogram>::merge, <bench[c9b452c63323ae17]::workloads::histogram::Histogram as core[44f98dc1fdbe93f7]::default::Default>::default>, <bench[c9b452c63323ae17]::workloads::histogram::Histogram as core[44f98dc1fdbe93f7]::default::Default>::default, bench[c9b452c63323ae17]::workloads::histogram::local::local_counts<rayon[599452d85584ec74]::iter::len::MaxLen<rayon[599452d85584ec74]::slice::chunks::Chunks<u8>>>::{closure#0}>>::{closure#0}, rayon[599452d85584ec74]::iter::plumbing::bridge_producer_consumer::helper<rayon[599452d85584ec74]::iter::len::MaxLenProducer<rayon[599452d85584ec74]::slice::chunks::ChunksProducer<u8>>, rayon[599452d85584ec74]::iter::fold::FoldConsumer<rayon[599452d85584ec74]::iter::reduce::ReduceConsumer<<bench[c9b452c63323ae17]::workloads::histogram::Histogram>::merge, <bench[c9b452c63323ae17]::workloads::histogram::Histogram as core[44f98dc1fdbe93f7]::default::Default>::default>, <bench[c9b452c63323ae17]::workloads::histogram::Histogram as core[44f98dc1fdbe93f7]::default::Default>::default, bench[c9b452c63323ae17]::workloads::histogram::local::local_counts<rayon[599452d85584ec74]::iter::len::MaxLen<rayon[599452d85584ec74]::slice::chunks::Chunks<u8>>>::{closure#0}>>::{closure#1}, bench[c9b452c63323ae17]::workloads::histogram::Histogram, bench[c9b452c63323ae17]::workloads::histogram::Histogram>::{closure#0}, (bench[c9b452c63323ae17]::workloads::histogram::Histogram, bench[c9b452c63323ae17]::workloads::histogram::Histogram)>>
 00edba: 0b                         |   end
 00edbb: 20 07                      |   local.get 7
 00edbd: 41 b0 d0 00                |   i32.const 10288
 00edc1: 6a                         |   i32.add
 00edc2: 20 07                      |   local.get 7
 00edc4: 41 18                      |   i32.const 24
 00edc6: 6a                         |   i32.add
 00edc7: 41 80 10                   |   i32.const 2048
 00edca: fc 0a 00 00                |   memory.copy 0 0
 00edce: 20 07                      |   local.get 7
 00edd0: 41 b0 d0 00                |   i32.const 10288
 00edd4: 6a                         |   i32.add
 00edd5: 41 80 10                   |   i32.const 2048
 00edd8: 6a                         |   i32.add
 00edd9: 20 02                      |   local.get 2
 00eddb: 41 80 10                   |   i32.const 2048
 00edde: fc 0a 00 00                |   memory.copy 0 0
 00ede2: 20 07                      |   local.get 7
 00ede4: 41 98 20                   |   i32.const 4120
 00ede7: 6a                         |   i32.add
 00ede8: 41 10                      |   i32.const 16
 00edea: 6a                         |   i32.add
 00edeb: 20 02                      |   local.get 2
 00eded: 41 80 10                   |   i32.const 2048
 00edf0: fc 0a 00 00                |   memory.copy 0 0
 00edf4: 20 07                      |   local.get 7
 00edf6: 42 00                      |   i64.const 0
 00edf8: 37 03 a8 30                |   i64.store 3 6184
 00edfc: 41 00                      |   i32.const 0
 00edfe: 21 05                      |   local.set 5
 00ee00: 03 40                      |   loop
 00ee02: 20 07                      |     local.get 7
 00ee04: 41 b0 d0 00                |     i32.const 10288
 00ee08: 6a                         |     i32.add
 00ee09: 20 05                      |     local.get 5
 00ee0b: 6a                         |     i32.add
 00ee0c: 22 01                      |     local.tee 1
 00ee0e: 20 01                      |     local.get 1
 00ee10: fd 00 03 00                |     v128.load 3 0
 00ee14: 20 07                      |     local.get 7
 00ee16: 41 98 20                   |     i32.const 4120
 00ee19: 6a                         |     i32.add
 00ee1a: 20 05                      |     local.get 5
 00ee1c: 6a                         |     i32.add
 00ee1d: 22 04                      |     local.tee 4
 00ee1f: 41 10                      |     i32.const 16
 00ee21: 6a                         |     i32.add
 00ee22: fd 00 03 00                |     v128.load 3 0
 00ee26: fd ce 01                   |     i64x2.add
 00ee29: fd 0b 03 00                |     v128.store 3 0
 00ee2d: 20 01                      |     local.get 1
 00ee2f: 41 10                      |     i32.const 16
 00ee31: 6a                         |     i32.add
 00ee32: 22 01                      |     local.tee 1
 00ee34: 20 01                      |     local.get 1
 00ee36: fd 00 03 00                |     v128.load 3 0
 00ee3a: 20 04                      |     local.get 4
 00ee3c: 41 20                      |     i32.const 32
 00ee3e: 6a                         |     i32.add
 00ee3f: fd 00 03 00                |     v128.load 3 0
 00ee43: fd ce 01                   |     i64x2.add
 00ee46: fd 0b 03 00                |     v128.store 3 0
 00ee4a: 20 05                      |     local.get 5
 00ee4c: 41 20                      |     i32.const 32
 00ee4e: 6a                         |     i32.add
 00ee4f: 22 05                      |     local.tee 5
 00ee51: 41 80 10                   |     i32.const 2048
 00ee54: 47                         |     i32.ne
 00ee55: 0d 00                      |     br_if 0
 00ee57: 0b                         |   end
 00ee58: 20 00                      |   local.get 0
 00ee5a: 20 07                      |   local.get 7
 00ee5c: 41 b0 d0 00                |   i32.const 10288
 00ee60: 6a                         |   i32.add
 00ee61: 41 80 10                   |   i32.const 2048
 00ee64: fc 0a 00 00                |   memory.copy 0 0
 00ee68: 0b                         | end
 00ee69: 20 07                      | local.get 7
 00ee6b: 41 b0 f0 00                | i32.const 14384
 00ee6f: 6a                         | i32.add
 00ee70: 24 00                      | global.set 0 <__stack_pointer>
 00ee72: 0b                         | end
