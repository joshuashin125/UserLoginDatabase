# CURRENT ISSUES TO DEBUG
# obtain the correct username and matching password
# print obtained values to html
# get the flag variables to work


# Import statements
import pandas as pd
import csv
from flask import Flask, render_template, request
import sys
import pymsgbox
import requests, json

# Sets dataframe and other variables
userData = pd.read_csv('chatbot_spreadsheet.csv')
cityOfChoice = ""
stateOfChoice = ""
app = Flask(__name__)


@app.route("/", methods = ['POST', 'GET'])
def login():
    global cityOfChoice
    global stateOfChoice

    if request.method == 'POST':
        option = int(request.form["choice"])
        usernameVar = str(request.form["username"])
        passwordVar = str(request.form["password"])
        newUser = str(request.form["newUs"])
        newPassword = str(request.form["newPw"])
        newCity = str(request.form["newMsgOne"])
        newState = str(request.form["newMsgTwo"])
        toBeDel = str(request.form["deletion"])
        extraData = str(request.form["dataChoice"])
        
        if(option == 1):
            exists = checkUser(usernameVar)
            if(exists != -1):
                if (passwordCheck(usernameVar, passwordVar, exists)):
                    if(extraData == "yes"):
                        tempInF = float(getWeather(usernameVar))
                        tempInF = (1.8 * (tempInF - 273)) + 32
                        tempInF = round(tempInF, 2)
                        infNum = int(getCovidData(usernameVar))
                        return render_template('userinfo.html', variable = cityOfChoice, variable2 = stateOfChoice, temperature = tempInF, infected = infNum)
                    else:
                        return render_template('userinfo.html', variable = cityOfChoice, variable2 = stateOfChoice, temperature = "INVALID", infected = "INVALID")
                else:
                    pymsgbox.alert('Wrong Login try again!')
                    return render_template('index.html')
                    #return f"<p>Incorrect Login: Please retry after pressing back button {cityOfChoice}</p>"
            else:
                pymsgbox.alert('User does not exist try again!')
                return render_template('index.html')
        
        elif(option == 2):
            addNewUser(newUser, newPassword, newCity, newState)
            return render_template('index.html')
            #return f"<p>User added press back and login</p>"
        
        elif(option == 3):
            terminateUser(toBeDel)
            return render_template('index.html') 
            #return f"<p>user is deleted</p>" 
        else:
            pymsgbox.alert('INVALID OPTION!')
            return render_template('index.html')
            # return f"<p>Not Valid Option</p>"


    else:
        return render_template('index.html')  

# reset the values if logged out
def logout():
    global validUser
    global cityOfChoice
    global stateOfChoice
    validUser = 0
    cityOfChoice = ""
    stateOfChoice = ""

def passwordCheck(usName, passAtt, userIdx):
    # obtains global variables
    global userData
    global cityOfChoice
    global stateOfChoice
    
    if(userIdx != -1):
        temp = str(userData['password'].values[userIdx])
        if(temp == passAtt):
            cityOfChoice = userData['city'].values[userIdx]
            stateOfChoice = userData['state_or_prov'].values[userIdx]
            return True
    else:
        pymsgbox.alert('Incorrect login please try again!')
        return render_template('index.html')
        return False

# add users to database (csv)
def addNewUser(newUs, newPw, cityOne, stateTwo):
    global userData
    
    inputOne = str(newUs)
    inputTwo = str(newPw)
    inputThree = str(cityOne)
    inputFour = str(stateTwo)
    inDb = checkUser(inputOne)

    # checks if user already exists
    if(inDb == -1):
        # creates the new user with info
        new_row = {'username':inputOne, 'password':inputTwo, 'city':inputThree, 'state_or_prov':inputFour}
        # adds new user
        userData = userData.append(new_row, ignore_index=True)
        userData.to_csv('chatbot_spreadsheet.csv', encoding='utf-8', index=False)
        pymsgbox.alert('The account has been added!')
    else:
        pymsgbox.alert('Username already exists try new name!')

# gets rid of a user from database (csv)
def terminateUser(userDelete):
    global userData
    usTmp = str(userDelete)
    idxDel = int(checkUser(userDelete))
    
    if (idxDel !=  -1):
        tmpPass = pymsgbox.password('Enter password to delete!')
        tempPass = str(tmpPass) 
        canDel = passwordCheck(usTmp, tempPass, idxDel)
        if(canDel):
            userData = userData.drop(idxDel)
            userData.to_csv('chatbot_spreadsheet.csv', encoding='utf-8', index=False)
            pymsgbox.alert('The account has been deleted!')
        else:
            pymsgbox.alert('Wrong Password!')
    else:
        pymsgbox.alert('User does not exist!')
        #return f"<p>user does not exist</p>"
    
# weather api function
def getWeather(usParam):
    global userData
    cityIdx = int(checkUser(usParam))
    cityName = str(userData['city'].values[cityIdx])
    
    # Enter your API key here 
    api_key = "d39fdafb120e82c40eba1df9f6157877"
  
    # base_url variable to store url 
    base_url = "http://api.openweathermap.org/data/2.5/weather?"
    complete_url = base_url + "appid=" + api_key + "&q=" + cityName
    response = requests.get(complete_url) 
    x = response.json() 
    if x["cod"] != "404": 
        y = x["main"]  
        current_temperature = y["temp"] 
        return current_temperature
    else:
        return -1

# weather api function
def getCovidData(usParam):
    global userData
    stateIdx = int(checkUser(usParam))
    stateName = str(userData['state_or_prov'].values[stateIdx])
    
    
  
    # base_url variable to store url 
    base_urlCovid = "https://api.covidtracking.com/v1/states/"
    complete_url_covid = base_urlCovid + stateName + "/current.json"
    responseCovid = requests.get(complete_url_covid) 
    c19data = responseCovid.json() 
    if c19data != 0: 
        posVal = c19data["positive"]
        return posVal
    else:
        return -1

# Basic Functions

# Obtains row number of a user within the csv file
def checkUser(nameToFind):
    result = -1
    findUs = -1
    res = str(nameToFind)

     # Loops through users to determine if user exists and obtains user data
    for count in userData['username'].values:
        findUs = findUs + 1
        if(str(count) == res):
            result = findUs
            return int(result)
        
    return int(result)

    
if __name__ == '__main__':
    app.run(debug=True)