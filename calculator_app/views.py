from calculator_app.helpers import calculate_bill, date_verify, delete_bill, room_verify, handle_uploaded_file, calculate_urikake, calculate_total_amount
from . import views
from django.http import HttpResponseRedirect
from re import template
from django.template import loader
from .models import Room, Electric, Water, Gas
from django.db.models import F
from django.contrib.auth.models import User, auth
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.datastructures import MultiValueDictKeyError
from django.shortcuts import render, redirect
#from django.core.mail import send_mail
import datetime

def home(request):
    return render(request, "home.html")

@login_required(login_url='/login/')
def contact(request):
    return render(request, "contact.html")

def login(request):
    if request.method != "POST":
        return render(request, "login.html")
    else:
        auth.logout(request)
        
        # Guest login
        if len(request.POST) < 3:

            user = auth.authenticate(username=request.POST["username"], password="guestlogin")
            if user == None:
                messages.info(request, "開発者がこのアクセスを拒否しています")
                return render(request, "guest.html")

            request.session.set_expiry(600)
            auth.login(request, user)

            return redirect(home)

        username = request.POST["username"]
        pw = request.POST["password"]
        user = auth.authenticate(username=username,password=pw)

        if user != None:

            request.session.set_expiry(1800)
            auth.login(request, user)

            return redirect(home)

        else:
            
            messages.info(request, "ログイン情報が合ってないぞ")
            return redirect(login)

def logout(request):
    auth.logout(request)
    return redirect(home)

#@login_required(login_url='/login/')
#def comment(request):
    if request.method != "POST":
        messages.error(request, "Don't you dare try be cheeky :)")
        return render(request, "error.html")
    else:
        subject = "BOT: コメントからのメール"
        mail = request.POST["comment"]
        send_mail(subject, mail, "BOT", ["rochefort0717@hotmail.com"], fail_silently=False)
        return render(request, home)

@login_required(login_url='/login/')
def index(request):
    electric = Electric.objects.all().values().order_by('date_electric_start')
    water = Water.objects.all().values().order_by('date_water_start')
    gas = Gas.objects.all().values().order_by('date_gas_start')
    return render(request, "index.html", context={"electric":electric, "water":water, "gas":gas})

def register(request):

    if request.method != "POST":
        return render(request, "register.html")
    else:
        username = request.POST['username']
        phone_number = request.POST['phoneNumber']
        pw = request.POST['password']
        confirm_pw = request.POST['confirmPassword']
        if pw != confirm_pw:
            messages.info(request, "両方のパスワードは一致してないぞ")
            return redirect(register)
        elif len(pw) < 6:
            messages.info(request, "パスワードの長さはあなたの身長より短いぞ")
            return redirect(register)
        elif phone_number != "0267410334":
            messages.info(request, "電話番号が合ってないぞ")
            return redirect(register)
        else:
            if User.objects.filter(username=username).exists():
                messages.info(request, "ユーザーネームは既に存在してるぞ")
                return redirect(register)
            else:
                user = User.objects.create_user(username=username, password=pw)
                user.save()
                auth.logout(request)
        context = {'username':username,}
        return render(request, "registered.html", context)


