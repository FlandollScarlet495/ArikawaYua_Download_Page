import os

def read_file_in_chunks(file_path, chunk_size=1024*1024):
    """指定したサイズでファイルをチャンク読み込みするジェネレータ"""
    with open(file_path, 'rb') as f:
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            yield chunk

def write_chunks_to_file(file_path, chunks):
    """チャンクのイテレータやリストを書き込み"""
    with open(file_path, 'wb') as f:
        for chunk in chunks:
            f.write(chunk)

def split_file(file_path, chunk_size=1024*1024):
    """ファイルをchunk_sizeごとに分割してバイト列のリストを返す"""
    chunks = []
    with open(file_path, 'rb') as f:
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            chunks.append(chunk)
    return chunks

def ensure_dir_exists(path):
    """ディレクトリがなければ作成"""
    dir_path = os.path.dirname(path)
    if dir_path and not os.path.exists(dir_path):
        os.makedirs(dir_path)
