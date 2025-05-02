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

# Khởi tạo colorama
init(autoreset=True)

# Định nghĩa các chuỗi ngôn ngữ
LANGUAGES = {
    'vi': {
        'title': 'GIỚI THIỆU CÔNG CỤ EXE2PY',
        'menu_title': 'MENU CHÍNH',
        'start_analysis': 'Bắt đầu phân tích file EXE',
        'view_info': 'Xem thông tin về công cụ',
        'exit': 'Thoát',
        'choose_option': 'Chọn chức năng (1-3):',
        'enter_exe_path': 'Nhập đường dẫn file EXE cần chuyển đổi:',
        'file_not_found': 'Lỗi: File không tồn tại. Vui lòng thử lại.',
        'processing_file': 'Bắt đầu xử lý file:',
        'extraction_success': 'Đã trích xuất thành công PyInstaller archive:',
        'extraction_dir': 'Thư mục trích xuất:',
        'step2_title': 'Bước 2: Chuyển đổi file .pyc sang bytecode (.txt)',
        'step2_skip': 'Bạn có thể bỏ qua bước này nếu chỉ cần trích xuất file.',
        'perform_step2': 'Bạn có muốn thực hiện bước 2 không? (y/n):',
        'invalid_input': 'Vui lòng nhập y hoặc n',
        'converting_pyc': 'Bắt đầu chuyển đổi file .pyc sang bytecode...',
        'conversion_complete': 'Hoàn thành chuyển đổi bytecode: {} thành công, {} thất bại.',
        'bytecode_dir': 'Các file bytecode đã được lưu trong thư mục:',
        'lib_dir_detected': 'Phát hiện thư mục thư viện:',
        'convert_lib': 'Bạn có muốn chuyển đổi các file .pyc trong thư mục thư viện không? (y/n):',
        'converting_lib': 'Bắt đầu chuyển đổi thư viện...',
        'lib_conversion_complete': 'Hoàn thành chuyển đổi thư viện: {} thành công, {} thất bại.',
        'lib_bytecode_dir': 'Các file bytecode thư viện đã được lưu trong thư mục:',
        'skip_lib': 'Đã bỏ qua chuyển đổi thư viện.',
        'skip_step2': 'Đã bỏ qua bước 2 - Chuyển đổi bytecode.',
        'press_enter': 'Nhấn Enter để tiếp tục...',
        'processing_failed': 'Quá trình xử lý thất bại',
        'thank_you': 'Cảm ơn bạn đã sử dụng exe2py!',
        'invalid_choice': 'Lựa chọn không hợp lệ. Vui lòng chọn lại.',
        'intro': {
            'title': 'GIỚI THIỆU CÔNG CỤ EXE2PY',
            'description': 'Công cụ trích xuất và phân tích file EXE được tạo bởi PyInstaller(free).',
            'features': 'Tính năng chính:',
            'feature1': '• Trích xuất file từ EXE (PyInstaller archive)',
            'feature2': '• Chuyển đổi file .pyc sang bytecode (.txt)',
            'feature3': '• Hỗ trợ nhiều phiên bản Python (2.0 - 3.13)',
            'feature4': '• Tự động phát hiện phiên bản PyInstaller',
            'usage': 'Cách sử dụng:',
            'step1': '1. Nhập đường dẫn file EXE cần phân tích',
            'step2': '2. Chọn có/không thực hiện chuyển đổi bytecode',
            'step3': '3. Chọn có/không chuyển đổi thư viện',
            'notes': 'Lưu ý:',
            'note1': '• File EXE phải được tạo bởi PyInstaller',
            'note2': '• Có thể bỏ qua bước chuyển đổi bytecode',
            'note3': '• Kết quả được lưu trong thư mục riêng'
        }
    },
    'en': {
        'title': 'EXE2PY TOOL INTRODUCTION',
        'menu_title': 'MAIN MENU',
        'start_analysis': 'Start analyzing EXE file',
        'view_info': 'View tool information',
        'exit': 'Exit',
        'choose_option': 'Choose function (1-3):',
        'enter_exe_path': 'Enter EXE file path to convert:',
        'file_not_found': 'Error: File does not exist. Please try again.',
        'processing_file': 'Starting to process file:',
        'extraction_success': 'Successfully extracted PyInstaller archive:',
        'extraction_dir': 'Extraction directory:',
        'step2_title': 'Step 2: Convert .pyc files to bytecode (.txt)',
        'step2_skip': 'You can skip this step if you only need to extract files.',
        'perform_step2': 'Do you want to perform step 2? (y/n):',
        'invalid_input': 'Please enter y or n',
        'converting_pyc': 'Starting to convert .pyc files to bytecode...',
        'conversion_complete': 'Bytecode conversion completed: {} successful, {} failed.',
        'bytecode_dir': 'Bytecode files have been saved in directory:',
        'lib_dir_detected': 'Library directory detected:',
        'convert_lib': 'Do you want to convert .pyc files in the library directory? (y/n):',
        'converting_lib': 'Starting to convert library...',
        'lib_conversion_complete': 'Library conversion completed: {} successful, {} failed.',
        'lib_bytecode_dir': 'Library bytecode files have been saved in directory:',
        'skip_lib': 'Skipped library conversion.',
        'skip_step2': 'Skipped step 2 - Bytecode conversion.',
        'press_enter': 'Press Enter to continue...',
        'processing_failed': 'Processing failed',
        'thank_you': 'Thank you for using exe2py!',
        'invalid_choice': 'Invalid choice. Please choose again.',
        'intro': {
            'title': 'EXE2PY TOOL INTRODUCTION',
            'description': 'Tool for extracting and analyzing EXE files created by PyInstaller(free).',
            'features': 'Main features:',
            'feature1': '• Extract files from EXE (PyInstaller archive)',
            'feature2': '• Convert .pyc files to bytecode (.txt)',
            'feature3': '• Support multiple Python versions (2.0 - 3.13)',
            'feature4': '• Auto-detect PyInstaller version',
            'usage': 'How to use:',
            'step1': '1. Enter the EXE file path to analyze',
            'step2': '2. Choose whether to perform bytecode conversion',
            'step3': '3. Choose whether to convert libraries',
            'notes': 'Notes:',
            'note1': '• EXE file must be created by PyInstaller',
            'note2': '• Can skip bytecode conversion step',
            'note3': '• Results are saved in separate directory'
        }
    }
}

