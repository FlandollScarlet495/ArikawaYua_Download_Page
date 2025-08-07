# gui.py
# GUIを提供するモジュール

import sys
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QFileDialog, QLabel,
    QLineEdit, QTextEdit, QHBoxLayout, QTabWidget
)
from PyQt6.QtCore import QThread, pyqtSignal
from PyQt6.QtGui import QIcon
from compressor import compress_and_encrypt_parallel
from decompressor import decrypt_and_decompress_parallel
import traceback

class WorkerThread(QThread):
    log_signal = pyqtSignal(str)
    finished_signal = pyqtSignal(str)

    def __init__(self, mode, in_path, out_path, password):
        super().__init__()
        self.mode = mode
        self.in_path = in_path
        self.out_path = out_path
        self.password = password

    def run(self):
        try:
            self.log_signal.emit(f"{self.mode}処理を開始します...")
            if self.mode == "compress":
                compress_and_encrypt_parallel(self.in_path, self.out_path, 3, self.log_signal.emit)
            elif self.mode == "decompress":
                decrypt_and_decompress_parallel(self.in_path, self.out_path, self.log_signal.emit)
            self.finished_signal.emit(f"{self.mode}処理が完了しました。")
        except Exception as e:
            self.finished_signal.emit(f"エラー: {type(e).__name__}: {str(e)}\n{traceback.format_exc()}")

class AYDTCompressorGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("arikawa_yua_drift_turbo 💨")
        self.setMinimumWidth(550)

        self.tabs = QTabWidget()
        self.compress_tab = QWidget()
        self.decompress_tab = QWidget()
        self.tabs.addTab(self.compress_tab, "🚀 圧縮")
        self.tabs.addTab(self.decompress_tab, "📦 解凍")

        self.create_compress_tab()
        self.create_decompress_tab()

        main_layout = QVBoxLayout()
        main_layout.addWidget(self.tabs)
        self.setLayout(main_layout)

        self.worker = None

        # アイコン設定(iconは適宜変更してください(icon.icoを用意))
        self.setWindowIcon(QIcon("assets/icon.ico"))

    def create_compress_tab(self):
        layout = QVBoxLayout()

        self.in_label_c = QLabel("📁 入力ファイル / フォルダ:")
        self.in_path_c = QLineEdit()
        self.in_browse_btn_c = QPushButton("選択")
        self.in_browse_btn_c.clicked.connect(lambda: self.select_input(self.in_path_c))

        input_layout = QHBoxLayout()
        input_layout.addWidget(self.in_path_c)
        input_layout.addWidget(self.in_browse_btn_c)

        self.out_label_c = QLabel("📂 出力ファイル (.aydt):")
        self.out_path_c = QLineEdit()
        self.out_browse_btn_c = QPushButton("選択")
        self.out_browse_btn_c.clicked.connect(lambda: self.select_output(self.out_path_c))

        output_layout = QHBoxLayout()
        output_layout.addWidget(self.out_path_c)
        output_layout.addWidget(self.out_browse_btn_c)

        self.compress_btn = QPushButton("🚀 圧縮開始")
        self.compress_btn.clicked.connect(self.compress)

        self.log_c = QTextEdit()
        self.log_c.setReadOnly(True)

        layout.addWidget(self.in_label_c)
        layout.addLayout(input_layout)
        layout.addWidget(self.out_label_c)
        layout.addLayout(output_layout)
        layout.addWidget(self.compress_btn)
        layout.addWidget(self.log_c)

        self.compress_tab.setLayout(layout)

    def create_decompress_tab(self):
        layout = QVBoxLayout()

        self.in_label_d = QLabel("📁 入力ファイル (.aydt):")
        self.in_path_d = QLineEdit()
        self.in_browse_btn_d = QPushButton("選択")
        self.in_browse_btn_d.clicked.connect(lambda: self.select_input(self.in_path_d))

        input_layout = QHBoxLayout()
        input_layout.addWidget(self.in_path_d)
        input_layout.addWidget(self.in_browse_btn_d)

        self.out_label_d = QLabel("📂 出力先ファイル:")
        self.out_path_d = QLineEdit()
        self.out_browse_btn_d = QPushButton("選択")
        self.out_browse_btn_d.clicked.connect(lambda: self.select_output_directory(self.out_path_d))

        output_layout = QHBoxLayout()
        output_layout.addWidget(self.out_path_d)
        output_layout.addWidget(self.out_browse_btn_d)

        self.decompress_btn = QPushButton("📦 解凍開始")
        self.decompress_btn.clicked.connect(self.decompress)

        self.log_d = QTextEdit()
        self.log_d.setReadOnly(True)

        layout.addWidget(self.in_label_d)
        layout.addLayout(input_layout)
        layout.addWidget(self.out_label_d)
        layout.addLayout(output_layout)
        layout.addWidget(self.decompress_btn)
        layout.addWidget(self.log_d)

        self.decompress_tab.setLayout(layout)

    def select_input(self, target_lineedit):
        path, _ = QFileDialog.getOpenFileName(self, "入力ファイルを選択")
        if path:
            target_lineedit.setText(path)

    def select_output(self, target_lineedit):
        path, _ = QFileDialog.getSaveFileName(self, "出力ファイルを選択", filter="AYDTファイル (*.aydt)")
        if path:
            target_lineedit.setText(path)

    def select_output_directory(self, target_lineedit):
        path = QFileDialog.getExistingDirectory(self, "出力フォルダを選択")
        if path:
            target_lineedit.setText(path)

    def log_message_compress(self, message):
        self.log_c.append(message)

    def log_message_decompress(self, message):
        self.log_d.append(message)

    def on_finished_compress(self, message):
        self.log_c.append(message)
        self.compress_btn.setEnabled(True)

    def on_finished_decompress(self, message):
        self.log_d.append(message)
        self.decompress_btn.setEnabled(True)

    def compress(self):
        in_path = self.in_path_c.text()
        out_path = self.out_path_c.text()
        password = ""  # パスワード対応は後ほど！

        if not (in_path and out_path):
            self.log_c.append("❗ 入力・出力パスを指定してください。")
            return

        self.compress_btn.setEnabled(False)
        self.worker = WorkerThread("compress", in_path, out_path, password)
        self.worker.log_signal.connect(self.log_message_compress)
        self.worker.finished_signal.connect(self.on_finished_compress)
        self.worker.start()

    def decompress(self):
        in_path = self.in_path_d.text()
        out_path = self.out_path_d.text()
        password = ""  # パスワード対応は後で！

        if not (in_path and out_path):
            self.log_d.append("❗ 入力・出力パスを指定してください。")
            return

        self.decompress_btn.setEnabled(False)
        self.worker = WorkerThread("decompress", in_path, out_path, password)
        self.worker.log_signal.connect(self.log_message_decompress)
        self.worker.finished_signal.connect(self.on_finished_decompress)
        self.worker.start()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    gui = AYDTCompressorGUI()
    gui.show()
    sys.exit(app.exec())
