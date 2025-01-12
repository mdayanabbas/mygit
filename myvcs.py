import os,hashlib
import collections,struct
print("Hello")
def init(repo):
    os.mkdir(repo)
    os.mkdir(os.path.join(repo,'.git'))
    for name in ['objects','refs','refs/heads']:
        os.mkdir(os.path.join(repo, '.git',name))

    # write_file(os.path.join(repo,'.git','HEAD'),
    # b'ref: refs/heads/master')

    print('initialized empty repository: {}'.format(repo))

def hash_object(data,obj_type,write = True):
    header = '{} {}'.format(obj_type,len(data)).encode()
    full_data = header + b'\x00' + data
    sha1 = hashlib.sha256(full_data).hexdigest()
    if write:
        path = os.path.join('.git','objects',sha1[:2],sha1[2:])
        if not os.path.exists(path):
            os.makedirs(os.path.dirname(path),exist_ok = True)
            # write_file(path,zlib.compress(full_data))
    return sha1

# # init("Abbas")
# file_content = "My name is Abbas Bhai"
# temp = hash_object(file_content.encode(), 'blob', write=False)
# print(temp)

IndexEntry = collections.namedtuple('IndexEntry', [
    'ctime_s', 'ctime_n', 'mtime_s', 'mtime_n', 'dev', 'ino', 'mode', 'uid',
    'gid', 'size', 'sha1', 'flags', 'path',
])

def read_file(path):
    """Read contents of file at given path as bytes."""
    with open(path, 'rb') as f:
        return f.read()


def write_file(path, data):
    """Write data bytes to file at given path."""
    with open(path, 'wb') as f:
        f.write(data)

def read_index():
    try:
        data = read_file(os.path.join('.git','index'))
    except FileNotFoundError:
        return []
    digest = hashlib.sha1(data[:-20]).digest()
    assert digest == data[-20:], 'invalid index checksum'
    signature,version,num_entries = struct.unpack('!4sLL',data[:12])
    assert signature == b'DIRC',\
            'invalid index signature {}'.format(signature)

    assert version == 2, 'unknown index version {}'.format(version)
    entry_data = data[12:-20]
    entries = []
    i = 0
    while i + 62 < len(entry_data):
        fields_end = i + 62
        fields = struct.unpack('!LLLLLLLLLL20sH',
                                entry_data[i:fields_end])
        path_end = entry_data.index(b'\x00', fields_end)
        path = entry_data[fields_end:path_end]
        entry = IndexEntry(*(fields + (path.decode(),)))
        entries.append(entry)
        entry_len = ((62 + len(path) + 8) // 8) * 8
        i += entry_len

    assert len(entries) == num_entries
    return entries


print(read_index())
