use super::Checksum;

/// 64-bit FNV-1a: http://www.isthe.com/chongo/tech/comp/fnv/
/// Fed piece by piece so a checksum can stream over rows or counters without building a Vec.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub struct Fnv1a(u64);

impl Fnv1a {
    pub(super) const OFFSET_BASIS: u64 = 0xcbf2_9ce4_8422_2325;
    const PRIME: u64 = 0x0000_0100_0000_01b3;

    pub fn write(self, bytes: &[u8]) -> Self {
        Self(bytes.iter().fold(self.0, |hash, &byte| {
            (hash ^ u64::from(byte)).wrapping_mul(Self::PRIME)
        }))
    }

    pub fn finish(self) -> Checksum {
        Checksum(self.0)
    }
}

impl Default for Fnv1a {
    fn default() -> Self {
        Self(Self::OFFSET_BASIS)
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn writing_in_pieces_equals_writing_at_once() {
        let whole = Fnv1a::default().write(b"abcdef").finish();
        let pieces = Fnv1a::default()
            .write(b"ab")
            .write(b"")
            .write(b"cdef")
            .finish();
        assert_eq!(pieces, whole);
    }
}
