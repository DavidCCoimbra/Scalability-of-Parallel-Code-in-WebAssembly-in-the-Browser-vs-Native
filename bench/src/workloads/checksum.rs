use super::Fnv1a;

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub struct Checksum(pub u64);

impl Checksum {
    pub fn of_bytes(bytes: &[u8]) -> Self {
        Fnv1a::default().write(bytes).finish()
    }

    /// Callers pass `to_le_bytes`, never `to_ne_bytes`: a fixed byte order makes the checksum
    /// depend only on the values, not on the host CPU. WASM is little-endian by spec and
    /// x86-64 is too, so both give the same bytes today; the fixed order keeps it so on any
    /// host.
    pub fn of_words<const N: usize>(words: impl IntoIterator<Item = [u8; N]>) -> Self {
        words
            .into_iter()
            .fold(Fnv1a::default(), |hash, word| hash.write(&word))
            .finish()
    }

    pub fn of_slices<'a>(slices: impl IntoIterator<Item = &'a [u8]>) -> Self {
        slices
            .into_iter()
            .fold(Fnv1a::default(), Fnv1a::write)
            .finish()
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn fnv1a_of_empty_input_is_the_offset_basis() {
        assert_eq!(Checksum::of_bytes(&[]), Checksum(Fnv1a::OFFSET_BASIS));
    }

    #[test]
    fn fnv1a_matches_reference_value() {
        assert_eq!(Checksum::of_bytes(b"a"), Checksum(0xaf63_dc4c_8601_ec8c));
    }

    #[test]
    fn fnv1a_depends_on_byte_order() {
        assert_ne!(Checksum::of_bytes(&[1, 2]), Checksum::of_bytes(&[2, 1]));
    }

    #[test]
    fn words_hash_like_their_concatenated_bytes() {
        let words = [1u32, 0x0102_0304];
        let bytes: Vec<u8> = words.iter().flat_map(|word| word.to_le_bytes()).collect();
        assert_eq!(
            Checksum::of_words(words.map(u32::to_le_bytes)),
            Checksum::of_bytes(&bytes)
        );
    }

    #[test]
    fn slices_hash_like_their_concatenation() {
        assert_eq!(
            Checksum::of_slices([&b"ab"[..], b"c", b""]),
            Checksum::of_bytes(b"abc")
        );
    }
}
