use std::{path::PathBuf, str::FromStr};

use comment::Comment;
use severity::Severity;
use timestamp::Timestamp;
use topic::Topic;

use crate::error::{AnyError, Error};

pub mod comment;
pub mod severity;
pub mod timestamp;
pub mod topic;

#[derive(Debug, PartialEq)]
pub struct Events {
    inner: Vec<Event>,
}

impl Events {
    /// Loads an event log from a file system path.
    pub fn load(path: &PathBuf) -> Result<Self, AnyError> {
        let data = std::fs::read_to_string(path)?;
        let events = Self::from_str(&data)?;
        Ok(events)
    }

    /// Verify there were 0 bad events in the event log.
    pub fn check(&self) -> bool {
        self.inner.iter().find(|e| e.is_wild()).is_none()
    }

    pub fn count_normal(&self) -> usize {
        self.inner.iter().filter(|e| e.is_normal()).count()
    }

    pub fn count_wild(&self) -> usize {
        self.inner.iter().filter(|e| e.is_wild()).count()
    }

    pub fn len(&self) -> usize {
        self.inner.len()
    }
}

impl FromStr for Events {
    type Err = Error;

    fn from_str(s: &str) -> Result<Self, Self::Err> {
        let mut raw_events = s.split_terminator('\n');
        let mut events = Vec::new();
        while let Some(raw_e) = raw_events.next() {
            events.push(Event::from_str(raw_e)?);
        }
        Ok(Self { inner: events })
    }
}

#[derive(Debug, PartialEq)]
pub struct Event {
    timestamp: Timestamp,
    severity: Severity,
    topic: Topic,
    comment: Comment,
}

impl Event {
    pub fn is_wild(&self) -> bool {
        self.severity.is_bad()
    }

    pub fn is_normal(&self) -> bool {
        self.severity.is_good()
    }
}

impl FromStr for Event {
    type Err = Error;

    fn from_str(s: &str) -> Result<Self, Self::Err> {
        // take timestamp
        let (c_timestamp, rem) = match s.trim().split_once(|c: char| c.is_ascii_whitespace()) {
            Some(it) => it,
            None => return Err(Error::ExpectingTimestamp),
        };
        // take severity
        let (c_severity, rem) = match rem.trim().split_once(|c: char| c.is_ascii_whitespace()) {
            Some(it) => it,
            None => return Err(Error::ExpectingSeverity),
        };
        // take topic
        let (c_topic, rem) = match rem.trim().split_once(|c: char| c.is_ascii_whitespace()) {
            Some(it) => it,
            None => return Err(Error::ExpectingTopic),
        };
        // take comment as remaining text
        let c_comment = rem.trim();

        // formulate an event
        Ok(Self {
            timestamp: Timestamp::from_str(c_timestamp)?,
            severity: Severity::from_str(c_severity)?,
            topic: Topic::from(c_topic.to_string()),
            comment: Comment::from(c_comment.to_string()),
        })
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn from_str() {
        let ev = "180000000fs         INFO      ASSERT_EQ      sum receives 0110 and expects 0110";
        assert_eq!(
            Event::from_str(ev).unwrap(),
            Event {
                timestamp: Timestamp::with("180000000", "fs"),
                severity: Severity::Info,
                topic: Topic::from("ASSERT_EQ".to_string()),
                comment: Comment::from("sum receives 0110 and expects 0110".to_string()),
            }
        )
    }
}
