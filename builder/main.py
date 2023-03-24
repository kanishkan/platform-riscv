"""
    Build script for test.py
    test-builder.py
"""

from os.path import join
from SCons.Script import COMMAND_LINE_TARGETS, AlwaysBuild, Builder, Default, DefaultEnvironment

def generate_disassembly(target, source, env):
    elf_file = target[0].get_path()
    assert elf_file.endswith(".elf")
    env.Execute(
        " ".join(
            [
                env.subst("$CC").replace("-gcc", "-objdump"),
                "-d",
                '"%s"' % elf_file,
                ">",
                '"%s"' % elf_file.replace(".elf", ".dis"),
            ]
        )
    )

env = DefaultEnvironment()
platform = env.PioPlatform()
board_config = env.BoardConfig()

env.Replace(
    AR="riscv32-unknown-elf-gcc-ar",
    AS="riscv32-unknown-elf-gcc",
    CC="riscv32-unknown-elf-gcc",
    GDB="riscv32-unknown-elf-gdb",
    CXX="riscv32-unknown-elf-g++",
    OBJCOPY="riscv32-unknown-elf-objcopy",
    RANLIB="riscv32-unknown-elf-gcc-ranlib",
    SIZETOOL="riscv32-unknown-elf-size",

    ARFLAGS=["rcs"],

    SIZEPRINTCMD='$SIZETOOL -d $SOURCES',

    PROGSUFFIX=".elf"
)

# Allow user to override via pre:script
if env.get("PROGNAME", "program") == "program":
    env.Replace(PROGNAME="firmware")

mem_map = [
    "-DSIM_CTRL_BASE=%s" % board_config.get("memmap.sim_ctrl_base"),
    "-DSIM_CTRL_OUT=%s" % board_config.get("memmap.sim_ctrl_out"),
    "-DSIM_CTRL_CTRL=%s" % board_config.get("memmap.sim_ctrl_ctrl"),
    "-DTIMER_BASE=%s" % board_config.get("memmap.timer_base"),
    "-DTIMER_MTIME=%s" % board_config.get("memmap.timer_mtime"),
    "-DTIMER_MTIMEH=%s" % board_config.get("memmap.timer_mtimeh"),
    "-DTIMER_MTIMECMP=%s" % board_config.get("memmap.timer_mtimecmp"),
    "-DTIMER_MTIMECMPH=%s" % board_config.get("memmap.timer_mtimecmph"),
]

machine_flags = [
    "-march=%s" % board_config.get("build.march"),
    "-mabi=%s" % board_config.get("build.mabi"),
    "-MMD",
    "-Wall",
    "-fvisibility=hidden",
    "-nostdlib",
    "-nostartfiles",
    "-ffreestanding",
    "-static",
    "-mcmodel=%s" % board_config.get("build.mcmodel"),
]
compile_flags = machine_flags + mem_map

env.Append(
    ASFLAGS=compile_flags,
    APPFLAGS=[],
    CCFLAGS=compile_flags,
    LINKFLAGS=machine_flags,
    LIBS=[],
    BUILDERS=dict(
        ElfToHex=Builder(
            action=env.VerboseAction(" ".join([
                "$OBJCOPY",
                "-O",
                "ihex",
                "$SOURCES",
                "$TARGET"
            ]), "Building $TARGET"),
            suffix=".hex"
        ),
        ElfToBin=Builder(
            action=env.VerboseAction(" ".join([
                "$OBJCOPY",
                "-O",
                "binary",
                "$SOURCES",
                "$TARGET"
            ]), "Building $TARGET"),
            suffix=".bin"
        )
    )
)

if not board_config.get("build.ldscript", ""):
    env.Replace(LDSCRIPT_PATH="link.ld")
#
# Target: Build executable and linkable firmware
#

target_elf = None
if "nobuild" in COMMAND_LINE_TARGETS:
    target_elf = join("$BUILD_DIR", "${PROGNAME}.elf")
    target_bin = join("$BUILD_DIR", "${PROGNAME}.bin")
else:
    target_elf = env.BuildProgram()
    target_bin = env.ElfToBin(join("$BUILD_DIR", "${PROGNAME}"), target_elf)

AlwaysBuild(env.Alias("nobuild", target_bin))
target_buildprog = env.Alias("buildprog", target_bin, target_bin)

env.AddPostAction(
    target_elf, env.VerboseAction(generate_disassembly, "Generating disassembly")
)

#
# Target: Print binary size
#
target_size = env.AddPlatformTarget(
    "size",
    target_elf,
    env.VerboseAction("$SIZEPRINTCMD", "Calculating size $SOURCE"),
    "Program Size",
    "Calculate program size",
)

#
# Target: Define targets
#
Default([target_buildprog, target_size])