# Mặc định sử dụng tiếng Việt
current_language = 'vi'

def set_language(lang):
    """Set the current language"""
    global current_language
    if lang in LANGUAGES:
        current_language = lang
    else:
        current_language = 'vi'  # Default to Vietnamese if language not supported

def get_text(key):
    """Get text in current language"""
    if key in LANGUAGES[current_language]:
        return LANGUAGES[current_language][key]
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
{Fore.CYAN}║  {Fore.GREEN}exe2py(beta mode) v1.0                                               
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
{Fore.CYAN}║  {Fore.GREEN}{get_text('intro.title')}                        {Fore.CYAN}
{Fore.CYAN}╠════════════════════════════════════════════════════════════╣
{Fore.CYAN}║                                                            ║
{Fore.CYAN}║  {Fore.YELLOW}[+] {get_text('intro.description')}    
{Fore.CYAN}║                                                            
{Fore.CYAN}║  {Fore.YELLOW}[+] {get_text('intro.features')}                                    
{Fore.CYAN}║     {get_text('intro.feature1')}        
{Fore.CYAN}║     {get_text('intro.feature2')}           
{Fore.CYAN}║     {get_text('intro.feature3')}          
{Fore.CYAN}║     {get_text('intro.feature4')}             
{Fore.CYAN}║                                                            
{Fore.CYAN}║  {Fore.YELLOW}[+] {get_text('intro.usage')}                                      
{Fore.CYAN}║     {get_text('intro.step1')}              
{Fore.CYAN}║     {get_text('intro.step2')}        
{Fore.CYAN}║     {get_text('intro.step3')}                  
{Fore.CYAN}║                                                            
{Fore.CYAN}║  {Fore.YELLOW}[+] {get_text('intro.notes')}                                            
{Fore.CYAN}║     {get_text('intro.note1')}              
{Fore.CYAN}║     {get_text('intro.note2')}              
{Fore.CYAN}║     {get_text('intro.note3')}                
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
{Fore.CYAN}║  {Fore.YELLOW}[1] {get_text('start_analysis')}                        
{Fore.CYAN}║  {Fore.YELLOW}[2] {get_text('view_info')}                          
{Fore.CYAN}║  {Fore.YELLOW}[3] {get_text('exit')}                                            
{Fore.CYAN}║  {Fore.YELLOW}[4] {get_text('change_language')}                                            
{Fore.CYAN}║                                                            ║
{Fore.CYAN}╚════════════════════════════════════════════════════════════╝
"""
    print(menu)

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
            parser = argparse.ArgumentParser(description='Convert EXE files to Python')
            parser.add_argument('-f', '--force', action='store_true', help='Overwrite existing files')
            parser.add_argument('-v', '--verbose', action='store_true', help='Show detailed information')
            
            args = parser.parse_args()
            
            if args.verbose:
                print(f"{Fore.CYAN}[+] Verbose mode enabled - will show detailed information")
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
                        print(f"{Fore.GREEN}[+] {get_text('extraction_success')} {input_file}")
                        print(f"{Fore.GREEN}[+] {get_text('extraction_dir')} {extraction_dir}")
                        
                        # Hỏi người dùng có muốn thực hiện bước 2 không
                        print(f"\n{Fore.YELLOW}[!] {get_text('step2_title')}")
                        print(f"{Fore.YELLOW}[!] {get_text('step2_skip')}")
                        while True:
                            ans = input(f"{Fore.YELLOW}[?] {get_text('perform_step2')} ").strip().lower()
                            if ans in ("y", "n"):
                                break
                            print(f"{Fore.RED}[!] {get_text('invalid_input')}")
                        
                        if ans == "y":
                            print(f"{Fore.CYAN}[+] {get_text('converting_pyc')}")
                            success, failed = process_directory_to_bytecode(extraction_dir, args.force)
                            print(f"\n{Fore.GREEN}[+] {get_text('conversion_complete').format(success, failed)}")
                            print(f"{Fore.CYAN}[+] {get_text('bytecode_dir')} {extraction_dir}_bytecode")
                            
                            # Hỏi tiếp có chuyển đổi thư viện không
                            lib_dir = os.path.join(extraction_dir, 'PYZ-00.pyz_extracted')
                            if os.path.isdir(lib_dir):
                                print(f"\n{Fore.YELLOW}[!] {get_text('lib_dir_detected')} {lib_dir}")
                                while True:
                                    ans_lib = input(f"{Fore.YELLOW}[?] {get_text('convert_lib')} ").strip().lower()
                                    if ans_lib in ("y", "n"):
                                        break
                                    print(f"{Fore.RED}[!] {get_text('invalid_input')}")
                                
                                if ans_lib == "y":
                                    print(f"{Fore.CYAN}[+] {get_text('converting_lib')}")
                                    lib_success, lib_failed = process_flat_pyc_to_bytecode(lib_dir, args.force)
                                    print(f"\n{Fore.GREEN}[+] {get_text('lib_conversion_complete').format(lib_success, lib_failed)}")
                                    print(f"{Fore.CYAN}[+] {get_text('lib_bytecode_dir')} {lib_dir}_bytecode")
                                else:
                                    print(f"{Fore.CYAN}[!] {get_text('skip_lib')}")
                        else:
                            print(f"{Fore.CYAN}[!] {get_text('skip_step2')}")
                        
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
            print(f"\n{Fore.CYAN}[?] Select language / Chọn ngôn ngữ:")
            print(f"{Fore.YELLOW}[1] Tiếng Việt")
            print(f"{Fore.YELLOW}[2] English")
            lang_choice = input(f"{Fore.CYAN}[?] Choice / Lựa chọn (1-2): ").strip()
            if lang_choice == "1":
                set_language('vi')
            elif lang_choice == "2":
                set_language('en')
            continue
            
        else:
            print(f"{Fore.RED}[!] {get_text('invalid_choice')}")
            input(f"\n{Fore.CYAN}[?] {get_text('press_enter')}")

if __name__ == '__main__':
    main() 