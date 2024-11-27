""" Sustained Attention to Response Task (SART)

The SART in this module sends participants either a number of SMS messages,
phone calls, or no alert, depending on which group they are randomly assigned
to by the task.  This only occurs during the second block of trials.  The 
first block of trials is the same for each group.

Self-Contained Functions (Argument=Default Value):

sart(monitor="testMonitor", reps=8, omitNum=3, practice=True, 
     path="")

"""
# Author: Cary Stothart (cary.stothart@gmail.com)
# Date: 02/12/2013
# Version: 1.0

# TODO
# Replaced clock with perf clock
# Background thread does not work, needs fix or something - time.sleep works okay ig
# sys.exit does not work
# Commented out multi thread
# commented out twilio
# edited random number so only the non messaging/call group gets done
# Last fix DO NOT save the participants phone number or email this will fuck up data
# Last fix 2 Make sure to fix data output

import time
import copy
import re
import random
from threading import Thread

from psychopy import visual, core, data, event, gui
from twilio.rest import TwilioRestClient

# This is only modified by the alert functions.
alertStatus = "NA"

def sart(monitor="testMonitor", reps=8, omitNum=3, practice=True, 
         path=""):
    """ SART Task.
    
    monitor......The monitor to be used for the task.
    reps.........The number of repititions to be presented per block.  Each
                 repitition equals 45 trials (5 font sizes X 9 numbers).
    omitNum......The number participants should withold pressing a key on.
    practice.....Determine whether or not the task will display 18 practice
                 trials that contain feeback on accuracy.
    path.........The directory in which the output file will be placed.
    """
    partInfo = part_info_gui()
    partPhone = check_phone_num(partInfo[4])
    mainResultList = []
    fileName = "SART_" + str(partInfo[0]) + ".txt"
    outFile = open(path + fileName, "w")
    win = visual.Window(fullscr=True, color="black", units='cm',
                        monitor=monitor)
    sart_init_inst(win, omitNum)
    if practice == True:
        sart_prac_inst(win, omitNum)
        mainResultList.extend(sart_block(win, fb=True, omitNum=omitNum,
                                     reps=1, bNum=0, 
                                     phoneNum=partPhone,
                                     sms=False, call=False))
    sart_act_task_inst(win)
    mainResultList.extend(sart_block(win, fb=False, omitNum=omitNum,
                                     reps=reps, bNum=1, 
                                     phoneNum=partPhone,
                                     sms=False, call=False))
    sart_break_inst(win)
    random.seed(partInfo[0])
    ranNum = random.randint(61, 90)
    if (ranNum >= 1) and (ranNum <= 30):
        cond = "SMS"
        mainResultList.extend(sart_block(win, fb=False, omitNum=omitNum,
                                         reps=reps, bNum=2, 
                                         phoneNum=partPhone,
                                         sms=True, call=False))
    elif (ranNum >= 31) and (ranNum <= 60):
        cond = "Call"
        mainResultList.extend(sart_block(win, fb=False, omitNum=omitNum,
                                         reps=reps, bNum=2, 
                                         phoneNum=partPhone,
                                         sms=False, call=True))
    else:
        cond = "No Alert"
        mainResultList.extend(sart_block(win, fb=False, omitNum=omitNum,
                                         reps=reps, bNum=2, 
                                         phoneNum=partPhone,
                                         sms=False, call=False))
    outFile.write("group\tpart_num\tpart_gender\tpart_age\tpart_school_yr\t" +
                  "part_normal_vision\texp_initials\tblock_num\ttrial_num" +
                  "\talert_sent\talert_type\tnumber\tomit_num\tresp_acc\t" +
                  "resp_rt\ttrial_start_time_s\ttrial_end_time_s" +
                  "\tdifference_s\talert_status\tmean_trial_time_s\t" +
                  "timing_function\n")
    for line in mainResultList:
        outFile.write(cond + "\t")
        for item in partInfo:
            outFile.write(str(item) + "\t")
        for col in line:
            outFile.write(str(col) + "\t")
        outFile.write("time.perf_counter()\n")
    outFile.close()
    
def part_info_gui():
    info = gui.Dlg(title="SART")
    info.addText("Participant Info")
    info.addField("Part. Number: ")
    info.addField("Part. Gender: ", 
                  choices=["Please Select", "Male", "Female", "Other"])
    info.addField("Part. Age:  ")
    info.addField("Part. Email: ")
    info.addField("Part. Phone: ")
    info.addField("Part. Year in School: ", 
                  choices=["Please Select", "Freshman", "Sophmore", "Junior", 
                           "Senior", "1st Year Graduate Student", 
                           "2nd Year Graduate Student", 
                           "3rd Year Graduate Student", 
                           "4th Year Graduate Student",
                           "5th Year Graduate Student", 
                           "6th Year Graduate Student"])
    info.addField("Do you have normal or corrected-to-normal vision?", 
                  choices=["Please Select", "Yes", "No"])
    info.addText("Experimenter Info")
    info.addField("DIS Initials:  ")
    info.show()
    if info.OK:
        infoData = info.data
    else:
        sys.exit()
    return infoData
    
