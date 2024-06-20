use cliproc::{cli, proc, stage::Memory};
use cliproc::{Arg, Cli, Help, Subcommand};

pub struct Model {}

impl Subcommand<()> for Model {
    fn interpret(cli: &mut Cli<Memory>) -> cli::Result<Self> {
        Ok(Self {})
    }

    fn execute(self, c: &()) -> proc::Result {
        Ok(())
    }
}
