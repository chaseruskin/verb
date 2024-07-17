use std::str::FromStr;

use crate::error::Error;

#[derive(Debug, PartialEq)]
pub enum Severity {
    Trace,
    Debug,
    Info,
    Warn,
    Error,
    Fatal,
}

impl Severity {
    /// Checks if the severity is not okay.
    pub fn is_bad(&self) -> bool {
        match &self {
            Self::Warn | Self::Error | Self::Fatal => true,
            _ => false,
        }
    }

    /// Checks if the severity level is okay.
    pub fn is_good(&self) -> bool {
        match &self {
            Self::Trace | Self::Debug | Self::Info => true,
            _ => false,
        }
    }
}

impl FromStr for Severity {
    type Err = Error;

    fn from_str(s: &str) -> Result<Self, Self::Err> {
        match s {
            "TRACE" => Ok(Self::Trace),
            "DEBUG" => Ok(Self::Debug),
            "INFO" => Ok(Self::Info),
            "WARN" => Ok(Self::Warn),
            "ERROR" => Ok(Self::Error),
            "FATAL" => Ok(Self::Fatal),
            _ => Err(Error::UnknownSeverity(s.to_string()))
        }
    }
}