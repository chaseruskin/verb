type LastError = String;

#[derive(Debug, PartialEq, thiserror::Error)]
pub enum Error {
    #[error("{0}")]
    InvalidJson(LastError),
    #[error("expecting equal sign '=' character")]
    GenericParseMissingEq,
    #[error("exited with error code: {0}")]
    ChildProcErrorCode(i32),
    #[error("terminated by signal")]
    ChildProcTerminated,
    #[error("no generic found in testbench with matching name {0:?}")]
    GenericNotFound(String),
    #[error("simulation caught {0} wild events")]
    FoundUnexpectedEvents(usize),
    #[error("model failed to meet coverage by {0} points")]
    FailedCoverage(usize),
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
