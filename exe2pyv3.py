#!/usr/bin/env python3
"""
EXE2PY - Công cụ chuyển đổi file EXE sang Python
Tích hợp từ PyInstaller Extractor và PYC to Bytecode Converter
"""

import os
import sys
import struct
import marshal
import zlib
import time
import argparse
import traceback
import importlib
import py_compile
import re
import dis
from uuid import uuid4 as uniquename
from colorama import init, Fore, Back, Style
from tqdm import tqdm
import requests
import json

# Khởi tạo colorama
init(autoreset=True)

# Định nghĩa các chuỗi ngôn ngữ
LANGUAGES = {
    'vi': {
        'title': 'GIỚI THIỆU CÔNG CỤ EXE2PY',
        'menu_title': 'MENU CHÍNH',
        'start_analyze': 'Bắt đầu phân tích file EXE',
        'view_info': 'Xem thông tin về công cụ',
        'exit': 'Thoát',
        'change_language': 'Change language',
        'choose_option': 'Chọn chức năng (1-4):',
        'enter_exe_path': 'Nhập đường dẫn file EXE cần chuyển đổi:',
        'file_not_found': 'Lỗi: File không tồn tại. Vui lòng thử lại.',
        'processing_file': 'Bắt đầu xử lý file:',
        'step2_title': 'Bước 2: Chuyển đổi file .pyc sang bytecode (.txt)',
        'step2_skip': 'Bạn có thể bỏ qua bước này nếu chỉ cần trích xuất file.',
        'step2_question': 'Bạn có muốn thực hiện bước 2 không? (y/n):',
        'starting_step2': 'Bắt đầu chuyển đổi file .pyc sang bytecode...',
        'step2_complete': 'Hoàn thành chuyển đổi bytecode: {0} thành công, {1} thất bại.',
        'step2_output_dir': 'Các file bytecode đã được lưu trong thư mục: {0}',
        'lib_dir_found': 'Phát hiện thư mục thư viện: {0}',
        'convert_lib_question': 'Bạn có muốn chuyển đổi các file .pyc trong thư mục thư viện không? (y/n):',
        'starting_lib_convert': 'Bắt đầu chuyển đổi thư viện...',
        'lib_convert_complete': 'Hoàn thành chuyển đổi thư viện: {0} thành công, {1} thất bại.',
        'lib_output_dir': 'Các file bytecode thư viện đã được lưu trong thư mục: {0}',
        'skipped_lib_convert': 'Đã bỏ qua chuyển đổi thư viện.',
        'skipped_step2': 'Đã bỏ qua bước 2 - Chuyển đổi bytecode.',
        'step3_title': 'Bước 3: Giải mã file .pyc trong PYZ sang mã Python (.py)',
        'step3_desc': 'Sử dụng API PyLingual.io để chuyển đổi thư viện Python',
        'step3_question': 'Bạn có muốn thực hiện bước 3 không? (y/n):',
        'decompile_lib_question': 'Bạn có muốn giải mã các file .pyc trong thư mục thư viện sang Python? (y/n):',
        'starting_decompile': 'Bắt đầu giải mã thư viện sang Python...',
        'decompile_note1': 'Lưu ý: Quá trình này yêu cầu kết nối Internet và có thể mất nhiều thời gian.',
        'decompile_note2': 'Mỗi file sẽ được gửi lên PyLingual.io API để giải mã.',
        'internet_ok': 'Kết nối Internet OK - Bắt đầu giải mã...',
        'decompile_complete': 'Hoàn thành giải mã Python: {0} thành công, {1} thất bại.',
        'python_output_dir': 'Các file Python đã được lưu trong thư mục: {0}',
        'internet_error': 'Không thể kết nối đến PyLingual.io - Vui lòng kiểm tra kết nối Internet',
        'lib_error': 'Không thể thực hiện bước 3: Thiếu thư viện requests hoặc json',
        'lib_install_guide': 'Cài đặt thư viện: pip install requests',
        'skipped_step3': 'Đã bỏ qua bước 3 - Giải mã sang Python.',
        'no_lib_dir': 'Không tìm thấy thư mục thư viện (PYZ-00.pyz_extracted). Bỏ qua bước 3.',
        'press_enter': 'Nhấn Enter để tiếp tục...',
        'thank_you': 'Cảm ơn bạn đã sử dụng exe2py!',
        'invalid_choice': 'Lựa chọn không hợp lệ. Vui lòng chọn lại.',
        'waiting_for_api': 'Đang đợi kết quả từ server (có thể mất vài giây)...',
        'uploading_file': 'Đang tải file lên PyLingual.io...',
        'upload_success': 'Tải file lên thành công. Đang lấy kết quả...',
        'waiting_retry': 'Thử lại lần {0}/5 sau 5 giây...',
        'max_retries': 'Đã thử lại 5 lần nhưng đều thất bại.',
        'wait_between_files': 'Chờ 5 giây trước khi xử lý file tiếp theo...',
        'decompile_success': 'Giải mã thành công: {0}',
        'decompile_failed': 'Giải mã thất bại: {0}',
        'verbose_on': 'Chế độ verbose đã bật - sẽ hiển thị thông tin chi tiết',
        'processing_failed': 'Quá trình xử lý thất bại',
        'select_language': 'Chọn ngôn ngữ:',
        'step3_mode': 'Chọn chế độ giải mã:',
        'step3_auto': '[1] Tự động giải mã tất cả',
        'step3_specific': '[2] Giải mã theo chỉ định',
        'enter_patterns': 'Nhập các mẫu tên file cần giải mã (phân cách bằng dấu phẩy):',
        'invalid_mode': 'Chế độ không hợp lệ. Vui lòng chọn 1 hoặc 2.',
        'convert_py': 'Chuyển đổi file Python (py ↔ pyc)',
        'convert_py_title': 'CHUYỂN ĐỔI FILE PYTHON',
        'convert_option_1': '[1] Chuyển .pyc sang .py',
        'convert_option_2': '[2] Chuyển .py sang .pyc',
        'convert_option_back': '[3] Quay lại menu chính',
        'enter_paths': 'Nhập đường dẫn file cần chuyển đổi (phân cách bằng dấu phẩy):',
        'output_dir': 'Thư mục đầu ra: {0}',
        'converting': 'Đang chuyển đổi...',
        'convert_success': 'Chuyển đổi thành công: {0}',
        'convert_failed': 'Chuyển đổi thất bại: {0}',
        'invalid_converter_choice': 'Lựa chọn không hợp lệ. Vui lòng chọn 1, 2 hoặc 3.',
        'no_valid_files': 'Không tìm thấy file hợp lệ để chuyển đổi.',
        'file_not_exist': 'File không tồn tại: {0}',
    },
    'en': {
        'title': 'EXE2PY TOOL INTRODUCTION',
        'menu_title': 'MAIN MENU',
        'start_analyze': 'Start analyzing EXE file',
        'view_info': 'View tool information',
        'exit': 'Exit',
        'change_language': 'Change language',
        'choose_option': 'Choose function (1-4):',
        'enter_exe_path': 'Enter EXE file path to convert:',
        'file_not_found': 'Error: File does not exist. Please try again.',
        'processing_file': 'Starting to process file:',
        'step2_title': 'Step 2: Convert .pyc files to bytecode (.txt)',
        'step2_skip': 'You can skip this step if you only need to extract files.',
        'step2_question': 'Do you want to perform Step 2? (y/n):',
        'starting_step2': 'Starting conversion of .pyc files to bytecode...',
        'step2_complete': 'Completed bytecode conversion: {0} successful, {1} failed.',
        'step2_output_dir': 'Bytecode files have been saved in the directory: {0}',
        'lib_dir_found': 'Library directory detected: {0}',
        'convert_lib_question': 'Do you want to convert .pyc files in the library directory? (y/n):',
        'starting_lib_convert': 'Starting library conversion...',
        'lib_convert_complete': 'Completed library conversion: {0} successful, {1} failed.',
        'lib_output_dir': 'Library bytecode files have been saved in the directory: {0}',
        'skipped_lib_convert': 'Skipped library conversion.',
        'skipped_step2': 'Skipped Step 2 - Bytecode conversion.',
        'step3_title': 'Step 3: Decompile .pyc files in PYZ to Python code (.py)',
        'step3_desc': 'Using PyLingual.io API to convert Python libraries',
        'step3_question': 'Do you want to perform Step 3? (y/n):',
        'decompile_lib_question': 'Do you want to decompile .pyc files in the library directory to Python? (y/n):',
        'starting_decompile': 'Starting library decompilation to Python...',
        'decompile_note1': 'Note: This process requires Internet connection and may take time.',
        'decompile_note2': 'Each file will be sent to PyLingual.io API for decompilation.',
        'internet_ok': 'Internet connection OK - Starting decompilation...',
        'decompile_complete': 'Completed Python decompilation: {0} successful, {1} failed.',
        'python_output_dir': 'Python files have been saved in the directory: {0}',
        'internet_error': 'Cannot connect to PyLingual.io - Please check your Internet connection',
        'lib_error': 'Cannot perform Step 3: Missing requests or json library',
        'lib_install_guide': 'Install library: pip install requests',
        'skipped_step3': 'Skipped Step 3 - Decompilation to Python.',
        'no_lib_dir': 'Library directory not found (PYZ-00.pyz_extracted). Skipping Step 3.',
        'press_enter': 'Press Enter to continue...',
        'thank_you': 'Thank you for using exe2py!',
        'invalid_choice': 'Invalid choice. Please choose again.',
        'waiting_for_api': 'Waiting for results from server (may take a few seconds)...',
        'uploading_file': 'Uploading file to PyLingual.io...',
        'upload_success': 'Upload successful. Getting results...',
        'waiting_retry': 'Retrying {0}/5 after 5 seconds...',
        'max_retries': 'Tried 5 times but all failed.',
        'wait_between_files': 'Waiting 5 seconds before processing the next file...',
        'decompile_success': 'Decompilation successful: {0}',
        'decompile_failed': 'Decompilation failed: {0}',
        'verbose_on': 'Verbose mode enabled - will display detailed information',
        'processing_failed': 'Processing failed',
        'select_language': 'Select language:',
        'step3_mode': 'Select decompilation mode:',
        'step3_auto': '[1] Auto decompile all',
        'step3_specific': '[2] Decompile specific files',
        'enter_patterns': 'Enter file patterns to decompile (comma-separated):',
        'invalid_mode': 'Invalid mode. Please choose 1 or 2.',
        'convert_py': 'Convert Python files (py ↔ pyc)',
        'convert_py_title': 'PYTHON FILE CONVERTER',
        'convert_option_1': '[1] Convert .pyc to .py',
        'convert_option_2': '[2] Convert .py to .pyc',
        'convert_option_back': '[3] Back to main menu',
        'enter_paths': 'Enter file paths to convert (comma-separated):',
        'output_dir': 'Output directory: {0}',
        'converting': 'Converting...',
        'convert_success': 'Conversion successful: {0}',
        'convert_failed': 'Conversion failed: {0}',
        'invalid_converter_choice': 'Invalid choice. Please select 1, 2 or 3.',
        'no_valid_files': 'No valid files found to convert.',
        'file_not_exist': 'File does not exist: {0}',
    }
}

