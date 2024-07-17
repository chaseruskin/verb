#[derive(Debug, PartialEq)]
pub struct Topic {
    inner: String,
}

impl From<String> for Topic {
    fn from(value: String) -> Self {
        Self { inner: value }
    }
}
