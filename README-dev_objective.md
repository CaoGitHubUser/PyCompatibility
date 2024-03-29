<meta content="This is a README that this project WILL BE IN FUTURE.
The feature that implemented will add to /README.md">
<meta content="
Copying and distribution of this file, with or without modification,
are permitted in any medium without royalty provided the copyright
notice and this notice are preserved.  This file is offered as-is,
without any warranty.
">

# PyCompatibility

**_PyCompatibility is a static Python version compatibility checker._**

## Installation

### Current version build
Run `pip install PyCompatibility` or `pip install PyCompatibility=X.X` for specified version.

### Development release build
1. Clone this repository.
2. Run `pip install .`

## Usage

### Entry
Run `Compat <subcommand> --<args>`

### Common arguments
The following flags are always available for all subcommands.
* `--help` or `-h` - Help command.Print help message for the subcommand.
* `--configuration-path`, `--cfg` - Path to the configuration file.
* `--log-level` - The logging level.Logs lesser than this level will not be logged. CLI only.
* `--color` / `--no-color` - Colorful output. Default is true. CLI only.
* `--version` - Show the version of this program and exit.

### Help message
Run `Compat`, `Compat --help` or `Compat -h` to print the help message of this project.
Run `Compat <subcommand> --help` or `Compat <subcommand> -h` to print the help message of the subcommand.

### Configuration
By default, PyCompatibility will look for the configuration files with the following precedence order:
* `Compat.json`
* `pyproject.toml`

PyCompatibility currently will only support `.json` and `.toml`.
Specially, configuration in `pyproject.toml` needs to write into the `[tool.PyCompatibility]` section.

If an option provided both in CLI flag and configuration file, CLI option will be used.

### Init
Run `Compat init` will generate a configuration file with some simple questions.
Available files to store the configuration are `Compat.json` and `pyproject.toml`

### Check command
Run `Compat check INCLUDE` to run the check command.

Flags available:

* Min version: The min version of Python(3.xx) that you want PyCompatibility to check the supporting of it  
CLI flag: `--min-version`, `-minV`  
Name in configuration file: `min_version`  
Required: True[^1]  
Example:
```shell
Compat check --min-version 8
Compat check --min-version "8"
```
These set it to Python 3.8

* Max version: The max version of Python(3.xx) that you want PyCompatibility to check the supporting of it  
CLI flag: `--max-version`, `-maxV`  
Name in configuration file: `max_version`  
Required: True[^1]  
Example:
```shell
# The syntax is similar to the `--min-version`
Compat check --max-version 8
Compat check --max-version "8"
```

* Version: A version range that you want PyCompatibility to check the supporting of it  
CLI flag: `--version`, `-V`  
Name in configuration file: `version`  
Required: True[^1]  
Example:  
CLI:
```shell
Compat check -V "8" "10"
Compat check -V 8 10
```
Configuration file(pyproject.toml):
```toml
[tool.PyCompatibility]
version = [8, 10]
# version = ["8", "10"]
```

NOTE: The version should be greater than or equal the last EOL version,
and lesser than or equal the latest stable version

* Exclude: The files that PyCompatibility **will not** check  
CLI flag: `--exclude`  
Name in configuration file: `exclude`  
Required: False  
Example:
```shell
Compat check --exclude ./non_python_scripts/ ---exclude ./other_non_python_scripts/
```

* Report: The path to the file to write the JSON check report  
CLI flag: `--report`, `-o`  
Name in configuration file: `report`  
Required: False  
**If report is not specified, the JSON output will be formatted and print to stdout**

[^1]: If `Version` is provided, `Min version` and `Max version` will not be required.
Also, if `Min version` and `Max version` are provided, `Version` will not be required.
But, if `Version` is provided, and `Min version` and/or `Max version` is also provided,
`Version` will be ignored.

### Clean up

PyCompatibility will store its cache at `.compat_cache`.
Run `Compat cleanup` will delete the cache.
