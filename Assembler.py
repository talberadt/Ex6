#################################################################
# FILE : Assembler.py
# WRITERS : Amir Kaya, Tal Beradt
# EXERCISE : nand2tetris ex6 2020-2021
# DESCRIPTION: A file that translates Hack assembly programs into executable
# Hack binary code
# STUDENTS I DISCUSSED THE EXERCISE WITH:
# WEB PAGES I USED:
# NOTES: ...
#################################################################
import math
import sys
import os


def check_if_int(num):
    try:
        int(num)
        return True
    except ValueError:
        return False


def dec_to_16bit(num):
    deg = math.pow(2, 15)
    s = ""
    while deg >= 1:
        if num - deg >= 0:
            num = num - deg
            s += "1"
        else:
            s += "0"
        deg = deg / 2
    return s


def clear_symbol_table(symbol_table):
    symbol_table.clear()
    for i in range(16):  # Adds R0-R15
        s = "R" + str(i)
        symbol_table[s] = dec_to_16bit(i)
    symbol_table["SCREEN"] = dec_to_16bit(16384)
    symbol_table["KBD"] = dec_to_16bit(24576)
    symbol_table["SP"] = dec_to_16bit(0)
    symbol_table["LCL"] = dec_to_16bit(1)
    symbol_table["ARG"] = dec_to_16bit(2)
    symbol_table["THIS"] = dec_to_16bit(3)
    symbol_table["THAT"] = dec_to_16bit(4)


def initialization(symbol_table, comp, dest, jump):
    for i in range(16):  # Adds R0-R15
        s = "R" + str(i)
        symbol_table[s] = dec_to_16bit(i)
    symbol_table["SCREEN"] = dec_to_16bit(16384)
    symbol_table["KBD"] = dec_to_16bit(24576)
    symbol_table["SP"] = dec_to_16bit(0)
    symbol_table["LCL"] = dec_to_16bit(1)
    symbol_table["ARG"] = dec_to_16bit(2)
    symbol_table["THIS"] = dec_to_16bit(3)
    symbol_table["THAT"] = dec_to_16bit(4)

    #  Initialize comp table

    comp["0"] = "110101010"
    comp["1"] = "110111111"
    comp["-1"] = "110111010"
    comp["D"] = "110001100"
    comp["A"] = "110110000"
    comp["!D"] = "110001101"
    comp["!A"] = "110110001"
    comp["-D"] = "110001111"
    comp["-A"] = "110110011"
    comp["D+1"] = "110011111"
    comp["A+1"] = "110110111"
    comp["D-1"] = "110001110"
    comp["A-1"] = "110110010"
    comp["D+A"] = "110000010"
    comp["D-A"] = "110010011"
    comp["A-D"] = "110000111"
    comp["D&A"] = "110000000"
    comp["D|A"] = "110010101"
    comp["M"] = "111110000"
    comp["!M"] = "111110001"
    comp["-M"] = "111110011"
    comp["M+1"] = "111110111"
    comp["M-1"] = "111110010"
    comp["D+M"] = "111000010"
    comp["D-M"] = "111010011"
    comp["M-D"] = "111000111"
    comp["D&M"] = "111000000"
    comp["D|M"] = "111010101"

    comp["D>>"] = "010010000"
    comp["D<<"] = "010110000"
    comp["A>>"] = "010000000"
    comp["A<<"] = "010100000"
    comp["M>>"] = "011000000"
    comp["M<<"] = "011100000"

    comp["D*A"] = "000000000"
    comp["D*M"] = "001000000"

    #  Initialize dest table

    dest["null"] = "000"
    dest["M"] = "001"
    dest["D"] = "010"
    dest["MD"] = "011"
    dest["A"] = "100"
    dest["AM"] = "101"
    dest["AD"] = "110"
    dest["AMD"] = "111"

    #  Initialize jump table

    jump["null"] = "000"
    jump["JGT"] = "001"
    jump["JEQ"] = "010"
    jump["JGE"] = "011"
    jump["JLT"] = "100"
    jump["JNE"] = "101"
    jump["JLE"] = "110"
    jump["JMP"] = "111"


def first_pass(instructions, symbol_table):
    line_c = -1
    for ins in instructions:
        if ins[0] != "(":  # If not a label and not comment
            line_c = line_c + 1  # Count line
            continue
        words = ins.split("/")
        words[0] = words[0].strip("() ")
        symbol_table[words[0]] = dec_to_16bit(line_c + 1)


def a_instruction(ins, n, symbol_table):
    ins = ins.strip("@")
    symbol = ins.split("/")
    if check_if_int(symbol[0]):
        return dec_to_16bit(int(symbol[0]))
    else:
        if symbol[0] not in symbol_table:
            symbol_table[symbol[0]] = dec_to_16bit(n[0])
            n[0] += 1
        return symbol_table.get(symbol[0])


def c_instruction(instruction, comp_table, dest_table, jump_table):
    symbol = instruction.split("/")
    inst = symbol[0].split("=")
    if len(inst) > 1:
        dest = dest_table[inst[0]]
        ins = inst[1].split(";")
    else:
        dest = "000"
        ins = inst[0].split(";")
    if len(ins) > 1:
        jmp = jump_table[ins[1]]
    else:
        jmp = "000"
    comp = comp_table[ins[0]]
    return "1%s%s%s" % (comp, dest, jmp)


def second_pass(instructions, symbol_table, comp_table, dest_table,
                jump_table, file_name):
    n = [16]
    with open("%s.hack" % file_name, "w") as f:
        for ins in instructions:
            if ins[0] != "(":  # If not a label and not comment
                f.write(a_instruction(ins, n, symbol_table) if
                        ins[0] == "@" else
                        c_instruction(ins, comp_table, dest_table,
                                      jump_table))
                f.write("\n")


def handle_file(file_name, symbol_table, comp, dest, jump):
    instructions = list()
    with open(file_name, "r") as file:
        for line in file:
            line = line.strip()
            if line and line[0] != "/":  # All non-blank instructions and
                # non-comment instructions
                instructions.append(line.replace(" ", ""))
    first_pass(instructions, symbol_table)
    file_name = file_name.split(".")
    second_pass(instructions, symbol_table, comp, dest, jump, file_name[0])
    clear_symbol_table(symbol_table)


def main():
    symbol_table = dict()
    comp = dict()
    dest = dict()
    jump = dict()
    initialization(symbol_table, comp, dest, jump)  # Initializes the symbol table
    if sys.argv[1].endswith(".asm"):  # Single File
        handle_file(sys.argv[1], symbol_table, comp, dest, jump)  # Handles
    else:  # Directory
        for file in os.listdir(sys.argv[1]):
            if file.endswith(".asm"):
                handle_file(os.path.join(sys.argv[1], file),
                            symbol_table, comp, dest, jump)  # Handles


if __name__ == "__main__":
    main()
