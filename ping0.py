import os
import sys
import platform
import argparse
import json
import urllib.parse
import requests
import multiprocessing
from operator import itemgetter
from tabulate import tabulate
from datetime import datetime
import numpy as np
from slugify import slugify


class Ping0Utility:
    def __init__(self, export_format=None):
        self.export_format = export_format

    @staticmethod
    def print_progress_bar(iteration, total, prefix='', suffix='', decimals=1, length=100, fill='█', print_end="\r"):
        percent = f"{100 * (iteration / float(total)):.{decimals}f}"
        filled_length = int(length * iteration // total)
        bar = fill * filled_length + '-' * (length - filled_length)
        print(f'\r{prefix} |{bar}| {percent}% {suffix}', end=print_end)
        if iteration == total:
            print(' ' * length * 2)
            print("\r", end="")

    @staticmethod
    def ping(host, ipv = 4):
        op = platform.system()
        if op == 'Windows':
            ping_result = os.popen(f'ping -n 1 -w 1000 -{ipv} {host}').read().strip().split("\n")[-1].strip()
            ping_response = ping_result.split('=')[-1].split('ms')[0].strip() if '=' in ping_result else '99999999'
        elif op == 'Linux':
            ping_result = os.popen(f'ping -qc1 -{ipv} {host} -W 0.5 2> /dev/null').read().strip().split("\n")[-1]
            ping_response = ping_result.split('/')[-2] if '/' in ping_result else '99999999'
        else:
            print('Não suportado')
            return None
        return int(float(ping_response))

    @staticmethod
    def file_read(file):
        if os.path.isfile(file):
            with open(file, "r") as f:
                return f.read().splitlines()
        else:
            sys.exit("Erro: Arquivo inválido")

    def ping_response(self, file_array):
        file_array_total = len(file_array)
        if file_array_total == 0:
            sys.exit("Erro: Nenhum host encontrado no arquivo")

        results = []
        self.print_progress_bar(0, file_array_total, prefix='Progresso:', suffix='Completo', length=50)
        for i, line in enumerate(file_array):
            host, name = (line.split(' ', 1) + [''])[:2]
            results.append([host, name, self.ping(host, 4), self.ping(host, 6)])
            self.print_progress_bar(i + 1, file_array_total, prefix='Progresso:', suffix='Completo', length=50)

        return self.sort_fix(results, 2)

    def ping_response_speedtest(self, data_json, max_processes=10):
        file_array_total = len(data_json)
        if file_array_total == 0:
            sys.exit("Erro: Nenhum host encontrado com essa palavra")

        manager = multiprocessing.Manager()
        results = manager.dict()
        self.print_progress_bar(0, file_array_total, prefix='Progresso:', suffix='Completo', length=50)

        processes = []
        for i, line in enumerate(data_json):
            while len(processes) >= max_processes:
                for p in processes:
                    if not p.is_alive():
                        processes.remove(p)
            p = multiprocessing.Process(target=self.parse_ping, args=(results, i, line))
            p.start()
            processes.append(p)

        for i, p in enumerate(processes):
            p.join()
            
            self.print_progress_bar(i + 1, file_array_total, prefix='Progresso:', suffix='Completo', length=50)
        
        return self.sort_fix(results.values(), 3)

    def parse_ping(self, results, i, line):
        parsed_url = urllib.parse.urlparse(line['url'])
        results[i] = [parsed_url.hostname, f"{line['sponsor']} ({line['id']})", f"{line['name']} - {line['cc']}", self.ping(parsed_url.hostname, 4), self.ping(parsed_url.hostname, 6), line['lat'], line['lon']]

    @staticmethod
    def sort_fix(arr, index):
        sorted_arr = sorted(arr, key=itemgetter(index))

        for item in sorted_arr:

            if item[index+1] == 99999999:
                item[index+1] = 'FALHOU'
            else:
                item[index+1] = f"{item[index+1]}ms"

            if item[index] == 99999999:
                item[index] = 'FALHOU'
            else:
                item[index] = f"{item[index]}ms"
        return sorted_arr

    @staticmethod
    def speedtest_read(keyword):
        url = f"https://www.speedtest.net/api/js/servers?engine=js&search={urllib.parse.quote(keyword)}&limit=100"
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36'}
        response = requests.get(url, headers=headers)
        return response.json()

    @staticmethod
    def prepare_table(ping_response, headers):
        return tabulate(ping_response, headers)

    @staticmethod
    def prepare_csv(ping_response, headers):
        return tabulate(ping_response, headers, tablefmt="tsv")

    @staticmethod
    def print_table(table):
        print(table)

    @staticmethod
    def export_result(printed, prefix):
        filename = Ping0Utility.get_filename(prefix) + "_resultado_ping0.txt"
        with open(filename, 'w') as f:
            f.write(printed)

    @staticmethod
    def export_result_csv(ping_response, headers, prefix):
        filename = Ping0Utility.get_filename(prefix) + "_resultado_ping0.csv"
        np.savetxt(filename, [headers] + ping_response, delimiter="; ", fmt='%s')

    @staticmethod
    def get_filename(prefix):
        now = datetime.now()
        return now.strftime(f"%Y-%m-%d_%H-%M-%S_[{slugify(prefix, separator='-')}]")

    @staticmethod
    def current_version():
        return '1.0.1'

    @staticmethod
    def get_version():
        print(f'Versão: {Ping0Utility.current_version()}')


class Ping0App:
    def __init__(self):
        self.ping_utility = Ping0Utility()

    def run(self):
        multiprocessing.freeze_support()

        parser = argparse.ArgumentParser(description="Ping para hosts via arquivos ou Speedtest")
        group = parser.add_mutually_exclusive_group()
        group.add_argument("-f", "--file", help="Arquivo de hosts")
        group.add_argument("-s", "--speedtest", help="Palavra chave para busca dos servidores, utilize aspas para utilizar mais de uma palavra ex: \"Claro Net\"")
        parser.add_argument("-e", "--export", help="Exportar resultados")
        parser.add_argument("-v", "--version", action='store_true', help="Somente Ipv4")
        # parser.add_argument("-6", "--export", help="Somente Ipv6")

        args = parser.parse_args()

        if args.file:
            headers = ["Host/IP", "Servidor", "Ping"]
            hosts = self.ping_utility.file_read(args.file)
            results = self.ping_utility.ping_response(hosts)
            table = self.ping_utility.prepare_table(results, headers)
            self.ping_utility.print_table(table)
            if args.export == 'csv':
                self.ping_utility.export_result_csv(results, headers, args.file)
            elif args.export == 'txt':
                self.ping_utility.export_result(table, args.file)
        elif args.speedtest:
            headers = ["Host/IP", "Servidor (ID)", "Local", "Ping4", "Ping6", "Lat", "Lon"]
            hosts = self.ping_utility.speedtest_read(args.speedtest)
            results = self.ping_utility.ping_response_speedtest(hosts)
            table = self.ping_utility.prepare_table(results, headers)
            self.ping_utility.print_table(table)
            if args.export == 'csv':
                self.ping_utility.export_result_csv(results, headers, args.speedtest)
            elif args.export == 'txt':
                self.ping_utility.export_result(table, args.speedtest)
        
        if args.version:
            return self.ping_utility.get_version()

if __name__ == '__main__':
    Ping0App().run()
