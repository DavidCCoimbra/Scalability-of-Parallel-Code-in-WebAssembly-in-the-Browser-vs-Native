013cb0 func[55] <rayon[599452d85584ec74]::iter::plumbing::bridge_producer_consumer::helper::<rayon[599452d85584ec74]::iter::len::MaxLenProducer<rayon[599452d85584ec74]::slice::chunks::ChunksProducer<u8>>, rayon[599452d85584ec74]::iter::for_each::ForEachConsumer<<bench[c9b452c63323ae17]::workloads::histogram::atomic::AtomicHistogram as bench[c9b452c63323ae17]::workloads::workload::Workload>::run::{closure#0}>>>:
 013cb1: 02 7f                      | local[6..7] type=i32
 013cb3: 23 00                      | global.get 0 <__stack_pointer>
 013cb5: 41 d0 00                   | i32.const 80
 013cb8: 6b                         | i32.sub
 013cb9: 22 06                      | local.tee 6
 013cbb: 24 00                      | global.set 0 <__stack_pointer>
 013cbd: 20 06                      | local.get 6
 013cbf: 20 00                      | local.get 0
 013cc1: 36 02 04                   | i32.store 2 4
 013cc4: 20 06                      | local.get 6
 013cc6: 20 03                      | local.get 3
 013cc8: 36 02 0c                   | i32.store 2 12
 013ccb: 02 40                      | block
 013ccd: 02 40                      |   block
 013ccf: 02 40                      |     block
 013cd1: 02 40                      |       block
 013cd3: 02 40                      |         block
 013cd5: 02 40                      |           block
 013cd7: 20 00                      |             local.get 0
 013cd9: 41 01                      |             i32.const 1
 013cdb: 76                         |             i32.shr_u
 013cdc: 22 00                      |             local.tee 0
 013cde: 20 03                      |             local.get 3
 013ce0: 49                         |             i32.lt_u
 013ce1: 0d 00                      |             br_if 0
 013ce3: 20 01                      |             local.get 1
 013ce5: 0d 01                      |             br_if 1
 013ce7: 20 02                      |             local.get 2
 013ce9: 45                         |             i32.eqz
 013cea: 0d 00                      |             br_if 0
 013cec: 20 02                      |             local.get 2
 013cee: 41 01                      |             i32.const 1
 013cf0: 76                         |             i32.shr_u
 013cf1: 21 03                      |             local.set 3
 013cf3: 0c 02                      |             br 2
 013cf5: 0b                         |           end
 013cf6: 20 04                      |           local.get 4
 013cf8: 28 02 08                   |           i32.load 2 8
 013cfb: 22 07                      |           local.tee 7
 013cfd: 45                         |           i32.eqz
 013cfe: 0d 02                      |           br_if 2
 013d00: 20 04                      |           local.get 4
 013d02: 28 02 04                   |           i32.load 2 4
 013d05: 22 01                      |           local.tee 1
 013d07: 45                         |           i32.eqz
 013d08: 0d 04                      |           br_if 4
 013d0a: 20 04                      |           local.get 4
 013d0c: 28 02 00                   |           i32.load 2 0
 013d0f: 21 02                      |           local.set 2
 013d11: 20 05                      |           local.get 5
 013d13: 28 02 00                   |           i32.load 2 0
 013d16: 28 02 00                   |           i32.load 2 0
 013d19: 21 00                      |           local.set 0
 013d1b: 03 40                      |           loop
 013d1d: 20 02                      |             local.get 2
 013d1f: 21 04                      |             local.set 4
 013d21: 02 40                      |             block
 013d23: 20 01                      |               local.get 1
 013d25: 20 07                      |               local.get 7
 013d27: 20 01                      |               local.get 1
 013d29: 20 07                      |               local.get 7
 013d2b: 49                         |               i32.lt_u
 013d2c: 1b                         |               select
 013d2d: 22 05                      |               local.tee 5
 013d2f: 41 07                      |               i32.const 7
 013d31: 71                         |               i32.and
 013d32: 22 03                      |               local.tee 3
 013d34: 45                         |               i32.eqz
 013d35: 0d 00                      |               br_if 0
 013d37: 20 02                      |               local.get 2
 013d39: 21 04                      |               local.set 4
 013d3b: 03 40                      |               loop
 013d3d: 20 00                      |                 local.get 0
 013d3f: 20 04                      |                 local.get 4
 013d41: 2d 00 00                   |                 i32.load8_u 0 0
 013d44: 41 07                      |                 i32.const 7
 013d46: 74                         |                 i32.shl
 013d47: 6a                         |                 i32.add
 013d48: 42 01                      |                 i64.const 1
 013d4a: fe 1f 03 00                |                 i64.atomic.rmw.add 3 0
 013d4e: 1a                         |                 drop
 013d4f: 20 04                      |                 local.get 4
 013d51: 41 01                      |                 i32.const 1
 013d53: 6a                         |                 i32.add
 013d54: 21 04                      |                 local.set 4
 013d56: 20 03                      |                 local.get 3
 013d58: 41 7f                      |                 i32.const 4294967295
 013d5a: 6a                         |                 i32.add
 013d5b: 22 03                      |                 local.tee 3
 013d5d: 0d 00                      |                 br_if 0
 013d5f: 0b                         |               end
 013d60: 0b                         |             end
 013d61: 20 02                      |             local.get 2
 013d63: 20 05                      |             local.get 5
 013d65: 6a                         |             i32.add
 013d66: 21 02                      |             local.set 2
 013d68: 02 40                      |             block
 013d6a: 20 05                      |               local.get 5
 013d6c: 41 08                      |               i32.const 8
 013d6e: 49                         |               i32.lt_u
 013d6f: 0d 00                      |               br_if 0
 013d71: 03 40                      |               loop
 013d73: 20 00                      |                 local.get 0
 013d75: 20 04                      |                 local.get 4
 013d77: 2d 00 00                   |                 i32.load8_u 0 0
 013d7a: 41 07                      |                 i32.const 7
 013d7c: 74                         |                 i32.shl
 013d7d: 6a                         |                 i32.add
 013d7e: 42 01                      |                 i64.const 1
 013d80: fe 1f 03 00                |                 i64.atomic.rmw.add 3 0
 013d84: 1a                         |                 drop
 013d85: 20 00                      |                 local.get 0
 013d87: 20 04                      |                 local.get 4
 013d89: 41 01                      |                 i32.const 1
 013d8b: 6a                         |                 i32.add
 013d8c: 2d 00 00                   |                 i32.load8_u 0 0
 013d8f: 41 07                      |                 i32.const 7
 013d91: 74                         |                 i32.shl
 013d92: 6a                         |                 i32.add
 013d93: 42 01                      |                 i64.const 1
 013d95: fe 1f 03 00                |                 i64.atomic.rmw.add 3 0
 013d99: 1a                         |                 drop
 013d9a: 20 00                      |                 local.get 0
 013d9c: 20 04                      |                 local.get 4
 013d9e: 41 02                      |                 i32.const 2
 013da0: 6a                         |                 i32.add
 013da1: 2d 00 00                   |                 i32.load8_u 0 0
 013da4: 41 07                      |                 i32.const 7
 013da6: 74                         |                 i32.shl
 013da7: 6a                         |                 i32.add
 013da8: 42 01                      |                 i64.const 1
 013daa: fe 1f 03 00                |                 i64.atomic.rmw.add 3 0
 013dae: 1a                         |                 drop
 013daf: 20 00                      |                 local.get 0
 013db1: 20 04                      |                 local.get 4
 013db3: 41 03                      |                 i32.const 3
 013db5: 6a                         |                 i32.add
 013db6: 2d 00 00                   |                 i32.load8_u 0 0
 013db9: 41 07                      |                 i32.const 7
 013dbb: 74                         |                 i32.shl
 013dbc: 6a                         |                 i32.add
 013dbd: 42 01                      |                 i64.const 1
 013dbf: fe 1f 03 00                |                 i64.atomic.rmw.add 3 0
 013dc3: 1a                         |                 drop
 013dc4: 20 00                      |                 local.get 0
 013dc6: 20 04                      |                 local.get 4
 013dc8: 41 04                      |                 i32.const 4
 013dca: 6a                         |                 i32.add
 013dcb: 2d 00 00                   |                 i32.load8_u 0 0
 013dce: 41 07                      |                 i32.const 7
 013dd0: 74                         |                 i32.shl
 013dd1: 6a                         |                 i32.add
 013dd2: 42 01                      |                 i64.const 1
 013dd4: fe 1f 03 00                |                 i64.atomic.rmw.add 3 0
 013dd8: 1a                         |                 drop
 013dd9: 20 00                      |                 local.get 0
 013ddb: 20 04                      |                 local.get 4
 013ddd: 41 05                      |                 i32.const 5
 013ddf: 6a                         |                 i32.add
 013de0: 2d 00 00                   |                 i32.load8_u 0 0
 013de3: 41 07                      |                 i32.const 7
 013de5: 74                         |                 i32.shl
 013de6: 6a                         |                 i32.add
 013de7: 42 01                      |                 i64.const 1
 013de9: fe 1f 03 00                |                 i64.atomic.rmw.add 3 0
 013ded: 1a                         |                 drop
 013dee: 20 00                      |                 local.get 0
 013df0: 20 04                      |                 local.get 4
 013df2: 41 06                      |                 i32.const 6
 013df4: 6a                         |                 i32.add
 013df5: 2d 00 00                   |                 i32.load8_u 0 0
 013df8: 41 07                      |                 i32.const 7
 013dfa: 74                         |                 i32.shl
 013dfb: 6a                         |                 i32.add
 013dfc: 42 01                      |                 i64.const 1
 013dfe: fe 1f 03 00                |                 i64.atomic.rmw.add 3 0
 013e02: 1a                         |                 drop
 013e03: 20 00                      |                 local.get 0
 013e05: 20 04                      |                 local.get 4
 013e07: 41 07                      |                 i32.const 7
 013e09: 6a                         |                 i32.add
 013e0a: 2d 00 00                   |                 i32.load8_u 0 0
 013e0d: 41 07                      |                 i32.const 7
 013e0f: 74                         |                 i32.shl
 013e10: 6a                         |                 i32.add
 013e11: 42 01                      |                 i64.const 1
 013e13: fe 1f 03 00                |                 i64.atomic.rmw.add 3 0
 013e17: 1a                         |                 drop
 013e18: 20 04                      |                 local.get 4
 013e1a: 41 08                      |                 i32.const 8
 013e1c: 6a                         |                 i32.add
 013e1d: 22 04                      |                 local.tee 4
 013e1f: 20 02                      |                 local.get 2
 013e21: 47                         |                 i32.ne
 013e22: 0d 00                      |                 br_if 0
 013e24: 0b                         |               end
 013e25: 0b                         |             end
 013e26: 20 01                      |             local.get 1
 013e28: 20 05                      |             local.get 5
 013e2a: 6b                         |             i32.sub
 013e2b: 22 01                      |             local.tee 1
 013e2d: 0d 00                      |             br_if 0
 013e2f: 0c 05                      |             br 5
 013e31: 0b                         |           end
 013e32: 0b                         |         end
 013e33: 10 a0 03                   |         call 416 <rayon_core[7650722b9b765dc1]::current_num_threads>
 013e36: 22 03                      |         local.tee 3
 013e38: 20 02                      |         local.get 2
 013e3a: 41 01                      |         i32.const 1
 013e3c: 76                         |         i32.shr_u
 013e3d: 22 02                      |         local.tee 2
 013e3f: 20 03                      |         local.get 3
 013e41: 20 02                      |         local.get 2
 013e43: 4b                         |         i32.gt_u
 013e44: 1b                         |         select
 013e45: 21 03                      |         local.set 3
 013e47: 0b                         |       end
 013e48: 20 06                      |       local.get 6
 013e4a: 20 03                      |       local.get 3
 013e4c: 36 02 08                   |       i32.store 2 8
 013e4f: 20 04                      |       local.get 4
 013e51: 28 02 04                   |       i32.load 2 4
 013e54: 21 03                      |       local.set 3
 013e56: 20 06                      |       local.get 6
 013e58: 20 00                      |       local.get 0
 013e5a: 36 02 10                   |       i32.store 2 16
 013e5d: 20 04                      |       local.get 4
 013e5f: 28 02 00                   |       i32.load 2 0
 013e62: 21 01                      |       local.set 1
 013e64: 20 04                      |       local.get 4
 013e66: 28 02 08                   |       i32.load 2 8
 013e69: 21 02                      |       local.set 2
 013e6b: 20 04                      |       local.get 4
 013e6d: 28 02 0c                   |       i32.load 2 12
 013e70: 21 04                      |       local.set 4
 013e72: 20 06                      |       local.get 6
 013e74: 20 05                      |       local.get 5
 013e76: 36 02 4c                   |       i32.store 2 76
 013e79: 20 06                      |       local.get 6
 013e7b: 20 04                      |       local.get 4
 013e7d: 36 02 48                   |       i32.store 2 72
 013e80: 20 06                      |       local.get 6
 013e82: 20 02                      |       local.get 2
 013e84: 36 02 44                   |       i32.store 2 68
 013e87: 20 06                      |       local.get 6
 013e89: 20 01                      |       local.get 1
 013e8b: 36 02 3c                   |       i32.store 2 60
 013e8e: 20 06                      |       local.get 6
 013e90: 20 05                      |       local.get 5
 013e92: 36 02 30                   |       i32.store 2 48
 013e95: 20 06                      |       local.get 6
 013e97: 20 04                      |       local.get 4
 013e99: 36 02 2c                   |       i32.store 2 44
 013e9c: 20 06                      |       local.get 6
 013e9e: 20 02                      |       local.get 2
 013ea0: 36 02 28                   |       i32.store 2 40
 013ea3: 20 06                      |       local.get 6
 013ea5: 20 02                      |       local.get 2
 013ea7: 20 00                      |       local.get 0
 013ea9: 6c                         |       i32.mul
 013eaa: 22 04                      |       local.tee 4
 013eac: 20 03                      |       local.get 3
 013eae: 20 04                      |       local.get 4
 013eb0: 20 03                      |       local.get 3
 013eb2: 49                         |       i32.lt_u
 013eb3: 1b                         |       select
 013eb4: 22 04                      |       local.tee 4
 013eb6: 36 02 40                   |       i32.store 2 64
 013eb9: 20 06                      |       local.get 6
 013ebb: 20 03                      |       local.get 3
 013ebd: 20 04                      |       local.get 4
 013ebf: 6b                         |       i32.sub
 013ec0: 36 02 24                   |       i32.store 2 36
 013ec3: 20 06                      |       local.get 6
 013ec5: 20 01                      |       local.get 1
 013ec7: 20 04                      |       local.get 4
 013ec9: 6a                         |       i32.add
 013eca: 36 02 20                   |       i32.store 2 32
 013ecd: 23 01                      |       global.get 1 <__tls_base>
 013ecf: 41 28                      |       i32.const 40
 013ed1: 6a                         |       i32.add
 013ed2: 22 00                      |       local.tee 0
 013ed4: 28 02 00                   |       i32.load 2 0
 013ed7: 21 04                      |       local.set 4
 013ed9: 20 06                      |       local.get 6
 013edb: 20 06                      |       local.get 6
 013edd: 41 08                      |       i32.const 8
 013edf: 6a                         |       i32.add
 013ee0: 36 02 38                   |       i32.store 2 56
 013ee3: 20 06                      |       local.get 6
 013ee5: 20 06                      |       local.get 6
 013ee7: 41 10                      |       i32.const 16
 013ee9: 6a                         |       i32.add
 013eea: 36 02 34                   |       i32.store 2 52
 013eed: 20 06                      |       local.get 6
 013eef: 20 06                      |       local.get 6
 013ef1: 41 08                      |       i32.const 8
 013ef3: 6a                         |       i32.add
 013ef4: 36 02 1c                   |       i32.store 2 28
 013ef7: 20 06                      |       local.get 6
 013ef9: 20 06                      |       local.get 6
 013efb: 41 10                      |       i32.const 16
 013efd: 6a                         |       i32.add
 013efe: 36 02 18                   |       i32.store 2 24
 013f01: 20 06                      |       local.get 6
 013f03: 20 06                      |       local.get 6
 013f05: 41 04                      |       i32.const 4
 013f07: 6a                         |       i32.add
 013f08: 36 02 14                   |       i32.store 2 20
 013f0b: 02 40                      |       block
 013f0d: 20 04                      |         local.get 4
 013f0f: 45                         |         i32.eqz
 013f10: 0d 00                      |         br_if 0
 013f12: 20 06                      |         local.get 6
 013f14: 41 14                      |         i32.const 20
 013f16: 6a                         |         i32.add
 013f17: 20 04                      |         local.get 4
 013f19: 41 00                      |         i32.const 0
 013f1b: 10 4a                      |         call 74 <rayon_core[7650722b9b765dc1]::join::join_context::<rayon[599452d85584ec74]::iter::plumbing::bridge_producer_consumer::helper<rayon[599452d85584ec74]::iter::len::MaxLenProducer<rayon[599452d85584ec74]::slice::chunks::ChunksProducer<u8>>, rayon[599452d85584ec74]::iter::for_each::ForEachConsumer<<bench[c9b452c63323ae17]::workloads::histogram::atomic::AtomicHistogram as bench[c9b452c63323ae17]::workloads::workload::Workload>::run::{closure#0}>>::{closure#0}, rayon[599452d85584ec74]::iter::plumbing::bridge_producer_consumer::helper<rayon[599452d85584ec74]::iter::len::MaxLenProducer<rayon[599452d85584ec74]::slice::chunks::ChunksProducer<u8>>, rayon[599452d85584ec74]::iter::for_each::ForEachConsumer<<bench[c9b452c63323ae17]::workloads::histogram::atomic::AtomicHistogram as bench[c9b452c63323ae17]::workloads::workload::Workload>::run::{closure#0}>>::{closure#1}, (), ()>::{closure#0}>
 013f1d: 0c 03                      |         br 3
 013f1f: 0b                         |       end
 013f20: 10 d1 01                   |       call 209 <rayon_core[7650722b9b765dc1]::registry::global_registry>
 013f23: 28 02 00                   |       i32.load 2 0
 013f26: 21 03                      |       local.set 3
 013f28: 20 00                      |       local.get 0
 013f2a: 28 02 00                   |       i32.load 2 0
 013f2d: 22 04                      |       local.tee 4
 013f2f: 45                         |       i32.eqz
 013f30: 0d 01                      |       br_if 1
 013f32: 02 40                      |       block
 013f34: 20 04                      |         local.get 4
 013f36: 28 02 8c 01                |         i32.load 2 140
 013f3a: 20 03                      |         local.get 3
 013f3c: 47                         |         i32.ne
 013f3d: 0d 00                      |         br_if 0
 013f3f: 20 06                      |         local.get 6
 013f41: 41 14                      |         i32.const 20
 013f43: 6a                         |         i32.add
 013f44: 20 04                      |         local.get 4
 013f46: 41 00                      |         i32.const 0
 013f48: 10 4a                      |         call 74 <rayon_core[7650722b9b765dc1]::join::join_context::<rayon[599452d85584ec74]::iter::plumbing::bridge_producer_consumer::helper<rayon[599452d85584ec74]::iter::len::MaxLenProducer<rayon[599452d85584ec74]::slice::chunks::ChunksProducer<u8>>, rayon[599452d85584ec74]::iter::for_each::ForEachConsumer<<bench[c9b452c63323ae17]::workloads::histogram::atomic::AtomicHistogram as bench[c9b452c63323ae17]::workloads::workload::Workload>::run::{closure#0}>>::{closure#0}, rayon[599452d85584ec74]::iter::plumbing::bridge_producer_consumer::helper<rayon[599452d85584ec74]::iter::len::MaxLenProducer<rayon[599452d85584ec74]::slice::chunks::ChunksProducer<u8>>, rayon[599452d85584ec74]::iter::for_each::ForEachConsumer<<bench[c9b452c63323ae17]::workloads::histogram::atomic::AtomicHistogram as bench[c9b452c63323ae17]::workloads::workload::Workload>::run::{closure#0}>>::{closure#1}, (), ()>::{closure#0}>
 013f4a: 0c 03                      |         br 3
 013f4c: 0b                         |       end
 013f4d: 20 03                      |       local.get 3
 013f4f: 41 c0 00                   |       i32.const 64
 013f52: 6a                         |       i32.add
 013f53: 20 04                      |       local.get 4
 013f55: 20 06                      |       local.get 6
 013f57: 41 14                      |       i32.const 20
 013f59: 6a                         |       i32.add
 013f5a: 10 e8 01                   |       call 232 <<rayon_core[7650722b9b765dc1]::registry::Registry>::in_worker_cross::<rayon_core[7650722b9b765dc1]::join::join_context<rayon[599452d85584ec74]::iter::plumbing::bridge_producer_consumer::helper<rayon[599452d85584ec74]::iter::len::MaxLenProducer<rayon[599452d85584ec74]::slice::chunks::ChunksProducer<u8>>, rayon[599452d85584ec74]::iter::for_each::ForEachConsumer<<bench[c9b452c63323ae17]::workloads::histogram::atomic::AtomicHistogram as bench[c9b452c63323ae17]::workloads::workload::Workload>::run::{closure#0}>>::{closure#0}, rayon[599452d85584ec74]::iter::plumbing::bridge_producer_consumer::helper<rayon[599452d85584ec74]::iter::len::MaxLenProducer<rayon[599452d85584ec74]::slice::chunks::ChunksProducer<u8>>, rayon[599452d85584ec74]::iter::for_each::ForEachConsumer<<bench[c9b452c63323ae17]::workloads::histogram::atomic::AtomicHistogram as bench[c9b452c63323ae17]::workloads::workload::Workload>::run::{closure#0}>>::{closure#1}, (), ()>::{closure#0}, ((), ())>>
 013f5d: 0c 02                      |       br 2
 013f5f: 0b                         |     end
 013f60: 41 80 80 c0 00             |     i32.const 1048576
 013f65: 41 37                      |     i32.const 55
 013f67: 41 bc cc c0 00             |     i32.const 1058364
 013f6c: 10 84 03                   |     call 388 <core[44f98dc1fdbe93f7]::panicking::panic_fmt>
 013f6f: 00                         |     unreachable
 013f70: 0b                         |   end
 013f71: 20 03                      |   local.get 3
 013f73: 41 c0 00                   |   i32.const 64
 013f76: 6a                         |   i32.add
 013f77: 20 06                      |   local.get 6
 013f79: 41 14                      |   i32.const 20
 013f7b: 6a                         |   i32.add
 013f7c: 10 98 02                   |   call 280 <<rayon_core[7650722b9b765dc1]::registry::Registry>::in_worker_cold::<rayon_core[7650722b9b765dc1]::join::join_context<rayon[599452d85584ec74]::iter::plumbing::bridge_producer_consumer::helper<rayon[599452d85584ec74]::iter::len::MaxLenProducer<rayon[599452d85584ec74]::slice::chunks::ChunksProducer<u8>>, rayon[599452d85584ec74]::iter::for_each::ForEachConsumer<<bench[c9b452c63323ae17]::workloads::histogram::atomic::AtomicHistogram as bench[c9b452c63323ae17]::workloads::workload::Workload>::run::{closure#0}>>::{closure#0}, rayon[599452d85584ec74]::iter::plumbing::bridge_producer_consumer::helper<rayon[599452d85584ec74]::iter::len::MaxLenProducer<rayon[599452d85584ec74]::slice::chunks::ChunksProducer<u8>>, rayon[599452d85584ec74]::iter::for_each::ForEachConsumer<<bench[c9b452c63323ae17]::workloads::histogram::atomic::AtomicHistogram as bench[c9b452c63323ae17]::workloads::workload::Workload>::run::{closure#0}>>::{closure#1}, (), ()>::{closure#0}, ((), ())>>
 013f7f: 0b                         | end
 013f80: 20 06                      | local.get 6
 013f82: 41 d0 00                   | i32.const 80
 013f85: 6a                         | i32.add
 013f86: 24 00                      | global.set 0 <__stack_pointer>
 013f88: 0b                         | end
