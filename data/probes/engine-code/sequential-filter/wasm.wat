015a58 func[65] <<bench[c9b452c63323ae17]::workloads::gaussian::sequential::SequentialBlur as bench[c9b452c63323ae17]::workloads::workload::Workload>::run>:
 015a59: 16 7f                      | local[1..22] type=i32
 015a5b: 02 40                      | block
 015a5d: 02 40                      |   block
 015a5f: 02 40                      |     block
 015a61: 20 00                      |       local.get 0
 015a63: 28 02 14                   |       i32.load 2 20
 015a66: 22 01                      |       local.tee 1
 015a68: 45                         |       i32.eqz
 015a69: 0d 00                      |       br_if 0
 015a6b: 02 40                      |       block
 015a6d: 02 40                      |         block
 015a6f: 02 40                      |           block
 015a71: 02 40                      |             block
 015a73: 02 40                      |               block
 015a75: 20 00                      |                 local.get 0
 015a77: 28 02 20                   |                 i32.load 2 32
 015a7a: 22 02                      |                 local.tee 2
 015a7c: 45                         |                 i32.eqz
 015a7d: 0d 00                      |                 br_if 0
 015a7f: 41 00                      |                 i32.const 0
 015a81: 21 03                      |                 local.set 3
 015a83: 20 00                      |                 local.get 0
 015a85: 28 02 10                   |                 i32.load 2 16
 015a88: 41 7f                      |                 i32.const 4294967295
 015a8a: 6a                         |                 i32.add
 015a8b: 21 04                      |                 local.set 4
 015a8d: 20 00                      |                 local.get 0
 015a8f: 28 02 08                   |                 i32.load 2 8
 015a92: 21 05                      |                 local.set 5
 015a94: 02 40                      |                 block
 015a96: 20 00                      |                   local.get 0
 015a98: 28 02 0c                   |                   i32.load 2 12
 015a9b: 22 06                      |                   local.tee 6
 015a9d: 0d 00                      |                   br_if 0
 015a9f: 20 04                      |                   local.get 4
 015aa1: 45                         |                   i32.eqz
 015aa2: 0d 08                      |                   br_if 8
 015aa4: 20 01                      |                   local.get 1
 015aa6: 21 00                      |                   local.set 0
 015aa8: 20 01                      |                   local.get 1
 015aaa: 20 05                      |                   local.get 5
 015aac: 4b                         |                   i32.gt_u
 015aad: 0d 07                      |                   br_if 7
 015aaf: 0c 08                      |                   br 8
 015ab1: 0b                         |                 end
 015ab2: 20 06                      |                 local.get 6
 015ab4: 20 06                      |                 local.get 6
 015ab6: 41 7f                      |                 i32.const 4294967295
 015ab8: 6a                         |                 i32.add
 015ab9: 22 07                      |                 local.tee 7
 015abb: 41 00                      |                 i32.const 0
 015abd: 47                         |                 i32.ne
 015abe: 22 08                      |                 local.tee 8
 015ac0: 4d                         |                 i32.le_u
 015ac1: 0d 01                      |                 br_if 1
 015ac3: 20 00                      |                 local.get 0
 015ac5: 28 02 1c                   |                 i32.load 2 28
 015ac8: 21 09                      |                 local.set 9
 015aca: 20 00                      |                 local.get 0
 015acc: 28 02 04                   |                 i32.load 2 4
 015acf: 22 0a                      |                 local.tee 10
 015ad1: 20 08                      |                 local.get 8
 015ad3: 6a                         |                 i32.add
 015ad4: 21 0b                      |                 local.set 11
 015ad6: 20 0a                      |                 local.get 10
 015ad8: 20 06                      |                 local.get 6
 015ada: 41 7e                      |                 i32.const 4294967294
 015adc: 6a                         |                 i32.add
 015add: 22 0c                      |                 local.tee 12
 015adf: 6a                         |                 i32.add
 015ae0: 21 0d                      |                 local.set 13
 015ae2: 41 01                      |                 i32.const 1
 015ae4: 21 0e                      |                 local.set 14
 015ae6: 41 00                      |                 i32.const 0
 015ae8: 21 03                      |                 local.set 3
 015aea: 41 00                      |                 i32.const 0
 015aec: 21 0f                      |                 local.set 15
 015aee: 03 40                      |                 loop
 015af0: 20 06                      |                   local.get 6
 015af2: 20 02                      |                   local.get 2
 015af4: 20 01                      |                   local.get 1
 015af6: 20 02                      |                   local.get 2
 015af8: 20 01                      |                   local.get 1
 015afa: 49                         |                   i32.lt_u
 015afb: 1b                         |                   select
 015afc: 22 10                      |                   local.tee 16
 015afe: 4b                         |                   i32.gt_u
 015aff: 0d 05                      |                   br_if 5
 015b01: 02 40                      |                   block
 015b03: 20 0f                      |                     local.get 15
 015b05: 20 0f                      |                     local.get 15
 015b07: 41 00                      |                     i32.const 0
 015b09: 47                         |                     i32.ne
 015b0a: 6b                         |                     i32.sub
 015b0b: 20 01                      |                     local.get 1
 015b0d: 6c                         |                     i32.mul
 015b0e: 22 11                      |                     local.tee 17
 015b10: 20 06                      |                     local.get 6
 015b12: 6a                         |                     i32.add
 015b13: 22 00                      |                     local.tee 0
 015b15: 20 11                      |                     local.get 17
 015b17: 4f                         |                     i32.ge_u
 015b18: 0d 00                      |                     br_if 0
 015b1a: 20 11                      |                     local.get 17
 015b1c: 21 01                      |                     local.set 1
 015b1e: 0c 08                      |                     br 8
 015b20: 0b                         |                   end
 015b21: 02 40                      |                   block
 015b23: 20 00                      |                     local.get 0
 015b25: 20 05                      |                     local.get 5
 015b27: 4d                         |                     i32.le_u
 015b28: 0d 00                      |                     br_if 0
 015b2a: 20 11                      |                     local.get 17
 015b2c: 21 01                      |                     local.set 1
 015b2e: 0c 08                      |                     br 8
 015b30: 0b                         |                   end
 015b31: 20 06                      |                   local.get 6
 015b33: 20 03                      |                   local.get 3
 015b35: 6a                         |                   i32.add
 015b36: 22 00                      |                   local.tee 0
 015b38: 20 06                      |                   local.get 6
 015b3a: 49                         |                   i32.lt_u
 015b3b: 0d 03                      |                   br_if 3
 015b3d: 20 00                      |                   local.get 0
 015b3f: 20 05                      |                   local.get 5
 015b41: 4b                         |                   i32.gt_u
 015b42: 0d 03                      |                   br_if 3
 015b44: 02 40                      |                   block
 015b46: 20 0e                      |                     local.get 14
 015b48: 20 04                      |                     local.get 4
 015b4a: 20 0e                      |                     local.get 14
 015b4c: 20 04                      |                     local.get 4
 015b4e: 49                         |                     i32.lt_u
 015b4f: 1b                         |                     select
 015b50: 20 01                      |                     local.get 1
 015b52: 6c                         |                     i32.mul
 015b53: 22 12                      |                     local.tee 18
 015b55: 20 06                      |                     local.get 6
 015b57: 6a                         |                     i32.add
 015b58: 22 00                      |                     local.tee 0
 015b5a: 20 12                      |                     local.get 18
 015b5c: 4f                         |                     i32.ge_u
 015b5d: 0d 00                      |                     br_if 0
 015b5f: 20 12                      |                     local.get 18
 015b61: 21 01                      |                     local.set 1
 015b63: 0c 08                      |                     br 8
 015b65: 0b                         |                   end
 015b66: 02 40                      |                   block
 015b68: 20 00                      |                     local.get 0
 015b6a: 20 05                      |                     local.get 5
 015b6c: 4d                         |                     i32.le_u
 015b6d: 0d 00                      |                     br_if 0
 015b6f: 20 12                      |                     local.get 18
 015b71: 21 01                      |                     local.set 1
 015b73: 0c 08                      |                     br 8
 015b75: 0b                         |                   end
 015b76: 20 02                      |                   local.get 2
 015b78: 20 10                      |                   local.get 16
 015b7a: 6b                         |                   i32.sub
 015b7b: 21 02                      |                   local.set 2
 015b7d: 20 09                      |                   local.get 9
 015b7f: 20 0a                      |                   local.get 10
 015b81: 20 03                      |                   local.get 3
 015b83: 6a                         |                   i32.add
 015b84: 22 13                      |                   local.tee 19
 015b86: 2d 00 00                   |                   i32.load8_u 0 0
 015b89: 22 14                      |                   local.tee 20
 015b8b: 41 02                      |                   i32.const 2
 015b8d: 74                         |                   i32.shl
 015b8e: 20 0a                      |                   local.get 10
 015b90: 20 12                      |                   local.get 18
 015b92: 6a                         |                   i32.add
 015b93: 22 00                      |                   local.tee 0
 015b95: 2d 00 00                   |                   i32.load8_u 0 0
 015b98: 22 12                      |                   local.tee 18
 015b9a: 6a                         |                   i32.add
 015b9b: 20 0a                      |                   local.get 10
 015b9d: 20 11                      |                   local.get 17
 015b9f: 6a                         |                   i32.add
 015ba0: 22 11                      |                   local.tee 17
 015ba2: 20 08                      |                   local.get 8
 015ba4: 6a                         |                   i32.add
 015ba5: 2d 00 00                   |                   i32.load8_u 0 0
 015ba8: 6a                         |                   i32.add
 015ba9: 20 11                      |                   local.get 17
 015bab: 2d 00 00                   |                   i32.load8_u 0 0
 015bae: 41 03                      |                   i32.const 3
 015bb0: 6c                         |                   i32.mul
 015bb1: 6a                         |                   i32.add
 015bb2: 20 0b                      |                   local.get 11
 015bb4: 20 03                      |                   local.get 3
 015bb6: 6a                         |                   i32.add
 015bb7: 2d 00 00                   |                   i32.load8_u 0 0
 015bba: 20 14                      |                   local.get 20
 015bbc: 6a                         |                   i32.add
 015bbd: 20 12                      |                   local.get 18
 015bbf: 6a                         |                   i32.add
 015bc0: 41 01                      |                   i32.const 1
 015bc2: 74                         |                   i32.shl
 015bc3: 6a                         |                   i32.add
 015bc4: 20 00                      |                   local.get 0
 015bc6: 20 08                      |                   local.get 8
 015bc8: 6a                         |                   i32.add
 015bc9: 2d 00 00                   |                   i32.load8_u 0 0
 015bcc: 6a                         |                   i32.add
 015bcd: 41 08                      |                   i32.const 8
 015bcf: 6a                         |                   i32.add
 015bd0: 41 04                      |                   i32.const 4
 015bd2: 76                         |                   i32.shr_u
 015bd3: 3a 00 00                   |                   i32.store8 0 0
 015bd6: 02 40                      |                   block
 015bd8: 20 07                      |                     local.get 7
 015bda: 45                         |                     i32.eqz
 015bdb: 0d 00                      |                     br_if 0
 015bdd: 20 09                      |                     local.get 9
 015bdf: 20 07                      |                     local.get 7
 015be1: 6a                         |                     i32.add
 015be2: 20 11                      |                     local.get 17
 015be4: 20 0c                      |                     local.get 12
 015be6: 6a                         |                     i32.add
 015be7: 2d 00 00                   |                     i32.load8_u 0 0
 015bea: 20 11                      |                     local.get 17
 015bec: 20 07                      |                     local.get 7
 015bee: 6a                         |                     i32.add
 015bef: 2d 00 00                   |                     i32.load8_u 0 0
 015bf2: 22 12                      |                     local.tee 18
 015bf4: 6a                         |                     i32.add
 015bf5: 20 0d                      |                     local.get 13
 015bf7: 20 03                      |                     local.get 3
 015bf9: 6a                         |                     i32.add
 015bfa: 22 14                      |                     local.tee 20
 015bfc: 41 01                      |                     i32.const 1
 015bfe: 6a                         |                     i32.add
 015bff: 2d 00 00                   |                     i32.load8_u 0 0
 015c02: 22 15                      |                     local.tee 21
 015c04: 41 02                      |                     i32.const 2
 015c06: 74                         |                     i32.shl
 015c07: 6a                         |                     i32.add
 015c08: 20 00                      |                     local.get 0
 015c0a: 20 0c                      |                     local.get 12
 015c0c: 6a                         |                     i32.add
 015c0d: 2d 00 00                   |                     i32.load8_u 0 0
 015c10: 6a                         |                     i32.add
 015c11: 20 00                      |                     local.get 0
 015c13: 20 07                      |                     local.get 7
 015c15: 6a                         |                     i32.add
 015c16: 2d 00 00                   |                     i32.load8_u 0 0
 015c19: 22 16                      |                     local.tee 22
 015c1b: 6a                         |                     i32.add
 015c1c: 20 14                      |                     local.get 20
 015c1e: 2d 00 00                   |                     i32.load8_u 0 0
 015c21: 20 12                      |                     local.get 18
 015c23: 6a                         |                     i32.add
 015c24: 20 15                      |                     local.get 21
 015c26: 6a                         |                     i32.add
 015c27: 20 16                      |                     local.get 22
 015c29: 6a                         |                     i32.add
 015c2a: 41 01                      |                     i32.const 1
 015c2c: 74                         |                     i32.shl
 015c2d: 6a                         |                     i32.add
 015c2e: 41 08                      |                     i32.const 8
 015c30: 6a                         |                     i32.add
 015c31: 41 04                      |                     i32.const 4
 015c33: 76                         |                     i32.shr_u
 015c34: 3a 00 00                   |                     i32.store8 0 0
 015c37: 20 11                      |                     local.get 17
 015c39: 20 06                      |                     local.get 6
 015c3b: 20 13                      |                     local.get 19
 015c3d: 20 06                      |                     local.get 6
 015c3f: 20 00                      |                     local.get 0
 015c41: 20 06                      |                     local.get 6
 015c43: 20 09                      |                     local.get 9
 015c45: 41 01                      |                     i32.const 1
 015c47: 6a                         |                     i32.add
 015c48: 20 0c                      |                     local.get 12
 015c4a: 10 40                      |                     call 64 <bench[c9b452c63323ae17]::workloads::gaussian::blur_interior>
 015c4c: 0b                         |                   end
 015c4d: 20 09                      |                   local.get 9
 015c4f: 20 10                      |                   local.get 16
 015c51: 6a                         |                   i32.add
 015c52: 21 09                      |                   local.set 9
 015c54: 20 0f                      |                   local.get 15
 015c56: 41 01                      |                   i32.const 1
 015c58: 6a                         |                   i32.add
 015c59: 21 0f                      |                   local.set 15
 015c5b: 20 0e                      |                   local.get 14
 015c5d: 41 01                      |                   i32.const 1
 015c5f: 6a                         |                   i32.add
 015c60: 21 0e                      |                   local.set 14
 015c62: 20 03                      |                   local.get 3
 015c64: 20 01                      |                   local.get 1
 015c66: 6a                         |                   i32.add
 015c67: 21 03                      |                   local.set 3
 015c69: 20 02                      |                   local.get 2
 015c6b: 0d 00                      |                   br_if 0
 015c6d: 0b                         |                 end
 015c6e: 0b                         |               end
 015c6f: 0f                         |               return
 015c70: 0b                         |             end
 015c71: 20 05                      |             local.get 5
 015c73: 0d 01                      |             br_if 1
 015c75: 41 01                      |             i32.const 1
 015c77: 21 00                      |             local.set 0
 015c79: 41 00                      |             i32.const 0
 015c7b: 21 01                      |             local.set 1
 015c7d: 0c 04                      |             br 4
 015c7f: 0b                         |           end
 015c80: 20 03                      |           local.get 3
 015c82: 21 01                      |           local.set 1
 015c84: 0c 03                      |           br 3
 015c86: 0b                         |         end
 015c87: 41 01                      |         i32.const 1
 015c89: 21 03                      |         local.set 3
 015c8b: 20 01                      |         local.get 1
 015c8d: 41 00                      |         i32.const 0
 015c8f: 20 04                      |         local.get 4
 015c91: 1b                         |         select
 015c92: 22 00                      |         local.tee 0
 015c94: 20 05                      |         local.get 5
 015c96: 49                         |         i32.lt_u
 015c97: 0d 03                      |         br_if 3
 015c99: 20 00                      |         local.get 0
 015c9b: 41 01                      |         i32.const 1
 015c9d: 6a                         |         i32.add
 015c9e: 21 00                      |         local.set 0
 015ca0: 0c 02                      |         br 2
 015ca2: 0b                         |       end
 015ca3: 41 00                      |       i32.const 0
 015ca5: 20 06                      |       local.get 6
 015ca7: 20 10                      |       local.get 16
 015ca9: 41 84 bf c0 00             |       i32.const 1056644
 015cae: 10 a0 01                   |       call 160 <core[44f98dc1fdbe93f7]::slice::index::slice_index_fail>
 015cb1: 00                         |       unreachable
 015cb2: 0b                         |     end
 015cb3: 41 80 80 c0 00             |     i32.const 1048576
 015cb8: 41 37                      |     i32.const 55
 015cba: 41 c8 cf c0 00             |     i32.const 1058760
 015cbf: 10 84 03                   |     call 388 <core[44f98dc1fdbe93f7]::panicking::panic_fmt>
 015cc2: 00                         |     unreachable
 015cc3: 0b                         |   end
 015cc4: 20 01                      |   local.get 1
 015cc6: 20 00                      |   local.get 0
 015cc8: 20 05                      |   local.get 5
 015cca: 41 e8 c2 c0 00             |   i32.const 1057128
 015ccf: 10 a0 01                   |   call 160 <core[44f98dc1fdbe93f7]::slice::index::slice_index_fail>
 015cd2: 00                         |   unreachable
 015cd3: 0b                         | end
 015cd4: 20 03                      | local.get 3
 015cd6: 20 06                      | local.get 6
 015cd8: 41 a8 bd c0 00             | i32.const 1056424
 015cdd: 10 ed 02                   | call 365 <core[44f98dc1fdbe93f7]::panicking::panic_bounds_check>
 015ce0: 00                         | unreachable
 015ce1: 0b                         | end
