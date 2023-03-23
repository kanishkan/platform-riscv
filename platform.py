import os
import sys

from platformio.public import PlatformBase

class RiscvPlatform(PlatformBase):
    def get_boards(self, id_=None):
        result = super().get_boards(id_)
        if not result:
            return result
        if id_:
            return self._add_default_debug_tools(result)
        else:
            for key in result:
                result[key] = self._add_default_debug_tools(result[key])
        return result

    def _add_default_debug_tools(self, board):
        debug = board.manifest.get("debug", {})
        if "tools" not in debug:
            debug["tools"] = {}

        tools = (
            "ovpsim"
        )
        for tool in tools:
            if tool in debug["tools"]:
                continue

            if tool == "ovpsim":
                debug["tools"][tool] = {
                    "init_cmds": [
                        "define pio_reset_halt_target",
                        "end",
                        "define pio_reset_run_target",
                        "end",
                        "set mem inaccessible-by-default off",
                        "set arch riscv:rv32",
                        "set remotetimeout 250",
                        "target extended-remote $DEBUG_PORT",
                        "$INIT_BREAK",
                        "$LOAD_CMDS",
                    ],
                    "server": {
                        "package": "tool-ovpsim-corev",
                        "arguments": [
                            "--variant", "CV32E40P",
                            "--port", "3333",
                            "--program",
                            "$PROG_PATH"
                        ],
                        "executable": "riscvOVPsimCOREV"
                    }
                }

        board.manifest["debug"] = debug
        return board
