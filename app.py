import streamlit as st
from sympy import symbols, Matrix, simplify, sympify


def periksa_linearitas(var_str, transformasi_str):
    try:
        # Parse variabel
        var_names = [v.strip() for v in var_str.split(",")]
        var_names = [v for v in var_names if v]
        
        if not var_names:
            return {"is_linear": False, "r1": None, "r2": None, 
                    "error": "Silakan masukkan nama variabel."}
        
        # Buat simbol untuk variabel input
        vars_dict = {var: symbols(var) for var in var_names}
        
        # Parse transformasi
        transformasi_str = transformasi_str.strip()
        if transformasi_str.startswith("(") and transformasi_str.endswith(")"):
            transformasi_str = transformasi_str[1:-1]
        
        components = [e.strip() for e in transformasi_str.split(",")]
        
        if not components:
            return {"is_linear": False, "r1": None, "r2": None,
                    "error": "Transformasi kosong."}
        
        # Konversi setiap komponen ke sympy expression
        F_components = []
        for comp in components:
            expr = sympify(comp, locals=vars_dict)
            # Cek jika ada simbol asing selain variabel input
            used_symbols = expr.free_symbols
            allowed_symbols = set(vars_dict.values())
            if not used_symbols.issubset(allowed_symbols):
                unknowns = used_symbols - allowed_symbols
                return {
                    "is_linear": False,
                    "r1": None,
                    "r2": None,
                    "error": f"Terdapat variabel tidak dikenal pada transformasi: {', '.join(str(s) for s in unknowns)}"
                }
            F_components.append(expr)
        
        # Buat simbol untuk u, v, k
        u_symbols = symbols(f"u0:{len(var_names)}")
        v_symbols = symbols(f"v0:{len(var_names)}")
        k = symbols("k")
        
        if len(var_names) == 1:
            u_symbols = (u_symbols,)
            v_symbols = (v_symbols,)
        
        # Buat dictionary untuk substitusi
        u_dict = {vars_dict[var]: u_symbols[i] for i, var in enumerate(var_names)}
        v_dict = {vars_dict[var]: v_symbols[i] for i, var in enumerate(var_names)}
        
        # Hitung F(u)
        F_u = Matrix([comp.subs(u_dict) for comp in F_components])
        
        # Hitung F(v)
        F_v = Matrix([comp.subs(v_dict) for comp in F_components])
        
        # Hitung F(u+v)
        uv_dict = {vars_dict[var]: u_symbols[i] + v_symbols[i] 
                   for i, var in enumerate(var_names)}
        F_uv = Matrix([comp.subs(uv_dict) for comp in F_components])
        
        # Hitung F(k*u)
        ku_dict = {vars_dict[var]: k * u_symbols[i] for i, var in enumerate(var_names)}
        F_ku = Matrix([comp.subs(ku_dict) for comp in F_components])
        
        # Kondisi 1: F(u+v) = F(u) + F(v)
        R1 = simplify(F_uv - (F_u + F_v))
        
        # Kondisi 2: F(k*u) = k*F(u)
        R2 = simplify(F_ku - k * F_u)
        
        # Cek apakah semua entry nol
        is_linear = all(entry == 0 for entry in R1) and all(entry == 0 for entry in R2)
        
        return {
            "is_linear": is_linear,
            "F_uv": F_uv,
            "F_u": F_u,
            "F_v": F_v,
            "F_u_plus_F_v": F_u + F_v,
            "r1": R1,
            "F_ku": F_ku,
            "k_F_u": k * F_u,
            "r2": R2,
            "error": None
        }
    
    except Exception as e:
        return {"is_linear": False, "r1": None, "r2": None,
                "error": f"Error: {str(e)}"}


