use std::collections::HashMap;
use std::path::PathBuf;

use crate::error::Error;
use crate::generic::Generic;
use crate::unit::Unit;
use cliproc::{cli, proc, stage::Memory};
use cliproc::{Arg, Cli, Help, Subcommand};

pub struct Model {
    model: PathBuf,
    dut: Unit,
    tb: Unit,
    dir: Option<PathBuf>,
    generics: Vec<Generic>,
    coverage: Option<String>,
    rand_seed: Option<usize>,
    loop_limit: Option<isize>,
    model_args: Vec<String>,
}

impl Subcommand<()> for Model {
    fn interpret(cli: &mut Cli<Memory>) -> cli::Result<Self> {
        cli.help(Help::with(HELP))?;
        Ok(Self {
            loop_limit: cli.get(Arg::option("loop-limit"))?,
            rand_seed: cli.get(Arg::option("seed"))?,
            coverage: cli.get(Arg::option("coverage"))?,
            dir: cli.get(Arg::option("directory").switch('C'))?,
            generics: cli
                .get_all(Arg::option("generic").switch('g'))?
                .unwrap_or_default(),
            dut: cli.require(Arg::option("dut"))?,
            tb: cli.require(Arg::option("tb"))?,
            model: cli.require(Arg::positional("model"))?,
            model_args: cli.remainder()?,
        })
    }

    fn execute(mut self, _c: &()) -> proc::Result {
        // update the generics in the TB interface json data
        let ignore_case = self.tb.get_language().to_ascii_uppercase() == "VHDL";
        for override_gen in self.generics {
            let mut detected_gen = false;
            for net in self.tb.get_generics_mut() {
                if net.is_identifier(override_gen.key(), ignore_case) == true {
                    net.set_default(override_gen.value().to_string());
                    detected_gen = true;
                    break;
                }
            }
            if detected_gen == false {
                return Err(Error::GenericNotFound(override_gen.key().to_string()))?;
            }
        }

        // set environment variables for the software model
        let mut envs = HashMap::new();
        envs.insert("VERB_DUT", self.dut.to_string());
        envs.insert("VERB_TB", self.tb.to_string());
        if let Some(ll) = &self.loop_limit {
            envs.insert("VERB_LOOP_LIMIT", ll.to_string());
        }
        if let Some(rs) = &self.rand_seed {
            envs.insert("VERB_RAND_SEED", rs.to_string());
        }
        if let Some(cov) = &self.coverage {
            envs.insert("VERB_COVERAGE_FILE", cov.to_string());
        }

        if self.model.is_file() && self.model.is_relative() && self.model.exists() {
            self.model = self.model.canonicalize()?;
        }

        let mut child = match std::process::Command::new(&self.model)
            .current_dir(if let Some(d) = self.dir {
                d
            } else {
                std::env::current_dir().unwrap()
            })
            .args(self.model_args)
            .envs(&envs)
            .stdout(std::process::Stdio::inherit())
            .stderr(std::process::Stdio::inherit())
            .spawn()
        {
            Ok(r) => Ok(r),
            Err(e) => Err(e),
        }?;

        let exit_code = child.wait()?;
        match exit_code.code() {
            Some(num) => {
                if num != 0 {
                    Err(Error::ChildProcErrorCode(num))?
                } else {
                    Ok(())
                }
            }
            None => Err(Error::ChildProcTerminated)?,
        }
    }
}

const HELP: &str = "\
Run the software script for a design's model.

Usage:
    verb model [options] --dut <json> --tb <json> <command> [--] [args]...

Args:
    <command>       file system path used to execute the model
    --dut <json>    design-under-test's interface encoded in json format
    --tb <json>     testbench's interface encoded in json format

Options:
    --generic, -g <key=value>  override a testbench generic
    --seed <num>       set the random number generator seed
    --coverage <file>  path to write coverage report
    --loop-limit <num> set the maximum number of iterations when using CDTG
    --directory, -C    change the working directory where the model will run
    args               arguments to pass to the model's command
";
