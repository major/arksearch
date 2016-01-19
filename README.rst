Command line Intel ARK search
=============================

This **completely unofficial** script will perform a search of `Intel's ARK site`_ for processor information.

Installation
------------

From PyPi::

    pip install arksearch

or via git::

    git clone https://github.com/major/arksearch
    cd arksearch
    python setup.py install

Usage
-----

Using the script is fairly straightforward:

* Search for a processor, such as the ``E3-1230``
* Choose the exact processor from a list
* Read the data printed below

Here's a brief example:

::

    $ arksearch E3-1230
    Found 5 processors...
    [0] Intel® Xeon® Processor E3-1230 v5 (8M Cache, 3.40 GHz)
    [1] Intel® Xeon® Processor E3-1230L v3 (8M Cache, 1.80 GHz)
    [2] Intel® Xeon® Processor E3-1230 v3 (8M Cache, 3.30 GHz)
    [3] Intel® Xeon® Processor E3-1230 v2 (8M Cache, 3.30 GHz)
    [4] Intel® Xeon® Processor E3-1230 (8M Cache, 3.20 GHz)
    Which processor? 0
    +----------------------------------------------------------+-----------------------------------------+
    | Parameter                                                | Value                                   |
    +----------------------------------------------------------+-----------------------------------------+
    | Status                                                   | Launched                                |
    | Launch Date                                              | Q4'15                                   |
    | Processor Number                                         | E3-1230V5                               |
    | Intel® Smart Cache                                       | 8 MB                                    |
    | DMI3                                                     | 8 GT/s                                  |
    | Instruction Set                                          | 64-bit                                  |
    | Instruction Set Extensions                               | SSE4.1/4.2, AVX 2.0                     |
    ... SNIP ...

This is handy for quick, single CPU lookups. However, if you need bulk access to data, please `sign up for an API key`_.

Pull requests are always welcome.

*-- Major*

.. _Intel's ARK site: http://ark.intel.com/
.. _sign up for an API key: http://odata.intel.com/
