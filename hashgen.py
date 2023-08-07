import hashlib
import subprocess


def generate_hash_from_url(url, hash_algorithm='sha256'):
    try:
        # Fetch the content using curl
        curl_process = subprocess.Popen(["curl", "-s", url], stdout=subprocess.PIPE)
        content, _ = curl_process.communicate()
        if curl_process.returncode != 0:
            print("Error: Unable to fetch the content from the URL.")
            return

        # Calculate the hash using the specified algorithm
        hasher = hashlib.new(hash_algorithm)
        hasher.update(content)
        file_hash = hasher.hexdigest()
        print(f"URL {hash_algorithm.upper()} hash: {file_hash}")
        return str(file_hash)
    except Exception as e:
        print(f"Error: {e}")


def generate_hashes_from_local_file(file_path):
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as file:
        for chunk in iter(lambda: file.read(4096), b""):
            sha256_hash.update(chunk)
    file_hash = sha256_hash.hexdigest()
    print(f"File SHA256 hash: {file_hash}")
    return sha256_hash.hexdigest()


def generate_hash(url, file_path):
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as file:
        for chunk in iter(lambda: file.read(4096), b""):
            sha256_hash.update(chunk)
    file_hash = sha256_hash.hexdigest()
    try:
        # Fetch the content using curl
        curl_process = subprocess.Popen(["curl", "-s", url], stdout=subprocess.PIPE)
        content, _ = curl_process.communicate()

        if curl_process.returncode != 0:
            print("Error: Unable to fetch the content from the URL.")
            return

        # Calculate the hash using the specified algorithm
        hasher = hashlib.new('sha256')
        hasher.update(content)
        file_hash = hasher.hexdigest()

    except Exception as e:
        print(f"Error: {e}")

    print(f"File SHA256 hash: {file_hash}")
    print(f"URL SHA256 hash: {file_hash}")


if __name__ == "__main__":
    file_path = input("File path: ")
    url = input("URL: ")
    generate_hash(url, file_path)
