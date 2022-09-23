import datetime
from math import ceil
import os
import csv
from calculator_app.models import Electric, Water, Gas, Room, File

# a function that verifies the room input and return boolean
def room_verify(dict_temp):
    # verify first if dict has empty input
    for value in dict_temp.values():
        if value == "":
            return False
        else:
            continue

    start_date = datetime.datetime.strptime(dict_temp[list(dict_temp)[2]], "%Y-%m-%d").date()
    end_date = datetime.datetime.strptime(dict_temp[list(dict_temp)[3]], "%Y-%m-%d").date()
    room_number = dict_temp[list(dict_temp)[0]]

    # verify if start date is smaller than end date
    if start_date > end_date:
        return False

    # verify room number
    for i in range(65, 76):
        if room_number == chr(i):
            break
    else:
        return False

    return True

# validate the input date of electric, water, gas bill
# arguments (bill type, start date, end date)
# return boolean
def date_verify(name, date1, date2):
    date1 -= datetime.timedelta(days=1)
    date2 += datetime.timedelta(days=1)
    if name == "electric":
        bill = Electric.objects.exclude(date_electric_end__lte=date1).exclude(date_electric_start__gte=date2)
        if len(bill) > 0:
            return False
        
    elif name == "water":
        bill = Water.objects.exclude(date_water_end__lte=date1).exclude(date_water_start__gte=date2)
        if len(bill) > 0:
            return False
    elif name == "gas":
        bill = Gas.objects.exclude(date_gas_end__lte=date1).exclude(date_gas_start__gte=date2)
        if len(bill) > 0:
            return False
    else:
        return False
        
    return True

