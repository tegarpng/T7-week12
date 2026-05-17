from PySide6.QtWidgets import QWidget, QVBoxLayout
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


class SalesChartWidget(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout(self)
        self.figure = Figure(figsize=(8, 4), tight_layout=True)
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)

    def plot(self, summary, chart_type, title):
        self.figure.clear()
        ax = self.figure.add_subplot(111)

        nama_bulan = {
            1: "Jan", 2: "Feb", 3: "Mar"
        }
        months = summary["bulan"].map(nama_bulan).tolist()
        totals = summary["Sales"].tolist()

        if chart_type == "Bar Chart":
            ax.bar(months, totals, color="#2c7be5")
        elif chart_type == "Line Chart":
            ax.plot(months, totals, marker="o", linewidth=2, color="#00a676")
        elif chart_type == "Pie Chart":
            ax.pie(totals, labels=months, autopct="%1.1f%%", startangle=90)
            ax.axis("equal")

        ax.set_title(title)

        if chart_type != "Pie Chart":
            ax.set_xlabel("Bulan")
            ax.set_ylabel("Total Penjualan")
            ax.grid(True, alpha=0.25)

        self.canvas.draw()