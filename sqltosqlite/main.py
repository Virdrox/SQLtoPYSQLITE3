#coding:utf-8
import sys
from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import QApplication, QPushButton, QFileDialog, QStatusBar
from PySide6.QtCore import QFile, QIODevice
from PySide6 import QtGui
version = "1.0"

#Autoincrement & arrangement of int
def autoIncrementArrangement(list : list, line : str):
        line = line.replace('auto_increment', 'AUTOINCREMENT')
        if "int(" in line:
            numDeb = line.find("int(")
            for i in range(numDeb, len(line)):
                if line[i] == ')' :
                    line = line.replace(line[numDeb:i],'INTEGER')
            line = line.replace(')','') 
        elif "INT(" in line:
            numDeb = line.find("INT(")
            for i in range(numDeb, len(line)):
                if line[i] == ')' :
                    line = line.replace(line[numDeb:i],'INTEGER')   
            line = line.replace(')','')     
        elif "int" in line:
            line = line.replace('int','INTEGER') 
        return line  

#Convert method
def Convert(importPath : str, exportPath : str, namePY : str, nameDB : str):
    """---------------------------HEADER-------------------------"""
    finalScript = """"""
    finalScript += "#coding:utf-8\n"
    finalScript += "import sqlite3\n"

    #Read the sql file line by line and store them into lines[]
    lines = []
    with open(importPath, mode="r", encoding="utf-8") as f:
        lines = f.readlines()
    lines.append(' ')

    #Remove all escape characters in files[]
    escapes = '\b\n\r\t\\' 
    for i in range(0, len(lines)):
        for c in escapes: 
            lines[i] = lines[i].replace(c, '')

    #Create .db and create a connection with the DB + create a cursor
    finalScript += "\n"
    finalScript += f"con = sqlite3.connect('{nameDB}.db')\n"
    finalScript += f"con = sqlite3.connect('{nameDB}.db', timeout = 1000)\n"
    finalScript += "con.rollback()\n"
    finalScript += "cur = con.cursor()\n"   
    finalScript += "\n"

    """----------------------------BODY--------------------------"""
    tempLine = ""
    comBool = False
    comTemp = ""

    for line in lines:
        #Formatting of quotation marks
        line = line.replace('"', "'")
        #Retirement of spaces at the beginning of the line
        line = line.lstrip()

        #-----------PART OF THE AUTOINCREMENTS & INT-----------"""
        #AutoIncrement & arrangement of int
        line = autoIncrementArrangement(lines,line)  

        """-------------------PART OF SCHEMES--------------------"""
        #Del all schema (not compatible with sqlite3)
        if "CREATE SCHEMA" in line :
            line = ""

        #-------------------PART OF COMMENTS-------------------"""
        #Replaces comments on multiple lines
        if (line.find('/*') != -1 and line.find('*/') == -1  or comBool == True):
            comBool = True
            comTemp += line
            if line.find('*/') != -1:
                comBool = False
                comTemp = comTemp.replace('/*','#')
                comTemp = comTemp.replace('*/','')
                finalScript += '\n' + comTemp + '\n'
                comTemp = ""

        #Replaces comments on one line
        elif ("/*" and "*/") in line :
            line = line.replace("/*", "#")
            line = line.replace("*/", "")
            finalScript += '\n' + line + '\n'

        #-------------------PART OF SELECT-------------------"""
        # For SELECT operator
        elif ("SELECT" or "select") in line :
            if (line[-1:] == ";") :
                line = line.replace(line[-1:], "")
                if tempLine == "" :
                    finalScript += '\n' + 'cur.execute("' + line + '")' + '\n'
                else : 
                    finalScript += '\n' + 'cur.execute("' + tempLine + " " + line +'")' + '\n'
                finalScript += 'print(cur.fetchall())' + '\n'
            else :
                tempLine += line + " "

        #-------------------PART OF CREATION & INSERTION-------------------"""
        #arrange the line if the instruction is on a line
        elif (line[-1:] == ";" and tempLine == " "):
            line = line[:-1]
            line = 'cur .execute("' + line + '")'
            finalScript += line + '\n'

        #The next two conditions allow you to arrange an instruction on several lines
        elif (line[-1:] == ";" and tempLine != ""):
            line = line[:-1]
            line = 'cur.execute("' + tempLine + line + '")'
            finalScript += line + '\n'
            tempLine = ""
        else:
            tempLine += line

    f.close()
    
    #---------------------------FOOTER-------------------------"""
    finalScript += "\ncon.commit()\n"
    finalScript += "cur.close()\n"
    finalScript += "con.close()\n"
    finalScript += 'print("DB crée !")\n'
    finalScript += 'input()\n'

    #---------------------------EXPORT-------------------------"""
    #Export in python file
    if exportPath[-1:] == "/":
        exportPath = exportPath[:-1]
    exportScript = open(exportPath+"/"+namePY+".py", mode="w", encoding="utf-8")
    exportScript.write(finalScript)
    exportScript.close()

#Import Path File
def importFile():
    fname = QFileDialog.getOpenFileName(filter='*.sql')
    fileBrowseFile.setText(fname[0])

#Export Path Directory
def exportFile():
    fname = QFileDialog.getExistingDirectory()
    fileBrowseExport.setText(fname)

#Launch of the conversion
def running(importPath : str, exportPath : str, namePY : str, nameDB : str):
    try:
        Convert(importPath=importPath, exportPath=exportPath, namePY=namePY, nameDB=nameDB)
        statusBar.showMessage("Conversion completed at " + exportPath)
    except FileNotFoundError:
        statusBar.showMessage("File or directory not found")

#MAIN
if __name__ == "__main__":
    app = QApplication(sys.argv)

    ui_file_name = "./graph/graphs.ui"
    ui_file = QFile(ui_file_name)
    if not ui_file.open(QIODevice.ReadOnly):
        print(f"Cannot open {ui_file_name}: {ui_file.errorString()}")
        sys.exit(-1)
    loader = QUiLoader()
    window = loader.load(ui_file)

    convertButton = window.convertButton
    browseButtonFile = window.browseButtonFile
    browseButtonExport = window.browseButtonExport
    fileBrowseFile = window.fileBrowseFile
    fileBrowseExport = window.fileBrowseExport
    lineNameScript = window.lineNameScript
    lineNameDB = window.lineNameDB

    statusBar = window.status
    statusBar.showMessage("Version " + version)

    browseButtonFile.clicked.connect(importFile)
    browseButtonExport.clicked.connect(exportFile)

    convertButton.clicked.connect(lambda: running(importPath=fileBrowseFile.text(), exportPath=fileBrowseExport.text(), namePY=lineNameScript.text(), nameDB=lineNameDB.text()))

    ui_file.close()

    if not window:
        print(loader.errorString())
        sys.exit(-1)
    window.show()

    sys.exit(app.exec())
