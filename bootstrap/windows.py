"""Windows-specific helpers: registry PATH refresh, winget install with precheck, and
per-user file association registration. Kept in a separate module so utils.py stays
focused on cross-platform plumbing — none of this runs on POSIX (refresh_path is a
no-op there; the file-assoc / winget entry points are gated on sys.platform by callers
or by the runner script setting --systype windows).
"""

import os
import subprocess
import sys

from bootstrap import log

HOMEDIR = os.path.expanduser("~")


def _replace_home(path):
    return path.replace("~", HOMEDIR)


def refresh_path():
    """Re-read PATH from HKLM and HKCU registry hives into os.environ. No-op off Windows.

    Why this exists: scoop, winget, rustup, the Go installer, and friends all modify
    HKCU\\Environment\\Path during install. Without this, anything that changes PATH
    mid-run is invisible to subsequent subprocesses we spawn — os.environ was captured
    at process startup. We call this both at the end of every _run_cmd (so a freshly
    installed tool is visible to the next command) and at the start of every _run_check
    (so a chain of skipped prechecks doesn't keep checking against a stale PATH that
    our parent shell handed us before any of those tools were installed).
    """
    if sys.platform != "win32":
        return
    try:
        import winreg

        parts = []
        for hive, subkey in (
            (winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Control\Session Manager\Environment"),
            (winreg.HKEY_CURRENT_USER, "Environment"),
        ):
            try:
                with winreg.OpenKey(hive, subkey) as key:
                    val, _ = winreg.QueryValueEx(key, "Path")
                    if val:
                        parts.append(os.path.expandvars(val))
            except OSError:
                pass
        if parts:
            os.environ["PATH"] = os.pathsep.join(parts)
    except Exception:
        pass  # PATH refresh is best-effort; never fail the run if registry access errors


def install_winget_packages(pkgs, run_cmd):
    """Install each winget package one at a time, skipping any already installed.

    winget exits non-zero (e.g. 0x8a15002b "no available upgrade") when a package is
    already installed at the latest version, which the engine would otherwise log as a
    failure even though nothing went wrong. `winget list --id X -e` exits 0 iff the
    package is installed regardless of upgrade availability — exactly the signal we want
    for an idempotent skip. We also install one at a time so a single missing manifest
    or transient network failure doesn't take out the rest of the batch.
    """
    for pkg in pkgs:
        check = subprocess.run(
            f"winget list --id {pkg} -e --accept-source-agreements",
            shell=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=60,
        )
        if check.returncode == 0:
            log.skip(f"winget: {pkg} already installed")
            continue
        run_cmd(
            f"winget install --id {pkg} --silent --accept-source-agreements --accept-package-agreements",
            shortcircuit=False,
        )


def set_file_assoc(ext, progid, cmd, name=None, icon=None, label=None):
    """Register a per-user file association under HKCU\\Software\\Classes — no admin needed.

    Writes:
      HKCU\\Software\\Classes\\<ext>\\(default)                          = <progid>
      HKCU\\Software\\Classes\\<progid>\\(default)                       = <name>           (if name)
      HKCU\\Software\\Classes\\<progid>\\DefaultIcon\\(default)          = <icon>           (if icon)
      HKCU\\Software\\Classes\\<progid>\\shell\\open\\FriendlyAppName    = <name>           (if name)
      HKCU\\Software\\Classes\\<progid>\\shell\\open\\command\\(default) = <cmd>

    The `name` writes are what make the "Open with" picker show e.g. "Neovim" instead
    of "Terminal" or "Shim". Windows reads FriendlyAppName / the ProgID default before
    falling back to the launcher .exe's embedded ProductName, which on stripped binaries
    or AppX execution aliases is often blank or generic.

    The `icon` write sets the Explorer thumbnail. Format is either "<path>,<index>" to
    pull a PE icon resource (e.g. "C:\\Program Files\\Neovim\\bin\\nvim.exe,0") or a path
    to a .ico file. Without it, files of the type inherit the icon of whatever wrapper
    exe Windows finds first in cmd, which is often a generic shell-script icon when the
    launcher is `wt` / `cmd` / `pwsh`.

    For extensions Windows already claims via UserChoice (e.g. .txt → Notepad on Win11),
    we clear UserChoice so Explorer falls back to our class registration. Windows blocks
    programmatic *creation* of UserChoice (it's hash-protected) but allows deletion. We
    only delete UserChoice when it points to a *different* ProgID — a user's "Always use
    this app" selection that already matches us is preserved across re-runs.
    """
    import winreg

    label = label or f"{ext} -> {progid}"
    log.action(f"file association: {label}")

    cmd = _replace_home(cmd)
    if icon:
        icon = _replace_home(icon)

    with winreg.CreateKey(winreg.HKEY_CURRENT_USER, rf"Software\Classes\{ext}") as k:
        winreg.SetValueEx(k, None, 0, winreg.REG_SZ, progid)

    with winreg.CreateKey(winreg.HKEY_CURRENT_USER, rf"Software\Classes\{progid}") as k:
        if name:
            winreg.SetValueEx(k, None, 0, winreg.REG_SZ, name)

    if icon:
        with winreg.CreateKey(winreg.HKEY_CURRENT_USER, rf"Software\Classes\{progid}\DefaultIcon") as k:
            winreg.SetValueEx(k, None, 0, winreg.REG_SZ, icon)

    with winreg.CreateKey(winreg.HKEY_CURRENT_USER, rf"Software\Classes\{progid}\shell\open") as k:
        if name:
            winreg.SetValueEx(k, "FriendlyAppName", 0, winreg.REG_SZ, name)

    with winreg.CreateKey(winreg.HKEY_CURRENT_USER, rf"Software\Classes\{progid}\shell\open\command") as k:
        winreg.SetValueEx(k, None, 0, winreg.REG_SZ, cmd)

    uc_path = rf"Software\Microsoft\Windows\CurrentVersion\Explorer\FileExts\{ext}\UserChoice"
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, uc_path) as k:
            current_progid, _ = winreg.QueryValueEx(k, "ProgId")
    except (FileNotFoundError, OSError):
        current_progid = None
    if current_progid is not None and current_progid != progid:
        try:
            winreg.DeleteKey(winreg.HKEY_CURRENT_USER, uc_path)
        except (FileNotFoundError, OSError):
            pass


def install_file_associations(config):
    """Top-level entry: reads config['file_associations']['windows'] and registers each."""
    if "file_associations" not in config:
        log.skip("No file_associations in config")
        return
    section = config["file_associations"].get("windows", [])
    if not section:
        log.skip("No windows entries in file_associations")
        return
    if sys.platform != "win32":
        log.skip("file_associations.windows: not on Windows, skipping")
        return
    log.header("Registering Windows file associations")
    for assoc in section:
        set_file_assoc(
            assoc["ext"],
            assoc["progid"],
            assoc["cmd"],
            name=assoc.get("name"),
            icon=assoc.get("icon"),
            label=assoc.get("label"),
        )
