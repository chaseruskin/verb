use std::io::{BufRead, BufReader};
use std::path::PathBuf;
use std::process::{Command, Stdio};

use crate::generic::{Generic, Generics};
use crate::unit::{Net, Unit};
use cliproc::{cli, proc, stage::Memory};
use cliproc::{Arg, Cli, Help, Subcommand};

pub struct Model {
    model: PathBuf,
    dut: Unit,
    tb: Unit,
    generics: Vec<Generic>,
    seed: Option<usize>,
    max_iters: Option<usize>,
    model_args: Vec<String>,
}

impl Subcommand<()> for Model {
    fn interpret(cli: &mut Cli<Memory>) -> cli::Result<Self> {
        cli.help(Help::with(HELP))?;
        Ok(Self {
            max_iters: cli.get(Arg::option("max-iters"))?,
            seed: cli.get(Arg::option("seed"))?,
            generics: cli
                .get_all(Arg::option("generic").switch('g'))?
                .unwrap_or_default(),
            dut: cli.require(Arg::option("dut"))?,
            tb: cli.require(Arg::option("tb"))?,
            model: cli.require(Arg::positional("model"))?,
            model_args: cli.remainder()?,
        })
    }

    fn execute(self, _c: &()) -> proc::Result {
        // Run some python code

        // set environment variables

        // check how to run the code (what file type)

        let python_interp = "python";

        std::env::set_var("VERTEX_FDI_DUT", self.dut.to_string());
        std::env::set_var("VERTEX_FDI_TB", self.tb.to_string());
        std::env::set_var("VERTEX_FDI_GENERICS", Generics::from(&self.generics).to_string());
        std::env::set_var("VERTEX_FDI_MAX_ITERS", serde_json::to_string(&self.max_iters).unwrap());

        println!("{}", self.dut.to_string());
        println!("{}", Generics::from(&self.generics).to_string());

        // let mut child = Command::new(python_interp)
        //     .arg(&self.model)
        //     .args(&self.model_args)
        //     .stdout(Stdio::piped())
        //     .spawn()
        //     .unwrap();

        // let stdout = child.stdout.take().unwrap();
        // // Stream output
        // let lines = BufReader::new(stdout).lines();
        // for line in lines {
        //     println!("{}", line.unwrap());
        // }
        Ok(())
    }
}

const HELP: &str = "\
Run the software script for a design's model.

Usage:
    vertex model [options] --dut <json> --tb <json> <model> [--] [args]...

Args:
    <model>         file system path to the software model
    --dut <json>    design-under-test's interface encoded in json format
    --tb <json>     testbench's interface encoded in json format

Options:
    --generic, -g <key=value>  override a testbench generic
    --seed <num>       set the random number generator seed
    --coverage         path to write coverage report (default: coverage.txt)
    --max-iters <num>  set the maximum number of iterations when using CDTG
    args               arguments to pass to the software model
";