# Mặc định sử dụng tiếng Việt
current_language = 'vi'

def set_language(lang):
    """Đặt ngôn ngữ hiện tại"""
    global current_language
    try:
        if lang in LANGUAGES:
            current_language = lang
            print(f"{Fore.GREEN}[+] Đã chuyển sang ngôn ngữ: {lang}")
        else:
            current_language = 'vi'  # Mặc định là tiếng Việt nếu ngôn ngữ không được hỗ trợ
            print(f"{Fore.YELLOW}[!] Ngôn ngữ không được hỗ trợ, sử dụng tiếng Việt")
    except Exception as e:
        print(f"{Fore.RED}[!] Lỗi khi chuyển đổi ngôn ngữ: {str(e)}")
        current_language = 'vi'

def get_text(key, *args):
    """Lấy văn bản theo ngôn ngữ hiện tại"""
    try:
        keys = key.split('.')
        data = LANGUAGES[current_language]
        for k in keys:
            if k in data:
                data = data[k]
            else:
                return key
        
        # Thay thế các tham số định dạng nếu có
        if args and isinstance(data, str):
            try:
                return data.format(*args)
            except:
                return data
        return data
    except Exception as e:
        print(f"{Fore.RED}[!] Lỗi ngôn ngữ: {str(e)}")
        return key

def clear_screen():
    """Xóa màn hình console dựa trên hệ điều hành"""
    os.system('cls' if os.name == 'nt' else 'clear')

class CTOCEntry:
    def __init__(self, position, cmprsdDataSize, uncmprsdDataSize, cmprsFlag, typeCmprsData, name):
        self.position = position
        self.cmprsdDataSize = cmprsdDataSize
        self.uncmprsdDataSize = uncmprsdDataSize
        self.cmprsFlag = cmprsFlag
        self.typeCmprsData = typeCmprsData
        self.name = name

