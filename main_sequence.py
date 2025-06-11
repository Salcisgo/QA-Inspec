import sys
sys.path.append("c:/scripts/")  # Ajusta la ruta si es necesario

import odcLib
import json
import re


def main(serial, selected_order, user, password,unique_Id):
    process_Check = odcLib.processCheck(serial)
    print(f"Resultado de processCheck: {process_Check}")

    if process_Check == "PALLET_ID":
        # Obtener assy_profile_id, pn, rd
        response = odcLib.getAssyProfileId_PID(serial)
        print(f"Respuesta getAssyProfileId_PID: {response}")
        processed_response = response.replace("<br>", "").split(",")
        if len(processed_response) < 3:
            return {"status": "error", "msg": "Respuesta inválida de getAssyProfileId_PID"}
        assy_profile_id, pn, rd = processed_response[:3]

        # Obtener PalletID
        palletid = assy_profile_id.split("|")[0] if "|" in assy_profile_id else assy_profile_id

        # Obtener datos de CTN
        ctn_data_raw = odcLib.getCTN_Data(unique_Id)
        print(f"Respuesta getCTN_Data: {ctn_data_raw}")
        import json
        try:
            ctn_data = json.loads(ctn_data_raw)
            ctn_info = ctn_data["result"][0]
            CTN = ctn_info["CTNNO"]
            DATECODE = ctn_info["DATECODE"]
            LOTCODE = ctn_info["LOTCODE"]
            SUPCODE = ctn_info["SUPCODE"]
        except Exception as e:
            return {"status": "error", "msg": f"Error al procesar getCTN_Data: {e}"}

        # Ejecutar transaction
        transaction_response = odcLib.transaction(
            serial, assy_profile_id, rd, pn, CTN, DATECODE, SUPCODE, LOTCODE, user, password
        )
        print(f"Respuesta transaction: {transaction_response}")
        if "OK" not in transaction_response.upper():
            return {"status": "error", "msg": "Transaction falló: " + transaction_response}

        return {
            "status": "ok",
            "msg": "Estatus:"+process_Check+"Proceda a la inspección visual."
        }

    elif process_Check == "Serial Number does not exist in system":
        # Ejecutar olsu
        olsu_response = odcLib.olsu(selected_order, serial,user,password)
        print(f"Respuesta de OLSU: {olsu_response}")
        if "REGISTER SUCCESS" not in olsu_response.upper():
            return {"status": "error", "msg": "OLSU falló: " + olsu_response}

        # Continuar con el flujo como en PALLET_ID

        # Obtener assy_profile_id, pn, rd
        response = odcLib.getAssyProfileId_PID(serial)
        print(f"Respuesta getAssyProfileId_PID: {response}")
        processed_response = response.replace("<br>", "").split(",")
        if len(processed_response) < 3:
            return {"status": "error", "msg": "Respuesta inválida de getAssyProfileId_PID"}
        assy_profile_id, pn, rd = processed_response[:3]

        # Obtener PalletID
        palletid = assy_profile_id.split("|")[0] if "|" in assy_profile_id else assy_profile_id

        # Obtener datos de CTN
        ctn_data_raw = odcLib.getCTN_Data(unique_Id)
        print(f"Respuesta getCTN_Data: {ctn_data_raw}")
        import json
        try:
            ctn_data = json.loads(ctn_data_raw)
            ctn_info = ctn_data["result"][0]
            CTN = ctn_info["CTNNO"]
            DATECODE = ctn_info["DATECODE"]
            LOTCODE = ctn_info["LOTCODE"]
            SUPCODE = ctn_info["SUPCODE"]
        except Exception as e:
            return {"status": "error", "msg": f"Error al procesar getCTN_Data: {e}"}

        # Ejecutar transaction
        transaction_response = odcLib.transaction(
            serial, assy_profile_id, rd, pn, CTN, DATECODE, SUPCODE, LOTCODE, user, password
        )
        print(f"Respuesta transaction: {transaction_response}")
        # Extraer el mensaje de la respuesta XML
        match = re.search(r"<message>(.*?)</message>", transaction_response, re.IGNORECASE)
        message = match.group(1).strip() if match else ""

        if "SUCCESS" not in message.upper():
            return {"status": "error", "msg": "Transaction falló: " + transaction_response}

        return {
            "status": "ok",
            "msg": "Estatus:"+process_Check+"Proceda a la inspección visual."
        }
    
        
    elif process_Check == "QA_INSP":
        
        # Proceder a la inspección visual directamente
        return {
            "status": "ok",
            "msg": "Estatus:"+process_Check+"Realice la inspeccion visual y/Proceda a seleccionar PASA o FALLA."
        }

    else:
        return {"status": "Process Check", "msg": f"Estatus: {process_Check}"}

def run_cell_inspect():
    # Aquí puedes llamar a las funciones principales de CellInspect
    # Por ejemplo, podrías iniciar la ventana principal o ejecutar una secuencia de pruebas
    print("Iniciando secuencia principal de QA INSPEC...")
    # Si quieres iniciar la interfaz gráfica:
    CellInspect.root.mainloop()
    # O puedes llamar a otras funciones según tu flujo:
    # CellInspect.main()
    # CellInspect.on_capture_clicked()
    # etc.

if __name__ == "__main__":
    # main_sequence(serial, selected_order, user, password)  # Descomentar y proporcionar argumentos adecuados
    run_cell_inspect()