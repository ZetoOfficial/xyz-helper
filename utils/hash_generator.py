import hashlib
import random
import string


class FileHashGenerator:
    @staticmethod
    def generate_session_id(length=20):
        characters = string.ascii_letters + string.digits
        return ''.join(random.choice(characters) for _ in range(length))

    @staticmethod
    def file_md5_hash(filename):
        hash_md5 = hashlib.md5()
        with open(filename, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()

    @staticmethod
    def check_md5_hash(filename, md5_hash):
        return FileHashGenerator.file_md5_hash(filename) == md5_hash