class PyInstArchive:
    PYINST20_COOKIE_SIZE = 24
    PYINST21_COOKIE_SIZE = 24 + 64
    MAGIC = b'MEI\014\013\012\013\016'

    def __init__(self, path):
        self.filePath = path
        self.pycMagic = b'\0' * 4
        self.barePycList = []

    def open(self):
        try:
            self.fPtr = open(self.filePath, 'rb')
            self.fileSize = os.stat(self.filePath).st_size
            return True
        except:
            print(f'{Fore.RED}[!] Lỗi: Không thể mở file {self.filePath}')
            return False

    def close(self):
        try:
            self.fPtr.close()
        except:
            pass

    def checkFile(self):
        print(f'{Fore.CYAN}[+] Đang xử lý {self.filePath}')

        searchChunkSize = 8192
        endPos = self.fileSize
        self.cookiePos = -1

        if endPos < len(self.MAGIC):
            print(f'{Fore.RED}[!] Lỗi: File quá ngắn hoặc bị cắt')
            return False

        while True:
            startPos = endPos - searchChunkSize if endPos >= searchChunkSize else 0
            chunkSize = endPos - startPos

            if chunkSize < len(self.MAGIC):
                break

            self.fPtr.seek(startPos, os.SEEK_SET)
            data = self.fPtr.read(chunkSize)

            offs = data.rfind(self.MAGIC)

            if offs != -1:
                self.cookiePos = startPos + offs
                break

            endPos = startPos + len(self.MAGIC) - 1

            if startPos == 0:
                break

        if self.cookiePos == -1:
            print(f'{Fore.RED}[!] Lỗi: Không tìm thấy cookie, phiên bản PyInstaller không được hỗ trợ hoặc không phải file PyInstaller')
            return False

        self.fPtr.seek(self.cookiePos + self.PYINST20_COOKIE_SIZE, os.SEEK_SET)

        if b'python' in self.fPtr.read(64).lower():
            print(f'{Fore.GREEN}[+] Phiên bản PyInstaller: 2.1+')
            self.pyinstVer = 21
        else:
            self.pyinstVer = 20
            print(f'{Fore.GREEN}[+] Phiên bản PyInstaller: 2.0')

        return True

    def getCArchiveInfo(self):
        try:
            if self.pyinstVer == 20:
                self.fPtr.seek(self.cookiePos, os.SEEK_SET)
                (magic, lengthofPackage, toc, tocLen, pyver) = \
                struct.unpack('!8siiii', self.fPtr.read(self.PYINST20_COOKIE_SIZE))
            elif self.pyinstVer == 21:
                self.fPtr.seek(self.cookiePos, os.SEEK_SET)
                (magic, lengthofPackage, toc, tocLen, pyver, pylibname) = \
                struct.unpack('!8sIIii64s', self.fPtr.read(self.PYINST21_COOKIE_SIZE))
        except:
            print(f'{Fore.RED}[!] Lỗi: File không phải là PyInstaller archive')
            return False

        self.pymaj, self.pymin = (pyver//100, pyver%100) if pyver >= 100 else (pyver//10, pyver%10)
        print(f'{Fore.GREEN}[+] Phiên bản Python: {self.pymaj}.{self.pymin}')

        tailBytes = self.fileSize - self.cookiePos - (self.PYINST20_COOKIE_SIZE if self.pyinstVer == 20 else self.PYINST21_COOKIE_SIZE)
        self.overlaySize = lengthofPackage + tailBytes
        self.overlayPos = self.fileSize - self.overlaySize
        self.tableOfContentsPos = self.overlayPos + toc
        self.tableOfContentsSize = tocLen

        print(f'{Fore.GREEN}[+] Kích thước package: {lengthofPackage} bytes')
        return True

    def parseTOC(self):
        self.fPtr.seek(self.tableOfContentsPos, os.SEEK_SET)
        self.tocList = []
        parsedLen = 0

        while parsedLen < self.tableOfContentsSize:
            (entrySize, ) = struct.unpack('!i', self.fPtr.read(4))
            nameLen = struct.calcsize('!iIIIBc')

            (entryPos, cmprsdDataSize, uncmprsdDataSize, cmprsFlag, typeCmprsData, name) = \
            struct.unpack( \
                '!IIIBc{0}s'.format(entrySize - nameLen), \
                self.fPtr.read(entrySize - 4))

            try:
                name = name.decode("utf-8").rstrip("\0")
            except UnicodeDecodeError:
                newName = str(uniquename())
                print(f'{Fore.YELLOW}[!] Cảnh báo: Tên file {name} chứa byte không hợp lệ. Sử dụng tên ngẫu nhiên {newName}')
                name = newName

            if name.startswith("/"):
                name = name.lstrip("/")

            if len(name) == 0:
                name = str(uniquename())
                print(f'{Fore.YELLOW}[!] Cảnh báo: Tìm thấy file không tên trong CArchive. Sử dụng tên ngẫu nhiên {name}')

            self.tocList.append( \
                                CTOCEntry(                      \
                                    self.overlayPos + entryPos, \
                                    cmprsdDataSize,             \
                                    uncmprsdDataSize,           \
                                    cmprsFlag,                  \
                                    typeCmprsData,              \
                                    name                        \
                                ))

            parsedLen += entrySize
        print(f'{Fore.GREEN}[+] Tìm thấy {len(self.tocList)} files trong CArchive')

    def extractFiles(self):
        print(f'{Fore.CYAN}[+] Bắt đầu trích xuất...')
        extractionDir = os.path.join(os.getcwd(), os.path.basename(self.filePath) + '_extracted')

        if not os.path.exists(extractionDir):
            os.mkdir(extractionDir)

        os.chdir(extractionDir)

        for entry in self.tocList:
            self.fPtr.seek(entry.position, os.SEEK_SET)
            data = self.fPtr.read(entry.cmprsdDataSize)

            if entry.cmprsFlag == 1:
                try:
                    data = zlib.decompress(data)
                except zlib.error:
                    print(f'{Fore.RED}[!] Lỗi: Không thể giải nén {entry.name}')
                    continue
                assert len(data) == entry.uncmprsdDataSize

            if entry.typeCmprsData == b'd' or entry.typeCmprsData == b'o':
                continue

            basePath = os.path.dirname(entry.name)
            if basePath != '':
                if not os.path.exists(basePath):
                    os.makedirs(basePath)

            if entry.typeCmprsData == b's':
                print(f'{Fore.GREEN}[+] Điểm vào có thể: {entry.name}.pyc')
                if self.pycMagic == b'\0' * 4:
                    self.barePycList.append(entry.name + '.pyc')
                self._writePyc(entry.name + '.pyc', data)

            elif entry.typeCmprsData == b'M' or entry.typeCmprsData == b'm':
                if data[2:4] == b'\r\n':
                    if self.pycMagic == b'\0' * 4:
                        self.pycMagic = data[0:4]
                    self._writeRawData(entry.name + '.pyc', data)
                else:
                    if self.pycMagic == b'\0' * 4:
                        self.barePycList.append(entry.name + '.pyc')
                    self._writePyc(entry.name + '.pyc', data)
            else:
                self._writeRawData(entry.name, data)
                if entry.typeCmprsData == b'z' or entry.typeCmprsData == b'Z':
                    self._extractPyz(entry.name)

        self._fixBarePycs()
        return extractionDir

    def _writeRawData(self, filepath, data):
        nm = filepath.replace('\\', os.path.sep).replace('/', os.path.sep).replace('..', '__')
        nmDir = os.path.dirname(nm)
        if nmDir != '' and not os.path.exists(nmDir):
            os.makedirs(nmDir)

        with open(nm, 'wb') as f:
            f.write(data)

    def _writePyc(self, filename, data):
        with open(filename, 'wb') as pycFile:
            pycFile.write(self.pycMagic)
            if self.pymaj >= 3 and self.pymin >= 7:
                pycFile.write(b'\0' * 4)
                pycFile.write(b'\0' * 8)
            else:
                pycFile.write(b'\0' * 4)
                if self.pymaj >= 3 and self.pymin >= 3:
                    pycFile.write(b'\0' * 4)
            pycFile.write(data)

    def _fixBarePycs(self):
        for pycFile in self.barePycList:
            with open(pycFile, 'r+b') as pycFile:
                pycFile.write(self.pycMagic)

    def _extractPyz(self, name):
        dirName = name + '_extracted'
        if not os.path.exists(dirName):
            os.mkdir(dirName)

        with open(name, 'rb') as f:
            pyzMagic = f.read(4)
            assert pyzMagic == b'PYZ\0'

            pyzPycMagic = f.read(4)

            if self.pycMagic == b'\0' * 4:
                self.pycMagic = pyzPycMagic
            elif self.pycMagic != pyzPycMagic:
                self.pycMagic = pyzPycMagic
                print(f'{Fore.YELLOW}[!] Cảnh báo: pyc magic của files trong PYZ archive khác với CArchive')

            if self.pymaj != sys.version_info.major or self.pymin != sys.version_info.minor:
                print(f'{Fore.YELLOW}[!] Cảnh báo: Script đang chạy trên phiên bản Python khác với phiên bản dùng để build')
                print(f'{Fore.YELLOW}[!] Vui lòng chạy script này trên Python {self.pymaj}.{self.pymin}')
                print(f'{Fore.YELLOW}[!] Bỏ qua trích xuất pyz')
                return

            (tocPosition, ) = struct.unpack('!i', f.read(4))
            f.seek(tocPosition, os.SEEK_SET)

            try:
                toc = marshal.load(f)
            except:
                print(f'{Fore.RED}[!] Unmarshalling THẤT BẠI. Không thể trích xuất {name}')
                return

            print(f'{Fore.GREEN}[+] Tìm thấy {len(toc)} files trong PYZ archive')

            if type(toc) == list:
                toc = dict(toc)

            for key in toc.keys():
                (ispkg, pos, length) = toc[key]
                f.seek(pos, os.SEEK_SET)
                fileName = key

                try:
                    fileName = fileName.decode('utf-8')
                except:
                    pass

                fileName = fileName.replace('..', '__').replace('.', os.path.sep)

                if ispkg == 1:
                    filePath = os.path.join(dirName, fileName, '__init__.pyc')
                else:
                    filePath = os.path.join(dirName, fileName + '.pyc')

                fileDir = os.path.dirname(filePath)
                if not os.path.exists(fileDir):
                    os.makedirs(fileDir)

                try:
                    data = f.read(length)
                    data = zlib.decompress(data)
                except:
                    print(f'{Fore.RED}[!] Lỗi: Không thể giải nén {filePath}, có thể đã bị mã hóa')
                    open(filePath + '.encrypted', 'wb').write(data)
                else:
                    self._writePyc(filePath, data)

def get_python_version_from_pyc(pyc_file):
    try:
        with open(pyc_file, 'rb') as f:
            magic = f.read(4)
            
        magic_to_version = {
            3310: (3, 4),
            3350: (3, 5), 
            3390: (3, 6),
            3400: (3, 7),
            3430: (3, 8), 
            3450: (3, 9),
            3490: (3, 10),
            3500: (3, 11),
            3510: (3, 12),
            3570: (3, 13),
            3571: (3, 13),
        }
        
        magic_int = struct.unpack('<H', magic[:2])[0]
        closest_magic = min(magic_to_version.keys(), key=lambda x: abs(x - magic_int))
        
        if abs(closest_magic - magic_int) < 50:
            detected_version = magic_to_version[closest_magic]
            print(f"{Fore.GREEN}[+] Phát hiện Python {detected_version[0]}.{detected_version[1]} bytecode")
            return detected_version
        else:
            print(f"{Fore.RED}[!] Magic number không xác định: {magic_int} (0x{magic_int:04x})")
            return None
    except Exception as e:
        print(f"{Fore.RED}[!] Lỗi phát hiện phiên bản Python: {str(e)}")
        return None

def pyc_to_py(pyc_file, output_file=None, force=False):
    if not os.path.exists(pyc_file):
        print(f"{Fore.RED}[!] Lỗi: File '{pyc_file}' không tồn tại.")
        return False
    
    if not pyc_file.endswith('.pyc'):
        print(f"{Fore.YELLOW}[!] Cảnh báo: File '{pyc_file}' không có phần mở rộng .pyc")
    
    if output_file is None:
        if pyc_file.endswith('.pyc'):
            output_file = pyc_file[:-4] + '.py'
        else:
            output_file = pyc_file + '.py'
    
    if os.path.exists(output_file) and not force:
        print(f"{Fore.RED}[!] Lỗi: File đầu ra '{output_file}' đã tồn tại. Sử dụng --force để ghi đè.")
        return False
    
    py_version = get_python_version_from_pyc(pyc_file)
    
    if py_version and py_version[0] == 3 and py_version[1] >= 12:
        print(f"{Fore.YELLOW}[!] Phát hiện Python {py_version[0]}.{py_version[1]} bytecode - sử dụng xử lý đặc biệt")
        return handle_modern_python_pyc(pyc_file, output_file, py_version)
    
    success = False
    try:
        import uncompyle6
        print(f"{Fore.CYAN}[+] Đang thử decompile '{pyc_file}' với uncompyle6...")
        with open(output_file, 'w', encoding='utf-8') as f:
            uncompyle6.decompile_file(pyc_file, f)
        print(f"{Fore.GREEN}[+] Chuyển đổi thành công '{pyc_file}' sang '{output_file}'")
        success = True
            
    except Exception as e:
        error_details = traceback.format_exc()
        print(f"{Fore.RED}[!] Lỗi decompile '{pyc_file}' với uncompyle6: {str(e)}")
        print(f"{Fore.RED}[!] Thông tin lỗi chi tiết:\n{error_details}")
        
        success = try_alternative_decompilers(pyc_file, output_file)
    
    return success

def handle_modern_python_pyc(pyc_file, output_file, py_version):
    py_ver_str = f"{py_version[0]}.{py_version[1]}"
    print(f"{Fore.CYAN}[+] Đang xử lý file bytecode Python {py_ver_str}...")
    
    try:
        print(f"{Fore.CYAN}[+] Thử pycdc cho file Python {py_ver_str}...")
        import subprocess
        try:
            result = subprocess.run(['pycdc', pyc_file], capture_output=True, text=True, encoding='utf-8')
            if result.returncode == 0 and result.stdout.strip():
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(result.stdout)
                print(f"{Fore.GREEN}[+] Chuyển đổi thành công file Python {py_ver_str} '{pyc_file}' sang '{output_file}' sử dụng pycdc")
                return True
            else:
                print(f"{Fore.YELLOW}[!] pycdc không khả dụng hoặc không có output: {result.stderr}")
        except FileNotFoundError:
            print(f"{Fore.YELLOW}[!] pycdc không được cài đặt. Bỏ qua phương pháp này.")
    except Exception as e:
        print(f"{Fore.RED}[!] Lỗi sử dụng pycdc: {str(e)}")

    try:
        print(f"{Fore.CYAN}[+] Sử dụng phương pháp disassembly đặc biệt cho Python {py_ver_str}...")
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(f"# Disassembly của file Python {py_ver_str}: {pyc_file}\n")
            f.write("# Lưu ý: Đây là disassembly vì không hỗ trợ decompile trực tiếp cho phiên bản Python này\n")
            f.write("# Bạn có thể cần tái tạo thủ công mã Python từ thông tin này\n\n")
            
            with open(pyc_file, 'rb') as pyc:
                pyc.seek(16)
                try:
                    code = marshal.load(pyc)
                    f.write("# Đã trích xuất thành công đối tượng code\n\n")
                    
                    f.write(f"# Sử dụng Python {sys.version} cho disassembly\n\n")
                    
                    f.write("# Các hằng số chuỗi tìm thấy trong code:\n")
                    str_constants = []
                    for const in code.co_consts:
                        if isinstance(const, str) and const:
                            try:
                                str_constants.append(const)
                                f.write(f"# '{const}'\n")
                            except UnicodeEncodeError:
                                f.write(f"# <string không thể hiển thị>\n")
                    f.write("\n")
                    
                    f.write("# Disassembly đầy đủ:\n")
                    old_stdout = sys.stdout
                    sys.stdout = f
                    dis.dis(code)
                    sys.stdout = old_stdout
                    
                    f.write("\n\n# Thông tin đối tượng Code:\n")
                    f.write(f"# co_name: {code.co_name}\n")
                    f.write(f"# co_filename: {code.co_filename}\n")
                    f.write(f"# co_firstlineno: {code.co_firstlineno}\n")
                    f.write(f"# co_names: {code.co_names}\n")
                    f.write(f"# co_varnames: {code.co_varnames}\n")
                    
                except Exception as e:
                    f.write(f"# Lỗi trích xuất đối tượng code: {str(e)}\n")
                    traceback_str = traceback.format_exc()
                    f.write(f"# Traceback: {traceback_str}\n")
        
        print(f"{Fore.GREEN}[+] Phân tích cơ bản Python {py_ver_str} đã lưu vào '{output_file}'. Có thể cần tái tạo thủ công.")
        return True
    except Exception as e:
        print(f"{Fore.RED}[!] Tất cả các phương pháp decompile Python {py_ver_str} đều thất bại: {str(e)}")
        traceback.print_exc()
        return False

def try_alternative_decompilers(pyc_file, output_file):
    try:
        print(f"{Fore.CYAN}[+] Thử với decompiler thay thế: decompyle3...")
        import decompyle3.main
        decompyle3.main.decompile_file(pyc_file, output_file)
        print(f"{Fore.GREEN}[+] Chuyển đổi thành công '{pyc_file}' sang '{output_file}' sử dụng decompyle3")
        return True
    except Exception as e:
        print(f"{Fore.RED}[!] decompyle3 cũng thất bại: {str(e)}")
    
    try:
        print(f"{Fore.CYAN}[+] Thử với decompiler thay thế: pycdc...")
        import subprocess
        result = subprocess.run(['pycdc', pyc_file], capture_output=True, text=True)
        if result.returncode == 0:
            with open(output_file, 'w') as f:
                f.write(result.stdout)
            print(f"{Fore.GREEN}[+] Chuyển đổi thành công '{pyc_file}' sang '{output_file}' sử dụng pycdc")
            return True
        else:
            print(f"{Fore.RED}[!] pycdc thất bại: {result.stderr}")
    except Exception as e:
        print(f"{Fore.RED}[!] Lỗi sử dụng pycdc: {str(e)}")
    
    try:
        print(f"{Fore.CYAN}[+] Thử disassembly cơ bản như phương án cuối cùng...")
        import dis
        import marshal
        
        with open(output_file, 'w') as f:
            f.write(f"# Disassembly của {pyc_file}\n")
            f.write("# Lưu ý: Đây là disassembly dự phòng vì decompile thất bại\n")
            f.write("# Bạn có thể cần tái tạo thủ công mã Python từ thông tin này\n\n")
            
            with open(pyc_file, 'rb') as pyc:
                pyc.seek(16)
                try:
                    code = marshal.load(pyc)
                    f.write("# Đã trích xuất thành công đối tượng code\n\n")
                    
                    old_stdout = sys.stdout
                    sys.stdout = f
                    dis.dis(code)
                    sys.stdout = old_stdout
                    
                    f.write("\n\n# Thông tin đối tượng Code:\n")
                    f.write(f"# co_name: {code.co_name}\n")
                    f.write(f"# co_filename: {code.co_filename}\n")
                    f.write(f"# co_firstlineno: {code.co_firstlineno}\n")
                    f.write(f"# co_names: {code.co_names}\n")
                    f.write(f"# co_varnames: {code.co_varnames}\n")
                    f.write(f"# co_consts: {code.co_consts}\n")
                except Exception as e:
                    f.write(f"# Lỗi trích xuất đối tượng code: {str(e)}\n")
        
        print(f"{Fore.GREEN}[+] Disassembly cơ bản đã lưu vào '{output_file}'. Có thể cần tái tạo thủ công.")
        return True
    except Exception as e:
        print(f"{Fore.RED}[!] Tất cả các phương pháp decompile đều thất bại: {str(e)}")
        return False

def process_directory_to_bytecode(directory, force=False):
    success = 0
    failed = 0
    bytecode_dir = directory + "_bytecode"
    if not os.path.exists(bytecode_dir):
        try:
            os.makedirs(bytecode_dir)
        except Exception:
            return 0, 0
    pyc_files = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.pyc'):
                pyc_files.append(os.path.join(root, file))
    for pyc_path in tqdm(pyc_files, desc="Đang chuyển đổi pyc → bytecode txt", ncols=80, leave=False, dynamic_ncols=True):
        rel_path = os.path.relpath(pyc_path, directory)
        output_path = os.path.join(bytecode_dir, rel_path[:-4] + '.txt')
        output_dir = os.path.dirname(output_path)
        if not os.path.exists(output_dir):
            try:
                os.makedirs(output_dir)
            except Exception:
                failed += 1
                continue
        if pyc_to_bytecode_txt(pyc_path, output_path, force=force):
            success += 1
        else:
            failed += 1
    return success, failed

def process_flat_pyc_to_bytecode(directory, force=False):
    """Chỉ chuyển các file .pyc ở thư mục gốc, không đệ quy."""
    import glob
    success = 0
    failed = 0
    bytecode_dir = directory + "_bytecode"
    if not os.path.exists(bytecode_dir):
        try:
            os.makedirs(bytecode_dir)
        except Exception:
            return 0, 0
    pyc_files = glob.glob(os.path.join(directory, '*.pyc'))
    for pyc_path in tqdm(pyc_files, desc="Đang chuyển đổi pyc thư viện → bytecode txt", ncols=80, leave=False, dynamic_ncols=True):
        file_name = os.path.basename(pyc_path)
        output_path = os.path.join(bytecode_dir, file_name[:-4] + '.txt')
        if pyc_to_bytecode_txt(pyc_path, output_path, force=force):
            success += 1
        else:
            failed += 1
    return success, failed

def pyc_to_bytecode_txt(pyc_file, output_file=None, force=False):
    import dis
    import marshal
    if not os.path.exists(pyc_file):
        return False
    if output_file is None:
        output_file = pyc_file[:-4] + '.txt'
    if os.path.exists(output_file) and not force:
        return False
    try:
        with open(pyc_file, 'rb') as f:
            f.seek(16)
            code = marshal.load(f)
        with open(output_file, 'w', encoding='utf-8') as out:
            out.write(f'# Bytecode disassembly of {pyc_file}\n')
            dis.dis(code, file=out)
        return True
    except Exception:
        return False

def print_banner():
    banner = f"""
{Fore.CYAN}╔═════════════════════════════════════════════════════════════════════╗
{Fore.CYAN}║                                                            
{Fore.CYAN}║  {Fore.YELLOW}███████╗██╗  ██╗███████╗     ██████╗              
{Fore.CYAN}║  {Fore.YELLOW}██╔════╝╚██╗██╔╝██╔════╝    ██╔═══██╗             
{Fore.CYAN}║  {Fore.YELLOW}█████╗   ╚███╔╝ █████╗      ╚════██╔╝             
{Fore.CYAN}║  {Fore.YELLOW}██╔══╝   ██╔██╗ ██╔══╝       █████╔╝              
{Fore.CYAN}║  {Fore.YELLOW}███████╗██╔╝ ██╗███████╗    ██╔═══╝               
{Fore.CYAN}║  {Fore.YELLOW}╚══════╝╚═╝  ╚═╝╚══════╝    ███████╗              
{Fore.CYAN}║  {Fore.YELLOW}                            ╚══════╝              
{Fore.CYAN}║  {Fore.YELLOW}██████╗ ██╗   ██╗                             
{Fore.CYAN}║  {Fore.YELLOW}██╔══██╗╚██╗ ██╔╝                             
{Fore.CYAN}║  {Fore.YELLOW}██████╔╝ ╚████╔╝                              
{Fore.CYAN}║  {Fore.YELLOW}██╔═══╝   ╚██╔╝                               
{Fore.CYAN}║  {Fore.YELLOW}██║        ██║                                
{Fore.CYAN}║  {Fore.YELLOW}╚═╝        ╚═╝                                
{Fore.CYAN}║                                                            
{Fore.CYAN}║  {Fore.GREEN}exe2py v1.0                                               
{Fore.CYAN}║  {Fore.GREEN}Author: HiepZ8 (Hồ Hiệp)
{Fore.CYAN}║  {Fore.GREEN}Github: https://github.com/hiep-py
{Fore.CYAN}║  {Fore.GREEN}Tiktok: https://www.tiktok.com/@hiepz8py
{Fore.CYAN}║  {Fore.GREEN}Youtube: https://www.youtube.com/@Hohiep-db2vx (@Hohiep-db2vx)      
{Fore.CYAN}║                                                            
{Fore.CYAN}╚═════════════════════════════════════════════════════════════════════╝
"""
    print(banner)

def print_intro():
    intro = f"""
{Fore.CYAN}╔════════════════════════════════════════════════════════════╗
{Fore.CYAN}║  {Fore.GREEN}{get_text('title')}                        {Fore.CYAN}
{Fore.CYAN}╠════════════════════════════════════════════════════════════╣
{Fore.CYAN}║                                                            ║
{Fore.CYAN}║  {Fore.YELLOW}[+] Công cụ trích xuất và phân tích file EXE được tạo    
{Fore.CYAN}║     bởi PyInstaller(free).                                      
{Fore.CYAN}║                                                            
{Fore.CYAN}║  {Fore.YELLOW}[+] Tính năng chính:                                    
{Fore.CYAN}║     • Trích xuất file từ EXE (PyInstaller archive)        
{Fore.CYAN}║     • Chuyển đổi file .pyc sang bytecode (.txt)           
{Fore.CYAN}║     • Hỗ trợ nhiều phiên bản Python (2.0 - 3.13)          
{Fore.CYAN}║     • Tự động phát hiện phiên bản PyInstaller             
{Fore.CYAN}║                                                            
{Fore.CYAN}║  {Fore.YELLOW}[+] Cách sử dụng:                                      
{Fore.CYAN}║     1. Nhập đường dẫn file EXE cần phân tích              
{Fore.CYAN}║     2. Chọn có/không thực hiện chuyển đổi bytecode        
{Fore.CYAN}║     3. Chọn có/không chuyển đổi thư viện                  
{Fore.CYAN}║                                                            
{Fore.CYAN}║  {Fore.YELLOW}[+] Lưu ý:                                            
{Fore.CYAN}║     • File EXE phải được tạo bởi PyInstaller              
{Fore.CYAN}║     • Có thể bỏ qua bước chuyển đổi bytecode              
{Fore.CYAN}║     • Kết quả được lưu trong thư mục riêng                
{Fore.CYAN}║                                                            
{Fore.CYAN}╚════════════════════════════════════════════════════════════╝
"""
    print(intro)

def print_menu():
    menu = f"""
{Fore.CYAN}╔════════════════════════════════════════════════════════════╗
{Fore.CYAN}║  {Fore.GREEN}{get_text('menu_title')}                                        {Fore.CYAN}
{Fore.CYAN}╠════════════════════════════════════════════════════════════╣
{Fore.CYAN}║                                                            ║
{Fore.CYAN}║  {Fore.YELLOW}[1] {get_text('start_analyze')}                        
{Fore.CYAN}║  {Fore.YELLOW}[2] {get_text('view_info')}                          
{Fore.CYAN}║  {Fore.YELLOW}[3] {get_text('exit')}                                            
{Fore.CYAN}║  {Fore.YELLOW}[4] {get_text('change_language')}
{Fore.CYAN}║  {Fore.YELLOW}[5] {get_text('convert_py')}                                           
{Fore.CYAN}║                                                            ║
{Fore.CYAN}╚════════════════════════════════════════════════════════════╝
"""
    print(menu)

def decompile_pyc_pylingual(pyc_file, output_file=None):
    """Gửi file PYC đến PyLingual.io API và lấy kết quả giải mã"""
    max_retries = 5
    for attempt in range(1, max_retries + 1):
        try:
            # API endpoints
            upload_url = "https://api.pylingual.io/upload"
            
            # Tải file lên
            print(f"{Fore.CYAN}[+] {get_text('uploading_file')}")
            
            with open(pyc_file, 'rb') as f:
                files = {'file': (os.path.basename(pyc_file), f)}
                response = requests.post(upload_url, files=files)
            
            if response.status_code != 200:
                print(f"{Fore.RED}[!] API Error: {response.status_code}")
                if attempt < max_retries:
                    print(f"{Fore.YELLOW}[!] {get_text('waiting_retry', attempt)}")
                    time.sleep(5)
                    continue
                else:
                    print(f"{Fore.RED}[!] {get_text('max_retries')}")
                    return None
            
            # Lấy identifier từ response
            data = response.json()
            if 'identifier' not in data:
                print(f"{Fore.RED}[!] Invalid response: {data}")
                if attempt < max_retries:
                    print(f"{Fore.YELLOW}[!] {get_text('waiting_retry', attempt)}")
                    time.sleep(5)
                    continue
                else:
                    print(f"{Fore.RED}[!] {get_text('max_retries')}")
                    return None
            
            identifier = data['identifier']
            print(f"{Fore.GREEN}[+] {get_text('upload_success')}")
            print(f"{Fore.CYAN}[+] Identifier: {identifier}")
            
            # Lưu identifier để sử dụng sau này nếu cần
            with open("last_identifier.txt", "w") as f:
                f.write(identifier)
            
            # URL để lấy kết quả giải mã
            view_json_url = f"https://api.pylingual.io/view_chimera?identifier={identifier}"
            
            # Đợi kết quả (có thể mất vài giây)
            print(f"{Fore.CYAN}[+] {get_text('waiting_for_api')}")
            time.sleep(10)  # Đợi 10 giây để đảm bảo kết quả đã sẵn sàng
            
            # Truy cập trực tiếp vào API view_chimera để lấy toàn bộ JSON
            print(f"{Fore.CYAN}[+] Lấy dữ liệu từ API view_chimera dưới dạng JSON...")
            
            try:
                view_response = requests.get(view_json_url)
                if view_response.status_code == 200:
                    # Phân tích JSON
                    view_data = view_response.json()
                    
                    # Tìm kiếm sâu trong JSON để tìm file_raw_python
                    def find_key(obj, key):
                        if isinstance(obj, dict):
                            if key in obj:
                                return obj[key]
                            for k, v in obj.items():
                                result = find_key(v, key)
                                if result is not None:
                                    return result
                        elif isinstance(obj, list):
                            for item in obj:
                                result = find_key(item, key)
                                if result is not None:
                                    return result
                        return None
                    
                    file_raw_python = find_key(view_data, "file_raw_python")
                    
                    if file_raw_python:
                        # Lấy nội dung mã nguồn từ editor_content nếu có
                        if "editor_content" in file_raw_python:
                            source_code = file_raw_python["editor_content"]
                            source_code = source_code.replace("\\n", "\n")
                            print(f"{Fore.GREEN}[+] Đã trích xuất mã nguồn từ API!")
                            
                            if output_file:
                                try:
                                    # Đảm bảo thư mục đầu ra tồn tại
                                    output_dir = os.path.dirname(output_file)
                                    if output_dir and not os.path.exists(output_dir):
                                        os.makedirs(output_dir)
                                        
                                    with open(output_file, 'w', encoding='utf-8') as f:
                                        f.write(source_code)
                                    print(f"{Fore.GREEN}[+] Đã lưu kết quả vào: {output_file}")
                                    return True
                                except Exception as e:
                                    print(f"{Fore.RED}[!] Lưu file thất bại: {str(e)}")
                                    return False
                            return source_code
                else:
                    print(f"{Fore.RED}[!] API view_chimera trả về lỗi: {view_response.status_code}")
                    if attempt < max_retries:
                        print(f"{Fore.YELLOW}[!] {get_text('waiting_retry', attempt)}")
                        time.sleep(5)
                        continue
                    else:
                        print(f"{Fore.RED}[!] {get_text('max_retries')}")
            except Exception as e:
                print(f"{Fore.RED}[!] Lỗi khi xử lý phản hồi JSON: {str(e)}")
                if attempt < max_retries:
                    print(f"{Fore.YELLOW}[!] {get_text('waiting_retry', attempt)}")
                    time.sleep(5)
                    continue
                else:
                    print(f"{Fore.RED}[!] {get_text('max_retries')}")
            
            # Phương pháp dự phòng: Truy cập web URL và phân tích nội dung
            web_url = f"https://www.pylingual.io/view_chimera?identifier={identifier}"
            try:
                print(f"{Fore.CYAN}[+] Phương pháp dự phòng: Phân tích trang web HTML...")
                web_response = requests.get(web_url)
                
                if web_response.status_code == 200:
                    # Tìm mã nguồn trong script (var content = JSON.parse("..."))
                    match = re.search(r'var content = JSON\.parse\("(.+?)"\);', web_response.text)
                    if match:
                        try:
                            json_str = match.group(1).replace('\\"', '"').replace('\\\\', '\\')
                            content_data = json.loads(json_str)
                            
                            # Kiểm tra xem có file_raw_python không
                            if "file_raw_python" in content_data:
                                print(f"{Fore.GREEN}[+] Tìm thấy file_raw_python trong script JSON!")
                                
                                # Kiểm tra xem có editor_content không
                                if "editor_content" in content_data["file_raw_python"]:
                                    source_code = content_data["file_raw_python"]["editor_content"]
                                    source_code = source_code.replace("\\n", "\n")
                                    print(f"{Fore.GREEN}[+] Đã trích xuất mã nguồn từ script JSON!")
                                    
                                    if output_file:
                                        try:
                                            # Đảm bảo thư mục đầu ra tồn tại
                                            output_dir = os.path.dirname(output_file)
                                            if output_dir and not os.path.exists(output_dir):
                                                os.makedirs(output_dir)
                                                
                                            with open(output_file, 'w', encoding='utf-8') as f:
                                                f.write(source_code)
                                            print(f"{Fore.GREEN}[+] Đã lưu kết quả vào: {output_file}")
                                            return True
                                        except Exception as e:
                                            print(f"{Fore.RED}[!] Lưu file thất bại: {str(e)}")
                                            return False
                                    return source_code
                        except Exception as e:
                            print(f"{Fore.YELLOW}[!] Lỗi khi phân tích JSON từ script: {str(e)}")
                            if attempt < max_retries:
                                print(f"{Fore.YELLOW}[!] {get_text('waiting_retry', attempt)}")
                                time.sleep(5)
                                continue
                            else:
                                print(f"{Fore.RED}[!] {get_text('max_retries')}")
            except Exception as e:
                print(f"{Fore.YELLOW}[!] Lỗi khi xử lý trang web: {str(e)}")
                if attempt < max_retries:
                    print(f"{Fore.YELLOW}[!] {get_text('waiting_retry', attempt)}")
                    time.sleep(5)
                    continue
                else:
                    print(f"{Fore.RED}[!] {get_text('max_retries')}")
            
            # Nếu đến đây mà vẫn chưa return, có nghĩa là lần thử hiện tại thất bại
            if attempt < max_retries:
                print(f"{Fore.YELLOW}[!] {get_text('waiting_retry', attempt)}")
                time.sleep(5)
            else:
                print(f"{Fore.RED}[!] {get_text('max_retries')}")
                
        except Exception as e:
            print(f"{Fore.RED}[!] Error: {str(e)}")
            if attempt < max_retries:
                print(f"{Fore.YELLOW}[!] {get_text('waiting_retry', attempt)}")
                time.sleep(5)
            else:
                print(f"{Fore.RED}[!] {get_text('max_retries')}")
                return False
    
    # Nếu tất cả các lần thử đều thất bại
    return False

def find_main_file(directory):
    """Tìm các file có chứa từ 'main' trong tên"""
    main_files = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.lower().endswith('.pyc') and 'main' in file.lower():
                main_files.append(os.path.join(root, file))
    return main_files

def process_pyz_files_with_pylingual(pyz_dir, force=False, specific_files=None):
    """Chuyển đổi các file .pyc trong thư mục PYZ-00.pyz_extracted sử dụng PyLingual API"""
    if not os.path.exists(pyz_dir):
        print(f"{Fore.RED}[!] Thư mục không tồn tại: {pyz_dir}")
        return 0, 0
    
    success = 0
    failed = 0
    python_dir = pyz_dir + "_python"
    if not os.path.exists(python_dir):
        try:
            os.makedirs(python_dir)
        except Exception as e:
            print(f"{Fore.RED}[!] Không thể tạo thư mục đầu ra: {python_dir}")
            print(f"{Fore.RED}[!] Lỗi: {str(e)}")
            return 0, 0
    
    # Tìm file main trước
    main_files = find_main_file(pyz_dir)
    if main_files:
        print(f"{Fore.GREEN}[+] Tìm thấy {len(main_files)} file main:")
        for main_file in main_files:
            print(f"{Fore.CYAN}[+] {main_file}")
        
        # Giải mã các file main trước
        print(f"\n{Fore.YELLOW}[!] Bắt đầu giải mã các file main...")
        for main_path in main_files:
            rel_path = os.path.relpath(main_path, pyz_dir)
            output_path = os.path.join(python_dir, rel_path[:-4] + '.py')
            output_dir = os.path.dirname(output_path)
            
            if not os.path.exists(output_dir):
                try:
                    os.makedirs(output_dir)
                except Exception:
                    print(f"{Fore.RED}[!] Không thể tạo thư mục: {output_dir}")
                    failed += 1
                    continue
            
            if os.path.exists(output_path) and not force:
                print(f"{Fore.YELLOW}[!] File đã tồn tại, bỏ qua: {output_path}")
                continue
            
            print(f"{Fore.CYAN}[+] Đang giải mã file main: {main_path}")
            result = decompile_pyc_pylingual(main_path, output_path)
            
            if result:
                success += 1
                print(f"{Fore.GREEN}[+] {get_text('decompile_success', output_path)}")
            else:
                failed += 1
                print(f"{Fore.RED}[!] {get_text('decompile_failed', main_path)}")
            
            print(f"{Fore.CYAN}[+] {get_text('wait_between_files')}")
            time.sleep(5)
    
    # Tìm tất cả các file .pyc trong thư mục PYZ
    pyc_files = []
    for root, dirs, files in os.walk(pyz_dir):
        for file in files:
            if file.endswith('.pyc'):
                pyc_path = os.path.join(root, file)
                # Bỏ qua các file main đã xử lý
                if pyc_path not in main_files:
                    pyc_files.append(pyc_path)
    
    if not pyc_files:
        print(f"{Fore.YELLOW}[!] Không tìm thấy file .pyc nào khác trong thư mục {pyz_dir}")
        return success, failed
    
    # Nếu có danh sách file cụ thể, lọc ra các file cần xử lý
    if specific_files:
        filtered_files = []
        for pyc_path in pyc_files:
            rel_path = os.path.relpath(pyc_path, pyz_dir)
            if any(specific in rel_path for specific in specific_files):
                filtered_files.append(pyc_path)
        pyc_files = filtered_files
        if not pyc_files:
            print(f"{Fore.YELLOW}[!] Không tìm thấy file nào khớp với mẫu đã chỉ định")
            return success, failed
        print(f"{Fore.GREEN}[+] Tìm thấy {len(pyc_files)} file .pyc cần giải mã theo chỉ định")
    else:
        print(f"{Fore.GREEN}[+] Tìm thấy {len(pyc_files)} file .pyc khác cần giải mã")
    
    # Giải mã các file còn lại
    for pyc_path in tqdm(pyc_files, desc="Đang giải mã các file khác", ncols=80, leave=False, dynamic_ncols=True):
        rel_path = os.path.relpath(pyc_path, pyz_dir)
        output_path = os.path.join(python_dir, rel_path[:-4] + '.py')
        output_dir = os.path.dirname(output_path)
        
        if not os.path.exists(output_dir):
            try:
                os.makedirs(output_dir)
            except Exception:
                print(f"{Fore.RED}[!] Không thể tạo thư mục: {output_dir}")
                failed += 1
                continue
        
        if os.path.exists(output_path) and not force:
            print(f"{Fore.YELLOW}[!] File đã tồn tại, bỏ qua: {output_path}")
            continue
        
        print(f"{Fore.CYAN}[+] Đang giải mã: {pyc_path}")
        result = decompile_pyc_pylingual(pyc_path, output_path)
        
        if result:
            success += 1
            print(f"{Fore.GREEN}[+] {get_text('decompile_success', output_path)}")
        else:
            failed += 1
            print(f"{Fore.RED}[!] {get_text('decompile_failed', pyc_path)}")
        
        print(f"{Fore.CYAN}[+] {get_text('wait_between_files')}")
        time.sleep(5)
    
    return success, failed

def find_all_pyc_directories(directory):
    """Tìm các thư mục con trực tiếp chứa file .pyc"""
    pyc_dirs = []
    # Chỉ xem xét các thư mục con trực tiếp
    for item in os.listdir(directory):
        item_path = os.path.join(directory, item)
        if os.path.isdir(item_path):
            # Kiểm tra xem thư mục con có chứa file .pyc không
            has_pyc = any(file.endswith('.pyc') for file in os.listdir(item_path))
            if has_pyc:
                pyc_dirs.append(item_path)
    return pyc_dirs

def py_to_pyc(py_file, output_file=None, force=False):
    """Chuyển đổi file .py sang .pyc"""
    if not os.path.exists(py_file):
        print(f"{Fore.RED}[!] {get_text('file_not_exist', py_file)}")
        return False
    
    if not py_file.endswith('.py'):
        print(f"{Fore.YELLOW}[!] Cảnh báo: File '{py_file}' không có phần mở rộng .py")
    
    if output_file is None:
        output_file = py_file + 'c'  # Thêm 'c' để tạo .pyc
    
    if os.path.exists(output_file) and not force:
        print(f"{Fore.RED}[!] Lỗi: File đầu ra '{output_file}' đã tồn tại. Sử dụng --force để ghi đè.")
        return False
    
    try:
        # Tạo thư mục đầu ra nếu chưa tồn tại
        output_dir = os.path.dirname(output_file)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        # Dùng py_compile để biên dịch file .py thành .pyc
        import py_compile
        py_compile.compile(py_file, output_file)
        print(f"{Fore.GREEN}[+] Chuyển đổi thành công '{py_file}' sang '{output_file}'")
        return True
    except Exception as e:
        print(f"{Fore.RED}[!] Lỗi khi biên dịch '{py_file}': {str(e)}")
        traceback.print_exc()
        return False

def convert_multiple_files(file_paths, converter_func, output_dir, force=False):
    """Chuyển đổi nhiều file cùng lúc"""
    success = 0
    failed = 0
    
    # Tạo thư mục đầu ra nếu chưa tồn tại
    if not os.path.exists(output_dir):
        try:
            os.makedirs(output_dir)
        except Exception as e:
            print(f"{Fore.RED}[!] Không thể tạo thư mục đầu ra: {output_dir}")
            print(f"{Fore.RED}[!] Lỗi: {str(e)}")
            return 0, 0
    
    for path in file_paths:
        path = path.strip()
        if not path:
            continue
        
        if not os.path.exists(path):
            print(f"{Fore.RED}[!] {get_text('file_not_exist', path)}")
            failed += 1
            continue
        
        file_name = os.path.basename(path)
        
        # Xác định phần mở rộng đầu ra dựa trên loại chuyển đổi
        if converter_func == pyc_to_py:
            output_file = os.path.join(output_dir, file_name[:-4] + '.py' if file_name.endswith('.pyc') else file_name + '.py')
        elif converter_func == py_to_pyc:
            output_file = os.path.join(output_dir, file_name + 'c' if not file_name.endswith('.pyc') else file_name)
        
        if converter_func(path, output_file, force):
            success += 1
        else:
            failed += 1
    
    return success, failed

def print_converter_menu():
    """Hiển thị menu chuyển đổi Python"""
    menu = f"""
{Fore.CYAN}╔════════════════════════════════════════════════════════════╗
{Fore.CYAN}║  {Fore.GREEN}{get_text('convert_py_title')}                                  {Fore.CYAN}
{Fore.CYAN}╠════════════════════════════════════════════════════════════╣
{Fore.CYAN}║                                                            ║
{Fore.CYAN}║  {Fore.YELLOW}{get_text('convert_option_1')}                                      
{Fore.CYAN}║  {Fore.YELLOW}{get_text('convert_option_2')}                                      
{Fore.CYAN}║  {Fore.YELLOW}{get_text('convert_option_back')}                                     
{Fore.CYAN}║                                                            ║
{Fore.CYAN}╚════════════════════════════════════════════════════════════╝
"""
    print(menu)

def process_python_conversion():
    """Xử lý chuyển đổi file Python"""
    clear_screen()
    print_banner()
    print(f"\n{Fore.CYAN}╔════════════════════════════════════════════════════════════╗")
    print(f"{Fore.CYAN}║  {Fore.GREEN}{get_text('convert_py_title')}                                  {Fore.CYAN}║")
    print(f"{Fore.CYAN}╚════════════════════════════════════════════════════════════╝")
    
    print(f"\n{Fore.YELLOW}[!] {get_text('convert_option_1')}")
    print(f"{Fore.YELLOW}[!] {get_text('convert_option_2')}")
    
    while True:
        converter_choice = input(f"\n{Fore.CYAN}[?] Chọn chế độ chuyển đổi (1-2): ").strip()
        if converter_choice in ("1", "2"):
            break
        print(f"{Fore.RED}[!] {get_text('invalid_mode')}")
    
    # Tạo thư mục đầu ra với thời gian hiện tại
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    output_dir = os.path.join(os.getcwd(), f"py2thon-{timestamp}")
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    print(f"\n{Fore.GREEN}[+] {get_text('output_dir', output_dir)}")
    
    # Nhập đường dẫn file
    paths_input = input(f"\n{Fore.CYAN}[?] {get_text('enter_paths')} ").strip()
    if not paths_input:
        print(f"{Fore.RED}[!] {get_text('no_valid_files')}")
        input(f"\n{Fore.CYAN}[?] {get_text('press_enter')}")
        return
    
    # Tách các đường dẫn
    file_paths = [p.strip() for p in paths_input.split(",")]
    
    # Kiểm tra các file tồn tại
    valid_files = []
    for path in file_paths:
        if not os.path.exists(path):
            print(f"{Fore.RED}[!] {get_text('file_not_exist', path)}")
        else:
            valid_files.append(path)
    
    if not valid_files:
        print(f"{Fore.RED}[!] {get_text('no_valid_files')}")
        input(f"\n{Fore.CYAN}[?] {get_text('press_enter')}")
        return
    
    print(f"\n{Fore.GREEN}[+] Tìm thấy {len(valid_files)} file hợp lệ để chuyển đổi")
    
    # Bắt đầu chuyển đổi
    print(f"\n{Fore.CYAN}[+] {get_text('converting')}")
    
    success = 0
    failed = 0
    
    # Nếu chọn chuyển .pyc sang .py, sử dụng API PyLingual.io
    if converter_choice == "1":
        print(f"{Fore.CYAN}[+] {get_text('decompile_note1')}")
        print(f"{Fore.CYAN}[+] {get_text('decompile_note2')}")
        
        try:
            # Kiểm tra kết nối Internet
            try:
                requests.get("https://www.pylingual.io", timeout=5)
                print(f"{Fore.GREEN}[+] {get_text('internet_ok')}")
                
                for path in tqdm(valid_files, desc="Đang giải mã", ncols=80, leave=False, dynamic_ncols=True):
                    file_name = os.path.basename(path)
                    output_file = os.path.join(output_dir, file_name[:-4] + '.py' if file_name.endswith('.pyc') else file_name + '.py')
                    
                    print(f"{Fore.CYAN}[+] Đang giải mã: {path}")
                    result = decompile_pyc_pylingual(path, output_file)
                    
                    if result:
                        success += 1
                        print(f"{Fore.GREEN}[+] {get_text('decompile_success', output_file)}")
                    else:
                        failed += 1
                        print(f"{Fore.RED}[!] {get_text('decompile_failed', path)}")
                    
                    # Thêm độ trễ giữa các file để tránh quá tải API
                    print(f"{Fore.CYAN}[+] {get_text('wait_between_files')}")
                    time.sleep(5)
                
            except requests.RequestException:
                print(f"{Fore.RED}[!] {get_text('internet_error')}")
                input(f"\n{Fore.CYAN}[?] {get_text('press_enter')}")
                return
        except ImportError:
            print(f"{Fore.RED}[!] {get_text('lib_error')}")
            print(f"{Fore.YELLOW}[!] {get_text('lib_install_guide')}")
            input(f"\n{Fore.CYAN}[?] {get_text('press_enter')}")
            return
    # Nếu chọn chuyển .py sang .pyc, sử dụng py_compile
    else:
        for path in tqdm(valid_files, desc="Đang biên dịch", ncols=80, leave=False, dynamic_ncols=True):
            file_name = os.path.basename(path)
            output_file = os.path.join(output_dir, file_name + 'c' if not file_name.endswith('.pyc') else file_name)
            
            print(f"{Fore.CYAN}[+] Đang biên dịch: {path}")
            if py_to_pyc(path, output_file, force=True):
                success += 1
                print(f"{Fore.GREEN}[+] {get_text('convert_success', output_file)}")
            else:
                failed += 1
                print(f"{Fore.RED}[!] {get_text('convert_failed', path)}")
    
    print(f"\n{Fore.GREEN}[+] Chuyển đổi hoàn tất:")
    print(f"{Fore.GREEN}[+] - {success} file thành công")
    print(f"{Fore.RED}[+] - {failed} file thất bại")
    print(f"{Fore.CYAN}[+] - Thư mục đầu ra: {output_dir}")
    
    input(f"\n{Fore.CYAN}[?] {get_text('press_enter')}")

def main():
    while True:
        clear_screen()
        print_banner()
        print_menu()
        
        choice = input(f"{Fore.CYAN}[?] {get_text('choose_option')} ").strip()
        
        if choice == "1":
            clear_screen()
            print_banner()
            # Xử lý file EXE
            parser = argparse.ArgumentParser(description='Chuyển đổi file EXE sang Python')
            parser.add_argument('-f', '--force', action='store_true', help='Ghi đè file đã tồn tại')
            parser.add_argument('-v', '--verbose', action='store_true', help='Hiển thị thông tin chi tiết')
            
            args = parser.parse_args()
            
            if args.verbose:
                print(f"{Fore.CYAN}[+] {get_text('verbose_on')}")
            else:
                sys.tracebacklimit = 0
            
            # Hỏi người dùng nhập đường dẫn file
            while True:
                input_file = input(f"{Fore.CYAN}[?] {get_text('enter_exe_path')} ").strip()
                if os.path.exists(input_file):
                    break
                print(f"{Fore.RED}[!] {get_text('file_not_found')}")
            
            print(f"{Fore.CYAN}[+] {get_text('processing_file')} {input_file}")
            
            # Bước 1: Trích xuất từ EXE
            arch = PyInstArchive(input_file)
            if arch.open():
                if arch.checkFile():
                    if arch.getCArchiveInfo():
                        arch.parseTOC()
                        extraction_dir = arch.extractFiles()
                        arch.close()
                        print(f"{Fore.GREEN}[+] Đã trích xuất thành công PyInstaller archive: {input_file}")
                        print(f"{Fore.GREEN}[+] Thư mục trích xuất: {extraction_dir}")
                        
                        # Kiểm tra nếu tồn tại thư mục PYZ
                        lib_dir = os.path.join(extraction_dir, 'PYZ-00.pyz_extracted')
                        has_lib_dir = os.path.isdir(lib_dir)
                        
                        # Hỏi người dùng có muốn thực hiện bước 2 không
                        print(f"\n{Fore.YELLOW}[!] {get_text('step2_title')}")
                        print(f"{Fore.YELLOW}[!] {get_text('step2_skip')}")
                        while True:
                            ans_step2 = input(f"{Fore.YELLOW}[?] {get_text('step2_question')} ").strip().lower()
                            if ans_step2 in ("y", "n"):
                                break
                            print(f"{Fore.RED}[!] Vui lòng nhập 'y' hoặc 'n'")
                        
                        if ans_step2 == "y":
                            print(f"{Fore.CYAN}[+] {get_text('starting_step2')}")
                            success, failed = process_directory_to_bytecode(extraction_dir, args.force)
                            print(f"\n{Fore.GREEN}[+] {get_text('step2_complete', success, failed)}")
                            print(f"{Fore.CYAN}[+] {get_text('step2_output_dir', extraction_dir + '_bytecode')}")
                            
                            # Hỏi tiếp có chuyển đổi thư viện không
                            if has_lib_dir:
                                print(f"\n{Fore.YELLOW}[!] {get_text('lib_dir_found', lib_dir)}")
                                while True:
                                    ans_lib = input(f"{Fore.YELLOW}[?] {get_text('convert_lib_question')} ").strip().lower()
                                    if ans_lib in ("y", "n"):
                                        break
                                    print(f"{Fore.RED}[!] Vui lòng nhập 'y' hoặc 'n'")
                                
                                if ans_lib == "y":
                                    print(f"{Fore.CYAN}[+] {get_text('starting_lib_convert')}")
                                    lib_success, lib_failed = process_flat_pyc_to_bytecode(lib_dir, args.force)
                                    print(f"\n{Fore.GREEN}[+] {get_text('lib_convert_complete', lib_success, lib_failed)}")
                                    print(f"{Fore.CYAN}[+] {get_text('lib_output_dir', lib_dir + '_bytecode')}")
                                else:
                                    print(f"{Fore.CYAN}[!] {get_text('skipped_lib_convert')}")
                            
                            # Hỏi có muốn thực hiện bước 3 không sau khi hoàn thành bước 2
                            print(f"\n{Fore.YELLOW}[!] {get_text('step3_title')}")
                            print(f"{Fore.YELLOW}[!] {get_text('step3_desc')}")
                            while True:
                                ans_step3 = input(f"{Fore.YELLOW}[?] {get_text('step3_question')} ").strip().lower()
                                if ans_step3 in ("y", "n"):
                                    break
                                print(f"{Fore.RED}[!] Vui lòng nhập 'y' hoặc 'n'")
                            
                            if ans_step3 == "y":
                                print(f"{Fore.CYAN}[+] {get_text('starting_decompile')}")
                                print(f"{Fore.YELLOW}[!] {get_text('decompile_note1')}")
                                print(f"{Fore.YELLOW}[!] {get_text('decompile_note2')}")
                                
                                try:
                                    # Kiểm tra kết nối Internet
                                    try:
                                        requests.get("https://www.pylingual.io", timeout=5)
                                        print(f"{Fore.GREEN}[+] {get_text('internet_ok')}")
                                        
                                        # Tìm tất cả các thư mục chứa file .pyc
                                        pyc_dirs = find_all_pyc_directories(extraction_dir)
                                        if not pyc_dirs:
                                            print(f"{Fore.YELLOW}[!] Không tìm thấy thư mục nào chứa file .pyc")
                                            input(f"\n{Fore.CYAN}[?] {get_text('press_enter')}")
                                            continue
                                        
                                        print(f"{Fore.GREEN}[+] Tìm thấy {len(pyc_dirs)} thư mục chứa file .pyc:")
                                        for i, dir_path in enumerate(pyc_dirs, 1):
                                            print(f"{Fore.CYAN}[{i}] {dir_path}")
                                        
                                        # Chọn chế độ giải mã
                                        print(f"\n{Fore.CYAN}[?] {get_text('step3_mode')}")
                                        print(f"{Fore.YELLOW}{get_text('step3_auto')}")
                                        print(f"{Fore.YELLOW}{get_text('step3_specific')}")
                                        
                                        while True:
                                            mode = input(f"{Fore.CYAN}[?] Chọn chế độ (1-2): ").strip()
                                            if mode in ("1", "2"):
                                                break
                                            print(f"{Fore.RED}[!] {get_text('invalid_mode')}")
                                        
                                        specific_files = None
                                        if mode == "2":
                                            patterns = input(f"{Fore.CYAN}[?] {get_text('enter_patterns')} ").strip()
                                            if patterns:
                                                specific_files = [p.strip() for p in patterns.split(",")]
                                        
                                        total_success = 0
                                        total_failed = 0
                                        
                                        # Xử lý từng thư mục
                                        for dir_path in pyc_dirs:
                                            print(f"\n{Fore.CYAN}[+] Đang xử lý thư mục: {dir_path}")
                                            
                                            # Tạo thư mục đầu ra cho Python
                                            python_dir = dir_path + "_python"
                                            if not os.path.exists(python_dir):
                                                os.makedirs(python_dir)
                                            
                                            # Bắt đầu giải mã
                                            py_success, py_failed = process_pyz_files_with_pylingual(dir_path, args.force, specific_files)
                                            total_success += py_success
                                            total_failed += py_failed
                                            
                                            print(f"{Fore.GREEN}[+] Đã xử lý xong thư mục: {dir_path}")
                                            print(f"{Fore.CYAN}[+] Kết quả: {py_success} thành công, {py_failed} thất bại")
                                        
                                        print(f"\n{Fore.GREEN}[+] Tổng kết quá trình giải mã:")
                                        print(f"{Fore.GREEN}[+] Tổng số file thành công: {total_success}")
                                        print(f"{Fore.RED}[+] Tổng số file thất bại: {total_failed}")
                                        
                                    except requests.RequestException:
                                        print(f"{Fore.RED}[!] {get_text('internet_error')}")
                                except ImportError:
                                    print(f"{Fore.RED}[!] {get_text('lib_error')}")
                                    print(f"{Fore.YELLOW}[!] {get_text('lib_install_guide')}")
                        else:
                            print(f"{Fore.CYAN}[!] {get_text('skipped_step2')}")
                        
                        input(f"\n{Fore.CYAN}[?] {get_text('press_enter')}")
                        continue
            
            print(f"{Fore.RED}[!] {get_text('processing_failed')}")
            input(f"\n{Fore.CYAN}[?] {get_text('press_enter')}")
            
        elif choice == "2":
            clear_screen()
            print_banner()
            print_intro()
            input(f"\n{Fore.CYAN}[?] {get_text('press_enter')}")
            
        elif choice == "3":
            clear_screen()
            print_banner()
            print(f"\n{Fore.GREEN}[+] {get_text('thank_you')}")
            break
            
        elif choice == "4":
            clear_screen()
            print_banner()
            print(f"\n{Fore.CYAN}[?] {get_text('select_language')}")
            print(f"{Fore.YELLOW}[1] Tiếng Việt")
            print(f"{Fore.YELLOW}[2] English")
            while True:
                lang_choice = input(f"{Fore.CYAN}[?] Choice / Lựa chọn (1-2): ").strip()
                if lang_choice in ("1", "2"):
                    break
                print(f"{Fore.RED}[!] Vui lòng nhập 1 hoặc 2")
            
            if lang_choice == "1":
                set_language('vi')
            elif lang_choice == "2":
                set_language('en')
            continue
            
        elif choice == "5":
            # Xử lý chuyển đổi Python
            process_python_conversion()
            continue
            
        else:
            print(f"{Fore.RED}[!] {get_text('invalid_choice')}")
            input(f"\n{Fore.CYAN}[?] {get_text('press_enter')}")

if __name__ == '__main__':
    main() 