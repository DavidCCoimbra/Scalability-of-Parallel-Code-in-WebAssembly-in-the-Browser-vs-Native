use crate::input::{GrayImage, Palette, few_colors_with, noise};

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum InputKind {
    Noise,
    FewColors { k: usize, palette: Palette },
}

impl InputKind {
    /// k colors spread over the grey levels, the study's input.
    pub const fn few(k: usize) -> Self {
        Self::FewColors {
            k,
            palette: Palette::Spread,
        }
    }

    pub fn name(self) -> &'static str {
        match self {
            Self::Noise => "noise",
            Self::FewColors { .. } => "few",
        }
    }

    pub fn k(self) -> Option<usize> {
        match self {
            Self::Noise => None,
            Self::FewColors { k, .. } => Some(k),
        }
    }

    pub fn palette(self) -> Option<Palette> {
        match self {
            Self::Noise => None,
            Self::FewColors { palette, .. } => Some(palette),
        }
    }

    pub fn image(self, width: usize, height: usize, seed: u64) -> GrayImage {
        match self {
            Self::Noise => noise(width, height, seed),
            Self::FewColors { k, palette } => few_colors_with(width, height, seed, k, palette),
        }
    }
}
