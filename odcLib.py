#Version 1.0 Salvador Cisneros G. 15/Mar/2021
#Version 1.1 Salvador Cisneros G. 30/Nov/2024 .- Se gregan funciones para casar ensambles

import requests

lunar_port = "8312"
powin_port = "8292"
lunar_serverName = "DES_LUN"
powin_serverName = "DESPOW"
rootUrl = "http://"+"cmxapp37:"+lunar_port+"/"+lunar_serverName+"/"


def processCheck(serialNumber):
    url=rootUrl+"check.asp?sn="+serialNumber
    response = requests.get(url)
    #print(response.text)
    #print(url)
    #print("Process check: ",response.text)
    response.close()
    return(response.text)



def getTicket(serialNumber):
    url=rootUrl+"getticket2.asp?sn="+serialNumber
    response = requests.get(url)
    print(response.text)
    response.close()
    return(response.text)

    
def sendPass(ticketNumber, serialNumber, station, tester, user):

    url=rootUrl+"result.asp"
    headers = {'Content-Type':'text/xml'}

    xmlQuery = f"""<?xml version=\"1.0\"?>
    <test>
          <ticket> {ticketNumber} </ticket>
          <sn> {serialNumber} </sn>
          <station> {station} </station>
          <testername> {tester} </testername>
          <user> {user} </user>
          <result>P</result>
          <description> {station} </description>
          <parameter>
                     <par name=\"SN\">{serialNumber}</par>
          </parameter>
    </test>"""
    
    response = requests.post(url, data=xmlQuery, headers=headers)
    print(url)
    print (response.text);
    #print(response.request.url)
    #print(response.request.body)
    #print(response.request.headers)
    response.close()
    return(response.text)
    
def sendFail(ticketNumber, serialNumber, station, tester, user, failDetails,failCode):

    url=rootUrl+"result.asp"
    headers = {'Content-Type':'text/xml'}

    xmlQuery = f"""<?xml version=\"1.0\"?>
    <test>
          <ticket> {ticketNumber} </ticket>
          <sn> {serialNumber} </sn>
          <station> {station} </station>
          <testername> {tester} </testername>
          <user> {user} </user>
          <result>F</result>
          <description> {station} </description>
          <failure>
            <failcode code=\"{failCode}\">
                <description>{failDetails}</description>
            </failcode>
        </failure>
    </test>"""
    
    response = requests.post(url, data=xmlQuery, headers=headers)
    print(url)
    print (response.text)
    #print(response.request.url)
    #print(response.request.body)
    #print(response.request.headers)
    response.close()
    return(response.text)    
    
def checkStatus(serial):
    url=rootUrl+"process.asp?process=true&ticket="+serial
    response = requests.get(url)
    #print(response.text)
    response.close()
    return(response.text)
    
def processTicket(ticket):
    url=rootUrl+"process.asp?ticket="+ticket+"&process=true"
    print(url)
    response = requests.get(url)
    print(response.text)
    response.close()
    return(response.text)

    
def clearTicket(ticket,serial):
    url=rootUrl+"clearTicket.asp?sn="+serial+"&ticket="+ticket
    
    response = requests.get(url)
    print(url)
    print(response.text)
    response.close()

def getParameter(serialNumber):
    url=rootUrl+"getParameter.asp?PROFILE=GET_VSENSE_PROFILE&SN="+serialNumber
    response = requests.get(url)
    response.close()
    return(response.text)


def getParameter2(serialNumber):
    url = rootUrl + "getParameter.asp?PROFILE=GET_VSENSE_PROFILE&SN=" + serialNumber
    try:
        # Hacer la solicitud con un timeout de 10 segundos
        response = requests.get(url, timeout=10)
        response.raise_for_status()  # Lanza una excepción para códigos de estado HTTP 4xx/5xx
        return response.text
    except requests.exceptions.Timeout:
        return "Error: La solicitud ha excedido el tiempo de espera."
    except requests.exceptions.ConnectionError:
        return "Error: No se pudo conectar al servidor."
    except requests.exceptions.HTTPError as http_err:
        return f"Error HTTP: {http_err}"
    except requests.exceptions.RequestException as req_err:
        return f"Error en la solicitud: {req_err}"
    finally:
        # Cerrar la respuesta si existe
        if 'response' in locals():
            response.close()
        
import re

def encrypt(data):
    url = rootUrl + "advisory.aspx"
    headers = {'Content-Type': 'text/xml'}

    xmlQuery = f"""<?xml version=\"1.0\"?>
    <odcse>
        <control>
            <advisory>ENCRYPT</advisory>
            <data>{data}</data>
        </control>
    </odcse>"""
    response = requests.post(url, data=xmlQuery, headers=headers)
    text = response.text
    response.close()
    #print(text)
    # Buscar el contenido entre <details> y </details>
    match = re.search(r"RETURNED</message><details>(.*?)</details>", text)
    print(match)
    if match:
        return match.group(1).strip()
    else:
        return ""

def getAssyProfileDetails(serialNumber):
    url=rootUrl+"getParameter.asp?PROFILE=GET_ASSY_PROFILE_DETAILS&SN="+serialNumber
    #url = rootUrl+"getParameter.asp"
    #url = rootUrl + "getParameter.asp?PROFILE=&SN=" + serialNumber
    print(url)

    response = requests.get(url)
    response.close()
    print(response.text)
    return(response.text)

