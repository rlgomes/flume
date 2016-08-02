# http adapter

The `http` adapter can be used to read and write data to and from an HTTP server.

## read

Reading from an HTTP request is done using the [read](../sources/read) source
with the following options available at this time:

```python
read('http',
     url=None,
     method='GET',
     headrs=None,
     time='time',
     follow_link=True,
     format=None,
     cache=None,
     status=200) | ...
```

Argument    | Description                                                               | Required?
----------- | ------------------------------------------------------------------------- | :---------
url         | URL to hit when issuing the HTTP request                                  | Yes
method      | method to use when issuing the HTTP request                               | No, default: `GET`
headers     | headers used when issuing the HTTP request                                | No, default: `None`
time        | field name that contains valid timestamp                                  | No, default: `time`
follow_link | boolean that indicates to follow the HTTP Link header (*)                 | No, default: `True`
format      | format specifier used to pick a different kind of [streamer](streamers/)  | No, default: `None`
cache       | specify a cache file to use for HTTP caching with **requests-cache** (**) | No, default: `None`
status      | specify the accepted status or statuses (list) for a successful request   | No, default: `200`

 * (*) [Link header RFC](https://goo.gl/Sigk0://tools.ietf.org/html/rfc5988)
 * (**) [requests-cache documentation](https://requests-cache.readthedocs.io/en/latest/)

## write

Writing to the HTTP adapter is done using the [write](../sinks/write) sink with
the following options available at this time:

```python
... | write('http',
            url=None,
            method='GET',
            headrs=None,
            array=True,
            status=200)
```

Argument    | Description                                                                  | Required?
----------- | ---------------------------------------------------------------------------- | :---------
url         | URL to hit when issuing the HTTP request                                     | Yes
method      | method to use when issuing the HTTP request                                  | No, default: `GET`
headers     | headers used when issuing the HTTP request                                   | No, default: `None`
array       | specify if the payload of the HTTP request should be an array or JSON object | No, default: `False`
status      | specify the accepted status or statuses (list) for a successful request      | No, default: `200`


## reading some points from Github

```python
from flume import count, read, reduce, write

(
    read('http',
         url='https://api.github.com/repos/rlgomes/flume/commits',
         cache='flume-http-cache',
         time='commit.author.date')
    | reduce(count=count())
    | write('stdio')
).execute()
```

The above **flume** program calculates how many commits there have been to the
**flume** github repo since it was first created. I turned the cache on so you
wouldn't hit any Github Rate Limiting issues and if you want to get the latest
and greatest data just delete the `flume-http-cache.sqlite` file.

## writing some points

```python
from flume import *

oauth_token = raw_input('Provide your github oauth token: ')

(
    emit(limit=1)
    | put(description='gist generated from flume at {time}',
          public=True,
          files={
              'example.txt': {
                  'content': 'just a silly example of what you can do'
              }
          })
    | remove('time')
    | write('http',
            url='https://api.github.com/gists',
            method='POST',
            headers={
                'authorization': 'token %s' % oauth_token,
                'content-type': 'application/json'
            },
            array=False)
).execute()
```

In order to run the above you'll have to create a throw away oauth token
at https://github.com/settings/tokens and remember to scroll down and give
access to create gists. Then when you run it you won't get any output but 
if you visit https://gist.github.com/ the last gist created should be called
`example.txt` and you should see all the details we created above.