def check_phone_num(phoneNum):
    type1 = re.search(".*(\d{3}).*(\d{3}).*(\d{4}).*", phoneNum)
    type2 = re.search(".*(\d{3}).*(\d{4}).*", phoneNum)
    if type1 is not None:
            phoneNum = type1.group(1) + type1.group(2) + type1.group(3)
            return phoneNum
    if type2 is not None:
            phoneNum = "850" + type2.group(1) + type2.group(2)
            return phoneNum
    phoneNum = ' '
    return phoneNum

def sart_init_inst(win, omitNum):
    inst = visual.TextStim(win, text=("In this task, a series of numbers will" +
                                      " be presented to you.  For every" +
                                      " number that appears except for the" +
                                      " number " + str(omitNum) + ", you are" +
                                      " to press the space bar as quickly as" +
                                      " you can.  That is, if you see any" +
                                      " number but the number " +
                                      str(omitNum) + ", press the space" +
                                      " bar.  If you see the number " +
                                      str(omitNum) + ", do not press the" +
                                      " space bar or any other key.\n\n" +
                                      "Please give equal importance to both" +
                                      " accuracy and speed while doing this" + 
                                      " task.\n\nPress the b key when you" +
                                      " are ready to start."), 
                           color="white", height=0.7, pos=(0, 0))
    event.clearEvents()
    while 'b' not in event.getKeys():
        inst.draw()
        win.flip()
        
def sart_prac_inst(win, omitNum):
    inst = visual.TextStim(win, text=("We will now do some practice trials " +
                                      "to familiarize you with the task.\n" +
                                      "\nRemember, press the space bar when" +
                                      " you see any number except for the " +
                                      " number " + str(omitNum) + ".\n\n" +
                                      "Press the b key to start the " +
                                      "practice."), 
                           color="white", height=0.7, pos=(0, 0))
    event.clearEvents()
    while 'b' not in event.getKeys():
        inst.draw()
        win.flip()
        
def sart_act_task_inst(win):
    inst = visual.TextStim(win, text=("We will now start the actual task.\n" +
                                      "\nRemember, give equal importance to" +
                                      " both accuracy and speed while doing" +
                                      " this task.\n\nPress the b key to " +
                                      "start the actual task."), 
                           color="white", height=0.7, pos=(0, 0))
    event.clearEvents()
    while 'b' not in event.getKeys():
        inst.draw()
        win.flip()
        
def sart_break_inst(win):
        inst = visual.TextStim(win, text=("You will now have a 60 second " +
                                          "break.  Please remain in your " +
                                          "seat during the break."),
                               color="white", height=0.7, pos=(0, 0))
        nbInst = visual.TextStim(win, text=("You will now do a new block of" +
                                            " trials.\n\nPress the b key " +
                                            "bar to begin."),
                                 color="white", height=0.7, pos=(0, 0))
        startTime = time.perf_counter()
        while 1:
            eTime = time.perf_counter() - startTime
            inst.draw()
            win.flip()
            if eTime > 5: #changed
                break
        event.clearEvents()
        while 'b' not in event.getKeys():
            nbInst.draw()
            win.flip()

