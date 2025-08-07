# decompressor.py
# 並列解凍モジュール（暗号化なし）

import os
from concurrent.futures import ProcessPoolExecutor, as_completed
import zstandard as zstd

def decompress_chunk_with_path(chunk: bytes) -> tuple[str, bytes]:
    # チャンクの先頭4バイトがパス長、その後がパス（UTF-8）、残りが圧縮データ
    path_len = int.from_bytes(chunk[:4], 'big')
    path_bytes = chunk[4:4+path_len]
    relative_path = path_bytes.decode('utf-8')
    compressed_data = chunk[4+path_len:]
    dctx = zstd.ZstdDecompressor()
    decompressed_data = dctx.decompress(compressed_data)
    return relative_path, decompressed_data

def decrypt_and_decompress_parallel(input_path, output_folder, log_func=None):
    # 出力フォルダ作成（存在しなければ）
    os.makedirs(output_folder, exist_ok=True)

    chunks = []
    with open(input_path, 'rb') as f_in:
        while True:
            size_bytes = f_in.read(8)
            if not size_bytes:
                break
            chunk_size = int.from_bytes(size_bytes, 'big')
            compressed_chunk = f_in.read(chunk_size)
            if len(compressed_chunk) != chunk_size:
                raise RuntimeError("チャンクサイズが一致しません。ファイル破損の可能性があります。")
            chunks.append(compressed_chunk)

    if log_func:
        log_func(f"読み込んだチャンク数: {len(chunks)}")

    results = [None] * len(chunks)

    with ProcessPoolExecutor() as executor:
        futures = {}
        for i, chunk in enumerate(chunks):
            if log_func:
                log_func(f"チャンク{i+1}/{len(chunks)}を解凍キューに登録")
            futures[executor.submit(decompress_chunk_with_path, chunk)] = i

        for future in as_completed(futures):
            i = futures[future]
            try:
                res = future.result()
                if res is None:
                    raise RuntimeError(f"チャンク{i+1}の解凍結果がNoneです。")
                if not (isinstance(res, tuple) and len(res) == 2):
                    raise RuntimeError(f"チャンク{i+1}の解凍結果の形式がおかしいです: {res}")
                relative_path, decompressed_chunk = res
                results[i] = (relative_path, decompressed_chunk)
                if log_func:
                    log_func(f"チャンク{i+1}/{len(chunks)}の解凍完了: {relative_path} ({len(decompressed_chunk)} bytes)")
            except Exception as e:
                if log_func:
                    log_func(f"チャンク{i+1}でエラー: {e}")
                raise

    # 処理結果のチェック＋ファイル書き込みをまとめて行う例
    for i, item in enumerate(results):
        if item is None:
            raise RuntimeError(f"チャンク{i+1}の処理結果がありません。解凍失敗しています。")
        if not (isinstance(item, tuple) and len(item) == 2):
            raise RuntimeError(f"チャンク{i+1}の処理結果の形式がおかしいです: {item}")

        relative_path, chunk = item  # type: ignore
        print(f"results[{i}]: {relative_path} ({len(chunk)} bytes)")

        output_file_path = os.path.join(output_folder, relative_path)
        os.makedirs(os.path.dirname(output_file_path), exist_ok=True)
        with open(output_file_path, 'wb') as f_out:
            f_out.write(chunk)

    if log_func:
        log_func(f"解凍完了: {output_folder}")
