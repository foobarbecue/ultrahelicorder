from obspy.clients.fdsn import Client
client = Client("IRIS")
res = client.get_waveforms(network="HV",station="WOOD",channel="EHZ", location="--", starttime="2018-05-04T22:30:00", endtime="2018-05-04T22:35:00")
res.plot()