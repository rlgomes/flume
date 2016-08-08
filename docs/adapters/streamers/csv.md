# csv

The `csv` streamer can handle the majority of `csv` files and even has a few
options to tweak the reading and writing of `csv` data:

## read

No arguments exposed at this point for read operations.

## write

Argument          | Description                                                                    | Required?
----------------- | ------------------------------------------------------------------------------ | :---------
headers           | boolean used to specify to print or not print the headers                      | No, default: `True`
delimiter         | delimiter character to use when reading the data                               | No, defualt: `,`
ignore_whitespace | boolean used to specify if any preceding/trailing whitespace should be ignored | No, default: `False`
