from SCons.Script import DefaultEnvironment

env = DefaultEnvironment()
board_config = env.BoardConfig()

machine_flags = [
    "-march=%s" % board_config.get("build.march"),
]

env.Append(
    ASFLAGS=machine_flags,
    ASPPFLAGS=[
        "-x", "assembler-with-cpp",
    ],
    CCFLAGS=machine_flags + [
        "-Os",
        "-fdata-sections",
        "-ffunction-sections",
    ],
    CPPDEFINES=[
        "__riscv__",
        "__pulp__"
    ],
    LINKFLAGS=machine_flags + [
        "-nostartfiles"
    ],
    LIBS=["gcc"],
)