@login_required(login_url='/login/')
def newinput(request):
    if request.method != "POST":
        return render(request, "newinput.html")
    else:
        if "electric_save" in request.POST:

            # raise error for empty date or invalid date input            
            try:
                start_date = datetime.datetime.strptime(request.POST["electric_date_start"], "%Y-%m-%d").date()
                end_date = datetime.datetime.strptime(request.POST["electric_date_end"], "%Y-%m-%d").date()
            except ValueError:
                messages.error(request, "電気代の日付は入力されてないぞ")
                return render(request, "error.html")

            diff = abs((end_date-start_date).days)
            # add 1 to date difference as the first date also count
            diff += 1

            # raise error if diff is smaller than 20 days 
            # (electric bill will always be about a month, although sometimes less than 27 days, so just roughly)
            if diff < 20 or (end_date < start_date):
                messages.error(request, "電気代の日付の期間は足りてないぞ（最低限20日分）")
                return render(request, "error.html")

            # check if the dates from start to end is already in DB
            # TODO: algorithm input
            if date_verify("electric", start_date, end_date) == False:
                messages.error(request, "電気代：この期間の日付は既に登録されてるぞ")
                return render(request, "error.html")

            amount = {
                "A":request.POST["amount_a"], 
                "B":request.POST["amount_b"], 
                "C":request.POST["amount_c"],
                "D":request.POST["amount_d"],
                "E":request.POST["amount_e"],
                "F":request.POST["amount_f"],
                }
            
            # raise error for empty input
            for key, value in amount.items():
                if value == "":
                    error_message = "部屋" + key + "の金額がないぞ"
                    messages.error(request, error_message)
                    return render(request, "error.html")

            # add data to DB
            for i in range(diff):
                data = Electric(
                    date_electric_start = start_date,
                    date_electric_end = end_date,
                    room_A = amount["A"],
                    room_B = amount["B"],
                    room_CShare = amount["C"],
                    room_D = amount["D"],
                    room_E = amount["E"],
                    room_F = amount["F"]
                )
                data.save()
                
            return render(request, "inputed.html", context= {"electric":"電気代"})

        elif "water_save" in request.POST:
            water_date_start = request.POST["water_date_start"]
            water_date_end = request.POST["water_date_end"]
            amount_water = request.POST["amount_water"]
            
            try:
                start_date = datetime.datetime.strptime(water_date_start, "%Y-%m-%d").date()
                end_date = datetime.datetime.strptime(water_date_end, "%Y-%m-%d").date()
            except ValueError:
                messages.error(request, "水道代の日付は入力されてないぞ")
                return render(request, "error.html")

            diff = abs((end_date-start_date).days)
            diff += 1

            # raise error for empty date or invalid date input
            # roughly 25 days minimum to just avoid some missinput
            if diff < 25 or  (water_date_end < water_date_start):
                messages.error(request, "水道代の日付の期間は足りてないぞ（最低限25日分）")
                return render(request, "error.html")
            
            # check if the dates is already in DB
            if date_verify("water", start_date, end_date) == False:
                messages.error(request, "水道代：この期間の日付は既に登録されてるぞ")
                return render(request, "error.html")
            
            if amount_water == "":
                messages.error(request, "水道代の金額がないぞ")
                return render(request, "error.html")

            data = Water(
                date_water_start = start_date,
                date_water_end = end_date,
                amount = amount_water
                )
            data.save()

            return render(request, "inputed.html", context={"water":"水道代"})
        
        elif "gas_save" in request.POST:
            gas_date_start = request.POST["gas_date_start"]
            gas_date_end = request.POST["gas_date_end"]
            amount_gas = request.POST["amount_gas"]

            try:
                start_date = datetime.datetime.strptime(gas_date_start, "%Y-%m-%d").date()
                end_date = datetime.datetime.strptime(gas_date_end, "%Y-%m-%d").date()
            except ValueError:
                messages.error(request, "ガス代の日付は入力されてないぞ")
                return render(request, "error.html")

            diff = abs((end_date-start_date).days)
            diff += 1

            # raise error for empty date or invalid date input
            if diff < 25 or gas_date_end < gas_date_start:
                messages.error(request, "ガス代の日付の期間は足りてないぞ（最低限25日分）")
                return render(request, "error.html")

            # check if dates is already in DB
            if date_verify("gas", start_date, end_date) == False:
                messages.error(request, "ガス代：この期間の日付は既に登録されてるぞ")
                return render(request, "error.html")

            if amount_gas == "":
                messages.error(request, "ガス代の金額がないぞ")
                return render(request, "error.html")

            data = Gas(
                date_gas_start = start_date,
                date_gas_end = end_date,
                amount = amount_gas
                )
            data.save()
            start_date += datetime.timedelta(days=1)

            return render(request, "inputed.html", context={"gas":"ガス代"})

