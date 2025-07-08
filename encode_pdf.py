import base64
import zstandard as zstd

def compress_and_encode(file_path):
    with open(file_path, "rb") as f:
        data = f.read()
    compressed = zstd.ZstdCompressor(level=22).compress(data)
    encoded = base64.b85encode(compressed).decode("utf-8")
    return encoded

# 사용 예시:
if __name__ == "__main__":
    encoded_str = compress_and_encode("TimeExplorer-Instruction.pdf")
    with open("encoded.txt", "w") as f:
        f.write(encoded_str)