# called by the function "calculate_bill"
# take arguments of bill type and model object
def calculation(type,obj):
    #a list to take the payment details to return at the end
    payment = []
    
    # query the rooms that is in the bill date
    rooms = []
    if type == "gas":
        rooms = Room.objects.filter(amount_gas=obj).values().order_by("date_room")
        total_payment = obj.amount
    elif type == "water":
        rooms = Room.objects.filter(amount_water=obj).values().order_by("date_room")
        total_payment = obj.amount
    elif type == "electric":
        rooms = Room.objects.filter(amount_electric=obj).values().order_by("date_room")
        total_payment = obj.room_A + obj.room_B + obj.room_CShare + obj.room_D + obj.room_E + obj.room_F

   # empty room count
    empty_room = 0

    # occupied room count
    occupied_room = 0
    
    # 3000yen is the payment for every empty room
    empty_room_payment = 3000
    
    # TODO: change logic (empty room only if the room is empty the whole month)
    
    # loop through every day for a room to see if every day is empty
    for num in range(65, 76):
        for i in range(len(rooms)):

            # if room not empty then break the loop to continue for next room
            if not (rooms[i][chr(num)] is None or rooms[i][chr(num)] == "None" or rooms[i][chr(num)] == "空室"):
            # The syntax of condition check below is not working
            #if (rooms[i][chr(num)] is not None) or rooms[i][chr(num)] != "None" or rooms[i][chr(num)] != "空室":
                break

        # if loop completed means the room is empty room throughout the month
        else:
            # increment the empty room count
            empty_room += 1

    # count every day that is occupied/used
    # (even 1 day of use will eliminate the possibility of empty room so no need to worry about empty rooms)
    for num in range(65, 76):
        for i in range(len(rooms)):
            if not (rooms[i][chr(num)] is None or rooms[i][chr(num)] == "None" or rooms[i][chr(num)] == "空室"):
            # The syntax of condition check below is not working
            #if (rooms[i][chr(num)] is not None) or rooms[i][chr(num)] != "None" or rooms[i][chr(num)] != "空室":
                occupied_room += 1

    
    # calculate avg payment for every occupied room/day
    # only electric fee need to acknowledge empty room's fee
    try:
        if type == "electric":
            # average payment for every day = total payment - (empty rooms * 3000) / total days of occupied rooms
            avg_payment = ceil((float(total_payment) - (empty_room*empty_room_payment)) / occupied_room)
        else:
            avg_payment = ceil(float(total_payment) / occupied_room)
    except ZeroDivisionError:
        return payment

    # in every room
    for num in range(65, 76):

        # ready a dict for room to start the loop
        room = {"name":"", "num":"", "payment":0, "date_start":"", "date_end":""}

        # through every day
        for i in range(len(rooms)):

            # assign room name(even if the name is None) to the "name" variable
            name = rooms[i][chr(num)]

            # check if the current list "room"'s index has the same name as current loop in "rooms"
            if room["name"] == name:
                if not ((name is None) or name == "None" or rooms[i][chr(num)] == "空室"):
                #if (name is not None) or name != "None" or rooms[i][chr(num)] != "空室":
                    room["payment"] += avg_payment
                room["date_end"] = rooms[i]["date_room"]

            # if the name is different, the person living in the room is changed
            # current room dict has the total payment of previous person
            # append the data to list and reset the list to current person
            else:

                # append dict into the list
                if room["name"] != "":
                    payment.append(room)
                
                # update current value in to dict
                room = {}
                room["name"] = name
                room["num"] = chr(num)
                if ((name is None) or name == "None" or name == "空室") is True:
                    room["payment"] = 0
                else:
                    room["payment"] = avg_payment
                room["date_start"] = rooms[i]["date_room"]
                room["date_end"] = rooms[i]["date_room"]
        
        # at the end of the loop through every day, we will later move to the next room,
        # means have to append the last person of the current room at the end of the month into the list
        else:
            payment.append(room)
        
    # create a list to store the index of list "payment" for room with 0 yen payment
    # so that we can pop those index later
    room_zero_payment = []

    for i in range(len(payment)):
        try:
            if (payment[i]["name"] is None) or payment[i]["name"] == "None" or rooms[i][chr(num)] == "空室":
                payment[i]["name"] = "空室"

                # while name is None, and date start to end is the whole month and under calculation of electric bill,
                # it matches the empty room condition, so the payment will be 3000 for that room
                if payment[i]["date_start"] == rooms[0]["date_room"] and payment[i]["date_end"] == rooms[len(rooms)-1]["date_room"] and type == "electric":
                    payment[i]["payment"] = empty_room_payment

                # if the room payment is 0 yen, than we remove the room from list
                # add the index number to room_zero_payment and pop the list "payment" after this loop finish
                if payment[i]["payment"] == 0:
                    room_zero_payment.append(i)

        # if we remove an item in the list payment, the for loop will eventually go beyond the index range
        # so we have to break the loop from that error
        except IndexError:
            break

    return payment

# insert the Room table with the given bill type dates
# then call the function "calculation" to calculate the bill
# arguments (bill type, start date)
# return a list
def calculate_bill(name, date):
    # payment list contains payments of rooms for the particular dates 
    payment = []
    datesplit = date.split("-")
    date = datetime.date(int(datesplit[0]), int(datesplit[1]), int(datesplit[2]))
    if name == "electric":
        electric = Electric.objects.get(date_electric_start=date)
        end_date = electric.date_electric_end

        while (date<=end_date):
            try:
                room = Room.objects.get(date_room=date)
            except Room.DoesNotExist:
                room = Room(date_room=date, amount_electric=electric)
                room.save()
            else:
                room.amount_electric = electric
                room.save()
            date += datetime.timedelta(days=1)
        payment = calculation("electric", electric)

    elif name == "water":
        water = Water.objects.get(date_water_start=date)
        end_date = water.date_water_end

        while (date<=end_date):
            try:
                room = Room.objects.get(date_room=date)
            except Room.DoesNotExist:
                room = Room(date_room=date, amount_water=water)
                room.save()
            else:
                room.amount_water = water
                room.save()
            date += datetime.timedelta(days=1)
        payment = calculation("water", water)

    elif name == "gas":
        gas = Gas.objects.get(date_gas_start=date)
        end_date = gas.date_gas_end

        while (date<=end_date):
            try:
                room = Room.objects.get(date_room=date)
            except Room.DoesNotExist:
                room = Room(date_room=date, amount_gas=gas)
                room.save()
            else:
                room.amount_gas = gas
                room.save()
            date += datetime.timedelta(days=1)
        payment = calculation("gas", gas)

    return payment

