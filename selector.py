import tkinter as tk
from dataclasses import dataclass


@dataclass
class ScreenRegion:
    x1: int
    y1: int
    x2: int
    y2: int
    relative_x1: float  # Percentage from left
    relative_y1: float  # Percentage from top
    relative_width: float  # Percentage of screen width
    relative_height: float  # Percentage of screen height
    horizontal_sections: int  # Number of horizontal divisions
    vertical_sections: int   # Number of vertical divisions
    # Which sections are covered horizontally (start, end)
    horizontal_span: tuple
    # Which sections are covered vertically (start, end)
    vertical_span: tuple

    def generate_region_formula(self) -> str:
        """Generate a Python dictionary formula for the region calculation."""
        # Calculate if this is aligned to any edge
        is_left = self.relative_x1 < 0.1
        is_right = self.relative_x1 + self.relative_width > 0.9
        is_top = self.relative_y1 < 0.1
        is_bottom = self.relative_y1 + self.relative_height > 0.9

        # Generate formulas for each component
        left_formula = (
            "0" if is_left else
            f"width - (width // {round(1/self.relative_width)})" if is_right else
            f"width * {self.relative_x1:.3f}"
        )

        top_formula = (
            "0" if is_top else
            f"height - (height // {round(1/self.relative_height)})" if is_bottom else
            f"height * {self.relative_y1:.3f}"
        )

        width_formula = (
            f"width // {round(1/self.relative_width)}"
            if self.relative_width < 0.5 else
            f"width * {self.relative_width:.3f}"
        )

        height_formula = (
            f"height // {round(1/self.relative_height)}"
            if self.relative_height < 0.5 else
            f"height * {self.relative_height:.3f}"
        )

        formula = f"""region = {{
    'left': {left_formula},  # {self._generate_position_comment('horizontal')}
    'top': {top_formula},  # {self._generate_position_comment('vertical')}
    'width': {width_formula},  # {self._generate_size_comment('width')}
    'height': {height_formula}  # {self._generate_size_comment('height')}
}}"""
        return formula

    def _generate_position_comment(self, direction: str) -> str:
        """Generate a human-readable comment for position."""
        if direction == 'horizontal':
            if self.relative_x1 < 0.1:
                return "Start from left side"
            elif self.relative_x1 + self.relative_width > 0.9:
                return "Start from right side"
            else:
                return f"Start at {self.relative_x1:.1%} from left"
        else:
            if self.relative_y1 < 0.1:
                return "Start from top"
            elif self.relative_y1 + self.relative_height > 0.9:
                return "Start from bottom"
            else:
                return f"Start at {self.relative_y1:.1%} from top"

    def _generate_size_comment(self, dimension: str) -> str:
        """Generate a human-readable comment for size."""
        value = self.relative_width if dimension == 'width' else self.relative_height
        fraction = round(1/value) if value < 0.5 else None

        if fraction:
            return f"1/{fraction} of screen {dimension}"
        else:
            return f"{value:.1%} of screen {dimension}"


class ScreenSelector:
    def __init__(self):
        self.root = tk.Tk()
        self.root.wait_visibility(self.root)
        self.root.wm_attributes('-alpha', 0.3)  # Changed for linux
        self.root.attributes('-fullscreen', True)
        self.root.attributes('-topmost', True)

        # Create canvas
        self.canvas = tk.Canvas(self.root, cursor="cross")
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # Variables for drawing
        self.start_x = None
        self.start_y = None
        self.current_rect = None
        self.screen_width = self.root.winfo_screenwidth()
        self.screen_height = self.root.winfo_screenheight()

        # Bind events
        self.canvas.bind("<Button-1>", self.start_draw)
        self.canvas.bind("<B1-Motion>", self.draw)
        self.canvas.bind("<ButtonRelease-1>", self.end_draw)
        self.canvas.bind("<Escape>", self.cancel)
        self.root.bind("<Escape>", self.cancel)

        self.result = None

    def start_draw(self, event):
        self.start_x = event.x
        self.start_y = event.y
        if self.current_rect:
            self.canvas.delete(self.current_rect)
        self.current_rect = self.canvas.create_rectangle(
            self.start_x, self.start_y, self.start_x, self.start_y,
            outline='red', width=2
        )

    def draw(self, event):
        if self.current_rect:
            self.canvas.coords(self.current_rect,
                               self.start_x, self.start_y,
                               event.x, event.y)

    def end_draw(self, event):
        end_x, end_y = event.x, event.y

        # Calculate relative positions and sizes
        x1 = min(self.start_x, end_x)
        y1 = min(self.start_y, end_y)
        x2 = max(self.start_x, end_x)
        y2 = max(self.start_y, end_y)

        relative_x1 = x1 / self.screen_width
        relative_y1 = y1 / self.screen_height
        relative_width = (x2 - x1) / self.screen_width
        relative_height = (y2 - y1) / self.screen_height

        # Calculate best-fit sections
        h_sections = self.calculate_best_sections(x1, x2, self.screen_width)
        v_sections = self.calculate_best_sections(y1, y2, self.screen_height)

        self.result = ScreenRegion(
            x1=x1,
            y1=y1,
            x2=x2,
            y2=y2,
            relative_x1=relative_x1,
            relative_y1=relative_y1,
            relative_width=relative_width,
            relative_height=relative_height,
            horizontal_sections=h_sections[0],
            vertical_sections=v_sections[0],
            horizontal_span=h_sections[1],
            vertical_span=v_sections[1]
        )

        self.root.quit()

    def calculate_best_sections(self, start, end, total_size, max_sections=16):
        """Find the best way to divide the screen into sections (max 16) that encompass the selection."""
        best_sections = (1, (0, 1))
        best_error = float('inf')
        target_size = end - start

        for sections in range(2, max_sections + 1):
            section_size = total_size / sections
            start_section = int(start / section_size)
            # Ensure region covered
            end_section = int((end + section_size - 1) / section_size) - 1

            # Calculate the actual size this would cover
            actual_start = start_section * section_size
            actual_end = (end_section + 1) * section_size
            actual_size = actual_end - actual_start

            # Calculate error as a combination of position offset and size difference
            # Favor slightly larger regions over smaller ones
            position_error = abs(start - actual_start) + abs(end - actual_end)
            size_error = actual_size - \
                target_size if actual_size >= target_size else (
                    target_size - actual_size) * 2
            error = position_error + size_error

            if error < best_error:
                best_error = error
                best_sections = (sections, (start_section, end_section + 1))

        return best_sections

    def cancel(self, event):
        self.result = None
        self.root.quit()

    def get_region(self):
        self.root.mainloop()
        self.root.destroy()
        return self.result


def capture_screen_region():
    selector = ScreenSelector()
    region = selector.get_region()

    if region:
        region.generate_region_formula()
        return region
    return None
