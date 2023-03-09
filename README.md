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
#### Fun example
```python
from datetime import datetime as dt
from pyntree import Node
data = {'right_now': dt.now()}  # Some sample data
Node(data).save('file.pyn')  # 1-liner to save your data to a file!
```

## Status
pyntree is currently in beta while I battle-test it and work out any bugs not found by the unit tests.

Under normal usage pyntree should perform as expected, but I cannot guaruntee it is production-ready.

You can help by installing and testing the latest release, and reporting any bugs.

You can also star/watch this repository to be notified when I make changes and release updates.

## Docs
The documentation is available at https://pen.jvadair.com/books/pyntree

## Project board
To view, visit https://board.jvadair.com
and use credentials:
- Username: public
- Password: public

## Contributing
If you would like to contribute, feel free to fork the repository and start a pull request. I will manually review/test them before implementing. If you have any questions regarding the project or how to contribute, you're welcome to [contact me](mailto:dev@jvadair.com).

<p align="center">
Copyright &copy; 2023 James Adair
</p>
