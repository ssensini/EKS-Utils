# EKS-Utils

A command-line script to login to an EKS cluster providing the basic information to connect and letting the script work for you. The actual configuration will be saved in a *config.json* file, to allow later connection to work without user input.

# Requirements

- Python 3.x installed

# Installation

Install the dependencies with *pip*:

```
pip install requirements.txt
```

Run the script:

```
python init.py
```

# Release notes

- 2023-07-03: fix bug for missing check on _config.json_ file [#5](https://github.com/ssensini/EKS-Utils/issues/5)
- 2023-05-18: added support to _kubectl proxy_ command
- 2023-02-07: fix enhancement [#1](https://github.com/ssensini/EKS-Utils/issues/1)
- 2023-02-09: fix bug for negative choice [#2](https://github.com/ssensini/EKS-Utils/issues/2)
