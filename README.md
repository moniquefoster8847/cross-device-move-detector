# cross-device-move-detector

Detects whether moving a file between two paths would cross a filesystem boundary and therefore require copy-and-delete instead of a simple rename.

## Usage

```python
from cross_device_move_detector import is_cross_device

# Same filesystem: a rename will work.
assert not is_cross_device("/tmp/a.txt", "/tmp/b.txt")
```

The function returns `False` when either path does not exist, because a missing source means there is nothing to move and a missing destination means the move will fail before the device comparison matters. That means the example above also returns `False` when `/tmp/a.txt` does not exist; create both files first if you want the same-device comparison to be meaningful.

## Why this exists

`os.rename` only works within a single filesystem. When a move crosses a device boundary, callers must fall back to copying the file and then deleting the source. Deciding which strategy to use requires comparing the `st_dev` of the two paths, but doing so correctly is easy to get wrong with symlinks and missing paths.

This library makes one clear choice: it resolves both paths with `os.path.realpath` before comparing `st_dev`. That follows symlinks, matching the behaviour of `mv` on POSIX systems, so a symlink that points to another device is reported as cross-device. If you need to reason about the symlink itself rather than its target, this library is not the right tool.

The awkward edge you will hit is missing paths. Rather than raising `FileNotFoundError`, the function returns `False`. That keeps the common “check before moving” flow simple, but it means a typo in the source path looks identical to a same-device move. Callers that need to distinguish these cases should check existence separately.
