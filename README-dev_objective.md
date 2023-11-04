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
* `--debug` - Print debug messages when the program runs.  
Name in configuration file: `debug`

### Help message
Run `Compat` , `Compat --help` or `Compat -h` to print the help message of this project.
Run `Compat <subcommand> --help` or `Compat <subcommand> -h` to print the help message of the subcommand.

### Configuration
By default, PyCompatibility will look for the configuration files with the following precedence order:
* `Compat.json`
* `pyproject.toml`

PyCompatibility currently will only support `.json`, `.toml` and `.yaml`.
Specially, configuration in `pyproject.toml` needs to write into the `[tool.PyCompatibility]` section.

If an option provided both in CLI flag and configuration file, CLI option will be used.

### Check command
Run `Compat check` to run the check command.

Flags available:

* Min version: The min version of Python(3.xx) that you want PyCompatibility to check the supporting of it  
CLI flag: `--min-version`, `-minV`  
Name in configuration file: `min_version`  
Required: True[^1]  
Example:
```shell
Compat check --min-version 8
Compat check --min-version 3.8
Compat check --min-version py38

Compat check --min-version=8
Compat check --min-version=3.8
Compat check --min-version=py38
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
Compat check --max-version 3.8
Compat check --max-version=8
# ...
```

* Configuration file path: The path to the configuration file  
CLI flag: `--configuration-path`, `--cfg`  
Name in configuration file: N/A  
Required: False  
Example:
```shell
Compat check --configuration-path CompatConfig.toml
```

* Version: A version range that you want PyCompatibility to check the supporting of it  
CLI flag: `--version`, `-V`  
Name in configuration file: `version`  
Required: True[^1]  
Example:  
CLI:
```shell
Compat check -V 8 10
Compat check -V 3.8 3.10
Compat check -V py38 py310

Compat check -V=8-10
Compat check -V=3.8-3.10
Compat check -V=py38-py310
```
Configuration file(pyproject.toml):
```toml
[tool.PyCompatibility]
version = [8, 10]
# version = ["py38", "py310"]
# version = ["3.8", "3.10"]
```

* Include: The files that PyCompatibility **should only** check  
CLI flag: `--include`  
Name in configuration file: `include`  
Required: False  
Example:
```shell
Compat check --include ./python_scripts/
```

* Exclude: The files that PyCompatibility **will not** check  
CLI flag: `--exclude`  
Name in configuration file: `exclude`  
Required: False  
Example:
```shell
Compat check --exclude ./non_python_scripts/
```

* Output: The format of the checking result
CLI flag: `--output`, `-o`  
Name in configuration file: `output`  
Required: False  
Choice: `text`, `json`  
**If JSON output is specified, debug mode will be closed as it is not format-able for the JSON result**

[^1]: If `Version` is provided, `Min version` and `Max version` will not be required.
Also, if `Min version` and `Max version` are provided, `Version` will not be required.
But, if `Version` is provided, and `Min version` and/or `Max version` is also provided,
`Version` will be ignored.

### Clean up

PyCompatibility will store its cache at `.compat_cache`.
Run `Compat cleanup` will delete the cache.
