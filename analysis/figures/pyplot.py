import matplotlib

# The backend must be chosen before pyplot is first imported; Agg writes files without a display.
matplotlib.use("Agg")

import matplotlib.pyplot as plt  # noqa: E402

__all__ = ["plt"]
