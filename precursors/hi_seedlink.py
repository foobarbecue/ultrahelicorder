from obspy.clients.seedlink.easyseedlink import create_client

def handle_trace(trace):
    print(trace)

client = create_client('rtserve.iris.washington.edu', on_data=handle_trace)
client.select_stream('HV','WOOD','EHZ')
client.run()