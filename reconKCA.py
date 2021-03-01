import requests
import argparse
import concurrent.futures
import urllib3
from csv import DictWriter

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

parser = argparse.ArgumentParser(description="This is a very simple tool written by glomerulust for basic recon. "
                                             "Since I am developing this tool as a hobby and personal use only, "
                                             "it is not very user "
                                             "friendly at the moment. "
                                             "\n I am a beginner in this field and I will try to "
                                             "add more functionalities to this tool as time goes on, if you have any "
                                             "questions/advice, you can contact me on twitter.com/glomerulust "
                                 )
parser.add_argument('-w', '--wordlist', type=str, metavar='', required=True, help=".txt file with subdomains")
parser.add_argument('-t', '--threads', type=int, metavar='', required=False, default=5, help="number of threads, "
                                                                                             "default is 5")
parser.add_argument('-to', '--timeout', type=int, metavar='', required=False, help="timeout in seconds", default=5)
parser.add_argument('-o', '--output_name', type=str, metavar='', required=False, help="name of the output file",
                    default='results_reconKCA.csv')

args = parser.parse_args()


class reconTool:
    num_threads = args.threads
    output_name = args.output_name
    output = {'subdomain': '-', 'status': '-', 'Content-Type': '-', 'Error': '-'}

    def __init__(self):
        self.subdomain_list = self.get_subdomain_list(args.wordlist)
        self.basic_recon_results = self.recon_subdomains(self.subdomain_list)
        self.write_csv(self.basic_recon_results)

    @staticmethod
    def get_subdomain_list(subdomains_txt):
        list_subdomains = []
        with open(subdomains_txt, 'r') as file:
            for line in file:
                list_subdomains.append(line.rstrip('\n'))
        return list_subdomains

    def recon_subdomains(self, subdomain_list):
        recon_results = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.num_threads) as executor:
            results = executor.map(get_request, subdomain_list)
        for out in results:
            recon_results.append(out)
        return recon_results

    def write_csv(self, recon_result_list):
        print("Writing results...")
        recon_result_list = list(filter(None, recon_result_list))
        with open(self.output_name, 'w') as out:
            writer = DictWriter(out, fieldnames=list(self.output))
            writer.writeheader()
            writer.writerows(recon_result_list)
        print(f"Basic recon saved as {self.output_name} in the current directory")


def get_request(subdomain, timeout=args.timeout):
    output = reconTool.output.copy()
    output['subdomain'] = subdomain

    print(f"Checking {subdomain}...")
    try:
        r = requests.get(url='https://' + subdomain, timeout=timeout, verify=False)
        output['status'] = str(r.status_code)
        output['Content-Type'] = r.headers['Content-Type']
        return output
    except requests.exceptions.Timeout:
        output['Error'] = 'Timeout'
        return output
    except Exception as inst:
        output['Error'] = str(inst)
        return


if __name__ == '__main__':
    status_counts = {}
    run = reconTool()
    basic_results = list(filter(None, run.basic_recon_results))
    for res_dict in basic_results:
        status = res_dict['status']
        if str(status) in status_counts:
            status_counts[str(status)] += 1
        else:
            status_counts[str(status)] = 1

    print(f"Status counts are:\n {status_counts}")
