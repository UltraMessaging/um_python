# um_python Vers 0.3
Python API generator for Ultra Messaging using Python cffi.

**THIS IS A WORK IN PROGRESS** Disruptive changes should be expected
on a daily, even hourly basis.
There is no "stable" release as yet, although we attempt to make the
"master" branch at least buildable at any given time.
The purpose for publishing the um_python project this early is to give
users a feeling for the direction we are going, and to give users the
opportunity to contribute.

* [Introduction](#introduction)
* [Prerequisites](#prerequisites)
* [Generate the Wrapper](#generate-the-wrapper)
* [Test the Wrapper](#test-the-wrapper)
* [Using the API](#using-the-api)
* [Troubleshooting](#troubleshooting)

# Introduction

This project is a simple tool to generate an Ultra Messaging wrapper API for
Python using cffi.

Note that a cffi API is a python wrapper around a native library,
and therefore requires the UM native dynamic library to be installed.
I.e. this is not a pure Python implementation of UM.

Python itself has tools to make the generation of cffi APIs reasonably easy.
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

* The "python" command must invoke Python.
Make sure it is in your PATH.
We have tried it with both Python 2.7 and 3.7; both seem to work.
However, a single ".so" will not work for both Python versions.
You must build the ".so" with the version of Python that you plan to use
in your runtime environment.

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

**WARNING**: the lbmtst.py program publishes messages to your network on
the topic "lbmtst.py".
It will look for the file "um.cfg" and read a configuration if it exists,
but if not, it will simply use all of the default topic resolution multicast
group.
If your internal network has other programs running that use UM's
default topic resolution multicast group, **this test has the ability to
disrupt those programs**.
Informatica recommends creating a "um.cfg" file with multicast groups that
do not interfere with other instances of UM.

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

* Run test program.
Publishes 50 messages and receives all of them.
```
python lbmtst.py
```

# Using the API

It is beyond the scope of this project to produce stand-alone documentation
of the Python wrapper API.
The user is expected to be familiar with the C API and with how cffi
wraps functions and structures.
Since cffi is a wrapper around the C API, the
[Ultra Messaging C API](https://ultramessaging.github.io/currdoc/doc/API/index.html)
documentation should be used for API information.
See also
[cffi documentation](https://cffi.readthedocs.io/en/latest/overview.html).

The lbmtst.py example program should get you started.
The generated files "_lbm_cffi.c" and "lbm_py_callback.h" can also be helpful.
Although these files are only needed for the generation of the wrapper and
not is needed at runtime, we recommend keeping them for reference purposes.

## Callbacks

UM uses a large number of application callbacks (54 as of UM version 6.11.1),
although most real-world applications only use a few of them.
The application passes a pointer to its function either as a parameter to
a UM API function, or as a field in a UM data structure.

To keep the UM Python wrapper as fast and efficient as possible, a single
Python function is defined for each callback type (signature).
The application must supply a function with that name and pass it to the
UM API which sets the callback.

When "./build_lbm_py.sh" is executed to create the wrapper, it creates
a file named "lbm_py_callback.h" which defines the Python functions that
the wrapper can call.

For example, consider a UM receiver.
A C application creates a receiver by calling
[lbm_rcv_create](https://ultramessaging.github.io/currdoc/doc/API/lbm_8h.html#aa7491c50fefbc2b70f8035fce7ac1477).
The 4th parameter is defined as:
```
  lbm_rcv_cb_proc  proc
```
where "lbm_rcv_cb_proc" is a typedef.

To determine the corresponding Python function, drop any "_t" suffix
(there isn't one for this typedef) and add a "py" in front.
So, look in "lbm_py_callback.h" and find the function named
"pylbm_rcv_cb_proc".
It should look like this:
```
  extern "Python" int  pylbm_rcv_cb_proc(lbm_rcv_t *rcv, lbm_msg_t *msg, void *clientd);
```

This guides you in the definition of the python function, which should be
defined like this:
```
@ffi.def_extern()
def pylbm_rcv_cb_proc(rcv, msg, clientd):
```

This approach has a significant disadvantage:
It is not unusual for a developer to want to have different receive
callbacks for different topics (or classes of topics).
A simple approach of solving this problem is to define a callback class which
decouples the callback that UM calls from the application callback
function.
This approach is demonstrated for the receiver callback in the "lbmtst.py"
test program using a class named "LbmRcvCallback".
Note however that this class introduces a small additional latency.
For the lowest possible latency, you must directly use the single receiver
callback "pylbm_rcv_cb_proc()".

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
