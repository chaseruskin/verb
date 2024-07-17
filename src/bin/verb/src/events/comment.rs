#[derive(Debug, PartialEq)]
pub struct Comment {
    inner: String,
}

impl From<String> for Comment {
    fn from(value: String) -> Self {
        Self {
            inner: value
        }
    }
}