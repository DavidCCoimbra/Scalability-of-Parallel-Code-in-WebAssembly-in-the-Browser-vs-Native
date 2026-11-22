015752 func[64] <bench[c9b452c63323ae17]::workloads::gaussian::blur_interior>:
 015753: 02 7f                      | local[8..9] type=i32
 015755: 0b 7b                      | local[10..20] type=v128
 015757: 02 40                      | block
 015759: 02 40                      |   block
 01575b: 02 40                      |     block
 01575d: 02 40                      |       block
 01575f: 02 40                      |         block
 015761: 02 40                      |           block
 015763: 02 40                      |             block
 015765: 02 40                      |               block
 015767: 02 40                      |                 block
 015769: 20 07                      |                   local.get 7
 01576b: 20 01                      |                   local.get 1
 01576d: 4b                         |                   i32.gt_u
 01576e: 0d 00                      |                   br_if 0
 015770: 20 07                      |                   local.get 7
 015772: 41 01                      |                   i32.const 1
 015774: 6a                         |                   i32.add
 015775: 21 08                      |                   local.set 8
 015777: 20 07                      |                   local.get 7
 015779: 20 01                      |                   local.get 1
 01577b: 4f                         |                   i32.ge_u
 01577c: 0d 01                      |                   br_if 1
 01577e: 20 07                      |                   local.get 7
 015780: 41 02                      |                   i32.const 2
 015782: 6a                         |                   i32.add
 015783: 22 09                      |                   local.tee 9
 015785: 20 01                      |                   local.get 1
 015787: 4b                         |                   i32.gt_u
 015788: 0d 02                      |                   br_if 2
 01578a: 20 07                      |                   local.get 7
 01578c: 20 03                      |                   local.get 3
 01578e: 4b                         |                   i32.gt_u
 01578f: 0d 03                      |                   br_if 3
 015791: 20 07                      |                   local.get 7
 015793: 20 03                      |                   local.get 3
 015795: 4f                         |                   i32.ge_u
 015796: 0d 04                      |                   br_if 4
 015798: 20 09                      |                   local.get 9
 01579a: 20 03                      |                   local.get 3
 01579c: 4b                         |                   i32.gt_u
 01579d: 0d 05                      |                   br_if 5
 01579f: 20 07                      |                   local.get 7
 0157a1: 20 05                      |                   local.get 5
 0157a3: 4b                         |                   i32.gt_u
 0157a4: 0d 06                      |                   br_if 6
 0157a6: 20 07                      |                   local.get 7
 0157a8: 20 05                      |                   local.get 5
 0157aa: 4f                         |                   i32.ge_u
 0157ab: 0d 07                      |                   br_if 7
 0157ad: 20 09                      |                   local.get 9
 0157af: 20 05                      |                   local.get 5
 0157b1: 4b                         |                   i32.gt_u
 0157b2: 0d 08                      |                   br_if 8
 0157b4: 02 40                      |                   block
 0157b6: 20 07                      |                     local.get 7
 0157b8: 45                         |                     i32.eqz
 0157b9: 0d 00                      |                     br_if 0
 0157bb: 41 00                      |                     i32.const 0
 0157bd: 21 01                      |                     local.set 1
 0157bf: 02 40                      |                     block
 0157c1: 20 07                      |                       local.get 7
 0157c3: 41 10                      |                       i32.const 16
 0157c5: 49                         |                       i32.lt_u
 0157c6: 0d 00                      |                       br_if 0
 0157c8: 20 07                      |                       local.get 7
 0157ca: 41 f0 ff ff ff 07          |                       i32.const 2147483632
 0157d0: 71                         |                       i32.and
 0157d1: 21 01                      |                       local.set 1
 0157d3: 41 00                      |                       i32.const 0
 0157d5: 21 03                      |                       local.set 3
 0157d7: 03 40                      |                       loop
 0157d9: 20 06                      |                         local.get 6
 0157db: 20 03                      |                         local.get 3
 0157dd: 6a                         |                         i32.add
 0157de: 20 00                      |                         local.get 0
 0157e0: 20 03                      |                         local.get 3
 0157e2: 6a                         |                         i32.add
 0157e3: 22 05                      |                         local.tee 5
 0157e5: fd 00 00 00                |                         v128.load 0 0
 0157e9: 22 0a                      |                         local.tee 10
 0157eb: fd 89 01                   |                         i16x8.extend_low_i8x16_u
 0157ee: 20 05                      |                         local.get 5
 0157f0: 41 02                      |                         i32.const 2
 0157f2: 6a                         |                         i32.add
 0157f3: fd 00 00 00                |                         v128.load 0 0
 0157f7: 22 0b                      |                         local.tee 11
 0157f9: fd 89 01                   |                         i16x8.extend_low_i8x16_u
 0157fc: fd 8e 01                   |                         i16x8.add
 0157ff: 20 02                      |                         local.get 2
 015801: 20 03                      |                         local.get 3
 015803: 6a                         |                         i32.add
 015804: 22 09                      |                         local.tee 9
 015806: 41 01                      |                         i32.const 1
 015808: 6a                         |                         i32.add
 015809: fd 00 00 00                |                         v128.load 0 0
 01580d: 22 0c                      |                         local.tee 12
 01580f: fd 89 01                   |                         i16x8.extend_low_i8x16_u
 015812: 41 02                      |                         i32.const 2
 015814: fd 8b 01                   |                         i16x8.shl
 015817: fd 8e 01                   |                         i16x8.add
 01581a: 20 04                      |                         local.get 4
 01581c: 20 03                      |                         local.get 3
 01581e: 6a                         |                         i32.add
 01581f: 22 08                      |                         local.tee 8
 015821: fd 00 00 00                |                         v128.load 0 0
 015825: 22 0d                      |                         local.tee 13
 015827: fd 89 01                   |                         i16x8.extend_low_i8x16_u
 01582a: fd 8e 01                   |                         i16x8.add
 01582d: 20 08                      |                         local.get 8
 01582f: 41 02                      |                         i32.const 2
 015831: 6a                         |                         i32.add
 015832: fd 00 00 00                |                         v128.load 0 0
 015836: 22 0e                      |                         local.tee 14
 015838: fd 89 01                   |                         i16x8.extend_low_i8x16_u
 01583b: fd 8e 01                   |                         i16x8.add
 01583e: 20 09                      |                         local.get 9
 015840: fd 00 00 00                |                         v128.load 0 0
 015844: 22 0f                      |                         local.tee 15
 015846: fd 89 01                   |                         i16x8.extend_low_i8x16_u
 015849: 20 05                      |                         local.get 5
 01584b: 41 01                      |                         i32.const 1
 01584d: 6a                         |                         i32.add
 01584e: fd 00 00 00                |                         v128.load 0 0
 015852: 22 10                      |                         local.tee 16
 015854: fd 89 01                   |                         i16x8.extend_low_i8x16_u
 015857: fd 8e 01                   |                         i16x8.add
 01585a: 20 09                      |                         local.get 9
 01585c: 41 02                      |                         i32.const 2
 01585e: 6a                         |                         i32.add
 01585f: fd 00 00 00                |                         v128.load 0 0
 015863: 22 11                      |                         local.tee 17
 015865: fd 89 01                   |                         i16x8.extend_low_i8x16_u
 015868: fd 8e 01                   |                         i16x8.add
 01586b: 20 08                      |                         local.get 8
 01586d: 41 01                      |                         i32.const 1
 01586f: 6a                         |                         i32.add
 015870: fd 00 00 00                |                         v128.load 0 0
 015874: 22 12                      |                         local.tee 18
 015876: fd 89 01                   |                         i16x8.extend_low_i8x16_u
 015879: fd 8e 01                   |                         i16x8.add
 01587c: 41 01                      |                         i32.const 1
 01587e: fd 8b 01                   |                         i16x8.shl
 015881: fd 8e 01                   |                         i16x8.add
 015884: fd 0c 08 00 08 00 08 00 08 |                         v128.const 0x00080008 0x00080008 0x00080008 0x00080008
 01588d: 00 08 00 08 00 08 00 08 00 | 
 015896: 22 13                      |                         local.tee 19
 015898: fd 8e 01                   |                         i16x8.add
 01589b: 41 04                      |                         i32.const 4
 01589d: fd 8d 01                   |                         i16x8.shr_u
 0158a0: fd 0c ff 00 ff 00 ff 00 ff |                         v128.const 0x00ff00ff 0x00ff00ff 0x00ff00ff 0x00ff00ff
 0158a9: 00 ff 00 ff 00 ff 00 ff 00 | 
 0158b2: 22 14                      |                         local.tee 20
 0158b4: fd 4e                      |                         v128.and
 0158b6: 20 0a                      |                         local.get 10
 0158b8: fd 8a 01                   |                         i16x8.extend_high_i8x16_u
 0158bb: 20 0b                      |                         local.get 11
 0158bd: fd 8a 01                   |                         i16x8.extend_high_i8x16_u
 0158c0: fd 8e 01                   |                         i16x8.add
 0158c3: 20 0c                      |                         local.get 12
 0158c5: fd 8a 01                   |                         i16x8.extend_high_i8x16_u
 0158c8: 41 02                      |                         i32.const 2
 0158ca: fd 8b 01                   |                         i16x8.shl
 0158cd: fd 8e 01                   |                         i16x8.add
 0158d0: 20 0d                      |                         local.get 13
 0158d2: fd 8a 01                   |                         i16x8.extend_high_i8x16_u
 0158d5: fd 8e 01                   |                         i16x8.add
 0158d8: 20 0e                      |                         local.get 14
 0158da: fd 8a 01                   |                         i16x8.extend_high_i8x16_u
 0158dd: fd 8e 01                   |                         i16x8.add
 0158e0: 20 0f                      |                         local.get 15
 0158e2: fd 8a 01                   |                         i16x8.extend_high_i8x16_u
 0158e5: 20 10                      |                         local.get 16
 0158e7: fd 8a 01                   |                         i16x8.extend_high_i8x16_u
 0158ea: fd 8e 01                   |                         i16x8.add
 0158ed: 20 11                      |                         local.get 17
 0158ef: fd 8a 01                   |                         i16x8.extend_high_i8x16_u
 0158f2: fd 8e 01                   |                         i16x8.add
 0158f5: 20 12                      |                         local.get 18
 0158f7: fd 8a 01                   |                         i16x8.extend_high_i8x16_u
 0158fa: fd 8e 01                   |                         i16x8.add
 0158fd: 41 01                      |                         i32.const 1
 0158ff: fd 8b 01                   |                         i16x8.shl
 015902: fd 8e 01                   |                         i16x8.add
 015905: 20 13                      |                         local.get 19
 015907: fd 8e 01                   |                         i16x8.add
 01590a: 41 04                      |                         i32.const 4
 01590c: fd 8d 01                   |                         i16x8.shr_u
 01590f: 20 14                      |                         local.get 20
 015911: fd 4e                      |                         v128.and
 015913: fd 66                      |                         i8x16.narrow_i16x8_u
 015915: fd 0b 00 00                |                         v128.store 0 0
 015919: 20 01                      |                         local.get 1
 01591b: 20 03                      |                         local.get 3
 01591d: 41 10                      |                         i32.const 16
 01591f: 6a                         |                         i32.add
 015920: 22 03                      |                         local.tee 3
 015922: 47                         |                         i32.ne
 015923: 0d 00                      |                         br_if 0
 015925: 0b                         |                       end
 015926: 20 07                      |                       local.get 7
 015928: 20 01                      |                       local.get 1
 01592a: 46                         |                       i32.eq
 01592b: 0d 01                      |                       br_if 1
 01592d: 0b                         |                     end
 01592e: 03 40                      |                     loop
 015930: 20 06                      |                       local.get 6
 015932: 20 01                      |                       local.get 1
 015934: 6a                         |                       i32.add
 015935: 20 00                      |                       local.get 0
 015937: 20 01                      |                       local.get 1
 015939: 6a                         |                       i32.add
 01593a: 22 03                      |                       local.tee 3
 01593c: 2d 00 00                   |                       i32.load8_u 0 0
 01593f: 20 03                      |                       local.get 3
 015941: 41 02                      |                       i32.const 2
 015943: 6a                         |                       i32.add
 015944: 2d 00 00                   |                       i32.load8_u 0 0
 015947: 6a                         |                       i32.add
 015948: 20 02                      |                       local.get 2
 01594a: 20 01                      |                       local.get 1
 01594c: 6a                         |                       i32.add
 01594d: 22 05                      |                       local.tee 5
 01594f: 41 01                      |                       i32.const 1
 015951: 6a                         |                       i32.add
 015952: 2d 00 00                   |                       i32.load8_u 0 0
 015955: 41 02                      |                       i32.const 2
 015957: 74                         |                       i32.shl
 015958: 6a                         |                       i32.add
 015959: 20 04                      |                       local.get 4
 01595b: 20 01                      |                       local.get 1
 01595d: 6a                         |                       i32.add
 01595e: 22 09                      |                       local.tee 9
 015960: 2d 00 00                   |                       i32.load8_u 0 0
 015963: 6a                         |                       i32.add
 015964: 20 09                      |                       local.get 9
 015966: 41 02                      |                       i32.const 2
 015968: 6a                         |                       i32.add
 015969: 2d 00 00                   |                       i32.load8_u 0 0
 01596c: 6a                         |                       i32.add
 01596d: 20 05                      |                       local.get 5
 01596f: 2d 00 00                   |                       i32.load8_u 0 0
 015972: 20 03                      |                       local.get 3
 015974: 41 01                      |                       i32.const 1
 015976: 6a                         |                       i32.add
 015977: 2d 00 00                   |                       i32.load8_u 0 0
 01597a: 6a                         |                       i32.add
 01597b: 20 05                      |                       local.get 5
 01597d: 41 02                      |                       i32.const 2
 01597f: 6a                         |                       i32.add
 015980: 2d 00 00                   |                       i32.load8_u 0 0
 015983: 6a                         |                       i32.add
 015984: 20 09                      |                       local.get 9
 015986: 41 01                      |                       i32.const 1
 015988: 6a                         |                       i32.add
 015989: 2d 00 00                   |                       i32.load8_u 0 0
 01598c: 6a                         |                       i32.add
 01598d: 41 01                      |                       i32.const 1
 01598f: 74                         |                       i32.shl
 015990: 6a                         |                       i32.add
 015991: 41 08                      |                       i32.const 8
 015993: 6a                         |                       i32.add
 015994: 41 04                      |                       i32.const 4
 015996: 76                         |                       i32.shr_u
 015997: 3a 00 00                   |                       i32.store8 0 0
 01599a: 20 00                      |                       local.get 0
 01599c: 41 01                      |                       i32.const 1
 01599e: 6a                         |                       i32.add
 01599f: 21 00                      |                       local.set 0
 0159a1: 20 02                      |                       local.get 2
 0159a3: 41 01                      |                       i32.const 1
 0159a5: 6a                         |                       i32.add
 0159a6: 21 02                      |                       local.set 2
 0159a8: 20 04                      |                       local.get 4
 0159aa: 41 01                      |                       i32.const 1
 0159ac: 6a                         |                       i32.add
 0159ad: 21 04                      |                       local.set 4
 0159af: 20 06                      |                       local.get 6
 0159b1: 41 01                      |                       i32.const 1
 0159b3: 6a                         |                       i32.add
 0159b4: 21 06                      |                       local.set 6
 0159b6: 20 01                      |                       local.get 1
 0159b8: 20 07                      |                       local.get 7
 0159ba: 41 7f                      |                       i32.const 4294967295
 0159bc: 6a                         |                       i32.add
 0159bd: 22 07                      |                       local.tee 7
 0159bf: 47                         |                       i32.ne
 0159c0: 0d 00                      |                       br_if 0
 0159c2: 0b                         |                     end
 0159c3: 0b                         |                   end
 0159c4: 0f                         |                   return
 0159c5: 0b                         |                 end
 0159c6: 41 00                      |                 i32.const 0
 0159c8: 20 07                      |                 local.get 7
 0159ca: 20 01                      |                 local.get 1
 0159cc: 41 ec cb c0 00             |                 i32.const 1058284
 0159d1: 10 a0 01                   |                 call 160 <core[44f98dc1fdbe93f7]::slice::index::slice_index_fail>
 0159d4: 00                         |                 unreachable
 0159d5: 0b                         |               end
 0159d6: 41 01                      |               i32.const 1
 0159d8: 20 08                      |               local.get 8
 0159da: 20 01                      |               local.get 1
 0159dc: 41 dc cb c0 00             |               i32.const 1058268
 0159e1: 10 a0 01                   |               call 160 <core[44f98dc1fdbe93f7]::slice::index::slice_index_fail>
 0159e4: 00                         |               unreachable
 0159e5: 0b                         |             end
 0159e6: 41 02                      |             i32.const 2
 0159e8: 20 09                      |             local.get 9
 0159ea: 20 01                      |             local.get 1
 0159ec: 41 cc cb c0 00             |             i32.const 1058252
 0159f1: 10 a0 01                   |             call 160 <core[44f98dc1fdbe93f7]::slice::index::slice_index_fail>
 0159f4: 00                         |             unreachable
 0159f5: 0b                         |           end
 0159f6: 41 00                      |           i32.const 0
 0159f8: 20 07                      |           local.get 7
 0159fa: 20 03                      |           local.get 3
 0159fc: 41 ec ca c0 00             |           i32.const 1058156
 015a01: 10 a0 01                   |           call 160 <core[44f98dc1fdbe93f7]::slice::index::slice_index_fail>
 015a04: 00                         |           unreachable
 015a05: 0b                         |         end
 015a06: 41 01                      |         i32.const 1
 015a08: 20 08                      |         local.get 8
 015a0a: 20 03                      |         local.get 3
 015a0c: 41 fc ca c0 00             |         i32.const 1058172
 015a11: 10 a0 01                   |         call 160 <core[44f98dc1fdbe93f7]::slice::index::slice_index_fail>
 015a14: 00                         |         unreachable
 015a15: 0b                         |       end
 015a16: 41 02                      |       i32.const 2
 015a18: 20 09                      |       local.get 9
 015a1a: 20 03                      |       local.get 3
 015a1c: 41 8c cb c0 00             |       i32.const 1058188
 015a21: 10 a0 01                   |       call 160 <core[44f98dc1fdbe93f7]::slice::index::slice_index_fail>
 015a24: 00                         |       unreachable
 015a25: 0b                         |     end
 015a26: 41 00                      |     i32.const 0
 015a28: 20 07                      |     local.get 7
 015a2a: 20 05                      |     local.get 5
 015a2c: 41 9c cb c0 00             |     i32.const 1058204
 015a31: 10 a0 01                   |     call 160 <core[44f98dc1fdbe93f7]::slice::index::slice_index_fail>
 015a34: 00                         |     unreachable
 015a35: 0b                         |   end
 015a36: 41 01                      |   i32.const 1
 015a38: 20 08                      |   local.get 8
 015a3a: 20 05                      |   local.get 5
 015a3c: 41 ac cb c0 00             |   i32.const 1058220
 015a41: 10 a0 01                   |   call 160 <core[44f98dc1fdbe93f7]::slice::index::slice_index_fail>
 015a44: 00                         |   unreachable
 015a45: 0b                         | end
 015a46: 41 02                      | i32.const 2
 015a48: 20 09                      | local.get 9
 015a4a: 20 05                      | local.get 5
 015a4c: 41 bc cb c0 00             | i32.const 1058236
 015a51: 10 a0 01                   | call 160 <core[44f98dc1fdbe93f7]::slice::index::slice_index_fail>
 015a54: 00                         | unreachable
 015a55: 0b                         | end
