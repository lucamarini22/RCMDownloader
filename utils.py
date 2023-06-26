import os
import ctypes
import platform


def bytes_to_gb(bytes: float) -> float:
    """Converts bytes to gb.

    Args:
        bytes (float): number of bytes.

    Returns:
        float: corresponding number of gb.
    """
    return bytes / 1024 / 1024 / 1024

def get_free_space_gb(dirname: str) -> float:
    """Gets the number of free space in folder (in gb). 

    Args:
        dirname (str): path of the folder.

    Returns:
        float: number of free gb in folder.
    """
    if platform.system() == 'Windows':
        free_bytes = ctypes.c_ulonglong(0)
        ctypes.windll.kernel32.GetDiskFreeSpaceExW(ctypes.c_wchar_p(dirname), None, None, ctypes.pointer(free_bytes))
        return bytes_to_gb(free_bytes.value)
    else:
        st = os.statvfs(dirname)
        return bytes_to_gb(st.f_bavail * st.f_frsize)