use std::collections::HashMap;
use std::path::PathBuf;

use crate::error::Error;
use crate::generic::Generic;
use crate::unit::{Language, Unit};
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
            loop_limit: cli.get(Arg::option("loop-limit").value("num"))?,
            rand_seed: cli.get(Arg::option("seed").value("num"))?,
            coverage: cli.get(Arg::option("coverage").value("file"))?,
            dir: cli.get(Arg::option("directory").switch('C').value("dir"))?,
            generics: cli
                .get_all(Arg::option("generic").switch('g').value("key=value"))?
                .unwrap_or_default(),
            dut: cli.require(Arg::option("dut").value("json"))?,
            tb: cli.require(Arg::option("tb").value("json"))?,
            model: cli.require(Arg::positional("command"))?,
            model_args: cli.remainder()?,
        })
    }

    fn execute(mut self, _c: &()) -> proc::Result {
        // update the generics in the TB interface json data
        let ignore_case = self.tb.get_language() == &Language::Vhdl;

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
Run a design's software model.

Usage:
    verb model [options] --dut <json> --tb <json> <command> [--] [args]...

Args:
    <command>       the command to execute the model
    --dut <json>    hw design-under-test's interface encoded in json format
    --tb <json>     hw testbench's interface encoded in json format

Options:
    --generic, -g <key=value>  override a testbench generic
    --seed <num>               the randomness seed
    --coverage <file>          destination for the coverage report
    --loop-limit <num>         the max number of main loop iterations
    --directory, -C <dir>      the directory where the model will run
    args                       arguments to pass to the model's command
";
