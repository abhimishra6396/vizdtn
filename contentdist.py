import csv
import geopy.distance
from shapely.geometry import LineString, Point
import time
import operator

class parseGTFS:
    def __init__(self,trip_files):
        self.trip_files = trip_files
        self.start_time = 12*3600
        self.visited_count = 0
        self.time_taken = 0
    def readCSV(self, file_name):
        csv_file = open(file_name, mode='r')
        data = csv.DictReader(csv_file)
        return data
    def toElapsedTime(self, date_time, current_date):
        time_midnight = 3600*int(date_time[0]) + 60*int(date_time[1]) + int(date_time[2])
        return time_midnight
    def parseTrips(self):
        trips = parseGTFS(trip_files)
        trips_data = trips.readCSV(self.trip_files[8])
        trip_set=set()
        trajectories=[]
        stop_dict={}
        trip_dict={}
        for row in trips_data:
            prev_len=len(trip_set)
            trip_set.add(row["trip_id"])
            trip_dict[row["trip_id"]]=row["route_id"]
            new_len=len(trip_set)
            if (prev_len!=new_len):
                trajectories.append(Trajectory(row["trip_id"], row["service_id"], row["shape_id"]))
        stops = parseGTFS(trip_files)
        stops_data = stops.readCSV(self.trip_files[6])
        for row in stops_data:
            if int(row["location_type"])==0:
                stop_dict[row["stop_id"]] = [row["stop_lat"],row["stop_lon"],0,0,set()]
        stop_times = parseGTFS(trip_files)
        stop_times_data = stop_times.readCSV(self.trip_files[5])
        for row in stop_times_data:
            if int(row["stop_sequence"])==1:
                stop_dict[row["stop_id"]][2]+=1
        stop_freq = sorted(stop_dict.items(), key=lambda x: x[1][2], reverse=True)
        #print stop_freq[0]
        self.start_transfer(stop_freq[0][0], 60)
        calendar = parseGTFS(trip_files)
        calendar_data = calendar.readCSV(self.trip_files[2])
        stop_times_data = stop_times.readCSV(self.trip_files[5])
        count=0
        for row in stop_times_data:
            if len(stop_dict[row["stop_id"]][4])==0:
                stop_dict[row["stop_id"]][4].add(trip_dict[row["trip_id"]])
            elif ~(trip_dict[row["trip_id"]] in stop_dict[row["stop_id"]][4]):
                stop_dict[row["stop_id"]][4].add(trip_dict[row["trip_id"]])
            if len(stop_dict[row["stop_id"]][4])>1:
                stop_dict[row["stop_id"]][3]=1
        for key in stop_dict.keys():
            if stop_dict[key][3]==1:
                count+=1
        #print count
        return trajectories
    def start_transfer(self, stop_id, content_transfer_time):
        a=1

class Trajectory:
    def __init__(self,trip_id,service_id,shape_id):
        self.trip_id=trip_id
        self.service_id=service_id
        self.shapeid=shape_id
        self.trajectory=[]
        self.stops=[]
        self.proj=[]
        self.stop_proj=[]
    def getPosition(self, time):
        first_stop_x = 1
        first_stop_y = 2
        second_stop_x = 3
        second_stop_y = 4
        time_first = 5
        time_second =6
        posx = first_stop_x + ((time-time_first)*(second_stop_x-first_stop_x))/(time_second-time_first)
        posy = first_stop_y + ((time-time_first)*(second_stop_y-first_stop_y))/(time_second-time_first)
        return (posx, posy)
    def isActive(self, time):
        return isvActive

class Transit:
    def __init__(self,file_name,trajectories):
        self.file_name=file_name
        self.trajectories=trajectories
    def activeTrajectories(self, time):
        return allActiveTrajectories

trip_files = ["../NYC/agency.txt", "../NYC/calendar_dates.txt", "../NYC/calendar.txt", "../NYC/routes.txt", "../NYC/shapes.txt", "../NYC/stop_times.txt", "../NYC/stops.txt", "../NYC/transfers.txt", "../NYC/trips.txt"]
inst = parseGTFS(trip_files)
inst_data = inst.parseTrips()
