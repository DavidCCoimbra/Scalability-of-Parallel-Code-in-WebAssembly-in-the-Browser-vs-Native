use std::str::FromStr;

use super::{UnknownName, parse_named};

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum Environment {
    Native,
    Chrome,
    Firefox,
}

impl Environment {
    pub(super) const ALL: [Self; 3] = [Self::Native, Self::Chrome, Self::Firefox];

    pub fn name(self) -> &'static str {
        match self {
            Self::Native => "native",
            Self::Chrome => "chrome",
            Self::Firefox => "firefox",
        }
    }
}

impl FromStr for Environment {
    type Err = UnknownName;

    fn from_str(name: &str) -> Result<Self, Self::Err> {
        parse_named(name, &Self::ALL, Self::name)
    }
}
