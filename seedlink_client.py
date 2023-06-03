from obspy.clients.seedlink.easyseedlink import EasySeedLinkClient
from obspy.signal.filter import bandpass
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as tk
import threading

bhe_data = []
bhn_data = []
bhz_data = []


class SeedClient(EasySeedLinkClient):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.root = None
        self.fig = None
        self.ax = None
        self.canvas = None

    def initialize_window(self):
        self.root = tk.Tk()
        self.root.title('Waveform')

        self.fig = plt.Figure(figsize=(8, 6))
        self.ax = self.fig.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.root)
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

    def update_waveform(self, bhe_data, bhn_data, bhz_data, starttime, sampling_rate):
        num_samples = len(bhe_data)
        endtime = starttime + num_samples / sampling_rate
        times = np.arange(starttime, endtime, 1 / sampling_rate)

        self.fig.clear()

        amplitude = 0.2
        spacing = 0.5

        # Canal BHE
        ax_bhe = self.fig.add_subplot(311)
        for i, (t, bhe) in enumerate(zip(times, bhe_data)):
            offset = i * spacing
            try:
                ax_bhe.plot([t], [bhe + offset], color='blue',
                            linestyle='-', marker='o')
                ax_bhe.fill_betweenx(
                    [bhe + offset - amplitude, bhe + offset + amplitude], [t], [t], color='black')
            except (ValueError, TypeError):
                pass
        ax_bhe.set_ylabel('BHE Offset')
        ax_bhe.set_title('Waveform - BHE')

        # Canal BHN
        ax_bhn = self.fig.add_subplot(312)
        for i, (t, bhn) in enumerate(zip(times, bhn_data)):
            offset = i * spacing
            try:
                ax_bhn.plot([t], [bhn + offset], color='green',
                            linestyle='-', marker='o')
                ax_bhn.fill_betweenx(
                    [bhn + offset - amplitude, bhn + offset + amplitude], [t], [t], color='black')
            except (ValueError, TypeError):
                pass
        ax_bhn.set_ylabel('BHN Offset')
        ax_bhn.set_title('Waveform - BHN')

        # Canal BHZ
        ax_bhz = self.fig.add_subplot(313)
        for i, (t, bhz) in enumerate(zip(times, bhz_data)):
            offset = i * spacing
            try:
                ax_bhz.plot([t], [bhz + offset], color='red',
                            linestyle='-', marker='o')
                ax_bhz.fill_betweenx(
                    [bhz + offset - amplitude, bhz + offset + amplitude], [t], [t], color='black')
            except (ValueError, TypeError):
                pass
        ax_bhz.set_xlabel('Time')
        ax_bhz.set_ylabel('BHZ Offset')
        ax_bhz.set_title('Waveform - BHZ')

        self.fig.tight_layout()
        self.canvas.draw()
        self.canvas.get_tk_widget().update()

    # On SeedClient data do

    def on_data(self, trace):
        global bhe_data, bhn_data, bhz_data
        print(trace)
        data = trace.data
        starttime = trace.stats.starttime
        sampling_rate = trace.stats.sampling_rate

        freq_min = 1.0  # Frecuencia de corte inferior en Hz
        freq_max = 10.0  # Frecuencia de corte superior en Hz
        orden = 4  # Orden del filtro

        if self.root is None:
            self.initialize_window()

        if trace.stats.channel == 'BHE':
            bhe_data = list(bhe_data)
            bhe_data.extend(data)
            bhe_data = bandpass(data=bhe_data, freqmin=freq_min,
                                freqmax=freq_max, df=sampling_rate, corners=orden)

        if trace.stats.channel == 'BHN':
            bhn_data = list(bhn_data)
            bhn_data.extend(data)
            bhn_data = bandpass(data=bhn_data, freqmin=freq_min,
                                freqmax=freq_max, df=sampling_rate, corners=orden)

        if trace.stats.channel == 'BHZ':
            bhz_data = list(bhz_data)
            bhz_data.extend(data)
            bhz_data = bandpass(data=bhz_data, freqmin=freq_min,
                                freqmax=freq_max, df=sampling_rate, corners=orden)

        max_samples = int(2000 * sampling_rate)
        bhe_data = bhe_data[-max_samples:]
        bhn_data = bhn_data[-max_samples:]
        bhz_data = bhz_data[-max_samples:]

        self.update_waveform(bhe_data, bhn_data, bhz_data,
                             starttime, sampling_rate)

    def on_seedlink_error(self):
        print("Error occurred")

    def on_terminate(self):
        print("Terminated")

    def quit_application(self):
        if self.root is not None:
            self.root.quit()


def run_client():
    client = SeedClient('rtserve.iris.washington.edu:18000')
    # TLIG STATION TLAPA GUERRERO
    client.select_stream('MX', 'TLIG', selector='BHE')
    client.select_stream('MX', 'TLIG', selector='BHN')
    client.select_stream('MX', 'TLIG', selector='BHZ')

    """ client.select_stream('MX', 'CCIG', selector='BHE')
    client.select_stream('MX', 'HPIG', selector='BHE')
    client.select_stream('MX', 'HSTG', selector='BHE')
    client.select_stream('MX', 'MOIG', selector='BHE')
    client.select_stream('MX', 'SRIG', selector='BHE')
    client.select_stream('MX', 'TLIG', selector='BHE')
    client.select_stream('MX', 'ZAIG', selector='BHE') """

    try:
        client.run()
    except KeyboardInterrupt:
        client.quit_application()


if __name__ == "__main__":
    client_thread = threading.Thread(target=run_client)

    client_thread.start()

    root = tk.Tk()
    root.mainloop()
