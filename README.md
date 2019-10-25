# um_python Vers 0.4
Python API generator for Ultra Messaging using Python cffi.

* [Introduction](#introduction)
* [Prerequisites](#prerequisites)
* [Generate the Wrapper](#generate-the-wrapper)
* [Test the Wrapper](#test-the-wrapper)
* [Using the API](#using-the-api)
* [Troubleshooting](#troubleshooting)
* [To Do](#to-do)

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

**ATTENTION**: this Python API is \*not\* an official part of the UM
product and has not been extensively tested by us.
We offer it to you to shorten your development cycle, but understand that
it has not been through our QA cycle.
We are happy look into any problems you find and fix them if possible.
But the bulk of testing responsibility is yours.
Please contact us through the normal UM support channel if you encounter
problems and/or have suggestions for its improvement.

We actively encourage our users to submit improvements to this project.
If your UM Python submission is better served as a separate project, we
will link to it, or will even consider hosting it under the UltraMessaging
org if you prefer.
See [To Do](#to-do) for more information.

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
See [cffi installation instructions](https://cffi.readthedocs.io/en/latest/installation.html).

# Generate the Wrapper

* Download um_python project from
[Github repository](https://github.com/UltraMessaging/um_python).
You can either clone the repository or
[download the ZIP file](https://github.com/UltraMessaging/um_python/archive/master.zip).
From Linux, enter:
```
wget -O um_python-master.zip https://github.com/UltraMessaging/um_python/archive/master.zip
unzip um_python-master.zip
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

The tool generates a ".so" file which implements the API wrapper.
Python 2.7 names the file "_lbm_cffi.so", and Python 3.7 names the
file in a more complicated way.
For example,
on my system it names it "_lbm_cffi.cpython-37m-x86_64-linux-gnu.so".
At any rate, look for "*.so" and make sure that file is available to Python
at run-time.

# Test the Wrapper

**WARNING**: the "lbmtst.py" program publishes messages to your network on
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
(The "lbmtst.py" test program demonstrates both ways.
Search for "lbm_src_notify_func" for the data structure method.)

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
it only allows for a single callback of each type.
However, it is not unusual for a developer to want to have multiple callback
functions for the same callback type.
For example, messages from different topics or classes of topics might
require different application logic to process.

### LbmRcvCallback Class

A simple general approach of solving this problem is to define a callback
class which decouples the application callback from the function that
the wrapper directly calls.
This approach is demonstrated for the receiver callback in the "lbmtst.py"
test program using a class named "LbmRcvCallback".
It works as follows:

1. The wrapper calls pylbm_rcv_cb_proc()
2. pylbm_rcv_cb_proc() assumes the clientd is an instance of the
LbmRcvCallback class, and invokes the lbm_rcv_deliver() method.
3. lbm_rcv_deliver() calls the application's registered callback.

Note however that this class introduces a small additional latency.

### Multiple Entry Points

A lower-latency solution is to define multiple Python entry points that are
directly callable by the wrapper.
This can be done by editing the "lbm_py_callback.h" file and adding
additional entries.
And then re-building the wrapper layer using the command:
```
python `pwd`/lbmwrapper.py
```

For example, to add a second receiver callback, you could do this:
```
echo 'extern "Python" int  my_rcv_cb_2(lbm_rcv_t *rcv, lbm_msg_t *msg, void *clientd);' >>lbm_py_callback.h
python `pwd`/lbmwrapper.py
```

Then, inside your application:
```
@ffi.def_extern()
def my_rcv_cb_2(rcv, msg, clientd):
    ...

...
lib.lbm_rcv_create(p_rcv, ctx, topic, lib.my_rcv_cb_2,
                              my_clientd, ffi.NULL)
```

The disadvantage of doing all this is that you need to re-build the
wrapper any time some application wants to add an additional callback,
and could lead to multiple versions of the wrapper for different
applications.
However, if you simply consider the wrapper to be a part of the
application and package the two together, it might be a workable plan.

# Troubleshooting

## Import Problem Running build_lbm_py.sh

```
Traceback (most recent call last):
  File "/home/sford/python/new/lbmwrapper.py", line 1, in <module>
    from cffi import FFI
ImportError: ...
Cannot continue processing, error occured
```

You or your system administrator needs to install cffi.
See [cffi installation instructions](https://cffi.readthedocs.io/en/latest/installation.html).

## Import Problem Running Application

```
Traceback (most recent call last):
  File "lbmtst.py", line 22, in <module>
    from _lbm_cffi import ffi, lib
ImportError: ...
```

This can mean that the ".so" wrapper library can't be found by Python.

It can also mean that the wrapper was generated with one version of Python
and the program is being run with the other version of Python.

## Convert Problem Running Application

```
Trying to convert the result back to C:
TypeError: an integer is required
```

This can mean that you coded an application callback that didn't return
a value.
Most application callbacks need to return an integer value zero.

# To Do

At present, Informatica does not have specific plans to implement any
of the following improvements.
We welcome contributions by the user community.

User submissions that include Python code should be
[PEP 8](https://www.python.org/dev/peps/pep-0008/) compliant and pass "pylint"
with no warnings, using a minimum of pylint disable/enable comments.
Use of "pycodestyle" is also recommended.

## Wrap the Wrapper

By its very nature, the cffi-based API is C-centric.
The non-time-critical parts of the API could be made more pythonic
and object-oriented by creating a Python wrapper around the cffi API.
For non-latency-sensitive applications, even the send and receive
paths could be wrapped.

## Test Suite

The um_python project should have a reasonably thorough automated
test suite.
A traditional unit test suite is not possible since the underlying
UM library functions are not testable in isolation.
But some kind of integration/system-level test would be helpful.
