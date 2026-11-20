mod generators;
mod gray_image;
mod palette;
mod split_mix64;

pub use generators::{few_colors, few_colors_with, noise};
pub use gray_image::GrayImage;
pub use palette::Palette;
pub use split_mix64::SplitMix64;

pub const SEED: u64 = 0x5EED;
pub const MAX_COLORS: usize = 1 << u8::BITS;
