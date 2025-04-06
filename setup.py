# -*- coding: utf-8 -*-
"""

Author: Hao Chen (chen960216@gmail.com)
Created: 20230911osaka
Modified for Ubuntu with apt dependencies: [Your Name or AI Assistant] [Current Date, e.g., 20250406]

"""
import os
import sys
import fnmatch
from setuptools import setup, Extension
import pybind11
from pybind11.setup_helpers import Pybind11Extension, build_ext

# find_files 関数 (変更なし)
def find_files(path, file_extension, visited=None, finded_files=None):
    """指定されたパス以下から特定の拡張子を持つファイルを再帰的に検索します。"""
    if finded_files is None:
        finded_files = []
    if visited is None:
        visited = set()

    try:
        path_real = os.path.realpath(path)
    except OSError as e:
        print(f"警告: パス '{path}' の解決中にエラー: {e}", file=sys.stderr)
        return finded_files

    if path_real in visited:
        return finded_files
    visited.add(path_real)

    if os.path.isfile(path):
        if fnmatch.fnmatch(os.path.basename(path), '*' + file_extension):
            finded_files.append(path)
        return finded_files

    if os.path.isdir(path):
        try:
            for item in os.listdir(path):
                item_path = os.path.join(path, item)
                if os.path.exists(item_path):
                    find_files(item_path, file_extension, visited, finded_files)
        except OSError as e:
             print(f"警告: ディレクトリ '{path}' の読み込み中にエラー: {e}", file=sys.stderr)

    return finded_files

# requirements_from_file 関数 (変更なし)
def requirements_from_file(file_name):
    """requirements.txtから依存関係を読み込みます。"""
    if not os.path.exists(file_name):
        print(f"警告: {file_name} が見つかりません。依存関係なしで進めます。", file=sys.stderr)
        return []
    try:
        with open(file_name, 'r', encoding='utf-8') as f:
            return [line.strip() for line in f if line.strip() and not line.startswith('#')]
    except Exception as e:
        print(f"警告: {file_name} の読み込み中にエラー: {e}", file=sys.stderr)
        return []


if __name__ == '__main__':

    # バージョンファイル読み込み (変更なし)
    version_file = os.path.join(os.path.dirname(__file__), "trac_ik", "version.py")
    version = "0.0.1"
    if os.path.exists(version_file):
        version_globals = {}
        try:
            with open(version_file, 'r', encoding='utf-8') as f:
                exec(f.read(), version_globals)
            version = version_globals.get('__version__', version)
            if version == "0.0.1" and '__version__' not in version_globals:
                 print(f"警告: {version_file} で __version__ が定義されていません。", file=sys.stderr)
        except Exception as e:
            print(f"警告: {version_file} の読み込み中にエラーが発生しました: {e}", file=sys.stderr)
    else:
        print(f"警告: {version_file} が見つかりません。デフォルトバージョン '{version}' を使用します。", file=sys.stderr)

    module_name = "pytracik"
    src_dir = os.path.join(".", "src")
    src_files = []
    for ext in ['.cpp', '.cxx', '.cc']:
        src_files.extend(find_files(src_dir, ext))

    if not src_files:
        print(f"エラー: '{src_dir}' 内に C++ ソースファイル (.cpp, .cxx, .cc) が見つかりません。", file=sys.stderr)
        sys.exit(1)

    # --- Ubuntu 用の設定 (apt で依存関係をインストールした場合) ---

    # aptでインストールした場合、システムの標準パスが使われるため、
    # Eigen, KDL, NLopt, Boost のヘッダパス指定は通常不要。
    include_dirs = [
        pybind11.get_include(), # pybind11 のヘッダーパスは必要
        src_dir,                 # プロジェクト自身のソース/ヘッダーディレクトリ
        '/usr/include/eigen3' # Eigenのヘッダーパス 

    ]

    # aptでインストールした場合、システムの標準パスにあるライブラリを使うため、
    # ライブラリ名を指定する。'-l' オプションに対応する名前 (lib<name>.so -> <name>)
    # KDLは orocos-kdl パッケージに含まれるライブラリ名を確認してください
    # (通常は orocos-kdl だが、バージョンによって変わる可能性もゼロではない)
    # Boostは必要なコンポーネントを指定 (例: date_time, system)
    libraries = [
        'nlopt',        # libnlopt-dev が提供
        'orocos-kdl',   # liborocos-kdl-dev が提供 (要確認)
        'boost_date_time', # libboost-date-time-dev が提供
        # 他に C++ コード内で Boost::System などを使っていれば追加
        # 'boost_system',
    ]

    # aptでインストールした場合、システムの標準ライブラリパス (/usr/lib など) が
    # 自動で検索されるため、library_dirs の指定は通常不要。
    library_dirs = []

    # コンパイルオプション (変更なし)
    extra_compile_args = [
        '-std=c++17',
        '-fPIC',
        '-O3',
        '-Wall',
        '-Wextra',
        '-Wno-unused-parameter',
        # Eigenのための最適化フラグ (任意)
        # '-march=native', # 実行するマシンに最適化 (配布用には注意)
        # '-mavx',        # AVX命令セットを利用 (CPUが対応している場合)
    ]

    # リンクオプション (変更なし)
    extra_link_args = []

    # Extension オブジェクト (変更なし)
    trac_ik_module = [
        Pybind11Extension(
            module_name,
            sorted(list(set(src_files))),
            include_dirs=include_dirs,
            libraries=libraries,
            library_dirs=library_dirs, # 空リストを渡す
            language='c++',
            extra_compile_args=extra_compile_args,
            extra_link_args=extra_link_args,
        ),
    ]

    # setup() 関数 (変更なし)
    setup(
        name="pytracik",
        version=version,
        description="TracIK Python Bindings",
        author="Hao Chen",
        author_email="chen960216@gmail.com",
        license="MIT Software License",
        url="https://github.com/chenhaox/pytracik",
        keywords="robotics inverse kinematics kdl trac-ik",
        packages=['trac_ik'],
        include_package_data=True,
        # platforms=['Linux', 'Unix'], # 必要なら
        cmdclass={"build_ext": build_ext},
        ext_modules=trac_ik_module,
        install_requires=requirements_from_file('requirements.txt'),
        python_requires='>=3.9',
        zip_safe=False,
    )