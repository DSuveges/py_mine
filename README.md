# py_mine

The `prototype.ipynb` notebook contains the prototype of the minefield logic and data model.

## Summary of the logic

1. The minefield object can be initialized by providing the x and y lenght of the fields + number of mines.
2. Upon initialization the coordinates of the provided number of mines are generated within the field.
3. Upon "clicking" on a filed the number of mines in the neighbouring fields is returned.
4. Clicking on a coordinate of a mine will return 1 - indicating death.
5. Each click is stored in a list. If clicking in a field which has alrady been clicked triggers the return of 2.
6. If the number of mines in the neighbouring fields is zero, then clicking all neighbouring cells recursively.
7. If the number of mines == number of un-clicked fields, triggers the return of -1 indicating winning.