@login_required(login_url='/login/')
def history(request):
    if request.method != "POST":
        return redirect(home)
    else:
        if "search" in request.POST:
            if request.POST["search"] == "電気代検索":
                data = request.POST["selectElectricMonth"].split("|")
                try:
                    date_start = datetime.datetime.strptime(data[0], '%B %d, %Y').strftime('%Y-%m-%d')
                except ValueError:
                    data[0] = data[0].split(".")[0] + data[0].split(".")[1]
                    date_start = datetime.datetime.strptime(data[0], '%b %d, %Y').strftime('%Y-%m-%d')
                room = calculate_bill("electric", date_start)
                # return is at the end of this function

            elif request.POST["search"] == "水道代検索":
                data = request.POST["selectWaterMonth"].split("|")
                try:
                    date_start = datetime.datetime.strptime(data[0], '%B %d, %Y').strftime('%Y-%m-%d')
                except ValueError:
                    data[0] = data[0].split(".")[0] + data[0].split(".")[1]
                    date_start = datetime.datetime.strptime(data[0], '%b %d, %Y').strftime('%Y-%m-%d')
                room = calculate_bill("water", date_start)
                # return is at the end of this function

            elif request.POST["search"] == "ガス代検索":
                data = request.POST["selectGasMonth"].split("|")
                try:
                    date_start = datetime.datetime.strptime(data[0], '%B %d, %Y').strftime('%Y-%m-%d')
                except ValueError:
                    data[0] = data[0].split(".")[0] + data[0].split(".")[1]
                    date_start = datetime.datetime.strptime(data[0], '%b %d, %Y').strftime('%Y-%m-%d')
                room = calculate_bill("gas", date_start)
                # return is at the end of this function

        # query for delete
        elif "electric_del" in request.POST:
            data = request.POST["selectElectricMonth"].split("|")
            try:
                date_start = datetime.datetime.strptime(data[0], '%B %d, %Y').strftime('%Y-%m-%d')
            except ValueError:
                data[0] = data[0].split(".")[0] + data[0].split(".")[1]
                date_start = datetime.datetime.strptime(data[0], '%b %d, %Y').strftime('%Y-%m-%d')
            # call delete bill function
            delete_bill("electric", date_start)
            deleted = str(date_start) + "の電気代データは削除されたぞ" 
            return render(request, "inputed.html", context={"deleted":deleted})

        elif "water_del" in request.POST:
            data = request.POST["selectWaterMonth"].split("|")
            try:
                date_start = datetime.datetime.strptime(data[0], '%B %d, %Y').strftime('%Y-%m-%d')
            except ValueError:
                data[0] = data[0].split(".")[0] + data[0].split(".")[1]
                date_start = datetime.datetime.strptime(data[0], '%b %d, %Y').strftime('%Y-%m-%d')
            # call delete bill function
            delete_bill("water", date_start)
            deleted = str(date_start) + "の水道代データは削除されたぞ" 
            return render(request, "inputed.html", context={"deleted":deleted})

        elif "gas_del" in request.POST:
            data = request.POST["selectGasMonth"].split("|")
            try:
                date_start = datetime.datetime.strptime(data[0], '%B %d, %Y').strftime('%Y-%m-%d')
            except ValueError:
                data[0] = data[0].split(".")[0] + data[0].split(".")[1]
                date_start = datetime.datetime.strptime(data[0], '%b %d, %Y').strftime('%Y-%m-%d')

            # call delete bill function
            delete_bill("gas", date_start)
            deleted = str(date_start) + "のガス代データは削除されたぞ" 
            return render(request, "inputed.html", context={"deleted":deleted})

        elif "room_query" in request.POST:
            date_start = request.POST["room_date_start"]
            date_end = request.POST["room_date_end"]

            # check if start and end dates are inserted
            try:
                date_start = datetime.datetime.strptime(date_start, "%Y-%m-%d").date()
                date_end = datetime.datetime.strptime(date_end, "%Y-%m-%d").date()
            except ValueError:
                messages.error(request, "日付がないぞ")
                return render(request, "error.html")

            # query DB for the rooms within the date range
            # room has to be dict similar to the what returned by calculate_bill
            room = Room.objects.filter(date_room__range=(date_start, date_end)).values().order_by("date_room")
            for rooms in room:
                del rooms["amount_electric_id"]
                del rooms["amount_water_id"]
                del rooms["amount_gas_id"]
                for key, value in rooms.items():
                    if value == None:
                        rooms[key] = "空室"

        # this is the end of function
        # read db for user to search and query for
        electric = Electric.objects.all().values().order_by('date_electric_start')
        water = Water.objects.all().values().order_by('date_water_start')
        gas = Gas.objects.all().values().order_by('date_gas_start')
                     
        # type in context is the search type(electric, water, gas), and cut the 4th and 5th index because we don't need the word 検索(eg: 電気代検索)
        # this only work if user use those 検索, not delete or room query
        if "search" in request.POST:
            
            # get the total amount of the payment for user query
            total_amount = calculate_total_amount(request.POST["search"][:3], date_start)
   
            context = {"query":room, "total_amount":total_amount, "electric":electric, "water":water, "gas":gas, "month_start":data[0], "month_end":data[1], "type":request.POST["search"][:3]}
        else:
            context = {"query":room, "electric":electric, "water":water, "gas":gas}

        return render(request, "history.html", context=context)

