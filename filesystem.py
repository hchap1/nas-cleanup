from os import path, listdir

class Directory:
    def __init__(self, path: str):
        self.path = path
        self.files = []

class File:
    def __init__(self, abspath: str, filename: str, extension: str):
        self.path = abspath
        self.filename = filename
        self.extension = extension
        self.absolute = path.join(self.path, self.filename + self.extension)
        self.checksum = Checksum(self)

class Checksum:
    def __init__(self, file: File):
        self.sum = 0
        with open(path.join(file.path, file.filename + file.extension), "rb") as data:
            binary = list(data.read())
        for num in binary:
            self.sum += num
        if len(binary) == 0:
            print(f"Zero-byte file: {file.absolute}")
        self.average = int(self.sum / len(binary))
        self.value = int((self.sum + self.average) / 100)

def recursively_walk_directories(root: Directory, dump):
    for item in listdir(root.path):
        item_path = path.join(root.path, item)
        if path.isdir(item_path): recursively_walk_directories(Directory(item_path), dump)
        elif path.isfile(item_path):
            filename, extension = path.splitext(item)
            root.files.append(File(path.abspath(item_path).strip(item), filename, extension))
    dump.append(root)

def middle_10_percent(data):
    if not data or len(data) <= 10:
        return data

    n = len(data)
    start = max(0, n // 2 - n // 20)
    end = min(n, n // 2 + n // 20)
    middle_slice = data[start:end]
    return middle_slice[:10000]

if __name__ == "__main__":
    roots = []
    while True:
        root = input("Enter Directory [ENTER] to cancel.\n -> ")
        if root == "": break
        if path.isdir(root): roots.append(Directory(root))
        else: print("[ERROR] Invalid directory.")

    directories = []
    checksums = {}

    for root in roots:
        recursively_walk_directories(root, directories)

    duplicates = []

    for directory in directories:
        for file in directory.files:
            if checksums.get(file.checksum.value) != None:
                if len(checksums[file.checksum.value].filename) > len(file.filename):
                    duplicates.append((checksums[file.checksum.value].absolute, file.absolute))
                    checksums[file.checksum.value] = file
                else:
                    duplicates.append((file.absolute, checksums[file.checksum.value].absolute))
            else:
                checksums[file.checksum.value] = file

    for duplicate in duplicates:
        print(f"[DUPLICATE] {duplicate[0].absolute} is a copy of {duplicate[1].absolute}")
