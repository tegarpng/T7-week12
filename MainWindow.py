from pathlib import Path
import sys

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QComboBox, QPushButton,
    QFileDialog, QTableWidget, QTableWidgetItem, QHBoxLayout, QVBoxLayout, QMessageBox
)

from Data.loader import load_sales_data, get_city, get_cust_type, get_product, filter_by_city, filter_by_cust, filter_by_product, get_monthly_summary
from Data.chart_widget import SalesChartWidget

class Dashboard(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Dashboard Penjualan")
        self.resize(1000, 650)

        csv_path = Path(__file__).parent / "Data" / "SuperMarketAnalysis.csv"
        self.df = load_sales_data(csv_path)

        self.setup_ui()
        self.update_dashboard()

    def setup_ui(self):
        central = QWidget()
        main_layout = QHBoxLayout(central)
        self.setCentralWidget(central)

        # --- Kolom Kiri ---
        table_raw = QVBoxLayout()

        self.summary_label = QLabel("Summary akan muncul di sini")
        table_raw.addWidget(self.summary_label)

        self.city = QVBoxLayout()
        self.city_label = QLabel("City")
        self.filter_city = QComboBox()
        self.filter_city.addItems(get_city(self.df))
        self.city.addWidget(self.city_label)
        self.city.addWidget(self.filter_city)

        self.cust = QVBoxLayout()
        self.label_cust = QLabel("Customer Type")
        self.filter_cust_type = QComboBox()
        self.filter_cust_type.addItems(get_cust_type(self.df))
        self.cust.addWidget(self.label_cust)
        self.cust.addWidget(self.filter_cust_type)

        self.product = QVBoxLayout()
        self.product_label = QLabel("Product Line")
        self.filter_product = QComboBox()
        self.filter_product.addItems(get_product(self.df))
        self.product.addWidget(self.product_label)
        self.product.addWidget(self.filter_product)
        
        self.chart = QVBoxLayout()
        self.chart_label = QLabel("Chart Type")
        self.filter_chart = QComboBox()
        self.filter_chart.addItems(["Bar Chart", "Line Chart", "Pie Chart"])
        self.chart.addWidget(self.chart_label)
        self.chart.addWidget(self.filter_chart)

        filter_loc = QHBoxLayout()
        filter_loc.addLayout(self.city)
        filter_loc.addLayout(self.cust)
        filter_loc.addLayout(self.product)
        filter_loc.addLayout(self.chart)
        table_raw.addLayout(filter_loc)

        self.table = QTableWidget()
        table_raw.addWidget(self.table)

        plot_data = QVBoxLayout()

        btn_layout = QHBoxLayout()
        self.refresh_btn = QPushButton("Refresh")
        self.export_btn = QPushButton("Export Chart")
        btn_layout.addWidget(self.refresh_btn)
        btn_layout.addWidget(self.export_btn)

        self.chart_widget = SalesChartWidget()
        plot_data.addLayout(btn_layout)
        plot_data.addWidget(self.chart_widget)

        main_layout.addLayout(table_raw)
        main_layout.addLayout(plot_data)

        # Hubungkan filter ke update_dashboard
        self.filter_city.currentTextChanged.connect(self.update_dashboard)
        self.filter_cust_type.currentTextChanged.connect(self.update_dashboard)
        self.filter_product.currentTextChanged.connect(self.update_dashboard)
        self.filter_chart.currentTextChanged.connect(self.update_dashboard)
        self.refresh_btn.clicked.connect(self.refresh_data)
        self.export_btn.clicked.connect(self.export_file)

    def update_dashboard(self):
        filtered_df = filter_by_city(self.df, self.filter_city.currentText())
        filtered_df = filter_by_cust(filtered_df, self.filter_cust_type.currentText())
        filtered_df = filter_by_product(filtered_df, self.filter_product.currentText())

        self.update_summary(filtered_df)
        self.update_table(filtered_df)
        self.update_chart(filtered_df)

    def refresh_data(self):
        csv_path = Path(__file__).parent / "Data" / "SuperMarketAnalysis.csv"
        self.df = load_sales_data(csv_path)

        self.filter_city.blockSignals(True)
        self.filter_cust_type.blockSignals(True)
        self.filter_product.blockSignals(True)
        self.filter_chart.blockSignals(True)

        self.filter_city.setCurrentIndex(0)
        self.filter_cust_type.setCurrentIndex(0)
        self.filter_product.setCurrentIndex(0)
        self.filter_chart.setCurrentIndex(0)

        self.filter_city.blockSignals(False)
        self.filter_cust_type.blockSignals(False)
        self.filter_product.blockSignals(False)
        self.filter_chart.blockSignals(False)

        self.update_dashboard()
    
    def update_chart(self, df):
        chart_type = self.filter_chart.currentText()
        summary = get_monthly_summary(df)
        city = self.filter_city.currentText()
        product = self.filter_product.currentText()
        cust = self.filter_cust_type.currentText()
        title = f"Penjualan per Bulan | Kota: {city} | Produk: {product} | Customer Type: {cust}"
        self.chart_widget.plot(summary, chart_type, title)

    def update_summary(self, df):
        total_sales = df["Sales"].sum()
        total_rows = len(df)
        self.summary_label.setText(
            f"Sales penjualan: K {total_sales:,.0f} | Jumlah data: {total_rows} baris"
        )

    def update_table(self, df):
        columns = list(df.columns)
        self.table.setRowCount(len(df))
        self.table.setColumnCount(len(columns))
        self.table.setHorizontalHeaderLabels(columns)

        for row_index, row in df.reset_index(drop=True).iterrows():
            for col_index, column in enumerate(columns):
                value = row[column]
                if column == "Sales":
                    value = f"K {value:,.0f}"
                self.table.setItem(row_index, col_index, QTableWidgetItem(str(value)))

        self.table.resizeColumnsToContents()

    def export_file(self):
        file_path, _ = QFileDialog.getSaveFileName(
			self,
			"Export Chart",
			"",
			"PNG Files (*.png);;JPG Files (*.jpg);;JPEG Files (*.jpeg);;All Files (*)"
		)
        
        if not file_path:
            return
        
        try:
            self.chart_widget.figure.savefig(file_path, dpi=150, bbox_inches="tight")

            QMessageBox.information(
                self, "Sukses",
                f"Chart berhasil di-export!\n\nFile: {file_path}"
            )

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Gagal export:\n{e}")
            
if __name__ == "__main__":
    app = QApplication(sys.argv)

    qss_path = Path(__file__).parent / "style.qss"
    with open(qss_path, "r") as f:
        app.setStyleSheet(f.read())

    window = Dashboard()
    window.show()
    sys.exit(app.exec())