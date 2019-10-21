import ctypes
import random


def get_lorem_bytes():
	lorem = 'Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do\
	eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim\
	veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea\
	commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit\
	esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat\
	cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id\
	est laborum.'.split()
	file_str = ' '.join(random.choices(lorem, k=random.randint(600, 1000))).encode('utf-8')
	# file_str = ' '.join(random.choices(lorem, k=random.randint(3, 50))).encode('utf-8')
	return file_str

def test_01_create_file():
	'''
	Create a file and write to it.
	'''
	fd = uvafs.uva_open(b"test01.txt", True)
	if fd < 0: return -1
	# print(fd)
	file_str = b"this is my file."
	ret = uvafs.uva_write(fd, file_str, len(file_str))
	if ret < 0: return -1
	ret = uvafs.uva_close(fd)
	if ret < 0: return -1

	return 0

def test_02_create_read_file():
	'''
	Create a file, write to it, and then verify it can be read back properly.
	'''
	fd = uvafs.uva_open(b"test02.txt", True)
	if fd < 0: return -1
	file_str = b"this is my file."
	ret = uvafs.uva_write(fd, file_str, len(file_str))
	if ret < 0: return -1
	ret = uvafs.uva_close(fd)
	if ret < 0: return -1

	fd = uvafs.uva_open(b"test02.txt", False)
	if fd < 0: return -1
	recv = ctypes.create_string_buffer(512)
	recv_len = uvafs.uva_read(fd, recv, 0, 512)
	if recv_len < 0: return -1
	if recv_len != len(file_str): return -2
	ret = uvafs.uva_close(fd)
	if ret < 0: return -1

	if file_str != recv[0:len(file_str)]:
		return -3

	return 0

def test_03_longer_file():
	'''
	Create a file that is a bit longer.
	'''
	fd = uvafs.uva_open(b"test03.txt", True)
	if fd < 0: return -1
	file_str = get_lorem_bytes()
	ret = uvafs.uva_write(fd, file_str, len(file_str))
	if ret < 0: return -1
	ret = uvafs.uva_close(fd)
	if ret < 0: return -1

	return 0

def test_04_longer_file_rw():
	'''
	Create a file that is a bit longer.
	'''
	fd = uvafs.uva_open(b"test04.txt", True)
	if fd < 0: return -1
	file_str = get_lorem_bytes()
	ret = uvafs.uva_write(fd, file_str, len(file_str))
	if ret < 0: return -1
	ret = uvafs.uva_close(fd)
	if ret < 0: return -1

	fd = uvafs.uva_open(b"test04.txt", False)
	if fd < 0: return -1
	recv = ctypes.create_string_buffer(len(file_str))
	recv_len = uvafs.uva_read(fd, recv, 0, len(file_str))
	if recv_len < 0: return -1
	if recv_len != len(file_str): return -2
	ret = uvafs.uva_close(fd)
	if ret < 0: return -1

	if file_str != recv.raw:
		return -3

	return 0

def test_05_long_file_name():
	'''
	Create a file that is a bit longer.
	'''
	fd = uvafs.uva_open(b"this_is_my_really_long_file_name and it has spaces too that shouldn't be a problem right? wow ok 127 characters is actually qui", True)
	if fd < 0: return -1
	file_str = b"very long filename."
	ret = uvafs.uva_write(fd, file_str, len(file_str))
	if ret < 0: return -1
	ret = uvafs.uva_close(fd)
	if ret < 0: return -1

	return 0

def test_06_write_a_read_file():
	'''
	Create a file that is a bit longer.
	'''
	success = False
	fd = uvafs.uva_open(b"test06.txt", False)
	if fd < 0: return -1
	file_str = b"very long filename."
	ret = uvafs.uva_write(fd, file_str, len(file_str))
	if ret == -1: success = True
	ret = uvafs.uva_close(fd)
	if ret < 0: return -1

	if success:
		return 0
	else:
		return -2

def test_07_read_a_write_file():
	'''
	Create a file that is a bit longer.
	'''
	success = False
	fd = uvafs.uva_open(b"test07.txt", True)
	if fd < 0: return -1
	recv = ctypes.create_string_buffer(512)
	recv_len = uvafs.uva_read(fd, recv, 0, 512)
	if recv_len == -1: success = True
	ret = uvafs.uva_close(fd)
	if ret < 0: return -1

	if success:
		return 0
	else:
		return -2

def test_08_write_read_read():
	'''
	check consecutive reading
	'''
	fd = uvafs.uva_open(b"test08.txt", True)
	file_str = get_lorem_bytes()
	ret = uvafs.uva_write(fd, file_str, len(file_str))
	if ret < 0: return -1
	ret = uvafs.uva_close(fd)
	if ret < 0: return -1

	fd = uvafs.uva_open(b"test08.txt", False)
	if fd < 0: return -1
	l = int(len(file_str)/2)
	recv = ctypes.create_string_buffer(l)
	recv_len = uvafs.uva_read(fd, recv, 0, l)
	if recv_len < 0: return -1
	if recv_len != l: return -2
	str_cmp = recv.raw
	# print(str_cmp)
	recv = ctypes.create_string_buffer(len(file_str)-l)
	recv_len = uvafs.uva_read(fd, recv, 0, len(file_str))
	str_cmp += recv.raw
	ret = uvafs.uva_close(fd)
	if ret < 0: return -1
	# print(str_cmp)
	if recv_len != len(file_str)-l:	return -2
	if file_str != str_cmp:
		print()
		print(file_str)
		print(str_cmp)
		return -3
	return 0



def run_test(test):
	print('Running test "{}"...'.format(test.__name__), end='')
	ret = test()
	if ret == 0:
		print('SUCCESS')
	else:
		print('ERROR: {}'.format(ret))


# To use C version, do this:
uvafs = ctypes.CDLL('libuva_fs.so')

# To use Python version, create an object called `uvafs` with the filesystem
# functions.
#import uva_fs
#uvafs = uva_fs.filesystem()



# run_test(test_01_create_file)
# run_test(test_02_create_read_file)
# run_test(test_03_longer_file)
# run_test(test_04_longer_file_rw)
# run_test(test_05_long_file_name)
# run_test(test_06_write_a_read_file)
# run_test(test_07_read_a_write_file)
run_test(test_08_write_read_read)



