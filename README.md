# EKS-Utils

A command-line script to login to an EKS cluster providing the basic information to connect and letting the script work for you. The actual configuration will be saved in a *config.json* file, to allow later connection to work without user input.

# Requirements

- Python 3.7+

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

- 2023-03-07: fix bug in the requirements.txt [#3](https://github.com/ssensini/EKS-Utils/issues/3)
- 2023-02-09: fix bug for negative choice [#2](https://github.com/ssensini/EKS-Utils/issues/2)
- 2023-02-07: fix enhancement [#1](https://github.com/ssensini/EKS-Utils/issues/1)
