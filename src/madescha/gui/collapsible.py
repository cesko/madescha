import sys
from typing import Optional
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QGroupBox, QApplication,
    QFrame, QScrollArea, QSizePolicy
)
from PySide6.QtCore import (
    Qt, QPropertyAnimation, QEasingCurve, QTimer,
    QPointF, Property
)
from PySide6.QtGui import QFont, QCursor, QPainter, QColor, QPolygonF, QPen


class ArrowWidget(QWidget):
    """
    A small widget that draws a filled triangle and can rotate it smoothly.
    0 degrees = pointing right (collapsed), 90 degrees = pointing down (expanded).
    """

    #ARROW_COLOR = QColor("#e67e22")

    def __init__(
        self,
        size: int = 11,
        parent: Optional[QWidget] = None,
        color: QColor = QColor("#000000")
    ) -> None:
        """
        Initialize the arrow widget.

        Args:
            size: The size of the triangle in pixels.
            parent: Optional parent widget.
        """
        super().__init__(parent)
        self._rotation: float = 0.0
        self._arrow_size = size
        self._color = color

        diagonal = int((size ** 2 + size ** 2) ** 0.5) + 2
        self.setFixedSize(diagonal, diagonal)

    def get_rotation(self) -> float:
        """Return the current rotation angle in degrees."""
        return self._rotation

    def set_rotation(self, angle: float) -> None:
        """
        Set the rotation angle and trigger a repaint.

        Args:
            angle: Rotation in degrees.
        """
        self._rotation = angle
        self.update()

    rotation = Property(float, get_rotation, set_rotation)

    def paintEvent(self, event) -> None: 
        """Draw the triangle rotated by the current angle, centered in the widget."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Translate to the center of the widget so rotation is around the center
        painter.translate(self.width() / 2, self.height() / 2)
        painter.rotate(self._rotation)

        # Draw a right-pointing triangle centered on the origin
        half = self._arrow_size / 2
        # triangle = QPolygonF([
        #     QPointF(-half, -half),
        #     QPointF( half,  0.0 ),
        #     QPointF(-half,  half),
        # ])
        #painter.setPen(QPen(Qt.PenStyle.NoPen))
        #painter.setBrush(self._color)
        #painter.drawPolygon(triangle)

        pen = QPen(self._color)
        pen.setWidth(2)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)

        chevron = QPolygonF([
            QPointF(-half / 2, -half),
            QPointF( half / 2,  0.0),
            QPointF(-half / 2,  half),
        ])
        painter.drawPolyline(chevron)



class CollapsibleWidget(QWidget):
    """
    A widget that can be collapsed and expanded with an animation.
    Shows a title bar with a rotating triangle indicator and a content area.
    """

    ANIMATION_DURATION = 100  # ms

    def __init__(
        self,
        title: str = "Section",
        parent: Optional[QWidget] = None,
        start_collapsed: bool = False,
    ) -> None:
        """
        Initialize the collapsible widget.

        Args:
            title: The title displayed in the header bar.
            parent: Optional parent widget.
            start_collapsed: Whether the widget starts in collapsed state.
        """
        super().__init__(parent)

        self._is_collapsed: bool = start_collapsed
        self._setup_ui(title)
        self._setup_animations()

        if start_collapsed:
            self._content_wrapper.setMaximumHeight(0)
            self._arrow.set_rotation(0.0)
        else:
            self._content_wrapper.setMaximumHeight(0)
            self._arrow.set_rotation(90.0)
            QTimer.singleShot(0, self._expand_immediately)

    def _expand_immediately(self) -> None:
        """Expand to full height without animation (used on startup)."""
        self._content_wrapper.setMaximumHeight(16_777_215)

    def _setup_ui(self, title: str) -> None:
        """Build and configure the UI components."""
        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(0, 0, 0, 0)
        outer_layout.setSpacing(0)

        # --- Header bar ---
        self._header = QFrame(self)
        self._header.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self._header.mousePressEvent = lambda _: self._toggle_collapse()

        header_layout = QHBoxLayout(self._header)
        header_layout.setContentsMargins(4, 4, 4, 4)
        header_layout.setSpacing(8)

        self._arrow = ArrowWidget(size=11, parent=self._header)

        self._title_label = QLabel(title)
        title_font = QFont()
        title_font.setBold(True)
        self._title_label.setFont(title_font)

        header_layout.addWidget(self._arrow)
        header_layout.addWidget(self._title_label)
        header_layout.addStretch()

        # --- Content group box ---
        self._group_box = QGroupBox(self)
        self._content_layout = QVBoxLayout(self._group_box)
        self._content_layout.setContentsMargins(8, 8, 8, 8)
        self._content_layout.setSpacing(6)

        # Wrapper widget whose maximumHeight we animate
        self._content_wrapper = QWidget(self)
        wrapper_layout = QVBoxLayout(self._content_wrapper)
        wrapper_layout.setContentsMargins(0, 0, 0, 0)
        wrapper_layout.setSpacing(0)
        wrapper_layout.addWidget(self._group_box)

        outer_layout.addWidget(self._header)
        outer_layout.addWidget(self._content_wrapper)

    def _setup_animations(self) -> None:
        """Configure the height and arrow rotation animations."""
        self._height_animation = QPropertyAnimation(self._content_wrapper, b"maximumHeight")
        self._height_animation.setEasingCurve(QEasingCurve.Type.InOutCubic)
        self._height_animation.setDuration(self.ANIMATION_DURATION)

        self._arrow_animation = QPropertyAnimation(self._arrow, b"rotation")
        self._arrow_animation.setEasingCurve(QEasingCurve.Type.InOutCubic)
        self._arrow_animation.setDuration(self.ANIMATION_DURATION)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def content_layout(self) -> QVBoxLayout:
        """
        Return the layout where child widgets should be added.

        Returns:
            The QVBoxLayout inside the collapsible content area.
        """
        return self._content_layout

    def add_widget(self, widget: QWidget) -> None:
        """
        Add a widget to the collapsible content area.

        Args:
            widget: The widget to add.
        """
        self._content_layout.addWidget(widget)

    def set_title(self, title: str) -> None:
        """
        Update the header title.

        Args:
            title: New title string.
        """
        self._title_label.setText(title)

    def is_collapsed(self) -> bool:
        """
        Return whether the widget is currently collapsed.

        Returns:
            True if collapsed, False if expanded.
        """
        return self._is_collapsed

    def collapse(self) -> None:
        """Collapse the content area if it is currently expanded."""
        if not self._is_collapsed:
            self._toggle_collapse()

    def expand(self) -> None:
        """Expand the content area if it is currently collapsed."""
        if self._is_collapsed:
            self._toggle_collapse()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _get_content_height(self) -> int:
        """
        Calculate the natural height of the content wrapper.

        Returns:
            The height in pixels.
        """
        self._content_wrapper.setMaximumHeight(16_777_215)
        height = self._content_wrapper.sizeHint().height()
        return height

    def _toggle_collapse(self) -> None:
        """Toggle between collapsed and expanded states with animation."""
        self._is_collapsed = not self._is_collapsed

        # --- Arrow rotation ---
        current_rotation = self._arrow.get_rotation()
        target_rotation = 0.0 if self._is_collapsed else 90.0

        self._arrow_animation.stop()
        self._arrow_animation.setStartValue(current_rotation)
        self._arrow_animation.setEndValue(target_rotation)
        self._arrow_animation.start()

        # --- Height ---
        if self._is_collapsed:
            current_height = self._content_wrapper.height()
            self._height_animation.setStartValue(current_height)
            self._height_animation.setEndValue(0)
        else:
            content_height = self._get_content_height()
            self._height_animation.setStartValue(0)
            self._height_animation.setEndValue(content_height)

        self._height_animation.stop()
        self._height_animation.start()


# ──────────────────────────────────────────────────────────────────────────────
# Demo
# ──────────────────────────────────────────────────────────────────────────────

def _build_demo() -> None:
    """Build and show a demo window with a fixed size and scrollable content."""
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    window = QWidget()
    window.setWindowTitle("Collapsible Widget Demo")
    window.setMinimumSize(300, 200)
    window.resize(440, 300)

    window_layout = QVBoxLayout(window)
    window_layout.setContentsMargins(0, 0, 0, 0)

    # Scroll area fills the fixed window
    scroll = QScrollArea()
    scroll.setWidgetResizable(True)
    scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

    # Container inside the scroll area
    container = QWidget()
    container.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
    root_layout = QVBoxLayout(container)
    root_layout.setContentsMargins(16, 16, 16, 16)
    root_layout.setSpacing(10)

    # --- Section 1: starts expanded ---
    section1 = CollapsibleWidget("Personal Information", start_collapsed=False)
    for text in ("Name: Jane Doe", "Age: 30", "Location: Berlin"):
        section1.add_widget(QLabel(text))

    # --- Section 2: starts collapsed ---
    section2 = CollapsibleWidget("Network Settings", start_collapsed=True)
    for text in ("IP: 192.168.1.42", "Gateway: 192.168.1.1", "DNS: 8.8.8.8", "MTU: 1500"):
        section2.add_widget(QLabel(text))

    # --- Section 3: starts expanded ---
    section3 = CollapsibleWidget("Actions", start_collapsed=False)
    for label in ("Save", "Load", "Reset", "Export"):
        section3.add_widget(QPushButton(label))

    root_layout.addWidget(section1)
    root_layout.addWidget(section2)
    root_layout.addWidget(section3)
    root_layout.addStretch()

    scroll.setWidget(container)
    window_layout.addWidget(scroll)

    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    _build_demo()
