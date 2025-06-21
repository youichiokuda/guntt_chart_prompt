from datetime import datetime
from types import SimpleNamespace

class DataFrame:
    def __init__(self, data=None):
        if data is None:
            self._data = []
            self.columns = []
        elif isinstance(data, list):
            self._data = [dict(row) for row in data]
            self.columns = list(data[0].keys()) if data else []
        elif isinstance(data, dict):
            self.columns = list(data.keys())
            zipped = zip(*data.values())
            self._data = [dict(zip(self.columns, row)) for row in zipped]
        else:
            raise ValueError("Unsupported data type for DataFrame")

    def __len__(self):
        return len(self._data)

    @property
    def empty(self):
        return len(self._data) == 0

    def __getitem__(self, column):
        return [row.get(column) for row in self._data]

    def __setitem__(self, column, values):
        if not isinstance(values, list):
            values = [values] * len(self._data)
        for i, value in enumerate(values):
            if i >= len(self._data):
                self._data.append({})
            self._data[i][column] = value
        if column not in self.columns:
            self.columns.append(column)

    @property
    def iloc(self):
        parent = self
        class _ILoc:
            def __getitem__(self, idx):
                return parent._data[idx]
        return _ILoc()

    def sort_values(self, column, ascending=True):
        self._data.sort(key=lambda row: row.get(column), reverse=not ascending)
        return self

    def iterrows(self):
        for idx, row in enumerate(self._data):
            yield idx, row


def to_datetime(values):
    def _convert(v):
        if isinstance(v, datetime):
            return v
        return datetime.fromisoformat(str(v))
    if isinstance(values, list):
        return [_convert(v) for v in values]
    return _convert(values)

class _APITypes:
    @staticmethod
    def is_datetime64_any_dtype(arr):
        return all(isinstance(x, datetime) for x in arr)

api = SimpleNamespace(types=_APITypes())

def Timestamp(value):
    return to_datetime(value)
