use std::path::PathBuf;

use cliproc::{cli, proc, stage::Memory};
use cliproc::{Arg, Cli, Help, Subcommand};

use crate::error::Error;
use crate::events::Events;

pub struct Check {
    events: PathBuf,
    coverage: Option<String>,
    stats: bool,
}

impl Subcommand<()> for Check {
    fn interpret(cli: &mut Cli<Memory>) -> cli::Result<Self> {
        cli.help(Help::with(HELP))?;
        Ok(Self {
            stats: cli.check(Arg::flag("stats"))?,
            coverage: cli.get(Arg::option("coverage"))?,
            events: cli.require(Arg::positional("events"))?,
        })
    }

    fn execute(self, _c: &()) -> proc::Result {

        let events = Events::load(&self.events)?;

        let mut total_points: Option<usize> = None;
        let mut points_covered: Option<usize> = None;
        // load the coverage file
        if let Some(path) = &self.coverage {
            let data = std::fs::read_to_string(path)?;
            // find the coverage lines
            let stats = data.split_terminator('\n');
            for s in stats {
                let is_total_points = s.starts_with("Total points:");
                let is_points_covered = s.starts_with("Points covered:");
                if is_total_points == true || is_points_covered == true {
                    let (_name, value) = s.split_once(':').unwrap();
                    let value = value.trim();
                    if is_total_points == true {
                        total_points = Some(usize::from_str_radix(value, 10).unwrap());
                    } else {
                        points_covered = Some(usize::from_str_radix(value, 10).unwrap());
                    }
                }
            }
        }

        if self.stats == true {
            println!("info: simulation score: {}/{}", events.count_normal(), events.len());
        }

        // check coverage
        if total_points.is_some() && points_covered.is_some() {
            let tp = total_points.unwrap();
            let pc = points_covered.unwrap();
            if self.stats == true {
                println!("info: coverage score: {}/{}", pc, tp);
            }
            match tp == pc {
                true => (),
                false => return Err(Error::FailedCoverage(tp - pc))?,
            }
        }
        // check events
        match events.check() {
            true => Ok(()),
            false => Err(Error::FoundWildEvents(events.count_wild()))?,
        }
    }
}

const HELP: &str = "\
Analyze the simulation's results.

Usage:
    verb check [options] <events>

Args:
    <events>       file system path to the events log
    --stats        display summary statistics

Options:
    --coverage <file>  path to read coverage report
";
