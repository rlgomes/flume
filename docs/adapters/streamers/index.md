# streamers

Streamers are an abstraction on reading and writing different formats that
can be used by various [adapters](../../adapters) within **flume**. Not all
adapters have a need for using streamers but for those that do it because
quite easy to support various different formats.

## builtin

  * [csv](csv/) - Comma-Separated Values
  * [grok](grok/) - parse arbitrary text and structure it
  * [json](json/) - JavaScript Object Notation
  * [jsonl](jsonl/) - JSON Lines 

## write your own

All streamers extend from the **flume.adapters.streamres.base.Streamer** class
and implement the following methods:

  * **__init__** with keyword arguments for toggling special features
  * **read(self, stream)** read method that receives a **Python** an input
                           stream and should generate the various **flume** 
                           points (**from flume import Point**) that were
                           parsed from the stream.
  * **write(self, stream, points)** write method that receives an output stream
                                    and a list of points and should serialize
                                    those points onto the stream.
  * **eof(self, stream)** optionally if you want to do something special when
                          there are no more points to write then you can
                          implement the eof method and write to the stream
                          provided.

Once you've written your streamer you have to register it with **flume** using
the function **register_streamer(name, streamer)** where the name is a unique
string identifying your adapter such as elastic, http, influxdb, etc. and the
streamer is the class implementation of your streamer.
