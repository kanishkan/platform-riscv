import os

from SCons.Script import DefaultEnvironment

env = DefaultEnvironment()
platform = env.PioPlatform()

SDK_DIR = platform.get_package_dir("framework-pulp-sdk")
assert os.path.isdir(SDK_DIR)

board_config = env.BoardConfig()

try:
    import prettytable
except ImportError:
    env.Execute(
        env.VerboseAction(
            "$PYTHONEXE -m pip install prettytable",
            "Installing Python dependencies",
        )
    )

env.SConscript("_bare.py")

env.Append(
    ASPPFLAGS=[
        "-DLANGUAGE_ASSEMBLY",
        "-fno-common"
    ],
    CCFLAGS=[
        "-Wall",
        "-fno-builtin-printf"
    ],
    LINKFLAGS=[
        "-nostartfiles",
    ],
)

assert not board_config.get("build.ldscript", "");

