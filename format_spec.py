import struct

HEADER_MAGIC = b"AYDT"
HEADER_VERSION = 1

def pack_header(num_chunks):
    """
    ヘッダをバイナリに変換
    フォーマット例：
    4 bytes マジック ("AYDT")
    1 byte バージョン (1)
    4 bytes チャンク数 (unsigned int)
    """
    return HEADER_MAGIC + struct.pack(">B I", HEADER_VERSION, num_chunks)

def unpack_header(data):
    """
    バイナリからヘッダ情報を読み出す
    戻り値： (version, num_chunks)
    """
    if len(data) < 9:
        raise ValueError("ヘッダデータが短すぎます")
    magic = data[:4]
    if magic != HEADER_MAGIC:
        raise ValueError("ファイルマジックが違います")
    version = data[4]
    num_chunks = struct.unpack(">I", data[5:9])[0]
    return version, num_chunks

def pack_chunk_metadata(chunk_index, chunk_size):
    """
    チャンクのメタ情報をバイナリに変換
    フォーマット例：
    4 bytes チャンクインデックス (unsigned int)
    4 bytes チャンクサイズ (unsigned int)
    """
    return struct.pack(">I I", chunk_index, chunk_size)

def unpack_chunk_metadata(data):
    """
    バイナリからチャンクメタ情報を読み出す
    戻り値：(chunk_index, chunk_size)
    """
    if len(data) != 8:
        raise ValueError("チャンクメタデータのサイズが不正です")
    return struct.unpack(">I I", data)
