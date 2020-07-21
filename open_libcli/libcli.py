from json import loads, dumps
from prettytable import PrettyTable
from time import gmtime, strftime


class PrintData(object):
    def __init__(self, data):
        """Print list (columns is not None) or
        a single object (columns is None)

        Data is a dict.

        Output can be a pretty table (the default) or
        a JSON (options['is_json'] is True)

        columns is the default columns to print for list. Can
        be overide with options['columns']
        """
        self.data = data

    def _format_multiple_values(self, values):
        """Format list in string to be printable as prettytable"""
        row_value = ""
        if len(values) > 0:
            last = values.pop()
            for o in values:
                row_value += "%s\n" % o
            row_value += last
        return row_value

    def printObject(self, options=None):
        """print a single object"""

        if options is None:
            options = {}

        if 'show_only' in options.keys() and options['show_only']:
            show_only = options['show_only']
            print(self.data[show_only])
            return

        if 'format' in options.keys():
            if options['format'] == 'json':
                print(dumps(self.data, indent=2))
                return

        if 'exclude' in options.keys() and options['exclude']:
            for exc in options['exclude']:
                try:
                    self.data.pop(exc)
                except KeyError:
                    print("Error: exclude key \'%s\' doesn't exists" % exc)
                    return

        table = PrettyTable(["Field", "Value"])
        table.align["Field"] = "l"
        for key in self.data.keys():
            # if key not in exclude:
            if type(self.data[key]) is list:
                table.add_row([
                    key,
                    self._format_multiple_values(self.data[key])
                ])
            else:
                if key.endswith(('Date', 'Expiry')) and \
                   not self.data[key] == 'null' and self.data[key]:
                    value = strftime(
                        "%Y-%m-%d %H:%M:%S UTC",
                        gmtime(float(self.data[key])/1000)
                    )
                else:
                    value = self.data[key]
                table.add_row([key, value])
        print(table)

    def printList(self, default_col=None, options=None):
        """Print list of data.
        default_col = [('real_column name', 'Print name'),
                       column_name,              #if not custom name
                       etc...]
        """

        if 'format' in options.keys():
            if options['format'] == 'json':
                print(dumps(self.data, indent=2))
                return

        if 'columns' in options.keys() and len(options['columns']) >= 1:
            # Check all colmuns are present in data
            columns = self.data[0].keys()
            for col in options['columns']:
                if col not in columns:
                    print("Error; columns %s is not present" % col)
                    return
            columns_key = options['columns']
            columns_name = options['columns']
        elif default_col:
            columns_key = []
            columns_name = []
            for col in default_col:
                if type(col) is tuple:
                    columns_key.append(col[0])
                    columns_name.append(col[1])
                else:
                    columns_key.append(col)
                    columns_name.append(col)
        else:
            columns_key = self.data[0].keys()
            columns_name = self.data[0].keys()
        table = PrettyTable(columns_name)
        no_table = ''
        for line in self.data:
            compiled_line = []
            for key in columns_key:
                if type(key) is tuple:
                    compiled_line.append(key[0]([line[i] for i in key[1]]))
                else:
                    compiled_line.append(line[key])
            table.add_row(compiled_line)
            no_table = '%s\n%s' % (no_table,' '.join(map(str,compiled_line)))
        if 'format' in options.keys():
            if options['format'] == 'bash':
                print(no_table)
                return
        print(table)
