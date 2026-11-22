                 loop
                   local.get 6
                   local.get 2
                   local.get 1
                   local.get 2
                   local.get 1
                   i32.lt_u
                   select
                   local.tee 16
                   i32.gt_u
                   br_if 5
                   block
                     local.get 15
                     local.get 15
                     i32.const 0
                     i32.ne
                     i32.sub
                     local.get 1
                     i32.mul
                     local.tee 17
                     local.get 6
                     i32.add
                     local.tee 0
                     local.get 17
                     i32.ge_u
                     br_if 0
                     local.get 17
                     local.set 1
                     br 8
                   end
                   block
                     local.get 0
                     local.get 5
                     i32.le_u
                     br_if 0
                     local.get 17
                     local.set 1
                     br 8
                   end
                   local.get 6
                   local.get 3
                   i32.add
                   local.tee 0
                   local.get 6
                   i32.lt_u
                   br_if 3
                   local.get 0
                   local.get 5
                   i32.gt_u
                   br_if 3
                   block
                     local.get 14
                     local.get 4
                     local.get 14
                     local.get 4
                     i32.lt_u
                     select
                     local.get 1
                     i32.mul
                     local.tee 18
                     local.get 6
                     i32.add
                     local.tee 0
                     local.get 18
                     i32.ge_u
                     br_if 0
                     local.get 18
                     local.set 1
                     br 8
                   end
                   block
                     local.get 0
                     local.get 5
                     i32.le_u
                     br_if 0
                     local.get 18
                     local.set 1
                     br 8
                   end
                   local.get 2
                   local.get 16
                   i32.sub
                   local.set 2
                   local.get 9
                   local.get 10
                   local.get 3
                   i32.add
                   local.tee 19
                   i32.load8_u 0 0
                   local.tee 20
                   i32.const 2
                   i32.shl
                   local.get 10
                   local.get 18
                   i32.add
                   local.tee 0
                   i32.load8_u 0 0
                   local.tee 18
                   i32.add
                   local.get 10
                   local.get 17
                   i32.add
                   local.tee 17
                   local.get 8
                   i32.add
                   i32.load8_u 0 0
                   i32.add
                   local.get 17
                   i32.load8_u 0 0
                   i32.const 3
                   i32.mul
                   i32.add
                   local.get 11
                   local.get 3
                   i32.add
                   i32.load8_u 0 0
                   local.get 20
                   i32.add
                   local.get 18
                   i32.add
                   i32.const 1
                   i32.shl
                   i32.add
                   local.get 0
                   local.get 8
                   i32.add
                   i32.load8_u 0 0
                   i32.add
                   i32.const 8
                   i32.add
                   i32.const 4
                   i32.shr_u
                   i32.store8 0 0
                   block
                     local.get 7
                     i32.eqz
                     br_if 0
                     local.get 9
                     local.get 7
                     i32.add
                     local.get 17
                     local.get 12
                     i32.add
                     i32.load8_u 0 0
                     local.get 17
                     local.get 7
                     i32.add
                     i32.load8_u 0 0
                     local.tee 18
                     i32.add
                     local.get 13
                     local.get 3
                     i32.add
                     local.tee 20
                     i32.const 1
                     i32.add
                     i32.load8_u 0 0
                     local.tee 21
                     i32.const 2
                     i32.shl
                     i32.add
                     local.get 0
                     local.get 12
                     i32.add
                     i32.load8_u 0 0
                     i32.add
                     local.get 0
                     local.get 7
                     i32.add
                     i32.load8_u 0 0
                     local.tee 22
                     i32.add
                     local.get 20
                     i32.load8_u 0 0
                     local.get 18
                     i32.add
                     local.get 21
                     i32.add
                     local.get 22
                     i32.add
                     i32.const 1
                     i32.shl
                     i32.add
                     i32.const 8
                     i32.add
                     i32.const 4
                     i32.shr_u
                     i32.store8 0 0
                     local.get 17
                     local.get 6
                     local.get 19
                     local.get 6
                     local.get 0
                     local.get 6
                     local.get 9
                     i32.const 1
                     i32.add
                     local.get 12
                     call 64 <bench[c9b452c63323ae17]::workloads::gaussian::blur_interior>
                   end
                   local.get 9
                   local.get 16
                   i32.add
                   local.set 9
                   local.get 15
                   i32.const 1
                   i32.add
                   local.set 15
                   local.get 14
                   i32.const 1
                   i32.add
                   local.set 14
                   local.get 3
                   local.get 1
                   i32.add
                   local.set 3
                   local.get 2
                   br_if 0
                 end
