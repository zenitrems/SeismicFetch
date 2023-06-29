"""
Seismic Fetch
"""
import threading

import fetch_usgs
import emsc_client
import fetch_ssn

EXIT_FLAG = False


def ssn_fetch():
    """Fetch USGS Feed"""
    while not EXIT_FLAG:
        fetch_ssn.main()


def usgs_fetch():
    """Fetch USGS Feed"""
    while not EXIT_FLAG:
        fetch_usgs.main()


def emsc_socket():
    """Start EMSC Client"""
    while not EXIT_FLAG:
        emsc_client.main()


thread0 = threading.Thread(target=ssn_fetch)
thread1 = threading.Thread(target=usgs_fetch)
thread2 = threading.Thread(target=emsc_socket)

thread0.start()
thread1.start()
thread2.start()
input("Presiona Enter para salir...")
EXIT_FLAG = True
thread0.join()
thread1.join()
thread2.join()
