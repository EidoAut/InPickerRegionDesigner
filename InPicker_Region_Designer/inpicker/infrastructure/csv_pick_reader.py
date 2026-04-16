from __future__ import annotations

from typing import Iterable

import numpy as np

from inpicker.domain.exceptions import ValidationError


class CsvPickReader:
    REQUIRED_COLUMNS = ('x', 'y', 'z')

    def _normalize_rows(self, rows: np.ndarray) -> np.ndarray:
        if rows.dtype.names is None:
            raise ValidationError('CSV must include a header row with columns x,y,z.')
        names = {name.lower(): name for name in rows.dtype.names}
        missing = [col for col in self.REQUIRED_COLUMNS if col not in names]
        if missing:
            raise ValidationError(f"CSV is missing required columns: {', '.join(missing)}")
        if rows.shape == ():
            rows = np.array([rows], dtype=rows.dtype)
        return rows

    def read_csv_points(self, path: str) -> np.ndarray:
        try:
            rows = np.genfromtxt(path, delimiter=',', names=True, dtype=None, encoding='utf-8-sig')
        except Exception as exc:
            raise ValidationError(f'Could not read CSV file: {exc}') from exc
        if rows is None or (isinstance(rows, np.ndarray) and rows.size == 0):
            raise ValidationError('CSV file is empty or contains no data rows.')
        return self._normalize_rows(rows)