def getAssyProfileId(serialNumber):
    url=rootUrl+"getParameter.asp?PROFILE=GET_ASSY_PROFILE_ID&SN="+serialNumber+"&ST=WATER_POUCH_MERGE"
    #url = rootUrl+"getParameter.asp"
    #url = rootUrl + "getParameter.asp?PROFILE=&SN=" + serialNumber
    print(url)

    response = requests.get(url)
    response.close()
    return(response.text)

def getAssyProfileId_PALLET_ID(serial):
    url=rootUrl+"getParameter.asp?PROFILE=GET_ASSY_PROFILE_ID&SN="+serial+"&ST=PALLET_ID"
    
    #url = rootUrl+"getParameter.asp"
    #url = rootUrl + "getParameter.asp?PROFILE=&SN=" + serialNumber
    print(url)

    response = requests.get(url)
    
    response.close()
    print(response.text)
    return(response.text)

def getAssyProfileId_PID(serial): #Pallet ID para Lunar RSP= 10-06527A3MX||1|1,10-06527A3MX,10-06527A3MX_001 (assy_profile_id, pn, rd)
    url=rootUrl+"getParameter.asp?PROFILE=GET_ASSY_PROFILE_DETAILS_PID&SN="+serial
    print(url)
    response = requests.get(url)
    response.close()
    print(response.text)
    return(response.text)


def getCTN_Data(CTN_Number):
    url=rootUrl+"getParameter.asp?PROFILE=GET_CTNNO_DATA&UID="+CTN_Number

    #PROFILE=GET_CTNNO_DATA&UID=10025246137
    response = requests.get(url)
    response.close()
    print(response.text)
    return(response.text)

def transaction(serial,assyProfileId,rd,pn,ctn,datecode,supcode,lotcode,user,password):
    url=rootUrl+"transaction.aspx"
    print(url)
    headers = {'Content-Type':'text/xml'}

    xmlQuery = f"""<?xml version=\"1.0\"?>
    <odcse>
        <control>
            <module>ASSEMBLY</module>
        </control>
        <sns>
            <sn id="{serial}">
                <alias_sn>{serial}</alias_sn>
            </sn>
        </sns>
        <assembly>
            <assembly_profile>{assyProfileId}</assembly_profile>
            <components>
                <component rd="{rd}" pn="{pn}"><pnsn></pnsn>
                    <data_item>
                        <item name="CTN">{ctn}</item>
                        <item name="DATECODE">{datecode}</item>
                        <item name="LOTCODE">{lotcode}</item>
                        <item name="MFG_PN">{pn}</item>
                        <item name="SUPCODE">{supcode}</item>
                    </data_item>
                </component>
            </components>
        </assembly>
        <tracking>
            <station>PALLET_ID</station>
            <userid>{user}</userid>
            <password>{password}</password>
            <computer_name>CMXLUNARPC</computer_name>
            <resource_name>RES_PALLET_ID</resource_name>
            <comment></comment>
        </tracking>
    </odcse>
    """
    print(xmlQuery)
    response = requests.post(url, data=xmlQuery, headers=headers)
    print(response)
    response.close()
    return(response.text)

def get_SO_BB(model):
    url=rootUrl+"getParameter.asp?PROFILE=GET_SO_BB_RWK&MODEL=" + model

    print(url)

    response = requests.get(url)
    response.close()
    
    print(response.text)
    return(response.text)

def olsu(shop,serial,user,password):
    url=rootUrl+"transaction.aspx"
    print(url)
    headers = {'Content-Type':'text/xml'}

    xmlQuery = f"""<?xml version=\"1.0\"?>
    <odcse>
        <control>
            <module>REGISTRATION</module>
            <so>{shop}</so>
        </control>
        <sns>
            <sn id="{serial}"/>
        </sns>
        <tracking>
            <station>OLSU_REG</station>
            <userid>{user}</userid>
            <password>{password}</password>
            <computer_name>CMXDELUNAPP</computer_name>
            <resource_name>AUTO_CTT</resource_name>
            <comment></comment>
        </tracking>
    </odcse>"""

    response = requests.post(url, data=xmlQuery, headers=headers)
    response.close()
    print(response.text)
    return(response.text)



"""<odcse>
        <control>
            <module>ASSEMBLY</module>
        </control>
        <sns>
            <sn id="K1045D72P1006482">
           <alias_sn>K1045D72P1006482</alias_sn>
</sn>
        </sns>
        <assembly>
            <assembly_profile>10-06527A3MX||1|1</assembly_profile>
            <components>
                <component rd="10-06527A3MX_001" pn="10-06527A3MX"><pnsn></pnsn>
                    <data_item>
                        <item name="CTN">10025246137</item>
                        <item name="DATECODE">2307</item>
                        <item name="LOTCODE">S1CPS045300859</item>
                        <item name="MFG_PN">10-06527A3MX</item>
                        <item name="SUPCODE">LUNAR ENERGY, INC.</item>
                    </data_item>
                </component>
            </components>
        </assembly>
        <tracking>
            <station>PALLET_ID</station>
            <userid>MESGATEWAY</userid>
            <password>02 01 10 14 04 1B 01 14 12 1C</password>
            <computer_name>CMXLUNARPC</computer_name>
            <resource_name>RES_PALLET_ID</resource_name>
            <comment></comment>
        </tracking>
    </odcse>"""