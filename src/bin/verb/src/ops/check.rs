use cliproc::{cli, proc, stage::Memory};
use cliproc::{Arg, Cli, Help, Subcommand};

pub struct Check {}

impl Subcommand<()> for Check {
    fn interpret(cli: &mut Cli<Memory>) -> cli::Result<Self> {
        Ok(Self {})
    }

    fn execute(self, c: &()) -> proc::Result {
        Ok(())
    }
}
