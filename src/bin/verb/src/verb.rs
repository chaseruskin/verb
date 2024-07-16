use crate::ops::{check::Check, link::Link, model::Model};
use cliproc::{cli, proc, stage::Memory};
use cliproc::{Arg, Cli, Command, Help, Subcommand};
use std::env;

// Define the struct and the data required to perform its task
pub struct Verb {
    version: bool,
    subcommand: Option<Operation>,
}

impl Command for Verb {
    // Map the command-line data to the struct's data
    fn interpret(cli: &mut Cli<Memory>) -> cli::Result<Self> {
        cli.help(Help::with(HELP))?;
        Ok(Verb {
            version: cli.check(Arg::flag("version"))?,
            subcommand: cli.nest(Arg::subcommand("command"))?,
        })
    }

    // Process the struct's data to perform its task
    fn execute(self) -> proc::Result {
        if self.version == true {
            println!("{}", VERSION);
            return Ok(());
        }
        match self.subcommand {
            Some(sub) => sub.execute(&()),
            None => {
                println!("{}", HELP);
                Ok(())
            }
        }
    }
}

pub enum Operation {
    Link(Link),
    Model(Model),
    Check(Check),
}

impl Subcommand<()> for Operation {
    // Map the command-line data to the struct's data
    fn interpret(cli: &mut Cli<Memory>) -> cli::Result<Self> {
        match cli.select(&["link", "model", "check"])?.as_ref() {
            "link" => Ok(Operation::Link(Link::interpret(cli)?)),
            "model" => Ok(Operation::Model(Model::interpret(cli)?)),
            "check" => Ok(Operation::Check(Check::interpret(cli)?)),
            _ => panic!("an unimplemented command was passed through!"),
        }
    }

    // Process the struct's data to perform its task
    fn execute(self, c: &()) -> proc::Result {
        match self {
            Operation::Link(op) => op.execute(&c),
            Operation::Model(op) => op.execute(&c),
            Operation::Check(op) => op.execute(&c),
        }
    }
}

const VERSION: &str = env!("CARGO_PKG_VERSION");

const HELP: &str = "\
Verb is a tool to help simulate digital hardware.

Usage:
    verb [options] [command]

Commands:
    link        generate code snippets for hw/sw coherency 
    model       run the software script for a design's model
    check       analyze the output from a hardware simulation
    
Options:
    --version    print the version information and exit
    --help, -h   print this help information and exit
";
