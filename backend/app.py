"""
Backend - API REST para Gestión de Inventarios y Ventas
========================================================
"""

from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import json
import os
from datetime import datetime, date
from pathlib import Path

app = Flask(__name__, static_folder='../frontend')
CORS(app)

# ==================== RUTAS ====================
DATA_DIR = Path(__file__).parent.parent / "data"
DATA_DIR.mkdir(exist_ok=True)

INVENTORY_FILE = DATA_DIR / "inventario.json"
SALES_FILE = DATA_DIR / "ventas.json"
CASH_FILE = DATA_DIR / "caja.json"
USERS_FILE = DATA_DIR / "usuarios.json"

# Simple session storage (in production, use proper JWT or sessions)
active_sessions = {}

# Ruta para servir el frontend
@app.route('/')
def index():
    return send_from_directory('../frontend', 'index.html')

@app.route('/<path:filename>')
def serve_static(filename):
    return send_from_directory('../frontend', filename)


# ==================== HELPERS ====================
def load_json(file_path, default):
    if file_path.exists():
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return default

def save_json(file_path, data):
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


# ==================== INVENTARIO ====================
@app.route('/api/inventario', methods=['GET'])
def get_inventario():
    productos = load_json(INVENTORY_FILE, {})
    return jsonify(productos)

@app.route('/api/inventario/<codigo>', methods=['GET'])
def get_producto(codigo):
    productos = load_json(INVENTORY_FILE, {})
    producto = productos.get(codigo)
    if producto:
        return jsonify(producto)
    return jsonify({"error": "Producto no encontrado"}), 404

@app.route('/api/inventario', methods=['POST'])
def agregar_producto():
    data = request.json
    productos = load_json(INVENTORY_FILE, {})
    
    codigo = data.get('codigo')
    if codigo in productos:
        return jsonify({"success": False, "message": "El producto ya existe"}), 400
    
    productos[codigo] = {
        "nombre": data.get('nombre'),
        "precio": float(data.get('precio', 0)),
        "cantidad": int(data.get('cantidad', 0)),
        "umbral_minimo": int(data.get('umbral_minimo', 10)),
        "fecha_actualizacion": datetime.now().isoformat()
    }
    save_json(INVENTORY_FILE, productos)
    return jsonify({"success": True, "message": "Producto agregado"})

@app.route('/api/inventario/<codigo>', methods=['PUT'])
def actualizar_producto(codigo):
    data = request.json
    productos = load_json(INVENTORY_FILE, {})
    
    if codigo not in productos:
        return jsonify({"error": "Producto no encontrado"}), 404
    
    for key in ['nombre', 'precio', 'cantidad', 'umbral_minimo']:
        if key in data:
            productos[codigo][key] = float(data[key]) if key == 'precio' else int(data[key])
    
    productos[codigo]["fecha_actualizacion"] = datetime.now().isoformat()
    save_json(INVENTORY_FILE, productos)
    return jsonify({"success": True, "message": "Producto actualizado"})

@app.route('/api/inventario/<codigo>', methods=['DELETE'])
def eliminar_producto(codigo):
    productos = load_json(INVENTORY_FILE, {})
    
    if codigo not in productos:
        return jsonify({"error": "Producto no encontrado"}), 404
    
    del productos[codigo]
    save_json(INVENTORY_FILE, productos)
    return jsonify({"success": True, "message": "Producto eliminado"})

@app.route('/api/inventario/alertas', methods=['GET'])
def get_alertas():
    productos = load_json(INVENTORY_FILE, {})
    alertas = []
    for codigo, producto in productos.items():
        if producto["cantidad"] <= producto["umbral_minimo"]:
            alertas.append({
                "codigo": codigo,
                "nombre": producto["nombre"],
                "cantidad": producto["cantidad"],
                "umbral_minimo": producto["umbral_minimo"],
                "necesario": producto["umbral_minimo"] - producto["cantidad"] + 5
            })
    return jsonify(alertas)


# ==================== VENTAS ====================
@app.route('/api/ventas', methods=['GET'])
def get_ventas():
    ventas = load_json(SALES_FILE, [])
    return jsonify(ventas)

@app.route('/api/ventas/hoy', methods=['GET'])
def get_ventas_hoy():
    ventas = load_json(SALES_FILE, [])
    hoy = date.today().isoformat()
    ventas_hoy = [v for v in ventas if v["fecha"][:10] == hoy]
    return jsonify(ventas_hoy)

@app.route('/api/ventas/mes', methods=['GET'])
def get_ventas_mes():
    ventas = load_json(SALES_FILE, [])
    año = request.args.get('año', type=int, default=date.today().year)
    mes = request.args.get('mes', type=int, default=date.today().month)
    
    ventas_mes = [v for v in ventas 
                  if datetime.fromisoformat(v["fecha"]).year == año 
                  and datetime.fromisoformat(v["fecha"]).month == mes]
    return jsonify(ventas_mes)

