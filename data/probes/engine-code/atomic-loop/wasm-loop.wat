               loop
                 local.get 0
                 local.get 4
                 i32.load8_u 0 0
                 i32.const 7
                 i32.shl
                 i32.add
                 i64.const 1
                 i64.atomic.rmw.add 3 0
                 drop
                 local.get 0
                 local.get 4
                 i32.const 1
                 i32.add
                 i32.load8_u 0 0
                 i32.const 7
                 i32.shl
                 i32.add
                 i64.const 1
                 i64.atomic.rmw.add 3 0
                 drop
                 local.get 0
                 local.get 4
                 i32.const 2
                 i32.add
                 i32.load8_u 0 0
                 i32.const 7
                 i32.shl
                 i32.add
                 i64.const 1
                 i64.atomic.rmw.add 3 0
                 drop
                 local.get 0
                 local.get 4
                 i32.const 3
                 i32.add
                 i32.load8_u 0 0
                 i32.const 7
                 i32.shl
                 i32.add
                 i64.const 1
                 i64.atomic.rmw.add 3 0
                 drop
                 local.get 0
                 local.get 4
                 i32.const 4
                 i32.add
                 i32.load8_u 0 0
                 i32.const 7
                 i32.shl
                 i32.add
                 i64.const 1
                 i64.atomic.rmw.add 3 0
                 drop
                 local.get 0
                 local.get 4
                 i32.const 5
                 i32.add
                 i32.load8_u 0 0
                 i32.const 7
                 i32.shl
                 i32.add
                 i64.const 1
                 i64.atomic.rmw.add 3 0
                 drop
                 local.get 0
                 local.get 4
                 i32.const 6
                 i32.add
                 i32.load8_u 0 0
                 i32.const 7
                 i32.shl
                 i32.add
                 i64.const 1
                 i64.atomic.rmw.add 3 0
                 drop
                 local.get 0
                 local.get 4
                 i32.const 7
                 i32.add
                 i32.load8_u 0 0
                 i32.const 7
                 i32.shl
                 i32.add
                 i64.const 1
                 i64.atomic.rmw.add 3 0
                 drop
                 local.get 4
                 i32.const 8
                 i32.add
                 local.tee 4
                 local.get 2
                 i32.ne
                 br_if 0
               end
