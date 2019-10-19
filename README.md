# um_python
Python API generator for Ultra Messaging using Python cffi.

* [Introduction](#introduction)
* [Prerequisites](#prerequisites)
* [Generate the Wrapper](#generate-the-wrapper)
* [Test the Wrapper](#test-the-wrapper)
* [Using the API](#using-the-api)
* [Troubleshooting](#troubleshooting)

# Introduction

This project is a simple tool to generate an Ultra Messaging wrapper API for
Python using the cffi interface.
Note that cffi is a python wrapper over the UM native library,
and therefore requires the UM native dynamic library to be installed.
I.e. this is not a pure Python implementation of UM.

Python itself has tools to make the generation of cffi APIs easy.
For example, it can read a C header file (.h) and do most of the work for you.
However, the UM "lbm.h" file is not well-suited to the cffi tools.
The tools in the "um_python" project performs a set of transformations on
your "lbm.h" file, and invokes the cffi tools.

**ATTENTION**: this Python API has \*not\* been extensively tested by
Informatica.
In particular, we have not performed our QA test suites on it.
This project is intended to jump-start UM users to produce their
own Python API, which they will support.

Note however, that Informatica will perform "best effort" support when
users have problems with the Python API.
Please contact us through the normal UM support channel if you encounter
problems and/or have suggestions for its improvement.

## Why Make Users Generate the API? Why Not Just Ship the Wrapper?

Informatica is not prepared to ship a fully-supported Python API at this time.
There are different Python environments that lead to differences in how
the API must be created.
This is why this project is offered on Github -- it offers a tool that many
users find helpful, but does not have the same support requirements.

Because each version of UM can have differences this project must be
offered in the form of a general tool, and not a shrink-wrapped cffi
library.
Doing it this way allows users of many different versions of UM to create
a Python wrapper for that version of UM.
Note that a wrapper generated for one UM version \*might\* work on another
version, but it might not.
The safest approach is to generate a separate wrapper for each version of
UM that is in use.


# Prerequisites

The following is required to use this tool.

* Linux

* Ultra Messaging version 6.x must be installed with the standard UM directory
structure (i.e. subdirectories for "lib" and "include").

* The "gcc" command must invoke the GNU C compiler.
Make sure it is in your PATH.

* The "perl" command must invoke the Perl language interpreter.
Make sure it is in your PATH.

* The "python" command must invoke Python 2.x.
Make sure it is in your PATH.
(The cffi documentation claims that the resulting API wrapper is compatible
with Python 3.x. However, Informatica has not tested this.)

* The Python module "cffi" must be installed.
See [Installation and Status](https://cffi.readthedocs.io/en/latest/installation.html).

# Generate the Wrapper

* Download um_python project from
[Github repository](https://github.com/UltraMessaging/um_python).
You can either clone the repository or
[download the ZIP file](https://github.com/UltraMessaging/um_python/archive/master.zip).
From Linux, enter:
```
wget https://github.com/UltraMessaging/um_python/archive/master.zip
unzip master
cd um_python-master
```

* Create the Wrapper:
```
./build_lbm_py.sh UM_PLATFORM_DIR
```
where UM_PLATFORM_DIR is the path to the directory where UM is installed.
For example:
```
./build_lbm_py.sh $HOME/UMP_6.11.1/Linux-glibc-2.5-x86_64
```
The tool expects to find the "lib" and "include" directories there.

The tool generates the file "_lbm_cffi.so" which implements the API wrapper.

# Test the Wrapper

* Set the environment variable "LD_LIBRARY_PATH" to the "lib" directory of
your UM installation.
For example:
```
export LD_LIBRARY_PATH=$HOME/UMP_6.11.1/Linux-glibc-2.5-x86_64/lib
```

* Define your license key.
For example:
```
export LBM_LICENSE_INFO='Product=UME:Organization=My Org:Expiration-Date=never:License-Key=XXXX XXXX XXXX XXXX'
```

* Run the program.
For example:
```
python lbmsrc.py
```

**WARNING**: the lbmsrc.py program publishes messages to your network on
the topic "test".
It will look for the file "um.cfg" and read a configuration if it exists,
but if not, it will simply use all of the default topic resolution multicast
group.
If your internal network has other programs running that use UM's
default topic resolution multicast group, **this test has the ability to
disrupt those programs**.
Informatica recommends creating a "um.cfg" file with multicast groups that
do not interfere with other instances of UM.

# Using the API

It is beyond the scope of this project to produce stand-alone documentation
of the Python wrapper API.
The user is expected to be familiar with the C API and with how cffi
wraps functions and structures.
See [cffi documentation](https://cffi.readthedocs.io/en/latest/overview.html).

The lbmsrc.py and lbmrcv.py example programs should get you started.
The generated file "_lbm_cffi.c" can also sometimes be helpful.

# Troubleshooting

## Problems running build_lbm_py.sh

```
Traceback (most recent call last):
  File "/home/sford/python/new/lbmwrapper.py", line 1, in <module>
    from cffi import FFI
ImportError: No module named cffi
Cannot continue processing, error occured
```

You or your system administrator needs to install cffi.
See [cffi installation instructions](https://cffi.readthedocs.io/en/latest/installation.html).