@app.route('/api/ventas/total-hoy', methods=['GET'])
def get_total_hoy():
    ventas = load_json(SALES_FILE, [])
    hoy = date.today().isoformat()
    total = sum(v["total"] for v in ventas if v["fecha"][:10] == hoy)
    return jsonify({"total": total})

@app.route('/api/ventas/total-mes', methods=['GET'])
def get_total_mes():
    ventas = load_json(SALES_FILE, [])
    año = request.args.get('año', type=int, default=date.today().year)
    mes = request.args.get('mes', type=int, default=date.today().month)
    
    total = sum(v["total"] for v in ventas 
                if datetime.fromisoformat(v["fecha"]).year == año 
                and datetime.fromisoformat(v["fecha"]).month == mes)
    return jsonify({"total": total})

@app.route('/api/ventas', methods=['POST'])
def registrar_venta():
    data = request.json
    ventas = load_json(SALES_FILE, [])
    
    productos = data.get('productos', [])
    total = 0
    productos_venta = []
    
    productos_inv = load_json(INVENTORY_FILE, {})
    
    for item in productos:
        codigo = item['codigo']
        cantidad = int(item['cantidad'])
        
        if codigo not in productos_inv:
            return jsonify({"success": False, "message": f"Producto {codigo} no encontrado"}), 400
        
        prod = productos_inv[codigo]
        if prod['cantidad'] < cantidad:
            return jsonify({"success": False, "message": f"Stock insuficiente para {prod['nombre']}"}), 400
        
        subtotal = prod['precio'] * cantidad
        total += subtotal
        
        productos_venta.append({
            "codigo": codigo,
            "nombre": prod['nombre'],
            "cantidad": cantidad,
            "precio": prod['precio'],
            "subtotal": subtotal
        })
        
        # Reducir stock
        productos_inv[codigo]['cantidad'] -= cantidad
    
    save_json(INVENTORY_FILE, productos_inv)
    
    venta = {
        "id": len(ventas) + 1,
        "fecha": datetime.now().isoformat(),
        "productos": productos_venta,
        "total": total,
        "metodo_pago": data.get('metodo_pago', 'efectivo')
    }
    ventas.append(venta)
    save_json(SALES_FILE, ventas)
    
    # Registrar movimiento en caja
    caja = load_json(CASH_FILE, {"movimientos": [], "cierres": []})
    caja["movimientos"].append({
        "id": len(caja["movimientos"]) + 1,
        "fecha": datetime.now().isoformat(),
        "tipo": "ingreso",
        "monto": total,
        "descripcion": f"Venta #{venta['id']}"
    })
    save_json(CASH_FILE, caja)
    
    return jsonify({"success": True, "message": "Venta registrada", "venta": venta})


# ==================== CAJA ====================
@app.route('/api/caja/estado', methods=['GET'])
def get_estado_caja():
    ventas = load_json(SALES_FILE, [])
    caja = load_json(CASH_FILE, {"movimientos": [], "cierres": []})
    
    hoy = date.today().isoformat()
    ventas_hoy = sum(v["total"] for v in ventas if v["fecha"][:10] == hoy)
    ingresos = sum(m["monto"] for m in caja["movimientos"] 
                   if m["tipo"] == "ingreso" and m["fecha"][:10] == hoy)
    egresos = sum(m["monto"] for m in caja["movimientos"] 
                  if m["tipo"] == "egreso" and m["fecha"][:10] == hoy)
    
    return jsonify({
        "fecha": hoy,
        "ventas_del_dia": ventas_hoy,
        "ingresos": ingresos,
        "egresos": egresos,
        "balance": ingresos - egresos
    })

@app.route('/api/caja/cierre-diario', methods=['POST'])
def cierre_diario():
    caja = load_json(CASH_FILE, {"movimientos": [], "cierres": []})
    ventas = load_json(SALES_FILE, [])
    
    hoy = date.today().isoformat()
    ventas_hoy = sum(v["total"] for v in ventas if v["fecha"][:10] == hoy)
    gastos = sum(m["monto"] for m in caja["movimientos"] 
                 if m["tipo"] == "egreso" and m["fecha"][:10] == hoy)
    
    cierre = {
        "id": len(caja["cierres"]) + 1,
        "tipo": "diario",
        "fecha": datetime.now().isoformat(),
        "ventas": ventas_hoy,
        "gastos": gastos,
        "total": ventas_hoy - gastos,
        "estado": "cerrado"
    }
    caja["cierres"].append(cierre)
    save_json(CASH_FILE, caja)
    
    return jsonify({"success": True, "cierre": cierre})

