# EXE2PY - Công cụ chuyển đổi file EXE sang Python
# EXE2PY - EXE to Python Conversion Tool

[![Python Version](https://img.shields.io/badge/python-3.6%2B-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Author](https://img.shields.io/badge/author-HiepZ8-orange.svg)](https://github.com/hiep-py)

## 🇻🇳 Tiếng Việt

### Giới thiệu
EXE2PY là một công cụ mạnh mẽ được thiết kế để trích xuất và phân tích các file EXE được tạo bởi PyInstaller. Công cụ này giúp bạn chuyển đổi các file thực thi (.exe) thành mã Python có thể đọc được.

### Tính năng chính
- 🔍 Trích xuất file từ EXE (PyInstaller archive)
- 🔄 Chuyển đổi file .pyc sang bytecode (.txt)
- 🌐 Hỗ trợ nhiều phiên bản Python (2.0 - 3.13)
- 🔧 Tự động phát hiện phiên bản PyInstaller
- 🌈 Giao diện console đẹp mắt với màu sắc
- 🌍 Hỗ trợ đa ngôn ngữ (Tiếng Việt và Tiếng Anh)

### Cài đặt
```bash
# Clone repository
git clone https://github.com/hiep-py/exe2py.git

# Di chuyển vào thư mục dự án
cd exe2py

# Cài đặt các thư viện cần thiết
pip install -r requirements.txt
```

### Cách sử dụng
1. Chạy chương trình:
```bash
python exe2py.py
```

2. Chọn chức năng từ menu:
   - Bắt đầu phân tích file EXE
   - Xem thông tin về công cụ
   - Thoát
   - Thay đổi ngôn ngữ

3. Nhập đường dẫn file EXE cần chuyển đổi

4. Chọn có/không thực hiện chuyển đổi bytecode

5. Chọn có/không chuyển đổi thư viện

### Lưu ý
- File EXE phải được tạo bởi PyInstaller
- Có thể bỏ qua bước chuyển đổi bytecode
- Kết quả được lưu trong thư mục riêng

## 🇬🇧 English

### Introduction
EXE2PY is a powerful tool designed to extract and analyze EXE files created by PyInstaller. This tool helps you convert executable (.exe) files into readable Python code.

### Key Features
- 🔍 Extract files from EXE (PyInstaller archive)
- 🔄 Convert .pyc files to bytecode (.txt)
- 🌐 Support multiple Python versions (2.0 - 3.13)
- 🔧 Auto-detect PyInstaller version
- 🌈 Beautiful colored console interface
- 🌍 Multi-language support (Vietnamese and English)

### Installation
```bash
# Clone repository
git clone https://github.com/hiep-py/exe2py.git

# Move to project directory
cd exe2py

# Install required libraries
pip install -r requirements.txt
```

### Usage
1. Run the program:
```bash
python exe2py.py
```

2. Choose function from menu:
   - Start analyzing EXE file
   - View tool information
   - Exit
   - Change language

3. Enter the path of EXE file to convert

4. Choose whether to perform bytecode conversion

5. Choose whether to convert libraries

### Notes
- EXE file must be created by PyInstaller
- Can skip bytecode conversion step
- Results are saved in separate directory

## 📝 License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👨‍💻 Author
- **Hồ Hiệp (HiepZ8)**
  - GitHub: [hiep-py](https://github.com/hiep-py)
  - TikTok: [@hiepz8py](https://www.tiktok.com/@hiepz8py)
  - YouTube: [@Hohiep-db2vx](https://www.youtube.com/@Hohiep-db2vx)

## ⭐ Support
If you find this tool helpful, please give it a star on GitHub! 