# github

A collection of github utilities that allow you to easily read data from github.

# issues api

## user issues source

```python
github.issues.user(oauth=None,
                   **parameters)
```

Argument   | Description                                                               | Required?
---------- | ------------------------------------------------------------------------- | :---------
oauth      | the github oauth token to use when reading the authenticated users issues | Yes
parameters | [parameters](https://developer.github.com/v3/issues/#parameters)          | 

The `parameters` are any of the parameters exposed by the API that we've
exposed as a keyword argument.

## orgs issues source

```python
github.issues.orgs(org_name,
                   oauth=None,
                   **parametrs)
```

Argument   | Description                                                               | Required?
---------- | ------------------------------------------------------------------------- | :---------
org_name   | name of the organization on github                                        | Yes
oauth      | the github oauth token to use when reading the authenticated users issues | Yes
parameters | [parameters](https://developer.github.com/v3/issues/#parameters)          | 

The `parameters` are any of the parameters exposed by the API that we've
exposed as a keyword argument.

## repo issues source

```python
github.issues.repo(owner,
                   repo_name,
                   oauth=None,
                   **parametrs)
```

Argument   | Description                                                               | Required?
---------- | ------------------------------------------------------------------------- | :---------
owner      | name of the repo owner on github                                          | Yes
repo_name  | name of the repo name on github                                           | Yes
oauth      | the github oauth token to use when reading the authenticated users issues | Yes
parameters | [parameters](https://developer.github.com/v3/issues/#parameters-1)        | 

The `parameters` are any of the parameters exposed by the API that we've
exposed as a keyword argument.

## issue source

```python
github.issues.issue(owner,
                    repo_name,
                    issue_number,
                    oauth=None)
```

Argument     | Description                                                               | Required?
------------ | ------------------------------------------------------------------------- | :---------
owner        | name of the repo owner on github                                          | Yes
repo_name    | name of the repo name on github                                           | Yes
issue_nubmer | the github issue number to retrieve the details for                       | Yes
oauth        | the github oauth token to use when reading the authenticated users issues | Yes

# pulls api

## repo pull requests source 

```python
github.pulls.repo(owner,
                  repo_name,
                  oauth=None,
                  **parameters)
```

Argument   | Description                                                               | Required?
---------- | ------------------------------------------------------------------------- | :---------
owner      | name of the repo owner on github                                          | Yes
repo_name  | name of the repo name on github                                           | Yes
oauth      | the github oauth token to use when reading the authenticated users issues | Yes
parameters | [parameters](https://developer.github.com/v3/pulls/#parameters)           | No

The `parameters` are any of the parameters exposed by the API that we've
exposed as a keyword argument.

## pull request commits source 

```python
github.pulls.commits(owner,
                     repo_name,
                     pull_number,
                     oauth=None,
                     **parameters)
```

Argument    | Description                                                               | Required?
----------- | ------------------------------------------------------------------------- | :---------
owner       | name of the repo owner on github                                          | Yes
repo_name   | name of the repo name on github                                           | Yes
pull_number | pull number to get the commits associated with from github                | Yes
oauth       | the github oauth token to use when reading the authenticated users issues | Yes