def sart_block(win, fb, omitNum, reps, bNum, phoneNum, sms, call):
    account = "ENTER ACCOUNT NUMBER HERE" # Twilio account number.
    token = "ENTER TOKEN NUMBER HERE"  # Twilio token number.
    #client = TwilioRestClient(account, token)
    client = True
    mouse = event.Mouse(visible=0)
    xStim = visual.TextStim(win, text="X", height=3.35, color="white", 
                            pos=(0, 0))
    circleStim = visual.Circle(win, radius=1.50, lineWidth=8,
                               lineColor="white", pos=(0, -.2))
    numStim = visual.TextStim(win, font="Arial", color="white", pos=(0, 0))
    correctStim = visual.TextStim(win, text="CORRECT", color="green", 
                                  font="Arial", pos=(0, 0))
    incorrectStim = visual.TextStim(win, text="INCORRECT", color="red",
                                    font="Arial", pos=(0, 0))                                 
    numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9]
    if fb == True:
        fontSizes=[1.20, 3.00]
    else:
        fontSizes=[1.20, 1.80, 2.35, 2.50, 3.00]
    list= data.createFactorialTrialList({"number" : numbers, 
                                         "fontSize" : fontSizes})
    trials = data.TrialHandler(list, nReps=reps, method='random')
    clock = core.Clock()
    tNum = 0
    resultList =[]
    core.checkPygletDuringWait=True
    startTime = time.perf_counter()
    for trial in trials:
        tNum += 1
        resultList.append(sart_trial(win, fb, omitNum, xStim, circleStim,
                              numStim, correctStim, incorrectStim, clock, 
                              trials.thisTrial['fontSize'], 
                              trials.thisTrial['number'], tNum, bNum, mouse,
                              phoneNum, client, sms, call))
    endTime = time.perf_counter()
    totalTime = endTime - startTime
    for row in resultList:
        row.append(totalTime/tNum)
    print ("\n\n#### Block " + str(bNum) + " ####\nDes. Time Per P Trial: " +
           str(2.05*1000) + " ms\nDes. Time Per Non-P Trial: " +
           str(1.15*1000) + " ms\nActual Time Per Trial: " +
           str((totalTime/tNum)*1000) + " ms\n\n")
    return resultList
    
def sart_trial(win, fb, omitNum, xStim, circleStim, numStim, correctStim, 
               incorrectStim, clock, fontSize, number, tNum, bNum, mouse,
               phoneNum, client, sms, call):
    startTime = time.perf_counter()
    alertSent = 0
    alertType = "NA"
    mouse.setVisible(0)
    respRt = "NA"
    numStim.setHeight(fontSize)
    numStim.setText(number)
    numStim.draw()
    event.clearEvents()
    clock.reset()
    stimStartTime = time.perf_counter()
    win.flip()
    xStim.draw()
    circleStim.draw()
    waitTime = .25 - (time.perf_counter() - stimStartTime)
    core.wait(waitTime, hogCPUperiod=waitTime)
    maskStartTime = time.perf_counter()
    win.flip()
    if tNum in [4, 93, 182, 271]:
        alertSent = 1
        if sms == True:
            alertType = "SMS"
        elif call == True:
            alertType = "Call"
        else:
            alertType = "No Alert"
        """t = Thread(target=send_alert, args=(call, sms, client, 
                                                      phoneNum))
        t.start()"""
    waitTime = .90 - (time.perf_counter() - maskStartTime)
    core.wait(waitTime, hogCPUperiod=waitTime)
    allKeys = event.getKeys(timeStamped=clock)
    if len(allKeys) != 0:
        respRt = allKeys[0][1]
    if len(allKeys) == 0:
        if omitNum == number:
            respAcc = 1
        else:
            respAcc = 0                
    else:
        if omitNum == number:
            respAcc = 0
        else:
            respAcc = 1
    if fb == True:
        if respAcc == 0:
            incorrectStim.draw()
        else:
            correctStim.draw()
        stimStartTime = time.perf_counter()
        win.flip()
        waitTime = .90 - (time.perf_counter() - stimStartTime)
        core.wait(waitTime, hogCPUperiod=waitTime)
        win.flip()
    endTime = time.perf_counter()
    totalTime = endTime - startTime
    global alertStatus
    return [str(bNum), str(tNum), str(alertSent), str(alertType), str(number),
            str(omitNum), str(respAcc), str(respRt), str(startTime), 
            str(endTime), str(totalTime), str(alertStatus)]

def send_alert(call, sms, client, phoneNum):
    currentCall = "NA"
    if call == True:
        currentCall = client.calls.create(to=phoneNum, from_="ENTER NUMBER HERE", 
                                   url=("http://twimlets.com/holdmusic?Buck" +
                                        "et=com.twilio.music.ambient"), 
                                        timeout=60)                                       
    elif sms == True:
        message = client.sms.messages.create(to=phoneNum, from_="ENTER NUMBER HERE",
                                             body=str("Hello"))
    startTime = time.perf_counter()
    while(1):
        delay(sms, call, client, currentCall)
        #core.wait(1) #TODO - fix
        time.sleep(1)
        endTime = time.perf_counter() - startTime
        if endTime > 70:
            break
        
def delay(sms, call, client, currentCall):
    global alertStatus
    if call == True:
        callInfo = client.calls.get(currentCall.sid)    
        alertStatus = callInfo.status
    elif sms == True:
        alertStatus = "NA"
    else:
        alertStatus = "NA"

def main():
    sart(reps=1, omitNum=3, practice=True,      
         path=("testest"))

if __name__ == "__main__":
    main()