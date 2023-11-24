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
    
    for itms1 in block.statements:
        
        constructions = [pyverilog.vparser.ast.ForStatement,
                         pyverilog.vparser.ast.WhileStatement, pyverilog.vparser.ast.Case]

        for t in constructions:
            if isinstance(itms1, t):

                if isinstance(itms1.statement, pyverilog.vparser.ast.Block):
                    blockCheck(itms1.statement)

        if isinstance(itms1, pyverilog.vparser.ast.IfStatement):
             
            if isinstance(itms1.true_statement, pyverilog.vparser.ast.Block):
                blockCheck(itms1.true_statement)

        if isinstance(itms1, pyverilog.vparser.ast.NonblockingSubstitution):
  
            return False
        else:
            return True


def recognizer(new_module):

    if not new_module.endswith('.v'):
        new_module = new_module + '.v'
    result = True
    print('Analyzing module name ' + new_module)
    if not os.path.exists(new_module): 
        return True
    try:
        ast, _ = parse([new_module])
    except Exception as e:
        
        return False

    itm0 = ast.description.definitions[0]
    inputNameCorrect = 1
    i=0
    while (isinstance(itm0, pyverilog.vparser.ast.Pragma)):
        i+=1
        itm0= ast.description.definitions[i]

    for itms in itm0.portlist.ports:
        if (isinstance(itms, pyverilog.vparser.ast.Ioport)):
            if (isinstance(itms.first, pyverilog.vparser.ast.Input)):

                if not itms.first.name == 'CLK' or 'clear' or 'preset' or 'load':
                    inputNameCorrect = 0

    for defs in ast.description.definitions:
        if (isinstance(defs, pyverilog.vparser.ast.Pragma)):
            continue
        count_defs = []
        count_assign = []
        count_always = []
        count_instances = []
        len_items = len(defs.items)

        for itms in defs.items:
            if (isinstance(itms, pyverilog.vparser.ast.InstanceList)):
                for instances in itms.instances:
                    
                    result = result and recognizer(instances.module)
                    count_instances.append(itms)

            if (isinstance(itms, pyverilog.vparser.ast.Decl)):
                count_defs.append(itms)
                

            if (isinstance(itms, pyverilog.vparser.ast.Assign)):
                count_assign.append(itms)

            if (isinstance(itms, pyverilog.vparser.ast.Always)):
                alwaysConstructionCorrect = 1
                if (not (isinstance(itms, pyverilog.vparser.ast.AlwaysFF))) or (not (isinstance(itms, pyverilog.vparser.ast.AlwaysLatch))):
                    for sens in itms.sens_list.list:
                        if sens.type == ('posedge' or 'negedge') and not sens.sig == ('CLK'):
                            alwaysConstructionCorrect = 0
                if isinstance(itms.statement, pyverilog.vparser.ast.Block):
                    
                    if not blockCheck(itms.statement):
                        
                        alwaysConstructionCorrect = 0

                if alwaysConstructionCorrect == 1:
                    count_assign.append(itms)


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
