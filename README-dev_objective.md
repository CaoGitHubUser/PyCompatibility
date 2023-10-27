<meta content="This is a README that this project WILL be in FUTURE.
The feature that implemented will add to /README.md">

# PyCompatibility

**_PyCompatibility is a Python version compatibility checker._**

## Installation

### Current version build
1. Download the zip archive in the [project release page](https://github.com/CaoGitHubUser/PyCompatibility/releases)
2. Run `pip install .`

### Development release build
1. Clone this repository.
2. Run `pip install .`

## Usage

### Entry
Run `Compat <subcommand> --<args>`

### Common arguments
The following flags are always available for all subcommands.
* `--help`, `-h` - Help command.Print help message for the subcommand.
* `--configuration-path`, `--cfg` - Path to the configuration file.
* `--debug`, `--print-log` - Print logs when the program runs.

### Help message
Run `Compat` , `Compat --help` or `Compat -h` to print the help message of this project.
Run `Compat <subcommand> --help` or `Compat <subcommand> -h` to print the help message of the subcommand.

### Check command
Run `Compat check` to run the check command.
This command will *require* some arguments, others are optional.

| Name                    | CLI Flag                    | Name in configuration file | Required | Help                                                                                        | Example                           |
|-------------------------|-----------------------------|----------------------------|----------|---------------------------------------------------------------------------------------------|-----------------------------------|
| Min version             | --min-version, -min-V       | min_version                | True[^1] | The min version of Python(3.xx) that you want PyCompatibility to check the supporting of it | --min-version 8                   |
| Max version             | --max-version, -max-V       | max_version                | True[^1] | The max version of Python(3.xx) that you want PyCompatibility to check the supporting of it | --max-version 11                  |
| Configuration file path | --configuration-path, --cfg | Not available              | False    | The path to the configuration file                                                          | --configuration-path example.json |
| Version                 | --version, -V               | version                    | True[^1] | The version of Python that you want PyCompatibility to check the supporting of it           | --version 8~11, --version 8-11    |
| Include                 | --include                   | include                    | False    | The files that PyCompatibility **should only** check                                        | --include ./*/example.include     |
| Exclude                 | --exclude                   | exclude                    | False    | The files that PyCompatibility **will not** check                                           | --exclude ./*/example.exclude     |

[^1]: If `Version` is provided, `Min version` and `Max version` will not be required.
Also, if `Min version` and `Max version` are provided, `Version` will not be required.
But, if `Version` is provided, and `Min version` and/or `Max version` is also provided,
it/them will be used.

### Clean up

PyCompatibility will store its cache at `.compat_cache`.
Run `Compat cleanup` will delete the cache.
