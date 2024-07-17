use std::str::FromStr;

use crate::error::Error;

#[derive(Debug, PartialEq)]
pub struct Timestamp {
    time: String,
    units: String,
}

impl Timestamp {
    pub fn with(time: &str, units: &str) -> Self {
        Self {
            time: time.to_string(),
            units: units.to_string(),
        }
    }
}

impl FromStr for Timestamp {
    type Err = Error;

    fn from_str(s: &str) -> Result<Self, Self::Err> {
        // split into time and units
        let i = s.find(|c: char| c.is_ascii_alphabetic());
        match i {
            Some(i) => {
                let (time, unit) = s.split_at(i);
                Ok(Self {
                    time: time.to_string(),
                    units: unit.to_string(),
                })
            },
            None => return Err(Error::MissingTimeUnits)
        }
    }
}

