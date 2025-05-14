#!/usr/bin/env python3
import os
import sys
import hashlib
import zlib
import time

GIT_DIR = '.git'

def init():
    os.makedirs(os.path.join(GIT_DIR, 'objects'), exist_ok=True)
    os.makedirs(os.path.join(GIT_DIR, 'refs', 'heads'), exist_ok=True)
    with open(os.path.join(GIT_DIR, 'HEAD'), 'w') as f:
        f.write('ref: refs/heads/master\n')
    print('Initialized empty Git repository in {}'.format(os.path.abspath(GIT_DIR)))

def hash_object(data, obj_type='blob', write=True):
    header = '{} {}'.format(obj_type, len(data)).encode()
    full_data = header + b'\x00' + data
    sha1 = hashlib.sha1(full_data).hexdigest()
    if write:
        path = os.path.join(GIT_DIR, 'objects', sha1[:2], sha1[2:])
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'wb') as f:
            f.write(zlib.compress(full_data))
    return sha1

def cat_file(sha1):
    path = os.path.join(GIT_DIR, 'objects', sha1[:2], sha1[2:])
    with open(path, 'rb') as f:
        compressed = f.read()
    data = zlib.decompress(compressed)
    null_index = data.index(b'\x00')
    header = data[:null_index]
    content = data[null_index+1:]
    print(content.decode())

def write_tree():
    entries = []
    for fname in os.listdir('.'):
        if fname == GIT_DIR or not os.path.isfile(fname):
            continue
        with open(fname, 'rb') as f:
            data = f.read()
        sha1 = hash_object(data)
        mode = '100644'
        entry = '{} {}{}\x00{}'.format(mode, fname, '\x00', bytes.fromhex(sha1))
        entries.append(entry.encode())
    tree_data = b''.join(entries)
    return hash_object(tree_data, 'tree')

def commit(message):
    tree = write_tree()
    author = 'Your Name <you@example.com>'
    timestamp = int(time.time())
    commit_content = f'tree {tree}\nauthor {author} {timestamp} +0000\ncommitter {author} {timestamp} +0000\n\n{message}\n'
    sha1 = hash_object(commit_content.encode(), 'commit')
    with open(os.path.join(GIT_DIR, 'refs', 'heads', 'master'), 'w') as f:
        f.write(sha1)
    print(f'Committed to master: {sha1}')

def main():
    if len(sys.argv) < 2:
        print('Usage: mygit.py <command>')
        return
    cmd = sys.argv[1]
    if cmd == 'init':
        init()
    elif cmd == 'hash-object':
        with open(sys.argv[2], 'rb') as f:
            data = f.read()
        print(hash_object(data))
    elif cmd == 'cat-file':
        cat_file(sys.argv[2])
    elif cmd == 'commit':
        commit(' '.join(sys.argv[2:]))
    else:
        print(f'Unknown command: {cmd}')

if __name__ == '__main__':
    main()
