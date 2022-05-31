import requests
import bs4
import pandas as pd
"""Scraping function that finds an element with the specified id - y in specified page, in this case slud_contents
If the function doesnt find an element with the id - y, it returns x as NoneType and prints out which criteria it 
couldnt find in the page"""
def findScrape(y):
    try:
        x = slud_contents.find_all(id=y)[0].text
        return x
    except:
        print("could not find specified criteria:",y)
        x=None
        return x

#variable and variable datatype testing function
def printType(x):
    print(x, type(x)) 

col =["Links","Teksts","Atrasanas vieta","Stavs","Istabu skaits","Serija","Kvadratura","Cena","Datums"]
data = pd.DataFrame(columns=col)
p = 1
x=1

while True:
    page_address = f"https://www.ss.lv/lv/real-estate/flats/riga/yugla/sell/page{p}.html"
    page = requests.get(page_address)
    """Next if statement checks if the page that was just scraped has been through any redirects.
    If it has, the page.history would have an array with all the redirect codes, usually 302 and 301,
    and the if statement would jump to the else statement which would print out End of pages and break
    the while loop that the code is being run in.
    If it hasn't went through any redirects, the array will be empty and code will resume as normal"""
    if len(page.history)==0:
        page = requests.get(page_address)
        if page.status_code ==200:
            p+=1
            page_contents = bs4.BeautifulSoup(page.content, "html.parser")

            found = page_contents.find_all(class_="am", href=True) #Finds all the elements with the class "am" and with the attribute href 
            links = []
            for i in found:
                if i.text:
                    links.append(i["href"])#appends all of the links into a single array
            """Next loop iterates through all the links in the links array,
            and since the links that are in the class 'am' tags are local, 
            you have to add it to the base url, in this case its https://www.ss.lv/"""
            for link in range(len(links)):
                page = requests.get("https://www.ss.lv/"+links[link])
                print(x)
                x+=1
                print("https://www.ss.lv"+links[link])
                if page.status_code==200:
                    slud_contents=bs4.BeautifulSoup(page.content, "html.parser")

                    '''Finding all the variables that make up location: city,region,street
                    street needs to be found by finding the child tag <b> since if there is 
                    a map attached to the street it will print out, for example - "Juglas iela 5 [karte]" 
                    if it doesnt find a street element, it sets it to None just like the findScrape()
                    function defined at the start of the code. ' '.join(filter(None, [])) joins all the 
                    elements in an array filtering out any NoneType values so city+region+street(NoneType)
                    would become just city+region '''

                    try:
                        street = slud_contents.find_all(id="tdo_11")[0].findChild("b").text
                    except:
                        street = None

                    city = findScrape("tdo_20")
                    region = findScrape("tdo_856")
                    floor = findScrape("tdo_4")
                    rooms = findScrape("tdo_1")
                    area = findScrape("tdo_3")
                    price = findScrape("tdo_8")
                    series = findScrape("tdo_6")
                    
                    location = ', '.join(filter(None, [city,region,street]))
                    """The text is stored in one div element that has the id of 'msg_div_msg', but 
                    the element also has a table stored in it with all the prior city, region, rooms, etc
                    data in it. To get just the text out we have to remove the table row element <tr> which contains
                    the text for the table from the bs4 object with the <tag>.extract() function
                    If there is no text in page under the msg_div_msg id, return the text as NoneType"""
                    text = slud_contents.find_all(id = "msg_div_msg")[0]
                    try:
                        text.tr.extract()
                    except:
                        text = None 
                    
                    if text != None:
                        text = text.text
                    """get the date by finding elements with 2 different attributes,
                    since there is an another element with the class msg_footer and after that 
                    convert it to text using .text and then replace the 'Datums: ' starting text with 
                    an empty character"""
                    date = slud_contents.find("td", attrs={"class":"msg_footer","align":"right"}).text.replace("Datums: ","")
                    #append all of the scraped data into a pandas dataframe 
                    data = data.append({"Links":"https://www.ss.lv"+links[link],
                                        "Teksts":text,
                                        "Atrasanas vieta":location,
                                        "Stavs":floor,
                                        "Istabu skaits":rooms,
                                        "Serija":series,
                                        "Kvadratura":area,
                                        "Cena":price,
                                        "Datums":date}, ignore_index=True)
                else:
                    print("error", page.status_code)
    else:
        print("End of pages: ", page.history)
        break

#contert the data pandas dataframe to an excel file with the name dati.xlsx
data.to_excel('dati.xlsx', index=False)
print("File saved as dati.xlsx")


   
