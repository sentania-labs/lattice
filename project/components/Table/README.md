The dense data table: uppercase headers, hairline rules, mono figures.

Headers are `micro` size, uppercase, in `ink-subtle`, separated from the body
by a full `line`. Body rows are divided by `line-soft`, which is what lets a
table of forty rows read as a block rather than a grid.

Any column of figures gets `.lat-num` on the cell. That right-aligns it,
switches to the mono family and turns on tabular numerals, so digits line up
column-wise and a person can compare two rows without counting places. A number
in the proportional sans is a number a person has to read twice.

Cells use `overflow-wrap: anywhere` because object keys and resource
identifiers do not contain spaces and will otherwise push the table wide. Wrap
the table in `.lat-table-scroll` so that when it does overflow, the table
scrolls and the page does not.

The consumer supplies sorting, selection and pagination. Lattice styles the
table; it is not a datagrid.

Derived from `preview.py`'s `table.pv-tbl` rules.
