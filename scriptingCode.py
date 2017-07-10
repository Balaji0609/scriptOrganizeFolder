import os
# using cElementTree since it is faster than ElementTree
import xml.etree.cElementTree as eT
import re
import shutil
import errno
import sys

"""The variables below are global variables used to store current xml_file, test_case and test_suite that the program is
    processing"""


xml_file_name = ""
test_suite_name = ""
test_case_name = ""


"""The below function is used for sorting files as requested into a XML_FILE/TESTCASE_NAME/PID folders"""


def test_2_copy_files(source, destination):
    list_string = source.split("/")
    destination += list_string[-1]
# using below way for creating directories to try to avoid OSError.
    if not os.path.exists(os.path.dirname(destination)):
        try:
            os.makedirs(os.path.dirname(destination))
        except OSError as ex:
            if ex.errno != errno.EEXIST:
                raise
            print "OS directory creation error with following ERRNO and message :"
            print ex.errno + "\n" + ex.message
    try:
        shutil.copy(source, destination)
    except IOError as ex:
        print "There is some file I/O Error while writing files for task - 2 with following ERRNO and message :"
        print ex.errno + "\n" + ex.message


"""The below function takes the dictionary and outputs the values to a file which consists of requested task 1 output.
    It also uses the global variable for it. It also calls task_2 function for each PIDS in log file to do task 2"""


def task_1_write_file(log_path, dict_temp):
    try:
        with open("Task_1_Result.txt", "a") as FileObj:
            for key, value in dict_temp.iteritems():
                write_line = str(key) + "," + str(xml_file_name) + "," + str(test_case_name) + "," +str(test_suite_name)
                write_line += "," + str(value[1]) + "," + str(value[0]) + "," + str(value[2]) + "\n"
                FileObj.write(write_line)
                destination = "Task_2_Result/" + str(xml_file_name) + "/" + str(test_case_name) + "/" + str(key) + "/"
                test_2_copy_files(log_path, destination)
    except IOError as ex:
        print "There is some file I/O Error while writing task - 1 into file with following errno and message :"
        print ex.errno + "\n" + ex.message
    except Exception as ex:
        print "There is some other Exception while writing task - 1 to file with message : "
        print ex.message


"""The below function is used for identifying whether it is a new test or failed test or success test and returns the 
    value in a list"""


def parse_string(line):
    temp_list = [0, 0, 0]
    if "passed" in line:
        temp_list = [1, 0, 0]
    elif "FAILED" in line:
        temp_list = [0, 1, 0]
    elif "starting test case" in line:
        temp_list = [0, 0, 1]
    return temp_list


"""The below function process each log file by reading each line and using string manipulation and regex. Then it stores
    the required required values in a dictionary which consists of all pids in each log file as key and the count of 
    success, failure and total tests run as values which are present in a list format"""


def log_read_function(log_path):
    dict_temp = {}
    global test_suite_name
    global test_case_name
    global xml_file_name
    try:
        with open(log_path, 'r') as FileObj:
            for lines in FileObj:
                split_word = lines.split("-")
                if test_suite_name == "":
                    test_suite_name = split_word[3].strip()
                pid_val = re.findall("[0-9]+", split_word[0])
                pid_val = pid_val[0]
                temp_list = parse_string(split_word[5])
                if pid_val in dict_temp:
                    value_list = dict_temp[pid_val]
                    dict_temp[pid_val] = [x + y for x, y in zip(temp_list, value_list)]
                else:
                    dict_temp.update({pid_val: temp_list})
    except IOError as ex:
        print "There is some file I/O Error while reading the log file with following ERRNO and message :"
        print ex.errno + "\n" + ex.message
    except Exception as ex:
        print "There is some other exception while reading the log file with message :"
        print ex.message
    task_1_write_file(log_path, dict_temp)
    test_suite_name = ""


"""The below file reads the xml file, parses it and finds all elements with tag TestCase. Then it passes the logpath of 
    each test case to another function for processing log files for which it uses the attribute logpath in the TestCase 
    tag element"""


def xml_read_function(file_path):
    global test_case_name
    try:
        xml_data = eT.parse(file_path)
        xml_list = xml_data.findall(".//TestCase")
        for test_case in xml_list:
            test_case_name = test_case.attrib.get("name")
            log_read_function(test_case.attrib.get("logpath"))
    except Exception as ex:
        print "There is some Exception while parsing the xml file"
        print ex.message


"""The below function reads all files in the given directory with .xml extension and passes each file 
   path to xml parser"""


def read_files_in_dir(dir_path):
    global xml_file_name
    file_list = os.listdir(dir_path)
    if file_list == "":
        print "There are no files in directory"
        return
    for file_name in file_list:
        if file_name.endswith(".xml"):
            xml_file_name = file_name
            xml_read_function(dir_path+file_name)


"""The Below is the main function which removes task1_result file if it already exists for multiple test run 
   There is also a call to a function which reads the directory xml_runner ( "xml_runner/" )"""


if __name__ == "__main__":
    try:
        os.remove("Task1_Result")
    # print "Removing the Task - 1 result file since it is already present."
    except OSError:
        pass
    read_files_in_dir("xml_runner/")
