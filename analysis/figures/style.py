from analysis.configuration import Environment

THREADS = (1, 2, 4, 6, 7, 8)
COLORS: dict[str, str] = {Environment.NATIVE: "#4C78A8", Environment.CHROME: "#E45756", Environment.FIREFOX: "#F58518"}

PANEL_COLUMNS = 3
PANEL_WIDTH = 4
PANEL_HEIGHT = 3
MARKER_SIZE = 3
BAND_ALPHA = 0.2
TITLE_SIZE = 10
LEGEND_SIZE = 8
# In font-size units: a line sample long enough to show its dash pattern, columns close together.
LEGEND_HANDLE_LENGTH = 2.6
LEGEND_COLUMN_SPACING = 0.8
# The share of the figure's height left to the panels under a legend placed above them.
SHARED_LEGEND_TOP = 0.9
REFERENCE_COLOR = "grey"
REFERENCE_STYLE = "--"
REFERENCE_WIDTH = 0.8

# The paper's own figures are drawn at the size they are printed (inches), so their text is not
# scaled down: one row across both columns, or one column of the ACM sigplan page.
PAPER_FONT_SIZE = 8
PAPER_LEGEND_SIZE = 7
PAPER_ROW_SIZE = (7.0, 1.85)
PAPER_COLUMN_SIZE = (3.35, 1.8)
# One marker and one line style per k, since the lines of one browser share its colour.
K_MARKERS: dict[int | None, str] = {1: "o", 4: "s", 16: "^", 256: "D"}
K_LINES: dict[int | None, str] = {1: "-", 4: "--", 16: "-.", 256: ":"}
DEFAULT_MARKER = "o"
DEFAULT_LINE = "-"