# query database and then delete then particular row
# arguments (bill type, start date)
# return nothin
def delete_bill(name, date):
    datesplit = date.split("-")
    date = datetime.date(int(datesplit[0]), int(datesplit[1]),int(datesplit[2]))
    if name == "electric":
        electric = Electric.objects.get(date_electric_start=date)
        electric.delete()
        return
    elif name == "water":
        water = Water.objects.get(date_water_start=date)
        water.delete()
        return
    elif name == "gas":
        gas = Gas.objects.get(date_gas_start=date)
        gas.delete()
        return

# handle the file uploaded from urikake
# return a list
# when the list is valid: dicts of data
# else when invalid: error message
def handle_uploaded_file(file):
    # validate if the file uploaded is csv
    file_data = []
    if file.content_type != "text/csv":
        file_data.append("ファイルはCSVではないぞ")
    else:
        # save file to storage
        try:
            file_instance = File.objects.get(name="BillBalanceList.csv")
        except File.DoesNotExist:
            File(name="BillBalanceList.csv", file=file).save()
        else:
            file_instance.file = file
            file_instance.save()

        #TODO
        file_instance = File.objects.get(name="BillBalanceList.csv")
        with open(file_instance.file.path, "r") as csvfile:
            rows = csv.reader(csvfile)
            for row in rows:
                file_data.append(row)

    return file_data

def calculate_urikake(file_data):
    list_urikake = []

    # check if it's the right csv file that uploaded before moving on
    if file_data[0] != ['Payment', 'PaymentDetail', 'BillingAddressCode', 'IssueTime', 'BillNumber', 'PaymentAmount', 'RoomNumber', 'CheckIn', 'Nights', 'CheckOut', 'CourseNumber', 'BillingName', 'IssueUserName', 'UpdateHostName', 'TotalAmount', 'TotalPersonCount', 'PaymentMethodSequence', 'PaymentDetailSequence', 'Key', 'TimeSortKey', 'AccountDate']:
        file_data[0]
        list_urikake.append("このファイルは売掛のファイルではないぞ")
    else:
        for row in file_data:
            if row[0]=="売掛" and (row[1]=="売掛途中精算" or row[1]=="売掛精算"):

                # store the datas in a dict in the list
                for i in range(len(list_urikake)):

                    # every list_urikake element should be something like below
                    # {"OTA":row[2], "count":1, "amount":float(row[14])}
                    ota = list_urikake[i]["OTA"]

                    # look for the similar OTA name in row[2]
                    # by comparing them with the first 2 character (like "じゃらん事前決済" and "じゃらんポイント" has the same first 2 chr which is "じゃ")
                    if ota.find(row[2][:2], 0, 2) != -1:
                        list_urikake[i]["count"] += 1
                        list_urikake[i]["amount"] += float(row[14])
                        break
                    else:
                        continue
                else:
                    list_urikake.append({"OTA":row[2], "count":1, "amount":float(row[14])})

        # add the counts and total amounts to the last of the list
        counts = 0
        amounts = 0
        for i in range(len(list_urikake)):
            counts += list_urikake[i]["count"]
            amounts += list_urikake[i]["amount"]
        list_urikake.append({"OTA":"Total", "count":counts, "amount":amounts})
    return list_urikake

    # function to calculate the total amount of bill from user query (basically only electric that needs calculate)
    # takes arguments type bill and date start
def calculate_total_amount(name, date):

    total_amount = 1

    datesplit = date.split("-")
    date = datetime.date(int(datesplit[0]), int(datesplit[1]), int(datesplit[2]))
    
    if name == "電気代":
        
        electric = Electric.objects.get(date_electric_start=date)
        total_amount = electric.room_A + electric.room_B + electric.room_CShare + electric.room_D + electric.room_E + electric.room_F

    elif name == "水道代":

        water = Water.objects.get(date_water_start=date)
        total_amount = water.amount

    elif name == "ガス代":

        gas = Gas.objects.get(date_gas_start=date)
        total_amount = gas.amount

    return total_amount