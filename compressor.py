# compressor.py
# 並列圧縮モジュール（暗号化なし）

import os
import math
from concurrent.futures import ProcessPoolExecutor, as_completed
import zstandard as zstd

CHUNK_SIZE = 10 * 1024 * 1024  # 例: 10MB

def compress_chunk(chunk_data, compression_level=3):
    cctx = zstd.ZstdCompressor(level=compression_level)
    return cctx.compress(chunk_data)

def compress_chunk_with_path(chunk, compression_level, relative_path):
    cctx = zstd.ZstdCompressor(level=compression_level)
    compressed_data = cctx.compress(chunk)
    path_bytes = relative_path.encode('utf-8')
    path_len_bytes = len(path_bytes).to_bytes(4, 'big')
    return path_len_bytes + path_bytes + compressed_data

def compress_and_encrypt_parallel(input_path, output_path, compression_level=3, log_func=None):
    if compression_level == "" or compression_level is None:
        compression_level = 3
    try:
        compression_level = int(compression_level)
    except Exception as e:
        raise ValueError(f"圧縮レベルは整数でなければなりません（受け取った値: {compression_level}）: {e}")

    file_size = os.path.getsize(input_path)
    chunks_count = math.ceil(file_size / CHUNK_SIZE)

    if log_func:
        log_func(f"ファイルサイズ: {file_size} バイト, チャンク数: {chunks_count}")

    results = [None] * chunks_count

    base_dir = os.path.dirname(input_path)
    base_name = os.path.basename(input_path)
    name_without_ext = os.path.splitext(base_name)[0]

    original_filename = os.path.basename(input_path)
    name_without_ext, ext = os.path.splitext(original_filename)  # 拡張子を分離

    with open(input_path, 'rb') as f_in, ProcessPoolExecutor() as executor:
        futures = {}
        for i in range(chunks_count):
            chunk = f_in.read(CHUNK_SIZE)
            if not chunk:
                break
            relative_path = f"{name_without_ext}{ext}"  # ここで拡張子つける
            if log_func:
                log_func(f"チャンク{i+1}/{chunks_count}を圧縮キューに登録")
            futures[executor.submit(compress_chunk_with_path, chunk, compression_level, relative_path)] = i

        for future in as_completed(futures):
            i = futures[future]
            try:
                compressed_chunk = future.result()
                results[i] = compressed_chunk
                if log_func:
                    log_func(f"チャンク{i+1}/{chunks_count}の圧縮完了")
            except Exception as e:
                if log_func:
                    log_func(f"チャンク{i+1}でエラー: {e}")
                raise

    with open(output_path, 'wb') as f_out:
        for i, chunk in enumerate(results):
            if chunk is None:
                raise RuntimeError(f"チャンク{i}の処理結果がありません。圧縮処理に失敗しています。")
            chunk_size_bytes = len(chunk).to_bytes(8, 'big')
            f_out.write(chunk_size_bytes)
            f_out.write(chunk)

    if log_func:
        log_func(f"圧縮完了: {output_path}")
