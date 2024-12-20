from os import path, listdir, stat

include = set()
slicesize = 10000

default_conf = [
    "[INCLUDE] png jpeg jpg mov mp4 heic",
    "[SLICESIZE] 10000"
]
try:
    with open("config.txt", "r") as config: conf_lines = config.readlines()
except:
    conf_lines = default_conf

for line in conf_lines:
    if line[0:9] == "[INCLUDE]":
        for item in line.strip("\n").split(" ")[1:]:
            include.add("." + item)
    if line[0:11] == "[SLICESIZE]":
        slicesize = int(line.strip("\n").split(" ")[1])

class DebugTracker:
    def __init__(self):
        self.files = 0
        self.directories = 0
        self.totalbytes = 0
        self.mostrecent = "-"

    def log(self):
        print(f"\r[INFORMATION] {self.files} files scanned totalling {round(self.totalbytes / (1024 * 1024), 2) * 8}MB over {self.directories} directories. Current: {self.mostrecent}", end="")

class Directory:
    def __init__(self, path: str):
        self.path = path
        self.files = []

class File:
    def __init__(self, abspath: str, filename: str, extension: str, size):
        self.ignore = False
        self.path = abspath
        self.filename = filename
        self.extension = extension
        self.size = size
        self.absolute = path.join(self.path, self.filename + self.extension)
        self.checksum = Checksum(self)

class Checksum:
    def __init__(self, file: File):
        self.sum = 0
        with open(path.join(file.path, file.filename + file.extension), "rb") as data:
            if file.size > 100:
                data.seek(int(file.size / 2 - file.size / 20))
            binary = data.read(min(int(file.size / 10), slicesize))
        for num in binary:
            self.sum += num
        if len(binary) == 0:
            file.ignore = True
            return
        self.average = int(self.sum / len(binary))
        self.value = int((self.sum + self.average))

def recursively_walk_directories(root: Directory, dump, debug):
    debug.directories += 1
    for item in listdir(root.path):
        item_path = path.join(root.path, item)
        if path.isdir(item_path): recursively_walk_directories(Directory(item_path), dump, debug)
        elif path.isfile(item_path):
            size = stat(item_path).st_size
            if size < 1: continue
            filename, extension = path.splitext(item)
            if extension.lower() in include:
                debug.files += 1
                debug.totalbytes += size
                root.files.append(File(path.abspath(item_path).strip(item), filename, extension, size))
                debug.mostrecent = item_path
                debug.log()
    dump.append(root)

def middle_10_percent(data):
    if not data or len(data) <= 10:
        return data

    n = len(data)
    start = max(0, n // 2 - n // 20)
    if n / 2 - start > slicesize / 2: start = int(n / 2 - slicesize / 2)
    end = min(n, n // 2 + n // 20)
    if end - n / 2 > slicesize / 2: end = int(n / 2 + slicesize / 2)
    return data[start:end]

if __name__ == "__main__":
    roots = []
    while True:
        root = input("Enter Directory [ENTER] to cancel -> ")
        if root == "\n" or root == "": break
        if path.isdir(root): roots.append(Directory(root))
        else: print("[ERROR] Invalid directory.")

    directories = []
    checksums = {}
    debug = DebugTracker()

    print("[CHECKPOINT] Starting discovery of files.")

    for root in roots:
        recursively_walk_directories(root, directories, debug)

    print("\n[CHECKPOINT] Finished discovery of files.")

    duplicates = []

    for directory in directories:
        for file in directory.files:
            if checksums.get(file.checksum.value) != None:
                if len(checksums[file.checksum.value].filename) > len(file.filename):
                    duplicates.append((checksums[file.checksum.value].absolute, file.absolute))
                    checksums[file.checksum.value] = file
                else: duplicates.append((file.absolute, checksums[file.checksum.value].absolute))
            else: checksums[file.checksum.value] = file

    for duplicate in duplicates:
        print(f"[DUPLICATE] {duplicate[0]} is a copy of {duplicate[1]}")
