use std::{fmt::Display, str::FromStr};

use serde::Serialize;

use crate::error::Error;

#[derive(Debug, Serialize)]
pub struct Generics<'a>(&'a Vec<Generic>);

impl<'a> Display for Generics<'a> {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "{}", serde_json::to_string(self).unwrap())
    }
}

impl<'a> From<&'a Vec<Generic>> for Generics<'a> {
    fn from(value: &'a Vec<Generic>) -> Self {
        Self(value)
    }
}

#[derive(Debug, PartialEq, Clone, Serialize)]
pub struct Generic {
    key: String,
    value: String,
}

impl Generic {
    pub fn with(key: String, value: String) -> Self {
        Self {
            key: key,
            value: value,
        }
    }

    pub fn key(&self) -> &String {
        &self.key
    }

    pub fn value(&self) -> &String {
        &self.value
    }

    /// Splits the struct into its underlying components: a key and a value.
    pub fn split(self) -> (String, String) {
        (self.key, self.value)
    }
}

impl From<(String, String)> for Generic {
    fn from(value: (String, String)) -> Self {
        Self {
            key: value.0,
            value: value.1,
        }
    }
}

impl FromStr for Generic {
    type Err = Error;

    fn from_str(s: &str) -> Result<Self, Self::Err> {
        match s.split_once('=') {
            Some((k, v)) => Ok(Self {
                key: k.to_string(),
                value: v.to_string(),
            }),
            None => Err(Error::GenericParseMissingEq),
        }
    }
}
