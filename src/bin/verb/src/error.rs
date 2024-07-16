type LastError = String;

#[derive(Debug, PartialEq, thiserror::Error)]
pub enum Error {
    #[error("{0}")]
    InvalidJson(LastError),
    #[error("expecting equal sign '=' character")]
    GenericParseMissingEq,
}

impl Error {
    // Presents the message `s` without the first letter being capitalized.
    pub fn lowerize(s: String) -> String {
        s.char_indices()
            .into_iter()
            .map(|(i, c)| if i == 0 { c.to_ascii_lowercase() } else { c })
            .collect()
    }
}