@app.route('/api/caja/cierre-mensual', methods=['POST'])
def cierre_mensual():
    data = request.json
    año = data.get('año', date.today().year)
    mes = data.get('mes', date.today().month)
    
    caja = load_json(CASH_FILE, {"movimientos": [], "cierres": []})
    ventas = load_json(SALES_FILE, [])
    
    ventas_mes = sum(v["total"] for v in ventas 
                     if datetime.fromisoformat(v["fecha"]).year == año 
                     and datetime.fromisoformat(v["fecha"]).month == mes)
    
    cierre = {
        "id": len(caja["cierres"]) + 1,
        "tipo": "mensual",
        "fecha": datetime.now().isoformat(),
        "periodo": f"{año}-{mes:02d}",
        "ventas": ventas_mes,
        "gastos": 0,
        "total": ventas_mes,
        "estado": "cerrado"
    }
    caja["cierres"].append(cierre)
    save_json(CASH_FILE, caja)
    
    return jsonify({"success": True, "cierre": cierre})

@app.route('/api/caja/cierres', methods=['GET'])
def get_cierres():
    caja = load_json(CASH_FILE, {"movimientos": [], "cierres": []})
    return jsonify(caja["cierres"])


# ==================== AUTENTICACIÓN ====================
@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username', '').strip()
    password = data.get('password', '')
    
    if not username or not password:
        return jsonify({"success": False, "message": "Usuario y contraseña requeridos"}), 400
    
    usuarios = load_json(USERS_FILE, {})
    
    if username not in usuarios:
        return jsonify({"success": False, "message": "Usuario no encontrado"}), 401
    
    user = usuarios[username]
    if user['password'] != password:
        return jsonify({"success": False, "message": "Contraseña incorrecta"}), 401
    
    # Generate simple session token
    import secrets
    token = secrets.token_hex(16)
    active_sessions[token] = {
        "username": username,
        "rol": user.get('rol', 'usuario'),
        "login_time": datetime.now().isoformat()
    }
    
    return jsonify({
        "success": True, 
        "message": "Login exitoso",
        "token": token,
        "user": {"username": username, "rol": user.get('rol', 'usuario')}
    })

@app.route('/api/auth/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username', '').strip()
    password = data.get('password', '')
    rol = data.get('rol', 'usuario')
    
    if not username or not password:
        return jsonify({"success": False, "message": "Usuario y contraseña requeridos"}), 400
    
    if len(password) < 4:
        return jsonify({"success": False, "message": "La contraseña debe tener al menos 4 caracteres"}), 400
    
    usuarios = load_json(USERS_FILE, {})
    
    if username in usuarios:
        return jsonify({"success": False, "message": "El usuario ya existe"}), 400
    
    usuarios[username] = {
        "password": password,
        "rol": rol,
        "fecha_creacion": datetime.now().isoformat()
    }
    save_json(USERS_FILE, usuarios)
    
    return jsonify({"success": True, "message": "Usuario creado exitosamente"})

@app.route('/api/auth/reset-password', methods=['POST'])
def reset_password():
    data = request.json
    username = data.get('username', '').strip()
    password = data.get('password', '')

    if not username or not password:
        return jsonify({"success": False, "message": "Usuario y nueva contraseña requeridos"}), 400

    if len(password) < 4:
        return jsonify({"success": False, "message": "La contraseña debe tener al menos 4 caracteres"}), 400

    usuarios = load_json(USERS_FILE, {})
    if username not in usuarios:
        return jsonify({"success": False, "message": "Usuario no encontrado"}), 404

    usuarios[username]['password'] = password
    usuarios[username]['fecha_actualizacion'] = datetime.now().isoformat()
    save_json(USERS_FILE, usuarios)

    return jsonify({"success": True, "message": "Contraseña restablecida con éxito"})

@app.route('/api/auth/logout', methods=['POST'])
def logout():
    data = request.json
    token = data.get('token', '')
    
    if token in active_sessions:
        del active_sessions[token]
    
    return jsonify({"success": True, "message": "Sesión cerrada"})

@app.route('/api/auth/verify', methods=['GET'])
def verify_token():
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    
    if token in active_sessions:
        session = active_sessions[token]
        return jsonify({"valid": True, "user": session})
    
    return jsonify({"valid": False}), 401

@app.route('/api/auth/usuarios', methods=['GET'])
def get_usuarios():
    usuarios = load_json(USERS_FILE, {})
    # Return without passwords
    return jsonify({u: {"rol": data.get('rol'), "fecha_creacion": data.get('fecha_creacion')} 
                   for u, data in usuarios.items()})

@app.route('/api/auth/usuarios/<username>', methods=['DELETE'])
def delete_usuario(username):
    usuarios = load_json(USERS_FILE, {})
    
    if username not in usuarios:
        return jsonify({"error": "Usuario no encontrado"}), 404
    
    del usuarios[username]
    save_json(USERS_FILE, usuarios)
    
    return jsonify({"success": True, "message": "Usuario eliminado"})


# ==================== MAIN ====================
if __name__ == '__main__':
    print("\n🚀 Servidor iniciado en http://localhost:5000")
    app.run(debug=True, port=5000)