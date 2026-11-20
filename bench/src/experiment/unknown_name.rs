use std::fmt;

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct UnknownName(pub String);

impl fmt::Display for UnknownName {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "unknown name `{}`", self.0)
    }
}
