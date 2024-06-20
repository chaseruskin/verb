use cliproc::{Cli, ExitCode};
use std::env;
use vertex::vertex::Vertex;

fn main() -> ExitCode {
    Cli::default().parse(env::args()).go::<Vertex>()
}
