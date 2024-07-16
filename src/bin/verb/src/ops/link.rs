use crate::unit::{Net, Unit};
use cliproc::{cli, proc, stage::Memory};
use cliproc::{Arg, Cli, Help, Subcommand};

pub struct Link {
    json: Unit,
    bfm: bool,
    send: bool,
    comp: bool,
    exclude: Vec<String>,
    list: bool,
}

// use an 'exclude' list to ignore ports in the bfm

impl Subcommand<()> for Link {
    fn interpret(cli: &mut Cli<Memory>) -> cli::Result<Self> {
        cli.help(Help::with(HELP))?;
        Ok(Self {
            bfm: cli.check(Arg::flag("bfm"))?,
            send: cli.check(Arg::flag("send"))?,
            comp: cli.check(Arg::flag("comp"))?,
            list: cli.check(Arg::flag("list"))?,
            exclude: cli
                .get_all(Arg::option("exclude").switch('x'))?
                .unwrap_or(Vec::new()),
            json: cli.require(Arg::positional("json"))?,
        })
    }

    fn execute(self, _c: &()) -> proc::Result {
        let filtered_ports: Vec<&Net> = self
            .json
            .get_ports()
            .iter()
            .filter(|p| self.exclude.contains(p.get_identifier()) == false)
            .collect();

        if self.list == true {
            print!("input vectors order:\n ");
            filtered_ports
                .iter()
                .filter(|n| n.is_input())
                .for_each(|n| print!(" {}", n.get_identifier()));
            println!("\n");
            print!("output vectors order:\n ");
            filtered_ports
                .iter()
                .filter(|n| n.is_output())
                .for_each(|n| print!(" {}", n.get_identifier()));
            println!("\n");
            return Ok(());
        }

        let mut space_next_display = false;
        if self.bfm == true {
            println!(
                "{}",
                Self::to_string_bfm(&filtered_ports, &self.json.get_identifier(), "bfm")
            );
            space_next_display = true;
        }
        if self.send == true {
            if space_next_display == true {
                println!();
            }
            let filtered_ports: Vec<&Net> = filtered_ports
                .clone()
                .into_iter()
                .filter(|n| n.is_input())
                .collect();
            println!("{}", Self::to_string_send(&filtered_ports, "bfm"));
            space_next_display = true;
        }
        if self.comp == true {
            if space_next_display == true {
                println!();
            }
            let filtered_ports: Vec<&Net> = filtered_ports
                .into_iter()
                .filter(|n| n.is_output())
                .collect();
            println!(
                "{}",
                Self::to_string_comp(&filtered_ports, &self.json.get_identifier(), "bfm")
            );
            space_next_display = true;
        }
        Ok(())
    }
}

const HELP: &str = "\
Generate code snippets for hw/sw synchronization.

Usage:
    verb link [options] <json>

Args:
    <json>      hw unit's interface encoded in json format

Options:
    --bfm           print the hw bus functional model interface
    --send          print the hw function to send inputs to the dut
    --comp          print the hw function to compare outputs from the dut
    --exclude, -x   omit specific ports from the code snippets
    --list          list the port order and exit
";

impl Link {
    fn to_string_bfm(ports: &Vec<&Net>, unit: &str, bfm_inst: &str) -> String {
        let result = format!("type {}_bfm is record\n", unit);
        let mut result = ports.iter().fold(result, |mut acc, n| {
            acc.push_str(&format!("  {}: {};\n", n.get_identifier(), n.get_type()));
            acc
        });
        result.push_str(&format!(
            "end record;\n\nsignal {}: {}_bfm;",
            bfm_inst, unit
        ));
        result
    }

    fn to_string_send(ports: &Vec<&Net>, bfm_inst: &str) -> String {
        let input_fd = "i";
        let drive_fn = "drive";
        let result = format!("procedure send(file {0}: text) is\n  variable row: line;\nbegin\n  if endfile({0}) = false then\n    readline({0}, row);\n", input_fd);
        let mut result = ports.iter().fold(result, |mut acc, n| {
            acc.push_str(&format!(
                "    {0}(row, {1}.{2});\n",
                drive_fn,
                bfm_inst,
                n.get_identifier()
            ));
            acc
        });
        result.push_str(&format!("  end if;\nend procedure;"));
        result
    }

    fn to_string_comp(ports: &Vec<&Net>, unit: &str, bfm_inst: &str) -> String {
        let event_fd = "e";
        let output_fd = "o";
        let load_fn = "load";
        let assert_fn = "assert_eq";
        let result = format!("procedure compare(file {0}: text; file {1}: text) is\n  variable row: line;\n  variable expct: {2}_bfm;\nbegin\n  if endfile({1}) = false then\n    readline({1}, row);\n", event_fd, output_fd, unit);
        let mut result = ports.iter().fold(result, |mut acc, n| {
            acc.push_str(&format!(
                "    {0}(row, expct.{1});\n",
                load_fn,
                n.get_identifier()
            ));
            acc.push_str(&format!(
                "    {3}({0}, {1}.{2}, expct.{2}, \"{2}\");\n",
                event_fd,
                bfm_inst,
                n.get_identifier(),
                assert_fn,
            ));
            acc
        });
        result.push_str(&format!("  end if;\nend procedure;"));
        result
    }

    /// Computes the number of characters required for the longest known
    /// identifier.
    fn longest_id_len(ids: Vec<&String>) -> usize {
        ids.iter().map(|s| s.len()).max().unwrap_or(0)
    }
}
