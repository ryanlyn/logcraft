# `logcraft`
Python Macro-Generated Logging from Comments

## Introduction
### What is `logcraft`?
`logcraft` gives the functionality of automatically generating logging calls from annotated comments. This treats logging as documentation, separates application logging and program flow to the highest degree, and provides an overall better development experience.

Source code files are not modified. Instead the `@log` macro is only applied at the decoration of your object. This gives greater transparency and control to the developer.

<table>
<tr>
<td> Write This: </td> <td> Instead Of: </td>
</tr>
<tr>
<td> 

```python
@log
def do_something(x):
    #i: started doing something with {x}
    x = do_something_interesting(x)
    #i finished doing something
    return x
```

</td>
<td>

```python

def do_something(x):
    logging.info(f"started doing something with {x}")
    x = do_something_interesting(x)
    logging.info("finished doing something")
    return x
```

</td>
</tr>
</table>

Moreover, `logcraft` has the following benefits:
- No external dependencies
- Macro expansion is limited to decorated objects
- No source files are modified
- Works with `pickle` and other serialisation libraries
- Inject your own logger ([loguru](https://github.com/Delgan/loguru) etc.) or a custom callable to replace `print`
- Allows continuation over multiple comments
- Allows string formatting with evaluated variables

Inspired by: [node-comment-macros](https://github.com/tj/node-comment-macros) and conversations with [@kale](https://github.com/kmiller96) and [@jiaxi](https://github.com/jiaxililearn).

### Why `logcraft`?
A lot of logging in Python these days are simply descriptive in nature (e.g. "procedure `x` started" or "`x` iteration has `y` variable"). These logging calls usually adds no functionality to the program logic and clouds the programmer's interpretation of the source code.

This library applies the opinion that __logging which are documentative in nature should be treated as documentation__.

Hence, logging should be generated from annotated comments and logging configuration should be easily injected without modifying the program logic. Having logging as comments results in a clear delineation

### How Do I Install?
Simply run:
```bash
pip install logcraft
```

## Quickstart
Import the `@log` decorator:
```python
from logcraft.macro import log
```

Decorate your object with `@log` and annotate comments which are intended to be logging messages. Comments with the same annotation and are right after another are treated as continuations of the same logging call. Furthermore, annotated comments with `"{}"` will be expanded into f-strings that references variables in the local or global namespaces. 

_Note that `@log` has to be the top decorator_

The following:
```python
@log
def add_one(sequence):
    """Adds 1 to sequence"""
    #: add print call with line
    #: continuation
    # this is some ignored comment
    #: add another line

    #i: this is an info message
    #d: this is a debug message

    new_sequence = []
    for x in sequence:
        #d: adding 1 to x={x}
        new_sequence.append(x + 1) 
        #d: finished adding 1 to x={x}
    #i: constructed new sequence {new_sequence}

    return new_sequence
```
Will be expanded to:
```python
def add_one(sequence):
    """Adds 1 to sequence"""
    print("add print call with line continuation")
    # this is some ignored comment
    print("add another line")

    logging.info("this is an info message")
    logging.debug("this is a debug message")

    new_sequence = []
    for x in sequence:
        logging.debug(f"adding 1 to x={x}")
        new_sequence.append(x + 1) 
        logging.debug(f"finished adding 1 to x={x}")
    logging.info(f"constructed new sequence {new_sequence}")

    return new_sequence
```
## List of Annotations
The following are the available list of annotations:

```python
#: callable (default: print)

#c: logging.critical 
#d: logging.debug
#e: logging.error
#f: logging.fatal
#i: logging.info
#w: logging.warn
```

## Other Installation Methods
### Source
Clone the repository:
```bash
git clone https://github.com/ryanlyn/logcraft
```

Run installation:
```bash
cd logcraft
python setup.py install
```

## License
`logcraft` is made available under the MIT License. For more details, see the [LICENSE](./LICENSE).
