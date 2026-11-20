use crate::workloads::Checksum;

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct GrayImage {
    width: usize,
    height: usize,
    pitch: usize,
    pixels: Vec<u8>,
}

impl GrayImage {
    pub fn from_pixels(width: usize, height: usize, pixels: Vec<u8>) -> Self {
        assert_eq!(pixels.len(), Self::len(width, height), "pixel count");
        Self {
            width,
            height,
            pitch: width,
            pixels,
        }
    }

    pub(super) fn generate(width: usize, height: usize, mut pixel: impl FnMut() -> u8) -> Self {
        let pixels = (0..Self::len(width, height)).map(|_| pixel()).collect();
        Self::from_pixels(width, height, pixels)
    }

    pub fn with_pitch(self, pitch: usize) -> Self {
        assert!(pitch >= self.width, "pitch {pitch} < width {}", self.width);
        let mut pixels = vec![0; Self::len(pitch, self.height)];
        pixels
            .chunks_mut(pitch)
            .zip(self.rows())
            .for_each(|(padded, row)| padded[..self.width].copy_from_slice(row));
        Self {
            pitch,
            pixels,
            ..self
        }
    }

    fn len(width: usize, height: usize) -> usize {
        assert!(width > 0 && height > 0, "image must not be empty");
        width
            .checked_mul(height)
            .expect("image size overflows usize")
    }

    pub fn width(&self) -> usize {
        self.width
    }

    pub fn height(&self) -> usize {
        self.height
    }

    pub fn pitch(&self) -> usize {
        self.pitch
    }

    /// The whole buffer, padding included; equal to the rows back to back when the pitch is
    /// the width.
    pub fn pixels(&self) -> &[u8] {
        &self.pixels
    }

    pub fn row(&self, y: usize) -> &[u8] {
        let start = y * self.pitch;
        &self.pixels[start..start + self.width]
    }

    pub fn rows(&self) -> impl Iterator<Item = &[u8]> {
        (0..self.height).map(|y| self.row(y))
    }

    /// The checksum of the rows without their padding, so a padded image has the fingerprint
    /// of the same image unpadded.
    pub fn fingerprint(&self) -> Checksum {
        Checksum::of_slices(self.rows())
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn from_pixels_keeps_dimensions_and_pixels() {
        let image = GrayImage::from_pixels(3, 2, vec![1, 2, 3, 4, 5, 6]);
        assert_eq!((image.width(), image.height()), (3, 2));
        assert_eq!(image.pixels(), [1, 2, 3, 4, 5, 6]);
        assert_eq!(image.pitch(), 3);
    }

    #[test]
    #[should_panic]
    fn empty_image_is_rejected() {
        GrayImage::from_pixels(0, 0, Vec::new());
    }

    #[test]
    fn row_returns_one_line_of_pixels() {
        let image = GrayImage::from_pixels(3, 2, vec![1, 2, 3, 4, 5, 6]);
        assert_eq!(image.row(1), [4, 5, 6]);
    }

    #[test]
    #[should_panic]
    fn from_pixels_rejects_wrong_length() {
        GrayImage::from_pixels(3, 2, vec![0; 5]);
    }

    #[test]
    fn a_pitch_pads_each_row_and_keeps_the_rows_and_the_fingerprint() {
        let image = GrayImage::from_pixels(3, 2, vec![1, 2, 3, 4, 5, 6]);
        let padded = image.clone().with_pitch(5);
        assert_eq!(padded.pixels(), [1, 2, 3, 0, 0, 4, 5, 6, 0, 0]);
        assert!(padded.rows().eq(image.rows()));
        assert_eq!(padded.fingerprint(), Checksum::of_bytes(image.pixels()));
        assert_eq!(image.fingerprint(), Checksum::of_bytes(image.pixels()));
    }

    #[test]
    #[should_panic]
    fn a_pitch_below_the_width_is_rejected() {
        GrayImage::from_pixels(3, 2, vec![0; 6]).with_pitch(2);
    }
}
