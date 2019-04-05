import subprocess
import platform


filesystems = [
    'Squashfs', 'JFFS2'
]

filesystem_roots = {
    'Squashfs': 'squashfs-root',
    'JFFS2': 'jffs2-root'
}


def binwalk_get_fw_info(file_name, path):
    result = binwalk(path, '')
    if result == '':
        raise OSError('binwalk runs failed.')
    fw_filesystem = get_filesystem(result)
    fw_info = {
        'fw_name': file_name,
        'fw_path': path,
        'fw_filesystem': fw_filesystem
    }
    return fw_info


def binwalk_get_fw_root_directory(fw_info):
    global filesystem_roots
    result = binwalk(fw_info['fw_path'], '-Me')
    if result == '':
        raise OSError('binwalk runs failed.')
    binwalk_base_dir = fw_info['fw_path'].replace(fw_info['fw_name'], '_'+fw_info['fw_name']) + '.extracted'
    fw_filesystem = fw_info['fw_filesystem']
    if platform.system() == 'Windows':
        path_fix = '\\'
    else:
        path_fix = '/'
    return binwalk_base_dir + path_fix + filesystem_roots[fw_filesystem]


def get_filesystem(input):
    global filesystems
    for filesystem in filesystems:
        if filesystem + ' filesystem' in input:
            return filesystem


def binwalk(path, params):
    result = ''
    if platform.system() == 'Windows':
        result = call_wsl_binwalk(path, params)
        path_fix = '\\'
    elif platform.system() == 'Linux' or platform.system() == 'MacOS':
        result = call_linux_binwalk(path, params)
        path_fix = '/'
    return result


def call_wsl_binwalk(path, param):
    wsl_path = win_path_to_wsl_path(path)
    base_path = wsl_path[:wsl_path.rfind('/')]
    process = subprocess.Popen('wsl binwalk '+param+' -C '+base_path+' '+wsl_path,
                               shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    result = ''
    for line in process.stdout.readlines():
        result += line.decode('utf8')
        print(line.decode('utf8').replace('\n', ''))
    return result


def call_linux_binwalk(path, param):
    base_path = path[:path.rfind('/')]
    process = subprocess.Popen('binwalk '+param+' -C '+base_path+' '+path,
                               shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    result = ''
    for line in process.stdout.readlines():
        result += line.decode('utf8')
        print(line.decode('utf8').replace('\n', ''))
    return result


# Change Windows-style path to *nix-style path in WSL
# D:\aaa\bbb  -->  /mnt/d/aaa/bbb
def win_path_to_wsl_path(path):
    drive = path[0].lower()
    wsl_path = '/mnt/' + drive + path.replace('\\', '/')[2:]
    return wsl_path


if __name__ == '__main__':
    path = 'D:\\Analysis\\mico_all_f86a5_1.44.4.bin'
    file_name = 'mico_all_f86a5_1.44.4.bin'
    fw_info = binwalk_get_fw_info(file_name, path)
    print(fw_info)
    extracted_path = binwalk_get_fw_root_directory(fw_info)
    print(extracted_path)