@login_required(login_url='/login/')
def roominput(request):
    if request.method != "POST":
        return render(request, "roominput.html")
    else:
        # check if POST is accessed by clicking the save room data button
        if not request.POST["room_save"]:
            messages.error(request, "保存ボタンからのアクセスではないぞ")
            return render(request, "error.html")
        else:
            # create an empty list to store dict of room datas
            room_data = []
            invalid_data = []
            dict_temp = {}
            last_num = 0
            # filter and append room_data list with dict data of each room
            for key, value in request.POST.items():
                last_char = key[-1]
                if last_char.isdigit():

                    # add key:value pairs to dict
                    if int(last_char) == last_num:
                        dict_temp[key] = value

                    # if the last num is different, we have the full set of room data at the moment
                    # if list valid, append to room_data and clear dict_temp
                    # if not valid, append to invalid_data and clear dict_temp
                    else:
                        # verify data

                        if room_verify(dict_temp=dict_temp) == False:
                            # append to invalid_data otherwise
                            invalid_data.append(dict_temp)

                            # initialize dict and add the current key value to it
                            dict_temp = {}
                            dict_temp[key] = value

                            # lastly, assign the last_num of next data
                            last_num = int(last_char)
                            # ignore the codes below and continue the for loop
                            continue

                        # append valid data to room_data list
                        room_data.append(dict_temp)
                        # initialize dict and add the current key value to it
                        dict_temp = {}
                        dict_temp[key] = value

                        # lastly, assign the last_num of next data
                        last_num = int(last_char)

            # we have the last dict_temp at the end of the for loop
            else:
                # verify and filter it
                if room_verify(dict_temp=dict_temp) == False:
                    # append to invalid_data if invalid input
                    invalid_data.append(dict_temp)
                else:
                # append valid data to room_data list
                    room_data.append(dict_temp)
            
            # input data to DB and render invalid data to notify user
            for i in range(len(room_data)):
                dict_temp = room_data[i]
                room_number = dict_temp[list(dict_temp)[0]]
                room_name = dict_temp[list(dict_temp)[1]]

                # if user input is "none" or "空室"
                # clear the name field in DB
                if room_name.lower() == "none" or room_name == "空室":
                    room_name = None

                # abstract the date infos and find the days
                start_date = datetime.datetime.strptime(dict_temp[list(dict_temp)[2]], "%Y-%m-%d").date()
                end_date = datetime.datetime.strptime(dict_temp[list(dict_temp)[3]], "%Y-%m-%d").date()
                diff = abs((end_date-start_date).days)
                diff += 1
                
                
                # append room num and name for each day into DB
                date_temp = start_date
                # a dict contains date, room number and name to insert into models.Room
                
                while (date_temp<=end_date):
                    dict_data = {"date_room":date_temp, "room_number":room_number, "room_name":room_name}
                    try:
                        data = Room.objects.get(date_room=date_temp)
                    except Room.DoesNotExist:
                        data = Room()
                        setattr(data, "date_room", dict_data["date_room"]),
                        setattr(data, dict_data["room_number"], dict_data["room_name"])
                        data.save()
                    else:
                        setattr(data, "date_room", dict_data["date_room"])
                        setattr(data, dict_data["room_number"], dict_data["room_name"])
                        data.save()
                    date_temp += datetime.timedelta(days=1)


            return render(request, "inputed.html", {"room_data":room_data, "invalid_data":invalid_data})

@login_required(login_url='/login/')
def urikake(request):

    if request.method != "POST":
        return render(request, "urikake.html")
    else:
        try:
            file = request.FILES["file_urikake"]
        except MultiValueDictKeyError:
            messages.info(request, "ファイルがないぞ")
            return redirect(urikake)

        # process file_data
        file_data = handle_uploaded_file(file)

        # if handle_uploaded_file function returns dict(s) in the list, means it processed something
        # else it will return error message in the list which is a string
        if type(file_data[0]) != list:
            messages.info(request, file_data[0])
        else:
            list_urikake = calculate_urikake(file_data)
            # calculate_urikake function returns a list of dict
            # else it returns a list contain a string of error message
            if type(list_urikake[0]) != dict:
                messages.info(request, list_urikake[0])
                return redirect(urikake)
            return render(request, "urikaked.html", {"list_urikake":list_urikake})

        return redirect(urikake)

@login_required(login_url='/login')
def manual(request):
    return render(request, "manual.html")

def guest(request):
    return render(request, "guest.html")