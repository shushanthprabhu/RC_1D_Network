# !/usr/bin/env python3
# coding: utf-8
__author__ = "Shushanth Prabhu"
__email__ = "shushanth@gmail.com"
__version__ = "1.0"

from NetworkParser import foster_solver
from NetworkParser import FC_Error_list
import numpy as np
# import matplotlib.pyplot as plt
from sympy import symbols, fraction, cancel, quo
from sympy import Poly, rem


# TODO : Error Handling
# TODO : Write out Diagnostic file
# TODO : Idiot proof
# 200 Hz is the ideal PWM

def read_csv_file(file):
    """
    Read CSV File
    :param file: file path in csv format
    :return: file content
    """
    return foster_solver.read_csv_file(file)


# def plot_zth(input_trace, foster):
#     zth_input = np.asarray(input_trace)
#     plt.figure()
#     plt.subplot(2, 2, 1)
#     plt.plot(zth_input[:, 0], zth_input[:, 1])
#     plt.xlabel("Time [s]")
#     plt.ylabel("Voltage [V]")
#     plt.grid(True)
#
#     plt.subplot(2, 2, 2)
#     plt.plot(zth_input[:, 0], zth_input[:, 1])
#     plt.plot(zth_input[:, 0], foster_solver.foster_func(foster, zth_input[:, 0]))
#     plt.xlabel("Time [s]")
#     plt.ylabel("Voltage [V]")
#     plt.grid(True)
#
#     plt.subplot(2, 2, 3)
#     plt.plot(zth_input[:, 0], foster_solver.error_func(foster, zth_input[:, 0], zth_input[:, 1]))
#     plt.xlabel("Time [s]")
#     plt.ylabel("Error")
#     plt.grid(True)
#
#     plt.show()


def solve_cauer(time, zth, default_tuple):
    """
    Function to create a cauer model
    :param time:
    :param zth:
    :return:
    """
    if foster_solver.sanity_check(time, zth):
        foster_network = foster_solver.create_foster_network(time, zth, default_tuple)
        # plot_zth(zth, foster_network)
        # print(foster_network)
        s = symbols('s')
        i = 0
        f = 0
        while i != len(foster_network):
            f += (foster_network[i] / (1 + (foster_network[i] * foster_network[i + 1]) * s))
            i += 2

        sum_f = 1 / f
        n, d = fraction(cancel(sum_f))
        cauer_network = []
        flag = True

        while flag:
            q = quo(n, d)
            c = Poly(q, s).all_coeffs()[0]
            q_list = Poly(q, s).all_coeffs()
            cauer_network.append(c)

            q_list.pop(0)
            re = rem(n, d)
            if len(q_list) == 1:
                n = q_list[0] * d
            n = n + re
            n, d = fraction(d / n)
            if len(Poly(d, s).all_coeffs()) == 1:
                r = n / d
            else:
                r = quo(n, d)

            cauer_network.append(r)
            if len(foster_network) == len(cauer_network):
                flag = False
                break
            re = rem(n, d)
            n = re
            n, d = fraction(d / n)
        return cauer_network


def sort_rc_list(network):
    """
    Sort RC network to R List and C List
    :param network:
    :return: tuple with R List and C List
    """
    list_1, list_2 = foster_solver.sort_rc_list(network)
    return (list_1, list_2)


def get_cauer_network(file):
    if file.strip() or not file.isspace():
        zth = read_csv_file(file)
        zth = np.asarray(zth)

        cauer_network = solve_cauer(zth[:, 0], zth[:, 1], foster_solver.foster_default_value())
        return cauer_network

def export_network(list1,list2):
    print ("Hi")



if __name__ == "__main__":
    csv_file = r"C:\Users\ocu01756\OneDrive - Osram-Continental GmbH\Documents\personal\Papers\RC_Network\FosterNetwork\ExampleCircuit\ODE_Solve_5RC_Pair"
    csv_file += r"\Foster5.csv"

    # csv_file = r"C:\Users\ocu01756\OneDrive - Osram-Continental GmbH\Documents\personal\Papers\RC_Network\FosterNetwork\ExampleCircuit\SW_Validation_2\0.5P"
    # csv_file += r"\Book1.csv"
    # csv_file = r"C:\Users\ocu01756\OneDrive - Osram-Continental GmbH\Documents\personal\Papers\RC_Network\FosterNetwork\ExampleCircuit\SW_Validation"
    # csv_file += r"\goal_plot.csv"

    zth = read_csv_file(csv_file)
    zth = np.asarray(zth)

    cauer_network = solve_cauer(zth[:, 0], zth[:, 1], foster_solver.foster_default_value())
    # cauer_network =   [4.99999988158911e-11, 1.43737026931527, 4.18395772986766e-9, 0.0173849506907681, 0.00210262538652739, 1.27772630778777, 1.16413673474537e-6, 3.64330795658432, 3.90308981692776e-5, 1.09547941017863, 7.34748412854026, 0.0121294029074585, 44.3528098530672, 18.9501630576756]
    print("CAUER NETWORK-\n", cauer_network)

    c_list, r_list = sort_rc_list(cauer_network)

    print("R is ", r_list)
    print("C is ", c_list)

    cir_file_path = r"C:\Users\ocu01756\OneDrive - Osram-Continental GmbH\Documents\personal\Papers\RC_Network\FosterNetwork\ExampleCircuit\SW_Validation"
    cir_file_path += r"\Cauer_Circuit.asc"

    # from NetworkParser import asc_writer as cir
    # cir.write_cauer(cir_file_path,cauer_network)
