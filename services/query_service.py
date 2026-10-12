
from utils.utils import getDniFromExcel
from database.database import (
    createQuery,
    save_patient,
    save_vaccine,
    updateQuery,
    save_patientByQuery
)


def getVaccinesByAllDni(excel_route, cliente_his):
    dnis, errors = getDniFromExcel(excel_route)
    if not dnis:
        return {
            "consulta_id": None,
            "exitosos": 0,
            "errores": len(errors),
            "detalles_errores": errors,
        }

    query_id = createQuery(excel_route, len(dnis))

    success = 0
    errors = list(errors)

    try:
        for dni in dnis:
            try:
                vaccines = cliente_his.vaccinesByDni(dni)
                save_patient(
                    vaccines["dni"],
                    vaccines["paciente"],
                    vaccines["FN"],
                )
                save_vaccine(
                    query_id,
                    vaccines["dni"],
                    vaccines["vaccines"],
                )
                save_patientByQuery(dni=dni, queryId=query_id)
                success += 1

            except Exception as error:
                errors.append(f"DNI {dni}: {error}")

    finally:
        updateQuery(
            query_id,
            success,
            len(errors),
        )

    return {
        "queryId": query_id,
        "success": success,
        "errors": len(errors),
        "error_detail": errors,
    }
