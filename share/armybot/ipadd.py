import ipaddress

# Generar todas las IPs posibles (0.0.0.0/0)
def generar_todas_las_ips():
    red = ipaddress.ip_network("0.0.0.0/0", strict=False)
    return [str(ip) for ip in red.hosts()]

# Generar IPs en el rango 0.0.0.0/8
def generar_ips_rango_0_0_0_0_8():
    red = ipaddress.ip_network("0.0.0.0/8", strict=False)
    return [str(ip) for ip in red.hosts()]

# Ejemplo de uso
ips_totales = generar_todas_las_ips()  # Nota: Esto no es práctico para la mayoría de los casos debido a la cantidad masiva de direcciones
ips_rango_0_0_0_0_8 = generar_ips_rango_0_0_0_0_8()

print(f"Ejemplo de IP en el rango 0.0.0.0/8: {ips_rango_0_0_0_0_8[0]}")
