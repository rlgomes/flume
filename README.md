# flume

**flume** (pronounced *floom*) is a stream processing framework based off of an
older project called [juttle](http://juttle.github.io) from work I did at a previous
company. With **flume** I wanted to be able to use a similar syntax to that of
**juttle** but have the ability to write the stream pipelines in an imperative
programming language such as **python** where you can better coordinate the way
the various pipelines are connected and their order of execution.

This is in no way a production ready solution and actually there are a ton of
features missing which would make this more interesting but I wanted to get
the code up and start sharing it with others to see if there's any interest in
further developing this. I'll continue to tweak and adding things as I have
time and find something I need to accomplish with **flume**.

# installation

## from pypi

```bash
pip install flume
```

## from source

```bash
pip install -e git+git://github.com/rlgomes/flume.git#egg=flume
```

# development

All contributions are welcome! File an issue on anything you'd like to see
added or open a pull request with fixes or new features you'd wanted added to
**flume**.

## running tests

The **flume** tests are broken into unittests and integration tests with the
following directory structure:

```
  test/unit
  test/integration
```

They can easily be executed with the *Makefile* running:

```bash
make unit
```

or

```bash
make integration
```

## running coverage check

To run the same check we run in Travis to make sure that code coverage is above
90% simple run:

```bash
make coverage
```