def tampilkan_hasil(hasil):
    """Tampilkan hasil pemeriksaan linearitas."""
    if hasil["error"]:
        st.error(hasil["error"])
        return
    
    # Tampilkan status linearitas
    if hasil["is_linear"]:
        st.success("✓ LINIER (Linear)")
    else:
        st.error("✗ TIDAK LINIER (Non-linear)")
    
    # Tampilkan bukti simbolik
    st.subheader("Bukti Simbolik")
    
    from sympy import latex as sympy_latex
    
    # ===== KONDISI 1: ADITIF =====
    st.write("**Kondisi 1: F(u+v) = F(u) + F(v)** (Aditif)")
    
    col1, col2 = st.columns(2)
    with col1:
        st.write("**Sisi Kiri: F(u+v)**")
        fuv_latex = sympy_latex(hasil['F_uv'])
        st.latex(f"F(\\mathbf{{u}} + \\mathbf{{v}}) = {fuv_latex}")
    
    with col2:
        st.write("**Sisi Kanan: F(u) + F(v)**")
        fu_latex = sympy_latex(hasil['F_u'])
        fv_latex = sympy_latex(hasil['F_v'])
        fu_plus_fv_latex = sympy_latex(hasil['F_u_plus_F_v'])
        st.latex(f"F(\\mathbf{{u}}) + F(\\mathbf{{v}}) = {fu_plus_fv_latex}")
    
    st.write("**Hasil Pengurangan:**")
    r1_latex = sympy_latex(hasil['r1'])
    st.latex(f"F(\\mathbf{{u}} + \\mathbf{{v}}) - (F(\\mathbf{{u}}) + F(\\mathbf{{v}})) = {r1_latex}")
    
    if hasil['r1'] == 0 or all(entry == 0 for entry in hasil['r1']):
        st.success("✓ Kondisi 1 terpenuhi")
    else:
        st.error("✗ Kondisi 1 tidak terpenuhi")
    
    st.divider()
    
    # ===== KONDISI 2: HOMOGENITAS =====
    st.write("**Kondisi 2: F(k·u) = k·F(u)** (Homogenitas)")
    
    col1, col2 = st.columns(2)
    with col1:
        st.write("**Sisi Kiri: F(k·u)**")
        fku_latex = sympy_latex(hasil['F_ku'])
        st.latex(f"F(k \\mathbf{{u}}) = {fku_latex}")
    
    with col2:
        st.write("**Sisi Kanan: k·F(u)**")
        kfu_latex = sympy_latex(hasil['k_F_u'])
        st.latex(f"k \\cdot F(\\mathbf{{u}}) = {kfu_latex}")
    
    st.write("**Hasil Pengurangan:**")
    r2_latex = sympy_latex(hasil['r2'])
    st.latex(f"F(k \\mathbf{{u}}) - k \\cdot F(\\mathbf{{u}}) = {r2_latex}")
    
    if hasil['r2'] == 0 or all(entry == 0 for entry in hasil['r2']):
        st.success("✓ Kondisi 2 terpenuhi")
    else:
        st.error("✗ Kondisi 2 tidak terpenuhi")


# ===================== UI Streamlit =====================

st.set_page_config(page_title="Deteksi Transformasi Linier", layout="wide",page_icon="📏")

st.title("✖️➗ Deteksi Transformasi Linier ➕➖")
st.markdown(
    """
Aplikasi ini memeriksa apakah suatu transformasi F adalah **linier** 
menggunakan verifikasi simbolik dari dua kondisi:

    """
)
col1, col2 = st.columns(2)
with col1:
    st.info("**Aditif**: " \
    "F(u + v) = F(u) + F(v)")
with col2:
    st.info("**Homogen**:" \
    " F(k·u) = k·F(u)")
st.divider()

col1, col2 = st.columns(2)

with col1:
    st.subheader("Input")
    
    var_input = st.text_input(
        "Variabel",
        value="",
        help="Contoh: x,y,z"
    )
    
    trans_input = st.text_area(
        "Transformasi Fungsi",
        value="",
        height=100,
        help="Contoh: x + y, 2*y - z"
    )
    
    tombol_periksa = st.button("Periksa Linearitas", use_container_width=True)

with col2:
    st.subheader("Contoh-contoh")
    examples = [
        ("x,y", "(2*x, 3*y)", "LINIER"),
        ("x,y,z", "(x**2, y, z+1)", "TIDAK LINIER")]
    for var, trans, desc in examples:
        st.write(f"**{desc}**")
        st.code(f"Variabel: {var}\nTransformasi: {trans}", language="text")

st.divider()
st.subheader("Output")
if tombol_periksa:
    hasil = periksa_linearitas(var_input, trans_input)
    tampilkan_hasil(hasil)
else:
    st.info("Klik tombol untuk memeriksa linearitas transformasi.")

st.divider()
