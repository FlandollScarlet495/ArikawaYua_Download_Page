# main.py
# メインエントリーポイント

import sys
import argparse
from compressor import compress_and_encrypt_parallel
from decompressor import decrypt_and_decompress_parallel

def main():
    parser = argparse.ArgumentParser(description="arikawa_yua_drift_turbo 圧縮・解凍ツール")
    parser.add_argument('mode', choices=['compress', 'decompress'], nargs='?', help='動作モード')
    parser.add_argument('input', nargs='?', help='入力ファイルパス')
    parser.add_argument('output', nargs='?', help='出力ファイルパス')
    parser.add_argument('password', nargs='?', help='AESパスワード')

    args = parser.parse_args()

    if args.mode and args.input and args.output and args.password:
        try:
            if args.mode == 'compress':
                compress_and_encrypt_parallel(args.input, args.output, args.password)
                print("圧縮＆暗号化が完了しました。")
            else:
                decrypt_and_decompress_parallel(args.input, args.output, args.password)
                print("復号＆解凍が完了しました。")
        except Exception as e:
            print(f"エラー: {e}")
            sys.exit(1)
    else:
        # 引数不足ならGUIを起動
        from gui import AYDTCompressorGUI
        from PyQt6.QtWidgets import QApplication

        app = QApplication(sys.argv)
        gui = AYDTCompressorGUI()
        gui.show()
        sys.exit(app.exec())

if __name__ == "__main__":
    main()
