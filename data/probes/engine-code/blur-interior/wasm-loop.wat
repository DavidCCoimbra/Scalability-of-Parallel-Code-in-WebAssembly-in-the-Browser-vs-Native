                       loop
                         local.get 6
                         local.get 3
                         i32.add
                         local.get 0
                         local.get 3
                         i32.add
                         local.tee 5
                         v128.load 0 0
                         local.tee 10
                         i16x8.extend_low_i8x16_u
                         local.get 5
                         i32.const 2
                         i32.add
                         v128.load 0 0
                         local.tee 11
                         i16x8.extend_low_i8x16_u
                         i16x8.add
                         local.get 2
                         local.get 3
                         i32.add
                         local.tee 9
                         i32.const 1
                         i32.add
                         v128.load 0 0
                         local.tee 12
                         i16x8.extend_low_i8x16_u
                         i32.const 2
                         i16x8.shl
                         i16x8.add
                         local.get 4
                         local.get 3
                         i32.add
                         local.tee 8
                         v128.load 0 0
                         local.tee 13
                         i16x8.extend_low_i8x16_u
                         i16x8.add
                         local.get 8
                         i32.const 2
                         i32.add
                         v128.load 0 0
                         local.tee 14
                         i16x8.extend_low_i8x16_u
                         i16x8.add
                         local.get 9
                         v128.load 0 0
                         local.tee 15
                         i16x8.extend_low_i8x16_u
                         local.get 5
                         i32.const 1
                         i32.add
                         v128.load 0 0
                         local.tee 16
                         i16x8.extend_low_i8x16_u
                         i16x8.add
                         local.get 9
                         i32.const 2
                         i32.add
                         v128.load 0 0
                         local.tee 17
                         i16x8.extend_low_i8x16_u
                         i16x8.add
                         local.get 8
                         i32.const 1
                         i32.add
                         v128.load 0 0
                         local.tee 18
                         i16x8.extend_low_i8x16_u
                         i16x8.add
                         i32.const 1
                         i16x8.shl
                         i16x8.add
                         v128.const 0x00080008 0x00080008 0x00080008 0x00080008

                         local.tee 19
                         i16x8.add
                         i32.const 4
                         i16x8.shr_u
                         v128.const 0x00ff00ff 0x00ff00ff 0x00ff00ff 0x00ff00ff

                         local.tee 20
                         v128.and
                         local.get 10
                         i16x8.extend_high_i8x16_u
                         local.get 11
                         i16x8.extend_high_i8x16_u
                         i16x8.add
                         local.get 12
                         i16x8.extend_high_i8x16_u
                         i32.const 2
                         i16x8.shl
                         i16x8.add
                         local.get 13
                         i16x8.extend_high_i8x16_u
                         i16x8.add
                         local.get 14
                         i16x8.extend_high_i8x16_u
                         i16x8.add
                         local.get 15
                         i16x8.extend_high_i8x16_u
                         local.get 16
                         i16x8.extend_high_i8x16_u
                         i16x8.add
                         local.get 17
                         i16x8.extend_high_i8x16_u
                         i16x8.add
                         local.get 18
                         i16x8.extend_high_i8x16_u
                         i16x8.add
                         i32.const 1
                         i16x8.shl
                         i16x8.add
                         local.get 19
                         i16x8.add
                         i32.const 4
                         i16x8.shr_u
                         local.get 20
                         v128.and
                         i8x16.narrow_i16x8_u
                         v128.store 0 0
                         local.get 1
                         local.get 3
                         i32.const 16
                         i32.add
                         local.tee 3
                         i32.ne
                         br_if 0
                       end
