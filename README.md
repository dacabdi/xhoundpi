# xHoundPi
High precision GPS firmware for point surveyor xHound hardware modules based on ARM64 Raspberry Pi platforms.

---
## Collaborate
:warning: xHound project tasks are shared equally among developers and engineers who work on the survey problem domain or hardware design. The setup, collaboration guidelines, and notes, will/should be exhaustive and pedantic to keep the instructions clear to collaborators with any class of background or lack thereof.

#
:point_right: We aim to automate this setup process. In the meantime, use the following instructions.

#### Windows
1. [Download and install Visual Studio Code](https://code.visualstudio.com/download)
2. [Download and install the latest version of Python 3.9.x](https://www.python.org/downloads/)
   1. Ensure that you checked *Add python to PATH* during the installation process.
   2. Verify installation by opening an elevated terminal window and running `python --version` (should report `v3.x`).
   3. Verify that [`pip`](https://realpython.com/what-is-pip/) is also installed by issuing `pip --version` (see [link](https://realpython.com/what-is-pip/) for more).
3. Install `pipenv` by opening an elevated terminal window and running `pip install pipenv`.
4. Clone this repository and initialize the environment
   1. Open a command window.
   2. Create a subdirectory where to deploy the sources (e.g., `mkdir C:\repos`).
   3. Change current directory to the desired location (e.g., `cd C:\repos`).
   4. Clone the repository (i.e., `git clone https://github.com/dacabdi/xhoundpi.git`).
   5. Step into the sources directory (i.e., `cd xhoundapi` if you are still in `C:\repos`).
   6. Run command `pipenv install --dev` and await for initialization to complete.
   7. Run `pipenv shell` to enter the `pipenv` shell for this environment.
5. Verify by running tests and linter (see below in **Testing and validation**)

#### Linux
1. [Download and install Visual Studio Code](https://code.visualstudio.com/download)
2. Install Python 3 ([use this guide](https://realpython.com/installing-python/#how-to-install-python-on-linux))
   1. Ensure that Python and `pip` are installed `$ python --version` and `$ pip --version` respectively.
   2. From a terminal window, run: `$ pip install pipenv`.
3. Clone this repository and initialize the environment
   1. Open a command window.
   2. Create a subdirectory where to deploy the sources (e.g., `md ~\repos`).
   3. Change current directory to the desired location (e.g., `cd ~\repos`).
   4. Clone the repository (i.e., `git clone https://github.com/dacabdi/xhoundpi.git`).
   5. Step into the sources directory (i.e., `cd xhoundapi` if you are still in `~\repos`).
   6. Run command `pipenv install --dev` and await for initialization to complete.
   7. Run `pipenv shell` to enter the `pipenv` shell for this environment.
5. Verify by running tests and linter (see below in **Testing and validation**)
6. Open workspace (e.g., `code .\.vscode\xhoundpi.code-workspace`)

### Testing and validation
#### Quick feedback loop
- Run all tests issue the following command from the root of the repository: `pipenv run python -m unittest discover --start-directory "tests" --pattern "test*.py" --verbose --locals`
- Then run the linter using the commend: `pipenv run pylint xhoundpi` (tests are not linting and style conforming but please keep them clean)

#### Using nektos/act
The project [`nektos/act`](https://github.com/nektos/act) is designed to run GitHub actions locally and provide immediate feedback without resorting to the GitHub agents and pipelines. These tests would provide a closer validation to the one your PRs will be subjected too and always setup temporary clean environments on every run. Follow the setup instructions on the project's README and use it with our repository to run the validation workflows.

:warning: Currently failing due to a mismatch between GitHub's docker runner and `act`s ability to resolve the Python versions. Will be fixed soon.

#### Working with data captures to mock IO devices
To allow functional testing in isolation from the hardware, we have collected captures off the actual devices. See the `data` subdir for samples (the `notes.md` file describes the contents). To convert these text based captures to binary files, run the following commands from the root of the repository (assumes the `pipenv` shell is initialized):

`$ python -m tools.capture_processor [inputfile] [outputfile]`

E.g., to parse the `data/mixed_nmea_ubx_sample.txt` file and output the results into the file `data.hex` use `$ python -m tools.capture_processor "data/mixed_nmea_ubx_sample.txt" "data.hex"`. :warning: Adopt the convention of using the `.hex` extension for your processed samples, it will allow to filter them in the `.gitignore` file and avoid accidentally commiting them.

### Code submission

#### Conventions
1. Branches should be named `[user-github-handle]/[topic]`. :warning: Will be enforced programmatically in the future.
2. We aim for 100% test coverage, PRs with no testing and verification should not/will not be completed.
3. Squash all commits into one and delete the PR branch upon completion/merge.
4. Provide context in the PR description and ensure at least one other member reviewed the code.
5. All PRs must be named following the convention `[feature,patch,release,major]/some-informative-title'` to pass validation. This is programmatically enforced. The prefixes will be mapped to a version bump as follows (brush up on [semantic versioning](https://medium.com/the-non-traditional-developer/semantic-versioning-for-dummies-45c7fe04a1f8) to better understand the scheme),
```
      release -> release
      major -> major
      feature -> minor
      path -> patch
```
:smiley: Happy coding!

---
## Licensing
See LICENSE file.