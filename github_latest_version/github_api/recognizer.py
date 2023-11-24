from __future__ import absolute_import
from __future__ import print_function
import sys
import os
from optparse import OptionParser
import pyverilog
from pyverilog.vparser.parser import parse

# the next line can be removed after installation
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def blockCheck(block):
    print('block found')
    print(block.statements)
    for itms1 in block.statements:
        print(itms1)
        constructions = [pyverilog.vparser.ast.ForStatement,
                         pyverilog.vparser.ast.WhileStatement, pyverilog.vparser.ast.Case]

        for t in constructions:
            if isinstance(itms1, t):
                print('statement found')
                print(itms1.statement)
                if isinstance(itms1.statement, pyverilog.vparser.ast.Block):
                    blockCheck(itms1.statement)

        if isinstance(itms1, pyverilog.vparser.ast.IfStatement):
            print('statement found')
            print(itms1.true_statement)
            if isinstance(itms1.true_statement, pyverilog.vparser.ast.Block):
                blockCheck(itms1.true_statement)

        if isinstance(itms1, pyverilog.vparser.ast.NonblockingSubstitution):
            print('Block check failed')
            print(itms1)
            return False
        #add previous false checking
        else:
            print('Block check true')
            return True


def recognizer(new_module):

    if not new_module.endswith('.v'):
        new_module = new_module + '.v'
    result = True
    print('Analyzing module name')
    print(new_module)
    ast, _ = parse([new_module])
    # ast.show()
    print(ast.name)
    print(ast.description.definitions)
    print(ast.description.definitions[0].items)
    print("---------------------------")
    # while result == True:
    itm0 = ast.description.definitions[0]
    print(itm0.portlist)
    inputNameCorrect = 1

    for itms in itm0.portlist.ports:
        if (isinstance(itms, pyverilog.vparser.ast.Ioport)):
            if (isinstance(itms.first, pyverilog.vparser.ast.Input)):
                print('input name')
                print(itms.first.name)
                if not itms.first.name == 'CLK' or 'clear' or 'preset' or 'load':
                    inputNameCorrect = 0

    if inputNameCorrect == 0:
        print('Sequence variables are found')

    if inputNameCorrect == 1:
        print('Sequence variables are not found')

    for defs in ast.description.definitions:
        count_defs = []
        count_assign = []
        count_always = []
        count_instances = []
        len_items = len(defs.items)

        for itms in defs.items:
            if (isinstance(itms, pyverilog.vparser.ast.InstanceList)):
                print(itms.instances)
                for instances in itms.instances:
                    print(instances.module)
                    result = result and recognizer(instances.module)
                    count_instances.append(itms)

            if (isinstance(itms, pyverilog.vparser.ast.Decl)):
                count_defs.append(itms)
                print(itms.list)

            if (isinstance(itms, pyverilog.vparser.ast.Assign)):
                count_assign.append(itms)

            if (isinstance(itms, pyverilog.vparser.ast.Always)):
                alwaysConstructionCorrect = 1
                if (not (isinstance(itms, pyverilog.vparser.ast.AlwaysFF))) or (not (isinstance(itms, pyverilog.vparser.ast.AlwaysLatch))):
                    for sens in itms.sens_list.list:
                        if sens.type == ('posedge' or 'negedge') and not sens.sig == ('CLK'):
                            alwaysConstructionCorrect = 0
                # if - true_statement, for, while, case - statement; caseStatement - ?? caselist
                # create a recursion?
                if isinstance(itms.statement, pyverilog.vparser.ast.Block):
                    print('block found')
                    if not blockCheck(itms.statement):
                        print('block check failed')
                        alwaysConstructionCorrect = 0

                if alwaysConstructionCorrect == 1:
                    print('Always construction is correct')
                    count_assign.append(itms)
                else:
                    print('Always construction is incorrect')

        print("Objects def")
        print(count_defs)
        print("Objects assign")
        print(count_assign)
        print("Objects always")
        print(count_always)
        print("Objects instance")
        print(count_instances)
        print("Number of objects")
        print(len_items)

        if (len_items == len(count_defs) + len(count_assign) + len(count_always) + len(count_instances)) and (inputNameCorrect == 1):
            return result
        else:
            result = False
            return result
    return True


def main():

    USAGE = "Usage: python testparser.py file.v"

    optparser = OptionParser()

    (_, filelist) = optparser.parse_args()

    result = True

    for f in filelist:
        result = result and recognizer(f)

    if result:
        print('Комбинационная схема')
    else:
        print('Нужно подумать')


if __name__ == '__main__':
    main()
