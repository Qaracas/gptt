proveedores_ia = {
    "blackboxai": ClaseConcretaA(),
    "koboldai"  : ClaseConcretaB()
}

def pregunta(nombre_proveedor, pregunta):
    if nombre_proveedor in proveedores_ia:
        proveedor = proveedores_ia[nombre_proveedor]
        proveedor.pregunta(pregunta)
    else:
        print(f"No se encontró proveedor '{nombre_proveedor}'.")