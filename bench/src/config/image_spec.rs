use crate::experiment::InputKind;
use crate::input::GrayImage;

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub struct ImageSpec {
    pub input: InputKind,
    pub width: usize,
    pub height: usize,
    pub seed: u64,
    /// Bytes from one row to the next; None stores the rows back to back. Extra: no measured
    /// campaign sets it.
    pub pitch: Option<usize>,
}

impl ImageSpec {
    pub fn image(self) -> GrayImage {
        let image = self.input.image(self.width, self.height, self.seed);
        match self.pitch {
            Some(pitch) => image.with_pitch(pitch),
            None => image,
        }
    }

    pub fn row_stride(self) -> usize {
        self.pitch.unwrap_or(self.width)
    }
}
