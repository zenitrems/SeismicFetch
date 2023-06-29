"""
Sismos Fetcher
"""
import threading
import fetch_usgs




# def ssn_scrap():
# def usgs_fetch():
def emsc_socket():
    fetch_usgs.main()


# thread0 = threading.Thread(target=ssn_scrap)
# thread1 = threading.Thread(target=usgs_fetch)
thread2 = threading.Thread(target=emsc_socket)

thread2.start()
thread2.join()
