/// Bytes of WASM linear memory, or of the native resident set; None where the host cannot tell.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Default)]
pub struct MemorySizes {
    pub before_warmup: Option<u64>,
    pub after_measured: Option<u64>,
}
