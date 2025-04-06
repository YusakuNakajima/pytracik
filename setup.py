# -*- coding: utf-8 -*-
"""
Author: Hao Chen (chen960216@gmail.com)
Created: 20230911osaka
Modified for Ubuntu with apt dependencies: [Your Name or AI Assistant] [20250406]
"""

import os
import sys
import fnmatch
from setuptools import setup, find_packages
import pybind11
from pybind11.setup_helpers import Pybind11Extension, build_ext

def find_files(path, file_extension, visited=None, found_files=None):
    """指定されたパス以下から特定の拡張子を持つファイルを再帰的に検索します。"""
    if found_files is None:
        found_files = []
    if visited is None:
        visited = set()

    try:
        real_path = os.path.realpath(path)
    except OSError as e:
        print(f"警告: パス '{path}' の解決中にエラー: {e}", file=sys.stderr)
        return found_files

    if real_path in visited:
        return found_files
    visited.add(real_path)

    if os.path.isfile(real_path):
        if fnmatch.fnmatch(os.path.basename(real_path), '*' + file_extension):
            rel_path = os.path.relpath(real_path, start=os.path.dirname(__file__))
            found_files.append(rel_path)
        return found_files

    if os.path.isdir(real_path):
        try:
            for item in os.listdir(real_path):
                item_path = os.path.join(real_path, item)
                if os.path.exists(item_path):
                    find_files(item_path, file_extension, visited, found_files)
        except OSError as e:
            print(f"警告: ディレクトリ '{real_path}' の読み込み中にエラー: {e}", file=sys.stderr)

    return found_files

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

    # バージョンファイル読み込み
    version_file = os.path.join(os.path.dirname(__file__), "pytracik", "version.py")
    version = "0.0.1"
    if os.path.exists(version_file):
        version_globals = {}
        try:
            with open(version_file, 'r', encoding='utf-8') as f:
                exec(f.read(), version_globals)
            version = version_globals.get('__version__', version)
            if version == "0.0.1" and '__version__' not in version_globals:
                print(f"警告: {version_file} に __version__ が定義されていません。", file=sys.stderr)
        except Exception as e:
            print(f"警告: {version_file} の読み込み中にエラーが発生しました: {e}", file=sys.stderr)
    else:
        print(f"警告: {version_file} が見つかりません。デフォルトバージョン '{version}' を使用します。", file=sys.stderr)

    module_name = "pytracik._pytracik"
    src_dir = os.path.join(".", "src")
    src_files = []
    for ext in ['.cpp', '.cxx', '.cc']:
        src_files.extend(find_files(src_dir, ext))

    if not src_files:
        print(f"エラー: '{src_dir}' 内に C++ ソースファイル (.cpp, .cxx, .cc) が見つかりません。", file=sys.stderr)
        sys.exit(1)

    # --- Ubuntu 用の設定 (apt で依存関係をインストールした場合) ---
    include_dirs = [
        pybind11.get_include(),  # pybind11 のヘッダーパス
        src_dir,                 # プロジェクト自身のソース/ヘッダーディレクトリ
        '/usr/include/eigen3'    # Eigen の標準ヘッダーパス
    ]

    libraries = [
        'nlopt',           # libnlopt-dev が提供
        'orocos-kdl',      # liborocos-kdl-dev が提供（要確認）
        'boost_date_time', # libboost-date-time-dev が提供
        # 他に必要なライブラリがあれば追加
    ]

    library_dirs = []  # 通常、システム標準のため指定不要

    extra_compile_args = [
        '-std=c++17',
        '-fPIC',
        '-O3',
        '-Wall',
        '-Wextra',
        '-Wno-unused-parameter',
    ]

    extra_link_args = []  # 必要に応じて追加

    trac_ik_module = [
        Pybind11Extension(
            module_name,
            sorted(list(set(src_files))),
            include_dirs=include_dirs,
            libraries=libraries,
            library_dirs=library_dirs,
            language='c++',
            extra_compile_args=extra_compile_args,
            extra_link_args=extra_link_args,
        ),
    ]

    setup(
        name="pytracik",
        version=version,
        description="TracIK Python Bindings",
        author="Hao Chen",
        author_email="chen960216@gmail.com",
        license="MIT Software License",
        url="https://github.com/chenhaox/pytracik",
        keywords="robotics inverse kinematics kdl trac-ik",
        packages=find_packages(),  # 自動検出（必要に応じて include/exclude を調整）
        include_package_data=True,
        cmdclass={"build_ext": build_ext},
        ext_modules=trac_ik_module,
        install_requires=requirements_from_file('requirements.txt'),
        python_requires='>=3.9',
        zip_safe=False,
    )