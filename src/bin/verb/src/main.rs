use cliproc::{Cli, ExitCode};
use std::env;
use verb::verb::Verb;

fn main() -> ExitCode {
    Cli::default().parse(env::args()).go::<Verb>()
}
