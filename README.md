# xHoundPi
High precision GPS firmware for point surveyor xHound hardware modules based on ARM64 Raspberry Pi platfor

---
## Collaborate
:warning: xHound project tasks are shared equally among developers and engineers who work on the survey problem domain or hardware design. The setup, collaboration guidelines, and notes, will/should be exhaustive and pedantic to keep the instructions clear to collaborators with any class of background or lack thereof.

### Setup
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

#### Linux
:warning: *Pending*

### Testing and validation
- Run all tests issue the following command from the root of the repository: `pipenv run python -m unittest discover --start-directory 'tests' --pattern 'Test*.py' --verbose --locals`
- Then run the linter using the commend: `pipenv run pylint xhoundpi` (tests are not linting and style conforming but please keep them clean)

### Code submission

#### Conventions

1. All PRs must be named following the convention `[feature,patch,release,major]/some-informative-title'` to pass validation. The prefixes will be mapped to a version bump as follows (brush up on [semantic versioning](https://medium.com/the-non-traditional-developer/semantic-versioning-for-dummies-45c7fe04a1f8) to better understand the scheme),
```
      release -> release
      major -> major
      feature -> minor
      path -> patch
```
---
## Licensing
See LICENSE file.