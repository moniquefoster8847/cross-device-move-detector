import os


def is_cross_device(source: str, destination: str) -> bool:
    """Return True if moving *source* to *destination* crosses a device boundary.

    A move across devices cannot be done with :func:`os.rename`; the caller must
    copy the file and then delete the source. This function compares the ``st_dev``
    of the two paths. If either path does not exist, ``False`` is returned: a
    non-existent source means there is nothing to move, and a non-existent
    destination (or its parent) means the move will fail before device comparison
    matters.

    The check is deliberately conservative: both paths are resolved with
    :func:`os.path.realpath` so that symlinks do not produce false positives or
    negatives. This matches the behaviour of ``mv`` on POSIX systems, which
    follows symlinks when deciding whether a rename is possible.

    Args:
        source: Path to the file or directory being moved.
        destination: Path to the destination file or directory.

    Returns:
        ``True`` if the source and destination are on different devices,
        ``False`` otherwise (including when either path does not exist).
    """
    try:
        src_dev = os.stat(os.path.realpath(source)).st_dev
    except OSError:
        return False
    try:
        dst_dev = os.stat(os.path.realpath(destination)).st_dev
    except OSError:
        # The destination does not exist yet. Fall back to the device of its
        # nearest existing ancestor, which is the device it would be created on.
        parent = os.path.dirname(os.path.realpath(destination))
        while True:
            try:
                dst_dev = os.stat(parent).st_dev
                break
            except OSError:
                new_parent = os.path.dirname(parent)
                if new_parent == parent:
                    return False
                parent = new_parent
    return src_dev != dst_dev
