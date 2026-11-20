/// Recorded per run so the analysis can check whether buffer placement explains a difference
/// between runs: addresses equal modulo 4096 can be confused by the CPU (4K aliasing), and the
/// address modulo 64 is the offset in the cache line. In WASM it is the offset in linear memory.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Default)]
pub struct BufferAddresses {
    pub input: Option<usize>,
    pub output: Option<usize>,
}

impl BufferAddresses {
    pub fn of_input(input: &[u8]) -> Self {
        Self {
            input: Some(input.as_ptr() as usize),
            output: None,
        }
    }

    pub fn of_input_and_output(input: &[u8], output: &[u8]) -> Self {
        Self {
            output: Some(output.as_ptr() as usize),
            ..Self::of_input(input)
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn addresses_are_where_the_buffers_start() {
        let (input, output) = (vec![0u8; 8], vec![0u8; 8]);
        let addresses = BufferAddresses::of_input_and_output(&input[2..], &output);
        assert_eq!(addresses.input, Some(input.as_ptr() as usize + 2));
        assert_eq!(addresses.output, Some(output.as_ptr() as usize));
        assert_eq!(BufferAddresses::of_input(&input).output, None);
    }
}
