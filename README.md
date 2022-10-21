# Literature Review Data Collection

This repository is the center of data collection for my literature review on
applying machine learning techniques to speed running. This document will go
over the different things that I can get from my data, and how you can do that
too.

## Contents

 - [Getting Data](#getting-data)
 - [Saving Data as JSON](#saving-data-as-json)

## Getting Data

In this project I am getting data directly from the [speedrun.com REST
API](https://github.com/speedruncomorg/api). This is implemented (quite nicely)
in Python in the form of [srcomapi](https://github.com/blha303/srcomapi). I
have written a wrapper around this to facilitate the data retrieval that will
be useful for my dissertation.

All the code that I have written is contained in `/srcomwrapper`, specifically
in `srcom.py`. Here you will find functions that relate to retrieving data both
as individual structs or collections that have been purpose made.

## Saving Data as JSON

When you have changed what you want to get inside of `main.py`, the next step
is to save this from stdout into a JSON file. I have implemented a Makefile
that will use [JQ](https://stedolan.github.io/jq/) to format JSON and save it
to a file. You can use it in the following:

```bash
make saveoutput filename=testfilename.json
```

The above command will save a file into the location of
`data/testfilename.json`. This (should) be properly formatted to be used in
some other program.
