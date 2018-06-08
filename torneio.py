#!/usr/bin/python3

import sys
import os
import subprocess
import cgi

print("Content-type: text/html\n\n")
print("<html>")

def get_arg():
    args = cgi.FieldStorage()
    val = args.getvalue("c", "nop")

    if val == "nop":
        print("ERRO: Quantidade de times nao informado.")
        sys.exit()
    else:
        try:
            return int(val)
        except ValueError:
            print("ERRO: Valor informado invalido.")
            sys.exit()


def cria_arquivo(qnt_times):
    R = 1
    RT = 1

    # Calculo de rodadas
    calc_k = (qnt_times*2)

    # calculo diferente com quantidade par
    if qnt_times%2 == 0:
        calc_k -= 2

    # Criando o arquivo especifico para o usuario
    ip = cgi.escape(os.environ["REMOTE_ADDR"]).replace(".","-")
    filename = "torneio" + ip + ".mod"
    file = open(filename, "w")

    # Variaveis
    file.write("/* Variaveis de decisao */\n")
    for k in range(1, calc_k+1):
        for i in range(1, qnt_times+1):
            for j in range(1, qnt_times+1):
                varname = "k{0}m{1}n{2}".format(k, i, j)
                file.write("var " + varname + ", binary;\n")

        file.write("\n")

    # Funcao
    file.write("/* Funcao de objetivo */\n")
    file.write("minimize z:")
    for k in range(1, calc_k+1):
        for i in range(1, qnt_times+1):
            for j in range(1, qnt_times+1):
                varname = "k{0}m{1}n{2}".format(k, i, j)

                if k == calc_k and i == qnt_times and j == qnt_times:
                    file.write(" " + varname + ";")
                else:
                    file.write(" " + varname + " +")
    file.write("\n")

    file.write("\n")

    # Restricoes
    file.write("/* Limitadores */\n")
    for k in range(1, calc_k+1):
        for i in range(1, qnt_times+1):
            file.write("s.t. R{0} : ".format(R))
            R += 1

            for j in range(1, qnt_times+1):
                varname = "k{0}m{1}n{2}".format(k, i, j)

                if j == qnt_times:
                    file.write(varname + " <= 1;\n")
                else:
                    file.write(varname + " + ")

        for i in range(1, qnt_times+1):
            file.write("s.t. R{0} : ".format(R))
            R += 1

            for j in range(1, qnt_times+1):
                varname = "k{0}m{2}n{1}".format(k, i, j)

                if j == qnt_times:
                    file.write(varname + " <= 1;\n")
                else:
                    file.write(varname + " + ")

        for i in range(1, qnt_times+1):
            varname = "k{0}m{1}n{2}".format(k, i, i)
            file.write("s.t. R{0} : ".format(R) + varname + " = 0;\n")
            R += 1

        file.write("\n")

        file.write("s.t. RT{0} :".format(RT))
        RT += 1

        for i in range(1, qnt_times+1):
            for j in range(1, qnt_times+1):
                varname = "k{0}m{1}n{2}".format(k, i, j)

                if i == qnt_times and j == qnt_times:
                    max_rodada = int(qnt_times/2)

                    file.write(" " + varname + " = {0};\n".format(max_rodada))
                else:
                    file.write(" " + varname + " +")

        file.write("\n")

    for i in range(1, qnt_times+1):
        for j in range(1, qnt_times+1):
            if i != j:
                file.write("s.t. R{0} :".format(R))
                R += 1

                for k in range(1, calc_k+1):
                    varname = "k{0}m{1}n{2}".format(k, i, j)

                    if k == calc_k:
                        file.write(" " + varname + " <= 1;\n")
                    else:
                        file.write(" " + varname + " +")

    file.write("\n")
    file.write("end;\n")
    file.close()
    return filename


# Criando o Arquivo
temp_file_name = cria_arquivo(get_arg())
temp_sol_filename = temp_file_name[:-4]+".sol"

# Chamada do GLPSOL
sp = subprocess.call("glpsol -m " + temp_file_name + \
    " -o " + temp_sol_filename, \
    shell=True, stdout=subprocess.PIPE)

# Leitura formatada
with open(temp_sol_filename, 'r') as f:
    b = False

    for linha in f:
        if "Column" in linha and "name" in linha:
            b = True
            continue
        if "------" in linha:
            continue
        if "feasibility" in linha:
            b = False

        if b:
            isSaida = linha.split()
            if isSaida[3] == "1":
                cnt1 = isSaida[1].split("k")[1].split("m")[0]
                cnt2 = isSaida[1].split("k")[1].split("m")[1].split("n")[0]
                cnt3 = isSaida[1].split("k")[1].split("m")[1].split("n")[1]

                print("{0} {1} {2}".format(cnt1, cnt2, cnt3))

# Deletando os arquivos
os.delete(temp_file_name)
os.delete(temp_sol_filename)
print("</html>")
