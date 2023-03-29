![](img/pyntree-banner.jpeg)

# About

#### pyntree is a python package which allows you to easily and syntactically save your data. Not only that, it also lets you save in multiple formats, and even serialize and compress data by merely changing a few characters.

## Installing
`pip install pyntree`

## Example usage
```python
from pyntree import Node
db = Node("your_new_db.pyn")
db.hello = "world"
db.hello()
# Output: "world"
db.save()
```
#### 1-liner for saving existing data
```python
from datetime import datetime as dt
from pyntree import Node
data = {'right_now': dt.now()}  # Some sample data
Node(data).save('file.pyn')  # 1-liner to save your data to a file!
```

## Features
pyntree is capable of handling the following files, functions, and formats:
- Dictionaries in plain text
- Pickled files/serialization
- JSON files
- Encryption
- Backwards compatibility with files saved by pyndb (except encrypted files)
- Compression in many popular formats
- Autosaving & saving on close (when garbage collected)
- ...and more!

## Docs
The documentation is available at https://pen.jvadair.com/books/pyntree

## Project board
To view, visit https://board.jvadair.com and use credentials:
- Username: public
- Password: public

## Contributing
If you would like to contribute, feel free to fork the repository and start a pull request. I will manually review/test them before implementing. If you have any questions regarding the project or how to contribute, you're welcome to [contact me](mailto:dev@jvadair.com).

<p align="center">
Copyright &copy; 2023 James Adair
</p>
