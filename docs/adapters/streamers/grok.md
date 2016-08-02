# grok

The `grok` streamer can handle parsing almost any unstructed lines of text by
allowing you to define a `pattern` on how the lines are constructed which is
then used to deconstruct those lines into its various fields. The arguments
that the `grok` streamer currently exposes are:

## read

Argument | Description                                               | Required?
-------- | --------------------------------------------------------- | :---------
headers  | boolean used to specify to print or not print the headers | No, default: `True`

## write

Grok can not be used for writing data at this point in time.
